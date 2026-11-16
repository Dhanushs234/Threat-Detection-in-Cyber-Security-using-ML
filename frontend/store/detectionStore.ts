import { create } from 'zustand'
import { StatsUpdate, DetectionEvent, BlockedEvent } from '../services/socket'

export const MONITORING_STORAGE_KEY = 'isMonitoring'
export const MONITORING_SESSION_ID_KEY = 'sessionId'

const STORAGE_KEYS = {
  latestDetectionStatus: 'latestDetectionStatus',
  kpiStats: 'kpiStats',
  detectionLogs: 'detectionLogs',
  blockedThreats: 'blockedThreats',
  severityDistribution: 'severityDistribution',
  timelineBuckets: 'timelineBuckets',
  detectionsPerMinute: 'detectionsPerMinute',
  latestDetection: 'latestDetection',
}

const readSession = <T>(key: string, fallback: T): T => {
  if (typeof window === 'undefined') {
    return fallback
  }

  const raw = sessionStorage.getItem(key)
  if (!raw) {
    return fallback
  }

  try {
    return JSON.parse(raw) as T
  } catch (error) {
    console.warn(`Failed to parse sessionStorage key "${key}"`, error)
    return fallback
  }
}

const writeSession = (key: string, value: unknown) => {
  if (typeof window === 'undefined') {
    return
  }

  try {
    sessionStorage.setItem(key, JSON.stringify(value))
  } catch (error) {
    console.warn(`Failed to persist sessionStorage key "${key}"`, error)
  }
}

const removeSession = (key: string) => {
  if (typeof window === 'undefined') {
    return
  }

  sessionStorage.removeItem(key)
}

const getInitialMonitoringStatus = () => {
  if (typeof window === 'undefined') {
    return false
  }

  return sessionStorage.getItem(MONITORING_STORAGE_KEY) === 'true'
}

export const ensureMonitoringSessionId = () => {
  if (typeof window === 'undefined') {
    return null
  }

  let sessionId = sessionStorage.getItem(MONITORING_SESSION_ID_KEY)
  if (!sessionId) {
    const generator = window.crypto?.randomUUID?.bind(window.crypto)
    sessionId = generator ? generator() : `${Date.now()}-${Math.random()}`
    sessionStorage.setItem(MONITORING_SESSION_ID_KEY, sessionId)
  }

  return sessionId
}

export type DetectionLabel = 'normal' | 'suspicious' | 'attack'

export interface LatestDetectionStatus {
  label: DetectionLabel
  eventId: number
}

// State interfaces
export interface KpiStats {
  total_detections: number
  normal_count: number
  suspicious_count: number
  attack_count: number
  blocked_count: number
  total_time: number
  avg_time_per_detection: number
}

export interface DetectionLog {
  timestamp: string
  detection_id: string
  src_ip: string
  src_country: string
  dst_ip: string
  dst_country: string
  label: string
  severity: string
  hybrid_confidence: number
  risk_score: number
}

export interface ThreatMapDetection {
  src: string
  dst: string
  level: DetectionLabel
}

export interface BlockedThreat {
  timestamp: string
  detection_id: string
  src_ip: string
  reason: string
  severity: string
}

export interface SeverityDistribution {
  high: number
  medium: number
  low: number
}

export interface TimelineBucket {
  timestamp: string
  normal: number
  suspicious: number
  attack: number
}

export interface DetectionsPerMinutePoint {
  time: string
  count: number
}

// Store state
interface DetectionStore {
  // Monitoring status
  monitoringStatus: boolean

  // Latest detection label for status indicator
  latestDetectionStatus: LatestDetectionStatus

  // KPI statistics
  kpiStats: KpiStats

  // Detection logs (rolling, max 100)
  detectionLogs: DetectionLog[]

  // Blocked threats
  blockedThreats: BlockedThreat[]

  // Severity distribution
  severityDistribution: SeverityDistribution

  // Timeline buckets (for charts)
  timelineBuckets: TimelineBucket[]

  // Detections per minute (mini trend)
  detectionsPerMinute: DetectionsPerMinutePoint[]

  // Latest detection for threat map
  latestDetection: ThreatMapDetection | null

  // Actions
  setMonitoringStatus: (status: boolean) => void
  updateKpiStats: (stats: StatsUpdate) => void
  addDetectionLog: (detection: DetectionEvent) => void
  addBlockedThreat: (blocked: BlockedEvent) => void
  updateSeverityDistribution: (severity: string) => void
  addTimelineBucket: (label: string) => void
  setDetectionsPerMinute: (series: DetectionsPerMinutePoint[]) => void
  setDetection: (detection: ThreatMapDetection | null) => void
  resetStore: () => void
}

// Initial state
const defaultLatestDetectionStatus: LatestDetectionStatus = {
  label: 'normal',
  eventId: 0,
}

const defaultKpiStats: KpiStats = {
  total_detections: 0,
  normal_count: 0,
  suspicious_count: 0,
  attack_count: 0,
  blocked_count: 0,
  total_time: 0,
  avg_time_per_detection: 0,
}

const defaultSeverityDistribution: SeverityDistribution = {
  high: 0,
  medium: 0,
  low: 0,
}

const initialState = {
  monitoringStatus: getInitialMonitoringStatus(),
  latestDetectionStatus: readSession<LatestDetectionStatus>(
    STORAGE_KEYS.latestDetectionStatus,
    defaultLatestDetectionStatus,
  ),
  kpiStats: readSession<KpiStats>(STORAGE_KEYS.kpiStats, defaultKpiStats),
  detectionLogs: readSession<DetectionLog[]>(STORAGE_KEYS.detectionLogs, []),
  blockedThreats: readSession<BlockedThreat[]>(STORAGE_KEYS.blockedThreats, []),
  severityDistribution: readSession<SeverityDistribution>(
    STORAGE_KEYS.severityDistribution,
    defaultSeverityDistribution,
  ),
  timelineBuckets: readSession<TimelineBucket[]>(STORAGE_KEYS.timelineBuckets, []),
  detectionsPerMinute: readSession<DetectionsPerMinutePoint[]>(
    STORAGE_KEYS.detectionsPerMinute,
    [],
  ),
  latestDetection: readSession<ThreatMapDetection | null>(
    STORAGE_KEYS.latestDetection,
    null,
  ),
}

// Create store
export const useDetectionStore = create<DetectionStore>((set) => ({
  ...initialState,

  // Set monitoring status
  setMonitoringStatus: (status) =>
    set(() => {
      if (typeof window !== 'undefined') {
        sessionStorage.setItem(MONITORING_STORAGE_KEY, String(status))
        if (status) {
          ensureMonitoringSessionId()
        }
      }

      return { monitoringStatus: status }
    }),

  // Update KPI stats from WebSocket
  updateKpiStats: (stats) =>
    set(() => {
      writeSession(STORAGE_KEYS.kpiStats, stats)
      return { kpiStats: stats }
    }),

  // Add detection log (rolling, max 100)
  addDetectionLog: (detection) =>
    set((state) => {
      const detectionLogs = [detection, ...state.detectionLogs].slice(0, 100)

      const labelLower = detection.label?.toLowerCase() ?? 'normal'
      const normalizedLabel: DetectionLabel =
        labelLower === 'attack' || labelLower === 'suspicious' ? (labelLower as DetectionLabel) : 'normal'

      const latestDetectionStatus: LatestDetectionStatus = {
        label: normalizedLabel,
        eventId: state.latestDetectionStatus.eventId + 1,
      }

      const latestDetection: ThreatMapDetection = {
        src: detection.src_country,
        dst: detection.dst_country,
        level: normalizedLabel,
      }

      writeSession(STORAGE_KEYS.detectionLogs, detectionLogs)
      writeSession(STORAGE_KEYS.latestDetectionStatus, latestDetectionStatus)
      writeSession(STORAGE_KEYS.latestDetection, latestDetection)

      return {
        detectionLogs,
        latestDetectionStatus,
        latestDetection,
      }
    }),

  // Add blocked threat
  addBlockedThreat: (blocked) =>
    set((state) => {
      const blockedThreats = [blocked, ...state.blockedThreats]
      writeSession(STORAGE_KEYS.blockedThreats, blockedThreats)
      return { blockedThreats }
    }),

  // Update severity distribution
  updateSeverityDistribution: (severity) =>
    set((state) => {
      const newDistribution = { ...state.severityDistribution }
      const severityLower = severity.toLowerCase()

      if (severityLower === 'high') {
        newDistribution.high += 1
      } else if (severityLower === 'medium') {
        newDistribution.medium += 1
      } else if (severityLower === 'low') {
        newDistribution.low += 1
      }

      writeSession(STORAGE_KEYS.severityDistribution, newDistribution)

      return { severityDistribution: newDistribution }
    }),

  setDetectionsPerMinute: (series) =>
    set(() => {
      writeSession(STORAGE_KEYS.detectionsPerMinute, series)
      return { detectionsPerMinute: series }
    }),

  setDetection: (detection) =>
    set(() => {
      writeSession(STORAGE_KEYS.latestDetection, detection)
      return { latestDetection: detection }
    }),

  // Add timeline bucket
  addTimelineBucket: (label) =>
    set((state) => {
      const now = new Date().toISOString()
      const lastBucket = state.timelineBuckets[state.timelineBuckets.length - 1]
      
      // Create new bucket or update existing
      if (!lastBucket || new Date(now).getTime() - new Date(lastBucket.timestamp).getTime() > 60000) {
        // New bucket (1 minute interval)
        const newBucket: TimelineBucket = {
          timestamp: now,
          normal: label.toLowerCase() === 'normal' ? 1 : 0,
          suspicious: label.toLowerCase() === 'suspicious' ? 1 : 0,
          attack: label.toLowerCase() === 'attack' ? 1 : 0,
        }
        const timelineBuckets = [...state.timelineBuckets, newBucket].slice(-30)
        writeSession(STORAGE_KEYS.timelineBuckets, timelineBuckets)
        return {
          timelineBuckets,
        }
      } else {
        // Update existing bucket
        const updatedBuckets = [...state.timelineBuckets]
        const last = updatedBuckets[updatedBuckets.length - 1]
        
        if (label.toLowerCase() === 'normal') last.normal += 1
        if (label.toLowerCase() === 'suspicious') last.suspicious += 1
        if (label.toLowerCase() === 'attack') last.attack += 1
        
        writeSession(STORAGE_KEYS.timelineBuckets, updatedBuckets)

        return { timelineBuckets: updatedBuckets }
      }
    }),

  // Reset store
  resetStore: () =>
    set(() => {
      if (typeof window !== 'undefined') {
        sessionStorage.setItem(MONITORING_STORAGE_KEY, 'false')
        Object.values(STORAGE_KEYS).forEach((key) => removeSession(key))
      }
      return initialState
    }),
}))
