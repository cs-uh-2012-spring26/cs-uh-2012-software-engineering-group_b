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

function extractMessageList(res) {
  if (Array.isArray(res?.data)) return res.data
  if (Array.isArray(res?.data?.message)) return res.data.message
  if (Array.isArray(res?.data?.classes)) return res.data.classes
  return []
}

function ClassCard({ cls, onBook, onSendReminder, onViewBookings }) {
  const { user } = useAuth()
  const [msg, setMsg] = useState(null)
  const [booking, setBooking] = useState(false)
  const [sendingReminder, setSendingReminder] = useState(false)
  const [loadingBookings, setLoadingBookings] = useState(false)
  const [bookingsOpen, setBookingsOpen] = useState(false)
  const [bookings, setBookings] = useState([])
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

  async function handleReminder() {
    setSendingReminder(true)
    setMsg(null)
    try {
      const res = await onSendReminder(cls.class_id)
      const sentCount = res?.sent_count ?? 0
      setMsg({ type: 'success', text: `Reminder sent to ${sentCount} attendee(s).` })
    } catch (err) {
      setMsg({ type: 'error', text: err.response?.data?.message || 'Failed to send reminders.' })
    } finally {
      setSendingReminder(false)
    }
  }

  async function handleToggleBookings() {
    if (!bookingsOpen && bookings.length === 0) {
      setLoadingBookings(true)
      setMsg(null)
      try {
        const result = await onViewBookings(cls.class_id)
        setBookings(result)
      } catch (err) {
        setMsg({ type: 'error', text: err.response?.data?.message || 'Failed to load bookings.' })
      } finally {
        setLoadingBookings(false)
      }
    }
    setBookingsOpen((prev) => !prev)
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
        </>
      )}
      {(user?.role === 'trainer' || user?.role === 'admin') && (
        <div className="trainer-actions">
          <button className="btn-book" onClick={handleToggleBookings} disabled={loadingBookings}>
            {loadingBookings ? 'Loading bookings…' : bookingsOpen ? 'Hide bookings' : 'View bookings'}
          </button>
          {user?.role === 'trainer' && (
            <button className="btn-reminder" onClick={handleReminder} disabled={sendingReminder}>
              {sendingReminder ? 'Sending reminders…' : 'Send reminders'}
            </button>
          )}
        </div>
      )}
      {bookingsOpen && (user?.role === 'trainer' || user?.role === 'admin') && (
        <div className="booking-list">
          {bookings.length === 0 ? (
            <p className="inline-msg" style={{ color: '#666' }}>No bookings yet.</p>
          ) : (
            bookings.map((bookingItem) => (
              <p key={bookingItem.booking_id || bookingItem.user_id} className="inline-msg">
                {bookingItem.user_name} ({bookingItem.user_email})
              </p>
            ))
          )}
        </div>
      )}
      {msg && <p className={`inline-msg ${msg.type}`}>{msg.text}</p>}
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
  const [refreshing, setRefreshing] = useState(false)
  const [error, setError] = useState('')

  async function loadClasses(showRefreshState = false) {
    if (showRefreshState) setRefreshing(true)
    try {
      const res = await client.get('/classes/')
      setClasses(extractMessageList(res))
      setError('')
    } catch (err) {
      const msg = err.response?.data?.message || err.message || 'Network error'
      setError(`Failed to load classes: ${msg}`)
    } finally {
      setLoading(false)
      if (showRefreshState) setRefreshing(false)
    }
  }

  useEffect(() => {
    loadClasses(false)
  }, [])

  async function handleBook(classId) {
    await client.post('/bookings/', { class_id: classId })
    await loadClasses(true)
  }

  async function handleSendReminder(classId) {
    const res = await client.post(`/classes/${classId}/reminders`)
    return res.data
  }

  async function handleViewBookings(classId) {
    const res = await client.get(`/bookings/class/${classId}`)
    return extractMessageList(res)
  }

  return (
    <div className="page">
      <div className="page-header">
        <h2>Fitness Classes</h2>
        <div style={{ display: 'flex', gap: 8 }}>
          <button className="btn-action" onClick={() => loadClasses(true)} disabled={refreshing}>
            {refreshing ? 'Refreshing…' : 'Refresh'}
          </button>
          {(user?.role === 'trainer' || user?.role === 'admin') && (
            <Link to="/classes/create" className="btn-action">+ Create Class</Link>
          )}
        </div>
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {loading ? (
        <div className="loading">Loading classes…</div>
      ) : classes.length === 0 ? (
        <div className="empty-state">No classes available yet.</div>
      ) : (
        <div className="class-grid">
          {classes.map(cls => (
            <ClassCard
              key={cls.class_id}
              cls={cls}
              onBook={handleBook}
              onSendReminder={handleSendReminder}
              onViewBookings={handleViewBookings}
            />
          ))}
        </div>
      )}
    </div>
  )
}
