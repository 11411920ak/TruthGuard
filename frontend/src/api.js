import axios from 'axios'

// All /api calls are proxied to Render backend via vercel.json rewrites
const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
})

// Analysis APIs

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

export async function getResult(id) {
  const response = await api.get('/results/' + id)
  return response.data
}

export async function getHistory(params = {}) {
  const response = await api.get('/history', { params })
  return response.data
}

export async function getHistoryStats() {
  const response = await api.get('/history/stats')
  return response.data
}

export async function getEvaluationMetrics() {
  const response = await api.get('/evaluation/metrics')
  return response.data
}

export async function runEvaluationBenchmark() {
  const response = await api.post('/evaluation/run')
  return response.data
}

export async function healthCheck() {
  const response = await api.get('/health')
  return response.data
}

export default api