import { Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import { getToken, getStoredUser } from './api'
import Layout from './Layout'
import Login from './pages/Login'
import Signup from './pages/Signup'
import Dashboard from './pages/Dashboard'
import CreatePlan from './pages/CreatePlan'
import PlanDetail from './pages/PlanDetail'

function RequireAuth({ children }) {
  const [checking, setChecking] = useState(true)
  const [user, setUser] = useState(null)

  useEffect(() => {
    const token = getToken()
    if (!token) {
      setChecking(false)
      return
    }
    setUser(getStoredUser())
    setChecking(false)
  }, [])

  if (checking) return <div className="app-loading">Loading…</div>
  if (!getToken()) return <Navigate to="/login" replace />
  return children
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route
        path="/"
        element={
          <RequireAuth>
            <Layout />
          </RequireAuth>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="plans/new" element={<CreatePlan />} />
        <Route path="plans/:planId" element={<PlanDetail />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
