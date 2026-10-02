import React, { useEffect, useState, useMemo, useCallback, useRef } from 'react';
import { useToast } from '../../context/ToastContext';
import { useDashboardContext, type ActionRow } from '../../context/DashboardContext';
import { RiskFilter, defaultRiskFilters } from './RiskFilter';
import { ColumnSelectorPopover } from './ColumnSelectorPopover';
import { AddColumnPopover } from './AddColumnPopover';
import { exportToCSV } from '../../utils/csvExport';
import { measureTextWidth } from '../../utils/textMeasurement';
import { client, CURRENT_ENV } from '../../client';
import { ermEditDashboardSettingsv2 } from '@fca0-enterprise-risk-management/sdk';
import { logger } from '../../utils/logger';
import { cn } from '../../../@/lib/utils';
import {
  type DashboardSettings,
  DEFAULT_NEUTRAL_SETTINGS,
  STANDARD_MITIGATION_COLUMN_MAPPINGS,
  type MitigationColumnDefinition,
  type ColumnTitleObj,
} from '../../types/dashboardSettings';
import { getRowTrendLabel, isNewTopRiskMatch, isCriticalityDiffers } from '../../utils/reportTableUtils';
import {
  Filter,
  Loader2,
  Trash2,
  Save,
  Download,
  ArrowUp,
  ArrowDown,
  ArrowUpDown,
} from 'lucide-react';

import { Button } from '../../../@/components/ui/button';
import { Input } from '../../../@/components/ui/input';
import { Checkbox } from '../../../@/components/ui/checkbox';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../../@/components/ui/table';

export const DashboardActionTrackerTab: React.FC<{ dashboardId: string }> = ({ dashboardId }) => {
  const tableContainerRef = useRef<HTMLDivElement>(null);

  const {
    allRiskRows,
    armRoPayload,
    currentUserEmail,
    isLoadingPayload,
    payloadError,
    filterState: globalFilterState,
    setFilterState: setGlobalFilterState,
    searchText: globalSearchText,
    setSearchText: setGlobalSearchText,
    selectedType,
    setSelectedType,
    refetchPayload,
  } = useDashboardContext();
  const { showToast } = useToast();

  const [isFilterOpen, setIsFilterOpen] = useState(false);

  const [responseStatusFilters, setResponseStatusFilters] = useState<Record<string, boolean>>({
    Active: true,
    Draft: true,
    Closed: true,
    Rejected: false,
  });

  const [completionStatusFilters, setCompletionStatusFilters] = useState<Record<string, boolean>>({
    Completed: true,
    Late: true,
    Pending: true,
    'On Time': true,
  });

  const [fullSettings, setFullSettings] = useState<DashboardSettings>(DEFAULT_NEUTRAL_SETTINGS);
  const [addedColumns, setAddedColumns] = useState<Record<string, string>>({});
  const [displayedKeys, setDisplayedColumns] = useState<string[]>([]);
  const [columnWidths, setColumnWidths] = useState<Record<string, number>>({});

  const [sortConfig, setSortConfig] = useState<{ key: string; direction: 'asc' | 'desc' } | null>({
    key: 'response_due_date',
    direction: 'asc',
  });

  const [cellValues, setCellValues] = useState<Record<string, string>>({});
  const [isSaving, setIsSaving] = useState(false);

  const rawActionsList = useMemo<ActionRow[]>(() => {
    if (!armRoPayload?.mitigation_rows) return [];
    return Object.values(armRoPayload.mitigation_rows);
  }, [armRoPayload]);

  const risksList = useMemo(() => {
    return allRiskRows.filter((r) =>
      String(r.risktype || 'Risk')
        .toLowerCase()
        .includes('risk'),
    );
  }, [allRiskRows]);

  const oppsList = useMemo(() => {
    return allRiskRows.filter((r) =>
      String(r.risktype || '')
        .toLowerCase()
        .includes('opp'),
    );
  }, [allRiskRows]);

  useEffect(() => {
    const rawSettings = armRoPayload?.settings;
    let loadedSettings: DashboardSettings = {};

    if (typeof rawSettings === 'string') {
      try {
        loadedSettings = JSON.parse(rawSettings) as DashboardSettings;
      } catch (e) {
        logger.error('DashboardActionTrackerTab', 'Failed to parse settings JSON string', e);
      }
    } else if (rawSettings && typeof rawSettings === 'object') {
      loadedSettings = rawSettings as DashboardSettings;
    }

    const mergedSettings: DashboardSettings = {
      ...DEFAULT_NEUTRAL_SETTINGS,
      ...loadedSettings,
    };

    setFullSettings(mergedSettings);

    if (loadedSettings.cols_mitigations_list?.added_columns) {
      setAddedColumns(loadedSettings.cols_mitigations_list.added_columns);
    }

    if (
      loadedSettings.cols_mitigations_order_obj?.cols_mitigations &&
      Object.keys(loadedSettings.cols_mitigations_order_obj.cols_mitigations).length > 0
    ) {
      setDisplayedColumns(Object.keys(loadedSettings.cols_mitigations_order_obj.cols_mitigations));
    } else if (
      loadedSettings.cols_mitigations_list?.raw_columns &&
      loadedSettings.cols_mitigations_list.raw_columns.length > 0
    ) {
      setDisplayedColumns(loadedSettings.cols_mitigations_list.raw_columns);
    } else if (DEFAULT_NEUTRAL_SETTINGS.cols_mitigations_list?.raw_columns) {
      setDisplayedColumns(DEFAULT_NEUTRAL_SETTINGS.cols_mitigations_list.raw_columns);
    }

    if (loadedSettings.cols_mitigations_widths && typeof loadedSettings.cols_mitigations_widths === 'object') {
      setColumnWidths(loadedSettings.cols_mitigations_widths as Record<string, number>);
    }

    if (loadedSettings.filters_mitigations) {
      const respVals = loadedSettings.filters_mitigations.response_status?.values || [];
      if (respVals.length > 0) {
        setResponseStatusFilters({
          Active: respVals.includes('Active'),
          Draft: respVals.includes('Draft'),
          Closed: respVals.includes('Closed'),
          Rejected: respVals.includes('Rejected'),
        });
      }

      const compVals = loadedSettings.filters_mitigations.status_tracker?.values || [];
      if (compVals.length > 0) {
        setCompletionStatusFilters({
          Completed: compVals.includes('Completed'),
          Late: compVals.includes('Late'),
          Pending: compVals.includes('Pending'),
          'On Time': compVals.includes('On Time'),
        });
      }
    }

    const actionTrackerTableValues = loadedSettings.action_tracker_table?.value || {};
    const initialValues: Record<string, string> = {};
    Object.entries(actionTrackerTableValues).forEach(([key, valObj]) => {
      const v = (valObj as { value?: string })?.value;
      if (v) initialValues[key] = v;
    });
    setCellValues(initialValues);
  }, [armRoPayload]);

  const handleColumnResizeMouseDown = (e: React.MouseEvent, colKey: string) => {
    e.preventDefault();
    e.stopPropagation();

    const containerWidth = tableContainerRef.current?.clientWidth || 1000;
    const startX = e.clientX;
    const startPct = columnWidths[colKey] || 12;

    const onMouseMove = (moveEvent: MouseEvent) => {
      const deltaX = moveEvent.clientX - startX;
      const deltaPct = (deltaX / containerWidth) * 100;
      const newPct = Math.max(4, Math.min(60, startPct + deltaPct));

      setColumnWidths((prev) => ({
        ...prev,
        [colKey]: parseFloat(newPct.toFixed(2)),
      }));
    };

    const onMouseUp = () => {
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
      document.body.style.cursor = 'default';
      document.body.style.userSelect = 'auto';
    };

    document.body.style.cursor = 'col-resize';
    document.body.style.userSelect = 'none';
    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  };

  const filteredRiskImpactIdsSet = useMemo(() => {
    const activeRisks = allRiskRows.filter((row) => {
      const isOpportunity = String(row.risktype || '')
        .toLowerCase()
        .includes('opp');
      if (selectedType === 'Opportunity' && !isOpportunity) return false;
      if (selectedType === 'Risk' && isOpportunity) return false;

      if (globalFilterState.topRiskOnly && !(row.risktoprisk || row.css_toprisk?.includes('toprisk'))) {
        return false;
      }
      if (globalFilterState.criticalityDiffersOnly && !isCriticalityDiffers(row)) {
        return false;
      }

      const rowStatus = (row.riskstatus || 'Draft').toLowerCase();
      const isStatusMatch = globalFilterState.statuses.some((s) => s.toLowerCase() === rowStatus);
      if (!isStatusMatch) return false;

      const rowTrend = getRowTrendLabel(row);
      const isTrendMatch = globalFilterState.trends.some((t) => t.toLowerCase() === rowTrend.toLowerCase());
      if (!isTrendMatch) return false;

      if (!isNewTopRiskMatch(row, globalFilterState.newTopRisk)) return false;

      if (globalFilterState.categories && globalFilterState.categories.length > 0) {
        const rowCats: string[] = Array.isArray(row.categories) ? row.categories : [];
        if (!globalFilterState.categories.some((c) => rowCats.includes(c))) return false;
      }

      if (globalFilterState.impactCurrentCategory && globalFilterState.impactCurrentCategory.length > 0) {
        const rowImpactCats: string[] = Array.isArray(row.impactCurrentCategory) ? row.impactCurrentCategory : [];
        if (!globalFilterState.impactCurrentCategory.some((c) => rowImpactCats.includes(c))) return false;
      }

      if (globalSearchText.trim()) {
        const query = globalSearchText.toLowerCase().trim();
        const id = String(row.riskid_raw || row.pk_impact_id || '').toLowerCase();
        const title = String(row.risktitle || row.arm_title || '').toLowerCase();
        const desc = String(row.riskdescription || row.arm_description || '').toLowerCase();
        return id.includes(query) || title.includes(query) || desc.includes(query);
      }

      return true;
    });

    return new Set(activeRisks.map((r) => r.pk_impact_id || Number(r.primary_key)));
  }, [allRiskRows, globalFilterState, globalSearchText, selectedType]);

  const filteredActions = useMemo(() => {
    return rawActionsList.filter((action) => {
      const parentRiskId = Number(action.pk_impact_id_as_string);
      if (!filteredRiskImpactIdsSet.has(parentRiskId)) {
        return false;
      }

      const respStatus = action.response_status || 'Draft';
      if (!responseStatusFilters[respStatus]) {
        return false;
      }

      const compStatus = action.status_tracker || 'Pending';
      if (!completionStatusFilters[compStatus]) {
        return false;
      }

      return true;
    });
  }, [rawActionsList, filteredRiskImpactIdsSet, responseStatusFilters, completionStatusFilters]);

  const allAvailableColumns = useMemo<MitigationColumnDefinition[]>(() => {
    const customCols: MitigationColumnDefinition[] = Object.entries(addedColumns).map(([colKey, title]) => ({
      key: colKey,
      title,
      isAdded: true,
    }));
    return [...STANDARD_MITIGATION_COLUMN_MAPPINGS, ...customCols];
  }, [addedColumns]);

  const activeColumns = useMemo<MitigationColumnDefinition[]>(() => {
    const savedColsObj = fullSettings.cols_mitigations_order_obj?.cols_mitigations || {};

    return displayedKeys
      .map((key) => {
        const match = allAvailableColumns.find((c) => c.key === key);
        if (match) return match;

        if (key === 'risk_id' || key === 'riskid_raw') return allAvailableColumns.find((c) => c.key === 'riskid');
        if (key === 'risk_title' || key === 'arm_risktitle')
          return allAvailableColumns.find((c) => c.key === 'ARM_risktitle');

        const savedColInfo = savedColsObj[key];
        if (savedColInfo?.title) {
          const isAdded = savedColInfo.css === 'added' || Boolean(addedColumns[key]);
          return { key, title: savedColInfo.title, isAdded };
        }

        return undefined;
      })
      .filter((c): c is MitigationColumnDefinition => Boolean(c));
  }, [displayedKeys, allAvailableColumns, fullSettings, addedColumns]);

  const sortedAndFilteredActions = useMemo(() => {
    if (!sortConfig) return filteredActions;

    return [...filteredActions].sort((a, b) => {
      const primaryKeyA = a.primary_key;
      const primaryKeyB = b.primary_key;

      const col = activeColumns.find((c) => c.key === sortConfig.key);
      if (!col) return 0;

      let valA: unknown = col.isAdded ? cellValues[`${primaryKeyA}##${col.key}`] : a[col.key];
      let valB: unknown = col.isAdded ? cellValues[`${primaryKeyB}##${col.key}`] : b[col.key];

      if (!col.isAdded) {
        if (col.key === 'response_due_date') {
          const parseDate = (row: ActionRow) => {
            if (row.response_due_date_raw) return new Date(row.response_due_date_raw).getTime();
            if (row.response_due_date) return new Date(row.response_due_date).getTime();
            return 0;
          };
          valA = parseDate(a);
          valB = parseDate(b);
        } else if (col.key === 'response_completion_date') {
          const parseDate = (row: ActionRow) => {
            if (row.response_completion_date_raw) return new Date(row.response_completion_date_raw).getTime();
            if (row.response_completion_date) return new Date(row.response_completion_date).getTime();
            return 0;
          };
          valA = parseDate(a);
          valB = parseDate(b);
        } else if (col.key === 'ARM_risktitle' || col.key === 'risk_title') {
          valA = a.ARM_risktitle || a.risk_title || '';
          valB = b.ARM_risktitle || b.risk_title || '';
        }
      }

      if (valA == null) valA = '';
      if (valB == null) valB = '';

      let comparison = 0;
      if (typeof valA === 'number' && typeof valB === 'number') {
        comparison = valA - valB;
      } else {
        comparison = String(valA).toLowerCase().localeCompare(String(valB).toLowerCase(), undefined, { numeric: true });
      }

      return sortConfig.direction === 'asc' ? comparison : -comparison;
    });
  }, [filteredActions, sortConfig, activeColumns, cellValues]);

  const handleColumnDoubleClick = (e: React.MouseEvent, colKey: string, colTitle: string) => {
    e.preventDefault();
    e.stopPropagation();

    const containerWidth = tableContainerRef.current?.clientWidth || 1000;
    let maxPx = measureTextWidth(colTitle, 'bold 12px Inter, sans-serif') + 40;

    sortedAndFilteredActions.forEach((row) => {
      const primaryKey = row.primary_key;
      let cellText = '';

      if (cellValues[`${primaryKey}##${colKey}`]) {
        cellText = cellValues[`${primaryKey}##${colKey}`];
      } else {
        cellText = String(row[colKey] ?? '');
      }

      if (cellText) {
        const cellPx = measureTextWidth(cellText, '12px Inter, sans-serif') + 24;
        if (cellPx > maxPx) {
          maxPx = cellPx;
        }
      }
    });

    const autoPct = Math.max(5, Math.min(50, (maxPx / containerWidth) * 100));

    setColumnWidths((prev) => ({
      ...prev,
      [colKey]: parseFloat(autoPct.toFixed(2)),
    }));
  };

  const handleSortToggle = (colKey: string) => {
    setSortConfig((prev) => {
      if (!prev || prev.key !== colKey) {
        return { key: colKey, direction: 'asc' };
      }
      if (prev.direction === 'asc') {
        return { key: colKey, direction: 'desc' };
      }
      return null;
    });
  };

  const handleExportCSV = useCallback(() => {
    const headers = activeColumns.map((c) => c.title);
    const rows = sortedAndFilteredActions.map((row) => {
      const primaryKey = row.primary_key;
      return activeColumns.map((col) => {
        if (col.isAdded) {
          const cellKey = `${primaryKey}##${col.key}`;
          return cellValues[cellKey] || (row[col.key] as string) || '';
        }

        if (col.key === 'ARM_risktitle' || col.key === 'risk_title') {
          return String(row.ARM_risktitle || row.risk_title || '-');
        }

        return String(row[col.key] ?? '-');
      });
    });

    const filename = `${dashboardId.replace(/[^a-zA-Z0-9_-]/g, '_')}_action_tracker.csv`;
    exportToCSV(filename, headers, rows);
  }, [activeColumns, sortedAndFilteredActions, cellValues, dashboardId]);

  const toggleColumnVisibility = (key: string) => {
    const targetCol = allAvailableColumns.find((c) => c.key === key);
    if (!targetCol) return;

    setDisplayedColumns((prev) => {
      const isAlreadyActive = activeColumns.some((c) => c.key === targetCol.key);
      if (isAlreadyActive) {
        return prev.filter((k) => k !== targetCol.key);
      } else {
        return [...prev, targetCol.key];
      }
    });
  };

  const handleCreateColumn = (newColTitle: string) => {
    const nextIndex = Object.keys(addedColumns).length + 2;
    const newColKey = `col${nextIndex}`;
    setAddedColumns((prev) => ({ ...prev, [newColKey]: newColTitle }));
    setDisplayedColumns((prev) => [...prev, newColKey]);
  };

  const handleRemoveColumn = (colKey: string) => {
    setAddedColumns((prev) => {
      const next = { ...prev };
      delete next[colKey];
      return next;
    });

    setDisplayedColumns((prev) => prev.filter((k) => k !== colKey));

    setCellValues((prev) => {
      const next = { ...prev };
      Object.keys(next).forEach((key) => {
        if (key.endsWith(`##${colKey}`)) {
          delete next[key];
        }
      });
      return next;
    });
  };

  const handleCellValueChange = (primaryKey: string, colKey: string, value: string) => {
    const valueKey = `${primaryKey}##${colKey}`;
    setCellValues((prev) => ({
      ...prev,
      [valueKey]: value,
    }));
  };

  const handleSaveSettings = useCallback(async () => {
    try {
      setIsSaving(true);

      const actionTrackerCol: Record<string, { col: string; action: string }> = {};
      Object.entries(addedColumns).forEach(([colKey, colTitle]) => {
        actionTrackerCol[colKey] = { col: colTitle, action: 'add' };
      });

      const actionTrackerValue: Record<string, { value: string; action: string }> = {};
      const validColKeys = new Set(Object.keys(addedColumns));

      Object.entries(cellValues).forEach(([cellKey, val]) => {
        const colKey = cellKey.split('##').pop();
        if (colKey && validColKeys.has(colKey) && val.trim()) {
          actionTrackerValue[cellKey] = { value: val, action: 'add' };
        }
      });

      const displayedTitles = activeColumns.map((c) => c.title);
      const rawColumnKeys = activeColumns.map((c) => c.key);

      const activeRespFilters = Object.entries(responseStatusFilters)
        .filter(([, active]) => active)
        .map(([k]) => k);

      const activeCompFilters = Object.entries(completionStatusFilters)
        .filter(([, active]) => active)
        .map(([k]) => k);

      const colsMitigationsObjCols: Record<string, ColumnTitleObj> = {};
      activeColumns.forEach((c) => {
        colsMitigationsObjCols[c.key] = {
          title: c.title,
          ...(c.isAdded ? { css: 'added' } : {}),
        };
      });

      const updatedSettings: DashboardSettings = {
        ...DEFAULT_NEUTRAL_SETTINGS,
        ...fullSettings,
        cols_mitigations_widths: columnWidths,
        cols_mitigations_list: {
          added_columns: addedColumns,
          displayed_columns: displayedTitles,
          raw_columns: rawColumnKeys,
        },
        cols_mitigations_obj: {
          cols_mitigations: colsMitigationsObjCols,
        },
        cols_mitigations_order_obj: {
          cols_mitigations: colsMitigationsObjCols,
          default: false,
        },
        filters_mitigations: {
          response_status: {
            title: 'Response Status',
            values: activeRespFilters,
          },
          status_tracker: {
            title: 'Completion Status',
            values: activeCompFilters,
          },
        },
        action_tracker_table: {
          col: actionTrackerCol,
          value: actionTrackerValue,
        },
      };

      const settingsString = JSON.stringify(updatedSettings);

      await client(ermEditDashboardSettingsv2).applyAction({
        dashboardId,
        incomingSettings: settingsString,
        userMail: currentUserEmail,
        lastEditor: currentUserEmail,
        env: CURRENT_ENV ?? "dev",
      });

      setFullSettings(updatedSettings);
      showToast('Action Tracker settings saved successfully!', 'success');

      await refetchPayload();
    } catch (err: unknown) {
      const errObj = err as { message?: string };
      logger.error('DashboardActionTrackerTab', 'Failed to save settings', err);
      showToast(errObj?.message || 'Failed to save settings. Insufficient permissions.', 'error');
    } finally {
      setIsSaving(false);
    }
  }, [
    addedColumns,
    cellValues,
    activeColumns,
    columnWidths,
    responseStatusFilters,
    completionStatusFilters,
    fullSettings,
    dashboardId,
    currentUserEmail,
    refetchPayload,
    showToast,
  ]);

  if (isLoadingPayload) {
    return (
      <div className="flex-1 bg-white flex items-center justify-center p-12 rounded-md border text-airbus-navy font-medium text-xs">
        <Loader2 className="h-5 w-5 animate-spin mr-2" /> Loading Action Tracker Data...
      </div>
    );
  }

  if (payloadError) {
    return (
      <div className="flex-1 bg-white flex items-center justify-center p-12 rounded-md border text-red-600 text-xs font-medium">
        {payloadError}
      </div>
    );
  }

  return (
    <div className="flex-1 bg-white flex h-full w-full overflow-hidden select-text relative">
      <RiskFilter
        isOpen={isFilterOpen}
        onClose={() => setIsFilterOpen(false)}
        allRisks={allRiskRows}
        filters={globalFilterState}
        onFilterChange={setGlobalFilterState}
        onResetFilters={() => setGlobalFilterState(defaultRiskFilters)}
      />

      <div className="flex-1 flex flex-col p-3 h-full overflow-hidden gap-3">
        {/* Top Control Bar */}
        <div className="flex items-center gap-2 pb-2 text-xs shrink-0 border-b border-slate-200">
          <Button
            variant={isFilterOpen ? 'secondary' : 'ghost'}
            size="icon-xs"
            onClick={() => setIsFilterOpen(!isFilterOpen)}
            className="h-7 w-7 text-slate-700 cursor-pointer"
            title="Toggle Global Risk Filters"
          >
            <Filter className="h-4 w-4" />
          </Button>

          <div className="w-52">
            <Input
              placeholder="Search by keywords"
              value={globalSearchText}
              onChange={(e) => setGlobalSearchText(e.target.value)}
              className="h-7 text-xs bg-white border-slate-300 rounded-none focus-visible:ring-0"
            />
          </div>

          <div className="flex items-center ml-2">
            <Button
              type="button"
              size="xs"
              variant="outline"
              onClick={() => setSelectedType('Risk')}
              className={cn(
                'h-6 px-2 text-[11px] font-bold rounded-none border-red-600 cursor-pointer',
                selectedType === 'Risk'
                  ? 'bg-white text-red-600 border-red-600'
                  : 'bg-slate-100 text-slate-400 border-slate-300',
              )}
            >
              Risk ({selectedType === 'Risk' ? sortedAndFilteredActions.length : 0}/{risksList.length})
            </Button>
            <Button
              type="button"
              size="xs"
              variant="outline"
              onClick={() => setSelectedType('Opportunity')}
              className={cn(
                'h-6 px-2 text-[11px] rounded-none border-l-0 border-slate-300 cursor-pointer',
                selectedType === 'Opportunity'
                  ? 'bg-white text-blue-600 border-blue-600 font-bold'
                  : 'bg-slate-100 text-slate-400',
              )}
            >
              Opp. ({selectedType === 'Opportunity' ? sortedAndFilteredActions.length : 0}/{oppsList.length})
            </Button>
          </div>
        </div>

        {/* Response & Completion Status Filters */}
        <div className="flex flex-wrap items-center justify-between gap-4 text-xs shrink-0 bg-white border border-slate-200 p-2.5 rounded-md">
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-3">
              <span className="font-semibold text-slate-700">Response Status:</span>
              {['Active', 'Draft', 'Closed', 'Rejected'].map((status) => (
                <div key={status} className="flex items-center gap-1.5">
                  <Checkbox
                    id={`resp-${status}`}
                    checked={Boolean(responseStatusFilters[status])}
                    onCheckedChange={(checked) =>
                      setResponseStatusFilters((prev) => ({ ...prev, [status]: Boolean(checked) }))
                    }
                  />
                  <label htmlFor={`resp-${status}`} className="cursor-pointer text-slate-700 font-medium">
                    {status}
                  </label>
                </div>
              ))}
            </div>

            <div className="flex items-center gap-3 border-l border-slate-200 pl-6">
              <span className="font-semibold text-slate-700">Completion Status:</span>
              {['Completed', 'Late', 'Pending', 'On Time'].map((status) => (
                <div key={status} className="flex items-center gap-1.5">
                  <Checkbox
                    id={`comp-${status}`}
                    checked={Boolean(completionStatusFilters[status])}
                    onCheckedChange={(checked) =>
                      setCompletionStatusFilters((prev) => ({ ...prev, [status]: Boolean(checked) }))
                    }
                  />
                  <label htmlFor={`comp-${status}`} className="cursor-pointer text-slate-700 font-medium">
                    {status}
                  </label>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Action Toolbar */}
        <div className="flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3 text-xs">
            <ColumnSelectorPopover
              availableColumns={allAvailableColumns}
              activeColumns={activeColumns}
              onToggleVisibility={toggleColumnVisibility}
            />

            <div className="border-l border-slate-200 pl-3">
              <span className="text-slate-600 font-mono">
                Showing <strong>{sortedAndFilteredActions.length}</strong> action(s)
              </span>
            </div>

            <Button
              type="button"
              size="xs"
              onClick={handleSaveSettings}
              disabled={isSaving}
              className="h-7 px-3 bg-[#DA1884] hover:bg-[#b0136a] text-white font-semibold text-xs rounded shadow-2xs cursor-pointer flex items-center gap-1.5"
            >
              {isSaving ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Save className="h-3.5 w-3.5" />}
              <span>Save</span>
            </Button>

            <Button
              type="button"
              variant="outline"
              size="icon-xs"
              onClick={handleExportCSV}
              className="h-7 w-7 text-white bg-[#DA1884] hover:bg-[#b0136a] border-none cursor-pointer"
              title="Export as CSV"
            >
              <Download className="h-3.5 w-3.5" />
            </Button>
          </div>
        </div>

        {/* Scrollable Container with Relative (%) Widths & Excel-like Auto-Fit */}
        <div ref={tableContainerRef} className="flex-1 overflow-auto border border-slate-200 rounded-md bg-white">
          <Table className="text-xs table-fixed w-full">
            <TableHeader className="bg-airbus-navy text-white sticky top-0 z-10 shadow-xs">
              <TableRow className="hover:bg-transparent border-b border-slate-800">
                {activeColumns.map((col) => {
                  const isSorted = sortConfig?.key === col.key;
                  const colPct = columnWidths[col.key] || 12;

                  return (
                    <TableHead
                      key={col.key}
                      style={{ width: `${colPct}%` }}
                      onClick={() => handleSortToggle(col.key)}
                      className="relative py-2 px-2.5 text-white font-semibold truncate hover:bg-white/5 cursor-pointer select-none border-r border-slate-700/80 last:border-r-0 group/col"
                    >
                      <div className="flex items-center justify-between gap-1 pr-2">
                        <span className="truncate flex items-center gap-1">
                          <Button
                            variant="ghost"
                            size="icon-xs"
                            className="h-4 w-4 p-0 text-slate-300 hover:text-white hover:bg-white/10"
                          >
                            {isSorted ? (
                              sortConfig.direction === 'asc' ? (
                                <ArrowUp className="h-3.5 w-3.5 text-pink-400 font-bold" />
                              ) : (
                                <ArrowDown className="h-3.5 w-3.5 text-pink-400 font-bold" />
                              )
                            ) : (
                              <ArrowUpDown className="h-3.5 w-3.5 text-slate-300 opacity-70" />
                            )}
                          </Button>
                          <span>{col.title}</span>
                        </span>

                        {col.isAdded && (
                          <Button
                            variant="ghost"
                            size="icon-xs"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleRemoveColumn(col.key);
                            }}
                            className="h-5 w-5 text-slate-300 hover:text-red-300 hover:bg-white/10 cursor-pointer"
                            title="Delete Column"
                          >
                            <Trash2 className="h-3 w-3" />
                          </Button>
                        )}
                      </div>

                      {/* Resizer Handle: Drag (%) | Double Click Auto-Fit */}
                      <div
                        onMouseDown={(e) => handleColumnResizeMouseDown(e, col.key)}
                        onDoubleClick={(e) => handleColumnDoubleClick(e, col.key, col.title)}
                        onClick={(e) => e.stopPropagation()}
                        className="absolute -right-1 top-0 bottom-0 w-2.5 cursor-col-resize group/resizer hover:bg-pink-500/80 active:bg-pink-600 transition-colors z-30 flex items-center justify-center"
                        title="Drag to resize (%) | Double-click to auto-fit"
                      >
                        <div className="w-[2px] h-4 bg-slate-400/50 group-hover/resizer:bg-white transition-colors rounded-full" />
                      </div>
                    </TableHead>
                  );
                })}

                <TableHead className="w-[3%] p-0 text-center bg-airbus-navy border-l border-slate-700 sticky right-0 z-20">
                  <AddColumnPopover onAddColumn={handleCreateColumn} />
                </TableHead>
              </TableRow>
            </TableHeader>

            <TableBody>
              {sortedAndFilteredActions.length > 0 ? (
                sortedAndFilteredActions.map((row) => {
                  const isLate = row.css_mitigation === 'late' || row.status_tracker === 'Late';
                  const isPending = row.css_mitigation === 'pending' || row.status_tracker === 'Pending';
                  return (
                    <TableRow key={row.primary_key} className="hover:bg-slate-50 transition-colors">
                      {activeColumns.map((col) => {
                        if (col.isAdded) {
                          const cellKey = `${row.primary_key}##${col.key}`;
                          const val = cellValues[cellKey] || (row[col.key] as string) || '';

                          return (
                            <TableCell key={col.key} className="p-1 border-r border-slate-200/80 last:border-r-0">
                              <Input
                                value={val}
                                placeholder="Enter value..."
                                onChange={(e) => handleCellValueChange(row.primary_key, col.key, e.target.value)}
                                className="h-7 text-xs bg-slate-50/50 hover:bg-white border-transparent hover:border-slate-300 focus:border-airbus-blue focus:bg-white transition-all font-medium text-airbus-navy"
                              />
                            </TableCell>
                          );
                        }

                        if (col.key === 'response_due_date') {
                          const dueDateVal = String(row.response_due_date || '');
                          return (
                            <TableCell
                              key={col.key}
                              className={cn(
                                'p-2 font-mono text-[11px] font-semibold truncate select-text border-r border-slate-200/80 last:border-r-0',
                                isLate
                                  ? 'bg-red-600 text-white font-bold'
                                  : isPending
                                    ? 'bg-amber-500 text-white font-bold'
                                    : 'text-slate-700',
                              )}
                            >
                              {dueDateVal || '-'}
                            </TableCell>
                          );
                        }

                        if (col.key === 'riskid' || col.key === 'risk_id') {
                          return (
                            <TableCell
                              key={col.key}
                              className="p-2 font-mono text-airbus-blue font-bold truncate select-text border-r border-slate-200/80 last:border-r-0"
                            >
                              {String(row.riskid ?? row.risk_id ?? '-')}
                            </TableCell>
                          );
                        }

                        if (col.key === 'ARM_risktitle' || col.key === 'risk_title') {
                          const riskTitleVal = String(row.ARM_risktitle || row.risk_title || '-');
                          return (
                            <TableCell
                              key={col.key}
                              className="p-2 truncate font-medium text-slate-700 select-text border-r border-slate-200/80 last:border-r-0"
                              title={riskTitleVal}
                            >
                              {riskTitleVal}
                            </TableCell>
                          );
                        }

                        const cellString = String(row[col.key] ?? '');

                        return (
                          <TableCell
                            key={col.key}
                            className="p-2 truncate font-medium text-slate-700 select-text border-r border-slate-200/80 last:border-r-0"
                            title={cellString}
                          >
                            {cellString || '-'}
                          </TableCell>
                        );
                      })}

                      <TableCell className="p-0 border-l border-slate-100 bg-slate-50/30 sticky right-0" />
                    </TableRow>
                  );
                })
              ) : (
                <TableRow>
                  <TableCell colSpan={activeColumns.length + 1} className="h-32 text-center text-slate-400 text-xs">
                    No action items match the current filter selection.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>
      </div>

    </div>
  );
};
