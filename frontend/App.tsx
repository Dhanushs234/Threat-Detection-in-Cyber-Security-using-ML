import { useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, useNavigate, useLocation } from 'react-router-dom'
import Sidebar from './components/layout/Sidebar'
import Topbar from './components/layout/Topbar'
import Footer from './components/layout/Footer'
import Dashboard from './pages/Dashboard'
import ThreatMonitoring from './pages/ThreatMonitoring'
import ManualDetection from './pages/ManualDetection'
import ModelMetrics from './pages/ModelMetrics'
import About from './pages/About'
import { socketService } from './services/socket'
import { apiService } from './services/api'
import {
  MONITORING_SESSION_ID_KEY,
  MONITORING_STORAGE_KEY,
  useDetectionStore,
} from './store/detectionStore'
import { NAV_ROUTES } from './constants/navigation'

function AppContent() {
  const {
    updateKpiStats,
    addDetectionLog,
    addBlockedThreat,
    updateSeverityDistribution,
    addTimelineBucket,
    setDetectionsPerMinute,
    setDetection,
    monitoringStatus,
  } = useDetectionStore()
  const navigate = useNavigate()
  const location = useLocation()

  useEffect(() => {
    if (!monitoringStatus) {
      return
    }

    let isMounted = true

    socketService.connect()

    socketService.onStatsUpdate(data => {
      updateKpiStats(data)
    })

    socketService.onDetectionEvent(data => {
      addDetectionLog(data)
      updateSeverityDistribution(data.severity)
      addTimelineBucket(data.label)

      const level = (() => {
        const labelLower = data.label?.toLowerCase()
        if (labelLower === 'attack' || labelLower === 'suspicious') {
          return labelLower
        }
        return 'normal'
      })()

      if (data.src_country && data.dst_country) {
        setDetection({
          src: data.src_country,
          dst: data.dst_country,
          level,
        })
      }
    })

    socketService.onBlockedEvent(data => {
      addBlockedThreat(data)
    })

    socketService.onDetectionsPerMinuteUpdate(payload => {
      setDetectionsPerMinute(payload.detections_per_minute)
    })

    const fetchInitialTrend = async () => {
      try {
        const data = await apiService.getDetectionsPerMinute()
        if (isMounted) {
          setDetectionsPerMinute(data)
        }
      } catch (error) {
        console.warn('Initial detections-per-minute unavailable:', error)
      }
    }

    fetchInitialTrend()

    return () => {
      isMounted = false
      socketService.removeAllListeners()
      socketService.disconnect()
    }
  }, [
    monitoringStatus,
    updateKpiStats,
    addDetectionLog,
    addBlockedThreat,
    updateSeverityDistribution,
    addTimelineBucket,
    setDetectionsPerMinute,
  ])

  useEffect(() => {
    if (typeof window === 'undefined') {
      return
    }

    const PENDING_RESET_KEY = 'pendingMonitoringReset'

    const markForReset = () => {
      sessionStorage.setItem(PENDING_RESET_KEY, 'true')
    }

    const handlePageShow = () => {
      const pendingReset = sessionStorage.getItem(PENDING_RESET_KEY) === 'true'
      if (!pendingReset) {
        return
      }

      const navEntry = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming | undefined
      const isReload = navEntry?.type === 'reload'

      if (!isReload) {
        sessionStorage.clear()
      }

      sessionStorage.removeItem(PENDING_RESET_KEY)
    }

    window.addEventListener('beforeunload', markForReset)
    window.addEventListener('pagehide', markForReset)
    window.addEventListener('pageshow', handlePageShow)

    return () => {
      window.removeEventListener('beforeunload', markForReset)
      window.removeEventListener('pagehide', markForReset)
      window.removeEventListener('pageshow', handlePageShow)
    }
  }, [])

  useEffect(() => {
    const shortcutRoutes: Record<string, string> = {
      '1': '/',
      '2': '/monitoring',
      '3': '/manual',
      '4': '/metrics',
      '5': '/about',
    }

    const handleKeyDown = (e: KeyboardEvent) => {
      if (
        e.target instanceof HTMLInputElement ||
        e.target instanceof HTMLTextAreaElement
      ) {
        return
      }

      if (!e.ctrlKey && !e.metaKey) {
        const shortcutTarget = shortcutRoutes[e.key]
        if (shortcutTarget) {
          e.preventDefault()
          navigate(shortcutTarget)
          return
        }
      }

      const currentIndex = NAV_ROUTES.indexOf(location.pathname)

      if (e.key === 'ArrowRight' && currentIndex >= 0 && currentIndex < NAV_ROUTES.length - 1) {
        navigate(NAV_ROUTES[currentIndex + 1])
      }

      if (e.key === 'ArrowLeft' && currentIndex > 0) {
        navigate(NAV_ROUTES[currentIndex - 1])
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [location.pathname, navigate])

  return (
    <div className="flex h-screen" style={{ backgroundColor: 'var(--bg-main)' }}>
      {/* Sidebar */}
      <Sidebar />
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Topbar */}
        <Topbar />
        
        {/* Page Content */}
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/monitoring" element={<ThreatMonitoring />} />
            <Route path="/manual" element={<ManualDetection />} />
            <Route path="/metrics" element={<ModelMetrics />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </main>

        {/* Footer */}
        <Footer />
      </div>
    </div>
  )
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  )
}

export default App
