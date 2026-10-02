import { useState } from 'react'
import { Link } from 'react-router-dom'

function Login() {
  const [isLogin, setIsLogin] = useState(true)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')

  function handleSubmit(e) {
    e.preventDefault()
    // TODO: Connect to authentication API
    alert(`${isLogin ? 'Login' : 'Register'} coming soon! This feature will be available after core verification features are complete.`)
  }

  return (
    <div className="page" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', backgroundColor: '#222831' }}>
      <div className="auth-card fade-in-up">
        <div style={{ textAlign: 'center', marginBottom: '32px' }}>
          <div style={{ fontSize: '2.5rem', marginBottom: '12px', color: '#5AA9E6' }}>🛡️</div>
          <h1 style={{ fontSize: '1.6rem', fontWeight: 700, color: '#EAF4F4' }}>
            {isLogin ? 'Welcome back' : 'Create account'}
          </h1>
          <p style={{ color: 'rgba(234, 244, 244, 0.7)', fontSize: '0.9rem', marginTop: '8px' }}>
            {isLogin ? 'Sign in to access your audit dashboard' : 'Join TruthGuard to track verification history'}
          </p>
        </div>

        <form onSubmit={handleSubmit} className="glass-card" style={{ padding: '32px', background: '#1F3A5F', border: '1px solid rgba(90, 169, 230, 0.25)' }}>
          {!isLogin && (
            <div className="form-group">
              <label className="form-label">Full Name</label>
              <input
                type="text"
                className="form-input"
                placeholder="Your name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
          )}

          <div className="form-group">
            <label className="form-label">Email</label>
            <input
              type="email"
              className="form-input"
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label className="form-label">Password</label>
            <input
              type="password"
              className="form-input"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button
            type="submit"
            className="btn-primary"
            style={{ width: '100%', justifyContent: 'center', marginTop: '8px', background: '#5AA9E6', color: '#222831' }}
          >
            {isLogin ? '🔐 Sign In' : '🚀 Create Account'}
          </button>

          <div style={{ textAlign: 'center', marginTop: '20px' }}>
            <button
              type="button"
              onClick={() => setIsLogin(!isLogin)}
              style={{
                background: 'none',
                border: 'none',
                color: '#5AA9E6',
                cursor: 'pointer',
                fontSize: '0.85rem',
                fontFamily: 'Inter, sans-serif',
                fontWeight: 600,
              }}
            >
              {isLogin ? "Don't have an account? Sign up" : 'Already have an account? Sign in'}
            </button>
          </div>
        </form>

        <div style={{ textAlign: 'center', marginTop: '24px' }}>
          <Link to="/" style={{ color: 'rgba(234, 244, 244, 0.65)', fontSize: '0.85rem', textDecoration: 'none' }}>
            ← Continue without signing in
          </Link>
        </div>
      </div>
    </div>
  )
}

export default Login
