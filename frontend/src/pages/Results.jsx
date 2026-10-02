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
      <div className="page" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', backgroundColor: '#222831' }}>
        <div className="spinner"></div>
      </div>
    )
  }

  if (error || !result) {
    return (
      <div className="page" style={{ backgroundColor: '#222831' }}>
        <div className="container-sm" style={{ textAlign: 'center' }}>
          <div className="glass-card" style={{ padding: '48px', maxWidth: '500px', margin: '0 auto', background: '#1F3A5F', border: '1px solid rgba(90, 169, 230, 0.25)' }}>
            <div style={{ fontSize: '3rem', marginBottom: '16px' }}>🔍</div>
            <h2 style={{ fontSize: '1.3rem', fontWeight: 600, marginBottom: '12px', color: '#EAF4F4' }}>Result Not Found</h2>
            <p style={{ color: 'rgba(234, 244, 244, 0.65)', marginBottom: '24px' }}>{error || 'This analysis could not be found.'}</p>
            <Link to="/" className="btn-primary" style={{ textDecoration: 'none', background: '#5AA9E6', color: '#222831' }}>
              ← Back to Home
            </Link>
          </div>
        </div>
      </div>
    )
  }

  const verdictClass = {
    LIKELY_TRUE: 'likely-true',
    LIKELY_FALSE: 'likely-false',
    UNVERIFIED: 'unverified',
    SUSPICIOUS: 'suspicious',
  }[result.verdict] || 'unverified'

  const verdictMarker = {
    LIKELY_TRUE: '✓',
    LIKELY_FALSE: '✕',
    UNVERIFIED: '—',
    SUSPICIOUS: '!',
  }[result.verdict] || '•'

  return (
    <div className="page" style={{ backgroundColor: '#222831' }}>
      <div className="container-sm">
        {/* Back link */}
        <Link
          to="/"
          style={{
            color: 'rgba(234, 244, 244, 0.65)',
            textDecoration: 'none',
            fontSize: '0.85rem',
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            marginBottom: '24px',
          }}
        >
          ← Back to Home
        </Link>

        {/* Verdict Header */}
        <div
          className={`result-header ${verdictClass} fade-in-up`}
          style={{
            background: '#1F3A5F',
            border: '1px solid rgba(90, 169, 230, 0.25)',
          }}
        >
          <div
            style={{
              fontSize: '0.75rem',
              color: '#5AA9E6',
              textTransform: 'uppercase',
              letterSpacing: '1.8px',
              fontWeight: 700,
            }}
          >
            Analysis Result
          </div>
          <div className="verdict-large" style={{ color: '#EAF4F4' }}>
            <span style={{ color: '#5AA9E6', marginRight: '8px' }}>{verdictMarker}</span>
            {result.verdict.replace('_', ' ')}
          </div>

          {/* Stats */}
          <div className="stats-row">
            <div className="stat-card" style={{ background: '#222831', border: '1px solid rgba(90, 169, 230, 0.2)' }}>
              <div className="stat-value" style={{ color: '#5AA9E6' }}>{result.confidence}%</div>
              <div className="stat-label">Confidence</div>
            </div>
            <div className="stat-card" style={{ background: '#222831', border: '1px solid rgba(90, 169, 230, 0.2)' }}>
              <div className="stat-value" style={{ color: '#EAF4F4' }}>
                {result.risk_score}/100
              </div>
              <div className="stat-label">Risk Score</div>
            </div>
            <div className="stat-card" style={{ background: '#222831', border: '1px solid rgba(90, 169, 230, 0.2)' }}>
              <div className="stat-value" style={{ color: '#5AA9E6' }}>{result.evidence_coverage}%</div>
              <div className="stat-label">Evidence Coverage</div>
            </div>
          </div>
        </div>

        {/* Input Content */}
        <div
          className="glass-card fade-in-up-delay-1"
          style={{
            padding: '24px',
            marginBottom: '20px',
            background: '#1F3A5F',
            border: '1px solid rgba(90, 169, 230, 0.2)',
          }}
        >
          <div className="section-title">Analyzed Content</div>
          <p style={{ fontSize: '0.95rem', lineHeight: 1.6, color: '#EAF4F4' }}>
            {result.input_content}
          </p>
          <div style={{ marginTop: '8px', fontSize: '0.75rem', color: 'rgba(234, 244, 244, 0.6)' }}>
            Type: {result.input_type.toUpperCase()} • Analyzed on {new Date(result.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })}
          </div>
        </div>

        {/* OCR Screenshot Inspection Card (for Image inputs) */}
        {(result.input_type === 'image' || result.ocr_text) && (
          <div
            className="glass-card fade-in-up-delay-1"
            style={{
              padding: '24px',
              marginBottom: '20px',
              background: '#1F3A5F',
              borderLeft: '4px solid #5AA9E6',
              border: '1px solid rgba(90, 169, 230, 0.2)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '12px', flexWrap: 'wrap', gap: '8px' }}>
              <div style={{ fontSize: '0.75rem', color: 'rgba(234, 244, 244, 0.7)', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 600 }}>
                📸 Optical Character Recognition (OCR) Extracted Text
              </div>
              <span style={{
                fontSize: '0.72rem',
                fontWeight: 600,
                padding: '3px 10px',
                borderRadius: '12px',
                background: 'rgba(90, 169, 230, 0.15)',
                color: '#5AA9E6',
                border: '1px solid rgba(90, 169, 230, 0.35)',
              }}>
                ✓ Native Windows OCR Processed
              </span>
            </div>
            <div style={{
              background: '#222831',
              border: '1px solid rgba(90, 169, 230, 0.15)',
              borderRadius: '8px',
              padding: '14px',
              fontFamily: 'monospace',
              fontSize: '0.88rem',
              color: '#EAF4F4',
              lineHeight: 1.6,
              whiteSpace: 'pre-wrap',
            }}>
              {result.ocr_text || result.input_content}
            </div>

            {/* Embedded Link Callout */}
            {result.embedded_url && (
              <div style={{
                marginTop: '14px',
                padding: '10px 14px',
                borderRadius: '8px',
                background: 'rgba(34, 40, 49, 0.8)',
                border: '1px solid rgba(90, 169, 230, 0.3)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '8px',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <span style={{ fontSize: '1rem' }}>🔗</span>
                  <span style={{ fontSize: '0.85rem', color: '#EAF4F4', fontWeight: 500 }}>
                    Embedded link detected: <strong style={{ color: '#5AA9E6' }}>{result.embedded_url}</strong>
                  </span>
                </div>
                <span style={{
                  fontSize: '0.72rem',
                  fontWeight: 600,
                  padding: '2px 8px',
                  borderRadius: '4px',
                  background: 'rgba(90, 169, 230, 0.2)',
                  color: '#5AA9E6',
                }}>
                  Security Scanned
                </span>
              </div>
            )}
          </div>
        )}

        {/* Social Media Forensics Card */}
        {result.social_details && (
          <div
            className="glass-card fade-in-up-delay-1"
            style={{
              padding: '24px',
              marginBottom: '20px',
              background: '#1F3A5F',
              borderLeft: '4px solid #5AA9E6',
              border: '1px solid rgba(90, 169, 230, 0.2)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
              <div>
                <div style={{ fontSize: '0.75rem', color: 'rgba(234, 244, 244, 0.65)', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 600 }}>
                  📱 Social Media Credibility & Viral Forensics
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '4px' }}>
                  <span style={{ fontSize: '1.4rem' }}>💬</span>
                  <span style={{ fontSize: '1.2rem', fontWeight: 700, color: '#EAF4F4' }}>
                    {result.social_details.platform}
                  </span>
                </div>
              </div>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
                <span
                  style={{
                    padding: '4px 12px',
                    borderRadius: '20px',
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    background: '#222831',
                    color: '#EAF4F4',
                    border: '1px solid rgba(90, 169, 230, 0.3)',
                  }}
                >
                  🎭 Impersonation: {result.social_details.impersonation_risk}
                </span>

                <span
                  style={{
                    padding: '4px 12px',
                    borderRadius: '20px',
                    fontSize: '0.75rem',
                    fontWeight: 600,
                    background: '#222831',
                    color: '#5AA9E6',
                    border: '1px solid rgba(90, 169, 230, 0.4)',
                  }}
                >
                  ⚡ Manipulation: {result.social_details.manipulation_level} ({Math.round(result.social_details.manipulation_score)}%)
                </span>
              </div>
            </div>

            {/* Handles and Hashtags */}
            {((result.social_details.handles && result.social_details.handles.length > 0) ||
              (result.social_details.hashtags && result.social_details.hashtags.length > 0)) && (
              <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '16px' }}>
                {result.social_details.handles.map((h, idx) => (
                  <span
                    key={`h-${idx}`}
                    style={{
                      background: 'rgba(90, 169, 230, 0.15)',
                      border: '1px solid rgba(90, 169, 230, 0.3)',
                      color: '#5AA9E6',
                      padding: '3px 10px',
                      borderRadius: '12px',
                      fontSize: '0.78rem',
                      fontFamily: 'monospace',
                    }}
                  >
                    @{h}
                  </span>
                ))}
                {result.social_details.hashtags.map((ht, idx) => (
                  <span
                    key={`ht-${idx}`}
                    style={{
                      background: '#222831',
                      border: '1px solid rgba(234, 244, 244, 0.2)',
                      color: '#EAF4F4',
                      padding: '3px 10px',
                      borderRadius: '12px',
                      fontSize: '0.78rem',
                      fontFamily: 'monospace',
                    }}
                  >
                    #{ht}
                  </span>
                ))}
              </div>
            )}

            {/* Impersonation Warnings */}
            {result.social_details.impersonation_flags && result.social_details.impersonation_flags.length > 0 && (
              <div style={{ marginBottom: '12px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {result.social_details.impersonation_flags.map((flag, idx) => (
                  <div
                    key={`imp-${idx}`}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      padding: '8px 12px',
                      borderRadius: '6px',
                      background: '#222831',
                      border: '1px solid rgba(234, 244, 244, 0.3)',
                      color: '#EAF4F4',
                      fontSize: '0.82rem',
                    }}
                  >
                    <span>⚠️</span>
                    <span>{flag}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Manipulation & Virality Signals */}
            {result.social_details.manipulation_signals && result.social_details.manipulation_signals.length > 0 && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {result.social_details.manipulation_signals.map((sig, idx) => (
                  <div
                    key={`sig-${idx}`}
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      padding: '8px 12px',
                      borderRadius: '6px',
                      background: '#222831',
                      border: '1px solid rgba(90, 169, 230, 0.3)',
                      color: '#5AA9E6',
                      fontSize: '0.82rem',
                    }}
                  >
                    <span>⚡</span>
                    <span>{sig}</span>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* Video Forensics & Keyframe Analysis Card */}
        {result.video_details && (
          <div
            className="glass-card fade-in-up-delay-1"
            style={{
              padding: '24px',
              marginBottom: '20px',
              background: '#1F3A5F',
              borderLeft: '4px solid #5AA9E6',
              border: '1px solid rgba(90, 169, 230, 0.2)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
              <div>
                <div style={{ fontSize: '0.75rem', color: 'rgba(234, 244, 244, 0.65)', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 600 }}>
                  🎥 Video Temporal & Keyframe Forensics
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginTop: '4px' }}>
                  <span style={{ fontSize: '1.4rem' }}>🎬</span>
                  <span style={{ fontSize: '1.2rem', fontWeight: 700, color: '#EAF4F4' }}>
                    {result.video_details.filename}
                  </span>
                </div>
              </div>

              <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
                <span style={{
                  padding: '4px 10px',
                  borderRadius: '16px',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  background: '#222831',
                  color: '#EAF4F4',
                  border: '1px solid rgba(90, 169, 230, 0.3)',
                }}>
                  ⏱️ {result.video_details.duration}s
                </span>
                <span style={{
                  padding: '4px 10px',
                  borderRadius: '16px',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  background: '#222831',
                  color: '#5AA9E6',
                  border: '1px solid rgba(90, 169, 230, 0.4)',
                }}>
                  📺 {result.video_details.resolution} @ {result.video_details.fps} FPS
                </span>
                <span style={{
                  padding: '4px 10px',
                  borderRadius: '16px',
                  fontSize: '0.75rem',
                  fontWeight: 600,
                  background: '#222831',
                  color: '#5AA9E6',
                  border: '1px solid rgba(90, 169, 230, 0.4)',
                }}>
                  🔍 {result.video_details.keyframes_sampled} Frames Analyzed
                </span>
              </div>
            </div>

            {/* On-Screen Text OCR Transcript */}
            <div style={{ marginBottom: '14px' }}>
              <div style={{ fontSize: '0.75rem', color: 'rgba(234, 244, 244, 0.65)', textTransform: 'uppercase', letterSpacing: '0.5px', marginBottom: '6px', fontWeight: 600 }}>
                Visual On-Screen Text & Subtitle OCR (Sampled Keyframes)
              </div>
              <div style={{
                background: '#222831',
                border: '1px solid rgba(90, 169, 230, 0.15)',
                borderRadius: '8px',
                padding: '12px 16px',
                fontFamily: 'monospace',
                fontSize: '0.85rem',
                color: '#EAF4F4',
                lineHeight: 1.6,
                whiteSpace: 'pre-wrap',
              }}>
                {result.video_details.on_screen_text || '[No on-screen text overlays detected across sampled keyframes]'}
              </div>
            </div>
          </div>
        )}

        {/* Website Security Breakdown */}
        {result.website_details && (
          <div
            className="glass-card fade-in-up-delay-1"
            style={{
              padding: '24px',
              marginBottom: '20px',
              background: '#1F3A5F',
              borderLeft: '4px solid #5AA9E6',
              border: '1px solid rgba(90, 169, 230, 0.2)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '12px' }}>
              <div>
                <div style={{ fontSize: '0.75rem', color: 'rgba(234, 244, 244, 0.65)', textTransform: 'uppercase', letterSpacing: '1px', fontWeight: 600 }}>
                  🌐 Domain Security Profile
                </div>
                <div style={{ fontSize: '1.2rem', fontWeight: 700, color: '#EAF4F4', marginTop: '2px' }}>
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
                    background: '#222831',
                    color: '#5AA9E6',
                    border: '1px solid #5AA9E6',
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
                    background: '#222831',
                    color: '#EAF4F4',
                    border: '1px solid rgba(234, 244, 244, 0.3)',
                  }}
                >
                  {result.website_details.risk_level} RISK
                </span>
              </div>
            </div>

            {/* Evaluated Security Signals */}
            {result.website_details.signals && result.website_details.signals.length > 0 && (
              <div>
                <div style={{ fontSize: '0.8rem', color: 'rgba(234, 244, 244, 0.7)', marginBottom: '8px', fontWeight: 500 }}>
                  Safety & Fraud Signals Detected:
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {result.website_details.signals.map((sig, idx) => (
                    <span
                      key={idx}
                      style={{
                        display: 'inline-flex',
                        alignItems: 'center',
                        gap: '6px',
                        padding: '6px 12px',
                        borderRadius: '8px',
                        fontSize: '0.78rem',
                        background: '#222831',
                        border: '1px solid rgba(90, 169, 230, 0.25)',
                        color: '#EAF4F4',
                      }}
                    >
                      <span style={{ color: '#5AA9E6' }}>•</span> {sig}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Claims */}
        {result.claims && result.claims.length > 0 && (
          <div
            className="glass-card fade-in-up-delay-1"
            style={{
              padding: '24px',
              marginBottom: '20px',
              background: '#1F3A5F',
              border: '1px solid rgba(90, 169, 230, 0.2)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div>
                <div className="section-title" style={{ marginBottom: '4px' }}>
                  Extracted Claims ({result.claims.length})
                </div>
                <div style={{ fontSize: '0.78rem', color: 'rgba(234, 244, 244, 0.65)' }}>
                  Atomic propositions decomposed for individual verification
                </div>
              </div>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
              {result.claims.map((claim, idx) => (
                <div
                  key={claim.id || idx}
                  style={{
                    background: '#222831',
                    border: '1px solid rgba(90, 169, 230, 0.15)',
                    borderRadius: '12px',
                    padding: '16px',
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '10px',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '12px', flexWrap: 'wrap' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span style={{ fontSize: '0.75rem', fontWeight: 700, color: '#222831', background: '#5AA9E6', padding: '2px 8px', borderRadius: '6px' }}>
                        Claim {idx + 1}
                      </span>
                      <span style={{ fontSize: '0.75rem', color: 'rgba(234, 244, 244, 0.7)', textTransform: 'capitalize' }}>
                        {claim.claim_type}
                      </span>
                    </div>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      {claim.confidence && (
                        <span style={{ fontSize: '0.75rem', color: '#5AA9E6' }}>
                          {Math.round(claim.confidence)}% conf.
                        </span>
                      )}
                      <VerdictBadge verdict={claim.verdict} />
                    </div>
                  </div>

                  <p style={{ fontSize: '0.92rem', color: '#EAF4F4', lineHeight: 1.5, margin: 0 }}>
                    "{claim.claim_text}"
                  </p>

                  {/* Extracted Entities */}
                  {claim.entities && claim.entities.length > 0 && (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '4px' }}>
                      <span style={{ fontSize: '0.72rem', color: 'rgba(234, 244, 244, 0.6)', alignSelf: 'center', marginRight: '4px' }}>
                        Entities:
                      </span>
                      {claim.entities.map((ent, eIdx) => (
                        <span
                          key={eIdx}
                          style={{
                            fontSize: '0.72rem',
                            padding: '2px 8px',
                            borderRadius: '4px',
                            background: 'rgba(90, 169, 230, 0.15)',
                            border: '1px solid rgba(90, 169, 230, 0.3)',
                            color: '#5AA9E6',
                          }}
                        >
                          🏷️ {ent}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Reasons / Evidence */}
        {result.reasons && result.reasons.length > 0 && (
          <div
            className="glass-card fade-in-up-delay-2"
            style={{
              padding: '24px',
              marginBottom: '20px',
              background: '#1F3A5F',
              border: '1px solid rgba(90, 169, 230, 0.2)',
            }}
          >
            <div className="section-title">Why This Verdict?</div>
            {result.reasons.map((reason, i) => (
              <div key={i} className="evidence-item" style={{ background: '#222831', border: '1px solid rgba(90, 169, 230, 0.15)' }}>
                <span className="evidence-icon">
                  {reason.type === 'contradiction' ? '✕' : reason.type === 'support' ? '✓' : '!'}
                </span>
                <span className="evidence-text">{reason.text}</span>
              </div>
            ))}
          </div>
        )}

        {/* Sources */}
        {result.sources && result.sources.length > 0 && (
          <div
            className="glass-card fade-in-up-delay-2"
            style={{
              padding: '24px',
              marginBottom: '20px',
              background: '#1F3A5F',
              border: '1px solid rgba(90, 169, 230, 0.2)',
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div>
                <div className="section-title" style={{ marginBottom: '2px' }}>Independent Sources ({result.sources.length})</div>
                <div style={{ fontSize: '0.78rem', color: 'rgba(234, 244, 244, 0.65)' }}>
                  Cross-referenced for credibility, stance, and evidence reliability
                </div>
              </div>
            </div>
            {result.sources.map((source, i) => (
              <div key={i} className="source-item" style={{ background: '#222831', border: '1px solid rgba(90, 169, 230, 0.15)', display: 'flex', alignItems: 'center', gap: '14px', padding: '12px 16px', borderRadius: '10px', marginBottom: '8px' }}>
                <span className="source-badge" style={{
                  width: '8px',
                  height: '8px',
                  borderRadius: '50%',
                  display: 'inline-block',
                  background: '#5AA9E6',
                  boxShadow: '0 0 6px rgba(90, 169, 230, 0.6)',
                }}></span>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                    <span className="source-name" style={{ fontWeight: 600, color: '#EAF4F4', fontSize: '0.9rem' }}>{source.name}</span>
                    <span style={{
                      fontSize: '0.7rem',
                      padding: '1px 6px',
                      borderRadius: '4px',
                      background: 'rgba(234, 244, 244, 0.08)',
                      color: 'rgba(234, 244, 244, 0.7)',
                      textTransform: 'uppercase',
                      letterSpacing: '0.5px',
                    }}>
                      {source.type}
                    </span>
                  </div>
                  {source.url && (
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{ fontSize: '0.75rem', color: '#5AA9E6', textDecoration: 'none', display: 'inline-flex', alignItems: 'center', gap: '4px', marginTop: '2px' }}
                    >
                      🔗 Verify Source ↗
                    </a>
                  )}
                </div>
                <span className="source-reliability" style={{
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  color: '#5AA9E6',
                  background: 'rgba(90, 169, 230, 0.15)',
                  padding: '4px 10px',
                  borderRadius: '12px',
                  border: '1px solid rgba(90, 169, 230, 0.3)',
                }}>
                  {Math.round(source.reliability * 100)}% reliability
                </span>
              </div>
            ))}
          </div>
        )}

        {/* Recommendation */}
        {result.recommendation && (
          <div
            className="glass-card fade-in-up-delay-3"
            style={{
              padding: '24px',
              marginBottom: '20px',
              background: '#1F3A5F',
              border: '1px solid rgba(90, 169, 230, 0.25)',
            }}
          >
            <div className="section-title">Recommendation</div>
            <p style={{ fontSize: '0.95rem', lineHeight: 1.6, color: '#EAF4F4' }}>
              {result.recommendation}
            </p>
          </div>
        )}

        {/* Action buttons */}
        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', marginTop: '32px' }}>
          <Link to="/" className="btn-primary" style={{ textDecoration: 'none', background: '#5AA9E6', color: '#222831' }}>
            🔍 New Analysis
          </Link>
          <Link to="/history" className="btn-secondary" style={{ textDecoration: 'none', background: '#1F3A5F', color: '#EAF4F4' }}>
            📋 View Dashboard
          </Link>
        </div>
      </div>
    </div>
  )
}

export default Results
