import { create } from 'zustand'
import { apiService } from '../services/api'
import { ensureMonitoringSessionId, useDetectionStore } from './detectionStore'

interface MonitoringStore {
  monitoring: boolean
  startMonitoring: () => Promise<void>
  stopMonitoring: () => Promise<void>
}

export const useMonitoringStore = create<MonitoringStore>((set) => {
  const syncMonitoringState = (monitoringStatus: boolean) => {
    set({ monitoring: monitoringStatus })
  }

  syncMonitoringState(useDetectionStore.getState().monitoringStatus)

  useDetectionStore.subscribe((state) => {
    syncMonitoringState(state.monitoringStatus)
  })

  return {
    monitoring: useDetectionStore.getState().monitoringStatus,
    startMonitoring: async () => {
      const { setMonitoringStatus, monitoringStatus } = useDetectionStore.getState()
      if (monitoringStatus) return

      try {
        ensureMonitoringSessionId()
        await apiService.startMonitoring()
        setMonitoringStatus(true)
        syncMonitoringState(true)
      } catch (error) {
        console.error('Failed to start monitoring via shortcut:', error)
      }
    },
    stopMonitoring: async () => {
      const { setMonitoringStatus, monitoringStatus } = useDetectionStore.getState()
      if (!monitoringStatus) return

      try {
        await apiService.stopMonitoring()
        setMonitoringStatus(false)
        syncMonitoringState(false)
      } catch (error) {
        console.error('Failed to stop monitoring via shortcut:', error)
      }
    },
  }
})
