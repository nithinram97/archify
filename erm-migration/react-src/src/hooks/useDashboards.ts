import { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { client, CURRENT_ENV } from '../client';
import { ermGetDashboardList, ErmDashboardRiskAndOpportunity } from '@fca0-enterprise-risk-management/sdk';
import { extractValidSiglums } from '../utils/siglumUtils';
import type { DashboardDisplay } from '../types/dashboard';

/** Waits before each attempt when a refetch waits for a just-saved dashboard (search index lag). */
const RETRY_DELAYS_MS = [0, 500, 1000, 2000, 4000];

async function decodeDashboardList(result: string): Promise<DashboardDisplay[]> {
  const text = await new Response(
    new Blob([Uint8Array.from(atob(result), (c) => c.charCodeAt(0))])
      .stream()
      .pipeThrough(new DecompressionStream('gzip')),
  ).text();
  return JSON.parse(text);
}

export function useDashboards(currentUserEmail: string) {
  const [dashboards, setDashboards] = useState<DashboardDisplay[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [allSiglums, setAllSiglums] = useState<string[]>([]);

  // Only the latest request may update state: an older response landing last must not restore an old list.
  const requestId = useRef(0);
  const hasLoaded = useRef(false);

  const loadList = useCallback(async (): Promise<DashboardDisplay[] | null> => {
    const result = await client(ermGetDashboardList).executeFunction({ currentUserEmail, env: CURRENT_ENV ?? 'dev' });
    return result ? decodeDashboardList(result) : null;
  }, [currentUserEmail]);

  /**
   * Loads the list. With `until`, retries (0.5s, 1s, 2s, 4s) until the predicate holds, so a dashboard
   * saved a moment ago shows up even when the list function still reads the previous state.
   * Resolves `true` when the list is loaded (and `until` holds), `false` otherwise.
   */
  const fetchDashboards = useCallback(
    async (until?: (list: DashboardDisplay[]) => boolean): Promise<boolean> => {
      if (!currentUserEmail) return false;
      const id = ++requestId.current;
      if (hasLoaded.current) setIsRefreshing(true);
      else setIsLoading(true);
      setError(null);

      try {
        for (const delay of until ? RETRY_DELAYS_MS : [0]) {
          if (delay) await new Promise((resolve) => setTimeout(resolve, delay));
          const list = await loadList();
          if (id !== requestId.current) return false; // superseded by a newer request
          if (list) {
            setDashboards(list);
            hasLoaded.current = true;
          }
          if (list && (!until || until(list))) return true;
        }
        return false;
      } catch (err: unknown) {
        console.error('Failed to load dashboards:', err);
        if (id === requestId.current) {
          setError((err as { message?: string })?.message || 'Failed to load dashboards.');
        }
        return false;
      } finally {
        if (id === requestId.current) {
          setIsLoading(false);
          setIsRefreshing(false);
        }
      }
    },
    [currentUserEmail, loadList],
  );

  useEffect(() => {
    fetchDashboards();
  }, [fetchDashboards]);

  useEffect(() => {
    async function fetchSiglums() {
      try {
        const result = await client(ErmDashboardRiskAndOpportunity).aggregate({
          $select: { $count: 'unordered' },
          $groupBy: { fullItemPath: { $exactWithLimit: 10000 } },
        });
        setAllSiglums(
          extractValidSiglums(result.map((b: { $group: { fullItemPath: string } }) => b.$group.fullItemPath)),
        );
      } catch (err) {
        console.error(err);
      }
    }
    fetchSiglums();
  }, []);

  const combinedSiglums = useMemo(() => {
    const dashboardSiglums = dashboards
      .map((d) => d.ownerDashboard)
      .filter(Boolean)
      .flatMap((s) => s!.split(',').map((x) => x.trim()));
    return Array.from(new Set([...allSiglums, ...dashboardSiglums])).sort();
  }, [dashboards, allSiglums]);

  return { dashboards, isLoading, isRefreshing, error, combinedSiglums, refetch: fetchDashboards };
}
