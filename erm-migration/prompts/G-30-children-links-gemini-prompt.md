# Prompt: fix G-30 (child-risk links) in the ERM React app

Copy everything below the line into Gemini, in the workspace that has the latest ERM React repository and the Foundry functions repository.

---

You are working in the ERM_RO_Dashboard React + OSDK app (Slate migration) and its Foundry TypeScript functions repository. Your local copy is newer than the reference code in this prompt, so adapt to what is actually in the repository: reuse existing helpers, names and patterns instead of duplicating them, and do not revert newer changes.

## Goal

Fix gap **G-30**: in the risk edit drawer, child-risk edits are silently discarded. Wire the children picker to a backend action, the way legacy Slate did, and prevent parent/child cycles.

## Background (verified from the legacy Slate exports)

- Legacy HeatMap module saved child links with the hidden action widget `w_edit_children_action`, action type `ri.actions.main.action-type.a69cf8d1-3381-4512-b80f-b4797a74b336`.
- It ran on the edit panel's **Validate** click, right after the risk edit, and was skipped when nothing changed. Success toast: "R&O links updated"; failure toast: "R&O links failed".
- Its parameters were: the edited risk's `pk_impact_id` (the parent), the environment, `children_to_add`, `children_to_remove`, the write / owner / officer name lists, and the user's email.
- `children_to_add` / `children_to_remove` were computed as (selected children) minus (current `list_items`) and the reverse, then **mapped from pkImpactId to `risk_object_id`**.
- `riskObjectId` is the risk row's primary key: `<creationDate>_<version>_<iteration>_<pkImpactId>` (the same key `RiskEditDrawer` builds for `ermEditRisk`). So it is one risk on one dashboard. `riskParent` stores the parent's **pkImpactId**.
- Today `RiskEditDrawer.tsx` shows the Children picker but only calls `ermEditRisk` / `ermEditRiskDev`, so ticks and unticks are lost. Its children options also filter out the current children (`String(r.riskParent) !== String(currentPk)`), so existing children can never be unticked.
- Nothing in Slate, the v1 function or React prevented cycles (A parent of B, then B parent of A), or a "remove" from clearing a link that now points to another parent.

## Part 1: backend (Foundry Functions v2)

1. Add this Functions v2 function (a port of the v1 `ermEditChildrenNewPermissions`, with two guards). If a v2 version already exists, merge the guards into it instead. Check the property API names `riskObjectId`, `riskParent`, `updatedOn`, `pkImpactId` and the SDK package name against the ontology, and keep the repository's existing import style.

```ts
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
```

2. Publish it, then create a function-backed action on it (or repoint action type `a69cf8d1…`). Map every parameter **by name**; the order differs from v1. Keep the submission criteria equivalent to legacy (dashboard writers, owners, officers).
3. Regenerate / bump the OSDK in the React app so the action is importable. Note its API name; the frontend below assumes `ermEditChildrenNewPermissions`.

## Part 2: frontend (`src/components/dashboard-view/RiskEditDrawer.tsx`)

Make these changes. The diff at the end is a reference implementation against an older copy; apply the same intent to the current file.

1. Import the new action from the app's OSDK package (use its real API name).
2. Read `currentUserEmail` from `useDashboardContext()`.
3. Build `rowByPk` (pkImpactId → row) from `allRiskRows`, plus:
   - `ancestorPks`: the current risk and its parent chain, following `riskParent` (stop on a repeat);
   - `descendantPks`: the current risk and everything under it.
4. Picker options:
   - **Children:** every row except `ancestorPks`. Current children must stay listed so they can be unticked.
   - **Parent:** every row except `descendantPks`.
   - Before submitting, reject a selection where the chosen parent is also ticked as a child.
5. On Validate, after the existing `ermEditRisk` / `ermEditRiskDev` call succeeds:
   - `current = risk.list_items` (numbers); `toAdd = selected − current`; `toRemove = current − selected`;
   - if either is non-empty, map each pk to its riskObjectId: the row's `risk_object_id` / `riskObjectId`, else its `primary_key` if it contains `_`, else `${normalizedDashId}_${pk}` (the same key the drawer already builds);
   - call the action with `idParent` (this risk's pkImpactId), `userMail`, `idsChildrenToAdd`, `idsChildrenToRemove`, `env` (`CURRENT_ENV ?? 'dev'`), and the dashboard's `permissionsWriteNames`, `permissionsOwnerNames`, `permissionsOfficerNames` (parse the `_display` / raw / snake_case fields the way the rest of the app does).
6. Then `refetchPayload()` once.
   - If the children call failed, keep the drawer open, show "Risk saved, but child links were not: <error message>" in the drawer, and show an error toast. The backend's "Cannot link: …" message must reach the user.
   - Otherwise keep the existing success toast and close the drawer.
7. Do not change anything else: keep the `ermEditRisk` payload, styling and the other fields as they are.

## Checks before you finish

- Run the repository's typecheck, lint and build; fix any errors you introduce.
- Manual test on dev (`env = dev`):
  1. Tick a new child → Validate → the child shows this risk as parent after refresh.
  2. Untick an existing child → Validate → its parent is cleared.
  3. Open risk B whose parent is A: A must not appear in B's Children list, and B's descendants must not appear in B's Parent list.
  4. Call the action directly to link an ancestor as a child → it must fail with "Cannot link: …" and change nothing.
  5. Change only the title → no children action is called.
  6. A user who is not a writer, owner or officer cannot submit.
- Report the files changed, the action's API name, and anything you adapted from this prompt.

## Reference diff (older copy of RiskEditDrawer.tsx)

```diff
diff --git a/src/components/dashboard-view/RiskEditDrawer.tsx b/src/components/dashboard-view/RiskEditDrawer.tsx
index 3c1b8ea..61fb867 100644
--- a/src/components/dashboard-view/RiskEditDrawer.tsx
+++ b/src/components/dashboard-view/RiskEditDrawer.tsx
@@ -2,7 +2,12 @@ import React, { useState, useEffect, useMemo } from 'react';
 import { useDashboardContext, type ArmRiskRow } from '../../context/DashboardContext';
 import { useToast } from '../../context/ToastContext';
 import { client, CURRENT_ENV } from '../../client';
-import { ermEditRisk, ermEditRiskDev } from '@fca0-enterprise-risk-management/sdk';
+import {
+  ermEditRisk,
+  ermEditRiskDev,
+  // Function-backed action on ermEditChildrenNewPermissions (G-30); use the action's API name.
+  ermEditChildrenNewPermissions,
+} from '@fca0-enterprise-risk-management/sdk';
 import { logger } from '../../utils/logger';
 import { cn } from '../../../@/lib/utils';
 import { getScoreCode } from '../../utils/reportTableUtils';
@@ -22,6 +27,35 @@ import { Checkbox } from '../../../@/components/ui/checkbox';
 import { Popover, PopoverContent, PopoverTrigger } from '../../../@/components/ui/popover';
 import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from '../../../@/components/ui/command';
 
+const parseStringArray = (val: unknown): string[] => {
+  if (!val) return [];
+  if (Array.isArray(val)) return val.map((s) => String(s).trim()).filter(Boolean);
+  if (typeof val === 'string') {
+    const trimmed = val.trim();
+    if (trimmed.startsWith('[')) {
+      try {
+        const parsed = JSON.parse(trimmed);
+        if (Array.isArray(parsed)) return parsed.map((s) => String(s).trim()).filter(Boolean);
+      } catch {
+        // Fallback to comma-separated
+      }
+    }
+    return trimmed.split(',').map((s) => s.trim()).filter(Boolean);
+  }
+  return [];
+};
+
+/** pkImpactId of a risk row. */
+const pkOf = (row: ArmRiskRow): number =>
+  Number(row.pk_impact_id || row.PKImpactID || String(row.primary_key ?? '').split('_').pop() || 0);
+
+/** First non-empty value among a dashboard's display / raw / snake_case permission fields. */
+const dashboardList = (dashboard: unknown, camel: string): string[] => {
+  const d = (dashboard ?? {}) as Record<string, unknown>;
+  const snake = camel.replace(/[A-Z]/g, (c) => `_${c.toLowerCase()}`);
+  return parseStringArray(d[`${camel}_display`] ?? d[camel] ?? d[snake]);
+};
+
 interface RiskEditDrawerProps {
   open: boolean;
   onOpenChange: (_open: boolean) => void;
@@ -29,7 +63,7 @@ interface RiskEditDrawerProps {
 }
 
 export const RiskEditDrawer: React.FC<RiskEditDrawerProps> = ({ open, onOpenChange, risk }) => {
-  const { currentDashboard, allRiskRows, canEdit, refetchPayload } = useDashboardContext();
+  const { currentDashboard, currentUserEmail, allRiskRows, canEdit, refetchPayload } = useDashboardContext();
   // App-level toast: it stays visible after this drawer closes (a local one unmounted with it).
   const { showToast } = useToast();
 
@@ -49,27 +83,50 @@ export const RiskEditDrawer: React.FC<RiskEditDrawerProps> = ({ open, onOpenChan
   const [isSubmitting, setIsSubmitting] = useState(false);
   const [errorMessage, setErrorMessage] = useState<string | null>(null);
 
-  // Available Parent Risk Options
-  const availableParentOptions = useMemo(() => {
-    if (!risk) return [];
-    const currentPk = risk.pk_impact_id || Number(risk.primary_key);
+  // Parent links on this dashboard, used to keep the risk tree free of cycles.
+  const rowByPk = useMemo(() => new Map(allRiskRows.map((r) => [pkOf(r), r])), [allRiskRows]);
 
-    return allRiskRows.filter((r) => {
-      const pk = r.pk_impact_id || Number(r.primary_key);
-      return pk !== currentPk;
+  /** The current risk and all of its ancestors (parent, grandparent, ...). */
+  const ancestorPks = useMemo(() => {
+    const seen = new Set<number>();
+    let current = risk ? pkOf(risk) : 0;
+    while (current && !seen.has(current)) {
+      seen.add(current);
+      current = Number(rowByPk.get(current)?.riskParent ?? 0);
+    }
+    return seen;
+  }, [risk, rowByPk]);
+
+  /** The current risk and all of its descendants (children, grandchildren, ...). */
+  const descendantPks = useMemo(() => {
+    const childrenOf = new Map<number, number[]>();
+    allRiskRows.forEach((r) => {
+      const parent = Number(r.riskParent ?? 0);
+      if (parent) childrenOf.set(parent, [...(childrenOf.get(parent) ?? []), pkOf(r)]);
     });
-  }, [allRiskRows, risk]);
+    const seen = new Set<number>();
+    const stack = risk ? [pkOf(risk)] : [];
+    while (stack.length > 0) {
+      const pk = stack.pop()!;
+      if (seen.has(pk)) continue;
+      seen.add(pk);
+      stack.push(...(childrenOf.get(pk) ?? []));
+    }
+    return seen;
+  }, [risk, allRiskRows]);
 
-  // Available Child Risk Options
-  const availableChildrenOptions = useMemo(() => {
+  // Available Parent Risk Options: not the risk itself or one of its descendants.
+  const availableParentOptions = useMemo(() => {
     if (!risk) return [];
-    const currentPk = risk.pk_impact_id || Number(risk.primary_key);
+    return allRiskRows.filter((r) => !descendantPks.has(pkOf(r)));
+  }, [allRiskRows, risk, descendantPks]);
 
-    return allRiskRows.filter((r) => {
-      const pk = r.pk_impact_id || Number(r.primary_key);
-      return pk !== currentPk && String(r.riskParent) !== String(currentPk);
-    });
-  }, [allRiskRows, risk]);
+  // Available Child Risk Options: not the risk itself or one of its ancestors. Current children stay
+  // listed so they can be unticked (they were filtered out before, so they could never be removed).
+  const availableChildrenOptions = useMemo(() => {
+    if (!risk) return [];
+    return allRiskRows.filter((r) => !ancestorPks.has(pkOf(r)));
+  }, [allRiskRows, risk, ancestorPks]);
 
   // Hydrate local form inputs when opening
   useEffect(() => {
@@ -116,6 +173,12 @@ export const RiskEditDrawer: React.FC<RiskEditDrawerProps> = ({ open, onOpenChan
       return;
     }
 
+    const parentNumCheck = selectedParentId ? Number(selectedParentId) : 0;
+    if (parentNumCheck && selectedChildIds.includes(parentNumCheck)) {
+      setErrorMessage('A risk cannot be both the parent and a child of this risk.');
+      return;
+    }
+
     try {
       setIsSubmitting(true);
       setErrorMessage(null);
@@ -126,10 +189,9 @@ export const RiskEditDrawer: React.FC<RiskEditDrawerProps> = ({ open, onOpenChan
       const parentNum = selectedParentId ? Number(selectedParentId) : undefined;
 
       // Construct primary key: (dashboardId with single '_' between version and iteration) + "_" + pkImpactId
+      const normalizedDashId = String(currentDashboard?.dashboardId || '').replace(/___/g, '_');
       let primaryKey = risk.primary_key;
       if (!primaryKey || !primaryKey.includes('_')) {
-        const rawDashId = currentDashboard?.dashboardId || '';
-        const normalizedDashId = String(rawDashId).replace(/___/g, '_');
         primaryKey = `${normalizedDashId}_${pkImpactId}`;
       }
 
@@ -168,8 +230,55 @@ export const RiskEditDrawer: React.FC<RiskEditDrawerProps> = ({ open, onOpenChan
         });
       }
 
+      // G-30: save child links (legacy w_edit_children_action), only when they changed.
+      const currentChildIds = Array.isArray(risk.list_items) ? risk.list_items.map(Number) : [];
+      const childrenToAdd = selectedChildIds.filter((id) => !currentChildIds.includes(id));
+      const childrenToRemove = currentChildIds.filter((id) => !selectedChildIds.includes(id));
+      let childrenError: string | null = null;
+
+      if (childrenToAdd.length > 0 || childrenToRemove.length > 0) {
+        // riskObjectId = "<creationDate>_<version>_<iteration>_<pkImpactId>", the risk row's primary key.
+        const toObjectIds = (pks: number[]) =>
+          pks.map((pk) => {
+            const row = rowByPk.get(pk) as Record<string, unknown> | undefined;
+            const explicit = row?.risk_object_id ?? row?.riskObjectId;
+            if (explicit) return String(explicit);
+            const rowKey = String(row?.primary_key ?? '');
+            return rowKey.includes('_') ? rowKey : `${normalizedDashId}_${pk}`;
+          });
+
+        try {
+          logger.info('RiskEditDrawer', 'Submitting ermEditChildrenNewPermissions', {
+            idParent: pkImpactId,
+            add: childrenToAdd,
+            remove: childrenToRemove,
+            env: CURRENT_ENV,
+          });
+          await client(ermEditChildrenNewPermissions).applyAction({
+            idParent: pkImpactId,
+            userMail: currentUserEmail,
+            idsChildrenToAdd: toObjectIds(childrenToAdd),
+            idsChildrenToRemove: toObjectIds(childrenToRemove),
+            env: CURRENT_ENV ?? 'dev',
+            permissionsWriteNames: dashboardList(currentDashboard, 'permissionsWriteNames'),
+            permissionsOwnerNames: dashboardList(currentDashboard, 'permissionsOwnerNames'),
+            permissionsOfficerNames: dashboardList(currentDashboard, 'permissionsOfficerNames'),
+          });
+        } catch (err: unknown) {
+          logger.error('RiskEditDrawer', 'Failed to save child links', err);
+          childrenError = (err as { message?: string })?.message || 'R&O links failed.';
+        }
+      }
+
       await refetchPayload();
 
+      if (childrenError) {
+        // The risk itself was saved; keep the drawer open so the user sees why the links were not.
+        setErrorMessage(`Risk saved, but child links were not: ${childrenError}`);
+        showToast('Risk saved, but child links failed.', 'error');
+        return;
+      }
+
       showToast(`Risk #${risk.riskid_raw || pkImpactId} updated successfully!`, 'success');
       onOpenChange(false);
     } catch (err: unknown) {
```
