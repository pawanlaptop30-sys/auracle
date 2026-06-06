import { motion } from 'framer-motion'
import { useAuth } from '../context/AuthContext'
import { Navigate } from 'react-router-dom'

const FEATURES = [
  { icon: '🔥', title: 'Get Roasted',    desc: '4 severity levels from polite shade to absolute destruction', color: '#ff4d00' },
  { icon: '⚔️',  title: 'Taste Battle',  desc: '1v1 — AI judge decides who has better music taste',         color: '#a855f7' },
  { icon: '👥', title: 'Squad Mode',     desc: 'Up to 4 friends — awards ceremony + group roast',           color: '#1DB954' },
  { icon: '🏆', title: 'Awards',         desc: 'Earn titles like "Spotify\'s Puppet" and "Needs Therapy"',  color: '#f59e0b' },
]

const ROAST_EXAMPLES = [
  '"You\'ve listened to AR Rahman 847 times. He is not your therapist. Please call an actual one."',
  '"Your playlist is so mainstream even Spotify is embarrassed to recommend it."',
  '"Detected: 73% sad songs. Your music taste is a cry for help disguised as aesthetic."',
  '"You call yourself an Explorer but you\'ve listened to the same 12 artists for 3 years."',
]

export default function Home() {
  const { user, login, loading } = useAuth()
  if (!loading && user) return <Navigate to="/app/me" replace />

  return (
    <div className="min-h-screen bg-[#080808] overflow-x-hidden">
      {/* Nav */}
      <nav className="flex items-center justify-between px-6 py-4 border-b border-[#141414]">
        <span className="font-display font-extrabold text-[20px] text-[#1DB954] tracking-tight">Auracle</span>
        <motion.button whileTap={{ scale: 0.97 }} onClick={login}
          className="px-4 py-2 rounded-xl bg-[#1DB954] text-black text-[13px] font-bold hover:bg-[#17a349] transition-all">
          Connect Spotify
        </motion.button>
      </nav>

      {/* Hero */}
      <section className="px-6 pt-16 pb-12 text-center max-w-2xl mx-auto">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}>
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#ff4d0020] border border-[#ff4d0040] text-[#ff4d00] text-[12px] font-semibold mb-6">
            🔥 Your music taste will be judged
          </div>
          <h1 className="font-display font-extrabold text-5xl md:text-7xl leading-none tracking-tight mb-4">
            Find out who has the<br />
            <span className="text-[#1DB954]">worst taste</span> in<br />
            your friend group
          </h1>
          <p className="text-[#555] text-lg mb-8 leading-relaxed">
            Connect Spotify. Get roasted. Battle friends. Earn humiliating awards. Share your shame.
          </p>
          <motion.button
            whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}
            onClick={login}
            className="inline-flex items-center gap-3 bg-[#1DB954] hover:bg-[#17a349] text-black font-bold text-[16px] px-8 py-4 rounded-2xl transition-all shadow-[0_0_40px_#1DB95440]"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
              <path d="M12 2C6.477 2 2 6.477 2 12s4.477 10 10 10 10-4.477 10-10S17.523 2 12 2zm4.586 14.424c-.18.295-.563.387-.857.207-2.35-1.435-5.305-1.76-8.786-.963-.335.077-.67-.133-.746-.469-.077-.336.132-.67.469-.746 3.809-.87 7.077-.496 9.713 1.115.293.18.386.563.207.856zm1.223-2.722c-.226.367-.706.482-1.072.257-2.687-1.652-6.785-2.131-9.965-1.166-.413.127-.848-.106-.973-.517-.125-.413.108-.848.52-.973 3.632-1.102 8.147-.568 11.233 1.328.366.226.48.707.257 1.071zm.105-2.835C14.692 8.95 9.375 8.775 6.297 9.71c-.493.15-1.016-.129-1.166-.623-.148-.495.13-1.016.625-1.166 3.532-1.073 9.404-.866 13.115 1.337.445.264.59.838.327 1.282-.264.443-.838.59-1.284.327z"/>
            </svg>
            Dare to Connect
          </motion.button>
          <p className="text-[#333] text-[12px] mt-3">Free · No credit card · Instant regret</p>
        </motion.div>
      </section>

      {/* Roast ticker */}
      <div className="overflow-hidden py-4 border-y border-[#141414] bg-[#0a0a0a]">
        <motion.div
          animate={{ x: [0, -1200] }}
          transition={{ repeat: Infinity, duration: 20, ease: 'linear' }}
          className="flex gap-12 whitespace-nowrap"
        >
          {[...ROAST_EXAMPLES, ...ROAST_EXAMPLES].map((r, i) => (
            <span key={i} className="text-[#333] text-[13px] italic">{r}</span>
          ))}
        </motion.div>
      </div>

      {/* Features */}
      <section className="px-6 py-16 max-w-4xl mx-auto">
        <h2 className="font-display font-bold text-3xl text-center mb-10">What awaits you</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {FEATURES.map((f, i) => (
            <motion.div key={f.title}
              initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="bg-[#0f0f0f] border border-[#1a1a1a] rounded-2xl p-6 hover:border-[#252525] transition-all"
            >
              <div className="text-3xl mb-3">{f.icon}</div>
              <div className="font-display font-bold text-[18px] mb-1" style={{ color: f.color }}>{f.title}</div>
              <div className="text-[#555] text-[13px] leading-relaxed">{f.desc}</div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Awards preview */}
      <section className="px-6 py-12 max-w-4xl mx-auto">
        <h2 className="font-display font-bold text-3xl text-center mb-3">Squad Awards</h2>
        <p className="text-[#444] text-center text-[14px] mb-8">Your friend group will receive these prestigious titles</p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {[
            { award: '👑 Music Overlord',     desc: 'The best taste (allegedly)' },
            { award: '💀 Needs Therapy',      desc: 'Saddest playlist detected' },
            { award: '🤡 Spotify\'s Puppet',  desc: 'Most mainstream listener' },
            { award: '🔥 Hype Beast',         desc: 'Highest energy music' },
            { award: '🧅 Too Cool For This',  desc: 'Most obscure taste' },
            { award: '🔁 One-Trick Pony',     desc: 'Obsessed with one artist' },
            { award: '🌍 World Citizen',      desc: 'Most genre diversity' },
            { award: '😴 Background Music',   desc: 'Most chill/ambient' },
          ].map(a => (
            <div key={a.award} className="bg-[#0a0a0a] border border-[#1a1a1a] rounded-xl p-3 text-center">
              <div className="font-semibold text-[13px] mb-1">{a.award}</div>
              <div className="text-[#444] text-[11px]">{a.desc}</div>
            </div>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="px-6 py-16 text-center">
        <div className="max-w-lg mx-auto bg-[#0f0f0f] border border-[#1a1a1a] rounded-3xl p-10">
          <div className="text-4xl mb-4">🎵</div>
          <h2 className="font-display font-bold text-3xl mb-3">Ready to be judged?</h2>
          <p className="text-[#555] text-[14px] mb-6">Your music taste has been unexamined long enough.</p>
          <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }} onClick={login}
            className="bg-[#1DB954] hover:bg-[#17a349] text-black font-bold text-[15px] px-8 py-3.5 rounded-2xl transition-all">
            Connect with Spotify →
          </motion.button>
        </div>
      </section>

      <footer className="text-center py-6 text-[#2a2a2a] text-[12px] border-t border-[#0f0f0f]">
        Auracle v2 · Built for chaos · No music tastes were harmed (emotionally, maybe)
      </footer>
    </div>
  )
}
