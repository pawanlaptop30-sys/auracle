import { Outlet, NavLink, useNavigate, useLocation } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useAuth } from '../../context/AuthContext'
import toast from 'react-hot-toast'

const NAV = [
  { to: '/app/me',     icon: '🎧', label: 'My Profile' },
  { to: '/app/roast',  icon: '🔥', label: 'Get Roasted' },
  { to: '/app/battle', icon: '⚔️',  label: 'Battle' },
  { to: '/app/squad',  icon: '👥', label: 'Squad' },
]

export default function AppLayout() {
  const { user, logout } = useAuth()
  const navigate          = useNavigate()
  const location          = useLocation()
  const [drawerOpen, setDrawerOpen] = useState(false)

  useEffect(() => setDrawerOpen(false), [location.pathname])

  const handleLogout = async () => {
    await logout()
    toast.success('See you next time 👋')
    navigate('/')
  }

  return (
    <div className="min-h-screen bg-[#080808] flex flex-col">

      {/* Top bar */}
      <header className="sticky top-0 z-30 bg-[#080808]/90 backdrop-blur border-b border-[#1a1a1a] flex items-center justify-between px-4 md:px-6 h-14">
        <NavLink to="/app/me" className="font-display font-extrabold text-[18px] text-[#1DB954] tracking-tight">
          Auracle
        </NavLink>

        {/* Desktop nav */}
        <nav className="hidden md:flex items-center gap-1">
          {NAV.map(n => (
            <NavLink key={n.to} to={n.to}
              className={({ isActive }) =>
                `flex items-center gap-2 px-4 py-2 rounded-xl text-[13px] font-medium transition-all ${
                  isActive ? 'bg-[#1DB95420] text-[#1DB954]' : 'text-[#666] hover:text-white hover:bg-[#161616]'
                }`
              }
            >
              <span>{n.icon}</span>{n.label}
            </NavLink>
          ))}
        </nav>

        {/* User + logout */}
        <div className="flex items-center gap-3">
          {user?.avatar_url
            ? <img src={user.avatar_url} className="w-8 h-8 rounded-full object-cover ring-2 ring-[#252525]" alt="" />
            : <div className="w-8 h-8 rounded-full bg-[#1DB954] flex items-center justify-center text-black font-bold text-sm">{user?.display_name?.[0]}</div>
          }
          <button onClick={handleLogout}
            className="hidden md:block text-[12px] text-[#555] hover:text-[#f87171] transition-colors">
            Logout
          </button>
          {/* Mobile menu btn */}
          <button onClick={() => setDrawerOpen(v => !v)}
            className="md:hidden w-8 h-8 flex items-center justify-center text-[#666] hover:text-white">
            ☰
          </button>
        </div>
      </header>

      {/* Mobile drawer */}
      <AnimatePresence>
        {drawerOpen && (
          <>
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/70 z-40 md:hidden" onClick={() => setDrawerOpen(false)} />
            <motion.div initial={{ x: '100%' }} animate={{ x: 0 }} exit={{ x: '100%' }}
              transition={{ type: 'tween', duration: 0.22 }}
              className="fixed right-0 top-0 bottom-0 w-64 bg-[#0f0f0f] border-l border-[#252525] z-50 md:hidden flex flex-col">
              <div className="p-4 border-b border-[#252525] flex items-center justify-between">
                <span className="font-display font-extrabold text-[#1DB954]">Auracle</span>
                <button onClick={() => setDrawerOpen(false)} className="text-[#555] hover:text-white text-lg">✕</button>
              </div>
              <div className="flex-1 p-3 space-y-1">
                {NAV.map(n => (
                  <NavLink key={n.to} to={n.to}
                    className={({ isActive }) =>
                      `flex items-center gap-3 px-4 py-3 rounded-xl text-[14px] font-medium transition-all ${
                        isActive ? 'bg-[#1DB95420] text-[#1DB954]' : 'text-[#888] hover:text-white hover:bg-[#161616]'
                      }`
                    }
                  >
                    <span className="text-lg">{n.icon}</span>{n.label}
                  </NavLink>
                ))}
              </div>
              <div className="p-4 border-t border-[#252525]">
                <div className="flex items-center gap-3 mb-3">
                  {user?.avatar_url
                    ? <img src={user.avatar_url} className="w-9 h-9 rounded-full object-cover" alt="" />
                    : <div className="w-9 h-9 rounded-full bg-[#1DB954] flex items-center justify-center text-black font-bold">{user?.display_name?.[0]}</div>
                  }
                  <div>
                    <div className="text-[13px] font-medium">{user?.display_name}</div>
                    <div className="text-[11px] text-[#444]">@{user?.public_slug}</div>
                  </div>
                </div>
                <button onClick={handleLogout} className="w-full text-left text-[13px] text-[#555] hover:text-[#f87171] transition-colors">
                  ↩ Logout
                </button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Mobile bottom nav */}
      <nav className="fixed bottom-0 left-0 right-0 h-16 bg-[#0a0a0a]/95 backdrop-blur border-t border-[#1a1a1a] flex items-center md:hidden z-30">
        {NAV.map(n => (
          <NavLink key={n.to} to={n.to}
            className={({ isActive }) =>
              `flex-1 flex flex-col items-center justify-center gap-0.5 py-2 transition-all ${
                isActive ? 'text-[#1DB954]' : 'text-[#444] hover:text-[#888]'
              }`
            }
          >
            {({ isActive }) => (
              <>
                <span className="text-xl leading-none">{n.icon}</span>
                <span className={`text-[9px] font-medium ${isActive ? 'text-[#1DB954]' : 'text-[#444]'}`}>{n.label.split(' ')[0]}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Page */}
      <main className="flex-1 pb-20 md:pb-0">
        <motion.div key={location.pathname}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.2 }}
          className="max-w-4xl mx-auto px-4 md:px-6 py-6">
          <Outlet />
        </motion.div>
      </main>
    </div>
  )
}
