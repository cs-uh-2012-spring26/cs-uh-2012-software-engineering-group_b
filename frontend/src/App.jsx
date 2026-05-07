import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import Navbar from './components/Navbar'
import ProtectedRoute from './components/ProtectedRoute'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import ClassesPage from './pages/ClassesPage'
import CreateClassPage from './pages/CreateClassPage'

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Navbar />
        <Routes>
          <Route path="/" element={<Navigate to="/classes" replace />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/classes" element={<ClassesPage />} />
          <Route
            path="/classes/create"
            element={
              <ProtectedRoute roles={['trainer', 'admin']}>
                <CreateClassPage />
              </ProtectedRoute>
            }
          />
          <Route path="*" element={<Navigate to="/classes" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}
