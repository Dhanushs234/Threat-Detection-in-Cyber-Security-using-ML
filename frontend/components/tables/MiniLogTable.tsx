import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { useDetectionStore } from '../../store/detectionStore'

export default function MiniLogTable() {
  const { detectionLogs } = useDetectionStore()
  const navigate = useNavigate()

  // Get last 5 detections
  const recentLogs = detectionLogs.slice(0, 5)

  const handleRowClick = () => {
    navigate('/monitoring')
  }

  const getLabelColor = (label: string) => {
    const labelLower = label.toLowerCase()
    if (labelLower === 'attack') return '#EF4444'
    if (labelLower === 'suspicious') return '#F59E0B'
    return '#22C55E'
  }

  return (
    <div 
      className="card p-6 h-full flex flex-col"
      style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)', minHeight: '280px' }}
    >
      <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
        Recent Detections
      </h3>
      <div className="overflow-hidden rounded-lg border flex-1" style={{ borderColor: 'var(--border)' }}>
        <table className="w-full">
          <thead style={{ backgroundColor: 'var(--bg-panel)' }}>
            <tr>
              <th 
                className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider"
                style={{ color: 'var(--text-muted)' }}
              >
                Source IP
              </th>
              <th 
                className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider"
                style={{ color: 'var(--text-muted)' }}
              >
                Label
              </th>
            </tr>
          </thead>
          <tbody className="divide-y" style={{ borderColor: 'var(--border)' }}>
            {recentLogs.length === 0 ? (
              <tr>
                <td 
                  colSpan={2} 
                  className="px-4 py-8 text-center text-sm"
                  style={{ color: 'var(--text-muted)' }}
                >
                  No detections yet. Start monitoring to see live data.
                </td>
              </tr>
            ) : (
              recentLogs.map((log, index) => (
                <motion.tr
                  key={log.detection_id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                  onClick={handleRowClick}
                  className="cursor-pointer hover:bg-gray-800/30 transition-colors"
                >
                  <td 
                    className="px-4 py-3 text-sm font-mono"
                    style={{ color: 'var(--text-primary)' }}
                  >
                    {log.src_ip}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    <span 
                      className="px-2 py-1 rounded-full text-xs font-medium"
                      style={{ 
                        backgroundColor: `${getLabelColor(log.label)}20`,
                        color: getLabelColor(log.label)
                      }}
                    >
                      {log.label}
                    </span>
                  </td>
                </motion.tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
