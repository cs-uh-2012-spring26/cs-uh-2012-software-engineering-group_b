import { useEffect, useMemo, useState } from 'react'
import client from '../api/client'

const DEFAULT_PREFERENCES = {
  email: true,
  telegram: false,
}

export default function SettingsPage() {
  const [preferences, setPreferences] = useState(DEFAULT_PREFERENCES)
  const [savedPreferences, setSavedPreferences] = useState(DEFAULT_PREFERENCES)
  const [loadingCurrent, setLoadingCurrent] = useState(true)
  const [saving, setSaving] = useState(false)
  const [startingLink, setStartingLink] = useState(false)
  const [deepLink, setDeepLink] = useState('')
  const [telegramChatId, setTelegramChatId] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const hasUnsavedChanges = useMemo(
    () =>
      preferences.email !== savedPreferences.email ||
      preferences.telegram !== savedPreferences.telegram,
    [preferences, savedPreferences],
  )
  const canGenerateTelegramLink = savedPreferences.telegram && !hasUnsavedChanges

  useEffect(() => {
    let mounted = true
    async function loadCurrentPreferences() {
      setLoadingCurrent(true)
      setError('')
      try {
        const res = await client.get('/auth/notification-preferences')
        const current = {
          email: Boolean(res.data?.notification_preferences?.email ?? true),
          telegram: Boolean(res.data?.notification_preferences?.telegram ?? false),
        }
        if (!mounted) return
        setPreferences(current)
        setSavedPreferences(current)
        setTelegramChatId(res.data?.telegram_chat_id || '')
      } catch (err) {
        if (!mounted) return
        setError(err.response?.data?.message || err.message || 'Failed to load notification preferences.')
      } finally {
        if (mounted) setLoadingCurrent(false)
      }
    }
    loadCurrentPreferences()
    return () => {
      mounted = false
    }
  }, [])

  function handleToggle(channel) {
    setPreferences((prev) => ({ ...prev, [channel]: !prev[channel] }))
    setDeepLink('')
    setError('')
    setSuccess('')
  }

  async function handleSave(e) {
    e.preventDefault()
    setSaving(true)
    setError('')
    setSuccess('')

    try {
      const res = await client.post('/auth/notification-preferences', {
        notification_preferences: preferences,
      })
      const updated = {
        email: Boolean(res.data?.notification_preferences?.email ?? preferences.email),
        telegram: Boolean(res.data?.notification_preferences?.telegram ?? preferences.telegram),
      }
      setPreferences(updated)
      setSavedPreferences(updated)
      setTelegramChatId(res.data.telegram_chat_id || '')
      if (!updated.telegram) setDeepLink('')
      setSuccess('Notification preferences saved.')
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Failed to save notification preferences.')
    } finally {
      setSaving(false)
    }
  }

  async function handleStartTelegramLink() {
    if (!canGenerateTelegramLink) return
    setStartingLink(true)
    setError('')
    setSuccess('')

    try {
      const res = await client.post('/auth/telegram-link/start')
      const link = res.data.deep_link || ''
      setDeepLink(link)
      if (!link) {
        throw new Error('Telegram deep link was not returned by the server.')
      }
      setSuccess('Telegram link generated. Open it and press Start in Telegram.')
    } catch (err) {
      setError(err.response?.data?.message || err.message || 'Failed to generate Telegram link.')
    } finally {
      setStartingLink(false)
    }
  }

  return (
    <div className="page">
      <div className="page-header">
        <h2>Notification Settings</h2>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {success && <div className="alert alert-success">{success}</div>}
      {loadingCurrent && <div className="loading">Loading settings…</div>}

      <form className="form-card settings-card" onSubmit={handleSave} aria-busy={loadingCurrent}>
        <div className="settings-row">
          <div>
            <h3>Email reminders</h3>
            <p className="settings-help">Receive class reminders in your email inbox.</p>
          </div>
          <label className="switch">
            <input
              type="checkbox"
              checked={preferences.email}
              onChange={() => handleToggle('email')}
            />
            <span className="slider" />
          </label>
        </div>

        <div className="settings-row">
          <div>
            <h3>Telegram reminders</h3>
            <p className="settings-help">Receive class reminders through Telegram.</p>
          </div>
          <label className="switch">
            <input
              type="checkbox"
              checked={preferences.telegram}
              onChange={() => handleToggle('telegram')}
            />
            <span className="slider" />
          </label>
        </div>

        <button className="btn-primary" type="submit" disabled={saving}>
          {saving ? 'Saving…' : 'Save preferences'}
        </button>
        {hasUnsavedChanges && (
          <p className="settings-help" style={{ marginTop: 8 }}>
            You have unsaved changes.
          </p>
        )}
      </form>

      {preferences.telegram && (
        <div className="form-card settings-card">
          <h3>Telegram Configuration</h3>
          <p className="settings-help">
            Link your Telegram account to receive messages from the bot.
          </p>
          <button
            className="btn-action"
            onClick={handleStartTelegramLink}
            disabled={startingLink || !canGenerateTelegramLink}
          >
            {startingLink ? 'Generating link…' : 'Generate Telegram link'}
          </button>
          {savedPreferences.telegram && hasUnsavedChanges && (
            <p className="settings-help" style={{ marginTop: 8 }}>
              Save your updated preferences before generating a new one-time link.
            </p>
          )}

          {deepLink && (
            <p className="settings-help" style={{ marginTop: 12 }}>
              <a href={deepLink} target="_blank" rel="noreferrer" style={{ color: '#1a73e8' }}>
                Open Telegram deep link
              </a>
            </p>
          )}

          <p className="settings-help" style={{ marginTop: 8 }}>
            After opening the link, press <strong>Start</strong> in Telegram.
          </p>
          {telegramChatId && (
            <p className="settings-help" style={{ marginTop: 8 }}>
              Linked chat ID: {telegramChatId}
            </p>
          )}
        </div>
      )}
    </div>
  )
}
