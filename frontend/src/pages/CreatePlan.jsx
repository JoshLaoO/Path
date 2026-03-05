import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api, getStoredUser } from '../api'
import './CreatePlan.css'

const TRANSLATIONS = [
  { value: 'web', label: 'World English Bible (WEB)' },
  { value: 'kjv', label: 'King James Version (KJV)' },
  { value: 'asv', label: 'American Standard Version (ASV)' },
]

export default function CreatePlan() {
  const navigate = useNavigate()
  const user = getStoredUser()
  const [theme, setTheme] = useState('')
  const [durationDays, setDurationDays] = useState(7)
  const [translation, setTranslation] = useState('web')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    if (!user?.id) {
      setError('Not signed in')
      return
    }
    setError('')
    setLoading(true)
    try {
      const plan = await api.generatePlan({
        theme: theme.trim() || 'default',
        duration_days: durationDays,
        user_id: user.id,
        translation,
      })
      navigate(`/plans/${plan.id}`)
    } catch (err) {
      setError(err.message || 'Could not create plan')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="create-plan">
      <h1 className="create-plan-title">New plan</h1>
      <p className="create-plan-subtitle">
        Pick a theme and length. Verses are fetched from the Bible (bible-api.com).
      </p>
      <form onSubmit={handleSubmit} className="create-plan-form">
        {error && <p className="create-plan-error">{error}</p>}
        <label>
          Theme
          <input
            type="text"
            value={theme}
            onChange={(e) => setTheme(e.target.value)}
            placeholder="e.g. Peace, Defending your faith, Hope"
          />
        </label>
        <label>
          Days
          <input
            type="number"
            min={1}
            max={90}
            value={durationDays}
            onChange={(e) => setDurationDays(Number(e.target.value) || 7)}
          />
        </label>
        <label>
          Translation
          <select
            value={translation}
            onChange={(e) => setTranslation(e.target.value)}
          >
            {TRANSLATIONS.map((t) => (
              <option key={t.value} value={t.value}>
                {t.label}
              </option>
            ))}
          </select>
        </label>
        <button type="submit" className="create-plan-submit" disabled={loading}>
          {loading ? 'Creating plan…' : 'Create plan'}
        </button>
      </form>
    </div>
  )
}
