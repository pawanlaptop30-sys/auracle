import { useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'

export default function AuthSuccess() {
  const [params]    = useSearchParams()
  const { refetch } = useAuth()
  const navigate    = useNavigate()

  useEffect(() => {
    const token = params.get('token')
    const error = params.get('error')
    if (error) { toast.error(`Login failed: ${error}`); navigate('/', { replace: true }); return }
    if (token) {
      localStorage.setItem('auracle_token', token)
      refetch().then(() => navigate('/app/me', { replace: true }))
    } else {
      navigate('/', { replace: true })
    }
  }, [])

  return (
    <div className="min-h-screen flex items-center justify-center bg-[#080808]">
      <div className="flex flex-col items-center gap-4">
        <div className="w-12 h-12 border-2 border-[#1DB954] border-t-transparent rounded-full animate-spin" />
        <p className="font-display text-[#444] text-[14px]">Connecting your Spotify…</p>
      </div>
    </div>
  )
}
