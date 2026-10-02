function LoadingSpinner({ message = 'Analyzing...' }) {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px' }}>
      <div className="spinner"></div>
      <p style={{ color: 'rgba(234, 244, 244, 0.75)', fontSize: '0.95rem' }}>{message}</p>
    </div>
  )
}

export default LoadingSpinner
