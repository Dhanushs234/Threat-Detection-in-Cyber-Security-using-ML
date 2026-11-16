import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { useDetectionStore } from '../../store/detectionStore'

type StackedTimelineProps = {
  className?: string
}

export default function StackedTimeline({ className }: StackedTimelineProps) {
  const { timelineBuckets } = useDetectionStore()

  // Format data for Recharts
  const currentTime = Date.now()
  const fiveMinutesAgo = currentTime - 5 * 60 * 1000

  const chartData = timelineBuckets
    .filter((bucket) => {
      const bucketTime = new Date(bucket.timestamp).getTime()
      return bucketTime >= fiveMinutesAgo && bucketTime <= currentTime
    })
    .map((bucket) => ({
      time: new Date(bucket.timestamp).toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
      }),
      Normal: bucket.normal,
      Suspicious: bucket.suspicious,
      Attack: bucket.attack,
    }))

  return (
    <div
      className={`card dashboard-chart-card p-6 ${className ?? ''}`.trim()}
      style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)' }}
    >
      <h3 className="chart-title text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
        Detection Timeline
      </h3>
      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
            <XAxis
              dataKey="time"
              stroke="var(--text-muted)"
              style={{ fontSize: '12px' }}
            />
            <YAxis
              stroke="var(--text-muted)"
              style={{ fontSize: '12px' }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: 'var(--bg-panel)',
                border: '1px solid var(--border)',
                borderRadius: '8px',
                color: 'var(--text-primary)'
              }}
            />
            <Legend
              wrapperStyle={{ color: 'var(--text-primary)' }}
            />
            <Bar
              dataKey="Normal"
              stackId="a"
              fill="#22C55E"
              isAnimationActive={true}
              barSize={18}
            />
            <Bar
              dataKey="Suspicious"
              stackId="a"
              fill="#F59E0B"
              isAnimationActive={true}
              barSize={18}
            />
            <Bar
              dataKey="Attack"
              stackId="a"
              fill="#EF4444"
              isAnimationActive={true}
              barSize={18}
            />
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
