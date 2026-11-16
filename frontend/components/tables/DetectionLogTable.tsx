import { motion } from 'framer-motion'
import { useDetectionStore } from '../../store/detectionStore'

export default function DetectionLogTable() {
  const { detectionLogs } = useDetectionStore()

  const getLabelColor = (label: string) => {
    const labelLower = label.toLowerCase()
    if (labelLower === 'attack') return '#EF4444'
    if (labelLower === 'suspicious') return '#F59E0B'
    return '#22C55E'
  }

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
        Detection Logs
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
                Src IP
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>
                Src Country
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>
                Dst IP
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>
                Dst Country
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>
                Label
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>
                Severity
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>
                Confidence
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium uppercase tracking-wider" style={{ color: 'var(--text-muted)' }}>
                Risk Score
              </th>
            </tr>
          </thead>
          <tbody className="divide-y" style={{ borderColor: 'var(--border)' }}>
            {detectionLogs.length === 0 ? (
              <tr>
                <td colSpan={10} className="px-4 py-8 text-center text-sm" style={{ color: 'var(--text-muted)' }}>
                  No detections yet. Start monitoring to see live data.
                </td>
              </tr>
            ) : (
              detectionLogs.map((log, index) => (
                <motion.tr
                  key={log.detection_id}
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2, delay: index * 0.02 }}
                  className="hover:bg-gray-800/30 transition-colors"
                >
                  <td className="px-4 py-3 text-sm whitespace-nowrap" style={{ color: 'var(--text-muted)' }}>
                    {new Date(log.timestamp).toLocaleString()}
                  </td>
                  <td className="px-4 py-3 text-sm font-mono" style={{ color: 'var(--text-primary)' }}>
                    {log.detection_id}
                  </td>
                  <td className="px-4 py-3 text-sm font-mono" style={{ color: 'var(--text-primary)' }}>
                    {log.src_ip}
                  </td>
                  <td className="px-4 py-3 text-sm" style={{ color: 'var(--text-muted)' }}>
                    {log.src_country}
                  </td>
                  <td className="px-4 py-3 text-sm font-mono" style={{ color: 'var(--text-primary)' }}>
                    {log.dst_ip}
                  </td>
                  <td className="px-4 py-3 text-sm" style={{ color: 'var(--text-muted)' }}>
                    {log.dst_country}
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
                  <td className="px-4 py-3 text-sm">
                    <span 
                      className="px-2 py-1 rounded-full text-xs font-medium"
                      style={{ 
                        backgroundColor: `${getSeverityColor(log.severity)}20`,
                        color: getSeverityColor(log.severity)
                      }}
                    >
                      {log.severity}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm" style={{ color: 'var(--text-primary)' }}>
                    {log.hybrid_confidence}%
                  </td>
                  <td className="px-4 py-3 text-sm" style={{ color: 'var(--text-primary)' }}>
                    {log.risk_score}
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
