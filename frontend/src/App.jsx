import { useState } from 'react'
import Dashboard from './pages/Dashboard'
import AnalyticsPage from './pages/Analytics'
import AboutPage from './pages/About'
import { Navbar } from './components/Navbar'
import './App.css'

const pages = {
  dashboard: <Dashboard />,
  analytics: <AnalyticsPage />,
  about: <AboutPage />,
}

export default function App() {
  const [activePage, setActivePage] = useState('dashboard')

  return (
    <div className="app-shell">
      <Navbar activePage={activePage} onNavigate={setActivePage} />
      {pages[activePage]}
    </div>
  )
}
