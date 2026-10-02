import { useEffect, useState } from 'react'
import { useSearchParams, useNavigate, useLocation } from 'react-router-dom'
import LoadingSpinner from '../components/LoadingSpinner'
import { analyzeText, analyzeUrl, analyzeImage, analyzeVideo } from '../services/api'

const steps = [
  { label: 'Receiving input', icon: '📥' },
  { label: 'Running OCR & inspection', icon: '📸' },
  { label: 'Extracting claims', icon: '🧠' },
  { label: 'Searching sources', icon: '🔍' },
  { label: 'Analyzing evidence', icon: '📊' },
  { label: 'Calculating score', icon: '⚖️' },
  { label: 'Preparing report', icon: '📋' },
]

function Analyze() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const location = useLocation()
  const [currentStep, setCurrentStep] = useState(0)
  const [error, setError] = useState(null)
  const [analysisStarted, setAnalysisStarted] = useState(false)

  const type = searchParams.get('type') || location.state?.type || 'text'
  const content = searchParams.get('content') || ''
  const filename = searchParams.get('filename') || location.state?.file?.name || ''

  useEffect(() => {
    if (analysisStarted) return

    setAnalysisStarted(true)

    // Animate steps while waiting for API
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev < steps.length - 1 ? prev + 1 : prev))
    }, 800)

    // Call the real API
    const doAnalysis = async () => {
      try {
        if (!content && !location.state?.file && !filename) {
          clearInterval(interval)
          setError('No content or media file was provided for verification.')
          return
        }

        let result
        if (type === 'image') {
          if (!location.state?.file) {
            clearInterval(interval)
            setError('No image file found. Please upload a screenshot or image from the home page.')
            return
          }
          result = await analyzeImage(location.state.file)
        } else if (type === 'video') {
          if (!location.state?.file) {
            clearInterval(interval)
            setError('No video file found. Please upload a video from the home page.')
            return
          }
          result = await analyzeVideo(location.state.file)
        } else if (type === 'url') {
          result = await analyzeUrl(content)
        } else {
          result = await analyzeText(content || filename)
        }

        clearInterval(interval)
        setCurrentStep(steps.length - 1)

        // Navigate to results after a short delay for polish
        setTimeout(() => {
          navigate(`/results/${result.id}`)
        }, 500)
      } catch (err) {
        clearInterval(interval)
        setError(err.response?.data?.detail || 'Analysis failed. Please try again.')
      }
    }

    doAnalysis()

    return () => clearInterval(interval)
  }, [type, content, navigate, analysisStarted])

  if (error) {
    return (
      <div className="page" style={{ backgroundColor: '#222831' }}>
        <div className="container-sm" style={{ textAlign: 'center' }}>
          <div className="glass-card" style={{ padding: '48px', maxWidth: '500px', margin: '0 auto', background: '#1F3A5F', border: '1px solid rgba(90, 169, 230, 0.25)' }}>
            <div style={{ fontSize: '3rem', marginBottom: '16px' }}>✕</div>
            <h2 style={{ fontSize: '1.3rem', fontWeight: 600, marginBottom: '12px', color: '#EAF4F4' }}>Analysis Failed</h2>
            <p style={{ color: 'rgba(234, 244, 244, 0.7)', marginBottom: '24px' }}>{error}</p>
            <button className="btn-primary" onClick={() => navigate('/')} style={{ background: '#5AA9E6', color: '#222831' }}>
              ← Try Again
            </button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="page" style={{ backgroundColor: '#222831' }}>
      <div className="container-sm" style={{ textAlign: 'center' }}>
        {/* Analysis info */}
        <div className="fade-in-up">
          <div className="glass-card" style={{ padding: '24px', marginBottom: '40px', display: 'inline-block', background: '#1F3A5F', border: '1px solid rgba(90, 169, 230, 0.25)' }}>
            <span style={{ fontSize: '0.75rem', color: '#5AA9E6', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 700 }}>
              Analyzing {type}
            </span>
            <p style={{
              marginTop: '8px',
              fontSize: '0.9rem',
              color: '#EAF4F4',
              maxWidth: '500px',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}>
              {content || 'Uploaded file'}
            </p>
          </div>
        </div>

        {/* Spinner */}
        <div className="fade-in-up-delay-1" style={{ marginBottom: '48px' }}>
          <LoadingSpinner message={steps[currentStep]?.label + '...'} />
        </div>

        {/* Step progress */}
        <div className="fade-in-up-delay-2" style={{ maxWidth: '400px', margin: '0 auto' }}>
          {steps.map((step, index) => (
            <div
              key={step.label}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '14px',
                padding: '12px 16px',
                borderRadius: '10px',
                marginBottom: '4px',
                background: index === currentStep
                  ? 'rgba(90, 169, 230, 0.15)'
                  : 'transparent',
                border: index === currentStep ? '1px solid rgba(90, 169, 230, 0.3)' : '1px solid transparent',
                opacity: index <= currentStep ? 1 : 0.4,
                transition: 'all 0.3s ease',
              }}
            >
              <span style={{ fontSize: '1.1rem', width: '28px', textAlign: 'center', color: '#5AA9E6' }}>
                {index < currentStep ? '✓' : step.icon}
              </span>
              <span style={{
                fontSize: '0.9rem',
                fontWeight: index === currentStep ? 700 : 500,
                color: index === currentStep ? '#5AA9E6' : '#EAF4F4',
              }}>
                {step.label}
              </span>
              {index === currentStep && (
                <div className="spinner" style={{ width: '16px', height: '16px', borderWidth: '2px', marginLeft: 'auto' }}></div>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Analyze
