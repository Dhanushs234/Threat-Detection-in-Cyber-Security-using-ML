import { motion } from 'framer-motion'
import { useDetectionStore } from '../../store/detectionStore'

export default function BlockedThreatTable() {
  const { blockedThreats } = useDetectionStore()

  const getSeverityColor = (severity: string) => {
    const severityLower = severity.toLowerCase()
    if (severityLower === 'high') return '#DC2626'
    if (severityLower === 'medium') return '#F59E0B'
    return '#22C55E'
  }

  return (
    <div 
      className="card p-6"
      style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)' }}
    >
      <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
        Blocked Threats
      </h3>
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead style={{ backgroundColor: 'var(--bg-panel)' }}>
            <tr>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>
                Timestamp
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>
                Detection ID
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>
                Source IP
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>
                Reason
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>
                Severity
              </th>
            </tr>
          </thead>
          <tbody className="divide-y" style={{ borderColor: 'var(--border)' }}>
            {blockedThreats.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-8 text-center text-sm" style={{ color: 'var(--text-muted)' }}>
                  No blocked threats yet.
                </td>
              </tr>
            ) : (
              blockedThreats.map((threat, index) => (
                <motion.tr
                  key={threat.detection_id}
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2, delay: index * 0.02 }}
                  className="hover:bg-gray-800/30 transition-colors"
                >
                  <td className="px-4 py-3 text-sm whitespace-nowrap" style={{ color: 'var(--text-muted)' }}>
                    {new Date(threat.timestamp).toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-sm font-mono" style={{ color: 'var(--text-primary)' }}>
                    {threat.detection_id}
                  </td>
                  <td className="px-4 py-3 text-sm font-mono" style={{ color: 'var(--text-primary)' }}>
                    {threat.src_ip}
                  </td>
                  <td className="px-4 py-3 text-sm" style={{ color: 'var(--text-muted)' }}>
                    {threat.reason}
                  </td>
                  <td className="px-4 py-3 text-sm">
                    <span 
                      className="px-2 py-1 rounded-full text-xs font-medium"
                      style={{ 
                        backgroundColor: `${getSeverityColor(threat.severity)}20`,
                        color: getSeverityColor(threat.severity)
                      }}
                    >
                      {threat.severity}
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
