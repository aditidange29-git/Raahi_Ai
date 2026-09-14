import { useState, useEffect, useCallback } from 'react'

export function useApi<T>(
  fetcher: () => Promise<T>,
  deps: unknown[] = []
) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await fetcher()
      setData(result)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  useEffect(() => { load() }, [load])

  return { data, loading, error, refresh: load }
}

/** Poll an endpoint every `intervalMs` ms. */
export function usePoll<T>(
  fetcher: () => Promise<T>,
  intervalMs = 4000,
  deps: unknown[] = []
) {
  const { data, loading, error, refresh } = useApi<T>(fetcher, deps)

  useEffect(() => {
    const id = setInterval(refresh, intervalMs)
    return () => clearInterval(id)
  }, [refresh, intervalMs])

  return { data, loading, error, refresh }
}
