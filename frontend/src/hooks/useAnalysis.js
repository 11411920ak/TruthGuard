import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { analyzeText, analyzeUrl } from '../services/api'

function useAnalysis() {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  async function submitAnalysis(type, content) {
    setLoading(true)
    setError(null)

    try {
      let result

      if (type === 'url') {
        result = await analyzeUrl(content)
      } else {
        result = await analyzeText(content)
      }

      if (result.id) {
        navigate(`/results/${result.id}`)
      }

      return result
    } catch (err) {
      const message = err.response?.data?.detail || 'Analysis failed. Please try again.'
      setError(message)
      throw err
    } finally {
      setLoading(false)
    }
  }

  return { submitAnalysis, loading, error }
}

export default useAnalysis
