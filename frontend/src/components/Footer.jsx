function Footer() {
  return (
    <footer className="footer">
      <p>
        © {new Date().getFullYear()} <span className="gradient-text" style={{ fontWeight: 600 }}>TruthGuard</span> — AI-Based Digital Content Verification & Scam Detection
      </p>
      <p style={{ marginTop: '8px', fontSize: '0.75rem', color: 'rgba(234, 244, 244, 0.5)' }}>
        Final Year Project • Built with React, FastAPI & AI
      </p>
    </footer>
  )
}

export default Footer
