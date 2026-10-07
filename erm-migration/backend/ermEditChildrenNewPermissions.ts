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
 * Every risk row whose riskObjectId matches is edited, on every dashboard (same as v1).
 * Guards (not in v1):
 *  - a child cannot be idParent itself or one of its ancestors (no parent/child cycles);
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

/** idParent plus all of its ancestors, following riskParent upwards (stops on existing cycles). */
async function ancestorsOf(client: Client, RiskType: any, pk: number): Promise<Set<number>> {
    const seen = new Set<number>();
    let current = pk;
    while (current && !seen.has(current) && seen.size < 100) {
        seen.add(current);
        const page = await client(RiskType).where({ pkImpactId: current }).fetchPage({ $pageSize: 1 });
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

    const ancestors = await ancestorsOf(client, RiskType, Number(idParent));
    const looping = risksChildren.filter(r =>
        toAdd.includes(String(r.riskObjectId)) && ancestors.has(Number(r.pkImpactId)));
    if (looping.length > 0) {
        throw new Error(`Cannot link: risk ${looping[0].pkImpactId} is ${idParent} or one of its parents.`);
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
