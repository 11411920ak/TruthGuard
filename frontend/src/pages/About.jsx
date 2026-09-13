function About() {
  return (
    <div className="page">
      <div className="container-sm">
        <div className="fade-in-up">
          <h1 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '8px' }}>
            About <span className="gradient-text">TruthGuard</span>
          </h1>
          <p style={{ color: '#64748b', marginBottom: '40px' }}>
            AI-Based Digital Content Verification & Scam Detection System
          </p>
        </div>

        {/* Mission */}
        <div className="glass-card fade-in-up-delay-1" style={{ padding: '32px', marginBottom: '20px' }}>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '12px' }}>🎯 Our Mission</h2>
          <p style={{ color: '#94a3b8', lineHeight: 1.7, fontSize: '0.95rem' }}>
            In the age of digital misinformation, TruthGuard aims to empower users to make informed decisions
            about the content they encounter online. By combining multiple independent sources, AI analysis,
            and source reliability scoring, we provide transparent, evidence-based assessments of digital content.
          </p>
        </div>

        {/* How it works */}
        <div className="glass-card fade-in-up-delay-2" style={{ padding: '32px', marginBottom: '20px' }}>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '16px' }}>⚙️ How It Works</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {[
              { step: '1', title: 'Input', desc: 'Submit a URL, text claim, screenshot, or video for verification.' },
              { step: '2', title: 'Claim Extraction', desc: 'AI extracts individual verifiable claims from the content.' },
              { step: '3', title: 'Evidence Retrieval', desc: 'Multiple sources are searched — government, news, fact-checkers, and more.' },
              { step: '4', title: 'Source Reliability', desc: 'Each source is scored based on its credibility and track record.' },
              { step: '5', title: 'Verdict', desc: 'Evidence is weighed and a confidence score is calculated. Never just TRUE/FALSE — we show the full picture.' },
            ].map((item) => (
              <div key={item.step} style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
                <div style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, #10b981, #06b6d4)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 700,
                  fontSize: '0.85rem',
                  color: '#030712',
                  flexShrink: 0,
                }}>
                  {item.step}
                </div>
                <div>
                  <h3 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '4px' }}>{item.title}</h3>
                  <p style={{ fontSize: '0.85rem', color: '#94a3b8', lineHeight: 1.5 }}>{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Verdicts explained */}
        <div className="glass-card fade-in-up-delay-3" style={{ padding: '32px', marginBottom: '20px' }}>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '16px' }}>📊 Our Verdicts</h2>
          <p style={{ color: '#94a3b8', fontSize: '0.9rem', marginBottom: '16px', lineHeight: 1.6 }}>
            We never label content as simply "True" or "False." Instead, we provide nuanced verdicts:
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            {[
              { emoji: '🟢', label: 'LIKELY TRUE', desc: 'Multiple reliable sources confirm the claim', color: '#34d399' },
              { emoji: '🔴', label: 'LIKELY FALSE', desc: 'Strong evidence contradicts the claim', color: '#f87171' },
              { emoji: '🟡', label: 'UNVERIFIED', desc: 'Insufficient evidence to confirm or deny', color: '#fbbf24' },
              { emoji: '🟠', label: 'SUSPICIOUS', desc: 'Multiple warning signals detected', color: '#fb923c' },
            ].map((v) => (
              <div key={v.label} style={{ padding: '16px', borderRadius: '10px', background: 'rgba(10,15,30,0.4)' }}>
                <div style={{ marginBottom: '6px' }}>
                  <span style={{ fontSize: '1.1rem' }}>{v.emoji}</span>
                  <span style={{ marginLeft: '8px', fontWeight: 600, fontSize: '0.85rem', color: v.color }}>{v.label}</span>
                </div>
                <p style={{ fontSize: '0.8rem', color: '#64748b' }}>{v.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Tech stack */}
        <div className="glass-card fade-in-up-delay-3" style={{ padding: '32px', marginBottom: '20px' }}>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '16px' }}>🛠️ Tech Stack</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
            {[
              { label: 'React.js', desc: 'Frontend' },
              { label: 'FastAPI', desc: 'Backend' },
              { label: 'PostgreSQL', desc: 'Database' },
              { label: 'Tailwind CSS', desc: 'Styling' },
              { label: 'LLM API', desc: 'AI Analysis' },
              { label: 'scikit-learn', desc: 'ML Scoring' },
            ].map((tech) => (
              <div key={tech.label} style={{ padding: '12px', textAlign: 'center', borderRadius: '8px', background: 'rgba(10,15,30,0.4)' }}>
                <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{tech.label}</div>
                <div style={{ fontSize: '0.75rem', color: '#475569', marginTop: '4px' }}>{tech.desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Project info */}
        <div className="glass-card" style={{ padding: '24px', textAlign: 'center' }}>
          <p style={{ fontSize: '0.85rem', color: '#64748b' }}>
            TruthGuard is a final-year academic project demonstrating AI-based content verification
            and misinformation detection techniques.
          </p>
        </div>
      </div>
    </div>
  )
}

export default About
