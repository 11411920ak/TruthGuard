function About() {
  return (
    <div className="page" style={{ backgroundColor: '#222831' }}>
      <div className="container-sm">
        <div className="fade-in-up">
          <h1 style={{ fontSize: '2rem', fontWeight: 800, marginBottom: '8px', color: '#EAF4F4' }}>
            About <span className="gradient-text">TruthGuard</span>
          </h1>
          <p style={{ color: 'rgba(234, 244, 244, 0.7)', marginBottom: '40px' }}>
            AI-Based Digital Content Verification & Scam Detection System
          </p>
        </div>

        {/* Mission */}
        <div className="glass-card fade-in-up-delay-1" style={{ padding: '32px', marginBottom: '20px', background: '#1F3A5F', border: '1px solid rgba(90, 169, 230, 0.2)' }}>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '12px', color: '#EAF4F4' }}>🎯 Our Mission</h2>
          <p style={{ color: 'rgba(234, 244, 244, 0.85)', lineHeight: 1.7, fontSize: '0.95rem' }}>
            In the age of digital misinformation, TruthGuard aims to empower users to make informed decisions
            about the content they encounter online. By combining multiple independent sources, AI analysis,
            and source reliability scoring, we provide transparent, evidence-based assessments of digital content.
          </p>
        </div>

        {/* How it works */}
        <div className="glass-card fade-in-up-delay-2" style={{ padding: '32px', marginBottom: '20px', background: '#1F3A5F', border: '1px solid rgba(90, 169, 230, 0.2)' }}>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '16px', color: '#EAF4F4' }}>⚙️ How It Works</h2>
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
                  background: '#5AA9E6',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontWeight: 700,
                  fontSize: '0.85rem',
                  color: '#222831',
                  flexShrink: 0,
                }}>
                  {item.step}
                </div>
                <div>
                  <h3 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: '4px', color: '#EAF4F4' }}>{item.title}</h3>
                  <p style={{ fontSize: '0.85rem', color: 'rgba(234, 244, 244, 0.7)', lineHeight: 1.5 }}>{item.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Verdicts explained */}
        <div className="glass-card fade-in-up-delay-3" style={{ padding: '32px', marginBottom: '20px', background: '#1F3A5F', border: '1px solid rgba(90, 169, 230, 0.2)' }}>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '16px', color: '#EAF4F4' }}>📊 Our Verdicts</h2>
          <p style={{ color: 'rgba(234, 244, 244, 0.75)', fontSize: '0.9rem', marginBottom: '16px', lineHeight: 1.6 }}>
            We never label content as simply "True" or "False." Instead, we provide nuanced verdicts:
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' }}>
            {[
              { symbol: '✓', label: 'LIKELY TRUE', desc: 'Multiple reliable sources confirm the claim', color: '#5AA9E6' },
              { symbol: '✕', label: 'LIKELY FALSE', desc: 'Strong evidence contradicts the claim', color: '#EAF4F4' },
              { symbol: '—', label: 'UNVERIFIED', desc: 'Insufficient evidence to confirm or deny', color: 'rgba(234, 244, 244, 0.8)' },
              { symbol: '!', label: 'SUSPICIOUS', desc: 'Multiple warning signals detected', color: '#5AA9E6' },
            ].map((v) => (
              <div key={v.label} style={{ padding: '16px', borderRadius: '10px', background: '#222831', border: '1px solid rgba(90, 169, 230, 0.2)' }}>
                <div style={{ marginBottom: '6px' }}>
                  <span style={{ fontSize: '1.1rem', fontWeight: 800, color: v.color }}>{v.symbol}</span>
                  <span style={{ marginLeft: '8px', fontWeight: 700, fontSize: '0.85rem', color: v.color }}>{v.label}</span>
                </div>
                <p style={{ fontSize: '0.8rem', color: 'rgba(234, 244, 244, 0.65)' }}>{v.desc}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Tech stack */}
        <div className="glass-card fade-in-up-delay-3" style={{ padding: '32px', marginBottom: '20px', background: '#1F3A5F', border: '1px solid rgba(90, 169, 230, 0.2)' }}>
          <h2 style={{ fontSize: '1.2rem', fontWeight: 700, marginBottom: '16px', color: '#EAF4F4' }}>🛠️ Tech Stack</h2>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '12px' }}>
            {[
              { label: 'React.js', desc: 'Frontend UI' },
              { label: 'FastAPI', desc: 'Backend Services' },
              { label: 'PostgreSQL', desc: 'Audit Log' },
              { label: 'Minimal Theme', desc: '#222831 / #1F3A5F' },
              { label: 'LLM Verification', desc: 'AI Analysis' },
              { label: 'Scikit-learn', desc: 'ML Scoring' },
            ].map((tech) => (
              <div key={tech.label} style={{ padding: '12px', textAlign: 'center', borderRadius: '8px', background: '#222831', border: '1px solid rgba(90, 169, 230, 0.15)' }}>
                <div style={{ fontWeight: 600, fontSize: '0.9rem', color: '#EAF4F4' }}>{tech.label}</div>
                <div style={{ fontSize: '0.75rem', color: '#5AA9E6', marginTop: '4px' }}>{tech.desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Project info */}
        <div className="glass-card" style={{ padding: '24px', textAlign: 'center', background: '#1F3A5F', border: '1px solid rgba(90, 169, 230, 0.2)' }}>
          <p style={{ fontSize: '0.85rem', color: 'rgba(234, 244, 244, 0.7)' }}>
            TruthGuard is an AI-based digital content verification and scam detection system built with academic precision and minimal aesthetics.
          </p>
        </div>
      </div>
    </div>
  )
}

export default About
