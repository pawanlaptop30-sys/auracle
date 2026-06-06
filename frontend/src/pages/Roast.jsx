import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { roastApi } from '../utils/api'
import { Card, Btn, Badge, SectionTitle, Skeleton } from '../components/ui'
import toast from 'react-hot-toast'

const SEVERITIES = [
  { key: 'gentle',    label: '😊 Gentle',    desc: 'Politely passive-aggressive',     color: '#1DB954' },
  { key: 'roasted',   label: '🔥 Roasted',   desc: 'Standard funny burns',            color: '#f59e0b' },
  { key: 'destroyed', label: '💀 Destroyed', desc: 'Absolutely no mercy',             color: '#f87171' },
  { key: 'courtroom', label: '👨‍⚖️ Courtroom', desc: 'Formal legal verdict on your taste', color: '#a855f7' },
]

const CATEGORIES = [
  { key: 'age',        label: '🎂 Age Roast',       desc: 'Based on the era of your music'     },
  { key: 'mainstream', label: '🤡 Mainstream Roast', desc: 'For Spotify algorithm followers'    },
  { key: 'obsessive',  label: '😤 Intervention',     desc: 'For one-artist obsessives'          },
  { key: 'sad',        label: '💔 Sad Playlist',     desc: 'Your depression playlist exposed'   },
  { key: 'energy',     label: '⚡ Energy Roast',      desc: 'Too hype or too chill? Find out'   },
]

const TERMS = { short_term: '4 Weeks', medium_term: '6 Months', long_term: 'All Time' }

const LOADING_MSGS = [
  'Consulting the AI overlords about your taste…',
  'Preparing the most loving takedown of your life…',
  'Reading your Spotify history with disgust…',
  'Writing your musical eulogy…',
  'Summoning the roast gods…',
]

export default function Roast() {
  const [severity,   setSeverity]   = useState('roasted')
  const [term,       setTerm]       = useState('short_term')
  const [result,     setResult]     = useState(null)
  const [alibi,      setAlibi]      = useState(null)
  const [loading,    setLoading]    = useState(false)
  const [loadingAlibi, setLoadingAlibi] = useState(false)
  const [loadingCat, setLoadingCat] = useState(null)
  const [catResults, setCatResults] = useState({})
  const [loadingMsg, setLoadingMsg] = useState('')
  const [activeTab,  setActiveTab]  = useState('severity')

  const getRoasted = async () => {
    setLoading(true)
    setResult(null)
    setLoadingMsg(LOADING_MSGS[Math.floor(Math.random() * LOADING_MSGS.length)])
    try {
      const { data } = await roastApi.me(severity, term)
      setResult(data)
    } catch (e) {
      toast.error(e?.response?.data?.detail || 'Roast failed')
    } finally {
      setLoading(false)
    }
  }

  const getCategoryRoast = async (category) => {
    setLoadingCat(category)
    try {
      const { data } = await roastApi.category(category, term)
      setCatResults(prev => ({ ...prev, [category]: data.roast }))
    } catch {
      toast.error('Category roast failed')
    } finally {
      setLoadingCat(null)
    }
  }

  const getAlibi = async () => {
    setLoadingAlibi(true)
    try {
      const { data } = await roastApi.alibi(term)
      setAlibi(data.alibi)
    } catch {
      toast.error('Alibi generation failed')
    } finally {
      setLoadingAlibi(false)
    }
  }

  const shareRoast = () => {
    if (!result?.roast) return
    navigator.clipboard.writeText(`My Auracle roast: "${result.roast}" 💀`)
    toast.success('Roast copied — share the pain!')
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="font-display font-extrabold text-3xl">🔥 Get Roasted</h1>
        <p className="text-[#555] text-[13px] mt-1">AI-powered judgment of your music taste. You asked for this.</p>
      </div>

      {/* Term selector */}
      <div className="flex gap-2 flex-wrap">
        <span className="text-[12px] text-[#555] self-center">Period:</span>
        {Object.entries(TERMS).map(([k, v]) => (
          <button key={k} onClick={() => setTerm(k)}
            className={`px-3 py-1.5 rounded-lg text-[12px] font-medium transition-all border ${
              term === k ? 'bg-[#1DB954] text-black border-[#1DB954]' : 'bg-[#0f0f0f] text-[#555] border-[#252525] hover:text-white'
            }`}>
            {v}
          </button>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-[#0f0f0f] border border-[#252525] rounded-xl p-1">
        {[
          { key: 'severity',   label: '💀 Severity Levels' },
          { key: 'categories', label: '🎭 Roast Categories' },
          { key: 'alibi',      label: '⚖️ Get an Alibi' },
        ].map(t => (
          <button key={t.key} onClick={() => setActiveTab(t.key)}
            className={`flex-1 py-2 rounded-lg text-[12px] md:text-[13px] font-medium transition-all ${
              activeTab === t.key ? 'bg-[#1a1a1a] text-white' : 'text-[#555] hover:text-[#888]'
            }`}>
            {t.label}
          </button>
        ))}
      </div>

      {/* Severity tab */}
      {activeTab === 'severity' && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {SEVERITIES.map(s => (
              <motion.button key={s.key} whileTap={{ scale: 0.97 }} onClick={() => setSeverity(s.key)}
                className={`p-4 rounded-2xl border text-left transition-all ${
                  severity === s.key
                    ? 'border-opacity-60 bg-opacity-10'
                    : 'border-[#1e1e1e] bg-[#0f0f0f] hover:border-[#2a2a2a]'
                }`}
                style={severity === s.key ? { borderColor: s.color, background: `${s.color}12` } : {}}
              >
                <div className="text-2xl mb-2">{s.label.split(' ')[0]}</div>
                <div className="font-semibold text-[13px]" style={{ color: severity === s.key ? s.color : '#fff' }}>
                  {s.label.slice(s.label.indexOf(' ') + 1)}
                </div>
                <div className="text-[11px] text-[#555] mt-1">{s.desc}</div>
              </motion.button>
            ))}
          </div>

          <Btn onClick={getRoasted} loading={loading} size="lg" className="w-full"
            variant={severity === 'destroyed' ? 'fire' : severity === 'courtroom' ? 'purple' : 'green'}>
            {loading ? loadingMsg : `${SEVERITIES.find(s => s.key === severity)?.label} — Roast Me`}
          </Btn>

          <AnimatePresence>
            {result && (
              <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                <Card className={severity === 'destroyed' ? 'border-[#ff4d0040] bg-[#ff4d0008]' : severity === 'courtroom' ? 'border-[#a855f740] bg-[#a855f708]' : ''}>
                  <div className="flex items-center justify-between mb-4">
                    <Badge color={severity === 'destroyed' ? 'fire' : severity === 'courtroom' ? 'purple' : severity === 'roasted' ? 'amber' : 'green'}>
                      {SEVERITIES.find(s => s.key === severity)?.label}
                    </Badge>
                    <span className="text-[11px] text-[#444]">{TERMS[term]}</span>
                  </div>

                  <p className="text-[15px] leading-relaxed text-[#ddd] mb-4">"{result.roast}"</p>

                  <div className="flex items-center gap-3 flex-wrap">
                    {result.personality_type && (
                      <span className="text-[12px] bg-[#161616] border border-[#252525] rounded-full px-3 py-1">
                        {result.personality_type}
                      </span>
                    )}
                    {result.scores?.overall && (
                      <span className="text-[12px] text-[#555]">Taste score: {result.scores.overall}</span>
                    )}
                    <Btn onClick={shareRoast} variant="ghost" size="sm" className="ml-auto">📋 Copy & Share</Btn>
                    <Btn onClick={getRoasted} loading={loading} variant="outline" size="sm">🔄 Roast Again</Btn>
                  </div>
                </Card>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      )}

      {/* Categories tab */}
      {activeTab === 'categories' && (
        <div className="space-y-3">
          {CATEGORIES.map(cat => (
            <Card key={cat.key}>
              <div className="flex items-start justify-between gap-4 flex-wrap">
                <div className="flex-1">
                  <div className="font-semibold text-[14px] mb-0.5">{cat.label}</div>
                  <div className="text-[12px] text-[#555]">{cat.desc}</div>
                  {catResults[cat.key] && (
                    <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                      className="text-[13px] text-[#ccc] leading-relaxed mt-3 pt-3 border-t border-[#1a1a1a]">
                      "{catResults[cat.key]}"
                    </motion.p>
                  )}
                </div>
                <Btn onClick={() => getCategoryRoast(cat.key)}
                  loading={loadingCat === cat.key} variant="ghost" size="sm" className="flex-shrink-0">
                  {catResults[cat.key] ? '🔄 Again' : '🔥 Roast'}
                </Btn>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Alibi tab */}
      {activeTab === 'alibi' && (
        <div className="space-y-4">
          <Card>
            <SectionTitle sub="AI generates the most creative defense of your terrible taste">⚖️ Alibi Generator</SectionTitle>
            <p className="text-[#555] text-[13px] mb-4">
              Got called out for your music taste? Need a lawyer-level defense? We got you.
            </p>
            <Btn onClick={getAlibi} loading={loadingAlibi} variant="purple" className="w-full">
              Generate My Alibi
            </Btn>
            <AnimatePresence>
              {alibi && (
                <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                  className="mt-4 bg-[#a855f710] border border-[#a855f730] rounded-xl p-4">
                  <div className="text-[10px] uppercase tracking-wider text-[#a855f7] mb-2">⚖️ Your Defense</div>
                  <p className="text-[#ccc] text-[14px] leading-relaxed">"{alibi}"</p>
                  <Btn onClick={() => { navigator.clipboard.writeText(alibi); toast.success('Alibi copied!') }}
                    variant="ghost" size="sm" className="mt-3">📋 Copy Alibi</Btn>
                </motion.div>
              )}
            </AnimatePresence>
          </Card>

          <Card className="border-[#f59e0b30] bg-[#f59e0b08]">
            <div className="text-[11px] uppercase tracking-wider text-[#f59e0b] mb-2">💡 Pro Tip</div>
            <p className="text-[#888] text-[13px] leading-relaxed">
              Screenshot your alibi and send it to anyone who has judged your playlist. Works especially well against people who also use Auracle.
            </p>
          </Card>
        </div>
      )}
    </div>
  )
}
