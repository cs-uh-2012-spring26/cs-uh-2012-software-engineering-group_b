import { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext(null)

function decodeJwtPayload(token) {
  try {
    const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/')
    return JSON.parse(atob(base64))
  } catch {
    return null
  }
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('token'))
  const [user, setUser] = useState(() => {
    const t = localStorage.getItem('token')
    if (!t) return null
    const payload = decodeJwtPayload(t)
    if (!payload) return null
    return {
      email: payload.sub,
      role: payload.role,
      userId: payload.user_id,
    }
  })

  function login(newToken) {
    const payload = decodeJwtPayload(newToken)
    if (!payload) return
    localStorage.setItem('token', newToken)
    setToken(newToken)
    setUser({
      email: payload.sub,
      role: payload.role,
      userId: payload.user_id,
    })
  }

  function logout() {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ token, user, login, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
