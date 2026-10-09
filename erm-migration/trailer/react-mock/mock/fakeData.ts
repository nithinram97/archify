// Sample data only: invented programmes, risks, people and dates for screenshots.

export const CURRENT_USER = { id: 'u-1', email: 'alex.martin@example.com', username: 'alex.martin' };

const USERS = [
  ['alex.martin@example.com', 'MARTIN, Alex', 'B', 'BA'],
  ['sam.weber@example.com', 'WEBER, Sam', 'O', 'OP'],
  ['chris.lopez@example.com', 'LOPEZ, Chris', 'P', 'PR'],
  ['robin.patel@example.com', 'PATEL, Robin', 'B', 'BE'],
  ['jordan.smith@example.com', 'SMITH, Jordan', 'A', 'AQ'],
];
const OWNERS = 'alex.martin@example.com';
const WRITERS = 'sam.weber@example.com, chris.lopez@example.com';
const OFFICERS = 'robin.patel@example.com';

const DAY = 86400000;
const BASE = Date.UTC(2026, 6, 1);
const iso = (ms: number) => new Date(ms).toISOString();

// dashboardId = <creationDate ms>___<version>___<iteration>
const dash = (i: number, title: string, owner: string, v: number, it: number, status: string, type = 'Report') => {
  const created = BASE - i * 9 * DAY;
  return {
    dashboardId: `${created}___${v}___${it}`, boardTitle: title, reportType: type, boardStatus: status, ownerDashboard: owner,
    creationDate: iso(created).slice(0, 16).replace('T', ' '), lastUpdatedOn: iso(BASE + 60 * DAY - i * DAY).slice(0, 16).replace('T', ' '), updatedOn: iso(BASE + 60 * DAY - i * DAY),
    boardVersion: v, boardIteration: it, validation: status === 'Released', validatorName: status === 'Released' ? 'PATEL, Robin' : '',
    validatedOn: status === 'Released' ? iso(BASE + 50 * DAY) : '', editableUntil: '',
    permissionsReadNames_display: 'jordan.smith@example.com', permissionsWriteNames_display: WRITERS,
    permissionsOwnerNames_display: OWNERS, permissionsOfficerNames_display: OFFICERS,
    isEditor: true, isOwner: true, isOfficer: false, settings: '{}', pkImpactIdList: RISKS.map((r) => r[0]), lastEditor: 'MARTIN, Alex',
  };
};

// Heat map cell ranking used by the app: 1 = nearly certain x very high ... 16 = unlikely x low.
// CELL[probability 1..4][impact 1..4]
const CELL: Record<number, number[]> = { 4: [12, 7, 3, 1], 3: [13, 9, 5, 2], 2: [15, 11, 6, 4], 1: [16, 14, 10, 8] };
type PI = [number, number];
const cell = ([p, i]: PI) => CELL[p][i - 1];
// [pk, title, type, now [prob, impact], previous, target, level1 siglum, top risk, categories]
type R = [number, string, 'Risk' | 'Opportunity', PI, PI, PI, string, boolean, string[]];
const RISKS: R[] = [
  [2072, 'Skills shortage in final assembly', 'Risk', [4, 4], [3, 4], [2, 2], 'B', true, ['People']],
  [2041, 'Supplier capacity for castings', 'Risk', [3, 4], [3, 4], [2, 3], 'P', true, ['Supply chain']],
  [1003, 'Cybersecurity of shop-floor tools', 'Risk', [2, 3], [3, 4], [1, 2], 'O', true, ['IT security']],
  [3101, 'Castings delivery delay', 'Risk', [3, 3], [3, 3], [2, 2], 'P', true, ['Supply chain']],
  [2051, 'Test campaign slip', 'Risk', [2, 4], [3, 3], [1, 3], 'B', true, ['Engineering']],
  [2042, 'Raw material price increase', 'Risk', [2, 2], [3, 2], [1, 2], 'P', true, ['Finance', 'Supply chain']],
  [2061, 'Legacy access model', 'Risk', [1, 3], [2, 3], [1, 2], 'O', true, ['IT security']],
  [2062, 'Third-party tool licences', 'Risk', [1, 2], [2, 2], [1, 1], 'O', false, ['IT security']],
  [3302, 'Documentation gaps on rigs', 'Risk', [3, 2], [3, 2], [2, 2], 'A', true, ['Engineering']],
  [3401, 'Logistics bottleneck in hub', 'Risk', [4, 3], [3, 3], [2, 3], 'A', true, ['Supply chain']],
  [3501, 'Quality escapes at supplier', 'Risk', [1, 1], [2, 1], [1, 1], 'P', false, ['Quality']],
  [4101, 'Automated drilling cell', 'Opportunity', [3, 3], [2, 3], [4, 4], 'B', true, ['Industrial']],
  [4102, 'Supplier consolidation', 'Opportunity', [2, 3], [2, 3], [3, 3], 'P', true, ['Supply chain']],
  [4103, 'Digital twin for rigs', 'Opportunity', [2, 2], [1, 2], [3, 4], 'A', true, ['Engineering']],
];
const LEVEL_COLORS: Record<string, string> = { B: '#2563eb', O: '#16a34a', P: '#d97706', A: '#7c3aed' };

export const DASHBOARDS = [
  dash(0, 'Programme X · Quarterly risk review', 'B', 2, 1, 'Active'),
  dash(1, 'Programme X · Supply chain board', 'P', 1, 3, 'Active'),
  dash(2, 'Operations · Hamburg risks', 'O', 3, 1, 'Released'),
  dash(3, 'Cabin programme · Q3 review', 'A', 1, 1, 'Active', 'Dashboard'),
  dash(4, 'Engineering · Test rigs', 'B', 2, 2, 'Active'),
  dash(5, 'Programme X · Cyber and IT', 'O', 1, 2, 'Released'),
];

const row = ([pk, title, type, nowPI, prevPI, targetPI, lvl, top, cats]: R, dashId: string) => {
  const sign = type === 'Opportunity' ? -1 : 1;
  const status = 'Active';
  const score = cell(nowPI), prev = cell(prevPI), target = cell(targetPI);
  const crit = nowPI[0] * nowPI[1], critPrev = prevPI[0] * prevPI[1], critTarget = targetPI[0] * targetPI[1];
  return {
    primary_key: `${dashId.replace(/___/g, '_')}_${pk}`, risk_object_id: `${dashId.replace(/___/g, '_')}_${pk}`,
    pk_impact_id: pk, PKImpactID: pk, riskid_raw: `R-${pk}`, riskParent: 0, list_items: [], list_items_display: [],
    arm_perimeter: 'Programme X', riskperimeter: 'Programme X', arm_board: 'Programme X board', riskboard: 'Programme X board',
    arm_path: `Programme X/${lvl}`, full_item_path: `${lvl}/${lvl}A`, path: [lvl, `${lvl}A`], path_origin: [lvl], level1: lvl,
    color_level1: LEVEL_COLORS[lvl], border_level1: LEVEL_COLORS[lvl],
    risktitle: title, arm_title: title, riskdescription: `${title}: sample description for the trailer.`, arm_description: '',
    riskcause: 'Sample cause', riskeffect: 'Sample effect', lastreviewcomments: '', risk_comment: '',
    categories: cats, impactCurrentCategory: cats.slice(0, 1), riskstatus: status, risktype: type, siglum_owner: lvl,
    ScoringScheme: '4x4', confidenceLevel: 'Medium', occurrence_date: iso(BASE + 200 * DAY), target_criticality_date: iso(BASE + 150 * DAY),
    risklastrevieweddate: iso(BASE + 40 * DAY),
    arm_score: sign * score, riskscore: sign * score, previous_score: sign * prev, ARM_tar_impactscore: sign * target,
    risktoprisk: top ? 1 : 0, filter_toprisk: top ? 1 : 0, previous_toprisk: top ? 1 : 0, is_top_risk: top,
    is_reassessed: false, risk_board_assessed: true, Trend: crit - critPrev,
    arm_score_display: crit, riskscore_display: crit, previous_score_display: critPrev, ARM_tar_impactscore_display: critTarget,
    previous_ARM_impactscore_display: critPrev, previous_month_ARM_impactscore_display: critPrev,
    css_impactchange: crit > critPrev ? 'Degraded' : crit < critPrev ? 'Improved' : 'Stable', css_toprisk: top ? 'toprisk' : '',
    comment_validated_risk: false,
  };
};

const ACTIONS: [number, string, string, number, number, number][] = [
  [2041, 'Qualify a second castings source', 'Completed', -60, 100, 100],
  [2041, 'Build buffer stock', 'Completed', -20, 100, 100],
  [2041, 'Supplier capacity audit', 'In progress', -15, 80, 45],
  [2072, 'Cross-train assembly teams', 'In progress', 45, 60, 50],
  [2072, 'Recruitment campaign', 'Not started', 90, 20, 0],
  [1003, 'Patch shop-floor tools', 'Completed', -10, 100, 100],
  [3401, 'Second logistics provider', 'In progress', 60, 50, 35],
];

function payload(dashId: string) {
  const rows: Record<string, unknown> = {};
  for (const r of RISKS) { const x = row(r, dashId); rows[x.primary_key] = x; }
  const mitigation_rows: Record<string, unknown> = {};
  ACTIONS.forEach(([pk, title, status, dueDays, planned, achieved], i) => {
    const r = RISKS.find((x) => x[0] === pk)!;
    mitigation_rows[`M-${i}`] = {
      primary_key: `M-${i}`, pk_response_id: 900 + i, response_id: 900 + i, riskid: pk, pk_impact_id_as_string: String(pk),
      ARM_risktitle: r[1], risk_title: r[1], response_title: title,
      response_status: status === 'Completed' ? 'Closed' : 'Active',
      css_mitigation: status === 'Completed' ? 'completed' : dueDays < 0 ? 'late' : status === 'Not started' ? 'pending' : 'ontime',
      response_due_date: new Date(BASE + (60 + dueDays) * DAY).toLocaleDateString('en-GB'), response_due_date_raw: iso(BASE + (60 + dueDays) * DAY),
      planned_percentage: planned, achieved_percentage: achieved, target_score: r[5][0] * r[5][1],
      status_tracker: status === 'Completed' ? 'Completed' : dueDays < 0 ? 'Late' : status === 'Not started' ? 'Pending' : 'On Time',
    };
  });
  const d = DASHBOARDS.find((x) => x.dashboardId === dashId) ?? DASHBOARDS[0];
  return {
    level_labels: { B: 'Programme X', O: 'Operations', P: 'Procurement', A: 'Aftersales' },
    levels: { level1: ['B', 'O', 'P', 'A'] },
    rows, rows_shared: {}, search_rows: {}, msg: 'ok', settings: {},
    mitigation_rows, mitigation_count: ACTIONS.length,
    dashboard_infos: {
      dashboardId: d.dashboardId, boardTitle: d.boardTitle, boardStatus: d.boardStatus, boardVersion: d.boardVersion,
      boardIteration: d.boardIteration, creationDate: d.creationDate, reportType: d.reportType, ownerDashboard: [d.ownerDashboard],
      permissionsOwnerNames: [OWNERS], permissionsWriteNames: WRITERS.split(', '), permissionsOfficerNames: [OFFICERS],
      permissionsReadNames: ['jordan.smith@example.com'], validation: d.validation, settings: '{}',
      execSummary: '<p>Supplier capacity remains the main concern; cybersecurity is back on target.</p>', lastEditor: 'MARTIN, Alex',
      pkImpactIdList: RISKS.map((r) => r[0]), updatedOn: d.updatedOn,
    },
  };
}

async function gzipBase64(value: unknown): Promise<string> {
  const stream = new Blob([JSON.stringify(value)]).stream().pipeThrough(new CompressionStream('gzip'));
  const bytes = new Uint8Array(await new Response(stream).arrayBuffer());
  let s = '';
  for (const b of bytes) s += String.fromCharCode(b);
  return btoa(s);
}

export const QUERIES: Record<string, (args: any) => unknown> = {
  ermGetDashboardList: () => gzipBase64(DASHBOARDS),
  generateArmRoPayload: (args) => payload(args?.dashboardId ?? DASHBOARDS[0].dashboardId),
  ermGetSummaryTabData: () => JSON.stringify({
    canEdit: true,
    execSummaryHtml: '<p>Supplier capacity remains the main concern; cybersecurity is back on target.</p>',
    assumptionHtml: '<p>Figures as of the Q3 2026 review.</p>',
    heatmapCommentsRisksHtml: '<p>Two critical risks, both with mitigations under way.</p>',
    heatmapCommentsOpportunitiesHtml: '<p>Automation opportunity confirmed for Q4.</p>', link: '',
  }),
  ermGetRisksShared: () => JSON.stringify([]),
  ermFullSearchRiskList: () => JSON.stringify([]),
  ermSearchAggPaths: () => JSON.stringify([]),
  ermSearchCategories: () => JSON.stringify(['People', 'Supply chain', 'IT security', 'Engineering', 'Finance', 'Quality', 'Industrial']),
};

export const OBJECTS: Record<string, () => unknown[]> = {
  ErmCockpitUser: () => USERS.map(([email, name, s1, s2]) => ({ userIdentifier: email, email, userCleaned: name, displayName: name, userSiglum1letter: s1, userSiglum2letter: s2, userAppProfile: 'User' })),
  ErmDashboardWaterfall: () => [],
};
