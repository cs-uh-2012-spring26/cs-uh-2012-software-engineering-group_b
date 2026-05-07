import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Navbar() {
  const { user, logout, isAuthenticated } = useAuth()
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <nav className="navbar">
      <span className="navbar-brand">Coachly</span>
      <Link to="/classes">Classes</Link>
      {isAuthenticated ? (
        <>
          <Link to="/settings">Settings</Link>
          {(user?.role === 'trainer' || user?.role === 'admin') && (
            <Link to="/classes/create">+ Create Class</Link>
          )}
          <span className="role-badge">{user?.role}</span>
          <span style={{ fontSize: '0.9rem', opacity: 0.85 }}>{user?.email}</span>
          <button className="btn-logout" onClick={handleLogout}>Logout</button>
        </>
      ) : (
        <>
          <Link to="/login">Login</Link>
          <Link to="/register">Register</Link>
        </>
      )}
    </nav>
  )
}
