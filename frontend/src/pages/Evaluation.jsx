import { useState, useEffect } from 'react'
import VerdictBadge from '../components/VerdictBadge'
import { getEvaluationMetrics, runEvaluationBenchmark } from '../services/api'

const CLASSES = ['LIKELY_TRUE', 'LIKELY_FALSE', 'SUSPICIOUS', 'UNVERIFIED']

const CLASS_LABELS = {
  LIKELY_TRUE: 'Likely True',
  LIKELY_FALSE: 'Likely False',
  SUSPICIOUS: 'Suspicious',
  UNVERIFIED: 'Unverified',
}

function Evaluation() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [running, setRunning] = useState(false)

  async function loadMetrics() {
    setLoading(true)
    try {
      const res = await getEvaluationMetrics()
      setData(res)
    } catch (err) {
      console.error('Failed to load evaluation metrics:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadMetrics()
  }, [])

  async function handleRunBenchmark() {
    setRunning(true)
    try {
      const res = await runEvaluationBenchmark()
      setData(res)
    } catch (err) {
      console.error('Failed to run benchmark:', err)
    } finally {
      setRunning(false)
    }
  }

  if (loading) {
    return (
      <div className="page" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh' }}>
        <div className="spinner"></div>
      </div>
    )
  }

  const metrics = data?.metrics || {}
  const matrix = metrics.confusion_matrix || {}
  const perClass = metrics.per_class || {}

  return (
    <div className="page">
      <div className="container">
        {/* Header with Run Action */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px', marginBottom: '28px' }}>
          <div>
            <h1 style={{ fontSize: '2.2rem', fontWeight: 800, marginBottom: '6px' }}>
              Model <span className="gradient-text">Evaluation</span> & Benchmarks
            </h1>
            <p style={{ color: '#94a3b8', fontSize: '0.95rem' }}>
              Academic-grade classification performance, 4x4 confusion matrix, and multi-modal benchmarks
            </p>
          </div>

          <button
            onClick={handleRunBenchmark}
            disabled={running}
            className="btn-primary"
            style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', padding: '10px 20px', fontSize: '0.9rem' }}
          >
            {running ? (
              <>
                <span className="spinner" style={{ width: '16px', height: '16px', borderWidth: '2px' }} />
                <span>Running Benchmark...</span>
              </>
            ) : (
              <>
                <span>▶️</span>
                <span>Run Live Benchmark</span>
              </>
            )}
          </button>
        </div>

        {/* Top 4 Performance KPI Cards */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
          gap: '16px',
          marginBottom: '28px',
        }}>
          {/* Accuracy */}
          <div className="glass-card" style={{ padding: '20px', borderLeft: '4px solid #34d399' }}>
            <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600 }}>
              Overall Accuracy
            </div>
            <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#34d399', margin: '4px 0' }}>
              {metrics.accuracy ?? 0}%
            </div>
            <div style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
              {data?.total_evaluated || 0} benchmark ground-truth test cases
            </div>
          </div>

          {/* Macro F1 */}
          <div className="glass-card" style={{ padding: '20px', borderLeft: '4px solid #38bdf8' }}>
            <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600 }}>
              Macro F1-Score
            </div>
            <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#38bdf8', margin: '4px 0' }}>
              {metrics.macro_f1 ?? 0}%
            </div>
            <div style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
              Harmonic mean of precision & recall
            </div>
          </div>

          {/* Macro Precision */}
          <div className="glass-card" style={{ padding: '20px', borderLeft: '4px solid #a855f7' }}>
            <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600 }}>
              Macro Precision
            </div>
            <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#c084fc', margin: '4px 0' }}>
              {metrics.macro_precision ?? 0}%
            </div>
            <div style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
              Low false positive rate across classes
            </div>
          </div>

          {/* Macro Recall */}
          <div className="glass-card" style={{ padding: '20px', borderLeft: '4px solid #f59e0b' }}>
            <div style={{ fontSize: '0.75rem', color: '#64748b', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600 }}>
              Macro Recall
            </div>
            <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#fbbf24', margin: '4px 0' }}>
              {metrics.macro_recall ?? 0}%
            </div>
            <div style={{ fontSize: '0.78rem', color: '#94a3b8' }}>
              High detection rate of scam & truth claims
            </div>
          </div>
        </div>

        {/* 4x4 Confusion Matrix Section */}
        <div className="glass-card" style={{ padding: '24px', marginBottom: '28px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
            <div>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>
                4×4 Confusion Matrix
              </h3>
              <p style={{ color: '#94a3b8', fontSize: '0.82rem' }}>
                Rows represent Ground-Truth Actual class; Columns represent Predicted classification
              </p>
            </div>
            <span style={{
              fontSize: '0.75rem',
              color: '#34d399',
              background: 'rgba(52, 211, 153, 0.12)',
              border: '1px solid rgba(52, 211, 153, 0.25)',
              padding: '3px 10px',
              borderRadius: '12px',
              fontWeight: 600,
            }}>
              Diagonal = Correct Predictions
            </span>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'center', fontSize: '0.85rem' }}>
              <thead>
                <tr>
                  <th style={{ padding: '12px', background: 'rgba(0,0,0,0.3)', color: '#94a3b8', textAlign: 'left' }}>
                    Actual \ Predicted
                  </th>
                  {CLASSES.map((c) => (
                    <th key={`head-${c}`} style={{ padding: '12px', background: 'rgba(0,0,0,0.3)', color: '#cbd5e1' }}>
                      {CLASS_LABELS[c]}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {CLASSES.map((actual) => (
                  <tr key={`row-${actual}`} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                    <td style={{ padding: '12px', textAlign: 'left', fontWeight: 600, color: '#cbd5e1', background: 'rgba(0,0,0,0.15)' }}>
                      {CLASS_LABELS[actual]}
                    </td>
                    {CLASSES.map((pred) => {
                      const count = matrix[actual]?.[pred] || 0
                      const isDiag = actual === pred
                      const hasCount = count > 0

                      let cellBg = 'transparent'
                      let cellColor = '#64748b'

                      if (isDiag && hasCount) {
                        cellBg = 'rgba(52, 211, 153, 0.15)'
                        cellColor = '#34d399'
                      } else if (!isDiag && hasCount) {
                        cellBg = 'rgba(239, 68, 68, 0.15)'
                        cellColor = '#f87171'
                      }

                      return (
                        <td
                          key={`cell-${actual}-${pred}`}
                          style={{
                            padding: '14px',
                            fontWeight: isDiag ? 700 : 500,
                            fontSize: '1rem',
                            background: cellBg,
                            color: cellColor,
                            border: isDiag && hasCount ? '1px solid rgba(52, 211, 153, 0.3)' : '1px solid transparent',
                          }}
                        >
                          {count}
                        </td>
                      )
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Per-Class Detailed Performance Table */}
        <div className="glass-card" style={{ padding: '24px', marginBottom: '28px' }}>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc', marginBottom: '16px' }}>
            Per-Class Classification Report
          </h3>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid rgba(255,255,255,0.1)', color: '#94a3b8' }}>
                  <th style={{ padding: '10px' }}>Verdict Category</th>
                  <th style={{ padding: '10px' }}>Support</th>
                  <th style={{ padding: '10px' }}>Precision</th>
                  <th style={{ padding: '10px' }}>Recall</th>
                  <th style={{ padding: '10px' }}>F1-Score</th>
                  <th style={{ padding: '10px' }}>TP</th>
                  <th style={{ padding: '10px' }}>FP</th>
                  <th style={{ padding: '10px' }}>FN</th>
                </tr>
              </thead>
              <tbody>
                {CLASSES.map((c) => {
                  const item = perClass[c] || {}
                  return (
                    <tr key={`stat-${c}`} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                      <td style={{ padding: '12px 10px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <VerdictBadge verdict={c} />
                      </td>
                      <td style={{ padding: '12px 10px', color: '#f8fafc', fontWeight: 600 }}>
                        {item.support ?? 0}
                      </td>
                      <td style={{ padding: '12px 10px', color: '#38bdf8', fontWeight: 600 }}>
                        {item.precision ?? 0}%
                      </td>
                      <td style={{ padding: '12px 10px', color: '#fbbf24', fontWeight: 600 }}>
                        {item.recall ?? 0}%
                      </td>
                      <td style={{ padding: '12px 10px', color: '#34d399', fontWeight: 700 }}>
                        {item.f1_score ?? 0}%
                      </td>
                      <td style={{ padding: '12px 10px', color: '#94a3b8' }}>{item.tp ?? 0}</td>
                      <td style={{ padding: '12px 10px', color: '#94a3b8' }}>{item.fp ?? 0}</td>
                      <td style={{ padding: '12px 10px', color: '#94a3b8' }}>{item.fn ?? 0}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Item-Level Evaluation Audit Log */}
        {data?.item_results && data.item_results.length > 0 && (
          <div className="glass-card" style={{ padding: '24px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '8px' }}>
              <div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#f8fafc' }}>
                  Benchmark Test Execution Log
                </h3>
                <p style={{ color: '#94a3b8', fontSize: '0.82rem' }}>
                  Detailed test verification output for each ground-truth item
                </p>
              </div>
              <span style={{ fontSize: '0.8rem', color: '#64748b' }}>
                Average Latency: <strong>{data.average_latency_ms}ms</strong> | Total Time: <strong>{data.total_duration_sec}s</strong>
              </span>
            </div>

            <div style={{ overflowX: 'auto' }}>
              <table className="history-table">
                <thead>
                  <tr>
                    <th>Item ID</th>
                    <th>Type</th>
                    <th>Content Preview</th>
                    <th>Expected</th>
                    <th>Predicted</th>
                    <th>Status</th>
                    <th>Latency</th>
                  </tr>
                </thead>
                <tbody>
                  {data.item_results.map((item) => (
                    <tr key={item.id}>
                      <td style={{ fontFamily: 'monospace', color: '#94a3b8', fontSize: '0.78rem' }}>
                        {item.id}
                      </td>
                      <td style={{ textTransform: 'uppercase', fontSize: '0.75rem', color: '#38bdf8' }}>
                        {item.input_type}
                      </td>
                      <td style={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', color: '#e2e8f0', fontSize: '0.82rem' }}>
                        {item.content}
                      </td>
                      <td>
                        <VerdictBadge verdict={item.expected} />
                      </td>
                      <td>
                        <VerdictBadge verdict={item.predicted} />
                      </td>
                      <td>
                        <span style={{
                          padding: '2px 8px',
                          borderRadius: '10px',
                          fontSize: '0.75rem',
                          fontWeight: 600,
                          background: item.is_correct ? 'rgba(52, 211, 153, 0.15)' : 'rgba(239, 68, 68, 0.15)',
                          color: item.is_correct ? '#34d399' : '#f87171',
                        }}>
                          {item.is_correct ? '✓ Match' : '✗ Mismatch'}
                        </span>
                      </td>
                      <td style={{ color: '#94a3b8', fontSize: '0.78rem', textAlign: 'right' }}>
                        {item.latency_ms}ms
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Evaluation
