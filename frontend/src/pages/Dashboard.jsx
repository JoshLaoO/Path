import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'
import './Dashboard.css'

export default function Dashboard() {
  const [plans, setPlans] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    api
      .myPlans()
      .then((data) => {
        if (!cancelled) setPlans(data)
      })
      .catch((err) => {
        if (!cancelled) setError(err.message)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => { cancelled = true }
  }, [])

  if (loading) return <p className="dashboard-loading">Loading your plans…</p>
  if (error) return <p className="dashboard-error">{error}</p>

  return (
    <div className="dashboard">
      <h1 className="dashboard-title">My plans</h1>
      {plans.length === 0 ? (
        <div className="dashboard-empty">
          <p>You don’t have any plans yet.</p>
          <Link to="/plans/new" className="dashboard-cta">
            Create your first plan
          </Link>
        </div>
      ) : (
        <ul className="plan-list">
          {plans.map((plan) => (
            <li key={plan.id}>
              <Link to={`/plans/${plan.id}`} className="plan-card">
                <h2 className="plan-card-title">{plan.title}</h2>
                {plan.description && (
                  <p className="plan-card-desc">{plan.description}</p>
                )}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
