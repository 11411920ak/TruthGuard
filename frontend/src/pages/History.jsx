import { useState, useEffect, useMemo } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import VerdictBadge from '../components/VerdictBadge'
import { getHistory, getHistoryStats } from '../services/api'

const typeIcons = {
  text: '📝',
  url: '🌐',
  image: '📸',
  video: '🎥',
  social: '💬',
}


function History() {
  const [history, setHistory] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedType, setSelectedType] = useState('all')
  const [selectedVerdict, setSelectedVerdict] = useState('all')
  const navigate = useNavigate()

  async function loadData() {
    setLoading(true)
    try {
      const [historyData, statsData] = await Promise.all([
        getHistory({
          search: searchTerm || undefined,
          input_type: selectedType !== 'all' ? selectedType : undefined,
          verdict: selectedVerdict !== 'all' ? selectedVerdict : undefined,
        }),
        getHistoryStats(),
      ])
      setHistory(historyData.analyses || [])
      setStats(statsData)
    } catch (err) {
      console.error('Failed to fetch dashboard data:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadData()
  }, [selectedType, selectedVerdict])

  function handleSearchSubmit(e) {
    e.preventDefault()
    loadData()
  }

  // Export JSON
  function handleExportJSON() {
    const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(history, null, 2))
    const dlAnchor = document.createElement('a')
    dlAnchor.setAttribute('href', dataStr)
    dlAnchor.setAttribute('download', `truthguard_audit_log_${Date.now()}.json`)
    dlAnchor.click()
  }

  // Export CSV
  function handleExportCSV() {
    const headers = ['ID', 'Date', 'Type', 'Content', 'Verdict', 'Confidence', 'RiskScore']
    const rows = history.map((item) => [
      item.id,
      item.created_at,
      item.input_type,
      `"${(item.input_content || '').replace(/"/g, '""')}"`,
      item.verdict,
      item.confidence,
      item.risk_score,
    ])
    const csvContent = 'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((e) => e.join(','))].join('\n')
    const dlAnchor = document.createElement('a')
    dlAnchor.setAttribute('href', encodeURI(csvContent))
    dlAnchor.setAttribute('download', `truthguard_audit_log_${Date.now()}.csv`)
    dlAnchor.click()
  }

  const verdictTotal = useMemo(() => {
    if (!stats?.verdict_counts) return 0
    return Object.values(stats.verdict_counts).reduce((a, b) => a + b, 0)
  }, [stats])

  // Calculation for donut ring
  const trueRate = useMemo(() => {
    if (!verdictTotal || !stats?.verdict_counts?.LIKELY_TRUE) return 72
    return Math.round((stats.verdict_counts.LIKELY_TRUE / verdictTotal) * 100)
  }, [stats, verdictTotal])

  return (
    <div className="page" style={{ backgroundColor: '#222831' }}>
      <div className="container">
        {/* Welcome Banner & Quick Action */}
        <div
          className="glass-card fade-in-up"
          style={{
            padding: '28px 32px',
            marginBottom: '24px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            flexWrap: 'wrap',
            gap: '20px',
            background: '#1F3A5F',
            border: '1px solid rgba(90, 169, 230, 0.25)',
          }}
        >
          <div>
            <div
              style={{
                fontSize: '0.72rem',
                fontWeight: 700,
                color: '#5AA9E6',
                textTransform: 'uppercase',
                letterSpacing: '1.8px',
                marginBottom: '6px',
              }}
            >
              Welcome Back • System Forensics
            </div>
            <h1
              style={{
                fontSize: '2rem',
                fontWeight: 800,
                color: '#EAF4F4',
                marginBottom: '4px',
                lineHeight: 1.2,
              }}
            >
              Insights Drive Progress
            </h1>
            <p style={{ color: 'rgba(234, 244, 244, 0.7)', fontSize: '0.92rem' }}>
              Beautiful data. Brighter decisions. Real-time digital content intelligence.
            </p>
          </div>

          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
            <Link
              to="/"
              className="btn-primary"
              style={{
                textDecoration: 'none',
                background: '#5AA9E6',
                color: '#222831',
                padding: '10px 22px',
                fontWeight: 700,
                fontSize: '0.88rem',
              }}
            >
              Start Verification →
            </Link>
            <button
              onClick={handleExportCSV}
              disabled={history.length === 0}
              className="btn-secondary"
              style={{
                padding: '10px 18px',
                fontSize: '0.85rem',
                background: '#1F3A5F',
                border: '1px solid rgba(90, 169, 230, 0.35)',
                color: '#EAF4F4',
              }}
              title="Download verification records in CSV format"
            >
              📄 Export CSV
            </button>
            <button
              onClick={handleExportJSON}
              disabled={history.length === 0}
              className="btn-secondary"
              style={{
                padding: '10px 18px',
                fontSize: '0.85rem',
                background: '#1F3A5F',
                border: '1px solid rgba(90, 169, 230, 0.35)',
                color: '#EAF4F4',
              }}
              title="Download raw analysis data in JSON format"
            >
              📥 Export JSON
            </button>
          </div>
        </div>

        {/* 4 Stat KPI Cards strictly styled in #1F3A5F bg, #EAF4F4 text, #5AA9E6 trend indicators */}
        <div
          className="fade-in-up-delay-1"
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
            gap: '16px',
            marginBottom: '24px',
          }}
        >
          {/* Card 1: Total Verified */}
          <div
            className="glass-card"
            style={{
              padding: '22px 20px',
              background: '#1F3A5F',
              border: '1px solid rgba(90, 169, 230, 0.2)',
            }}
          >
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '10px',
              }}
            >
              <span
                style={{
                  fontSize: '0.75rem',
                  color: 'rgba(234, 244, 244, 0.65)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.6px',
                  fontWeight: 600,
                }}
              >
                Total Verified
              </span>
              <span style={{ fontSize: '1.2rem', color: '#5AA9E6' }}>🛡️</span>
            </div>
            <div
              style={{
                fontSize: '2.1rem',
                fontWeight: 800,
                color: '#EAF4F4',
                fontFamily: 'Outfit, sans-serif',
              }}
            >
              {stats ? stats.total_scans.toLocaleString() : '1,206'}
            </div>
            <div
              style={{
                fontSize: '0.78rem',
                color: '#5AA9E6',
                fontWeight: 600,
                marginTop: '6px',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}
            >
              <span>↑ +12%</span>
              <span style={{ color: 'rgba(234, 244, 244, 0.55)', fontWeight: 400 }}>vs last month</span>
            </div>
          </div>

          {/* Card 2: Scams & Flagged */}
          <div
            className="glass-card"
            style={{
              padding: '22px 20px',
              background: '#1F3A5F',
              border: '1px solid rgba(90, 169, 230, 0.2)',
            }}
          >
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '10px',
              }}
            >
              <span
                style={{
                  fontSize: '0.75rem',
                  color: 'rgba(234, 244, 244, 0.65)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.6px',
                  fontWeight: 600,
                }}
              >
                Flagged Scams
              </span>
              <span style={{ fontSize: '1.2rem', color: '#5AA9E6' }}>⚠️</span>
            </div>
            <div
              style={{
                fontSize: '2.1rem',
                fontWeight: 800,
                color: '#EAF4F4',
                fontFamily: 'Outfit, sans-serif',
              }}
            >
              {stats ? (stats.verdict_counts.LIKELY_FALSE || 0).toLocaleString() : '342'}
            </div>
            <div
              style={{
                fontSize: '0.78rem',
                color: '#5AA9E6',
                fontWeight: 600,
                marginTop: '6px',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}
            >
              <span>↑ +15%</span>
              <span style={{ color: 'rgba(234, 244, 244, 0.55)', fontWeight: 400 }}>threat detection</span>
            </div>
          </div>

          {/* Card 3: Avg Confidence */}
          <div
            className="glass-card"
            style={{
              padding: '22px 20px',
              background: '#1F3A5F',
              border: '1px solid rgba(90, 169, 230, 0.2)',
            }}
          >
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '10px',
              }}
            >
              <span
                style={{
                  fontSize: '0.75rem',
                  color: 'rgba(234, 244, 244, 0.65)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.6px',
                  fontWeight: 600,
                }}
              >
                Avg Confidence
              </span>
              <span style={{ fontSize: '1.2rem', color: '#5AA9E6' }}>📊</span>
            </div>
            <div
              style={{
                fontSize: '2.1rem',
                fontWeight: 800,
                color: '#EAF4F4',
                fontFamily: 'Outfit, sans-serif',
              }}
            >
              {stats ? `${stats.avg_confidence}%` : '89.4%'}
            </div>
            <div
              style={{
                fontSize: '0.78rem',
                color: '#5AA9E6',
                fontWeight: 600,
                marginTop: '6px',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}
            >
              <span>↑ +0.6%</span>
              <span style={{ color: 'rgba(234, 244, 244, 0.55)', fontWeight: 400 }}>model alignment</span>
            </div>
          </div>

          {/* Card 4: Verified Truthful */}
          <div
            className="glass-card"
            style={{
              padding: '22px 20px',
              background: '#1F3A5F',
              border: '1px solid rgba(90, 169, 230, 0.2)',
            }}
          >
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '10px',
              }}
            >
              <span
                style={{
                  fontSize: '0.75rem',
                  color: 'rgba(234, 244, 244, 0.65)',
                  textTransform: 'uppercase',
                  letterSpacing: '0.6px',
                  fontWeight: 600,
                }}
              >
                Confirmed Real Info
              </span>
              <span style={{ fontSize: '1.2rem', color: '#5AA9E6' }}>✅</span>
            </div>
            <div
              style={{
                fontSize: '2.1rem',
                fontWeight: 800,
                color: '#EAF4F4',
                fontFamily: 'Outfit, sans-serif',
              }}
            >
              {stats ? (stats.verdict_counts.LIKELY_TRUE || 0).toLocaleString() : '864'}
            </div>
            <div
              style={{
                fontSize: '0.78rem',
                color: '#5AA9E6',
                fontWeight: 600,
                marginTop: '6px',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}
            >
              <span>↑ +14%</span>
              <span style={{ color: 'rgba(234, 244, 244, 0.55)', fontWeight: 400 }}>verified claims</span>
            </div>
          </div>
        </div>

        {/* Minimal Charts Row (Area Line Chart in #5AA9E6 fading to #1F3A5F & Donut Chart) */}
        <div
          className="fade-in-up-delay-2"
          style={{
            display: 'grid',
            gridTemplateColumns: '2fr 1fr',
            gap: '16px',
            marginBottom: '24px',
          }}
        >
          {/* Chart 1: Verification Activity Overview */}
          <div
            className="glass-card"
            style={{
              padding: '24px',
              background: '#1F3A5F',
              border: '1px solid rgba(90, 169, 230, 0.25)',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
            }}
          >
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                marginBottom: '16px',
              }}
            >
              <div>
                <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#EAF4F4' }}>
                  Verification Overview
                </h3>
                <p style={{ fontSize: '0.78rem', color: 'rgba(234, 244, 244, 0.65)' }}>
                  Monthly audit volume and pattern detection
                </p>
              </div>

              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  background: 'rgba(34, 40, 49, 0.6)',
                  padding: '4px 10px',
                  borderRadius: '8px',
                  border: '1px solid rgba(90, 169, 230, 0.2)',
                  fontSize: '0.78rem',
                  color: '#EAF4F4',
                }}
              >
                <span>This Year</span>
                <span style={{ color: '#5AA9E6', fontSize: '0.7rem' }}>▼</span>
              </div>
            </div>

            {/* SVG Area Line Chart */}
            <div style={{ width: '100%', height: '200px', position: 'relative' }}>
              <svg viewBox="0 0 500 180" style={{ width: '100%', height: '100%', overflow: 'visible' }}>
                <defs>
                  <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#5AA9E6" stopOpacity="0.45" />
                    <stop offset="100%" stopColor="#1F3A5F" stopOpacity="0.0" />
                  </linearGradient>
                </defs>

                {/* Grid Lines */}
                <line x1="0" y1="30" x2="500" y2="30" stroke="rgba(90, 169, 230, 0.1)" strokeDasharray="3 3" />
                <line x1="0" y1="80" x2="500" y2="80" stroke="rgba(90, 169, 230, 0.1)" strokeDasharray="3 3" />
                <line x1="0" y1="130" x2="500" y2="130" stroke="rgba(90, 169, 230, 0.1)" strokeDasharray="3 3" />

                {/* Y-Axis Value Labels */}
                <text x="5" y="34" fill="rgba(234, 244, 244, 0.4)" fontSize="9" fontFamily="Inter">60K</text>
                <text x="5" y="84" fill="rgba(234, 244, 244, 0.4)" fontSize="9" fontFamily="Inter">40K</text>
                <text x="5" y="134" fill="rgba(234, 244, 244, 0.4)" fontSize="9" fontFamily="Inter">20K</text>

                {/* Area Gradient Fill */}
                <path
                  d="M 30 140 Q 90 150, 130 110 T 210 120 T 290 85 T 370 70 T 430 45 T 490 80 L 490 160 L 30 160 Z"
                  fill="url(#areaGradient)"
                />

                {/* Main Curve Line in #5AA9E6 */}
                <path
                  d="M 30 140 Q 90 150, 130 110 T 210 120 T 290 85 T 370 70 T 430 45 T 490 80"
                  fill="none"
                  stroke="#5AA9E6"
                  strokeWidth="3"
                  strokeLinecap="round"
                />

                {/* Peak Highlight Dot & Callout */}
                <circle cx="430" cy="45" r="5" fill="#5AA9E6" stroke="#EAF4F4" strokeWidth="2" />
                <rect x="395" y="15" width="70" height="22" rx="6" fill="#1F3A5F" stroke="#5AA9E6" strokeWidth="1" />
                <text x="430" y="30" fill="#EAF4F4" fontSize="10" fontWeight="700" textAnchor="middle" fontFamily="Inter">
                  {stats ? `${stats.total_scans} Scans` : '$42,560'}
                </text>

                {/* X-Axis Month Labels */}
                <text x="30" y="175" fill="rgba(234, 244, 244, 0.55)" fontSize="10" fontFamily="Inter">Jan</text>
                <text x="105" y="175" fill="rgba(234, 244, 244, 0.55)" fontSize="10" fontFamily="Inter">Feb</text>
                <text x="180" y="175" fill="rgba(234, 244, 244, 0.55)" fontSize="10" fontFamily="Inter">Mar</text>
                <text x="255" y="175" fill="rgba(234, 244, 244, 0.55)" fontSize="10" fontFamily="Inter">Apr</text>
                <text x="330" y="175" fill="rgba(234, 244, 244, 0.55)" fontSize="10" fontFamily="Inter">May</text>
                <text x="405" y="175" fill="rgba(234, 244, 244, 0.55)" fontSize="10" fontFamily="Inter">Jun</text>
                <text x="480" y="175" fill="rgba(234, 244, 244, 0.55)" fontSize="10" fontFamily="Inter">Jul</text>
              </svg>
            </div>
          </div>

          {/* Chart 2: Modality & Traffic Sources */}
          <div
            className="glass-card"
            style={{
              padding: '24px',
              background: '#1F3A5F',
              border: '1px solid rgba(90, 169, 230, 0.25)',
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
            }}
          >
            <div>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: '#EAF4F4', marginBottom: '4px' }}>
                Traffic Sources
              </h3>
              <p style={{ fontSize: '0.78rem', color: 'rgba(234, 244, 244, 0.65)' }}>
                Modality distribution breakdown
              </p>
            </div>

            {/* Circular Donut Ring */}
            <div style={{ position: 'relative', width: '130px', height: '130px', margin: '14px auto' }}>
              <svg viewBox="0 0 100 100" style={{ width: '100%', height: '100%', transform: 'rotate(-90deg)' }}>
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  fill="transparent"
                  stroke="#222831"
                  strokeWidth="10"
                />
                <circle
                  cx="50"
                  cy="50"
                  r="40"
                  fill="transparent"
                  stroke="#5AA9E6"
                  strokeWidth="10"
                  strokeDasharray="251.2"
                  strokeDashoffset={251.2 - (251.2 * trueRate) / 100}
                  strokeLinecap="round"
                />
              </svg>
              <div
                style={{
                  position: 'absolute',
                  inset: 0,
                  display: 'flex',
                  flexDirection: 'column',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <span style={{ fontSize: '1.4rem', fontWeight: 800, color: '#EAF4F4', fontFamily: 'Outfit' }}>
                  {trueRate}%
                </span>
                <span style={{ fontSize: '0.65rem', color: 'rgba(234, 244, 244, 0.65)', textTransform: 'uppercase' }}>
                  Real Info
                </span>
              </div>
            </div>

            {/* Source breakdown legend */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '0.78rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: '#EAF4F4' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#5AA9E6' }} />
                  <span>Websites / URLs</span>
                </span>
                <span style={{ color: 'rgba(234, 244, 244, 0.7)' }}>52%</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: '#EAF4F4' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'rgba(90, 169, 230, 0.6)' }} />
                  <span>Text Claims</span>
                </span>
                <span style={{ color: 'rgba(234, 244, 244, 0.7)' }}>26%</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', color: '#EAF4F4' }}>
                <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'rgba(234, 244, 244, 0.4)' }} />
                  <span>Media / Social</span>
                </span>
                <span style={{ color: 'rgba(234, 244, 244, 0.7)' }}>22%</span>
              </div>
            </div>
          </div>
        </div>

        {/* Filter & Search Toolbar */}
        <div
          className="glass-card fade-in-up-delay-2"
          style={{
            padding: '18px 20px',
            marginBottom: '20px',
            background: '#1F3A5F',
            border: '1px solid rgba(90, 169, 230, 0.2)',
          }}
        >
          <div
            style={{
              display: 'flex',
              gap: '12px',
              flexWrap: 'wrap',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}
          >
            {/* Search Input Form */}
            <form onSubmit={handleSearchSubmit} style={{ flex: '1 1 300px', display: 'flex', gap: '8px' }}>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search claims, domains, keywords..."
                style={{
                  flex: 1,
                  background: '#222831',
                  border: '1px solid rgba(90, 169, 230, 0.25)',
                  borderRadius: '10px',
                  padding: '9px 16px',
                  color: '#EAF4F4',
                  fontSize: '0.88rem',
                  outline: 'none',
                }}
              />
              <button
                type="submit"
                className="btn-primary"
                style={{
                  padding: '9px 18px',
                  fontSize: '0.85rem',
                  background: '#5AA9E6',
                  color: '#222831',
                }}
              >
                🔍 Search
              </button>
            </form>

            {/* Filters */}
            <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', alignItems: 'center' }}>
              {/* Verdict Filter */}
              <select
                value={selectedVerdict}
                onChange={(e) => setSelectedVerdict(e.target.value)}
                style={{
                  background: '#222831',
                  border: '1px solid rgba(90, 169, 230, 0.25)',
                  borderRadius: '10px',
                  padding: '9px 14px',
                  color: '#EAF4F4',
                  fontSize: '0.85rem',
                  outline: 'none',
                  cursor: 'pointer',
                }}
              >
                <option value="all">All Verdicts</option>
                <option value="LIKELY_FALSE">Likely False</option>
                <option value="SUSPICIOUS">Suspicious</option>
                <option value="UNVERIFIED">Unverified</option>
                <option value="LIKELY_TRUE">Likely True</option>
              </select>

              {/* Modality Filter */}
              <select
                value={selectedType}
                onChange={(e) => setSelectedType(e.target.value)}
                style={{
                  background: '#222831',
                  border: '1px solid rgba(90, 169, 230, 0.25)',
                  borderRadius: '10px',
                  padding: '9px 14px',
                  color: '#EAF4F4',
                  fontSize: '0.85rem',
                  outline: 'none',
                  cursor: 'pointer',
                }}
              >
                <option value="all">All Modalities</option>
                <option value="text">📝 Text Claims</option>
                <option value="url">🌐 Websites / URLs</option>
                <option value="image">📸 Screenshots / OCR</option>
                <option value="video">🎥 Videos</option>
                <option value="social">💬 Social Posts</option>
              </select>

              {(searchTerm || selectedType !== 'all' || selectedVerdict !== 'all') && (
                <button
                  onClick={() => {
                    setSearchTerm('')
                    setSelectedType('all')
                    setSelectedVerdict('all')
                  }}
                  style={{
                    background: 'transparent',
                    border: 'none',
                    color: '#5AA9E6',
                    fontSize: '0.85rem',
                    cursor: 'pointer',
                    textDecoration: 'underline',
                    padding: '0 4px',
                  }}
                >
                  Reset
                </button>
              )}
            </div>
          </div>
        </div>

        {/* History Table View */}
        {loading ? (
          <div style={{ display: 'flex', justifyContent: 'center', padding: '60px' }}>
            <div className="spinner"></div>
          </div>
        ) : history.length === 0 ? (
          <div
            className="glass-card"
            style={{
              padding: '60px 24px',
              textAlign: 'center',
              background: '#1F3A5F',
              border: '1px solid rgba(90, 169, 230, 0.2)',
            }}
          >
            <div style={{ fontSize: '3rem', marginBottom: '16px' }}>📋</div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '8px', color: '#EAF4F4' }}>
              No matching records found
            </h3>
            <p style={{ color: 'rgba(234, 244, 244, 0.65)', marginBottom: '24px' }}>
              Try adjusting your search terms or filters, or start a new verification scan.
            </p>
            <Link
              to="/"
              className="btn-primary"
              style={{
                textDecoration: 'none',
                background: '#5AA9E6',
                color: '#222831',
              }}
            >
              🔍 Start New Verification
            </Link>
          </div>
        ) : (
          <div
            className="glass-card"
            style={{
              padding: '8px',
              overflow: 'auto',
              background: '#1F3A5F',
              border: '1px solid rgba(90, 169, 230, 0.2)',
            }}
          >
            <table className="history-table">
              <thead>
                <tr>
                  <th>Timestamp</th>
                  <th>Modality</th>
                  <th>Inspected Content</th>
                  <th>Verdict</th>
                  <th>Risk Score</th>
                  <th>Confidence</th>
                  <th style={{ textAlign: 'right' }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {history.map((item) => (
                  <tr key={item.id} onClick={() => navigate(`/results/${item.id}`)} style={{ cursor: 'pointer' }}>
                    <td style={{ whiteSpace: 'nowrap', color: 'rgba(234, 244, 244, 0.7)', fontSize: '0.82rem' }}>
                      {new Date(item.created_at).toLocaleDateString('en-IN', {
                        day: 'numeric',
                        month: 'short',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </td>
                    <td>
                      <span
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '6px',
                          background: '#222831',
                          border: '1px solid rgba(90, 169, 230, 0.15)',
                          padding: '4px 10px',
                          borderRadius: '8px',
                          fontSize: '0.78rem',
                          color: '#EAF4F4',
                        }}
                      >
                        <span>{typeIcons[item.input_type] || '📝'}</span>
                        <span style={{ textTransform: 'capitalize' }}>{item.input_type}</span>
                      </span>
                    </td>
                    <td
                      style={{
                        maxWidth: '280px',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        whiteSpace: 'nowrap',
                        color: '#EAF4F4',
                        fontSize: '0.86rem',
                        fontWeight: 500,
                      }}
                    >
                      {item.input_content}
                    </td>
                    <td>
                      <VerdictBadge verdict={item.verdict} />
                    </td>
                    <td>
                      <span
                        style={{
                          display: 'inline-block',
                          padding: '3px 10px',
                          borderRadius: '12px',
                          fontSize: '0.75rem',
                          fontWeight: 700,
                          background: item.risk_score >= 60 ? 'rgba(234, 244, 244, 0.1)' : 'rgba(90, 169, 230, 0.15)',
                          color: item.risk_score >= 60 ? '#EAF4F4' : '#5AA9E6',
                          border: `1px solid ${item.risk_score >= 60 ? 'rgba(234, 244, 244, 0.4)' : '#5AA9E6'}`,
                        }}
                      >
                        {Math.round(item.risk_score)} / 100
                      </span>
                    </td>
                    <td style={{ textAlign: 'center', fontWeight: 600, color: '#EAF4F4', fontSize: '0.85rem' }}>
                      {Math.round(item.confidence)}%
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <span
                        style={{
                          fontSize: '0.82rem',
                          color: '#5AA9E6',
                          fontWeight: 600,
                        }}
                      >
                        Inspect ↗
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}

export default History
