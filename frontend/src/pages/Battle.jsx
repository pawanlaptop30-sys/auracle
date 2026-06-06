import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { battleApi } from '../utils/api'
import { Card, Btn, SectionTitle } from '../components/ui'
import toast from 'react-hot-toast'
import { useAuth } from '../context/AuthContext'

const TERMS = { short_term: '4 Weeks', medium_term: '6 Months', long_term: 'All Time' }

export default function Battle() {
  const { user }    = useAuth()
  const navigate    = useNavigate()
  const [slug, setSlug]   = useState('')
  const [term, setTerm]   = useState('short_term')
  const [loading, setLoading] = useState(false)

  const handleBattle = async () => {
    if (!slug.trim()) { toast.error('Enter a profile slug'); return }
    if (slug.trim() === user?.public_slug) { toast.error("You can't battle yourself 😭"); return }
    setLoading(true)
    try {
      const { data } = await battleApi.create(slug.trim(), term)
      navigate(`/battle/${data.slug}`)
    } catch (e) {
      toast.error(e?.response?.data?.detail || 'Could not start battle')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display font-extrabold text-3xl">⚔️ Taste Battle</h1>
        <p className="text-[#555] text-[13px] mt-1">1v1 — AI judge decides who has better music taste. No mercy.</p>
      </div>

      <Card>
        <SectionTitle>Challenge Someone</SectionTitle>
        <div className="space-y-4">
          <div>
            <label className="text-[12px] text-[#555] mb-1.5 block">Their Auracle profile slug</label>
            <input
              value={slug}
              onChange={e => setSlug(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleBattle()}
              placeholder="e.g. john-x4k2"
              className="w-full bg-[#161616] border border-[#252525] rounded-xl px-4 py-3 text-[14px] text-white placeholder-[#333] outline-none focus:border-[#1DB95450] transition-colors"
            />
            <p className="text-[11px] text-[#333] mt-1.5">Your slug: <span className="text-[#1DB954]">{user?.public_slug}</span> — share it so others can challenge you</p>
          </div>

          <div>
            <label className="text-[12px] text-[#555] mb-1.5 block">Compare period</label>
            <div className="flex gap-2 flex-wrap">
              {Object.entries(TERMS).map(([k, v]) => (
                <button key={k} onClick={() => setTerm(k)}
                  className={`px-3 py-1.5 rounded-lg text-[12px] font-medium transition-all border ${
                    term === k ? 'bg-[#1DB954] text-black border-[#1DB954]' : 'bg-[#0f0f0f] text-[#555] border-[#252525] hover:text-white'
                  }`}>
                  {v}
                </button>
              ))}
            </div>
          </div>

          <Btn onClick={handleBattle} loading={loading} size="lg" className="w-full" variant="fire">
            ⚔️ Start Battle
          </Btn>
        </div>
      </Card>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {[
          { icon: '📊', title: 'Real Data Only', desc: "Both profiles compared using your actual Spotify listening data — no fake scores" },
          { icon: '🤖', title: 'AI Judge',       desc: "LLaMA 3.3 70B delivers a funny, specific verdict citing your actual artists" },
          { icon: '📤', title: 'Share Result',   desc: "Share the battle result with anyone — even people without Auracle" },
        ].map(f => (
          <Card key={f.title}>
            <div className="text-2xl mb-2">{f.icon}</div>
            <div className="font-semibold text-[14px] mb-1">{f.title}</div>
            <div className="text-[#555] text-[12px] leading-relaxed">{f.desc}</div>
          </Card>
        ))}
      </div>

      <Card className="border-[#f59e0b30] bg-[#f59e0b08]">
        <div className="text-[11px] uppercase tracking-wider text-[#f59e0b] mb-2">💡 How It Works</div>
        <div className="space-y-2 text-[13px] text-[#888]">
          <p>1. Enter your opponent's Auracle profile slug</p>
          <p>2. Both your Spotify histories are analyzed</p>
          <p>3. AI judges taste diversity, uniqueness, energy, and consistency</p>
          <p>4. A verdict is delivered with individual roasts for both sides</p>
          <p>5. Share the result and let the drama unfold</p>
        </div>
      </Card>
    </div>
  )
}
