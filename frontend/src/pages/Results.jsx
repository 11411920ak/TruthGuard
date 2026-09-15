import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import VerdictBadge from '../components/VerdictBadge'
import { getResult } from '../services/api'

function Results() {
  const { id } = useParams()
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function fetchResult() {
      try {
        const data = await getResult(id)
        setResult(data)
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to load results')
      } finally {
        setLoading(false)
      }
    }

    fetchResult()
  }, [id])

  if (loading) {
    return (
      <div className="page" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <div className="spinner"></div>
      </div>
    )
  }

  if (error || !result) {
    return (
      <div className="page">
        <div className="container-sm" style={{ textAlign: 'center' }}>
          <div className="glass-card" style={{ padding: '48px', maxWidth: '500px', margin: '0 auto' }}>
            <div style={{ fontSize: '3rem', marginBottom: '16px' }}>🔍</div>
            <h2 style={{ fontSize: '1.3rem', fontWeight: 600, marginBottom: '12px' }}>Result Not Found</h2>
            <p style={{ color: '#94a3b8', marginBottom: '24px' }}>{error || 'This analysis could not be found.'}</p>
            <Link to="/" className="btn-primary" style={{ textDecoration: 'none' }}>
              ← Back to Home
            </Link>
          </div>
        </div>
      </div>
    )
  }

  const verdictColor = {
    LIKELY_TRUE: '#34d399',
    LIKELY_FALSE: '#f87171',
    UNVERIFIED: '#fbbf24',
    SUSPICIOUS: '#fb923c',
  }[result.verdict] || '#fbbf24'

  const verdictClass = {
    LIKELY_TRUE: 'likely-true',
    LIKELY_FALSE: 'likely-false',
    UNVERIFIED: 'unverified',
    SUSPICIOUS: 'suspicious',
  }[result.verdict] || 'unverified'

  const verdictEmoji = {
    LIKELY_TRUE: '🟢',
    LIKELY_FALSE: '🔴',
    UNVERIFIED: '🟡',
    SUSPICIOUS: '🟠',
  }[result.verdict] || '🟡'

  return (
    <div className="page">
      <div className="container-sm">
        {/* Back link */}
        <Link to="/" style={{ color: '#64748b', textDecoration: 'none', fontSize: '0.85rem', display: 'inline-flex', alignItems: 'center', gap: '6px', marginBottom: '24px' }}>
          ← Back to Home
        </Link>

        {/* Verdict Header */}
        <div className={`result-header ${verdictClass} fade-in-up`}>
          <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '1.5px', fontWeight: 600 }}>
            Analysis Result
          </div>
          <div className="verdict-large" style={{ color: verdictColor }}>
            {verdictEmoji} {result.verdict.replace('_', ' ')}
          </div>

          {/* Stats */}
          <div className="stats-row">
            <div className="stat-card">
              <div className="stat-value" style={{ color: verdictColor }}>{result.confidence}%</div>
              <div className="stat-label">Confidence</div>
            </div>
            <div className="stat-card">
              <div className="stat-value" style={{ color: result.risk_score > 70 ? '#f87171' : result.risk_score > 40 ? '#fbbf24' : '#34d399' }}>
                {result.risk_score}/100
              </div>
              <div className="stat-label">Risk Score</div>
            </div>
            <div className="stat-card">
              <div className="stat-value" style={{ color: '#22d3ee' }}>{result.evidence_coverage}%</div>
              <div className="stat-label">Evidence Coverage</div>
            </div>
          </div>
        </div>

        {/* Input Content */}
        <div className="glass-card fade-in-up-delay-1" style={{ padding: '24px', marginBottom: '20px' }}>
          <div className="section-title">Analyzed Content</div>
          <p style={{ fontSize: '0.95rem', lineHeight: 1.6, color: '#cbd5e1' }}>
            {result.input_content}
          </p>
          <div style={{ marginTop: '8px', fontSize: '0.75rem', color: '#475569' }}>
            Type: {result.input_type.toUpperCase()} • Analyzed on {new Date(result.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
          </div>
        </div>

        {/* Website Security Breakdown (for URL inputs) */}
        {result.website_details && (
          <div className="glass-card fade-in-up-delay-1" style={{ padding: '24px', marginBottom: '20px', borderLeft: '4px solid #22d3ee' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
              <div>
                <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 600 }}>
                  🌐 Domain Security Profile
                </div>
                <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc', marginTop: '2px' }}>
                  {result.website_details.domain}
                </div>
              </div>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <span
                  style={{
                    padding: '4px 12px',
                    borderRadius: '20px',
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    background: result.website_details.https ? 'rgba(52, 211, 153, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                    color: result.website_details.https ? '#34d399' : '#f87171',
                    border: `1px solid ${result.website_details.https ? 'rgba(52, 211, 153, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
                  }}
                >
                  {result.website_details.https ? '🔒 HTTPS Secure' : '⚠️ Insecure (HTTP)'}
                </span>
                <span
                  style={{
                    padding: '4px 12px',
                    borderRadius: '20px',
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    background:
                      result.website_details.risk_level === 'LOW'
                        ? 'rgba(52, 211, 153, 0.15)'
                        : result.website_details.risk_level === 'MODERATE'
                        ? 'rgba(251, 191, 36, 0.15)'
                        : result.website_details.risk_level === 'HIGH'
                        ? 'rgba(251, 146, 60, 0.15)'
                        : 'rgba(239, 68, 68, 0.15)',
                    color:
                      result.website_details.risk_level === 'LOW'
                        ? '#34d399'
                        : result.website_details.risk_level === 'MODERATE'
                        ? '#fbbf24'
                        : result.website_details.risk_level === 'HIGH'
                        ? '#fb923c'
                        : '#f87171',
                  }}
                >
                  {result.website_details.risk_level} RISK
                </span>
              </div>
            </div>

            {/* Evaluated Security Signals */}
            {result.website_details.signals && result.website_details.signals.length > 0 && (
              <div>
                <div style={{ fontSize: '0.8rem', color: '#94a3b8', marginBottom: '8px', fontWeight: 500 }}>
                  Safety & Fraud Signals Detected:
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {result.website_details.signals.map((sig, idx) => {
                    const isPositive =
                      sig.includes('✓') ||
                      sig.toLowerCase().includes('active') ||
                      sig.toLowerCase().includes('verified') ||
                      sig.toLowerCase().includes('encryption') ||
                      sig.toLowerCase().includes('transparency pages found')
                    const isCritical =
                      sig.toLowerCase().includes('critical') ||
                      sig.toLowerCase().includes('violation') ||
                      sig.toLowerCase().includes('insecure') ||
                      sig.toLowerCase().includes('blocked')

                    return (
                      <span
                        key={idx}
                        style={{
                          display: 'inline-flex',
                          alignItems: 'center',
                          gap: '6px',
                          padding: '6px 12px',
                          borderRadius: '8px',
                          fontSize: '0.78rem',
                          background: isCritical
                            ? 'rgba(239, 68, 68, 0.12)'
                            : isPositive
                            ? 'rgba(52, 211, 153, 0.1)'
                            : 'rgba(251, 191, 36, 0.1)',
                          border: `1px solid ${
                            isCritical
                              ? 'rgba(239, 68, 68, 0.25)'
                              : isPositive
                              ? 'rgba(52, 211, 153, 0.2)'
                              : 'rgba(251, 191, 36, 0.2)'
                          }`,
                          color: isCritical ? '#fca5a5' : isPositive ? '#6ee7b7' : '#fde047',
                        }}
                      >
                        {isCritical ? '🛑' : isPositive ? '🛡️' : '⚠️'} {sig}
                      </span>
                    )
                  })}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Claims */}
        {result.claims && result.claims.length > 0 && (
          <div className="glass-card fade-in-up-delay-1" style={{ padding: '24px', marginBottom: '20px' }}>
            <div className="section-title">Extracted Claims</div>
            {result.claims.map((claim) => (
              <div key={claim.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0', borderBottom: '1px solid rgba(52,211,153,0.06)' }}>
                <div>
                  <p style={{ fontSize: '0.9rem', color: '#e2e8f0' }}>"{claim.claim_text}"</p>
                  <span style={{ fontSize: '0.75rem', color: '#475569' }}>{claim.claim_type}</span>
                </div>
                <VerdictBadge verdict={claim.verdict} />
              </div>
            ))}
          </div>
        )}

        {/* Reasons / Evidence */}
        {result.reasons && result.reasons.length > 0 && (
          <div className="glass-card fade-in-up-delay-2" style={{ padding: '24px', marginBottom: '20px' }}>
            <div className="section-title">Why This Verdict?</div>
            {result.reasons.map((reason, i) => (
              <div key={i} className="evidence-item">
                <span className="evidence-icon">
                  {reason.type === 'contradiction' ? '❌' : reason.type === 'support' ? '✅' : '⚠️'}
                </span>
                <span className="evidence-text">{reason.text}</span>
              </div>
            ))}
          </div>
        )}

        {/* Sources */}
        {result.sources && result.sources.length > 0 && (
          <div className="glass-card fade-in-up-delay-2" style={{ padding: '24px', marginBottom: '20px' }}>
            <div className="section-title">Sources ({result.sources.length})</div>
            {result.sources.map((source, i) => (
              <div key={i} className="source-item">
                <span className="source-badge" style={{
                  background: source.reliability >= 0.85 ? '#34d399' : source.reliability >= 0.6 ? '#fbbf24' : '#f87171'
                }}></span>
                <div>
                  <span className="source-name">{source.name}</span>
                  <div style={{ fontSize: '0.75rem', color: '#475569', textTransform: 'capitalize' }}>{source.type}</div>
                </div>
                <span className="source-reliability">
                  {Math.round(source.reliability * 100)}% reliable
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Recommendation */}
        {result.recommendation && (
          <div className="glass-card fade-in-up-delay-3" style={{ padding: '24px', marginBottom: '20px', borderColor: `${verdictColor}33` }}>
            <div className="section-title">Recommendation</div>
            <p style={{ fontSize: '0.95rem', lineHeight: 1.6, color: '#cbd5e1' }}>
              {result.recommendation}
            </p>
          </div>
        )}

        {/* Action buttons */}
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', marginTop: '32px' }}>
          <Link to="/" className="btn-primary" style={{ textDecoration: 'none' }}>
            🔍 New Analysis
          </Link>
          <Link to="/history" className="btn-secondary" style={{ textDecoration: 'none' }}>
            📋 View History
          </Link>
        </div>
      </div>
    </div>
  )
}

export default Results
