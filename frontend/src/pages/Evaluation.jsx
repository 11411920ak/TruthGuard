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
      <div className="page" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '60vh', backgroundColor: '#222831' }}>
        <div className="spinner"></div>
      </div>
    )
  }

  const metrics = data?.metrics || {}
  const matrix = metrics.confusion_matrix || {}
  const perClass = metrics.per_class || {}

  return (
    <div className="page" style={{ backgroundColor: '#222831' }}>
      <div className="container">
        {/* Header with Run Action */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '16px', marginBottom: '28px' }}>
          <div>
            <h1 style={{ fontSize: '2.2rem', fontWeight: 800, marginBottom: '6px', color: '#EAF4F4' }}>
              Model <span className="gradient-text">Evaluation</span> & Benchmarks
            </h1>
            <p style={{ color: 'rgba(234, 244, 244, 0.7)', fontSize: '0.95rem' }}>
              Academic-grade classification performance, 4x4 confusion matrix, and multi-modal benchmarks
            </p>
          </div>

          <button
            onClick={handleRunBenchmark}
            disabled={running}
            className="btn-primary"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 22px',
              fontSize: '0.9rem',
              background: '#5AA9E6',
              color: '#222831',
              fontWeight: 700,
            }}
          >
            {running ? (
              <>
                <span className="spinner" style={{ width: '16px', height: '16px', borderWidth: '2px' }} />
                <span>Running Benchmark...</span>
              </>
            ) : (
              <>
                <span>▶</span>
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
          <div className="glass-card" style={{ padding: '20px', background: '#1F3A5F', border: '1px solid rgba(90, 169, 230, 0.25)', borderLeft: '4px solid #5AA9E6' }}>
            <div style={{ fontSize: '0.75rem', color: 'rgba(234, 244, 244, 0.65)', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600 }}>
              Overall Accuracy
            </div>
            <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#EAF4F4', margin: '4px 0', fontFamily: 'Outfit' }}>
              {metrics.accuracy ?? 0}%
            </div>
            <div style={{ fontSize: '0.78rem', color: '#5AA9E6', fontWeight: 500 }}>
              {data?.total_evaluated || 0} benchmark ground-truth test cases
            </div>
          </div>

          {/* Macro F1 */}
          <div className="glass-card" style={{ padding: '20px', background: '#1F3A5F', border: '1px solid rgba(90, 169, 230, 0.25)', borderLeft: '4px solid #5AA9E6' }}>
            <div style={{ fontSize: '0.75rem', color: 'rgba(234, 244, 244, 0.65)', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600 }}>
              Macro F1-Score
            </div>
            <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#5AA9E6', margin: '4px 0', fontFamily: 'Outfit' }}>
              {metrics.macro_f1 ?? 0}%
            </div>
            <div style={{ fontSize: '0.78rem', color: 'rgba(234, 244, 244, 0.6)' }}>
              Harmonic mean of precision & recall
            </div>
          </div>

          {/* Macro Precision */}
          <div className="glass-card" style={{ padding: '20px', background: '#1F3A5F', border: '1px solid rgba(90, 169, 230, 0.25)', borderLeft: '4px solid rgba(234, 244, 244, 0.4)' }}>
            <div style={{ fontSize: '0.75rem', color: 'rgba(234, 244, 244, 0.65)', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600 }}>
              Macro Precision
            </div>
            <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#EAF4F4', margin: '4px 0', fontFamily: 'Outfit' }}>
              {metrics.macro_precision ?? 0}%
            </div>
            <div style={{ fontSize: '0.78rem', color: '#5AA9E6' }}>
              Low false positive rate across classes
            </div>
          </div>

          {/* Macro Recall */}
          <div className="glass-card" style={{ padding: '20px', background: '#1F3A5F', border: '1px solid rgba(90, 169, 230, 0.25)', borderLeft: '4px solid #5AA9E6' }}>
            <div style={{ fontSize: '0.75rem', color: 'rgba(234, 244, 244, 0.65)', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600 }}>
              Macro Recall
            </div>
            <div style={{ fontSize: '2.2rem', fontWeight: 800, color: '#5AA9E6', margin: '4px 0', fontFamily: 'Outfit' }}>
              {metrics.macro_recall ?? 0}%
            </div>
            <div style={{ fontSize: '0.78rem', color: 'rgba(234, 244, 244, 0.6)' }}>
              High detection rate of scam & truth claims
            </div>
          </div>
        </div>

        {/* 4x4 Confusion Matrix Section */}
        <div className="glass-card" style={{ padding: '24px', marginBottom: '28px', background: '#1F3A5F', border: '1px solid rgba(90, 169, 230, 0.2)' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '10px' }}>
            <div>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#EAF4F4' }}>
                4×4 Confusion Matrix
              </h3>
              <p style={{ color: 'rgba(234, 244, 244, 0.65)', fontSize: '0.82rem' }}>
                Rows represent Ground-Truth Actual class; Columns represent Predicted classification
              </p>
            </div>
            <span style={{
              fontSize: '0.75rem',
              color: '#222831',
              background: '#5AA9E6',
              padding: '3px 10px',
              borderRadius: '12px',
              fontWeight: 700,
            }}>
              Diagonal = Correct Predictions
            </span>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'center', fontSize: '0.85rem' }}>
              <thead>
                <tr>
                  <th style={{ padding: '12px', background: '#222831', color: 'rgba(234, 244, 244, 0.6)', textAlign: 'left' }}>
                    Actual \ Predicted
                  </th>
                  {CLASSES.map((c) => (
                    <th key={`head-${c}`} style={{ padding: '12px', background: '#222831', color: '#EAF4F4' }}>
                      {CLASS_LABELS[c]}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {CLASSES.map((actual) => (
                  <tr key={`row-${actual}`} style={{ borderBottom: '1px solid rgba(90, 169, 230, 0.1)' }}>
                    <td style={{ padding: '12px', textAlign: 'left', fontWeight: 600, color: '#EAF4F4', background: '#222831' }}>
                      {CLASS_LABELS[actual]}
                    </td>
                    {CLASSES.map((pred) => {
                      const count = matrix[actual]?.[pred] || 0
                      const isDiag = actual === pred
                      const hasCount = count > 0

                      let cellBg = 'transparent'
                      let cellColor = 'rgba(234, 244, 244, 0.3)'

                      if (isDiag && hasCount) {
                        cellBg = 'rgba(90, 169, 230, 0.18)'
                        cellColor = '#5AA9E6'
                      } else if (!isDiag && hasCount) {
                        cellBg = '#222831'
                        cellColor = '#EAF4F4'
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
                            border: isDiag && hasCount ? '1px solid #5AA9E6' : '1px solid transparent',
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
        <div className="glass-card" style={{ padding: '24px', marginBottom: '28px', background: '#1F3A5F', border: '1px solid rgba(90, 169, 230, 0.2)' }}>
          <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#EAF4F4', marginBottom: '16px' }}>
            Per-Class Classification Report
          </h3>
          <div style={{ overflowX: 'auto' }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '0.85rem' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid rgba(90, 169, 230, 0.2)', color: 'rgba(234, 244, 244, 0.65)' }}>
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
                    <tr key={`stat-${c}`} style={{ borderBottom: '1px solid rgba(90, 169, 230, 0.1)' }}>
                      <td style={{ padding: '12px 10px', display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <VerdictBadge verdict={c} />
                      </td>
                      <td style={{ padding: '12px 10px', color: '#EAF4F4', fontWeight: 600 }}>
                        {item.support ?? 0}
                      </td>
                      <td style={{ padding: '12px 10px', color: '#5AA9E6', fontWeight: 600 }}>
                        {item.precision ?? 0}%
                      </td>
                      <td style={{ padding: '12px 10px', color: '#EAF4F4', fontWeight: 600 }}>
                        {item.recall ?? 0}%
                      </td>
                      <td style={{ padding: '12px 10px', color: '#5AA9E6', fontWeight: 700 }}>
                        {item.f1_score ?? 0}%
                      </td>
                      <td style={{ padding: '12px 10px', color: 'rgba(234, 244, 244, 0.7)' }}>{item.tp ?? 0}</td>
                      <td style={{ padding: '12px 10px', color: 'rgba(234, 244, 244, 0.7)' }}>{item.fp ?? 0}</td>
                      <td style={{ padding: '12px 10px', color: 'rgba(234, 244, 244, 0.7)' }}>{item.fn ?? 0}</td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Item-Level Evaluation Audit Log */}
        {data?.item_results && data.item_results.length > 0 && (
          <div className="glass-card" style={{ padding: '24px', background: '#1F3A5F', border: '1px solid rgba(90, 169, 230, 0.2)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px', flexWrap: 'wrap', gap: '8px' }}>
              <div>
                <h3 style={{ fontSize: '1.2rem', fontWeight: 700, color: '#EAF4F4' }}>
                  Benchmark Test Execution Log
                </h3>
                <p style={{ color: 'rgba(234, 244, 244, 0.65)', fontSize: '0.82rem' }}>
                  Detailed test verification output for each ground-truth item
                </p>
              </div>
              <span style={{ fontSize: '0.8rem', color: '#5AA9E6' }}>
                Average Latency: <strong>{data.average_latency_ms}ms</strong> | Total Time: <strong>{data.total_duration_sec}s</strong>
              </span>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '400px', overflowY: 'auto' }}>
              {data.item_results.map((item, idx) => (
                <div
                  key={idx}
                  style={{
                    background: '#222831',
                    padding: '12px 16px',
                    borderRadius: '8px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    border: '1px solid rgba(90, 169, 230, 0.1)',
                  }}
                >
                  <div style={{ flex: 1, marginRight: '16px' }}>
                    <div style={{ fontSize: '0.85rem', color: '#EAF4F4', fontWeight: 500, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', maxWidth: '600px' }}>
                      {item.content}
                    </div>
                    <div style={{ fontSize: '0.72rem', color: 'rgba(234, 244, 244, 0.55)', marginTop: '4px' }}>
                      Ground Truth: <strong style={{ color: '#EAF4F4' }}>{CLASS_LABELS[item.actual]}</strong> • Predicted: <strong style={{ color: item.correct ? '#5AA9E6' : '#EAF4F4' }}>{CLASS_LABELS[item.predicted]}</strong>
                    </div>
                  </div>
                  <span
                    style={{
                      fontSize: '0.75rem',
                      fontWeight: 700,
                      padding: '3px 8px',
                      borderRadius: '6px',
                      background: item.correct ? 'rgba(90, 169, 230, 0.18)' : '#1F3A5F',
                      color: item.correct ? '#5AA9E6' : '#EAF4F4',
                      border: `1px solid ${item.correct ? '#5AA9E6' : 'rgba(234, 244, 244, 0.3)'}`,
                    }}
                  >
                    {item.correct ? '✓ MATCH' : '✕ MISMATCH'}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Evaluation
