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

const typeLabels = {
  text: 'Claim / Text',
  url: 'Website / URL',
  image: 'Screenshot / OCR',
  video: 'Video Clip',
  social: 'Social Post',
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

  return (
    <div className="page">
      <div className="container">
        {/* Header with Title & Export Actions */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px', marginBottom: '28px' }}>
          <div>
            <h1 style={{ fontSize: '2.2rem', fontWeight: 800, marginBottom: '6px' }}>
              Forensics <span className="gradient-text">Dashboard</span> & History
            </h1>
            <p style={{ color: '#94a3b8', fontSize: '0.95rem' }}>
              Real-time audit records, cross-modal scam intelligence, and historical verifications
            </p>
          </div>

          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
            <button
              onClick={handleExportCSV}
              disabled={history.length === 0}
              className="btn-secondary"
              style={{ padding: '8px 16px', fontSize: '0.85rem' }}
              title="Download verification records in CSV format"
            >
              📄 Export CSV
            </button>
            <button
              onClick={handleExportJSON}
              disabled={history.length === 0}
              className="btn-secondary"
              style={{ padding: '8px 16px', fontSize: '0.85rem' }}
              title="Download raw analysis data in JSON format"
            >
              📥 Export JSON
            </button>
          </div>
        </div>

        {/* Top KPI Metrics Bar */}
        {stats && (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '16px',
            marginBottom: '28px',
          }}>
            {/* KPI 1: Total Scans */}
            <div className="glass-card" style={{ padding: '20px' }}>
              <div style={{ fontSize: '0.75rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600, marginBottom: '4px' }}>
                Total Verified
              </div>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: '#f8fafc' }}>
                {stats.total_scans}
              </div>
              <div style={{ fontSize: '0.78rem', color: '#64748b', marginTop: '4px' }}>
                Across all modalities
              </div>
            </div>

            {/* KPI 2: Flagged Scams */}
            <div className="glass-card" style={{ padding: '20px', borderLeft: '3px solid #ef4444' }}>
              <div style={{ fontSize: '0.75rem', color: '#f87171', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600, marginBottom: '4px' }}>
                Scams & False Claims
              </div>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: '#f87171' }}>
                {stats.verdict_counts.LIKELY_FALSE || 0}
              </div>
              <div style={{ fontSize: '0.78rem', color: '#64748b', marginTop: '4px' }}>
                {verdictTotal ? Math.round(((stats.verdict_counts.LIKELY_FALSE || 0) / verdictTotal) * 100) : 0}% of all scans
              </div>
            </div>

            {/* KPI 3: Suspicious Flags */}
            <div className="glass-card" style={{ padding: '20px', borderLeft: '3px solid #f59e0b' }}>
              <div style={{ fontSize: '0.75rem', color: '#fbbf24', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600, marginBottom: '4px' }}>
                Suspicious Content
              </div>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: '#fbbf24' }}>
                {stats.verdict_counts.SUSPICIOUS || 0}
              </div>
              <div style={{ fontSize: '0.78rem', color: '#64748b', marginTop: '4px' }}>
                Phishing / high urgency
              </div>
            </div>

            {/* KPI 4: Verified Truthful */}
            <div className="glass-card" style={{ padding: '20px', borderLeft: '3px solid #10b981' }}>
              <div style={{ fontSize: '0.75rem', color: '#34d399', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600, marginBottom: '4px' }}>
                Verified Real Info
              </div>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: '#34d399' }}>
                {stats.verdict_counts.LIKELY_TRUE || 0}
              </div>
              <div style={{ fontSize: '0.78rem', color: '#64748b', marginTop: '4px' }}>
                Confirmed by sources
              </div>
            </div>

            {/* KPI 5: System Confidence */}
            <div className="glass-card" style={{ padding: '20px', borderLeft: '3px solid #8b5cf6' }}>
              <div style={{ fontSize: '0.75rem', color: '#c084fc', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600, marginBottom: '4px' }}>
                Avg Confidence
              </div>
              <div style={{ fontSize: '2rem', fontWeight: 800, color: '#c084fc' }}>
                {stats.avg_confidence}%
              </div>
              <div style={{ fontSize: '0.78rem', color: '#64748b', marginTop: '4px' }}>
                Evidence agreement
              </div>
            </div>
          </div>
        )}

        {/* Visual Analytics Widgets */}
        {stats && verdictTotal > 0 && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px', marginBottom: '28px' }}>
            {/* Verdict Distribution Card */}
            <div className="glass-card" style={{ padding: '20px' }}>
              <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#f8fafc', marginBottom: '14px', display: 'flex', justifyContent: 'space-between' }}>
                <span>Verdict Distribution</span>
                <span style={{ color: '#94a3b8', fontWeight: 500 }}>{verdictTotal} Total</span>
              </div>

              {/* Progress Bar */}
              <div style={{ display: 'flex', height: '12px', borderRadius: '6px', overflow: 'hidden', marginBottom: '16px', background: 'rgba(255,255,255,0.05)' }}>
                <div style={{ width: `${((stats.verdict_counts.LIKELY_FALSE || 0) / verdictTotal) * 100}%`, background: '#ef4444' }} title="Likely False" />
                <div style={{ width: `${((stats.verdict_counts.SUSPICIOUS || 0) / verdictTotal) * 100}%`, background: '#f59e0b' }} title="Suspicious" />
                <div style={{ width: `${((stats.verdict_counts.UNVERIFIED || 0) / verdictTotal) * 100}%`, background: '#a855f7' }} title="Unverified" />
                <div style={{ width: `${((stats.verdict_counts.LIKELY_TRUE || 0) / verdictTotal) * 100}%`, background: '#10b981' }} title="Likely True" />
              </div>

              {/* Legend Grid */}
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', fontSize: '0.78rem' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#f87171' }}>
                  <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#ef4444' }} />
                  <span>Likely False: <strong>{stats.verdict_counts.LIKELY_FALSE || 0}</strong></span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#fbbf24' }}>
                  <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#f59e0b' }} />
                  <span>Suspicious: <strong>{stats.verdict_counts.SUSPICIOUS || 0}</strong></span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#c084fc' }}>
                  <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#a855f7' }} />
                  <span>Unverified: <strong>{stats.verdict_counts.UNVERIFIED || 0}</strong></span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: '#34d399' }}>
                  <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981' }} />
                  <span>Likely True: <strong>{stats.verdict_counts.LIKELY_TRUE || 0}</strong></span>
                </div>
              </div>
            </div>

            {/* Modality Breakdown Card */}
            <div className="glass-card" style={{ padding: '20px' }}>
              <div style={{ fontSize: '0.85rem', fontWeight: 700, color: '#f8fafc', marginBottom: '14px' }}>
                Inspected Modalities
              </div>
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                {Object.entries(stats.type_counts || {}).map(([type, count]) => (
                  <div
                    key={type}
                    onClick={() => setSelectedType(type === selectedType ? 'all' : type)}
                    style={{
                      flex: 1,
                      minWidth: '80px',
                      background: selectedType === type ? 'rgba(56, 189, 248, 0.2)' : 'rgba(255, 255, 255, 0.04)',
                      border: `1px solid ${selectedType === type ? '#38bdf8' : 'rgba(255, 255, 255, 0.08)'}`,
                      borderRadius: '8px',
                      padding: '10px 8px',
                      textAlign: 'center',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                    }}
                  >
                    <div style={{ fontSize: '1.2rem' }}>{typeIcons[type] || '📄'}</div>
                    <div style={{ fontSize: '1.1rem', fontWeight: 700, color: '#f8fafc', margin: '2px 0' }}>{count}</div>
                    <div style={{ fontSize: '0.72rem', color: '#94a3b8', textTransform: 'capitalize' }}>{type}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Filter & Search Toolbar */}
        <div className="glass-card" style={{ padding: '16px', marginBottom: '20px' }}>
          <div style={{ display: 'flex', gap: '12px', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between' }}>
            {/* Search Input Form */}
            <form onSubmit={handleSearchSubmit} style={{ flex: '1 1 280px', display: 'flex', gap: '8px' }}>
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Search claims, domains, keywords..."
                style={{
                  flex: 1,
                  background: 'rgba(0, 0, 0, 0.3)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '8px',
                  padding: '8px 14px',
                  color: '#f8fafc',
                  fontSize: '0.85rem',
                  outline: 'none',
                }}
              />
              <button type="submit" className="btn-primary" style={{ padding: '8px 14px', fontSize: '0.85rem' }}>
                🔍 Search
              </button>
            </form>

            {/* Filters */}
            <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', alignItems: 'center' }}>
              {/* Verdict Filter */}
              <select
                value={selectedVerdict}
                onChange={(e) => setSelectedVerdict(e.target.value)}
                style={{
                  background: 'rgba(0, 0, 0, 0.4)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '8px',
                  padding: '8px 12px',
                  color: '#f8fafc',
                  fontSize: '0.82rem',
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
                  background: 'rgba(0, 0, 0, 0.4)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  borderRadius: '8px',
                  padding: '8px 12px',
                  color: '#f8fafc',
                  fontSize: '0.82rem',
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
                    color: '#94a3b8',
                    fontSize: '0.8rem',
                    cursor: 'pointer',
                    textDecoration: 'underline',
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
          <div className="glass-card" style={{ padding: '60px 24px', textAlign: 'center' }}>
            <div style={{ fontSize: '3rem', marginBottom: '16px' }}>📋</div>
            <h3 style={{ fontSize: '1.2rem', fontWeight: 600, marginBottom: '8px', color: '#f8fafc' }}>
              No matching records found
            </h3>
            <p style={{ color: '#64748b', marginBottom: '24px' }}>
              Try adjusting your search terms or filters, or start a new verification scan.
            </p>
            <Link to="/" className="btn-primary" style={{ textDecoration: 'none' }}>
              🔍 Start New Verification
            </Link>
          </div>
        ) : (
          <div className="glass-card" style={{ padding: '4px', overflow: 'auto' }}>
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
                    <td style={{ whiteSpace: 'nowrap', color: '#94a3b8', fontSize: '0.82rem' }}>
                      {new Date(item.created_at).toLocaleDateString('en-IN', {
                        day: 'numeric',
                        month: 'short',
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </td>
                    <td>
                      <span style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '6px',
                        background: 'rgba(255, 255, 255, 0.05)',
                        padding: '3px 8px',
                        borderRadius: '6px',
                        fontSize: '0.78rem',
                        color: '#cbd5e1',
                      }}>
                        <span>{typeIcons[item.input_type] || '📝'}</span>
                        <span style={{ textTransform: 'capitalize' }}>{item.input_type}</span>
                      </span>
                    </td>
                    <td style={{
                      maxWidth: '280px',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                      color: '#e2e8f0',
                      fontSize: '0.85rem',
                    }}>
                      {item.input_content}
                    </td>
                    <td>
                      <VerdictBadge verdict={item.verdict} />
                    </td>
                    <td>
                      <span style={{
                        display: 'inline-block',
                        padding: '2px 8px',
                        borderRadius: '12px',
                        fontSize: '0.75rem',
                        fontWeight: 600,
                        background:
                          item.risk_score >= 75
                            ? 'rgba(239, 68, 68, 0.15)'
                            : item.risk_score >= 50
                            ? 'rgba(245, 158, 11, 0.15)'
                            : 'rgba(52, 211, 153, 0.15)',
                        color:
                          item.risk_score >= 75
                            ? '#f87171'
                            : item.risk_score >= 50
                            ? '#fbbf24'
                            : '#34d399',
                        border: `1px solid ${
                          item.risk_score >= 75
                            ? 'rgba(239, 68, 68, 0.3)'
                            : item.risk_score >= 50
                            ? 'rgba(245, 158, 11, 0.3)'
                            : 'rgba(52, 211, 153, 0.3)'
                        }`,
                      }}>
                        {Math.round(item.risk_score)} / 100
                      </span>
                    </td>
                    <td style={{ textAlign: 'center', fontWeight: 600, color: '#94a3b8', fontSize: '0.85rem' }}>
                      {Math.round(item.confidence)}%
                    </td>
                    <td style={{ textAlign: 'right' }}>
                      <span style={{
                        fontSize: '0.78rem',
                        color: '#38bdf8',
                        fontWeight: 500,
                      }}>
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
