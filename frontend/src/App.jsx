import { Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { AuthProvider, useAuth } from './context/AuthContext'
import AppLayout from './components/layout/AppLayout'
import Home        from './pages/Home'
import AuthSuccess from './pages/AuthSuccess'
import Me          from './pages/Me'
import Roast       from './pages/Roast'
import Battle      from './pages/Battle'
import BattleResult from './pages/BattleResult'
import Squad       from './pages/Squad'
import SquadRoom   from './pages/SquadRoom'
import PublicProfile from './pages/PublicProfile'

function Guard({ children }) {
  const { user, loading } = useAuth()
  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-[#080808]">
      <div className="flex flex-col items-center gap-4">
        <div className="w-10 h-10 border-2 border-[#1DB954] border-t-transparent rounded-full animate-spin" />
        <p className="text-[#444] text-sm font-display">Loading Auracle…</p>
      </div>
    </div>
  )
  if (!user) return <Navigate to="/" replace />
  return children
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/"               element={<Home />} />
      <Route path="/auth/success"   element={<AuthSuccess />} />
      <Route path="/u/:slug"        element={<PublicProfile />} />
      <Route path="/battle/:slug"   element={<BattleResult />} />
      <Route path="/squad/:code"    element={<SquadRoom />} />

      <Route path="/app" element={<Guard><AppLayout /></Guard>}>
        <Route index                element={<Navigate to="/app/me" replace />} />
        <Route path="me"            element={<Me />} />
        <Route path="roast"         element={<Roast />} />
        <Route path="battle"        element={<Battle />} />
        <Route path="squad"         element={<Squad />} />
      </Route>
    </Routes>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
      <Toaster
        position="bottom-center"
        toastOptions={{
          style: { background: '#161616', color: '#fff', border: '1px solid #252525', fontFamily: 'DM Sans', fontSize: 13 },
          success: { iconTheme: { primary: '#1DB954', secondary: '#080808' } },
          error:   { iconTheme: { primary: '#f87171', secondary: '#080808' } },
        }}
      />
    </AuthProvider>
  )
}
