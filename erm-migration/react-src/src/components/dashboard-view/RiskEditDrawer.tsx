import React, { useState, useEffect, useMemo } from 'react';
import { useDashboardContext, type ArmRiskRow } from '../../context/DashboardContext';
import { useToast } from '../../context/ToastContext';
import { client, CURRENT_ENV } from '../../client';
import {
  ermEditRisk,
  ermEditRiskDev,
  // Function-backed action on ermEditChildrenNewPermissions (G-30); use the action's API name.
  ermEditChildrenNewPermissions,
} from '@fca0-enterprise-risk-management/sdk';
import { logger } from '../../utils/logger';
import { cn } from '../../../@/lib/utils';
import { getScoreCode } from '../../utils/reportTableUtils';
import {
  Loader2,
  Check,
  ChevronsUpDown,
  AlertCircle,
  ExternalLink,
} from 'lucide-react';

// UI Components
import { Button } from '../../../@/components/ui/button';
import { Input } from '../../../@/components/ui/input';
import { Textarea } from '../../../@/components/ui/textarea';
import { Checkbox } from '../../../@/components/ui/checkbox';
import { Popover, PopoverContent, PopoverTrigger } from '../../../@/components/ui/popover';
import { Command, CommandEmpty, CommandGroup, CommandInput, CommandItem, CommandList } from '../../../@/components/ui/command';

const parseStringArray = (val: unknown): string[] => {
  if (!val) return [];
  if (Array.isArray(val)) return val.map((s) => String(s).trim()).filter(Boolean);
  if (typeof val === 'string') {
    const trimmed = val.trim();
    if (trimmed.startsWith('[')) {
      try {
        const parsed = JSON.parse(trimmed);
        if (Array.isArray(parsed)) return parsed.map((s) => String(s).trim()).filter(Boolean);
      } catch {
        // Fallback to comma-separated
      }
    }
    return trimmed.split(',').map((s) => s.trim()).filter(Boolean);
  }
  return [];
};

/** pkImpactId of a risk row. */
const pkOf = (row: ArmRiskRow): number =>
  Number(row.pk_impact_id || row.PKImpactID || String(row.primary_key ?? '').split('_').pop() || 0);

/** First non-empty value among a dashboard's display / raw / snake_case permission fields. */
const dashboardList = (dashboard: unknown, camel: string): string[] => {
  const d = (dashboard ?? {}) as Record<string, unknown>;
  const snake = camel.replace(/[A-Z]/g, (c) => `_${c.toLowerCase()}`);
  return parseStringArray(d[`${camel}_display`] ?? d[camel] ?? d[snake]);
};

interface RiskEditDrawerProps {
  open: boolean;
  onOpenChange: (_open: boolean) => void;
  risk: ArmRiskRow | null;
}

export const RiskEditDrawer: React.FC<RiskEditDrawerProps> = ({ open, onOpenChange, risk }) => {
  const { currentDashboard, currentUserEmail, allRiskRows, canEdit, refetchPayload } = useDashboardContext();
  // App-level toast: it stays visible after this drawer closes (a local one unmounted with it).
  const { showToast } = useToast();

  // Local Form States
  const [title, setTitle] = useState('');
  const [score, setScore] = useState<string>('0');
  const [perimeter, setPerimeter] = useState('');
  const [isTopRisk, setIsTopRisk] = useState(false);
  const [selectedParentId, setSelectedParentId] = useState<string>('');
  const [selectedChildIds, setSelectedChildIds] = useState<number[]>([]);

  // Open Popover States
  const [openParentCombo, setOpenParentCombo] = useState(false);
  const [openChildrenCombo, setOpenChildrenCombo] = useState(false);

  // Submission & Feedback States
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Parent links on this dashboard, used to keep the risk tree free of cycles.
  const rowByPk = useMemo(() => new Map(allRiskRows.map((r) => [pkOf(r), r])), [allRiskRows]);

  /** The current risk and all of its ancestors (parent, grandparent, ...). */
  const ancestorPks = useMemo(() => {
    const seen = new Set<number>();
    let current = risk ? pkOf(risk) : 0;
    while (current && !seen.has(current)) {
      seen.add(current);
      current = Number(rowByPk.get(current)?.riskParent ?? 0);
    }
    return seen;
  }, [risk, rowByPk]);

  /** The current risk and all of its descendants (children, grandchildren, ...). */
  const descendantPks = useMemo(() => {
    const childrenOf = new Map<number, number[]>();
    allRiskRows.forEach((r) => {
      const parent = Number(r.riskParent ?? 0);
      if (parent) childrenOf.set(parent, [...(childrenOf.get(parent) ?? []), pkOf(r)]);
    });
    const seen = new Set<number>();
    const stack = risk ? [pkOf(risk)] : [];
    while (stack.length > 0) {
      const pk = stack.pop()!;
      if (seen.has(pk)) continue;
      seen.add(pk);
      stack.push(...(childrenOf.get(pk) ?? []));
    }
    return seen;
  }, [risk, allRiskRows]);

  // Available Parent Risk Options: not the risk itself or one of its descendants.
  const availableParentOptions = useMemo(() => {
    if (!risk) return [];
    return allRiskRows.filter((r) => !descendantPks.has(pkOf(r)));
  }, [allRiskRows, risk, descendantPks]);

  // Available Child Risk Options: not the risk itself or one of its ancestors. Current children stay
  // listed so they can be unticked (they were filtered out before, so they could never be removed).
  const availableChildrenOptions = useMemo(() => {
    if (!risk) return [];
    return allRiskRows.filter((r) => !ancestorPks.has(pkOf(r)));
  }, [allRiskRows, risk, ancestorPks]);

  // Hydrate local form inputs when opening
  useEffect(() => {
    if (open && risk) {
      setTitle(risk.risktitle || risk.arm_title || '');
      setScore(String(risk.riskscore_display ?? Math.abs(risk.riskscore ?? risk.arm_score ?? 0)));
      setPerimeter(risk.riskperimeter || risk.arm_perimeter || '');
      setIsTopRisk(Boolean(risk.is_top_risk || risk.risktoprisk === 1 || risk.css_toprisk?.includes('toprisk')));

      const parentPk = risk.riskParent ? String(risk.riskParent) : '';
      setSelectedParentId(parentPk);

      const childrenPks = Array.isArray(risk.list_items) ? risk.list_items.map(Number) : [];
      setSelectedChildIds(childrenPks);

      setErrorMessage(null);
      setIsSubmitting(false);
    }
  }, [open, risk]);

  const handleToggleChild = (pkImpactId: number) => {
    if (!canEdit) return;
    setSelectedChildIds((prev) =>
      prev.includes(pkImpactId) ? prev.filter((id) => id !== pkImpactId) : [...prev, pkImpactId],
    );
  };

  const handleValidateAndSubmit = async () => {
    if (!canEdit) {
      setErrorMessage('Insufficient permissions: You must be an owner, writer, or officer to edit.');
      return;
    }

    if (!risk) return;

    if (!title.trim()) {
      setErrorMessage('Risk Title cannot be empty.');
      return;
    }

    const parsedScoreNum = Math.abs(parseFloat(score.replace(',', '.')));
    if (isNaN(parsedScoreNum) || parsedScoreNum > 16) {
      setErrorMessage('Criticality score must be a number between 0 and 16.');
      return;
    }

    const parentNumCheck = selectedParentId ? Number(selectedParentId) : 0;
    if (parentNumCheck && selectedChildIds.includes(parentNumCheck)) {
      setErrorMessage('A risk cannot be both the parent and a child of this risk.');
      return;
    }

    try {
      setIsSubmitting(true);
      setErrorMessage(null);

      const pkImpactId = risk.pk_impact_id || Number(risk.primary_key?.split('_').pop());
      const isOpportunity = String(risk.risktype || '').toLowerCase().includes('opp');
      const finalScore = isOpportunity ? -1 * parsedScoreNum : parsedScoreNum;
      const parentNum = selectedParentId ? Number(selectedParentId) : undefined;

      // Construct primary key: (dashboardId with single '_' between version and iteration) + "_" + pkImpactId
      const normalizedDashId = String(currentDashboard?.dashboardId || '').replace(/___/g, '_');
      let primaryKey = risk.primary_key;
      if (!primaryKey || !primaryKey.includes('_')) {
        primaryKey = `${normalizedDashId}_${pkImpactId}`;
      }

      const isMaster = CURRENT_ENV === 'master';

      logger.info('RiskEditDrawer', `Submitting ${isMaster ? 'ermEditRisk' : 'ermEditRiskDev'} with Primary Key: ${primaryKey}`, {
        finalScore,
        title,
        isTopRisk,
        perimeter,
        parentNum,
        env: CURRENT_ENV,
      });

      if (isMaster) {
        await client(ermEditRisk).applyAction({
          ErmRiskUserInput: primaryKey,
          risk_title: title.trim(),
          risk_score: finalScore,
          risk_toprisk: isTopRisk ? 1 : 0,
          risk_perimeter: perimeter.trim(),
          risk_parent: parentNum,
          risk_description: risk.riskdescription || risk.arm_description || '',
          updated_on: new Date().toISOString(),
        });
      } else {
        await (client(ermEditRiskDev as any) as any).applyAction({
          ErmRiskUserInputDev: primaryKey,
          risk_title: title.trim(),
          risk_score: finalScore,
          risk_toprisk: isTopRisk ? 1 : 0,
          risk_perimeter: perimeter.trim(),
          risk_parent: parentNum,
          risk_description: risk.riskdescription || risk.arm_description || '',
          updated_on: new Date().toISOString(),
        });
      }

      // G-30: save child links (legacy w_edit_children_action), only when they changed.
      const currentChildIds = Array.isArray(risk.list_items) ? risk.list_items.map(Number) : [];
      const childrenToAdd = selectedChildIds.filter((id) => !currentChildIds.includes(id));
      const childrenToRemove = currentChildIds.filter((id) => !selectedChildIds.includes(id));
      let childrenError: string | null = null;

      if (childrenToAdd.length > 0 || childrenToRemove.length > 0) {
        // riskObjectId = "<creationDate>_<version>_<iteration>_<pkImpactId>", the risk row's primary key.
        const toObjectIds = (pks: number[]) =>
          pks.map((pk) => {
            const row = rowByPk.get(pk) as Record<string, unknown> | undefined;
            const explicit = row?.risk_object_id ?? row?.riskObjectId;
            if (explicit) return String(explicit);
            const rowKey = String(row?.primary_key ?? '');
            return rowKey.includes('_') ? rowKey : `${normalizedDashId}_${pk}`;
          });

        try {
          logger.info('RiskEditDrawer', 'Submitting ermEditChildrenNewPermissions', {
            idParent: pkImpactId,
            add: childrenToAdd,
            remove: childrenToRemove,
            env: CURRENT_ENV,
          });
          await client(ermEditChildrenNewPermissions).applyAction({
            idParent: pkImpactId,
            userMail: currentUserEmail,
            idsChildrenToAdd: toObjectIds(childrenToAdd),
            idsChildrenToRemove: toObjectIds(childrenToRemove),
            env: CURRENT_ENV ?? 'dev',
            permissionsWriteNames: dashboardList(currentDashboard, 'permissionsWriteNames'),
            permissionsOwnerNames: dashboardList(currentDashboard, 'permissionsOwnerNames'),
            permissionsOfficerNames: dashboardList(currentDashboard, 'permissionsOfficerNames'),
          });
        } catch (err: unknown) {
          logger.error('RiskEditDrawer', 'Failed to save child links', err);
          childrenError = (err as { message?: string })?.message || 'R&O links failed.';
        }
      }

      await refetchPayload();

      if (childrenError) {
        // The risk itself was saved; keep the drawer open so the user sees why the links were not.
        setErrorMessage(`Risk saved, but child links were not: ${childrenError}`);
        showToast('Risk saved, but child links failed.', 'error');
        return;
      }

      showToast(`Risk #${risk.riskid_raw || pkImpactId} updated successfully!`, 'success');
      onOpenChange(false);
    } catch (err: unknown) {
      const errObj = err as { message?: string };
      logger.error('RiskEditDrawer', 'Failed to save risk edits', err);
      setErrorMessage(errObj?.message || 'Failed to apply risk edits. Check write permissions.');
      showToast('Failed to update risk details.', 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (!open || !risk) return null;

  const riskId = risk.riskid_raw || risk.pk_impact_id || '';
  const armScoreDisplay = risk.arm_score_display ?? Math.abs(risk.arm_score ?? 0);

  return (
    <aside className="w-96 bg-white border-l border-slate-200 h-full flex flex-col shrink-0 z-20 shadow-xl overflow-y-auto animate-in slide-in-from-right duration-200">
      {/* Header Bar */}
      <div className="p-3 bg-white border-b border-slate-200 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-1.5 text-xs font-semibold text-pink-600">
          <span>Risk ID : #{riskId}</span>
          <ExternalLink className="h-3 w-3 text-pink-600 cursor-pointer" />
        </div>

        <div className="flex items-center gap-2 text-xs">
          <span className="font-semibold text-slate-700">Top Risk:</span>
          <Checkbox
            disabled={!canEdit}
            checked={isTopRisk}
            onCheckedChange={(checked) => setIsTopRisk(Boolean(checked))}
            className="border-slate-300"
          />
        </div>
      </div>

      {/* Main Panel Body */}
      <div className="p-3 flex-1 space-y-3.5 text-xs">
        {/* Title Editor */}
        <div className="space-y-1">
          <label className="font-semibold text-slate-700 block">Title</label>
          <Textarea
            disabled={!canEdit}
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="Enter risk title..."
            className="min-h-16 text-xs bg-white border-slate-300 resize-none p-2 leading-snug"
          />
        </div>

        {/* Parent & Criticality Grid */}
        <div className="grid grid-cols-12 gap-2">
          <div className="col-span-8 space-y-1">
            <label className="font-semibold text-slate-700 block">Parent</label>
            <Popover open={openParentCombo && canEdit} onOpenChange={setOpenParentCombo}>
              <PopoverTrigger disabled={!canEdit} className="flex h-8 w-full items-center justify-between rounded-md border border-slate-300 bg-white px-2 text-xs font-normal outline-none hover:bg-slate-50 cursor-pointer disabled:pointer-events-none disabled:opacity-50">
                <span className="truncate">
                  {selectedParentId
                    ? availableParentOptions.find((r) => String(r.pk_impact_id) === selectedParentId)?.risktitle ||
                      `Parent #${selectedParentId}`
                    : 'None (Root Level)'}
                </span>
                <ChevronsUpDown className="h-3 w-3 shrink-0 opacity-50 ml-1" />
              </PopoverTrigger>
              <PopoverContent className="w-72 p-0" align="start">
                <Command>
                  <CommandInput placeholder="Search parent risk..." className="h-8 text-xs" />
                  <CommandList>
                    <CommandEmpty className="py-2 text-center text-xs">No matching parent found.</CommandEmpty>
                    <CommandGroup className="max-h-48 overflow-y-auto">
                      <CommandItem
                        onSelect={() => {
                          setSelectedParentId('');
                          setOpenParentCombo(false);
                        }}
                        className="text-xs font-semibold text-slate-500 cursor-pointer"
                      >
                        None (Root Level)
                      </CommandItem>
                      {availableParentOptions.map((opt) => {
                        const pkStr = String(opt.pk_impact_id || opt.primary_key);
                        const isSelected = selectedParentId === pkStr;

                        return (
                          <CommandItem
                            key={pkStr}
                            value={`${opt.riskid_raw} ${opt.risktitle}`}
                            onSelect={() => {
                              setSelectedParentId(pkStr);
                              setOpenParentCombo(false);
                            }}
                            className="text-xs cursor-pointer"
                          >
                            <Check className={cn('mr-2 h-3 w-3', isSelected ? 'opacity-100' : 'opacity-0')} />
                            <span className="truncate">
                              #{opt.riskid_raw} - {opt.risktitle}
                            </span>
                          </CommandItem>
                        );
                      })}
                    </CommandGroup>
                  </CommandList>
                </Command>
              </PopoverContent>
            </Popover>
          </div>

          <div className="col-span-4 space-y-1">
            <label className="font-semibold text-slate-700 block truncate" title="Assess Criticality">
              Assess Criticality
            </label>
            <Input
              disabled={!canEdit}
              value={score}
              onChange={(e) => setScore(e.target.value)}
              placeholder="0-16"
              className="h-8 text-xs font-mono bg-white border-slate-300"
            />
          </div>
        </div>

        {/* Children Multiselect */}
        <div className="space-y-1">
          <label className="font-semibold text-slate-700 block">
            Children ({selectedChildIds.length})
          </label>
          <Popover open={openChildrenCombo && canEdit} onOpenChange={setOpenChildrenCombo}>
            <PopoverTrigger disabled={!canEdit} className="flex h-8 w-full items-center justify-between rounded-md border border-slate-300 bg-white px-2.5 text-xs font-normal outline-none hover:bg-slate-50 cursor-pointer disabled:pointer-events-none disabled:opacity-50">
              <span className="truncate">
                {selectedChildIds.length > 0
                  ? `${selectedChildIds.length} child risk(s) linked`
                  : 'Select child risks...'}
              </span>
              <ChevronsUpDown className="h-3 w-3 shrink-0 opacity-50 ml-1" />
            </PopoverTrigger>
            <PopoverContent className="w-72 p-0" align="start">
              <Command>
                <CommandInput placeholder="Search child risks..." className="h-8 text-xs" />
                <CommandList>
                  <CommandEmpty className="py-2 text-center text-xs">No matching risks found.</CommandEmpty>
                  <CommandGroup className="max-h-48 overflow-y-auto">
                    {availableChildrenOptions.map((opt) => {
                      const pk = opt.pk_impact_id || Number(opt.primary_key);
                      const isChecked = selectedChildIds.includes(pk);

                      return (
                        <CommandItem
                          key={pk}
                          value={`${opt.riskid_raw} ${opt.risktitle}`}
                          onSelect={() => handleToggleChild(pk)}
                          className="text-xs cursor-pointer"
                        >
                          <Check className={cn('mr-2 h-3 w-3', isChecked ? 'opacity-100 text-emerald-600' : 'opacity-0')} />
                          <span className="truncate">
                            #{opt.riskid_raw} - {opt.risktitle}
                          </span>
                        </CommandItem>
                      );
                    })}
                  </CommandGroup>
                </CommandList>
              </Command>
            </PopoverContent>
          </Popover>
        </div>

        {/* Perimeter Input */}
        <div className="space-y-1">
          <label className="font-semibold text-slate-700 block">Perimeter</label>
          <Input
            disabled={!canEdit}
            value={perimeter}
            onChange={(e) => setPerimeter(e.target.value)}
            placeholder="Perimeter name..."
            className="h-8 text-xs bg-white border-slate-300"
          />
        </div>

        {/* Read-Only ARM Reference Section */}
        <div className="border-t border-slate-200 pt-2.5 space-y-2 text-[11px]">
          <div className="font-semibold text-slate-800">From ARM:</div>

          <div className="grid grid-cols-12 gap-y-1.5 gap-x-2 text-slate-600">
            <div className="col-span-3 font-medium text-slate-500">Title:</div>
            <div className="col-span-9 font-medium text-slate-800 leading-tight">{risk.arm_title || '-'}</div>

            <div className="col-span-3 font-medium text-slate-500">Description:</div>
            <div className="col-span-9 text-slate-700 leading-tight max-h-20 overflow-y-auto">
              {risk.arm_description || risk.riskdescription || '-'}
            </div>

            <div className="col-span-3 font-medium text-slate-500">Current criticality:</div>
            <div className="col-span-9 font-mono font-bold text-slate-800">
              {getScoreCode(armScoreDisplay)}
            </div>

            <div className="col-span-3 font-medium text-slate-500">Target criticality:</div>
            <div className="col-span-9 font-mono font-bold text-slate-800">
              {getScoreCode(risk.ARM_tar_impactscore_display ?? risk.ARM_tar_impactscore)}
            </div>

            <div className="col-span-3 font-medium text-slate-500">Item path:</div>
            <div className="col-span-9 font-mono text-[10px] text-slate-600 leading-tight break-all">
              {risk.arm_path || risk.full_item_path || '-'}
            </div>

            <div className="col-span-3 font-medium text-slate-500">In Board:</div>
            <div className="col-span-9 font-mono text-slate-800">{risk.arm_board || risk.riskboard || '-'}</div>
          </div>
        </div>

        {errorMessage && (
          <div className="flex items-center gap-2 text-xs font-medium text-red-600 bg-red-50 border border-red-200 rounded-md p-2">
            <AlertCircle className="h-4 w-4 text-red-600 shrink-0" />
            <span>{errorMessage}</span>
          </div>
        )}
      </div>

      {/* Footer Action Buttons */}
      <div className="p-3 border-t border-slate-200 bg-slate-50 shrink-0 grid grid-cols-2 gap-2">
        <Button
          type="button"
          onClick={handleValidateAndSubmit}
          disabled={isSubmitting || !canEdit}
          className="h-8 text-xs font-semibold bg-[#d81b60] hover:bg-[#c2185b] disabled:bg-slate-300 text-white rounded cursor-pointer shadow-2xs"
        >
          {isSubmitting ? <Loader2 className="h-3.5 w-3.5 animate-spin mr-1" /> : null}
          Validate
        </Button>

        <Button
          type="button"
          onClick={() => onOpenChange(false)}
          disabled={isSubmitting}
          className="h-8 text-xs font-semibold bg-[#d81b60] hover:bg-[#c2185b] text-white rounded cursor-pointer shadow-2xs"
        >
          Close
        </Button>
      </div>

    </aside>
  );
};
