import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { useToast } from '../../../context/ToastContext';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useDashboardContext, type ArmRiskRow } from '../../../context/DashboardContext';
import { OnePagerArmInfo } from './OnePagerArmInfo';
import { OnePagerHeatmap } from './OnePagerHeatmap';
import { OnePagerActionTracker } from './OnePagerActionTracker';
import { OnePagerWaterfall } from './OnePagerWaterfall';
import { OnePagerKeyMessages } from './OnePagerKeyMessages';
import { OnePagerHeader } from './OnePagerHeader';
import { SelectLayoutModal } from './SelectLayoutModal';
import { CustomSlotsDrawer } from './CustomSlotsDrawer';
import { client, CURRENT_ENV } from '../../../client';
import { 
  ermEditRiskSettingsMultiple, 
  ermEditRiskSettingsMultipleDev,
  ermEditRisk, 
  ermEditRiskDev 
} from '@fca0-enterprise-risk-management/sdk';
import {
  ResizablePanelGroup,
  ResizablePanel,
  ResizableHandle,
} from '../../../../@/components/ui/resizable';
import { GripVertical, FileText } from 'lucide-react';
import { cn } from '../../../../@/lib/utils';

// Typed wrapper alias for Shadcn ResizablePanelGroup
const ResizableGroup = ResizablePanelGroup as unknown as React.ComponentType<{
  children?: React.ReactNode;
  orientation?: 'horizontal' | 'vertical';
  direction?: 'horizontal' | 'vertical';
  className?: string;
  onLayout?: (_sizes: number[]) => void;
}>;

export type ComponentId =
  | 'armInfo'
  | 'heatmap'
  | 'waterfall'
  | 'actionTracker'
  | 'keyMessages'
  | 'assessmentJustification'
  | 'lastReviewComment';

export type SlotKey = 'slotTopLeft' | 'slotBottomLeft' | 'slotTopCenter' | 'slotBottomCenter' | 'slotRight';

export interface OnePagerProps {
  risk: ArmRiskRow | null;
  dashboardId: string;
  className?: string;
}

const PRESET_LAYOUTS: Record<number, Record<SlotKey, ComponentId>> = {
  1: {
    slotTopLeft: 'heatmap',
    slotBottomLeft: 'armInfo',
    slotTopCenter: 'waterfall',
    slotBottomCenter: 'actionTracker',
    slotRight: 'keyMessages',
  },
  2: {
    slotTopLeft: 'armInfo',
    slotBottomLeft: 'armInfo',
    slotTopCenter: 'heatmap',
    slotBottomCenter: 'actionTracker',
    slotRight: 'keyMessages',
  },
  3: {
    slotTopLeft: 'armInfo',
    slotBottomLeft: 'heatmap',
    slotTopCenter: 'waterfall',
    slotBottomCenter: 'actionTracker',
    slotRight: 'keyMessages',
  },
  4: {
    slotTopLeft: 'armInfo',
    slotBottomLeft: 'heatmap',
    slotTopCenter: 'waterfall',
    slotBottomCenter: 'actionTracker',
    slotRight: 'keyMessages',
  },
};

const DEFAULT_PANEL_SIZES: Record<string, Record<string, number[]>> = {
  layout1: {
    mainHorizontal: [68, 32],
    leftVertical: [58, 42],
    topLeftHorizontal: [50, 50],
    bottomLeftHorizontal: [50, 50],
  },
  layout2: {
    mainHorizontal: [28, 44, 28],
    centerVertical: [50, 50],
  },
  layout3_page1: {
    mainHorizontal: [68, 32],
    leftVertical: [50, 50],
    topHorizontal: [50, 50],
  },
  layout3_page2: {
    mainHorizontal: [68, 32],
    leftVertical: [50, 50],
  },
  layout4: {
    mainHorizontal: [68, 32],
    leftVertical: [50, 50],
    topHorizontal: [50, 50],
    bottomHorizontal: [50, 50],
  },
  keyMessagesStack_both: {
    vertical: [50, 25, 25],
  },
  keyMessagesStack_just: {
    vertical: [65, 35],
  },
  keyMessagesStack_lrc: {
    vertical: [65, 35],
  },
};

const ALL_COMPONENTS: { id: ComponentId; title: string; desc: string }[] = [
  { id: 'armInfo', title: 'ARM Information', desc: 'Description, Causes, and Effects' },
  { id: 'heatmap', title: 'Heatmap / Coldmap', desc: 'Matrix positioning and target' },
  { id: 'waterfall', title: 'Waterfall Trajectory', desc: 'Historical & projected score trend' },
  { id: 'actionTracker', title: 'Action Tracker', desc: 'Response plans and status tracking' },
  { id: 'keyMessages', title: 'Executive Key Messages', desc: 'Rich text summary and validation' },
  { id: 'assessmentJustification', title: 'Assessment Justification', desc: 'Assessment justification notes' },
  { id: 'lastReviewComment', title: 'Last Review Comment', desc: 'Last review board comments' },
];

export const OnePager: React.FC<OnePagerProps> = ({ risk: initialPropRisk, dashboardId, className }) => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const { armRoPayload, canEdit, refetchPayload, allRiskRows } = useDashboardContext();
  const { showToast } = useToast();

  const fromTab = searchParams.get('from') || 'maps';

  const [activeRisk, setActiveRisk] = useState<ArmRiskRow | null>(initialPropRisk);
  
  const [isEditMode, setIsEditMode] = useState<boolean>(false);

  // Helper to extract Risk Primary Key
  const getRiskPk = useCallback((r: ArmRiskRow | null) => {
    if (!r) return '';
    return String(r.riskid_raw || r.pk_impact_id || r.PKImpactID || r.primary_key || r.riskObjectId || '');
  }, []);

  // Sync activeRisk with incoming prop / refetched payload while preserving currently selected risk
  useEffect(() => {
    const currentActivePk = getRiskPk(activeRisk);
    
    if (currentActivePk && allRiskRows.length > 0) {
      const matchingUpdatedRisk = allRiskRows.find((r) => getRiskPk(r) === currentActivePk);
      if (matchingUpdatedRisk) {
        setActiveRisk(matchingUpdatedRisk);
        return;
      }
    }

    setActiveRisk(initialPropRisk);
  }, [initialPropRisk, allRiskRows, getRiskPk]);

  // Handle risk selection from dropdown: updates state AND URL search params
  const handleSelectRisk = useCallback((selectedRisk: ArmRiskRow) => {
    setActiveRisk(selectedRisk);
    const selectedPk = getRiskPk(selectedRisk);
    if (selectedPk) {
      setSearchParams({ riskId: selectedPk, from: fromTab }, { replace: true });
    }
  }, [getRiskPk, setSearchParams, fromTab]);

  const risk = activeRisk;

  const initialLayoutSettings = useMemo(() => {
    try {
      const rawSettings = risk?.print_settings || risk?.settings || armRoPayload?.settings;
      const parsed = typeof rawSettings === 'string' ? JSON.parse(rawSettings) : rawSettings || {};
      
      const ps = parsed?.print_settings?.print_settings || parsed?.print_settings || parsed;
      const op = parsed?.onepager || ps?.onepager || {};
      const wf = parsed?.waterfall || ps?.waterfall || {};

      const rawLayout =
        op?.layout ||
        parsed?.selectedLayout ||
        parsed?.layoutNumber ||
        parsed?.layout ||
        ps?.selectedLayout ||
        ps?.layoutNumber ||
        ps?.layout ||
        ps?.onepager?.layout ||
        1;

      const layoutNum = Number(rawLayout) || 1;

      const customSlots =
        (risk as Record<string, unknown>)?.onepager_slots ||
        parsed?.onepager_slots ||
        ps?.onepager_slots ||
        PRESET_LAYOUTS[layoutNum] ||
        PRESET_LAYOUTS[1];

      const pageAss = String(
        op?.page_assessment ||
        ps?.page_assessment ||
        parsed?.page_assessment ||
        'assessment_page1'
      );

      const pageLrc = String(
        op?.['page_last-review-comment'] ||
        ps?.['page_last-review-comment'] ||
        parsed?.['page_last-review-comment'] ||
        'last-review-comment_page2'
      );

      const customComps = (
        parsed?.custom_components ||
        ps?.custom_components ||
        ['heatmap', 'waterfall', 'keyMessages']
      ) as ComponentId[];

      const rawSizes = parsed?.panel_sizes || ps?.panel_sizes || {};
      
      const storedSizes: Record<string, Record<string, number[]>> = {
        layout1: { ...DEFAULT_PANEL_SIZES.layout1, ...(rawSizes.layout1 || {}) },
        layout2: { ...DEFAULT_PANEL_SIZES.layout2, ...(rawSizes.layout2 || {}) },
        layout3_page1: { ...DEFAULT_PANEL_SIZES.layout3_page1, ...(rawSizes.layout3_page1 || {}) },
        layout3_page2: { ...DEFAULT_PANEL_SIZES.layout3_page2, ...(rawSizes.layout3_page2 || {}) },
        layout4: { ...DEFAULT_PANEL_SIZES.layout4, ...(rawSizes.layout4 || {}) },
        keyMessagesStack_both: { ...DEFAULT_PANEL_SIZES.keyMessagesStack_both, ...(rawSizes.keyMessagesStack_both || {}) },
        keyMessagesStack_just: { ...DEFAULT_PANEL_SIZES.keyMessagesStack_just, ...(rawSizes.keyMessagesStack_just || {}) },
        keyMessagesStack_lrc: { ...DEFAULT_PANEL_SIZES.keyMessagesStack_lrc, ...(rawSizes.keyMessagesStack_lrc || {}) },
      };

      const showAss = Boolean(
        op?.display_assessment ??
        parsed?.showAssessmentJustification ??
        ps?.showAssessmentJustification ??
        ps?.display_assessment ??
        true
      );

      const showLrc = Boolean(
        op?.display_lrc ??
        parsed?.showLastReviewComment ??
        ps?.showLastReviewComment ??
        ps?.display_lrc ??
        true
      );

      return {
        selectedLayout: layoutNum,
        slots: customSlots as Record<SlotKey, ComponentId>,
        customComponents: customComps,
        panelSizes: storedSizes,
        showAssessmentJustification: showAss,
        assessmentPages: {
          page1: pageAss.includes('page1'),
          page2: pageAss.includes('page2'),
        },
        showLastReviewComment: showLrc,
        reviewCommentPages: {
          page1: pageLrc.includes('page1'),
          page2: pageLrc.includes('page2'),
        },
        waterfallMethod: String(wf?.method || 'target'),
        waterfallDateRange: (wf?.date_range || ['2022-09-21', '2026-10-21']) as [string, string],
      };
    } catch {
      return {
        selectedLayout: 1,
        slots: PRESET_LAYOUTS[1],
        customComponents: ['heatmap', 'waterfall', 'keyMessages'] as ComponentId[],
        panelSizes: DEFAULT_PANEL_SIZES,
        showAssessmentJustification: true,
        assessmentPages: { page1: true, page2: false },
        showLastReviewComment: true,
        reviewCommentPages: { page1: false, page2: true },
        waterfallMethod: 'target',
        waterfallDateRange: ['2022-09-21', '2026-10-21'] as [string, string],
      };
    }
  }, [risk, armRoPayload]);

  const [selectedLayout, setSelectedLayout] = useState<number>(initialLayoutSettings.selectedLayout);
  const [activeSlots, setActiveSlots] = useState<Record<SlotKey, ComponentId>>(initialLayoutSettings.slots);
  const [customComponents, setCustomComponents] = useState<ComponentId[]>(initialLayoutSettings.customComponents);
  const [panelSizes, setPanelSizes] = useState<Record<string, Record<string, number[]>>>(
    initialLayoutSettings.panelSizes
  );

  const [layout3ActivePage, setLayout3ActivePage] = useState<'page1' | 'page2'>('page1');

  const [showAssessmentJustification, setShowAssessmentJustification] = useState<boolean>(
    initialLayoutSettings.showAssessmentJustification
  );
  const [assessmentPages, setAssessmentPages] = useState<{ page1: boolean; page2: boolean }>(
    initialLayoutSettings.assessmentPages
  );

  const [showLastReviewComment, setShowLastReviewComment] = useState<boolean>(
    initialLayoutSettings.showLastReviewComment
  );
  const [reviewCommentPages, setReviewCommentPages] = useState<{ page1: boolean; page2: boolean }>(
    initialLayoutSettings.reviewCommentPages
  );

  const [activeWaterfallMethod, setActiveWaterfallMethod] = useState<string>(initialLayoutSettings.waterfallMethod);
  const [activeWaterfallDateRange, setActiveWaterfallDateRange] = useState<[string, string]>(
    initialLayoutSettings.waterfallDateRange
  );

  const handleCancelEdit = useCallback(() => {
    setSelectedLayout(initialLayoutSettings.selectedLayout);
    setActiveSlots(initialLayoutSettings.slots);
    setCustomComponents(initialLayoutSettings.customComponents);
    setPanelSizes(initialLayoutSettings.panelSizes);
    setShowAssessmentJustification(initialLayoutSettings.showAssessmentJustification);
    setAssessmentPages(initialLayoutSettings.assessmentPages);
    setShowLastReviewComment(initialLayoutSettings.showLastReviewComment);
    setReviewCommentPages(initialLayoutSettings.reviewCommentPages);
    setActiveWaterfallMethod(initialLayoutSettings.waterfallMethod);
    setActiveWaterfallDateRange(initialLayoutSettings.waterfallDateRange);
    setModalPendingLayout(initialLayoutSettings.selectedLayout);
    setIsEditMode(false);
  }, [initialLayoutSettings]);

  const [showSelectLayoutDialog, setShowSelectLayoutDialog] = useState(false);
  const [modalPendingLayout, setModalPendingLayout] = useState<number>(initialLayoutSettings.selectedLayout);
  const [showCustomDrawer, setShowCustomDrawer] = useState(false);
  const [draggedComponent, setDraggedComponent] = useState<ComponentId | null>(null);
  const [isSaving, setIsSaving] = useState(false);

  useEffect(() => {
    setSelectedLayout(initialLayoutSettings.selectedLayout);
    setActiveSlots(initialLayoutSettings.slots);
    setCustomComponents(initialLayoutSettings.customComponents);
    setPanelSizes(initialLayoutSettings.panelSizes);
    setShowAssessmentJustification(initialLayoutSettings.showAssessmentJustification);
    setAssessmentPages(initialLayoutSettings.assessmentPages);
    setShowLastReviewComment(initialLayoutSettings.showLastReviewComment);
    setReviewCommentPages(initialLayoutSettings.reviewCommentPages);
    setModalPendingLayout(initialLayoutSettings.selectedLayout);
  }, [initialLayoutSettings]);

  const handlePanelResize = (layoutKey: string, groupKey: string, sizes: number[]) => {
    setPanelSizes((prev) => ({
      ...prev,
      [layoutKey]: {
        ...(prev[layoutKey] || {}),
        [groupKey]: sizes,
      },
    }));
  };

  const handleWaterfallSettingsChange = useCallback((method: string, dateRange: [string, string]) => {
    setActiveWaterfallMethod((prev) => (prev !== method ? method : prev));
    setActiveWaterfallDateRange((prev) =>
      prev[0] !== dateRange[0] || prev[1] !== dateRange[1] ? dateRange : prev
    );
  }, []);

  const handleBackToOriginTab = () => {
    navigate(`/dashboard/${encodeURIComponent(dashboardId)}/${fromTab}`);
  };

  const getRiskPrimaryKey = (row: ArmRiskRow): string => {
    return String(row.riskObjectId || '');
  };

  const handlePersistLayout = useCallback(
    async (
      targetLayoutNum: number,
      slotsToSave: Record<SlotKey, ComponentId>,
      customCompsToSave: ComponentId[] = customComponents,
      justificationVal: boolean = showAssessmentJustification,
      reviewCommentVal: boolean = showLastReviewComment,
      assPagesVal = assessmentPages,
      revPagesVal = reviewCommentPages,
      saveAll: boolean = false
    ) => {
      if (!risk || !canEdit) return;

      try {
        setIsSaving(true);

        const rawRiskSettings = risk.print_settings || risk.settings;
        const existingSettings =
          typeof rawRiskSettings === 'string'
            ? JSON.parse(rawRiskSettings || '{}')
            : rawRiskSettings || {};

        if (existingSettings.print_settings) {
          delete existingSettings.print_settings;
        }

        const pageAssStr =
          assPagesVal.page1 && assPagesVal.page2
            ? 'assessment_page1 assessment_page2'
            : assPagesVal.page2
            ? 'assessment_page2'
            : 'assessment_page1';

        const pageLrcStr =
          revPagesVal.page1 && revPagesVal.page2
            ? 'last-review-comment_page1 last-review-comment_page2'
            : revPagesVal.page2
            ? 'last-review-comment_page2'
            : 'last-review-comment_page1';

        const updatedSettings = {
          ...existingSettings,
          selectedLayout: targetLayoutNum,
          layoutNumber: targetLayoutNum,
          showAssessmentJustification: justificationVal,
          showLastReviewComment: reviewCommentVal,
          onepager: {
            ...(existingSettings.onepager || {}),
            layout: String(targetLayoutNum),
            display_assessment: justificationVal,
            display_lrc: reviewCommentVal,
            page_assessment: pageAssStr,
            'page_last-review-comment': pageLrcStr,
          },
          waterfall: {
            ...(existingSettings.waterfall || {}),
            method: activeWaterfallMethod,
            date_range: activeWaterfallDateRange,
          },
          onepager_slots: slotsToSave,
          custom_components: customCompsToSave,
          panel_sizes: panelSizes,
        };

        const printSettingsJsonString = JSON.stringify(updatedSettings);

        // Environment switching logic
        const isMaster = CURRENT_ENV === 'master';
        const targetAction = isMaster ? ermEditRiskSettingsMultiple : ermEditRiskSettingsMultipleDev;
        const inputParamKey = isMaster ? 'erm_risk_user_input' : 'erm_risk_user_input_dev';

        let batchItems: Array<Record<string, unknown>> = [];

        if (saveAll) {
          const targetRows = allRiskRows.length > 0 ? allRiskRows : [risk];
          batchItems = targetRows
            .map((r) => getRiskPrimaryKey(r))
            .filter((pk) => pk.length > 0)
            .map((pk) => ({
              [inputParamKey]: [pk],
              print_settings: printSettingsJsonString,
            }));
        } else {
          const singlePk = getRiskPrimaryKey(risk);
          batchItems = [
            {
              [inputParamKey]: [singlePk],
              print_settings: printSettingsJsonString,
            },
          ];
        }

        await (client(targetAction as any) as any).batchApplyAction(batchItems, {
          $returnEdits: true,
        });

        const currentRiskId = String(risk.riskid_raw || risk.pk_impact_id || risk.PKImpactID || '');
        if (saveAll) {
          showToast(`Layout settings applied & saved to all ${batchItems.length} risks.`, 'success');
        } else {
          showToast(`Layout settings saved for risk #${currentRiskId}.`, 'success');
        }

        setIsEditMode(false);

        setTimeout(async () => {
          await refetchPayload();
        }, 1500);

      } catch (err) {
        console.error('Failed to save layout settings:', err);
        showToast('Failed to save layout settings. Please try again.', 'error');
      } finally {
        setIsSaving(false);
      }
    },
    [
      risk,
      canEdit,
      allRiskRows,
      showAssessmentJustification,
      showLastReviewComment,
      assessmentPages,
      reviewCommentPages,
      customComponents,
      activeWaterfallMethod,
      activeWaterfallDateRange,
      panelSizes,
      refetchPayload,
      showToast,
    ]
  );

  const handleApplyModalLayout = () => {
    setSelectedLayout(modalPendingLayout);

    if (modalPendingLayout >= 1 && modalPendingLayout <= 3) {
      setActiveSlots(PRESET_LAYOUTS[modalPendingLayout]);
    }

    setShowSelectLayoutDialog(false);
  };

  const handleHeaderSave = useCallback(() => {
    handlePersistLayout(
      selectedLayout,
      activeSlots,
      customComponents,
      showAssessmentJustification,
      showLastReviewComment,
      assessmentPages,
      reviewCommentPages,
      false
    );
  }, [
    selectedLayout,
    activeSlots,
    customComponents,
    showAssessmentJustification,
    showLastReviewComment,
    assessmentPages,
    reviewCommentPages,
    handlePersistLayout,
  ]);

  const handleHeaderSaveAll = useCallback(() => {
    handlePersistLayout(
      selectedLayout,
      activeSlots,
      customComponents,
      showAssessmentJustification,
      showLastReviewComment,
      assessmentPages,
      reviewCommentPages,
      true
    );
  }, [
    selectedLayout,
    activeSlots,
    customComponents,
    showAssessmentJustification,
    showLastReviewComment,
    assessmentPages,
    reviewCommentPages,
    handlePersistLayout,
  ]);

  const handleToggleCustomComponent = (id: ComponentId) => {
    setCustomComponents((prev) =>
      prev.includes(id) ? prev.filter((c) => c !== id) : [...prev, id]
    );
  };

  const handleToggleJustificationFromDrawer = () => {
    setShowAssessmentJustification((prev) => !prev);
  };

  const handleToggleLastReviewCommentFromDrawer = () => {
    setShowLastReviewComment((prev) => !prev);
  };

  const handleApplyCustomDrawer = () => {
    setShowCustomDrawer(false);
  };

  const handleDragStart = (e: React.DragEvent, componentId: ComponentId) => {
    if (selectedLayout !== 4) return;
    setDraggedComponent(componentId);
    e.dataTransfer.setData('text/plain', componentId);
    e.dataTransfer.effectAllowed = 'move';
  };

  const handleDragOver = (e: React.DragEvent) => {
    if (selectedLayout !== 4) return;
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = (targetComponentId: ComponentId, e: React.DragEvent) => {
    if (selectedLayout !== 4) return;
    e.preventDefault();

    const sourceComponent = draggedComponent || (e.dataTransfer.getData('text/plain') as ComponentId);
    if (!sourceComponent || sourceComponent === targetComponentId) return;

    const sourceIdx = customComponents.indexOf(sourceComponent);
    const targetIdx = customComponents.indexOf(targetComponentId);

    if (sourceIdx !== -1 && targetIdx !== -1) {
      const nextCustom = [...customComponents];
      nextCustom[sourceIdx] = targetComponentId;
      nextCustom[targetIdx] = sourceComponent;

      setCustomComponents(nextCustom);
    }
    setDraggedComponent(null);
  };

  const handleSaveLink = useCallback(
    async (newLink: string) => {
      if (!risk || !canEdit) return;

      try {
        setIsSaving(true);
        const singlePk = getRiskPrimaryKey(risk);

        // Environment switching logic
        const isMaster = CURRENT_ENV === 'master';
        const targetAction = isMaster ? ermEditRisk : ermEditRiskDev;
        const inputParamKey = isMaster ? 'ErmRiskUserInput' : 'ErmRiskUserInputDev';

        await (client(targetAction as any) as any).batchApplyAction(
          [
            {
              [inputParamKey]: singlePk,
              link: newLink,
              updated_on: new Date().toISOString(),
            },
          ],
          {
            $returnEdits: true,
          }
        );

        showToast('Google Drive link updated successfully!', 'success');

        setTimeout(async () => {
          await refetchPayload();
        }, 1200);
      } catch (err) {
        console.error('Failed to update Google Drive link:', err);
        showToast('Failed to update Google Drive link.', 'error');
      }
      finally {
        setIsSaving(false);
      }
    },
    [risk, canEdit, refetchPayload, showToast]
  );

  const assessmentJustificationText = useMemo(() => {
    if (!risk) return '';
    return String(
      risk.assessment_justification ||
      'No assessment justification recorded for this risk.'
    );
  }, [risk]);

  const lastReviewCommentText = useMemo(() => {
    if (!risk) return '';
    return String(
      risk.lastreviewcomments ||
      'No review comment recorded during the last board review.'
    );
  }, [risk]);

  const riskPkId = Number(risk?.pk_impact_id || risk?.primary_key || risk?.riskid_raw || 0);

  const renderComponentInstance = (componentId: ComponentId) => {
    if (!risk) return null;

    const shouldRenderJustification =
      showAssessmentJustification &&
      (selectedLayout !== 3 || assessmentPages[layout3ActivePage]);

    const shouldRenderReviewComment =
      showLastReviewComment &&
      (selectedLayout !== 3 || reviewCommentPages[layout3ActivePage]);

    switch (componentId) {
      case 'armInfo':
        return <OnePagerArmInfo risk={risk} className="h-full w-full border-none rounded-none p-1.5" />;
      case 'heatmap':
        return <OnePagerHeatmap risk={risk} className="h-full w-full border-none rounded-none p-1" />;
      case 'waterfall':
        return (
          <OnePagerWaterfall
            risk={risk}
            className="h-full w-full border-none rounded-none p-1"
            onSettingsChange={handleWaterfallSettingsChange}
          />
        );
      case 'actionTracker':
        return <OnePagerActionTracker risk={risk} dashboardId={dashboardId} isEditMode={isEditMode} className="h-full w-full border-none rounded-none p-1" />;
      
      case 'assessmentJustification':
        return (
          <div className="h-full w-full flex flex-col bg-white border border-slate-200 rounded-sm p-3 overflow-hidden">
            <div className="text-center py-1 bg-slate-50 border-b border-slate-200 shrink-0 select-none mb-2">
              <h2 className="text-[11px] font-extrabold text-[#00205B] tracking-wider uppercase">
                Assessment Justification
              </h2>
            </div>
            <div className="flex-1 overflow-y-auto text-xs text-slate-700 leading-relaxed bg-slate-50/50 p-2.5 rounded border border-slate-200/80">
              {assessmentJustificationText}
            </div>
          </div>
        );

      case 'lastReviewComment':
        return (
          <div className="h-full w-full flex flex-col bg-white border border-slate-200 rounded-sm p-3 overflow-hidden">
            <div className="text-center py-1 bg-slate-50 border-b border-slate-200 shrink-0 select-none mb-2">
              <h2 className="text-[11px] font-extrabold text-[#00205B] tracking-wider uppercase">
                Last Review Comment
              </h2>
            </div>
            <div className="flex-1 overflow-y-auto text-xs text-slate-700 leading-relaxed bg-slate-50/50 p-2.5 rounded border border-slate-200/80">
              {lastReviewCommentText}
            </div>
          </div>
        );

      case 'keyMessages': {
        const hasJust = shouldRenderJustification;
        const hasLrc = shouldRenderReviewComment;

        if (!hasJust && !hasLrc) {
          return (
            <div className="flex-1 flex flex-col h-full w-full overflow-hidden bg-white">
              <OnePagerKeyMessages risk={risk} isEditMode={isEditMode} className="flex-1 border-none rounded-none p-1 min-h-0" />
            </div>
          );
        }

        const stackGroupKey =
          hasJust && hasLrc
            ? 'keyMessagesStack_both'
            : hasJust
            ? 'keyMessagesStack_just'
            : 'keyMessagesStack_lrc';

        const currentStackSizes = panelSizes[stackGroupKey]?.vertical;

        // Dynamic group key guarantees that react-resizable-panels remounts with loaded defaultSize values
        const groupInstanceKey = `${stackGroupKey}_risk${riskPkId}_${isEditMode ? 'edit' : 'view'}`;

        if (hasJust && hasLrc) {
          return (
            <div className="flex-1 flex flex-col h-full w-full overflow-hidden bg-white">
              <ResizableGroup
                key={groupInstanceKey}
                orientation="vertical"
                className="h-full w-full"
                onLayout={(s: number[]) => handlePanelResize(stackGroupKey, 'vertical', s)}
              >
                <ResizablePanel
                  id="km-panel"
                  defaultSize={currentStackSizes?.[0] ?? 50}
                  minSize={20}
                >
                  <OnePagerKeyMessages risk={risk} isEditMode={isEditMode} className="h-full border-none rounded-none p-1 min-h-0" />
                </ResizablePanel>

                <ResizableHandle withHandle />

                <ResizablePanel
                  id="just-panel"
                  defaultSize={currentStackSizes?.[1] ?? 25}
                  minSize={15}
                >
                  <div className="h-full w-full p-2 border-t border-slate-200 bg-slate-50/80 flex flex-col overflow-hidden text-xs">
                    <span className="font-extrabold text-[#00205B] block mb-1 uppercase text-[10px] tracking-wider shrink-0 select-none">
                      Assessment Justification
                    </span>
                    <p className="flex-1 text-slate-700 leading-relaxed text-[11px] bg-white p-2 rounded border border-slate-200 overflow-y-auto min-h-0">
                      {assessmentJustificationText}
                    </p>
                  </div>
                </ResizablePanel>

                <ResizableHandle withHandle />

                <ResizablePanel
                  id="lrc-panel"
                  defaultSize={currentStackSizes?.[2] ?? 25}
                  minSize={15}
                >
                  <div className="h-full w-full p-2 border-t border-slate-200 bg-slate-50/80 flex flex-col overflow-hidden text-xs">
                    <span className="font-extrabold text-[#00205B] block mb-1 uppercase text-[10px] tracking-wider shrink-0 select-none">
                      Last Review Comment
                    </span>
                    <p className="flex-1 text-slate-700 leading-relaxed text-[11px] bg-white p-2 rounded border border-slate-200 overflow-y-auto min-h-0">
                      {lastReviewCommentText}
                    </p>
                  </div>
                </ResizablePanel>
              </ResizableGroup>
            </div>
          );
        }

        return (
          <div className="flex-1 flex flex-col h-full w-full overflow-hidden bg-white">
            <ResizableGroup
              key={groupInstanceKey}
              orientation="vertical"
              className="h-full w-full"
              onLayout={(s: number[]) => handlePanelResize(stackGroupKey, 'vertical', s)}
            >
              <ResizablePanel
                id="km-panel-single"
                defaultSize={currentStackSizes?.[0] ?? 65}
                minSize={20}
              >
                <OnePagerKeyMessages risk={risk} isEditMode={isEditMode} className="h-full border-none rounded-none p-1 min-h-0" />
              </ResizablePanel>

              <ResizableHandle withHandle />

              <ResizablePanel
                id={hasJust ? 'just-panel-single' : 'lrc-panel-single'}
                defaultSize={currentStackSizes?.[1] ?? 35}
                minSize={15}
              >
                <div className="h-full w-full p-2 border-t border-slate-200 bg-slate-50/80 flex flex-col overflow-hidden text-xs">
                  <span className="font-extrabold text-[#00205B] block mb-1 uppercase text-[10px] tracking-wider shrink-0 select-none">
                    {hasJust ? 'Assessment Justification' : 'Last Review Comment'}
                  </span>
                  <p className="flex-1 text-slate-700 leading-relaxed text-[11px] bg-white p-2 rounded border border-slate-200 overflow-y-auto min-h-0">
                    {hasJust ? assessmentJustificationText : lastReviewCommentText}
                  </p>
                </div>
              </ResizablePanel>
            </ResizableGroup>
          </div>
        );
      }
    }
  };

  if (!risk) {
    return (
      <div className="flex-1 bg-white flex flex-col items-center justify-center p-12 text-slate-400 text-xs font-mono">
        <FileText className="h-8 w-8 mb-2 text-slate-300" />
        No risk selected. Select a risk from the Heatmap to render OnePager.
      </div>
    );
  }

  const renderSlotCell = (componentIdOverride?: ComponentId, slotKeyOverride?: SlotKey) => {
    const slotKey = slotKeyOverride || 'slotTopLeft';
    const componentId = componentIdOverride || activeSlots[slotKey];
    const isDragging = draggedComponent === componentId;
    const isCustom = selectedLayout === 4;

    return (
      <div
        className={cn(
          'h-full w-full min-h-0 min-w-0 bg-white flex flex-col transition-opacity overflow-hidden relative group',
          isDragging && 'opacity-40'
        )}
        onDragOver={handleDragOver}
        onDrop={(e) => handleDrop(componentId, e)}
      >
        {isCustom && canEdit && isEditMode && (
          <div
            draggable
            onDragStart={(e) => handleDragStart(e, componentId)}
            className="absolute top-1.5 left-1/2 -translate-x-1/2 z-30 opacity-0 group-hover:opacity-100 transition-opacity duration-150 cursor-grab active:cursor-grabbing bg-slate-900/90 hover:bg-[#DA1884] text-white p-1 rounded-md shadow-md border border-slate-700/60 flex items-center justify-center select-none"
            title="Drag to swap panel position"
          >
            <GripVertical className="h-3.5 w-3.5" />
          </div>
        )}

        <div className="flex-1 h-full w-full min-h-0 min-w-0 overflow-hidden">
          {renderComponentInstance(componentId)}
        </div>
      </div>
    );
  };

  const renderCustomLayout4 = () => {
    const activeComps = customComponents;

    if (activeComps.length === 0) {
      return (
        <div className="h-full w-full bg-slate-50 flex flex-col items-center justify-center p-8 text-slate-400 text-xs font-mono select-none">
          No components selected. Use &quot;Customize Layout&quot; to add components.
        </div>
      );
    }

    if (activeComps.length === 1) {
      return renderSlotCell(activeComps[0]);
    }

    if (activeComps.length === 2) {
      return (
        <ResizableGroup
          orientation="horizontal"
          className="h-full w-full"
          onLayout={(s: number[]) => handlePanelResize('layout4', 'mainHorizontal', s)}
        >
          <ResizablePanel defaultSize={panelSizes.layout4?.mainHorizontal?.[0] ?? 50} minSize={25}>
            {renderSlotCell(activeComps[0])}
          </ResizablePanel>
          <ResizableHandle withHandle />
          <ResizablePanel defaultSize={panelSizes.layout4?.mainHorizontal?.[1] ?? 50} minSize={25}>
            {renderSlotCell(activeComps[1])}
          </ResizablePanel>
        </ResizableGroup>
      );
    }

    if (activeComps.length === 3) {
      return (
        <ResizableGroup
          orientation="horizontal"
          className="h-full w-full"
          onLayout={(s: number[]) => handlePanelResize('layout4', 'mainHorizontal', s)}
        >
          <ResizablePanel defaultSize={panelSizes.layout4?.mainHorizontal?.[0] ?? 68} minSize={40}>
            <ResizableGroup
              orientation="vertical"
              onLayout={(s: number[]) => handlePanelResize('layout4', 'leftVertical', s)}
            >
              <ResizablePanel defaultSize={panelSizes.layout4?.leftVertical?.[0] ?? 50} minSize={25}>
                {renderSlotCell(activeComps[0])}
              </ResizablePanel>
              <ResizableHandle withHandle />
              <ResizablePanel defaultSize={panelSizes.layout4?.leftVertical?.[1] ?? 50} minSize={25}>
                {renderSlotCell(activeComps[1])}
              </ResizablePanel>
            </ResizableGroup>
          </ResizablePanel>
          <ResizableHandle withHandle />
          <ResizablePanel defaultSize={panelSizes.layout4?.mainHorizontal?.[1] ?? 32} minSize={20}>
            {renderSlotCell(activeComps[2])}
          </ResizablePanel>
        </ResizableGroup>
      );
    }

    if (activeComps.length === 4) {
      return (
        <ResizableGroup
          orientation="horizontal"
          className="h-full w-full"
          onLayout={(s: number[]) => handlePanelResize('layout4', 'mainHorizontal', s)}
        >
          <ResizablePanel defaultSize={panelSizes.layout4?.mainHorizontal?.[0] ?? 50} minSize={25}>
            <ResizableGroup
              orientation="vertical"
              onLayout={(s: number[]) => handlePanelResize('layout4', 'leftVertical', s)}
            >
              <ResizablePanel defaultSize={panelSizes.layout4?.leftVertical?.[0] ?? 50} minSize={25}>
                {renderSlotCell(activeComps[0])}
              </ResizablePanel>
              <ResizableHandle withHandle />
              <ResizablePanel defaultSize={panelSizes.layout4?.leftVertical?.[1] ?? 50} minSize={25}>
                {renderSlotCell(activeComps[1])}
              </ResizablePanel>
            </ResizableGroup>
          </ResizablePanel>
          <ResizableHandle withHandle />
          <ResizablePanel defaultSize={panelSizes.layout4?.mainHorizontal?.[1] ?? 50} minSize={25}>
            <ResizableGroup
              orientation="vertical"
              onLayout={(s: number[]) => handlePanelResize('layout4', 'rightVertical', s)}
            >
              <ResizablePanel defaultSize={panelSizes.layout4?.rightVertical?.[0] ?? 50} minSize={25}>
                {renderSlotCell(activeComps[2])}
              </ResizablePanel>
              <ResizableHandle withHandle />
              <ResizablePanel defaultSize={panelSizes.layout4?.rightVertical?.[1] ?? 50} minSize={25}>
                {renderSlotCell(activeComps[3])}
              </ResizablePanel>
            </ResizableGroup>
          </ResizablePanel>
        </ResizableGroup>
      );
    }

    return (
      <ResizableGroup
        orientation="horizontal"
        className="h-full w-full"
        onLayout={(s: number[]) => handlePanelResize('layout4', 'mainHorizontal', s)}
      >
        <ResizablePanel defaultSize={panelSizes.layout4?.mainHorizontal?.[0] ?? 68} minSize={40}>
          <ResizableGroup
            orientation="vertical"
            onLayout={(s: number[]) => handlePanelResize('layout4', 'leftVertical', s)}
          >
            <ResizablePanel defaultSize={panelSizes.layout4?.leftVertical?.[0] ?? 50} minSize={25}>
              <ResizableGroup
                orientation="horizontal"
                onLayout={(s: number[]) => handlePanelResize('layout4', 'topHorizontal', s)}
              >
                <ResizablePanel defaultSize={panelSizes.layout4?.topHorizontal?.[0] ?? 50} minSize={25}>
                  {renderSlotCell(activeComps[0])}
                </ResizablePanel>
                <ResizableHandle withHandle />
                <ResizablePanel defaultSize={panelSizes.layout4?.topHorizontal?.[1] ?? 50} minSize={25}>
                  {renderSlotCell(activeComps[1])}
                </ResizablePanel>
              </ResizableGroup>
            </ResizablePanel>
            <ResizableHandle withHandle />
            <ResizablePanel defaultSize={panelSizes.layout4?.leftVertical?.[1] ?? 50} minSize={25}>
              <ResizableGroup
                orientation="horizontal"
                onLayout={(s: number[]) => handlePanelResize('layout4', 'bottomHorizontal', s)}
              >
                <ResizablePanel defaultSize={panelSizes.layout4?.bottomHorizontal?.[0] ?? 50} minSize={25}>
                  {renderSlotCell(activeComps[2])}
                </ResizablePanel>
                <ResizableHandle withHandle />
                <ResizablePanel defaultSize={panelSizes.layout4?.bottomHorizontal?.[1] ?? 50} minSize={25}>
                  {renderSlotCell(activeComps[3])}
                </ResizablePanel>
              </ResizableGroup>
            </ResizablePanel>
          </ResizableGroup>
        </ResizablePanel>
        <ResizableHandle withHandle />
        <ResizablePanel defaultSize={panelSizes.layout4?.mainHorizontal?.[1] ?? 32} minSize={20}>
          {renderSlotCell(activeComps[4])}
        </ResizablePanel>
      </ResizableGroup>
    );
  };

  return (
    <div className={cn('fixed inset-0 z-50 bg-[#001332] flex flex-col h-screen w-screen text-xs select-text overflow-hidden', className)}>
      <OnePagerHeader
        currentRisk={risk}
        allRisks={allRiskRows}
        onSelectRisk={handleSelectRisk}
        selectedLayout={selectedLayout}
        layout3ActivePage={layout3ActivePage}
        onChangeLayout3Page={setLayout3ActivePage}
        canEdit={canEdit}
        isEditMode={isEditMode}
        isSaving={isSaving}
        onToggleEditMode={(explicitVal?: boolean) => {
          if (explicitVal === false) {
            handleCancelEdit();
          } else {
            setIsEditMode((prev) => (typeof explicitVal === 'boolean' ? explicitVal : !prev));
          }
        }}
        onBackToHeatmap={handleBackToOriginTab}
        onOpenSelectLayout={() => setShowSelectLayoutDialog(true)}
        onOpenCustomDrawer={() => setShowCustomDrawer(true)}
        onSaveLink={handleSaveLink}
        onSaveLayout={handleHeaderSave}
        onSaveAllLayout={handleHeaderSaveAll}
      />

      <SelectLayoutModal
        open={showSelectLayoutDialog}
        onOpenChange={setShowSelectLayoutDialog}
        selectedLayout={selectedLayout}
        pendingLayout={modalPendingLayout}
        onSelectPendingLayout={setModalPendingLayout}
        showAssessmentJustification={showAssessmentJustification}
        assessmentPages={assessmentPages}
        onToggleJustification={() => setShowAssessmentJustification(!showAssessmentJustification)}
        onToggleJustificationPage={(page) =>
          setAssessmentPages((prev) => ({ ...prev, [page]: !prev[page] }))
        }
        showLastReviewComment={showLastReviewComment}
        reviewCommentPages={reviewCommentPages}
        onToggleLastReviewComment={() => setShowLastReviewComment(!showLastReviewComment)}
        onToggleReviewCommentPage={(page) =>
          setReviewCommentPages((prev) => ({ ...prev, [page]: !prev[page] }))
        }
        waterfallMethod={activeWaterfallMethod}
        waterfallDateRange={activeWaterfallDateRange}
        canEdit={canEdit}
        onApply={handleApplyModalLayout}
      />

      <CustomSlotsDrawer
        open={showCustomDrawer && selectedLayout === 4}
        canEdit={canEdit}
        allComponents={ALL_COMPONENTS}
        customComponents={customComponents}
        onToggleComponent={handleToggleCustomComponent}
        showAssessmentJustification={showAssessmentJustification}
        onToggleJustification={handleToggleJustificationFromDrawer}
        showLastReviewComment={showLastReviewComment}
        onToggleLastReviewComment={handleToggleLastReviewCommentFromDrawer}
        onApply={handleApplyCustomDrawer}
        onClose={() => setShowCustomDrawer(false)}
      />

      {/* Main Panel Canvas Area */}
      <div className="flex-1 min-h-0 min-w-0 overflow-hidden p-1 bg-slate-100">
        {selectedLayout === 4 ? (
          <div className="h-full w-full rounded border border-slate-200 bg-white overflow-hidden">
            {renderCustomLayout4()}
          </div>
        ) : selectedLayout === 3 ? (
          <div className="h-full w-full rounded border border-slate-200 bg-white overflow-hidden">
            {layout3ActivePage === 'page1' ? (
              /* Layout 3 Page 1 */
              <ResizableGroup
                orientation="horizontal"
                className="h-full w-full"
                onLayout={(s: number[]) => handlePanelResize('layout3_page1', 'mainHorizontal', s)}
              >
                <ResizablePanel defaultSize={panelSizes.layout3_page1?.mainHorizontal?.[0] ?? 68} minSize={40}>
                  <ResizableGroup
                    orientation="vertical"
                    onLayout={(s: number[]) => handlePanelResize('layout3_page1', 'leftVertical', s)}
                  >
                    <ResizablePanel defaultSize={panelSizes.layout3_page1?.leftVertical?.[0] ?? 50} minSize={25}>
                      <ResizableGroup
                        orientation="horizontal"
                        onLayout={(s: number[]) => handlePanelResize('layout3_page1', 'topHorizontal', s)}
                      >
                        <ResizablePanel defaultSize={panelSizes.layout3_page1?.topHorizontal?.[0] ?? 50} minSize={25}>
                          <OnePagerArmInfo risk={risk} mode="description" className="h-full w-full border-none rounded-none p-2" />
                        </ResizablePanel>

                        <ResizableHandle withHandle />

                        <ResizablePanel defaultSize={panelSizes.layout3_page1?.topHorizontal?.[1] ?? 50} minSize={25}>
                          {renderSlotCell('heatmap')}
                        </ResizablePanel>
                      </ResizableGroup>
                    </ResizablePanel>

                    <ResizableHandle withHandle />

                    <ResizablePanel defaultSize={panelSizes.layout3_page1?.leftVertical?.[1] ?? 50} minSize={25}>
                      <OnePagerArmInfo risk={risk} mode="causesEffects" className="h-full w-full border-none rounded-none p-2" />
                    </ResizablePanel>
                  </ResizableGroup>
                </ResizablePanel>

                <ResizableHandle withHandle />

                <ResizablePanel defaultSize={panelSizes.layout3_page1?.mainHorizontal?.[1] ?? 32} minSize={20}>
                  {renderSlotCell('keyMessages')}
                </ResizablePanel>
              </ResizableGroup>
            ) : (
              /* Layout 3 Page 2 */
              <ResizableGroup
                orientation="horizontal"
                className="h-full w-full"
                onLayout={(s: number[]) => handlePanelResize('layout3_page2', 'mainHorizontal', s)}
              >
                <ResizablePanel defaultSize={panelSizes.layout3_page2?.mainHorizontal?.[0] ?? 68} minSize={40}>
                  <ResizableGroup
                    orientation="vertical"
                    onLayout={(s: number[]) => handlePanelResize('layout3_page2', 'leftVertical', s)}
                  >
                    <ResizablePanel defaultSize={panelSizes.layout3_page2?.leftVertical?.[0] ?? 50} minSize={25}>
                      {renderSlotCell('waterfall')}
                    </ResizablePanel>
                    <ResizableHandle withHandle />
                    <ResizablePanel defaultSize={panelSizes.layout3_page2?.leftVertical?.[1] ?? 50} minSize={25}>
                      {renderSlotCell('actionTracker')}
                    </ResizablePanel>
                  </ResizableGroup>
                </ResizablePanel>
                <ResizableHandle withHandle />
                <ResizablePanel defaultSize={panelSizes.layout3_page2?.mainHorizontal?.[1] ?? 32} minSize={20}>
                  {renderSlotCell('keyMessages')}
                </ResizablePanel>
              </ResizableGroup>
            )}
          </div>
        ) : selectedLayout === 2 ? (
          <div className="h-full w-full rounded border border-slate-200 bg-white overflow-hidden">
            <ResizableGroup
              orientation="horizontal"
              className="h-full w-full"
              onLayout={(s: number[]) => handlePanelResize('layout2', 'mainHorizontal', s)}
            >
              <ResizablePanel defaultSize={panelSizes.layout2?.mainHorizontal?.[0] ?? 28} minSize={20}>
                {renderSlotCell(undefined, 'slotTopLeft')}
              </ResizablePanel>

              <ResizableHandle withHandle />

              <ResizablePanel defaultSize={panelSizes.layout2?.mainHorizontal?.[1] ?? 44} minSize={30}>
                <ResizableGroup
                  orientation="vertical"
                  onLayout={(s: number[]) => handlePanelResize('layout2', 'centerVertical', s)}
                >
                  <ResizablePanel defaultSize={panelSizes.layout2?.centerVertical?.[0] ?? 50} minSize={25}>
                    {renderSlotCell(undefined, 'slotTopCenter')}
                  </ResizablePanel>

                  <ResizableHandle withHandle />

                  <ResizablePanel defaultSize={panelSizes.layout2?.centerVertical?.[1] ?? 50} minSize={25}>
                    {renderSlotCell(undefined, 'slotBottomCenter')}
                  </ResizablePanel>
                </ResizableGroup>
              </ResizablePanel>

              <ResizableHandle withHandle />

              <ResizablePanel defaultSize={panelSizes.layout2?.mainHorizontal?.[2] ?? 28} minSize={20}>
                {renderSlotCell(undefined, 'slotRight')}
              </ResizablePanel>
            </ResizableGroup>
          </div>
        ) : (
          <div className="h-full w-full rounded border border-slate-200 bg-white overflow-hidden">
            <ResizableGroup
              orientation="horizontal"
              className="h-full w-full"
              onLayout={(s: number[]) => handlePanelResize('layout1', 'mainHorizontal', s)}
            >
              <ResizablePanel defaultSize={panelSizes.layout1?.mainHorizontal?.[0] ?? 68} minSize={40}>
                <ResizableGroup
                  orientation="vertical"
                  onLayout={(s: number[]) => handlePanelResize('layout1', 'leftVertical', s)}
                >
                  <ResizablePanel defaultSize={panelSizes.layout1?.leftVertical?.[0] ?? 58} minSize={30}>
                    <ResizableGroup
                      orientation="horizontal"
                      onLayout={(s: number[]) => handlePanelResize('layout1', 'topLeftHorizontal', s)}
                    >
                      <ResizablePanel defaultSize={panelSizes.layout1?.topLeftHorizontal?.[0] ?? 50} minSize={25}>
                        {renderSlotCell(undefined, 'slotTopLeft')}
                      </ResizablePanel>

                      <ResizableHandle withHandle />

                      <ResizablePanel defaultSize={panelSizes.layout1?.topLeftHorizontal?.[1] ?? 50} minSize={25}>
                        {renderSlotCell(undefined, 'slotTopCenter')}
                      </ResizablePanel>
                    </ResizableGroup>
                  </ResizablePanel>

                  <ResizableHandle withHandle />

                  <ResizablePanel defaultSize={panelSizes.layout1?.leftVertical?.[1] ?? 42} minSize={20}>
                    <ResizableGroup
                      orientation="horizontal"
                      onLayout={(s: number[]) => handlePanelResize('layout1', 'bottomLeftHorizontal', s)}
                    >
                      <ResizablePanel defaultSize={panelSizes.layout1?.bottomLeftHorizontal?.[0] ?? 50} minSize={25}>
                        {renderSlotCell(undefined, 'slotBottomLeft')}
                      </ResizablePanel>

                      <ResizableHandle withHandle />

                      <ResizablePanel defaultSize={panelSizes.layout1?.bottomLeftHorizontal?.[1] ?? 50} minSize={25}>
                        {renderSlotCell(undefined, 'slotBottomCenter')}
                      </ResizablePanel>
                    </ResizableGroup>
                  </ResizablePanel>
                </ResizableGroup>
              </ResizablePanel>

              <ResizableHandle withHandle />

              <ResizablePanel defaultSize={panelSizes.layout1?.mainHorizontal?.[1] ?? 32} minSize={20}>
                {renderSlotCell(undefined, 'slotRight')}
              </ResizablePanel>
            </ResizableGroup>
          </div>
        )}
      </div>

    </div>
  );
};
