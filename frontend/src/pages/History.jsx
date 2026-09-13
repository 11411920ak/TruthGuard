import { useState, useEffect } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import VerdictBadge from '../components/VerdictBadge'
import { getHistory } from '../services/api'

const typeIcons = {
  text: '📝',
  url: '🌐',
  image: '🖼️',
  video: '🎥',
}

function History() {
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    async function fetchHistory() {
      try {
        const data = await getHistory()
        setHistory(data.analyses || [])
      } catch (err) {
        console.error('Failed to fetch history:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchHistory()
  }, [])

  if (loading) {
    return (
      <div className="page" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
        <div className="spinner"></div>
      </div>
    )
  }

  return (
    <div className="page">
      <div className="container">
        <div className="fade-in-up">
          <h1 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '8px' }}>
            Analysis <span className="gradient-text">History</span>
          </h1>
          <p style={{ color: '#64748b', marginBottom: '36px' }}>
            Your past verifications and analyses
          </p>
        </div>

        {history.length === 0 ? (
          <div className="glass-card fade-in-up-delay-1" style={{ padding: '60px 24px', textAlign: 'center' }}>
            <div style={{ fontSize: '3rem', marginBottom: '16px' }}>📋</div>
            <h3 style={{ fontSize: '1.1rem', fontWeight: 600, marginBottom: '8px' }}>No analyses yet</h3>
            <p style={{ color: '#64748b', marginBottom: '24px' }}>Start your first verification to see results here.</p>
            <Link to="/" className="btn-primary" style={{ textDecoration: 'none' }}>
              🔍 Start Verifying
            </Link>
          </div>
        ) : (
          <div className="glass-card fade-in-up-delay-1" style={{ padding: '8px', overflow: 'auto' }}>
            <table className="history-table">
              <thead>
                <tr>
                  <th>Date</th>
                  <th>Type</th>
                  <th>Content</th>
                  <th>Result</th>
                  <th>Confidence</th>
                </tr>
              </thead>
              <tbody>
                {history.map((item) => (
                  <tr key={item.id} onClick={() => navigate(`/results/${item.id}`)}>
                    <td style={{ whiteSpace: 'nowrap', color: '#94a3b8' }}>
                      {new Date(item.created_at).toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}
                    </td>
                    <td>
                      <span style={{ fontSize: '1.1rem' }}>{typeIcons[item.input_type] || '📝'}</span>
                      <span style={{ marginLeft: '8px', fontSize: '0.8rem', color: '#94a3b8', textTransform: 'capitalize' }}>
                        {item.input_type}
                      </span>
                    </td>
                    <td style={{
                      maxWidth: '300px',
                      overflow: 'hidden',
                      textOverflow: 'ellipsis',
                      whiteSpace: 'nowrap',
                      color: '#cbd5e1',
                    }}>
                      {item.input_content}
                    </td>
                    <td>
                      <VerdictBadge verdict={item.verdict} />
                    </td>
                    <td style={{ textAlign: 'center', fontWeight: 600 }}>
                      {item.confidence}%
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
