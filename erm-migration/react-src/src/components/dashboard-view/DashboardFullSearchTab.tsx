import React, { useEffect, useState, useCallback, useRef } from 'react';
import { useToast } from '../../context/ToastContext';
import { useDashboardContext } from '../../context/DashboardContext';
import { RiskSearchPanel, type RiskSearchResult } from '../RiskSearchPanel';
import { client, CURRENT_ENV } from '../../client';
import { executeAddEditWorkflow } from '@fca0-enterprise-risk-management/sdk';
import { logger } from '../../utils/logger';
import { Save, Loader2, ShieldAlert, AlertCircle } from 'lucide-react';
import { Button } from '../../../@/components/ui/button';
import { Badge } from '../../../@/components/ui/badge';

const parseStringArray = (val: unknown): string[] => {
  if (!val) return [];
  if (Array.isArray(val)) return val.map((s) => String(s).trim()).filter(Boolean);
  if (typeof val === 'string') {
    const trimmed = val.trim();
    if (trimmed.startsWith('[')) {
      try {
        const parsed = JSON.parse(trimmed);
        if (Array.isArray(parsed)) {
          return parsed.map((s) => String(s).trim()).filter(Boolean);
        }
      } catch {
        // Fallback
      }
    }
    return trimmed
      .split(',')
      .map((s) => s.trim())
      .filter(Boolean);
  }
  return [];
};

export const DashboardFullSearchTab: React.FC<{ dashboardId: string }> = ({ dashboardId }) => {
  const { currentDashboard, currentUserEmail, canEdit, refetchPayload, allRiskRows } = useDashboardContext();
  const { showToast: showToastNotification } = useToast();

  const [selectedRisksMap, setSelectedRisksMap] = useState<Map<number, RiskSearchResult>>(new Map());
  const [isSaving, setIsSaving] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const isInitializedRef = useRef(false);

  // Re-initialize initial selected risks whenever dashboardId or allRiskRows changes
  useEffect(() => {
    isInitializedRef.current = false;
  }, [dashboardId]);

  useEffect(() => {
    if (allRiskRows && !isInitializedRef.current) {
      isInitializedRef.current = true;
      const initialMap = new Map<number, RiskSearchResult>();

      allRiskRows.forEach((r) => {
        const pkId = Number(r.pk_impact_id || r.primary_key || 0);
        if (pkId) {
          initialMap.set(pkId, {
            pkImpactId: pkId,
            riskId: String(r.riskid_raw || r.pk_impact_id || pkId),
            riskTitle: String(r.risktitle || r.arm_title || 'Untitled Risk'),
            riskDescription: String(r.riskdescription || r.arm_description || ''),
            siglumOwner: String(r.ownerDashboard || r.siglumOwner || r.siglum || ''),
            riskStatus: String(r.riskstatus || 'Active'),
            riskType: String(r.risktype || 'Risk'),
            riskScore: Number(r.riskscore ?? r.arm_score ?? 0),
          });
        }
      });

      setSelectedRisksMap(initialMap);
    }
  }, [allRiskRows]);

  useEffect(() => {
    logger.info('DashboardFullSearchTab', `Loaded Full Search Tab for: ${dashboardId}`);
  }, [dashboardId]);

  const handleToggleRiskSelection = useCallback((risk: RiskSearchResult) => {
    setSelectedRisksMap((prev) => {
      const next = new Map(prev);
      if (next.has(risk.pkImpactId)) {
        next.delete(risk.pkImpactId);
      } else {
        next.set(risk.pkImpactId, risk);
      }
      return next;
    });
  }, []);

  const handleToggleSelectAllVisible = useCallback((searchResults: RiskSearchResult[]) => {
    setSelectedRisksMap((prev) => {
      const next = new Map(prev);
      const allSelected = searchResults.length > 0 && searchResults.every((r) => prev.has(r.pkImpactId));

      searchResults.forEach((r) => {
        if (allSelected) {
          next.delete(r.pkImpactId);
        } else {
          next.set(r.pkImpactId, r);
        }
      });
      return next;
    });
  }, []);

  const handleSavePerimeter = useCallback(async () => {
    if (!canEdit || !currentDashboard) return;

    try {
      setIsSaving(true);
      setErrorMessage(null);

      const selectedImpactIds = Array.from(selectedRisksMap.keys())
        .map((id) => Number(id))
        .filter((id) => !isNaN(id));

      const rawCreationDate =
        currentDashboard.creationDate || (currentDashboard as Record<string, unknown>).creation_date;
      const creationTimestamp = new Date(String(rawCreationDate)).getTime() || Date.now();

      const ownerDashboard = currentDashboard.ownerDashboard
        ? currentDashboard.ownerDashboard.split(',').map((s: string) => s.trim()).filter(Boolean)
        : ['Airbus'];

      const finalReadEmails = parseStringArray(
        currentDashboard.permissionsReadNames_display ||
          (currentDashboard as Record<string, unknown>).permissionsReadNames,
      );
      const finalWriteEmails = parseStringArray(
        currentDashboard.permissionsWriteNames_display ||
          (currentDashboard as Record<string, unknown>).permissionsWriteNames,
      );
      const finalOwnerEmails = parseStringArray(
        currentDashboard.permissionsOwnerNames_display ||
          (currentDashboard as Record<string, unknown>).permissionsOwnerNames,
      );

      const existingSettingsString =
        typeof currentDashboard.settings === 'string'
          ? currentDashboard.settings
          : JSON.stringify(currentDashboard.settings || {});

      await client(executeAddEditWorkflow).applyAction({
        userMail: currentUserEmail,
        actionType: 'edit',
        env: CURRENT_ENV ?? "dev",
        creationDate: creationTimestamp,
        boardVersion: currentDashboard.boardVersion ?? 1,
        boardIteration: currentDashboard.boardIteration ?? 1,
        ownerDashboard,
        pkImpactIdList: selectedImpactIds,
        actionList: [],
        permissionsToAdd: [],
        permissionsToRemove: [],
        permissionsReadNames: finalReadEmails,
        permissionsWriteNames: finalWriteEmails,
        permissionsOwnerNames: finalOwnerEmails.length > 0 ? finalOwnerEmails : [currentUserEmail],
        boardTitle: currentDashboard.boardTitle || '',
        boardStatus: currentDashboard.boardStatus || 'Active',
        reportType: currentDashboard.reportType || 'Report',
        settings: existingSettingsString,
        validation: false,
      });

      await refetchPayload();
      showToastNotification('Risk changes saved successfully!', 'success');
    } catch (err: unknown) {
      const errObj = err as { message?: string };
      logger.error('DashboardFullSearchTab', 'Failed to save risk changes', err);
      const msg = errObj?.message || 'Failed to save risk risk changes.';
      setErrorMessage(msg);
      showToastNotification(msg, 'error');
    } finally {
      setIsSaving(false);
    }
  }, [canEdit, currentDashboard, selectedRisksMap, currentUserEmail, refetchPayload, showToastNotification]);

  return (
    <div className="flex-1 bg-white border border-slate-200 rounded-lg overflow-hidden flex flex-col shadow-xs h-full relative">
      {/* Top Action Bar for Perimeter Save */}
      <div className="p-3 bg-slate-50 border-b border-slate-200 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-3">

          {!canEdit && (
            <Badge variant="outline" className="text-[10px] bg-slate-100 text-slate-500 border-slate-300 gap-1">
              <ShieldAlert className="h-3 w-3 text-slate-400" /> Read Only
            </Badge>
          )}

          {errorMessage && (
            <div className="flex items-center gap-1.5 text-xs text-red-600 font-medium bg-red-50 px-2.5 py-1 rounded border border-red-200">
              <AlertCircle className="h-3.5 w-3.5 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}
        </div>

        <Button
          type="button"
          size="xs"
          onClick={handleSavePerimeter}
          disabled={!canEdit || isSaving}
          className="h-7 px-3 bg-[#DA1884] hover:bg-[#b0136a] text-white font-semibold text-xs rounded shadow-2xs cursor-pointer flex items-center gap-1.5 disabled:opacity-50"
        >
          {isSaving ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Save className="h-3.5 w-3.5" />}
          <span>Save Changes</span>
        </Button>
      </div>

      {/* Main Search Panel */}
      <div className="flex-1 flex flex-col min-h-0 overflow-hidden">
        <RiskSearchPanel
          selectedRisksMap={selectedRisksMap}
          setSelectedRisksMap={setSelectedRisksMap}
          onToggleRiskSelection={handleToggleRiskSelection}
          onToggleSelectAllVisible={handleToggleSelectAllVisible}
          dashboardId={dashboardId}
        />
      </div>

    </div>
  );
};
