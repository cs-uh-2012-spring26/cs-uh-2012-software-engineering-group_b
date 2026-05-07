import axios from 'axios'

// Always use relative URLs — the Vite proxy handles this in dev,
// and nginx proxy_pass handles this in production.
const client = axios.create({
  baseURL: '',
})

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export default client
