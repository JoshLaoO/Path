import { Outlet, Link, useNavigate } from 'react-router-dom'
import { logout } from './api'
import './Layout.css'

export default function Layout() {
  const navigate = useNavigate()

  function handleLogout() {
    logout()
    navigate('/login')
  }

  return (
    <div className="layout">
      <header className="layout-header">
        <Link to="/" className="layout-brand">
          Path
        </Link>
        <nav className="layout-nav">
          <Link to="/">My plans</Link>
          <Link to="/plans/new">New plan</Link>
          <button type="button" className="layout-logout" onClick={handleLogout}>
            Sign out
          </button>
        </nav>
      </header>
      <main className="layout-main">
        <Outlet />
      </main>
    </div>
  )
}
