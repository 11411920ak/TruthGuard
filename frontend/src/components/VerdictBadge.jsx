function VerdictBadge({ verdict }) {
  const config = {
    LIKELY_TRUE: { label: '🟢 Likely True', className: 'verdict-likely-true' },
    LIKELY_FALSE: { label: '🔴 Likely False', className: 'verdict-likely-false' },
    UNVERIFIED: { label: '🟡 Unverified', className: 'verdict-unverified' },
    SUSPICIOUS: { label: '🟠 Suspicious', className: 'verdict-suspicious' },
  }

  const cfg = config[verdict] || config.UNVERIFIED

  return (
    <span className={`verdict-badge ${cfg.className}`}>
      {cfg.label}
    </span>
  )
}

export default VerdictBadge
