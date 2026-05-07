import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import client from '../api/client'

export default function RegisterPage() {
  const { login } = useAuth()
  const navigate = useNavigate()

  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    invite_token: '',
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  function handleChange(e) {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)

    const payload = { name: form.name, email: form.email, password: form.password }
    if (form.invite_token.trim()) {
      payload.token = form.invite_token.trim()
    }

    try {
      const res = await client.post('/auth/register', payload)
      login(res.data.access_token)
      navigate('/classes')
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Registration failed.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="form-card">
      <h2>Create Account</h2>
      {error && <div className="alert alert-error">{error}</div>}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label>Name</label>
          <input
            type="text"
            name="name"
            value={form.name}
            onChange={handleChange}
            required
            autoFocus
          />
        </div>
        <div className="form-group">
          <label>Email</label>
          <input
            type="email"
            name="email"
            value={form.email}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label>Password</label>
          <input
            type="password"
            name="password"
            value={form.password}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <label>Invite Token <span style={{ fontWeight: 400, color: '#888' }}>(optional — for trainer/admin)</span></label>
          <input
            type="text"
            name="invite_token"
            value={form.invite_token}
            onChange={handleChange}
            placeholder="Leave blank to register as member"
          />
        </div>
        <button className="btn-primary" type="submit" disabled={loading}>
          {loading ? 'Registering…' : 'Register'}
        </button>
      </form>
      <p className="form-footer">
        Already have an account? <Link to="/login">Login</Link>
      </p>
    </div>
  )
}
