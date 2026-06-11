/** Cache client-side simples: TTL + dedupe de requisições em andamento. */

const PLACEHOLDER_MAX_AGE_MS = 15_000;

type CacheEntry = {
  data: unknown;
  fetchedAt: number;
};

const store = new Map<string, CacheEntry>();
const inflight = new Map<string, Promise<unknown>>();

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

export async function fetchWithApiCache<T>(
  key: string,
  fetcher: () => Promise<T>,
): Promise<T> {
  const cached = peekApiCache<T>(key);
  if (cached !== null) return cached;

  const pending = inflight.get(key);
  if (pending) return pending as Promise<T>;

  const promise = fetcher()
    .then((data) => {
      store.set(key, { data, fetchedAt: Date.now() });
      inflight.delete(key);
      return data;
    })
    .catch((err) => {
      inflight.delete(key);
      throw err;
    });

  inflight.set(key, promise);
  return promise;
}

export function resetApiClientCachesForTests() {
  store.clear();
  inflight.clear();
}
