import { motion } from 'framer-motion'

// ── Card ─────────────────────────────────────────────────────────────────────
export function Card({ children, className = '', glow = false }) {
  return (
    <div className={`bg-[#0f0f0f] border border-[#252525] rounded-2xl p-5 ${glow ? 'shadow-[0_0_30px_#1DB95425]' : ''} ${className}`}>
      {children}
    </div>
  )
}

// ── Skeleton ──────────────────────────────────────────────────────────────────
export function Skeleton({ h = 'h-4', w = 'w-full', className = '' }) {
  return <div className={`skeleton ${h} ${w} ${className}`} />
}

// ── Button ────────────────────────────────────────────────────────────────────
export function Btn({ children, onClick, variant = 'green', size = 'md', className = '', disabled = false, loading = false }) {
  const sizes = { sm: 'px-3 py-1.5 text-[12px]', md: 'px-5 py-2.5 text-[13px]', lg: 'px-7 py-3.5 text-[15px]' }
  const variants = {
    green:  'bg-[#1DB954] hover:bg-[#17a349] text-black font-bold',
    fire:   'bg-[#ff4d00] hover:bg-[#e64500] text-white font-bold',
    ghost:  'bg-[#161616] hover:bg-[#1e1e1e] text-white border border-[#252525]',
    outline:'bg-transparent border border-[#333] text-white hover:bg-[#161616]',
    purple: 'bg-[#a855f7] hover:bg-[#9333ea] text-white font-bold',
  }
  return (
    <motion.button
      whileTap={{ scale: 0.97 }}
      onClick={onClick}
      disabled={disabled || loading}
      className={`inline-flex items-center justify-center gap-2 rounded-xl transition-all select-none
        ${sizes[size]} ${variants[variant] || variants.green}
        ${disabled || loading ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer'}
        ${className}`}
    >
      {loading ? <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" /> : children}
    </motion.button>
  )
}

// ── Badge ─────────────────────────────────────────────────────────────────────
export function Badge({ children, color = 'green' }) {
  const colors = {
    green:  'bg-[#1DB95420] text-[#1DB954] border-[#1DB95440]',
    fire:   'bg-[#ff4d0020] text-[#ff4d00] border-[#ff4d0040]',
    purple: 'bg-[#a855f720] text-[#a855f7] border-[#a855f740]',
    amber:  'bg-[#f59e0b20] text-[#f59e0b] border-[#f59e0b40]',
    coral:  'bg-[#f8717120] text-[#f87171] border-[#f8717140]',
    gray:   'bg-[#25252520] text-[#888] border-[#333]',
  }
  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${colors[color] || colors.gray}`}>
      {children}
    </span>
  )
}

// ── Error ─────────────────────────────────────────────────────────────────────
export function ErrorMsg({ message }) {
  return (
    <div className="flex flex-col items-center py-10 text-center">
      <div className="text-3xl mb-2">😬</div>
      <p className="text-[#f87171] text-[13px]">{message || 'Something went wrong'}</p>
    </div>
  )
}

// ── Avatar ─────────────────────────────────────────────────────────────────────
export function Avatar({ src, name, size = 'md', color = '#1DB954' }) {
  const sizes = { sm: 'w-8 h-8 text-sm', md: 'w-12 h-12 text-lg', lg: 'w-16 h-16 text-2xl', xl: 'w-24 h-24 text-4xl' }
  if (src) return <img src={src} className={`${sizes[size]} rounded-full object-cover ring-2 ring-[#252525] flex-shrink-0`} alt={name} />
  return (
    <div className={`${sizes[size]} rounded-full flex items-center justify-center font-bold text-black flex-shrink-0`}
      style={{ background: `linear-gradient(135deg, ${color}, ${color}80)` }}>
      {name?.[0]?.toUpperCase() || '?'}
    </div>
  )
}

// ── Track row ─────────────────────────────────────────────────────────────────
export function TrackRow({ track, rank }) {
  return (
    <div className="flex items-center gap-3 py-2 px-2 rounded-xl hover:bg-[#161616] transition-all cursor-default group">
      <span className="font-display text-[12px] text-[#444] w-5 text-center flex-shrink-0">{rank}</span>
      {track.album_art
        ? <img src={track.album_art} className="w-10 h-10 rounded-lg object-cover flex-shrink-0" alt="" />
        : <div className="w-10 h-10 rounded-lg bg-[#1e1e1e] flex items-center justify-center text-lg flex-shrink-0">🎵</div>
      }
      <div className="flex-1 min-w-0">
        <div className="text-[13px] font-medium truncate group-hover:text-[#1DB954] transition-colors">{track.name}</div>
        <div className="text-[11px] text-[#555] truncate">{Array.isArray(track.artists) ? track.artists.join(', ') : track.artists}</div>
      </div>
      {track.popularity != null && (
        <div className="w-12 h-1.5 bg-[#1e1e1e] rounded-full overflow-hidden flex-shrink-0">
          <div className="h-full bg-[#1DB954] rounded-full" style={{ width: `${track.popularity}%` }} />
        </div>
      )}
    </div>
  )
}

// ── Artist row ────────────────────────────────────────────────────────────────
export function ArtistRow({ artist, rank }) {
  return (
    <div className="flex items-center gap-3 py-2 px-2 rounded-xl hover:bg-[#161616] transition-all cursor-default group">
      {rank && <span className="font-display text-[12px] text-[#444] w-5 text-center flex-shrink-0">{rank}</span>}
      {artist.image
        ? <img src={artist.image} className="w-10 h-10 rounded-full object-cover flex-shrink-0" alt="" />
        : <div className="w-10 h-10 rounded-full bg-[#1e1e1e] flex items-center justify-center text-lg flex-shrink-0">🎤</div>
      }
      <div className="flex-1 min-w-0">
        <div className="text-[13px] font-medium truncate group-hover:text-[#1DB954] transition-colors">{artist.name}</div>
        <div className="text-[11px] text-[#555] truncate">{(artist.genres || []).slice(0, 2).join(' · ') || 'Artist'}</div>
      </div>
    </div>
  )
}

// ── Score ring ────────────────────────────────────────────────────────────────
export function ScoreRing({ score, size = 80, color = '#1DB954', label = '' }) {
  const r   = (size / 2) - 6
  const c   = 2 * Math.PI * r
  const off = c - (score / 100) * c
  return (
    <div className="flex flex-col items-center gap-1">
      <svg width={size} height={size} className="-rotate-90">
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke="#1e1e1e" strokeWidth="5" />
        <circle cx={size/2} cy={size/2} r={r} fill="none" stroke={color} strokeWidth="5"
          strokeDasharray={c} strokeDashoffset={off} strokeLinecap="round"
          style={{ transition: 'stroke-dashoffset 0.8s ease' }} />
      </svg>
      <div className="font-display font-bold text-lg" style={{ color }}>{score.toFixed(0)}</div>
      {label && <div className="text-[10px] text-[#555] uppercase tracking-wider">{label}</div>}
    </div>
  )
}

// ── Personality pill ──────────────────────────────────────────────────────────
export function PersonalityPill({ type }) {
  return (
    <span className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-[#161616] border border-[#252525] text-[13px] font-semibold">
      {type}
    </span>
  )
}

// ── Section title ─────────────────────────────────────────────────────────────
export function SectionTitle({ children, sub }) {
  return (
    <div className="mb-4">
      <h2 className="font-display font-bold text-[16px]">{children}</h2>
      {sub && <p className="text-[#555] text-[12px] mt-0.5">{sub}</p>}
    </div>
  )
}

// ── Divider ───────────────────────────────────────────────────────────────────
export function Divider({ label }) {
  return (
    <div className="flex items-center gap-3 my-4">
      <div className="flex-1 h-px bg-[#252525]" />
      {label && <span className="text-[11px] text-[#444] uppercase tracking-wider">{label}</span>}
      <div className="flex-1 h-px bg-[#252525]" />
    </div>
  )
}
