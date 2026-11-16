import { useState } from 'react'
import { motion } from 'framer-motion'
import DetectionLogTable from '../components/tables/DetectionLogTable'
import BlockedThreatTable from '../components/tables/BlockedThreatTable'

type ViewMode = 'detections' | 'blocked'

export default function ThreatMonitoring() {
  const [viewMode, setViewMode] = useState<ViewMode>('detections')

  return (
    <div className="min-h-screen p-8" style={{ backgroundColor: 'var(--bg-main)' }}>
      <div className="mb-6">
        <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
          Threat Management
        </h1>
      </div>

      {/* Toggle View Buttons */}
      <div className="flex gap-3 mb-6">
        <button
          onClick={() => setViewMode('detections')}
          className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
            viewMode === 'detections'
              ? 'bg-blue-600 text-white shadow-lg'
              : 'bg-gray-800/50 hover:bg-gray-800'
          }`}
          style={{
            color: viewMode === 'detections' ? '#ffffff' : 'var(--text-muted)',
          }}
        >
          Detection Logs
        </button>
        <button
          onClick={() => setViewMode('blocked')}
          className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 ${
            viewMode === 'blocked'
              ? 'bg-blue-600 text-white shadow-lg'
              : 'bg-gray-800/50 hover:bg-gray-800'
          }`}
          style={{
            color: viewMode === 'blocked' ? '#ffffff' : 'var(--text-muted)',
          }}
        >
          Blocked Threats
        </button>
      </div>

      {/* Table View with Smooth Transition */}
      <motion.div
        key={viewMode}
        initial={{ opacity: 0, x: 20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ duration: 0.3 }}
      >
        {viewMode === 'detections' ? <DetectionLogTable /> : <BlockedThreatTable />}
      </motion.div>
    </div>
  )
}
