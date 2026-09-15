import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import CategoryCard from '../components/CategoryCard'

const categories = [
  { icon: '🌐', label: 'Website', description: 'Check if a website is safe' },
  { icon: '📰', label: 'News', description: 'Verify news claims' },
  { icon: '📱', label: 'Social Media', description: 'Check viral posts' },
  { icon: '🖼️', label: 'Screenshot', description: 'Analyze screenshots' },
  { icon: '🎥', label: 'Video', description: 'Verify video claims' },
  { icon: '🛒', label: 'Shopping', description: 'Detect shopping scams' },
  { icon: '🎓', label: 'Course / Job', description: 'Verify course & job offers' },
]

function Home() {
  const [input, setInput] = useState('')
  const [inputType, setInputType] = useState('text')
  const fileInputRef = useRef(null)
  const navigate = useNavigate()

  function detectInputType(value) {
    const trimmed = value.trim()
    if (/^https?:\/\//i.test(trimmed) || /^www\./i.test(trimmed)) {
      return 'url'
    }
    return 'text'
  }

  function handleInputChange(e) {
    const val = e.target.value
    setInput(val)
    setInputType(detectInputType(val))
  }

  function handleVerify() {
    if (!input.trim()) return
    // Navigate to analyze page with query params
    const params = new URLSearchParams({
      type: inputType,
      content: input.trim(),
    })
    navigate(`/analyze?${params.toString()}`)
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleVerify()
    }
  }

  function handleCategoryClick(category) {
    const placeholders = {
      'Website': 'https://example.com',
      'News': 'Paste a news article or headline here...',
      'Social Media': 'Paste the social media post content or URL...',
      'Screenshot': '',
      'Video': '',
      'Shopping': 'https://shop-example.com/product',
      'Course / Job': 'Paste the course/job offer details...',
    }
    if (category === 'Screenshot' || category === 'Video') {
      fileInputRef.current?.click()
      return
    }
    setInput(placeholders[category] || '')
    setInputType(category === 'Website' || category === 'Shopping' ? 'url' : 'text')
  }

  function handleFileUpload(e) {
    const file = e.target.files?.[0]
    if (!file) return
    const isVideo = file.type.startsWith('video/')
    const params = new URLSearchParams({
      type: isVideo ? 'video' : 'image',
      filename: file.name,
    })
    navigate(`/analyze?${params.toString()}`, {
      state: { file, type: isVideo ? 'video' : 'image' },
    })
  }

  return (
    <div>
      {/* Hero Section */}
      <section className="hero">
        <div className="container-sm">
          <h1 className="fade-in-up">
            <span className="gradient-text">TruthGuard</span>
          </h1>
          <p className="fade-in-up-delay-1">
            Verify Before You Trust — AI-powered content verification & scam detection
          </p>

          {/* Main Input */}
          <div className="fade-in-up-delay-2" style={{ marginBottom: '24px' }}>
            <textarea
              className="input-main"
              placeholder="Paste a URL, news article, claim, or social media post..."
              value={input}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              rows={4}
            />
          </div>

          {/* Input type indicator */}
          {input.trim() && (
            <div style={{ marginBottom: '16px', fontSize: '0.8rem', color: '#64748b' }}>
              Detected type: <span style={{ color: '#34d399', fontWeight: 600, textTransform: 'uppercase' }}>{inputType}</span>
            </div>
          )}

          {/* Action Buttons */}
          <div className="fade-in-up-delay-3" style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button
              className="btn-primary"
              onClick={handleVerify}
              disabled={!input.trim()}
              style={{ opacity: input.trim() ? 1 : 0.5 }}
            >
              🔍 Verify
            </button>
            <button className="btn-secondary" onClick={() => fileInputRef.current?.click()}>
              📸 Upload Screenshot
            </button>
            <button className="btn-secondary" onClick={() => fileInputRef.current?.click()}>
              🎥 Upload Video
            </button>
          </div>

          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileUpload}
            accept="image/*,video/*"
            style={{ display: 'none' }}
          />
        </div>
      </section>

      {/* Separator */}
      <div className="container-sm" style={{ textAlign: 'center', margin: '32px auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{ flex: 1, height: '1px', background: 'rgba(52,211,153,0.1)' }}></div>
          <span className="section-title" style={{ marginBottom: 0 }}>What do you want to verify?</span>
          <div style={{ flex: 1, height: '1px', background: 'rgba(52,211,153,0.1)' }}></div>
        </div>
      </div>

      {/* Category Cards */}
      <section className="container" style={{ paddingBottom: '80px' }}>
        <div
          className="category-grid"
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: '14px',
            maxWidth: '700px',
            margin: '0 auto',
          }}
        >
          {categories.map((cat) => (
            <CategoryCard
              key={cat.label}
              icon={cat.icon}
              label={cat.label}
              description={cat.description}
              onClick={() => handleCategoryClick(cat.label)}
            />
          ))}
        </div>
      </section>

      {/* Features Section */}
      <section className="container-sm" style={{ paddingBottom: '80px' }}>
        <div style={{ textAlign: 'center', marginBottom: '40px' }}>
          <h2 style={{ fontSize: '1.6rem', fontWeight: 700 }}>
            How <span className="gradient-text">TruthGuard</span> Works
          </h2>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px' }}>
          {[
            { icon: '🧠', title: 'Extract Claims', desc: 'AI breaks content into individual verifiable claims' },
            { icon: '🔍', title: 'Find Evidence', desc: 'Searches multiple independent sources for evidence' },
            { icon: '⚖️', title: 'Score & Verify', desc: 'Weighs source reliability and provides a confidence score' },
          ].map((feature) => (
            <div key={feature.title} className="glass-card" style={{ padding: '28px 20px', textAlign: 'center' }}>
              <div style={{ fontSize: '2rem', marginBottom: '12px' }}>{feature.icon}</div>
              <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '8px' }}>{feature.title}</h3>
              <p style={{ fontSize: '0.85rem', color: '#94a3b8', lineHeight: 1.5 }}>{feature.desc}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}

export default Home
