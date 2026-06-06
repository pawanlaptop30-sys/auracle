import axios from 'axios'

const BASE = import.meta.env.VITE_API_URL ?? '/api'

const api = axios.create({ baseURL: BASE, timeout: 30000 })

api.interceptors.request.use((c) => {
  const t = localStorage.getItem('auracle_token')
  if (t) c.headers.Authorization = `Bearer ${t}`
  return c
})

api.interceptors.response.use(
  (r) => r,
  (e) => {
    if (e.response?.status === 401) {
      localStorage.removeItem('auracle_token')
      window.location.href = '/'
    }
    return Promise.reject(e)
  }
)

export default api

export const authApi = {
  loginUrl: () => `${BASE}/auth/login`,
  me:       () => api.get('/auth/me'),
  logout:   () => api.delete('/auth/logout'),
}

export const profileApi = {
  me:        (term = 'short_term') => api.get(`/profile/me?term=${term}`),
  horoscope: (term = 'short_term') => api.get(`/profile/me/horoscope?term=${term}`),
  public:    (slug)                 => api.get(`/profile/${slug}`),
}

export const roastApi = {
  me:       (severity = 'roasted', term = 'short_term') => api.get(`/roast/me?severity=${severity}&term=${term}`),
  category: (category, term = 'short_term')             => api.get(`/roast/category?category=${category}&term=${term}`),
  alibi:    (term = 'short_term')                       => api.get(`/roast/alibi?term=${term}`),
}

export const battleApi = {
  create: (targetSlug, term = 'short_term') => api.post(`/battle/create?target_slug=${targetSlug}&term=${term}`),
  get:    (slug)                             => api.get(`/battle/${slug}`),
}

export const squadApi = {
  create: (name)  => api.post('/squad/create', { name }),
  join:   (code)  => api.post(`/squad/join/${code}`),
  get:    (code)  => api.get(`/squad/${code}`),
  refreshRoast: (code) => api.post(`/squad/${code}/refresh-roast`),
}
