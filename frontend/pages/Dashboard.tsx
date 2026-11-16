import { useEffect, useRef, useState } from 'react'
import { 
  ChartBarIcon, 
  CheckCircleIcon, 
  ExclamationTriangleIcon, 
  ShieldExclamationIcon,
  NoSymbolIcon,
} from '@heroicons/react/24/outline'
import { useDetectionStore } from '../store/detectionStore'
import KpiCard from '../components/kpi/KpiCard'
import StackedTimeline from '../components/charts/StackedTimeline'
import SeverityPie from '../components/charts/SeverityPie'
import MiniDetectionTrend from '../components/charts/MiniDetectionTrend'
import MiniLogTable from '../components/tables/MiniLogTable'
import AttackSourceIPs from '../components/tables/AttackSourceIPs'
import ThreatMap from '../components/ThreatMap'

export default function Dashboard() {
  const { 
    kpiStats, 
    updateKpiStats, 
    latestDetectionStatus,
    latestDetection,
  } = useDetectionStore()

  const [attackGlow, setAttackGlow] = useState(false)
  const glowTimeoutRef = useRef<number | null>(null)
  const { label: latestLabel, eventId: latestEventId } = latestDetectionStatus

  useEffect(() => {
    let isMounted = true

    const fetchInitialStats = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/monitor/stats')
        if (!response.ok) {
          throw new Error(`Stats fetch failed with status ${response.status}`)
        }
        const data: {
          total_detections: number
          normal_count: number
          suspicious_count: number
          attack_count: number
          blocked_count: number
          total_time: number
          avg_time_per_detection: number
        } = await response.json()

        if (isMounted) {
          updateKpiStats(data)
        }
      } catch (error) {
        console.warn('Initial KPI stats unavailable:', error)
      }
    }

    fetchInitialStats()

    return () => {
      isMounted = false
    }
  }, [updateKpiStats])

  useEffect(() => {
    if (latestLabel === 'attack') {
      setAttackGlow(true)

      if (glowTimeoutRef.current) {
        window.clearTimeout(glowTimeoutRef.current)
      }

      glowTimeoutRef.current = window.setTimeout(() => {
        setAttackGlow(false)
        glowTimeoutRef.current = null
      }, 2000)
    }

    // no cleanup function here to prevent cancelling fade on non-attack updates
  }, [latestLabel, latestEventId])

  useEffect(() => {
    return () => {
      if (glowTimeoutRef.current) {
        window.clearTimeout(glowTimeoutRef.current)
        glowTimeoutRef.current = null
      }
    }
  }, [])

  return (
    <div className="min-h-screen p-8" style={{ backgroundColor: 'var(--bg-main)' }}>
      <div className={`dashboard-content ${attackGlow ? 'attack-glow' : ''} p-6`}>
        <div className="mb-6">
          <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
            Dashboard
          </h1>
        </div>

        {/* KPI Cards Grid */}
        <div className="grid grid-cols-5 gap-4 mb-8">
          <KpiCard
            title="Total Detections"
            value={kpiStats.total_detections}
            icon={<ChartBarIcon className="w-7 h-7 text-slate-300" />}
            containerClass="bg-slate-800 text-white"
            labelClass="text-slate-300"
            valueClass="text-white"
          />
          <KpiCard
            title="Normal"
            value={kpiStats.normal_count}
            icon={<CheckCircleIcon className="w-7 h-7 text-green-300" />}
            containerClass="bg-green-900 text-white"
            labelClass="text-green-300"
            valueClass="text-white"
          />
          <KpiCard
            title="Suspicious"
            value={kpiStats.suspicious_count}
            icon={<ExclamationTriangleIcon className="w-7 h-7 text-yellow-300" />}
            containerClass="bg-yellow-900 text-white"
            labelClass="text-yellow-300"
            valueClass="text-white"
          />
          <KpiCard
            title="Attack"
            value={kpiStats.attack_count}
            icon={<ShieldExclamationIcon className="w-7 h-7 text-red-300" />}
            containerClass="bg-red-900 text-white"
            labelClass="text-red-300"
            valueClass="text-white"
          />
          <KpiCard
            title="Blocked"
            value={kpiStats.blocked_count}
            icon={<NoSymbolIcon className="w-7 h-7 text-purple-300" />}
            containerClass="bg-purple-900 text-white"
            labelClass="text-purple-300"
            valueClass="text-white"
          />
        </div>

        {/* Charts Section */}
        <div className="dashboard-middle mb-8">
          <StackedTimeline />
          <SeverityPie />
          <MiniDetectionTrend />
        </div>

        {/* Recent + Attack Panels */}
        <div
          className="grid gap-4 mb-8"
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(2, minmax(0, 1fr))',
            alignItems: 'stretch',
          }}
        >
          <MiniLogTable />
          <AttackSourceIPs />
        </div>

        <ThreatMap detection={latestDetection ?? undefined} />
      </div>
    </div>
  )
}
