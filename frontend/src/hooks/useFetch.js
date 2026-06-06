import { useState, useEffect, useRef } from 'react'

export function useFetch(fetchFn, deps = []) {
  const [data,    setData]    = useState(null)
  const [loading, setLoading] = useState(true)
  const [error,   setError]   = useState(null)
  const mounted = useRef(true)

  useEffect(() => {
    mounted.current = true
    setLoading(true)
    setError(null)
    fetchFn()
      .then(({ data }) => { if (mounted.current) setData(data) })
      .catch((e)       => { if (mounted.current) setError(e?.response?.data?.detail || 'Something went wrong') })
      .finally(()      => { if (mounted.current) setLoading(false) })
    return () => { mounted.current = false }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  return { data, loading, error }
}
