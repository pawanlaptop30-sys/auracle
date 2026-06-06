import { useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { squadApi } from '../utils/api'
import { useFetch } from '../hooks/useFetch'
import { Card, Btn, Avatar, ScoreRing, Badge, SectionTitle, ErrorMsg } from '../components/ui'
import html2canvas from 'html2canvas'
import toast from 'react-hot-toast'
import { useRef } from 'react'

const SCORE_COLOR = s => s >= 70 ? '#1DB954' : s >= 50 ? '#f59e0b' : '#f87171'
const RANK_MEDAL  = i => ['🥇','🥈','🥉','4️⃣'][i] || `${i+1}.`

export default function SquadRoom() {
  const { code }    = useParams()
  const navigate    = useNavigate()
  const resultRef   = useRef(null)
  const [roastLoading, setRoastLoading] = useState(false)
  const [freshRoast,   setFreshRoast]   = useState(null)
  const [activeTab,    setActiveTab]    = useState('leaderboard')

  const { data, loading, error, } = useFetch(() => squadApi.get(code), [code])

  const handleRefreshRoast = async () => {
    setRoastLoading(true)
    try {
      const { data: r } = await squadApi.refreshRoast(code)
      setFreshRoast(r.group_roast)
      toast.success('Fresh roast delivered 🔥')
    } catch { toast.error('Roast failed') }
    finally { setRoastLoading(false) }
  }

  const handleShare = () => {
    navigator.clipboard.writeText(`${window.location.origin}/squad/${code}`)
    toast.success('Squad link copied!')
  }

  const handleDownload = async () => {
    if (!resultRef.current) return
    try {
      const canvas = await html2canvas(resultRef.current, { backgroundColor: '#080808', scale: 2 })
      const a = document.createElement('a')
      a.download = `auracle-squad-${code}.png`
      a.href = canvas.toDataURL('image/png')
      a.click()
      toast.success('Squad card downloaded!')
    } catch { toast.error('Download failed') }
  }

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-[#080808]">
      <div className="flex flex-col items-center gap-4">
        <div className="w-12 h-12 border-2 border-[#1DB954] border-t-transparent rounded-full animate-spin" />
        <p className="font-display text-[#555]">Loading squad results…</p>
      </div>
    </div>
  )

  if (error) return (
    <div className="min-h-screen flex items-center justify-center bg-[#080808] p-6">
      <ErrorMsg message={error} />
    </div>
  )

  const members     = data?.members     || []
  const leaderboard = data?.leaderboard || []
  const awards      = data?.awards      || []
  const groupRoast  = freshRoast || data?.group_roast
  const pairs       = data?.pairs       || []

  return (
    <div className="min-h-screen bg-[#080808] p-4 md:p-6 max-w-3xl mx-auto pb-10">
      <button onClick={() => navigate(-1)} className="text-[#444] hover:text-white text-[13px] mb-5 transition-colors">← Back</button>

      {/* Header */}
      <div className="flex items-start justify-between gap-4 mb-6 flex-wrap">
        <div>
          <h1 className="font-display font-extrabold text-3xl">{data?.name || 'The Squad'}</h1>
          <p className="text-[#555] text-[13px] mt-1">
            Code: <span className="font-display text-[#1DB954] tracking-wider">{code}</span>
            {' · '}{members.length}/{data?.max_members} members
            {!data?.is_complete && <span className="text-[#f59e0b] ml-2">· Waiting for more…</span>}
          </p>
        </div>
        <div className="flex gap-2">
          {!data?.is_complete && (
            <Btn onClick={handleShare} variant="ghost" size="sm">🔗 Invite</Btn>
          )}
          <Btn onClick={handleDownload} variant="ghost" size="sm">⬇ Save</Btn>
        </div>
      </div>

      {/* Waiting state */}
      {members.length < 2 && (
        <Card className="text-center py-10 mb-6">
          <div className="text-4xl mb-3">⏳</div>
          <div className="font-display font-bold text-xl mb-2">Waiting for friends…</div>
          <p className="text-[#555] text-[13px] mb-4">Share the code <span className="font-display text-[#1DB954] tracking-wider">{code}</span> to get started</p>
          <Btn onClick={handleShare}>🔗 Copy Invite Link</Btn>
        </Card>
      )}

      {members.length >= 2 && (
        <>
          {/* Tabs */}
          <div className="flex gap-1 bg-[#0f0f0f] border border-[#252525] rounded-xl p-1 mb-5">
            {[
              { key: 'leaderboard', label: '🏆 Leaderboard' },
              { key: 'awards',      label: '🎖️ Awards' },
              { key: 'roast',       label: '🔥 Group Roast' },
              { key: 'compat',      label: '💞 Compatibility' },
            ].map(t => (
              <button key={t.key} onClick={() => setActiveTab(t.key)}
                className={`flex-1 py-2 rounded-lg text-[11px] md:text-[12px] font-medium transition-all ${
                  activeTab === t.key ? 'bg-[#1a1a1a] text-white' : 'text-[#444] hover:text-[#888]'
                }`}>
                {t.label}
              </button>
            ))}
          </div>

          <div ref={resultRef}>
            {/* Leaderboard */}
            {activeTab === 'leaderboard' && (
              <div className="space-y-3">
                <div className="text-[11px] text-[#555] uppercase tracking-wider mb-1">Ranked by Taste Score</div>
                {leaderboard.map((m, i) => (
                  <motion.div key={m.display_name}
                    initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.08 }}>
                    <Card className={i === 0 ? 'border-[#f59e0b40] bg-[#f59e0b08]' : ''}>
                      <div className="flex items-center gap-4">
                        <div className="font-display text-2xl w-8 text-center flex-shrink-0">{RANK_MEDAL(i)}</div>
                        <Avatar src={members.find(mm => mm.display_name === m.display_name)?.avatar_url}
                          name={m.display_name} size="md" color={SCORE_COLOR(m.score)} />
                        <div className="flex-1 min-w-0">
                          <div className="font-display font-bold text-[15px] truncate">{m.display_name}</div>
                          <div className="text-[12px] text-[#555]">{m.personality_type}</div>
                          <div className="flex flex-wrap gap-1 mt-1">
                            {(m.genres || []).slice(0, 3).map(g => (
                              <span key={g} className="text-[10px] bg-[#161616] border border-[#1e1e1e] rounded-full px-2 py-0.5 text-[#666]">{g}</span>
                            ))}
                          </div>
                        </div>
                        <ScoreRing score={m.score} color={SCORE_COLOR(m.score)} size={60} />
                      </div>
                    </Card>
                  </motion.div>
                ))}
              </div>
            )}

            {/* Awards */}
            {activeTab === 'awards' && (
              <div className="space-y-3">
                {awards.length === 0
                  ? <Card><p className="text-[#555] text-center py-6">Awards will appear once 2+ members join</p></Card>
                  : awards.map((a, i) => (
                    <motion.div key={a.award}
                      initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.07 }}>
                      <Card>
                        <div className="flex items-start gap-4">
                          <div className="text-3xl flex-shrink-0">{a.award.split(' ')[0]}</div>
                          <div className="flex-1">
                            <div className="font-display font-bold text-[15px] text-[#f59e0b]">{a.award}</div>
                            <div className="text-[13px] font-semibold text-white mt-0.5">{a.user}</div>
                            <div className="text-[12px] text-[#555] mt-0.5">{a.reason}</div>
                          </div>
                        </div>
                      </Card>
                    </motion.div>
                  ))
                }
              </div>
            )}

            {/* Group Roast */}
            {activeTab === 'roast' && (
              <div className="space-y-4">
                {groupRoast
                  ? (
                    <Card className="border-[#ff4d0030] bg-[#ff4d0008]">
                      <div className="flex items-center justify-between mb-3">
                        <div className="text-[10px] uppercase tracking-wider text-[#ff4d00]">🔥 Group Roast</div>
                        <Btn onClick={handleRefreshRoast} loading={roastLoading} variant="ghost" size="sm">🔄 Fresh Roast</Btn>
                      </div>
                      <p className="text-[14px] text-[#ccc] leading-relaxed">"{groupRoast}"</p>
                      <Btn onClick={() => { navigator.clipboard.writeText(groupRoast); toast.success('Roast copied!') }}
                        variant="ghost" size="sm" className="mt-3">📋 Copy & Share</Btn>
                    </Card>
                  )
                  : (
                    <Card className="text-center py-8">
                      <div className="text-3xl mb-3">🔥</div>
                      <p className="text-[#555] text-[13px] mb-4">Group roast will auto-generate when 2+ members join</p>
                      <Btn onClick={handleRefreshRoast} loading={roastLoading}>Generate Group Roast</Btn>
                    </Card>
                  )
                }

                {/* Individual roasts */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {members.map(m => (
                    <Card key={m.display_name}>
                      <div className="flex items-center gap-3 mb-2">
                        <Avatar src={m.avatar_url} name={m.display_name} size="sm" />
                        <div>
                          <div className="font-semibold text-[13px]">{m.display_name}</div>
                          <div className="text-[11px] text-[#555]">{m.personality_type}</div>
                        </div>
                      </div>
                      <div className="text-[12px] text-[#555] space-y-0.5">
                        <div>Top artist: <span className="text-[#888]">{m.top_artist || '—'}</span></div>
                        <div>Genres: <span className="text-[#888]">{(m.genres || []).slice(0, 2).join(', ') || '—'}</span></div>
                        <div>Score: <span className="font-semibold" style={{ color: SCORE_COLOR(m.scores?.overall || 0) }}>{m.scores?.overall || 0}</span></div>
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {/* Compatibility pairs */}
            {activeTab === 'compat' && (
              <div className="space-y-3">
                {pairs.length === 0
                  ? <Card><p className="text-[#555] text-center py-6">Need 2+ members for compatibility</p></Card>
                  : pairs.map((p, i) => (
                    <Card key={`${p.user_a}-${p.user_b}`}>
                      <div className="flex items-center gap-4">
                        <div className="flex-1">
                          <div className="font-semibold text-[14px]">{p.user_a} × {p.user_b}</div>
                          {p.shared_artists?.length > 0 && (
                            <div className="text-[12px] text-[#555] mt-1">
                              Both like: {p.shared_artists.slice(0, 3).join(', ')}
                            </div>
                          )}
                        </div>
                        <ScoreRing score={p.compat} size={56}
                          color={p.compat >= 60 ? '#1DB954' : p.compat >= 40 ? '#f59e0b' : '#f87171'} />
                      </div>
                      <div className="mt-2 text-[12px] text-[#555]">
                        {p.compat >= 70 ? '💚 Basically the same person' :
                         p.compat >= 50 ? '🤝 Common ground exists' :
                         p.compat >= 30 ? '🌍 Musical strangers' : '🌗 Opposite universes — do NOT share an aux'}
                      </div>
                    </Card>
                  ))
                }
              </div>
            )}
          </div>
        </>
      )}

      {/* Invite section if not complete */}
      {!data?.is_complete && members.length >= 1 && (
        <Card className="mt-5 border-[#1DB95430] bg-[#1DB95408]">
          <div className="flex items-center justify-between gap-4 flex-wrap">
            <div>
              <div className="font-semibold text-[14px] text-[#1DB954] mb-0.5">Invite more friends</div>
              <div className="text-[#555] text-[13px]">
                {data.max_members - members.length} spot{data.max_members - members.length !== 1 ? 's' : ''} remaining
              </div>
            </div>
            <Btn onClick={handleShare}>🔗 Copy Invite Link</Btn>
          </div>
        </Card>
      )}
    </div>
  )
}
