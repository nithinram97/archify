import React, { useState, useMemo } from 'react';
import { useToast } from '../../context/ToastContext';
import { useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  RefreshCw,
  Link as LinkIcon,
  CheckCircle2,
  Globe,
  Check,
  Loader2,
  ShieldCheck,
  ShieldAlert,
} from 'lucide-react';
import { client, CURRENT_ENV } from '../../client';
import { ermValidateDashboardAndRisksv2 } from '@fca0-enterprise-risk-management/sdk';
import { Button } from '../../../@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../../../@/components/ui/select';
import { Popover, PopoverContent, PopoverTrigger } from '../../../@/components/ui/popover';
import { Badge } from '../../../@/components/ui/badge';
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from '../../../@/components/ui/command';
import { cn } from '../../../@/lib/utils';
import type { DashboardTabType } from '../../hooks/useDashboardView';
import { logger } from '../../utils/logger';
import { useDashboardContext } from '../../context/DashboardContext';
import type { DashboardDisplay } from '../../types/dashboard';
import skywiseLogo from '../../assets/skywise.svg';

interface DashboardHeaderProps {
  dashboardId: string;
  activeTab: DashboardTabType;
  onTabChange: (_tab: DashboardTabType) => void;
  onBack: () => void;
}

const getTargetDashboardId = (d: DashboardDisplay): string => {
  const rawId = d.dashboardId;
  if (rawId) return String(rawId);
  if (d.creationDate) {
    const epoch = new Date(d.creationDate).getTime();
    return `${epoch}___${d.boardVersion ?? 1}___${d.boardIteration ?? 1}`;
  }
  return d.boardTitle || '';
};

const parseUserList = (raw: unknown): string[] => {
  if (!raw) return [];
  if (Array.isArray(raw)) return raw.map((s) => String(s).trim().toLowerCase()).filter(Boolean);
  if (typeof raw === 'string') {
    return raw
      .split(',')
      .map((s) => s.trim().toLowerCase())
      .filter(Boolean);
  }
  return [];
};

const truthy = (v: unknown): boolean => v === true || v === 'true' || v === 1 || v === '1';

export const DashboardHeader: React.FC<DashboardHeaderProps> = ({ dashboardId, activeTab, onTabChange, onBack }) => {
  const navigate = useNavigate();
  const { 
    dashboardTitle, 
    currentDashboard, 
    availableVersions, 
    allLatestDashboards, 
    currentUserEmail, 
    refetchPayload 
  } = useDashboardContext();
  const { showToast } = useToast();

  const [openDashboardCombo, setOpenDashboardCombo] = useState(false);
  const [openValidationConfirm, setOpenValidationConfirm] = useState(false);
  const [isValidating, setIsValidating] = useState(false);

  const tabs: { id: DashboardTabType; label: string }[] = [
    { id: 'maps', label: 'Maps' },
    { id: 'table', label: 'Table' },
    { id: 'action-tracker', label: 'Action Tracker' },
    { id: 'summary', label: 'Summary' },
    { id: 'report', label: 'Report' },
    { id: 'full-search', label: 'Full Search' },
  ];

  const currentVersionKey = currentDashboard ? getTargetDashboardId(currentDashboard) : dashboardId;
  const currentVersionLabel = `V${currentDashboard?.boardVersion ?? 1}.${currentDashboard?.boardIteration ?? 1}`;

  // Evaluates validation status directly from currentDashboard (derived from armRoPayload.dashboard_infos)
  const isAlreadyValidated = useMemo(() => {
    if (!currentDashboard) return false;
    const status = (currentDashboard.boardStatus || '').toLowerCase();
    const isValFlag = truthy(currentDashboard.validation);
    return status === 'validated' || isValFlag;
  }, [currentDashboard]);

  // Check if current user has Owner or Officer privileges to validate
  const canValidate = useMemo(() => {
    if (!currentDashboard || isAlreadyValidated) return false;
    
    const isOwnerFlag = currentDashboard.isOwner as unknown;
    if (isOwnerFlag === true || isOwnerFlag === 'true') return true;

    const lowerUser = currentUserEmail.toLowerCase().trim();
    const owners = parseUserList(currentDashboard.permissionsOwnerNames_display);
    const officers = parseUserList(currentDashboard.permissionsOfficerNames_display);

    return owners.includes(lowerUser) || officers.includes(lowerUser);
  }, [currentDashboard, isAlreadyValidated, currentUserEmail]);

  // Extract Validator Metadata
  const validatorInfo = useMemo(() => {
    if (!currentDashboard) return null;
    const rawUser = (currentDashboard as Record<string, unknown>).validatorName ||
                    (currentDashboard as Record<string, unknown>).validator || 
                    (currentDashboard as Record<string, unknown>).validatedBy || 
                    (currentDashboard as Record<string, unknown>).lastEditor ||
                    'Authorized Validator';
    const rawDate = (currentDashboard as Record<string, unknown>).validatedOn || 
                    (currentDashboard as Record<string, unknown>).validationOn || 
                    (currentDashboard as Record<string, unknown>).updatedOn || 
                    '';
    return { name: String(rawUser), date: String(rawDate) };
  }, [currentDashboard]);

  // Handle Validate Dashboard Action Trigger
  const handleValidateDashboard = async () => {
    if (!canValidate || !currentDashboard) return;

    try {
      setIsValidating(true);

      const targetId = getTargetDashboardId(currentDashboard);
      const displayName = currentUserEmail.split('@')[0].replace('.', ' ');

      logger.info('DashboardHeader', `Submitting validation for dashboard: ${targetId}`);

      await client(ermValidateDashboardAndRisksv2).applyAction(
        {
          dashboardId: targetId,
          validatorName: displayName,
          userMail: currentUserEmail.trim(),
          env: CURRENT_ENV ?? "dev",
        },
        {
          $returnEdits: true,
        }
      );

      showToast('Dashboard validated successfully!', 'success');
      await refetchPayload();
    } catch (err: unknown) {
      const errObj = err as { message?: string };
      logger.error('DashboardHeader', 'Failed to validate dashboard', err);
      showToast(errObj?.message || 'Failed to validate dashboard. Check permissions.', 'error');
    } finally {
      setIsValidating(false);
    }
  };

  const handleVersionChange = (newId: string | null) => {
    if (newId && newId !== currentVersionKey) {
      logger.info('DashboardHeader', `Switching dashboard version to: ${newId}`);
      navigate(`/dashboard/${encodeURIComponent(newId)}/${activeTab}`);
    }
  };

  const handleRefresh = () => {
    logger.info('DashboardHeader', 'User clicked refresh button');
    window.location.reload();
  };

  const handleCopyLink = () => {
    logger.info('DashboardHeader', 'Dashboard URL copied to clipboard');
    navigator.clipboard.writeText(window.location.href);
    showToast('Dashboard URL copied to clipboard!', 'success');
  };

  return (
    <header className="bg-[#001332] text-white flex flex-wrap items-center justify-between px-4 py-2 shrink-0 border-b border-slate-800 shadow-xs relative z-20">
      {/* Left Title & Breadcrumb Section */}
      <div className="flex items-center gap-2.5">
        <Button
          variant="ghost"
          size="icon-xs"
          onClick={onBack}
          className="text-slate-300 hover:text-white hover:bg-white/10 cursor-pointer"
          title="Back to Dashboards List"
        >
          <ArrowLeft className="h-4 w-4" />
        </Button>

        <div className="flex items-center gap-1.5 text-xs font-medium">
          <img src={skywiseLogo} alt="Skywise" className="h-5 object-contain" />
          <span className="text-slate-500">|</span>
          <span className="text-slate-200">
            ERM Dashboard <span className="text-[10px] text-slate-400 font-normal">(V1)</span>
          </span>
          <span className="text-slate-500">&gt;</span>

          {/* Title & Version Selector Group */}
          <div className="flex items-center gap-1">
            {/* Searchable Dashboard Title Switcher */}
            <Popover open={openDashboardCombo} onOpenChange={setOpenDashboardCombo}>
              <PopoverTrigger className="text-white font-semibold truncate max-w-xs text-xs px-1.5 py-0.5 rounded cursor-pointer border border-transparent hover:bg-white/10 hover:border-white/20 transition-all outline-none">
                {dashboardTitle || dashboardId}
              </PopoverTrigger>
              <PopoverContent className="w-80 p-0" align="start">
                <Command>
                  <CommandInput placeholder="Search dashboards..." className="h-8 text-xs" />
                  <CommandList>
                    <CommandEmpty className="py-3 text-center text-xs text-slate-500">
                      No dashboards found.
                    </CommandEmpty>
                    <CommandGroup className="max-h-60 overflow-y-auto">
                      {allLatestDashboards.map((dash) => {
                        const dashKey = getTargetDashboardId(dash);
                        const isSelected = currentDashboard
                          ? getTargetDashboardId(currentDashboard) === dashKey
                          : false;

                        return (
                          <CommandItem
                            key={dashKey}
                            value={dash.boardTitle || dashKey}
                            onSelect={() => {
                              setOpenDashboardCombo(false);
                              if (dashKey !== currentVersionKey) {
                                logger.info('DashboardHeader', `Switching active dashboard to: ${dashKey}`);
                                navigate(`/dashboard/${encodeURIComponent(dashKey)}/${activeTab}`);
                              }
                            }}
                            className="text-xs cursor-pointer flex items-center justify-between py-1.5 px-2"
                          >
                            <div className="flex items-center gap-2 truncate">
                              <Check
                                className={cn(
                                  'h-3.5 w-3.5 shrink-0',
                                  isSelected ? 'opacity-100 text-emerald-600' : 'opacity-0',
                                )}
                              />
                              <div className="flex flex-col truncate">
                                <span className="font-semibold text-slate-800 truncate">{dash.boardTitle}</span>
                                <span className="text-[10px] text-slate-400 font-mono">
                                  V{dash.boardVersion ?? 1}.{dash.boardIteration ?? 1} • {dash.ownerDashboard || 'Airbus'}
                                </span>
                              </div>
                            </div>
                          </CommandItem>
                        );
                      })}
                    </CommandGroup>
                  </CommandList>
                </Command>
              </PopoverContent>
            </Popover>

            {/* Seamless Version Selector */}
            {availableVersions.length > 1 ? (
              <Select value={currentVersionKey} onValueChange={handleVersionChange}>
                <SelectTrigger className="h-6 px-1.5 py-0 text-xs font-medium text-slate-300 hover:text-white bg-transparent hover:bg-white/10 border-transparent hover:border-white/20 rounded cursor-pointer transition-all gap-0.5 shadow-none border outline-none">
                  <SelectValue>{currentVersionLabel}</SelectValue>
                </SelectTrigger>
                <SelectContent align="start">
                  {availableVersions.map((ver) => {
                    const verId = getTargetDashboardId(ver);
                    const verLabel = `V${ver.boardVersion ?? 1}.${ver.boardIteration ?? 1}${ver.boardStatus ? ` (${ver.boardStatus})` : ''}`;
                    return (
                      <SelectItem key={verId} value={verId} className="text-xs cursor-pointer">
                        {verLabel}
                      </SelectItem>
                    );
                  })}
                </SelectContent>
              </Select>
            ) : (
              <span className="text-xs font-medium text-slate-400">({currentVersionLabel})</span>
            )}
          </div>
        </div>

        {/* VALIDATION ACTION BUTTON / VALIDATED STATUS BADGE */}
        {isAlreadyValidated ? (
          <div className="relative group/validated inline-block ml-2">
            <Badge
              variant="outline"
              className="bg-emerald-500/15 border-emerald-400/40 text-emerald-300 text-[11px] font-semibold h-6 px-2.5 rounded flex items-center gap-1 select-none cursor-pointer transition-colors hover:bg-emerald-500/25"
            >
              <ShieldCheck className="h-3.5 w-3.5 text-emerald-400" />
              <span>Dashboard validated ✓</span>
            </Badge>

            {/* Rich Hover Tooltip for Validator Details */}
            <div className="absolute left-0 top-full mt-1.5 hidden group-hover/validated:flex flex-col gap-1 w-64 p-2.5 bg-slate-900 border border-slate-700 text-white text-xs rounded-md shadow-2xl z-50 animate-in fade-in duration-150">
              <div className="flex items-center gap-1.5 text-emerald-400 font-bold border-b border-slate-800 pb-1 text-[11px]">
                <ShieldCheck className="h-3.5 w-3.5" />
                <span>Validated Dashboard Snapshot</span>
              </div>
              <div className="text-[11px] space-y-0.5 pt-0.5">
                <div className="text-slate-300">
                  Validated by: <strong className="text-white font-semibold">{validatorInfo?.name || 'Authorized Owner / Officer'}</strong>
                </div>
                {validatorInfo?.date && (
                  <div className="text-slate-400 font-mono text-[10px]">
                    Validated date: {validatorInfo.date}
                  </div>
                )}
              </div>
            </div>
          </div>
        ) : canValidate ? (
          <Popover open={openValidationConfirm} onOpenChange={setOpenValidationConfirm}>
            <PopoverTrigger
              type="button"
              disabled={isValidating}
              className="bg-slate-100 hover:bg-white text-airbus-navy text-[11px] font-bold ml-2 h-6 px-2.5 rounded shadow-2xs cursor-pointer transition-all inline-flex items-center gap-1 border-none outline-none disabled:opacity-50 select-none"
            >
              {isValidating ? (
                <>
                  <Loader2 className="h-3 w-3 animate-spin text-airbus-navy" /> Validating...
                </>
              ) : (
                <>
                  <CheckCircle2 className="h-3 w-3 text-emerald-600" /> Validate dashboard
                </>
              )}
            </PopoverTrigger>

            <PopoverContent align="start" className="w-84 p-3.5 bg-white border border-slate-200 text-slate-800 shadow-2xl rounded-lg space-y-3 z-50">
              <div className="flex items-center gap-2 border-b border-slate-100 pb-2">
                <ShieldAlert className="h-4 w-4 text-amber-600 shrink-0" />
                <h4 className="font-bold text-xs text-airbus-navy">Confirm Dashboard Validation</h4>
              </div>

              <div className="space-y-2 text-xs text-slate-600 leading-relaxed">
                <p>
                  Validating this dashboard will <strong>freeze its content and settings</strong> and mark version <strong>{currentVersionLabel}</strong> as a validated snapshot.
                </p>
                <div className="text-[11px] text-amber-900 bg-amber-50 border border-amber-200 rounded p-2 font-medium">
                  <strong>Note:</strong> Edits will be locked and for any future modifications a new iteration will be created (e.g., V{currentDashboard?.boardVersion ?? 1}.{(currentDashboard?.boardIteration ?? 1) + 1}).
                </div>
              </div>

              <div className="flex items-center justify-end gap-2 pt-1 border-t border-slate-100">
                <Button
                  type="button"
                  variant="outline"
                  size="xs"
                  onClick={() => setOpenValidationConfirm(false)}
                  className="h-7 text-xs font-medium px-3 border-slate-300 text-slate-700 hover:bg-slate-100"
                >
                  Cancel
                </Button>
                <Button
                  type="button"
                  size="xs"
                  onClick={() => {
                    setOpenValidationConfirm(false);
                    handleValidateDashboard();
                  }}
                  disabled={isValidating}
                  className="h-7 text-xs font-bold px-3 bg-emerald-600 hover:bg-emerald-700 text-white cursor-pointer shadow-xs"
                >
                  {isValidating ? <Loader2 className="h-3 w-3 animate-spin mr-1" /> : <CheckCircle2 className="h-3 w-3 mr-1" />}
                  Confirm Validation
                </Button>
              </div>
            </PopoverContent>
          </Popover>
        ) : null}
      </div>

      {/* Center Tabs Navigation */}
      <div className="flex items-center gap-1">
        {tabs.map((tab) => (
          <Button
            key={tab.id}
            variant="ghost"
            size="xs"
            onClick={() => onTabChange(tab.id)}
            className={cn(
              'text-xs font-medium px-3.5 py-1 text-slate-300 hover:text-white hover:bg-white/10 rounded-md cursor-pointer transition-all h-7',
              activeTab === tab.id &&
                'bg-white text-airbus-navy font-bold shadow-xs hover:bg-white hover:text-airbus-navy',
            )}
          >
            {tab.label}
          </Button>
        ))}
      </div>

      {/* Right Quick Action Icons */}
      <div className="flex items-center gap-1">
        <Button
          variant="ghost"
          size="icon-xs"
          onClick={handleRefresh}
          className="text-slate-300 hover:text-white hover:bg-white/10 h-7 w-7 cursor-pointer"
          title="Refresh App Data"
        >
          <RefreshCw className="h-3.5 w-3.5" />
        </Button>

        <Button
          variant="ghost"
          size="icon-xs"
          onClick={handleCopyLink}
          className="text-slate-300 hover:text-white hover:bg-white/10 h-7 w-7 cursor-pointer"
          title="Copy Dashboard Link"
        >
          <Globe className="h-3.5 w-3.5" />
        </Button>

        <Button
          variant="ghost"
          size="icon-xs"
          onClick={handleCopyLink}
          className="text-slate-300 hover:text-white hover:bg-white/10 h-7 w-7 cursor-pointer"
          title="Copy Link to Clipboard"
        >
          <LinkIcon className="h-3.5 w-3.5" />
        </Button>
      </div>

    </header>
  );
};
