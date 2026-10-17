// Stand-in for @osdk/client: answers every query, action and object read from fakeData.
import { QUERIES, OBJECTS } from './fakeData';
export type Client = any;
function handle(def: any) {
  const name = def?.apiName ?? String(def);
  const list = () => (OBJECTS[name] ? OBJECTS[name]() : []);
  const h: any = {
    executeFunction: async (args: any) => (QUERIES[name] ? QUERIES[name](args) : null),
    applyAction: async (args: any) => { console.info('[mock] action', name, args); await new Promise((r) => setTimeout(r, 300)); return {}; },
    fetchPage: async () => ({ data: list(), nextPageToken: undefined }),
    fetchOne: async () => list()[0],
    aggregate: async () => (name === 'ErmDashboardRiskAndOpportunity' ? ['B', 'BA', 'O', 'P'].map((s) => ({ $group: { fullItemPath: s } })) : []),
    async *asyncIter() { for (const o of list()) yield o; },
  };
  for (const m of ['where', 'orderBy', 'select', 'withProperties', 'pivotTo', 'union', 'intersect']) h[m] = () => h;
  return h;
}
export function createClient() { return handle as any; }
