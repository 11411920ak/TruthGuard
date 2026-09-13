import axios from 'axios'

const API_BASE = '/api'

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ── Analysis APIs ──

export async function analyzeText(content) {
  const response = await api.post('/analyze/text', { content })
  return response.data
}

export async function analyzeUrl(url) {
  const response = await api.post('/analyze/url', { url })
  return response.data
}

export async function analyzeImage(file) {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post('/analyze/image', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export async function analyzeVideo(file) {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post('/analyze/video', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

// ── Results & History APIs ──

export async function getResult(id) {
  const response = await api.get(`/results/${id}`)
  return response.data
}

export async function getHistory() {
  const response = await api.get('/history')
  return response.data
}

// ── Health check ──

export async function healthCheck() {
  const response = await api.get('/health')
  return response.data
}

export default api
