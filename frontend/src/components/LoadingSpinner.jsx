function LoadingSpinner({ message = 'Analyzing...' }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px' }}>
      <div className="spinner"></div>
      <p style={{ color: '#94a3b8', fontSize: '0.95rem' }}>{message}</p>
    </div>
  )
}

export default LoadingSpinner
