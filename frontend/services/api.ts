// API service for backend communication
const API_BASE_URL = 'http://127.0.0.1:8000'

export interface ApiResponse<T = any> {
  status: string
  data?: T
  message?: string
}

class ApiService {
  /**
   * Start monitoring
   */
  async startMonitoring(): Promise<ApiResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/monitor/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('Failed to start monitoring:', error)
      throw error
    }
  }

  /**
   * Stop monitoring
   */
  async stopMonitoring(): Promise<ApiResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/monitor/stop`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('Failed to stop monitoring:', error)
      throw error
    }
  }

  /**
   * Get monitoring status
   */
  async getMonitoringStatus(): Promise<ApiResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/monitor/status`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('Failed to get monitoring status:', error)
      throw error
    }
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<ApiResponse> {
    try {
      const response = await fetch(`${API_BASE_URL}/health`)
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      return await response.json()
    } catch (error) {
      console.error('Health check failed:', error)
      throw error
    }
  }

  async getDetectionsPerMinute(limit = 12): Promise<{ time: string; count: number }[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/monitor/detections-per-minute?limit=${limit}`)

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data: { detections_per_minute: { time: string; count: number }[] } = await response.json()
      return data.detections_per_minute
    } catch (error) {
      console.error('Failed to fetch detections per minute:', error)
      throw error
    }
  }
}

export const apiService = new ApiService()
