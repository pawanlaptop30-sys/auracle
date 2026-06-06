import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { authApi } from '../utils/api'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user,    setUser]    = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchMe = useCallback(async () => {
    const token = localStorage.getItem('auracle_token')
    if (!token) { setLoading(false); return }
    try {
      const { data } = await authApi.me()
      setUser(data)
    } catch {
      localStorage.removeItem('auracle_token')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { fetchMe() }, [fetchMe])

  const login  = () => { window.location.href = authApi.loginUrl() }
  const logout = async () => {
    try { await authApi.logout() } catch {}
    localStorage.removeItem('auracle_token')
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, refetch: fetchMe }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
