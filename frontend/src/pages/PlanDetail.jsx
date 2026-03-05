import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { api } from '../api'
import './PlanDetail.css'

export default function PlanDetail() {
  const { planId } = useParams()
  const [plan, setPlan] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let cancelled = false
    api
      .getPlanWithDays(planId)
      .then((data) => {
        if (!cancelled) setPlan(data)
      })
      .catch((err) => {
        if (!cancelled) setError(err.message)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => { cancelled = true }
  }, [planId])

  if (loading) return <p className="plan-detail-loading">Loading plan…</p>
  if (error) return <p className="plan-detail-error">{error}</p>
  if (!plan) return null

  const days = plan.plan_days || []

  return (
    <div className="plan-detail">
      <Link to="/" className="plan-detail-back">← My plans</Link>
      <header className="plan-detail-header">
        <h1 className="plan-detail-title">{plan.title}</h1>
        {plan.description && (
          <p className="plan-detail-desc">{plan.description}</p>
        )}
      </header>
      <ol className="plan-day-list">
        {days.map((day) => (
          <li key={day.id} className="plan-day">
            <span className="plan-day-num">Day {day.day_number}</span>
            <div className="plan-day-verse">
              {day.verse?.split('\n').map((line, i) => (
                <p key={i}>{line}</p>
              ))}
            </div>
          </li>
        ))}
      </ol>
    </div>
  )
}
