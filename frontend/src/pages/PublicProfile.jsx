import { useParams, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { profileApi, battleApi } from '../utils/api'
import { useFetch } from '../hooks/useFetch'
import { Btn, Avatar, ErrorMsg } from '../components/ui'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'
import { useState } from 'react'

export default function PublicProfile() {
  const { slug }    = useParams()
  const navigate    = useNavigate()
  const { user }    = useAuth()
  const [battling, setBattling] = useState(false)

  const { data, loading, error } = useFetch(() => profileApi.public(slug), [slug])

  const handleBattle = async () => {
    if (!user) { toast.error('Log in to battle'); navigate('/'); return }
    setBattling(true)
    try {
      const { data: b } = await battleApi.create(slug)
      navigate(`/battle/${b.slug}`)
    } catch (e) {
      toast.error(e?.response?.data?.detail || 'Could not start battle')
    } finally {
      setBattling(false)
    }
  }

  if (loading) return (
    <div className="min-h-screen flex items-center justify-center bg-[#080808]">
      <div className="w-10 h-10 border-2 border-[#1DB954] border-t-transparent rounded-full animate-spin" />
    </div>
  )

  if (error) return (
    <div className="min-h-screen flex items-center justify-center bg-[#080808] p-6">
      <ErrorMsg message={error} />
    </div>
  )

  return (
    <div className="min-h-screen bg-[#080808] flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
        className="w-full max-w-sm"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <span className="font-display font-extrabold text-2xl text-[#1DB954]">Auracle</span>
          <p className="text-[#444] text-[12px] mt-1">Music Roast App</p>
        </div>

        {/* Profile card */}
        <div className="bg-[#0f0f0f] border border-[#1a1a1a] rounded-3xl p-8 text-center"
          style={{ background: 'linear-gradient(135deg, #0a0a0a, #0f1a0a)' }}>
          <Avatar src={data?.avatar_url} name={data?.display_name} size="xl" />
          <h1 className="font-display font-bold text-2xl mt-4">{data?.display_name}</h1>
          <p className="text-[#444] text-[12px] mt-1 mb-6">@{data?.public_slug}</p>

          <div className="space-y-3">
            {user?.public_slug !== slug ? (
              <>
                <Btn onClick={handleBattle} loading={battling} size="lg" variant="fire" className="w-full">
                  ⚔️ Battle Their Taste
                </Btn>
                <Btn onClick={() => { navigator.clipboard.writeText(window.location.href); toast.success('Link copied!') }}
                  variant="ghost" size="md" className="w-full">
                  🔗 Share This Profile
                </Btn>
              </>
            ) : (
              <Btn onClick={() => navigate('/app/me')} size="lg" className="w-full">
                🎧 My Dashboard
              </Btn>
            )}
          </div>

          {!user && (
            <p className="text-[#333] text-[11px] mt-4">
              <a href="/" className="text-[#1DB954] hover:underline">Join Auracle</a> to battle this person's taste
            </p>
          )}
        </div>

        <p className="text-center text-[#2a2a2a] text-[11px] mt-6">
          Member since {data?.member_since ? new Date(data.member_since).getFullYear() : '—'}
        </p>
      </motion.div>
    </div>
  )
}
