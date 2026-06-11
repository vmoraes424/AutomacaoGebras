/** Cache client-side: placeholder instantâneo + revalidação sempre que fresh=true. */

const PLACEHOLDER_MAX_AGE_MS = 15_000;

type CacheEntry = {
  data: unknown;
  fetchedAt: number;
  /** Escrita originada de requisição fresh=true (prioridade sobre stale). */
  fromFresh: boolean;
};

const store = new Map<string, CacheEntry>();
const inflight = new Map<string, Promise<unknown>>();

function inflightKey(key: string, fresh: boolean): string {
  return `${key}::${fresh ? "fresh" : "stale"}`;
}

function isEntryValid(entry: CacheEntry | undefined): entry is CacheEntry {
  if (!entry) return false;
  return Date.now() - entry.fetchedAt <= PLACEHOLDER_MAX_AGE_MS;
}

export function hasApiCache(key: string): boolean {
  return isEntryValid(store.get(key));
}

export function peekApiCache<T>(key: string): T | null {
  const entry = store.get(key);
  if (!isEntryValid(entry)) return null;
  return entry.data as T;
}

export function invalidateApiCache(prefix?: string) {
  for (const key of [...store.keys()]) {
    if (!prefix || key.startsWith(prefix)) {
      store.delete(key);
    }
  }
  for (const key of [...inflight.keys()]) {
    if (!prefix || key.startsWith(prefix)) {
      inflight.delete(key);
    }
  }
}

function writeCacheEntry(key: string, data: unknown, fresh: boolean) {
  const existing = store.get(key);
  if (existing && existing.fromFresh && !fresh) {
    return;
  }
  store.set(key, { data, fetchedAt: Date.now(), fromFresh: fresh });
}

export async function fetchWithApiCache<T>(
  key: string,
  fetcher: () => Promise<T>,
  opts?: { fresh?: boolean },
): Promise<T> {
  const fresh = opts?.fresh ?? true;

  if (!fresh) {
    const cached = peekApiCache<T>(key);
    if (cached !== null) {
      return cached;
    }
  }

  const pendingKey = inflightKey(key, fresh);
  const pending = inflight.get(pendingKey);
  if (pending) {
    return pending as Promise<T>;
  }

  const promise = fetcher()
    .then((data) => {
      writeCacheEntry(key, data, fresh);
      inflight.delete(pendingKey);
      return data;
    })
    .catch((err) => {
      inflight.delete(pendingKey);
      throw err;
    });

  inflight.set(pendingKey, promise);
  return promise as Promise<T>;
}

export function resetApiClientCachesForTests() {
  store.clear();
  inflight.clear();
}
