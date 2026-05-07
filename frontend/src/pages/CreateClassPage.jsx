import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import client from '../api/client'

export default function CreateClassPage() {
  const navigate = useNavigate()

  const [form, setForm] = useState({
    title: '',
    datetime: '',
    capacity: '',
    trainer_name: '',
    recurrence_type: 'one_time',
    recurrence_end_date: '',
  })
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setSuccess('')
    setLoading(true)

    const payload = {
      title: form.title,
      datetime: new Date(form.datetime).toISOString(),
      capacity: parseInt(form.capacity, 10),
      trainer_name: form.trainer_name,
      recurrence_type: form.recurrence_type,
    }

    if (form.recurrence_type !== 'one_time' && form.recurrence_end_date) {
      payload.recurrence_end_date = form.recurrence_end_date
    }

    try {
      await client.post('/classes/', payload)
      setSuccess('Class created successfully!')
      setTimeout(() => navigate('/classes'), 1200)
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create class.')
    } finally {
      setLoading(false)
    }
  }

  const isRecurring = form.recurrence_type !== 'one_time'

  return (
    <div className="form-card" style={{ maxWidth: 500 }}>
      <h2>Create Fitness Class</h2>
      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Class Title</label>
          <input
            type="text"
            name="title"
            value={form.title}
            onChange={handleChange}
            required
            autoFocus
            placeholder="e.g. Morning Yoga"
          />
        </div>
        <div className="form-group">
          <label>Trainer Name</label>
          <input
            type="text"
            name="trainer_name"
            value={form.trainer_name}
            onChange={handleChange}
            required
            placeholder="e.g. Jane Smith"
          />
        </div>
        <div className="form-group">
          <label>Date &amp; Time</label>
          <input
            type="datetime-local"
            name="datetime"
            value={form.datetime}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label>Capacity</label>
          <input
            type="number"
            name="capacity"
            value={form.capacity}
            onChange={handleChange}
            required
            min="1"
            placeholder="e.g. 20"
          />
        </div>
        <div className="form-group">
          <label>Recurrence</label>
          <select name="recurrence_type" value={form.recurrence_type} onChange={handleChange}>
            <option value="one_time">One-time</option>
            <option value="daily">Daily</option>
            <option value="weekly">Weekly</option>
            <option value="monthly">Monthly</option>
          </select>
        </div>
        {isRecurring && (
          <div className="form-group">
            <label>Recurrence End Date</label>
            <input
              type="date"
              name="recurrence_end_date"
              value={form.recurrence_end_date}
              onChange={handleChange}
              required={isRecurring}
            />
          </div>
        )}
        <button className="btn-primary" type="submit" disabled={loading}>
          {loading ? 'Creating…' : 'Create Class'}
        </button>
      </form>
    </div>
  )
}
