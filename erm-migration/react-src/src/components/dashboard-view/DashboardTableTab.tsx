import React, { useEffect, useState, useMemo, useCallback, useRef } from 'react';
import { useToast } from '../../context/ToastContext';
import { useNavigate } from 'react-router-dom';
import { useDashboardContext } from '../../context/DashboardContext';
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
  STANDARD_COLUMN_MAPPINGS,
  type ColumnDefinition,
  type ColumnTitleObj,
} from '../../types/dashboardSettings';
import {
  getScoreLevelAndColor,
  getTrendConfig,
  getRowTrendLabel,
  isNewTopRiskMatch,
  isCriticalityDiffers,
  formatOccurrenceDate,
  buildHierarchicalTreeRows,
  type TreeProcessedRow,
} from '../../utils/reportTableUtils';
import {
  Filter,
  Loader2,
  Trash2,
  Save,
  Download,
  ArrowUp,
  ArrowDown,
  ArrowUpDown,
  CornerDownRight,
  FileText,
} from 'lucide-react';

import { Button } from '../../../@/components/ui/button';
import { Input } from '../../../@/components/ui/input';
import { Checkbox } from '../../../@/components/ui/checkbox';
import { Badge } from '../../../@/components/ui/badge';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../../../@/components/ui/table';

export const DashboardTableTab: React.FC<{ dashboardId: string }> = ({ dashboardId }) => {
  const navigate = useNavigate();
  const tableContainerRef = useRef<HTMLDivElement>(null);

  const {
    allRiskRows,
    armRoPayload,
    currentUserEmail,
    isLoadingPayload,
    payloadError,
    filterState,
    setFilterState,
    searchText,
    setSearchText,
    selectedType,
    setSelectedType,
    refetchPayload,
  } = useDashboardContext();
  const { showToast } = useToast();

  const [isFilterOpen, setIsFilterOpen] = useState(false);
  const [includeChildren, setIncludeChildren] = useState(false);

  const [fullSettings, setFullSettings] = useState<DashboardSettings>(DEFAULT_NEUTRAL_SETTINGS);
  const [addedColumns, setAddedColumns] = useState<Record<string, string>>({});
  const [displayedKeys, setDisplayedColumns] = useState<string[]>([]);
  const [cellValues, setCellValues] = useState<Record<string, string>>({});
  const [columnWidths, setColumnWidths] = useState<Record<string, number>>({});

  const [sortConfig, setSortConfig] = useState<{ key: string; direction: 'asc' | 'desc' } | null>(null);

  const [isSaving, setIsSaving] = useState(false);

  const risksList = useMemo(() => {
    return allRiskRows.filter((r) => {
      const typeStr = String(r.risktype || r.riskType || r.type || 'Risk').toLowerCase();
      return !typeStr.includes('opp');
    });
  }, [allRiskRows]);

  const oppsList = useMemo(() => {
    return allRiskRows.filter((r) => {
      const typeStr = String(r.risktype || r.riskType || r.type || '').toLowerCase();
      return typeStr.includes('opp');
    });
  }, [allRiskRows]);

  const activeRowsByType = useMemo(() => {
    return selectedType === 'Risk' ? risksList : oppsList;
  }, [selectedType, risksList, oppsList]);

  useEffect(() => {
    const rawSettings = armRoPayload?.settings;
    let loadedSettings: DashboardSettings = {};

    if (typeof rawSettings === 'string') {
      try {
        loadedSettings = JSON.parse(rawSettings) as DashboardSettings;
      } catch (e) {
        logger.error('DashboardTableTab', 'Failed to parse stringified settings', e);
      }
    } else if (rawSettings && typeof rawSettings === 'object') {
      loadedSettings = rawSettings as DashboardSettings;
    }

    const mergedSettings: DashboardSettings = {
      ...DEFAULT_NEUTRAL_SETTINGS,
      ...loadedSettings,
    };

    setFullSettings(mergedSettings);

    if (loadedSettings.cols_list?.added_columns) {
      setAddedColumns(loadedSettings.cols_list.added_columns);
    }

    if (loadedSettings.cols_order_obj?.cols && Object.keys(loadedSettings.cols_order_obj.cols).length > 0) {
      setDisplayedColumns(Object.keys(loadedSettings.cols_order_obj.cols));
    } else if (loadedSettings.cols_list?.raw_columns && loadedSettings.cols_list.raw_columns.length > 0) {
      setDisplayedColumns(loadedSettings.cols_list.raw_columns);
    } else if (DEFAULT_NEUTRAL_SETTINGS.cols_list?.raw_columns) {
      setDisplayedColumns(DEFAULT_NEUTRAL_SETTINGS.cols_list.raw_columns);
    }

    if (loadedSettings.cols_widths && typeof loadedSettings.cols_widths === 'object') {
      setColumnWidths(loadedSettings.cols_widths as Record<string, number>);
    }

    if (loadedSettings.report_table?.value) {
      const initialValues: Record<string, string> = {};
      Object.entries(loadedSettings.report_table.value).forEach(([key, valObj]) => {
        if (valObj?.value) {
          initialValues[key] = valObj.value;
        }
      });
      setCellValues(initialValues);
    }
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

  const allAvailableColumns = useMemo<ColumnDefinition[]>(() => {
    const customCols: ColumnDefinition[] = Object.entries(addedColumns).map(([colKey, title]) => ({
      key: colKey,
      title,
      isAdded: true,
    }));
    return [...STANDARD_COLUMN_MAPPINGS, ...customCols];
  }, [addedColumns]);

  const activeColumns = useMemo<ColumnDefinition[]>(() => {
    const savedColsObj = fullSettings.cols_order_obj?.cols || {};

    return displayedKeys
      .map((key) => {
        const match = allAvailableColumns.find((c) => c.key === key);
        if (match) return match;

        if (key === 'risk_id' || key === 'riskid') return allAvailableColumns.find((c) => c.key === 'riskid_raw');
        if (key === 'risk_title' || key === 'arm_title') return allAvailableColumns.find((c) => c.key === 'risktitle');
        if (key === 'risk_description' || key === 'arm_description')
          return allAvailableColumns.find((c) => c.key === 'riskdescription');

        const savedColInfo = savedColsObj[key];
        if (savedColInfo?.title) {
          const isAdded = savedColInfo.css === 'added' || Boolean(addedColumns[key]);
          return { key, title: savedColInfo.title, isAdded };
        }

        return undefined;
      })
      .filter((c): c is ColumnDefinition => Boolean(c));
  }, [displayedKeys, allAvailableColumns, fullSettings, addedColumns]);

  const treeProcessedRows = useMemo<TreeProcessedRow[]>(() => {
    const baseTree = buildHierarchicalTreeRows(activeRowsByType, includeChildren);

    return baseTree.filter(({ row }) => {
      if (filterState.topRiskOnly && !(row.risktoprisk || row.css_toprisk?.includes('toprisk'))) {
        return false;
      }
      if (filterState.criticalityDiffersOnly && !isCriticalityDiffers(row)) {
        return false;
      }

      const rowStatus = (row.riskstatus || 'Draft').toLowerCase();
      const isStatusMatch = filterState.statuses.some((s) => s.toLowerCase() === rowStatus);
      if (!isStatusMatch) return false;

      const rowTrend = getRowTrendLabel(row);
      const isTrendMatch = filterState.trends.some((t) => t.toLowerCase() === rowTrend.toLowerCase());
      if (!isTrendMatch) return false;

      if (!isNewTopRiskMatch(row, filterState.newTopRisk)) return false;

      if (filterState.categories && filterState.categories.length > 0) {
        const rowCats: string[] = Array.isArray(row.categories) ? row.categories : [];
        if (!filterState.categories.some((c) => rowCats.includes(c))) return false;
      }

      if (filterState.impactCurrentCategory && filterState.impactCurrentCategory.length > 0) {
        const rowImpactCats: string[] = Array.isArray(row.impactCurrentCategory) ? row.impactCurrentCategory : [];
        if (!filterState.impactCurrentCategory.some((c) => rowImpactCats.includes(c))) return false;
      }

      if (searchText.trim()) {
        const query = searchText.toLowerCase().trim();
        const id = String(row.riskid_raw || row.pk_impact_id || '').toLowerCase();
        const title = String(row.risktitle || row.arm_title || '').toLowerCase();
        const desc = String(row.riskdescription || row.arm_description || '').toLowerCase();
        return id.includes(query) || title.includes(query) || desc.includes(query);
      }

      return true;
    });
  }, [activeRowsByType, includeChildren, filterState, searchText]);

  const sortedRows = useMemo<TreeProcessedRow[]>(() => {
    if (!sortConfig) return treeProcessedRows;

    return [...treeProcessedRows].sort((itemA, itemB) => {
      const a = itemA.row;
      const b = itemB.row;

      const pkIdA = a.pk_impact_id || Number(a.primary_key);
      const pkIdB = b.pk_impact_id || Number(b.primary_key);

      const col = activeColumns.find((c) => c.key === sortConfig.key);
      if (!col) return 0;

      let valA: unknown = col.isAdded ? cellValues[`${pkIdA}##${col.key}`] : a[col.key];
      let valB: unknown = col.isAdded ? cellValues[`${pkIdB}##${col.key}`] : b[col.key];

      if (!col.isAdded) {
        if (col.key === 'riskscore' || col.key === 'riskscore_display' || col.key === 'riskscore_display_level') {
          valA = a.riskscore_display ?? a.riskscore ?? a.arm_score ?? 0;
          valB = b.riskscore_display ?? b.riskscore ?? b.arm_score ?? 0;
        } else if (
          col.key === 'previous_score' ||
          col.key === 'previous_score_display' ||
          col.key === 'previous_ARM_impactscore_level'
        ) {
          valA = a.previous_score_display ?? a.previous_score ?? a.previous_ARM_impactscore_display ?? -999;
          valB = b.previous_score_display ?? b.previous_score ?? b.previous_ARM_impactscore_display ?? -999;
        } else if (
          col.key === 'ARM_tar_impactscore_display' ||
          col.key === 'ARM_tar_impactscore' ||
          col.key === 'ARM_tar_impactscore_level'
        ) {
          valA = a.ARM_tar_impactscore_display ?? a.ARM_tar_impactscore ?? -999;
          valB = b.ARM_tar_impactscore_display ?? b.ARM_tar_impactscore ?? -999;
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
  }, [treeProcessedRows, sortConfig, activeColumns, cellValues]);

  const handleColumnDoubleClick = (e: React.MouseEvent, colKey: string, colTitle: string) => {
    e.preventDefault();
    e.stopPropagation();

    const containerWidth = tableContainerRef.current?.clientWidth || 1000;
    let maxPx = measureTextWidth(colTitle, 'bold 12px Inter, sans-serif') + 40;

    sortedRows.forEach(({ row }) => {
      const pkId = row.pk_impact_id || Number(row.primary_key);
      let cellText = '';

      if (cellValues[`${pkId}##${colKey}`]) {
        cellText = cellValues[`${pkId}##${colKey}`];
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
    const csvData = sortedRows.map(({ row, resolvedChildrenIds, resolvedParentId }) => {
      const pkId = row.pk_impact_id || Number(row.primary_key);
      return activeColumns.map((col) => {
        if (col.isAdded) {
          const cellKey = `${pkId}##${col.key}`;
          return cellValues[cellKey] || '';
        }

        if (col.key === 'list_items') return resolvedChildrenIds;
        if (col.key === 'riskParent' || col.key === 'riskparent') return resolvedParentId;

        let rawVal: unknown = row[col.key];

        if (col.key === 'riskscore' || col.key === 'riskscore_display' || col.key === 'riskscore_display_level') {
          const scoreNum = row.riskscore_display ?? row.riskscore ?? row.arm_score ?? 0;
          rawVal = `M${scoreNum}`;
        } else if (
          col.key === 'previous_score' ||
          col.key === 'previous_score_display' ||
          col.key === 'previous_ARM_impactscore_level'
        ) {
          const prevNum = row.previous_score_display ?? row.previous_score ?? row.previous_ARM_impactscore_display;
          rawVal = prevNum != null ? `M${prevNum}` : '-';
        } else if (
          col.key === 'ARM_tar_impactscore_display' ||
          col.key === 'ARM_tar_impactscore' ||
          col.key === 'ARM_tar_impactscore_level'
        ) {
          const targetNum = row.ARM_tar_impactscore_display ?? row.ARM_tar_impactscore;
          rawVal = targetNum != null ? `M${targetNum}` : '-';
        } else if (col.key === 'occurrence_date') {
          rawVal = formatOccurrenceDate(rawVal);
        } else if (Array.isArray(rawVal)) {
          rawVal = rawVal.join(', ');
        }

        return String(rawVal ?? '-');
      });
    });

    const filename = `${dashboardId.replace(/[^a-zA-Z0-9_-]/g, '_')}_risk_table.csv`;
    exportToCSV(filename, headers, csvData);
  }, [activeColumns, sortedRows, cellValues, dashboardId]);

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
    const nextIndex = Object.keys(addedColumns).length + 1;
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

  const handleCellValueChange = (pkImpactId: number, colKey: string, value: string) => {
    const valueKey = `${pkImpactId}##${colKey}`;
    setCellValues((prev) => ({
      ...prev,
      [valueKey]: value,
    }));
  };

  const handleSaveSettings = useCallback(async () => {
    try {
      setIsSaving(true);

      const reportTableCol: Record<string, { col: string; action: string }> = {};
      Object.entries(addedColumns).forEach(([colKey, colTitle]) => {
        reportTableCol[colKey] = { col: colTitle, action: 'add' };
      });

      const reportTableValue: Record<string, { value: string; action: string }> = {};
      const validColKeys = new Set(Object.keys(addedColumns));

      Object.entries(cellValues).forEach(([cellKey, val]) => {
        const colKey = cellKey.split('##')[1];
        if (colKey && validColKeys.has(colKey) && val.trim()) {
          reportTableValue[cellKey] = { value: val, action: 'add' };
        }
      });

      const activeColsMap: Record<string, ColumnTitleObj> = {};
      activeColumns.forEach((c) => {
        activeColsMap[c.key] = {
          title: c.title,
          ...(c.isAdded ? { css: 'added' } : {}),
        };
      });

      const updatedSettings: DashboardSettings = {
        ...fullSettings,
        cols_widths: columnWidths,
        cols_obj: activeColsMap,
        cols_order_obj: {
          cols: activeColsMap,
          default: false,
        },
        cols_list: {
          ...(fullSettings.cols_list || DEFAULT_NEUTRAL_SETTINGS.cols_list!),
          added_columns: addedColumns,
          displayed_columns: activeColumns.map((c) => c.title),
          raw_columns: activeColumns.map((c) => c.key),
          state: fullSettings.cols_list?.state || 'validate',
        },
        report_table: {
          ...(fullSettings.report_table || {}),
          col: reportTableCol,
          value: reportTableValue,
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
      showToast('Risk Table settings saved successfully!', 'success');

      await refetchPayload();
    } catch (err: unknown) {
      const errObj = err as { message?: string };
      logger.error('DashboardTableTab', 'Failed to save settings', err);
      showToast(errObj?.message || 'Failed to save settings. Insufficient permissions.', 'error');
    }  {
      setIsSaving(false);
    }
  }, [
    addedColumns,
    cellValues,
    activeColumns,
    columnWidths,
    fullSettings,
    dashboardId,
    currentUserEmail,
    refetchPayload,
    showToast,
  ]);

  if (isLoadingPayload) {
    return (
      <div className="flex-1 bg-white flex items-center justify-center p-12 rounded-md border text-airbus-navy font-medium text-xs">
        <Loader2 className="h-5 w-5 animate-spin mr-2" /> Loading Report Table Data...
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
        filters={filterState}
        onFilterChange={setFilterState}
        onResetFilters={() => setFilterState(defaultRiskFilters)}
      />

      <div className="flex-1 flex flex-col p-3 h-full overflow-hidden gap-3">
        {/* Top Control Bar */}
        <div className="flex items-center gap-2 pb-2 text-xs shrink-0 border-b border-slate-200">
          <Button
            variant={isFilterOpen ? 'secondary' : 'ghost'}
            size="icon-xs"
            onClick={() => setIsFilterOpen(!isFilterOpen)}
            className="h-7 w-7 text-slate-700 cursor-pointer"
            title="Toggle Filters"
          >
            <Filter className="h-4 w-4" />
          </Button>

          <div className="w-52">
            <Input
              placeholder="Search by keywords"
              value={searchText}
              onChange={(e) => setSearchText(e.target.value)}
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
              Risk ({selectedType === 'Risk' ? sortedRows.length : risksList.length})/{risksList.length}
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
              Opp. ({selectedType === 'Opportunity' ? sortedRows.length : oppsList.length})/{oppsList.length}
            </Button>
          </div>
        </div>

        <div className="flex items-center justify-between shrink-0">
          <div className="flex items-center gap-3 text-xs">
            <ColumnSelectorPopover
              availableColumns={allAvailableColumns}
              activeColumns={activeColumns}
              onToggleVisibility={toggleColumnVisibility}
            />

            <div className="flex items-center gap-1.5 border-l border-slate-200 pl-3">
              <Checkbox
                id="include-children"
                checked={includeChildren}
                onCheckedChange={(c) => setIncludeChildren(Boolean(c))}
              />
              <label htmlFor="include-children" className="cursor-pointer text-slate-700 font-medium">
                Include children
              </label>
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

            <span className="text-slate-500 text-xs font-mono ml-1">
              Showing <strong>{sortedRows.length}</strong> {selectedType.toLowerCase()}(s)
            </span>
          </div>
        </div>

        {/* Scrollable Container with Relative (%) Widths & Excel-like Auto-Fit */}
        <div ref={tableContainerRef} className="flex-1 overflow-auto border border-slate-200 rounded-md bg-white">
          <Table className="text-xs table-fixed w-full">
            <TableHeader className="bg-airbus-navy text-white sticky top-0 z-10 shadow-xs">
              <TableRow className="hover:bg-transparent border-b border-slate-800">
                <TableHead className="w-[3%] text-center py-2 px-1 text-white font-semibold border-r border-slate-700/80">
                  #
                </TableHead>

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
              {sortedRows.length > 0 ? (
                sortedRows.map(({ row, indentDepth, resolvedChildrenIds, resolvedParentId }, idx) => {
                  const pkId = row.pk_impact_id || Number(row.primary_key);

                  return (
                    <TableRow key={row.primary_key || pkId} className="hover:bg-slate-50 transition-colors">
                      <TableCell className="p-2 text-center text-slate-400 font-mono text-[11px] select-text border-r border-slate-200/80">
                        {idx + 1}
                      </TableCell>

                      {activeColumns.map((col) => {
                        if (col.isAdded) {
                          const cellKey = `${pkId}##${col.key}`;
                          const val = cellValues[cellKey] || '';

                          return (
                            <TableCell key={col.key} className="p-1 border-r border-slate-200/80 last:border-r-0">
                              <Input
                                value={val}
                                placeholder="Enter value..."
                                onChange={(e) => handleCellValueChange(pkId, col.key, e.target.value)}
                                className="h-7 text-xs bg-slate-50/50 hover:bg-white border-transparent hover:border-slate-300 focus:border-airbus-blue focus:bg-white transition-all font-medium text-airbus-navy"
                              />
                            </TableCell>
                          );
                        }

                        if (col.key === 'riskid_raw' || col.key === 'riskid' || col.key === 'risk_id') {
                          const riskIdVal = String(row.riskid_raw || row.pk_impact_id || row.primary_key || '-');
                          const targetRiskParam = row.riskid_raw || row.pk_impact_id;

                          return (
                            <TableCell
                              key={col.key}
                              className="p-2 font-mono font-bold text-airbus-navy text-[11px] select-text border-r border-slate-200/80 last:border-r-0 truncate"
                              title={riskIdVal}
                            >
                              <div className="flex items-center gap-1.5 truncate">
                                <Button
                                  variant="ghost"
                                  size="icon-xs"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    navigate(
                                      `/dashboard/${encodeURIComponent(dashboardId)}/onepager?riskId=${targetRiskParam}&from=table`
                                    );
                                  }}
                                  className="h-5 w-5 p-0 text-slate-400 hover:text-[#DA1884] hover:bg-pink-50 rounded shrink-0 cursor-pointer"
                                  title="Open OnePager Report"
                                >
                                  <FileText className="h-3.5 w-3.5" />
                                </Button>
                                <span className="truncate">{riskIdVal}</span>
                              </div>
                            </TableCell>
                          );
                        }

                        if (col.key === 'risktitle' || col.key === 'arm_title') {
                          return (
                            <TableCell
                              key={col.key}
                              className="p-2 truncate font-medium text-slate-800 select-text border-r border-slate-200/80 last:border-r-0"
                              title={row.risktitle}
                            >
                              <div
                                className="flex items-center gap-1.5 truncate"
                                style={{ paddingLeft: `${indentDepth * 16}px` }}
                              >
                                {indentDepth > 0 && <CornerDownRight className="h-3 w-3 text-slate-400 shrink-0" />}
                                <span className="truncate">{row.risktitle}</span>
                              </div>
                            </TableCell>
                          );
                        }

                        if (
                          col.key === 'riskscore' ||
                          col.key === 'riskscore_display' ||
                          col.key === 'riskscore_display_level'
                        ) {
                          const scoreNum = row.riskscore_display ?? row.riskscore ?? row.arm_score ?? 0;
                          const lvl = getScoreLevelAndColor(scoreNum, selectedType);
                          return (
                            <TableCell
                              key={col.key}
                              className="p-1 text-center select-text border-r border-slate-200/80 last:border-r-0"
                            >
                              <Badge
                                variant="outline"
                                className={cn('font-mono text-[11px] px-2 py-0.5 border', lvl.badgeCss)}
                              >
                                {lvl.levelCode}
                              </Badge>
                            </TableCell>
                          );
                        }

                        if (
                          col.key === 'previous_score' ||
                          col.key === 'previous_score_display' ||
                          col.key === 'previous_ARM_impactscore_level'
                        ) {
                          const prevNum =
                            row.previous_score_display ?? row.previous_score ?? row.previous_ARM_impactscore_display;
                          const lvl = getScoreLevelAndColor(prevNum, selectedType);
                          return (
                            <TableCell
                              key={col.key}
                              className="p-1 text-center select-text border-r border-slate-200/80 last:border-r-0"
                            >
                              {prevNum != null ? (
                                <Badge
                                  variant="outline"
                                  className={cn('font-mono text-[11px] px-2 py-0.5 border', lvl.badgeCss)}
                                >
                                  {lvl.levelCode}
                                </Badge>
                              ) : (
                                <span className="text-slate-400">-</span>
                              )}
                            </TableCell>
                          );
                        }

                        if (
                          col.key === 'ARM_tar_impactscore_display' ||
                          col.key === 'ARM_tar_impactscore' ||
                          col.key === 'ARM_tar_impactscore_level'
                        ) {
                          const targetNum = row.ARM_tar_impactscore_display ?? row.ARM_tar_impactscore;
                          const lvl = getScoreLevelAndColor(targetNum, selectedType);
                          return (
                            <TableCell
                              key={col.key}
                              className="p-1 text-center select-text border-r border-slate-200/80 last:border-r-0"
                            >
                              {targetNum != null ? (
                                <Badge
                                  variant="outline"
                                  className={cn('font-mono text-[11px] px-2 py-0.5 border', lvl.badgeCss)}
                                >
                                  {lvl.levelCode}
                                </Badge>
                              ) : (
                                <span className="text-slate-400">-</span>
                              )}
                            </TableCell>
                          );
                        }

                        if (col.key === 'Trend' || col.key === 'month_trend') {
                          const trendConf = getTrendConfig(row[col.key]);
                          return (
                            <TableCell
                              key={col.key}
                              className="p-2 text-center select-text border-r border-slate-200/80 last:border-r-0"
                            >
                              <div className="flex items-center justify-center gap-1">
                                {trendConf.icon}
                                <span className={cn('text-[11px]', trendConf.css)}>{trendConf.label}</span>
                              </div>
                            </TableCell>
                          );
                        }

                        if (col.key === 'list_items') {
                          return (
                            <TableCell
                              key={col.key}
                              className="p-2 font-mono text-[11px] text-slate-600 truncate select-text border-r border-slate-200/80 last:border-r-0"
                            >
                              {resolvedChildrenIds || '-'}
                            </TableCell>
                          );
                        }

                        if (col.key === 'riskParent' || col.key === 'riskparent') {
                          return (
                            <TableCell
                              key={col.key}
                              className="p-2 font-mono text-[11px] text-[#DA1884] font-bold truncate select-text border-r border-slate-200/80 last:border-r-0"
                            >
                              {resolvedParentId || '-'}
                            </TableCell>
                          );
                        }

                        if (col.key === 'occurrence_date') {
                          return (
                            <TableCell
                              key={col.key}
                              className="p-2 font-mono text-[11px] text-slate-700 truncate select-text border-r border-slate-200/80 last:border-r-0"
                            >
                              {formatOccurrenceDate(row.occurrence_date)}
                            </TableCell>
                          );
                        }

                        let rawVal: unknown = row[col.key];
                        if (Array.isArray(rawVal)) {
                          rawVal = rawVal.join(', ');
                        }

                        const cellString = String(rawVal ?? '-');

                        return (
                          <TableCell
                            key={col.key}
                            className="p-2 truncate font-medium text-slate-700 select-text border-r border-slate-200/80 last:border-r-0"
                            title={cellString}
                          >
                            {cellString}
                          </TableCell>
                        );
                      })}

                      <TableCell className="p-0 border-l border-slate-100 bg-slate-50/30 sticky right-0" />
                    </TableRow>
                  );
                })
              ) : (
                <TableRow>
                  <TableCell colSpan={activeColumns.length + 2} className="h-32 text-center text-slate-400 text-xs">
                    No {selectedType.toLowerCase()}s match the current filter selection.
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
