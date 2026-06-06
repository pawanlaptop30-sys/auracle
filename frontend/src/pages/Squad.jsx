import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { squadApi } from '../utils/api'
import { Card, Btn, SectionTitle } from '../components/ui'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

export default function Squad() {
  const { user }    = useAuth()
  const navigate    = useNavigate()
  const [squadName, setSquadName] = useState('')
  const [joinCode,  setJoinCode]  = useState('')
  const [creating,  setCreating]  = useState(false)
  const [joining,   setJoining]   = useState(false)
  const [tab,       setTab]       = useState('create')

  const handleCreate = async () => {
    setCreating(true)
    try {
      const { data } = await squadApi.create(squadName || 'The Squad')
      toast.success(`Squad created! Code: ${data.code}`)
      navigate(`/squad/${data.code}`)
    } catch (e) {
      toast.error(e?.response?.data?.detail || 'Failed to create squad')
    } finally {
      setCreating(false)
    }
  }

  const handleJoin = async () => {
    if (!joinCode.trim()) { toast.error('Enter a squad code'); return }
    setJoining(true)
    try {
      await squadApi.join(joinCode.trim().toUpperCase())
      navigate(`/squad/${joinCode.trim().toUpperCase()}`)
    } catch (e) {
      toast.error(e?.response?.data?.detail || 'Could not join squad')
    } finally {
      setJoining(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display font-extrabold text-3xl">👥 Squad Mode</h1>
        <p className="text-[#555] text-[13px] mt-1">Up to 4 friends — awards ceremony + group roast. Democracy for bad taste.</p>
      </div>

      {/* Tab switcher */}
      <div className="flex gap-1 bg-[#0f0f0f] border border-[#252525] rounded-xl p-1">
        {[{ key: 'create', label: '🏗️ Create Squad' }, { key: 'join', label: '🚪 Join Squad' }].map(t => (
          <button key={t.key} onClick={() => setTab(t.key)}
            className={`flex-1 py-2.5 rounded-lg text-[13px] font-medium transition-all ${
              tab === t.key ? 'bg-[#1a1a1a] text-white' : 'text-[#555] hover:text-[#888]'
            }`}>
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'create' && (
        <Card>
          <SectionTitle sub="You'll get a 6-character code to share with friends">Create a new squad</SectionTitle>
          <div className="space-y-4">
            <div>
              <label className="text-[12px] text-[#555] mb-1.5 block">Squad Name (optional)</label>
              <input value={squadName} onChange={e => setSquadName(e.target.value)}
                placeholder="The Chaotic Playlist Enjoyers"
                className="w-full bg-[#161616] border border-[#252525] rounded-xl px-4 py-3 text-[14px] text-white placeholder-[#333] outline-none focus:border-[#1DB95450] transition-colors" />
            </div>
            <Btn onClick={handleCreate} loading={creating} size="lg" className="w-full">
              🏗️ Create Squad & Get Code
            </Btn>
          </div>
        </Card>
      )}

      {tab === 'join' && (
        <Card>
          <SectionTitle sub="Enter the 6-character code from your friend">Join an existing squad</SectionTitle>
          <div className="space-y-4">
            <div>
              <label className="text-[12px] text-[#555] mb-1.5 block">Squad Code</label>
              <input value={joinCode} onChange={e => setJoinCode(e.target.value.toUpperCase())}
                onKeyDown={e => e.key === 'Enter' && handleJoin()}
                placeholder="e.g. XK9P2M"
                maxLength={6}
                className="w-full bg-[#161616] border border-[#252525] rounded-xl px-4 py-3 text-[14px] text-white placeholder-[#333] outline-none focus:border-[#1DB95450] transition-colors font-display tracking-widest text-center text-xl uppercase" />
            </div>
            <Btn onClick={handleJoin} loading={joining} size="lg" className="w-full" variant="purple">
              🚪 Join Squad
            </Btn>
          </div>
        </Card>
      )}

      {/* How it works */}
      <Card>
        <SectionTitle>How Squad Mode Works</SectionTitle>
        <div className="space-y-3">
          {[
            { step: '1', text: 'Create a squad — get a 6-character code',                     color: '#1DB954' },
            { step: '2', text: 'Share the code with up to 3 friends',                         color: '#f59e0b' },
            { step: '3', text: 'Everyone joins with their own Spotify account',                color: '#a855f7' },
            { step: '4', text: 'Leaderboard, awards, and group roast generated automatically', color: '#f87171' },
          ].map(s => (
            <div key={s.step} className="flex items-start gap-3">
              <div className="w-7 h-7 rounded-full flex items-center justify-center text-[12px] font-bold text-black flex-shrink-0"
                style={{ background: s.color }}>
                {s.step}
              </div>
              <p className="text-[#888] text-[13px] pt-0.5">{s.text}</p>
            </div>
          ))}
        </div>
      </Card>

      {/* Awards preview */}
      <Card>
        <SectionTitle sub="Awards are auto-assigned based on everyone's Spotify data">🏆 Squad Awards</SectionTitle>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
          {[
            '👑 Music Overlord', '💀 Needs Therapy', '🤡 Spotify\'s Puppet',
            '🧅 Too Cool For This', '🔥 Hype Beast', '😴 Background Music',
            '🌍 World Citizen', '🔁 One-Trick Pony', '🎭 Most Chaotic',
          ].map(a => (
            <div key={a} className="bg-[#161616] border border-[#1e1e1e] rounded-xl p-2.5 text-[12px] font-medium text-center">
              {a}
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}
