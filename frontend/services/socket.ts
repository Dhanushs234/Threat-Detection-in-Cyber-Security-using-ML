import { io, Socket } from 'socket.io-client'

// Backend WebSocket event payload types
export interface StatsUpdate {
  total_detections: number
  normal_count: number
  suspicious_count: number
  attack_count: number
  blocked_count: number
  total_time: number
  avg_time_per_detection: number
}

export interface DetectionEvent {
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

export interface BlockedEvent {
  timestamp: string
  detection_id: string
  src_ip: string
  reason: string
  severity: string
}

export interface DetectionsPerMinutePoint {
  time: string
  count: number
}

export interface DetectionsPerMinutePayload {
  detections_per_minute: DetectionsPerMinutePoint[]
}

// Event callback types
export type StatsUpdateCallback = (data: StatsUpdate) => void
export type DetectionEventCallback = (data: DetectionEvent) => void
export type BlockedEventCallback = (data: BlockedEvent) => void
export type DetectionsPerMinuteCallback = (data: DetectionsPerMinutePayload) => void

type ConnectionListener = (connected: boolean) => void

class SocketService {
  private socket: Socket | null = null
  private readonly BACKEND_URL = 'http://127.0.0.1:8000'
  private connectionListeners = new Set<ConnectionListener>()

  private notifyConnectionStatus(status: boolean): void {
    this.connectionListeners.forEach((listener) => {
      try {
        listener(status)
      } catch (error) {
        console.error('Connection listener error:', error)
      }
    })
  }

  /**
   * Initialize WebSocket connection
   * Should be called once on app load
   */
  connect(): void {
    if (this.socket?.connected) {
      console.log('Socket already connected')
      return
    }

    this.socket = io(this.BACKEND_URL, {
      path: '/socket.io',
      withCredentials: false,
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: 5,
      reconnectionDelay: 1000,
    })

    this.socket.on('connect', () => {
      console.log('✅ WebSocket connected')
      this.notifyConnectionStatus(true)
    })

    this.socket.on('disconnect', (reason) => {
      console.log('❌ WebSocket disconnected:', reason)
      this.notifyConnectionStatus(false)
    })

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error)
      this.notifyConnectionStatus(false)
    })
  }

  /**
   * Disconnect WebSocket
   * Should be called on app unmount
   */
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
      console.log('WebSocket disconnected')
      this.notifyConnectionStatus(false)
    }
  }

  /**
   * Check if socket is connected
   */
  isConnected(): boolean {
    return this.socket?.connected ?? false
  }

  /**
   * Subscribe to connection status changes
   */
  subscribeConnectionStatus(listener: ConnectionListener): () => void {
    this.connectionListeners.add(listener)
    listener(this.isConnected())
    return () => {
      this.connectionListeners.delete(listener)
    }
  }

  /**
   * Subscribe to stats updates
   */
  onStatsUpdate(callback: StatsUpdateCallback): void {
    if (!this.socket) {
      console.warn('Socket not initialized')
      return
    }

    this.socket.on('stats_update', (data: StatsUpdate) => {
      callback(data)
    })
  }

  /**
   * Subscribe to detection events
   */
  onDetectionEvent(callback: DetectionEventCallback): void {
    if (!this.socket) {
      console.warn('Socket not initialized')
      return
    }

    this.socket.on('detection_event', (data: DetectionEvent) => {
      callback(data)
    })
  }

  /**
   * Subscribe to blocked events
   */
  onBlockedEvent(callback: BlockedEventCallback): void {
    if (!this.socket) {
      console.warn('Socket not initialized')
      return
    }

    this.socket.on('blocked_event', (data: BlockedEvent) => {
      callback(data)
    })
  }

  onDetectionsPerMinuteUpdate(callback: DetectionsPerMinuteCallback): void {
    if (!this.socket) {
      console.warn('Socket not initialized')
      return
    }

    this.socket.on('detections_per_minute_update', (data: DetectionsPerMinutePayload) => {
      callback(data)
    })
  }

  /**
   * Unsubscribe from stats updates
   */
  offStatsUpdate(callback?: StatsUpdateCallback): void {
    if (!this.socket) return
    this.socket.off('stats_update', callback)
  }

  /**
   * Unsubscribe from detection events
   */
  offDetectionEvent(callback?: DetectionEventCallback): void {
    if (!this.socket) return
    this.socket.off('detection_event', callback)
  }

  /**
   * Unsubscribe from blocked events
   */
  offBlockedEvent(callback?: BlockedEventCallback): void {
    if (!this.socket) return
    this.socket.off('blocked_event', callback)
  }

  offDetectionsPerMinuteUpdate(callback?: DetectionsPerMinuteCallback): void {
    if (!this.socket) return
    this.socket.off('detections_per_minute_update', callback)
  }

  /**
   * Remove all event listeners
   */
  removeAllListeners(): void {
    if (!this.socket) return
    this.socket.removeAllListeners('stats_update')
    this.socket.removeAllListeners('detection_event')
    this.socket.removeAllListeners('blocked_event')
    this.socket.removeAllListeners('detections_per_minute_update')
  }
}

// Export singleton instance
export const socketService = new SocketService()
