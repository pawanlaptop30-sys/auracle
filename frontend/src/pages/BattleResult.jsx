import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { battleApi } from '../utils/api'
import { useFetch } from '../hooks/useFetch'
import { Card, Btn, Avatar, ScoreRing, Badge, SectionTitle, ErrorMsg } from '../components/ui'
import html2canvas from 'html2canvas'
import toast from 'react-hot-toast'
import { useRef } from 'react'

const SCORE_COLOR = s => s >= 70 ? '#1DB954' : s >= 50 ? '#f59e0b' : '#f87171'

export default function BattleResult() {
  const { slug }  = useParams()
  const navigate  = useNavigate()
  const resultRef = useRef(null)
  const { data, loading, error } = useFetch(() => battleApi.get(slug), [slug])

  const handleDownload = async () => {
    if (!resultRef.current) return
    try {
      const canvas = await html2canvas(resultRef.current, { backgroundColor: '#080808', scale: 2 })
      const a = document.createElement('a')
      a.download = `auracle-battle-${slug}.png`
      a.href = canvas.toDataURL('image/png')
      a.click()
      toast.success('Battle card downloaded!')
    } catch { toast.error('Download failed') }
  }

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-[#080808]">
      <div className="flex flex-col items-center gap-4">
        <div className="w-12 h-12 border-2 border-[#ff4d00] border-t-transparent rounded-full animate-spin" />
        <p className="font-display text-[#555]">The judge is deliberating…</p>
      </div>
    </div>
  )

  if (error) return (
    <div className="min-h-screen flex items-center justify-center bg-[#080808] p-6">
      <ErrorMsg message={error} />
    </div>
  )

  const { user_a, user_b, verdict, winner } = data || {}
  const isWinnerA = winner === user_a?.name

  return (
    <div className="min-h-screen bg-[#080808] p-4 md:p-6 max-w-3xl mx-auto pb-10">
      <button onClick={() => navigate(-1)} className="text-[#444] hover:text-white text-[13px] mb-6 transition-colors">← Back</button>

      <div ref={resultRef} className="space-y-5">
        {/* Title */}
        <div className="text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-[#ff4d0020] border border-[#ff4d0040] text-[#ff4d00] text-[12px] font-semibold mb-4">
            ⚔️ Taste Battle
          </div>
          <h1 className="font-display font-extrabold text-4xl md:text-5xl mb-2">
            {user_a?.name} <span className="text-[#333]">vs</span> {user_b?.name}
          </h1>
        </div>

        {/* Contestants */}
        <div className="grid grid-cols-2 gap-3">
          {[
            { u: user_a, isWinner: isWinnerA,  color: '#1DB954' },
            { u: user_b, isWinner: !isWinnerA, color: '#a855f7' },
          ].map(({ u, isWinner, color }) => (
            <Card key={u?.name}
              className={`text-center transition-all ${isWinner ? 'border-opacity-60' : ''}`}
              style={isWinner ? { borderColor: color, background: `${color}08` } : {}}>
              {isWinner && (
                <div className="text-[11px] font-bold uppercase tracking-wider mb-2" style={{ color }}>
                  👑 WINNER
                </div>
              )}
              <Avatar src={u?.avatar_url} name={u?.name} size="lg" color={color} />
              <div className="font-display font-bold text-[15px] mt-2 truncate">{u?.name}</div>
              <div className="text-[11px] text-[#555] mb-3">{u?.personality_type}</div>
              <ScoreRing score={u?.taste_score || 0} color={color} size={64} label="Score" />
              <div className="mt-3 space-y-1">
                {(u?.top_artists || []).slice(0, 3).map(a => (
                  <div key={a} className="text-[11px] text-[#555] truncate">{a}</div>
                ))}
              </div>
            </Card>
          ))}
        </div>

        {/* AI Verdict */}
        <Card className="border-[#ff4d0030] bg-[#ff4d0008]">
          <div className="text-[10px] uppercase tracking-wider text-[#ff4d00] mb-3">👨‍⚖️ AI Verdict</div>
          <p className="text-[15px] text-[#ddd] leading-relaxed mb-4">"{verdict?.verdict}"</p>
          {verdict?.winning_reason && (
            <div className="bg-[#161616] rounded-xl p-3 mb-4">
              <span className="text-[11px] text-[#555]">Why {winner} won: </span>
              <span className="text-[13px] text-[#aaa]">{verdict.winning_reason}</span>
            </div>
          )}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {[
              { name: user_a?.name, roast: verdict?.user_a_roast, color: '#1DB954' },
              { name: user_b?.name, roast: verdict?.user_b_roast, color: '#a855f7' },
            ].map(r => (
              <div key={r.name} className="bg-[#0a0a0a] border border-[#1a1a1a] rounded-xl p-3">
                <div className="text-[10px] font-bold uppercase tracking-wider mb-1" style={{ color: r.color }}>{r.name}</div>
                <p className="text-[12px] text-[#888] leading-relaxed">"{r.roast}"</p>
              </div>
            ))}
          </div>
        </Card>

        {/* Compatibility */}
        {verdict?.compat_score != null && (
          <Card>
            <SectionTitle>Compatibility Score</SectionTitle>
            <div className="flex items-center gap-5">
              <ScoreRing
                score={verdict.compat_score}
                color={verdict.compat_score >= 60 ? '#1DB954' : verdict.compat_score >= 40 ? '#f59e0b' : '#f87171'}
                size={80}
              />
              <div>
                <div className="font-display font-bold text-xl mb-1">
                  {verdict.compat_score >= 70 ? 'Musical Soulmates 💚' :
                   verdict.compat_score >= 50 ? 'Common Ground 🤝' :
                   verdict.compat_score >= 30 ? 'Musical Strangers 🌍' : 'Opposite Universes 🌗'}
                </div>
                {verdict.tagline && <p className="text-[#555] text-[13px]">"{verdict.tagline}"</p>}
              </div>
            </div>
            {verdict.shared_artists?.length > 0 && (
              <div className="mt-3 pt-3 border-t border-[#1a1a1a]">
                <div className="text-[11px] text-[#555] mb-2">Artists you both like:</div>
                <div className="flex flex-wrap gap-2">
                  {verdict.shared_artists.slice(0, 6).map(a => (
                    <span key={a} className="px-2.5 py-1 bg-[#161616] border border-[#252525] rounded-full text-[11px] text-[#888]">{a}</span>
                  ))}
                </div>
              </div>
            )}
          </Card>
        )}

        {/* Mood comparison */}
        <Card>
          <SectionTitle>Mood Comparison</SectionTitle>
          <div className="space-y-3">
            {[
              { label: 'Energy',      ka: user_a?.mood?.energy,      kb: user_b?.mood?.energy      },
              { label: 'Happiness',   ka: user_a?.mood?.valence,     kb: user_b?.mood?.valence     },
              { label: 'Mainstream',  ka: user_a?.mood?.mainstream,  kb: user_b?.mood?.mainstream  },
            ].map(m => (
              <div key={m.label}>
                <div className="text-[12px] text-[#555] mb-1.5">{m.label}</div>
                <div className="flex items-center gap-2">
                  <span className="text-[10px] text-[#1DB954] w-14 truncate">{user_a?.name?.split(' ')[0]}</span>
                  <div className="flex-1 h-2 bg-[#161616] rounded-full overflow-hidden">
                    <div className="h-full bg-[#1DB954] rounded-full" style={{ width: `${Math.round((m.ka || 0) * 100)}%` }} />
                  </div>
                  <span className="text-[11px] text-[#444] w-8 text-right">{Math.round((m.ka || 0) * 100)}%</span>
                </div>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-[10px] text-[#a855f7] w-14 truncate">{user_b?.name?.split(' ')[0]}</span>
                  <div className="flex-1 h-2 bg-[#161616] rounded-full overflow-hidden">
                    <div className="h-full bg-[#a855f7] rounded-full" style={{ width: `${Math.round((m.kb || 0) * 100)}%` }} />
                  </div>
                  <span className="text-[11px] text-[#444] w-8 text-right">{Math.round((m.kb || 0) * 100)}%</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      {/* Actions */}
      <div className="flex flex-wrap gap-3 mt-6">
        <Btn onClick={handleDownload}>⬇ Download Card</Btn>
        <Btn onClick={() => { navigator.clipboard.writeText(window.location.href); toast.success('Link copied!') }} variant="ghost">🔗 Share Battle</Btn>
        <Btn onClick={() => navigate('/app/battle')} variant="outline">⚔️ New Battle</Btn>
      </div>
    </div>
  )
}
