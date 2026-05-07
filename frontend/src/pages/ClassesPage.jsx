import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import client from '../api/client'

function formatDate(dateStr) {
  if (!dateStr) return 'TBD'
  const d = new Date(dateStr)
  return d.toLocaleString(undefined, {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function ClassCard({ cls, onBook }) {
  const { user } = useAuth()
  const [msg, setMsg] = useState(null)
  const [booking, setBooking] = useState(false)
  const isFull = cls.available_spots === 0

  async function handleBook() {
    setBooking(true)
    setMsg(null)
    try {
      await onBook(cls.class_id)
      setMsg({ type: 'success', text: 'Booked successfully!' })
    } catch (err) {
      setMsg({ type: 'error', text: err.response?.data?.message || 'Booking failed.' })
    } finally {
      setBooking(false)
    }
  }

  return (
    <div className="class-card">
      <h3>{cls.title}</h3>
      <p className="meta">Trainer: {cls.trainer_name}</p>
      <p className="meta">{formatDate(cls.datetime)}</p>
      {cls.recurrence_type !== 'one_time' && (
        <p className="meta" style={{ textTransform: 'capitalize' }}>
          Recurrence: {cls.recurrence_type}
        </p>
      )}
      <div className={`spots${isFull ? ' full' : ''}`}>
        {isFull ? 'Full' : `${cls.available_spots} / ${cls.capacity} spots left`}
      </div>
      {user?.role === 'member' && (
        <>
          <button className="btn-book" onClick={handleBook} disabled={isFull || booking}>
            {booking ? 'Booking…' : isFull ? 'Full' : 'Book'}
          </button>
          {msg && <p className={`inline-msg ${msg.type}`}>{msg.text}</p>}
        </>
      )}
      {!user && (
        <p className="inline-msg" style={{ color: '#888', marginTop: 8 }}>
          <Link to="/login" style={{ color: '#1a73e8' }}>Login</Link> to book
        </p>
      )}
    </div>
  )
}

export default function ClassesPage() {
  const { user } = useAuth()
  const [classes, setClasses] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    client.get('/classes/')
      .then(res => setClasses(res.data.message || []))
      .catch(err => {
        const msg = err.response?.data?.message || err.message || 'Network error'
        setError(`Failed to load classes: ${msg}`)
      })
      .finally(() => setLoading(false))
  }, [])

  async function handleBook(classId) {
    await client.post('/bookings/', { class_id: classId })
    // Refresh available spots after booking
    const res = await client.get('/classes/')
    setClasses(res.data.message || [])
  }

  return (
    <div className="page">
      <div className="page-header">
        <h2>Fitness Classes</h2>
        {(user?.role === 'trainer' || user?.role === 'admin') && (
          <Link to="/classes/create" className="btn-action">+ Create Class</Link>
        )}
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {loading ? (
        <div className="loading">Loading classes…</div>
      ) : classes.length === 0 ? (
        <div className="empty-state">No classes available yet.</div>
      ) : (
        <div className="class-grid">
          {classes.map(cls => (
            <ClassCard key={cls.class_id} cls={cls} onBook={handleBook} />
          ))}
        </div>
      )}
    </div>
  )
}
