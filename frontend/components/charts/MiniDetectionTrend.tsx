import { useMemo } from 'react'
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from 'recharts'
import { useDetectionStore } from '../../store/detectionStore'

const LINE_COLOR = 'rgba(255, 80, 80, 0.85)'

type MiniDetectionTrendProps = {
  className?: string
}

const formatTooltipLabel = (label: string) => `Time: ${label}`

export default function MiniDetectionTrend({ className }: MiniDetectionTrendProps) {
  const detectionsPerMinute = useDetectionStore((state) => state.detectionsPerMinute)

  const chartData = useMemo(() => {
    if (!Array.isArray(detectionsPerMinute) || detectionsPerMinute.length === 0) {
      const now = new Date()
      const timeLabel = `${now.getHours().toString().padStart(2, '0')}:${now
        .getMinutes()
        .toString()
        .padStart(2, '0')}`
      return [{ time: timeLabel, count: 0 }]
    }
    return detectionsPerMinute
  }, [detectionsPerMinute])

  const allZero = chartData.every(point => point.count === 0)

  return (
    <div
      className={`card dashboard-chart-card p-6 ${className ?? ''}`.trim()}
      style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)' }}
    >
      <h3 className="chart-title text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
        Mini Detection Trend
      </h3>
      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData} margin={{ top: 10, right: 12, left: 0, bottom: 0 }}>
            <CartesianGrid stroke="rgba(255,255,255,0.06)" vertical={false} />
            <XAxis
              dataKey="time"
              tickLine={false}
              axisLine={{ stroke: 'rgba(255,255,255,0.08)' }}
              style={{ fill: 'var(--text-muted)', fontSize: '0.75rem' }}
            />
            <YAxis
              tickLine={false}
              axisLine={{ stroke: 'rgba(255,255,255,0.08)' }}
              allowDecimals={false}
              width={36}
              domain={[0, (dataMax: number) => Math.max(5, dataMax || 1)]}
              style={{ fill: 'var(--text-muted)', fontSize: '0.75rem' }}
            />
            <Tooltip
              formatter={(value: number) => [`Detections: ${value}`, '']}
              labelFormatter={formatTooltipLabel}
              contentStyle={{
                backgroundColor: '#0f172a',
                border: '1px solid rgba(255,255,255,0.12)',
                borderRadius: '8px',
                color: '#F8FAFC',
              }}
            />
            <Line
              type="monotone"
              dataKey="count"
              stroke={LINE_COLOR}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 3, stroke: LINE_COLOR, fill: '#ffffff' }}
              animationDuration={220}
            />
          </LineChart>
        </ResponsiveContainer>
        {allZero && (
          <div className="absolute inset-0 flex items-center justify-center text-sm" style={{ color: 'var(--text-muted)' }}>
            No detections yet
          </div>
        )}
      </div>
    </div>
  )
}
