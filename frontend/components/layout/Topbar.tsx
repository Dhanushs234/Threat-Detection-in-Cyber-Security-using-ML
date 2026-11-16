import { useEffect, useMemo, useState } from 'react'
import { apiService } from '../../services/api'
import {
  ensureMonitoringSessionId,
  useDetectionStore,
  type DetectionLabel,
} from '../../store/detectionStore'

export default function Topbar() {
  const { monitoringStatus, setMonitoringStatus, latestDetectionStatus } = useDetectionStore()
  const [isLoading, setIsLoading] = useState(false)
  const [currentTimestamp, setCurrentTimestamp] = useState(() => new Date())
  const [systemStatus, setSystemStatus] = useState<DetectionLabel>('normal')
  const [isFading, setIsFading] = useState(true)

  useEffect(() => {
    const intervalId = setInterval(() => {
      setCurrentTimestamp(new Date())
    }, 1000)
    return () => clearInterval(intervalId)
  }, [])

  useEffect(() => {
    if (latestDetectionStatus.eventId === 0) {
      return
    }

    setSystemStatus(latestDetectionStatus.label)
    setIsFading(false)

    const timeoutId = window.setTimeout(() => {
      setIsFading(true)
    }, 5000)

    return () => {
      window.clearTimeout(timeoutId)
    }
  }, [latestDetectionStatus])

  async function handleToggleMonitoring() {
    if (isLoading) return

    console.log('Monitoring toggle button clicked', {
      currentMonitoringStatus: monitoringStatus,
      isLoading,
    })

    setIsLoading(true)
    try {
      if (monitoringStatus) {
        await apiService.stopMonitoring()
        setMonitoringStatus(false)
        console.log('⏹️ Monitoring stopped')
      } else {
        ensureMonitoringSessionId()
        await apiService.startMonitoring()
        setMonitoringStatus(true)
        console.log('✅ Monitoring started')
      }
    } catch (error) {
      console.error('Failed to toggle monitoring:', error)
      alert('Failed to update monitoring state. Please check backend connection.')
    } finally {
      setIsLoading(false)
    }
  }

  const buttonConfig = useMemo(
    () =>
      monitoringStatus
        ? {
            label: 'Stop Monitoring',
            className:
              'bg-red-600 hover:bg-red-700 text-white shadow-lg hover:shadow-red-600/50',
          }
        : {
            label: 'Start Monitoring',
            className:
              'bg-green-600 hover:bg-green-700 text-white shadow-lg hover:shadow-green-600/50',
          },
    [monitoringStatus],
  )

  const timeDisplay = formatTime(currentTimestamp)
  const dateDisplay = formatDate(currentTimestamp)

  return (
    <div
      className="h-16 border-b border-white/10 flex items-center justify-end px-5"
      style={{
        backgroundColor: 'var(--bg-panel)'
      }}
    >
      <div className="flex items-center gap-5 pr-3">
        <div className="top-bar-right flex items-center gap-3">
          <div className="status-indicator">
            <span className={`status-dot ${systemStatus} ${isFading ? 'idle' : ''}`} />
          </div>
          <div className="time-display flex flex-col leading-[1.2] items-end text-right" style={{ color: 'var(--text-muted)' }}>
            <span className="text-[0.9rem] font-medium text-white">{timeDisplay}</span>
            <span className="text-[0.75rem] text-white/70">{dateDisplay}</span>
          </div>
        </div>
        <button
          onClick={handleToggleMonitoring}
          disabled={isLoading}
          className={`px-4 py-2 rounded-md font-medium transition-all duration-200 ${buttonConfig.className} ${
            isLoading ? 'opacity-70 cursor-not-allowed' : ''
          }`}
          style={{
            minWidth: '160px',
          }}
        >
          {isLoading ? 'Processing…' : buttonConfig.label}
        </button>
      </div>
    </div>
  )
}

function formatTime(date: Date) {
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  const seconds = String(date.getSeconds()).padStart(2, '0')
  return `${hours}:${minutes}:${seconds}`
}

function formatDate(date: Date) {
  const day = String(date.getDate()).padStart(2, '0')
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const year = date.getFullYear()
  return `${day}-${month}-${year}`
}
