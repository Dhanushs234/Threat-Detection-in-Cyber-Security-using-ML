import { useDetectionStore } from '../../store/detectionStore'

export default function AttackSourceIPs() {
  const { detectionLogs } = useDetectionStore()

  const attackLogs = detectionLogs
    .filter((log) => log.label?.toLowerCase() === 'attack')
    .slice(0, 5)

  return (
    <div
      className="card p-6 h-full flex flex-col"
      style={{
        backgroundColor: 'var(--bg-card)',
        borderColor: 'var(--border)',
        minHeight: '280px',
      }}
    >
      <h3
        className="text-lg font-semibold mb-4"
        style={{ color: 'var(--text-primary)' }}
      >
        Attack Source IPs
      </h3>
      <div className="flex-1">
        {attackLogs.length === 0 ? (
          <div
            className="rounded-lg border h-full flex items-center justify-center px-4 text-center text-sm"
            style={{ borderColor: 'var(--border)', color: 'var(--text-muted)' }}
          >
            No attack detections yet. New attack sources will appear here instantly.
          </div>
        ) : (
          <div
            className="rounded-lg border divide-y"
            style={{ borderColor: 'var(--border)' }}
          >
            {attackLogs.map((log) => (
              <div
                key={`${log.detection_id}-${log.timestamp}`}
                className="px-4 py-3 flex items-center justify-between gap-4"
                style={{ backgroundColor: 'var(--bg-panel)' }}
              >
                <div className="flex items-center gap-2">
                  <span
                    className="inline-block h-2.5 w-2.5 rounded-full"
                    style={{ backgroundColor: '#EF4444' }}
                  />
                  <span
                    className="text-sm font-mono"
                    style={{ color: 'var(--text-primary)' }}
                  >
                    {log.src_ip}
                  </span>
                </div>
                <span
                  className="text-xs"
                  style={{ color: 'var(--text-muted)' }}
                >
                  {new Date(log.timestamp).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                    second: '2-digit',
                  })}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
