import { useState, useRef } from 'react'
import { motion } from 'framer-motion'
import { useAuth } from '../context/AuthContext'
import { profileApi, roastApi } from '../utils/api'
import { useFetch } from '../hooks/useFetch'
import { Card, Btn, Badge, Avatar, TrackRow, ArtistRow, ScoreRing, PersonalityPill, SectionTitle, Skeleton, ErrorMsg } from '../components/ui'
import html2canvas from 'html2canvas'
import toast from 'react-hot-toast'

const TERMS = { short_term: '4 Weeks', medium_term: '6 Months', long_term: 'All Time' }
const SCORE_COLOR = (s) => s >= 70 ? '#1DB954' : s >= 50 ? '#f59e0b' : '#f87171'

export default function Me() {
  const { user }       = useAuth()
  const [term, setTerm] = useState('short_term')
  const cardRef         = useRef(null)
  const [downloading, setDownloading] = useState(false)
  const [horoscope,   setHoroscope]   = useState(null)
  const [loadingH,    setLoadingH]    = useState(false)

  const { data, loading, error } = useFetch(() => profileApi.me(term), [term])

  const handleDownloadCard = async () => {
    if (!cardRef.current) return
    setDownloading(true)
    try {
      const canvas = await html2canvas(cardRef.current, { backgroundColor: '#080808', scale: 2 })
      const a = document.createElement('a')
      a.download = `auracle-${user?.public_slug}.png`
      a.href = canvas.toDataURL('image/png')
      a.click()
      toast.success('Vibe card downloaded! 🎉')
    } catch { toast.error('Download failed') }
    finally { setDownloading(false) }
  }

  const fetchHoroscope = async () => {
    setLoadingH(true)
    try {
      const { data: h } = await profileApi.horoscope(term)
      setHoroscope(h)
    } catch { toast.error('Horoscope failed') }
    finally { setLoadingH(false) }
  }

  const shareProfile = () => {
    const url = `${window.location.origin}/u/${user?.public_slug}`
    navigator.clipboard.writeText(url)
    toast.success('Profile link copied!')
  }

  if (error) return <ErrorMsg message={error} />

  const profile = data

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div>
          <h1 className="font-display font-extrabold text-3xl">Your Profile</h1>
          <p className="text-[#555] text-[13px] mt-1">Only your Spotify data — no global comparisons</p>
        </div>
        {/* Term toggle */}
        <div className="flex bg-[#0f0f0f] border border-[#252525] rounded-xl overflow-hidden">
          {Object.entries(TERMS).map(([k, v]) => (
            <button key={k} onClick={() => setTerm(k)}
              className={`px-3 py-2 text-[12px] font-medium transition-all ${term === k ? 'bg-[#1DB954] text-black font-bold' : 'text-[#555] hover:text-white'}`}>
              {v}
            </button>
          ))}
        </div>
      </div>

      {/* Vibe Card + Scores */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">

        {/* Vibe card */}
        <div>
          <div ref={cardRef}
            className="rounded-3xl p-7 text-center relative overflow-hidden"
            style={{ background: 'linear-gradient(135deg, #080808 0%, #0f1a0a 50%, #0a0810 100%)', border: '1px solid #1a1a1a' }}
          >
            <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 rounded-full bg-[#1DB95408] blur-3xl pointer-events-none" />
            <div className="relative">
              <div className="text-[10px] uppercase tracking-[3px] text-[#333] mb-5">Auracle · {TERMS[term]}</div>
              <Avatar src={user?.avatar_url} name={user?.display_name} size="xl" />
              <div className="font-display font-bold text-xl mt-3">{user?.display_name}</div>
              <div className="text-[12px] text-[#333] mb-4">@{user?.public_slug}</div>

              {loading
                ? <div className="space-y-2"><Skeleton h="h-6" w="w-32" className="mx-auto" /><Skeleton h="h-4" w="w-48" className="mx-auto" /></div>
                : <>
                    <PersonalityPill type={profile?.personality_type || '—'} />
                    <div className="grid grid-cols-2 gap-3 mt-5 text-left">
                      {[
                        { label: 'Top Artist', val: profile?.top_artist_names?.[0] || '—' },
                        { label: 'Top Genre',  val: profile?.genres?.[0]            || '—' },
                        { label: 'Energy',     val: `${Math.round((profile?.mood?.energy    || 0) * 100)}%`, color: '#f59e0b' },
                        { label: 'Happiness',  val: `${Math.round((profile?.mood?.valence   || 0) * 100)}%`, color: '#1DB954' },
                      ].map(s => (
                        <div key={s.label} className="bg-white/5 rounded-xl p-3">
                          <div className="text-[9px] uppercase tracking-wider text-[#444] mb-1">{s.label}</div>
                          <div className="font-semibold text-[13px] truncate" style={{ color: s.color || '#fff' }}>{s.val}</div>
                        </div>
                      ))}
                    </div>
                  </>
              }
              <div className="mt-5 text-[9px] tracking-[2px] text-[#222] uppercase">auracle.app</div>
            </div>
          </div>
          <div className="flex gap-3 mt-3">
            <Btn onClick={handleDownloadCard} disabled={loading || downloading} className="flex-1">
              {downloading ? '⏳' : '⬇'} Download Card
            </Btn>
            <Btn onClick={shareProfile} variant="ghost" className="flex-1">🔗 Share Profile</Btn>
          </div>
        </div>

        {/* Scores + mood */}
        <div className="space-y-4">
          <Card>
            <SectionTitle>Taste Scores</SectionTitle>
            {loading
              ? <div className="flex gap-4 flex-wrap"><Skeleton h="h-24" w="w-20" /><Skeleton h="h-24" w="w-20" /><Skeleton h="h-24" w="w-20" /></div>
              : (
                <div className="flex flex-wrap gap-4 justify-around">
                  {[
                    { label: 'Overall',    val: profile?.scores?.overall      || 0 },
                    { label: 'Diversity',  val: profile?.scores?.diversity    || 0 },
                    { label: 'Uniqueness', val: profile?.scores?.uniqueness   || 0 },
                    { label: 'Consistency',val: profile?.scores?.consistency  || 0 },
                  ].map(s => (
                    <ScoreRing key={s.label} score={s.val} color={SCORE_COLOR(s.val)} label={s.label} size={72} />
                  ))}
                </div>
              )
            }
          </Card>

          <Card>
            <SectionTitle>Mood Profile</SectionTitle>
            {loading
              ? <div className="space-y-3"><Skeleton h="h-4" /><Skeleton h="h-4" /><Skeleton h="h-4" /></div>
              : (
                <div className="space-y-3">
                  {[
                    { label: 'Energy',      val: Math.round((profile?.mood?.energy      || 0) * 100), color: '#f59e0b' },
                    { label: 'Happiness',   val: Math.round((profile?.mood?.valence     || 0) * 100), color: '#1DB954' },
                    { label: 'Danceability',val: Math.round((profile?.mood?.dance       || 0) * 100), color: '#a855f7' },
                    { label: 'Mainstream',  val: Math.round((profile?.mood?.mainstream  || 0) * 100), color: '#f87171' },
                  ].map(m => (
                    <div key={m.label}>
                      <div className="flex justify-between text-[12px] mb-1">
                        <span className="text-[#666]">{m.label}</span>
                        <span className="font-semibold" style={{ color: m.color }}>{m.val}%</span>
                      </div>
                      <div className="h-2 bg-[#161616] rounded-full overflow-hidden">
                        <motion.div initial={{ width: 0 }} animate={{ width: `${m.val}%` }}
                          transition={{ duration: 0.7, delay: 0.1 }}
                          className="h-full rounded-full" style={{ background: m.color }} />
                      </div>
                    </div>
                  ))}
                </div>
              )
            }
          </Card>

          {/* Intervention */}
          {!loading && profile?.intervention?.needed && (
            <div className="bg-[#ff4d0015] border border-[#ff4d0030] rounded-2xl p-4">
              <div className="text-[11px] font-bold uppercase tracking-wider text-[#ff4d00] mb-2">⚠️ Intervention Required</div>
              <p className="text-[#ccc] text-[13px] leading-relaxed">{profile.intervention.message}</p>
            </div>
          )}
        </div>
      </div>

      {/* Genres */}
      {!loading && profile?.genres?.length > 0 && (
        <Card>
          <SectionTitle>Your Genres</SectionTitle>
          <div className="flex flex-wrap gap-2">
            {profile.genres.slice(0, 15).map((g, i) => (
              <span key={g} className="px-3 py-1.5 rounded-full text-[12px] font-medium border"
                style={{
                  background: `hsl(${i * 25}, 60%, 12%)`,
                  borderColor: `hsl(${i * 25}, 60%, 20%)`,
                  color: `hsl(${i * 25}, 70%, 65%)`,
                }}>
                {g}
              </span>
            ))}
          </div>
        </Card>
      )}

      {/* Top Tracks + Artists */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
        <Card>
          <SectionTitle>Top Tracks</SectionTitle>
          {loading
            ? Array(6).fill(0).map((_, i) => <div key={i} className="flex gap-3 py-2"><Skeleton h="h-10" w="w-10" /><div className="flex-1 space-y-2"><Skeleton h="h-3" /><Skeleton h="h-2" w="w-2/3" /></div></div>)
            : (profile?.top_tracks || []).slice(0, 8).map((t, i) => <TrackRow key={t.id} track={t} rank={i + 1} />)
          }
        </Card>
        <Card>
          <SectionTitle>Top Artists</SectionTitle>
          {loading
            ? Array(6).fill(0).map((_, i) => <div key={i} className="flex gap-3 py-2"><Skeleton h="h-10" w="w-10" className="rounded-full" /><div className="flex-1 space-y-2"><Skeleton h="h-3" /><Skeleton h="h-2" w="w-1/2" /></div></div>)
            : (profile?.top_artists || []).slice(0, 8).map((a, i) => <ArtistRow key={a.id} artist={a} rank={i + 1} />)
          }
        </Card>
      </div>

      {/* Music Horoscope */}
      <Card>
        <SectionTitle sub="AI-generated based on your actual listening data">🔮 Music Horoscope</SectionTitle>
        {horoscope
          ? (
            <div className="space-y-4">
              <div className="bg-[#0a0a1a] border border-[#1a1a2a] rounded-xl p-4">
                <div className="text-[10px] uppercase tracking-wider text-[#a855f7] mb-2">This Week's Forecast</div>
                <p className="text-[#aaa] text-[14px] leading-relaxed">{horoscope.horoscope}</p>
              </div>
              {horoscope.three_words && (
                <div className="text-center">
                  <div className="text-[11px] text-[#444] uppercase tracking-wider mb-1">Your taste in 3 words</div>
                  <div className="font-display font-bold text-2xl text-[#1DB954]">{horoscope.three_words}</div>
                </div>
              )}
            </div>
          )
          : (
            <div className="text-center py-6">
              <div className="text-3xl mb-3">🔮</div>
              <p className="text-[#555] text-[13px] mb-4">The stars are ready to judge your music taste</p>
              <Btn onClick={fetchHoroscope} loading={loadingH} variant="ghost">Read My Horoscope</Btn>
            </div>
          )
        }
      </Card>
    </div>
  )
}
