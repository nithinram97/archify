import { createEditBatch, Edits, Integer } from "@osdk/functions";
import { Client } from "@osdk/client";
import { ErmRiskUserInput, ErmRiskUserInputDev } from "@ontology/sdk";

/**
 * Link / unlink child risks to a parent risk (Functions v2 port of ermEditChildrenNewPermissions).
 *
 *   idsChildrenToAdd     riskObjectIds that get riskParent = idParent
 *   idsChildrenToRemove  riskObjectIds that get riskParent = 0
 *   idParent             pkImpactId of the parent risk; 0 means no change (same as v1)
 *
 * riskObjectId is the risk row's primary key, "<creationDate>_<version>_<iteration>_<pkImpactId>",
 * so each id is one risk on one dashboard and the parent chain is followed inside that dashboard.
 * Guards (not in v1):
 *  - a child cannot be idParent itself or one of its ancestors on the same dashboard (no cycles);
 *  - "remove" only detaches children whose current riskParent is idParent.
 * The permission lists and userMail are not used in the logic: they are parameters only so
 * the action can check rights against them, as in v1.
 */

type ChildrenEdits =
    | Edits.Object<ErmRiskUserInput>
    | Edits.Object<ErmRiskUserInputDev>;

const IN_CHUNK = 500;

function chunk<T>(list: T[], size = IN_CHUNK): T[][] {
    const out: T[][] = [];
    for (let i = 0; i < list.length; i += size) out.push(list.slice(i, i + size));
    return out;
}

/** Reads every page of a query (fetchPage alone silently stops after the first page). */
async function fetchAll(query: any): Promise<any[]> {
    const out: any[] = [];
    for await (const obj of query.asyncIter()) out.push(obj);
    return out;
}

/** "<creationDate>_<version>_<iteration>" part of a riskObjectId (everything before the last "_"). */
const dashboardPrefix = (riskObjectId: string): string => riskObjectId.slice(0, riskObjectId.lastIndexOf("_"));

/**
 * pk plus all of its ancestors on one dashboard, following riskParent upwards.
 * Stops on a cycle already in the data, on a missing row, or after 100 levels.
 */
async function ancestorsOf(client: Client, RiskType: any, prefix: string, pk: number): Promise<Set<number>> {
    const seen = new Set<number>();
    let current = pk;
    while (current && !seen.has(current) && seen.size < 100) {
        seen.add(current);
        const page = await client(RiskType).where({ riskObjectId: `${prefix}_${current}` }).fetchPage({ $pageSize: 1 });
        current = Number(page.data[0]?.riskParent ?? 0);
    }
    return seen;
}

export default async function ermEditChildrenNewPermissions(
    client: Client,
    idParent: Integer,
    userMail: string,
    idsChildrenToAdd?: string[],
    idsChildrenToRemove?: string[],
    env?: string,
    // To manage the action rights
    permissionsWriteNames?: string[],
    permissionsOwnerNames?: string[],
    permissionsOfficerNames?: string[]
): Promise<ChildrenEdits[]> {
    const toAdd = (idsChildrenToAdd ?? []).map(String);
    const toRemove = (idsChildrenToRemove ?? []).map(String);
    const environment = env ?? "dev";
    console.info("Workflow Initialized", {
        action: "ermEditChildrenNewPermissions", userMail, env: environment, idParent,
        toAdd: toAdd.length, toRemove: toRemove.length,
    });

    const batch = createEditBatch<ChildrenEdits>(client);
    if ((toAdd.length === 0 && toRemove.length === 0) || idParent === 0) {
        return batch.getEdits();
    }

    const RiskType: any = environment === "master" ? ErmRiskUserInput : ErmRiskUserInputDev;
    const idsChildren = Array.from(new Set([...toAdd, ...toRemove]));
    const parts = await Promise.all(
        chunk(idsChildren).map(part => fetchAll(client(RiskType).where({ riskObjectId: { $in: part } })))
    );
    const risksChildren = parts.flat();

    const ancestorsByDashboard = new Map<string, Set<number>>();
    for (const child of risksChildren) {
        if (!toAdd.includes(String(child.riskObjectId))) continue;
        const prefix = dashboardPrefix(String(child.riskObjectId));
        if (!ancestorsByDashboard.has(prefix)) {
            ancestorsByDashboard.set(prefix, await ancestorsOf(client, RiskType, prefix, Number(idParent)));
        }
        if (ancestorsByDashboard.get(prefix)!.has(Number(child.pkImpactId))) {
            throw new Error(`Cannot link: risk ${child.pkImpactId} is ${idParent} or one of its parents.`);
        }
    }

    const now = new Date().toISOString();
    let edited = 0;
    for (const riskChild of risksChildren) {
        const isAdd = toAdd.includes(String(riskChild.riskObjectId));
        if (!isAdd && Number(riskChild.riskParent) !== Number(idParent)) continue;
        batch.update(riskChild, {
            riskParent: isAdd ? idParent : 0,
            updatedOn: now,
        } as any);
        edited++;
    }

    console.info("Children updated", { action: "ermEditChildrenNewPermissions", edited });
    return batch.getEdits();
}
