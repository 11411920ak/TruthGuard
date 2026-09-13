import { Link, useLocation } from 'react-router-dom'

function Navbar() {
  const location = useLocation()

  const links = [
    { path: '/', label: 'Home' },
    { path: '/history', label: 'History' },
    { path: '/about', label: 'About' },
  ]

  return (
    <nav className="navbar">
      <Link to="/" className="navbar-brand">
        <span style={{ fontSize: '1.4rem' }}>🛡️</span>
        <span className="gradient-text">TruthGuard</span>
      </Link>

      <ul className="navbar-links">
        {links.map((link) => (
          <li key={link.path}>
            <Link
              to={link.path}
              className={location.pathname === link.path ? 'active' : ''}
            >
              {link.label}
            </Link>
          </li>
        ))}
        <li>
          <Link to="/login" className="btn-secondary" style={{ padding: '8px 20px', fontSize: '0.85rem' }}>
            Login
          </Link>
        </li>
      </ul>
    </nav>
  )
}

export default Navbar
