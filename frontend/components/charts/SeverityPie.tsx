import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { useDetectionStore } from '../../store/detectionStore'

const COLORS = {
  High: '#DC2626',
  Medium: '#F59E0B',
  Low: '#22C55E',
}

interface SeverityPieProps {
  className?: string
}

export default function SeverityPie({ className }: SeverityPieProps) {
  const { severityDistribution } = useDetectionStore()

  const chartData = [
    { name: 'Low', value: severityDistribution.low },
    { name: 'Medium', value: severityDistribution.medium },
    { name: 'High', value: severityDistribution.high },
  ]

  return (
    <div
      className={`card dashboard-chart-card p-6 ${className ?? ''}`.trim()}
      style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)' }}
    >
      <h3 className="chart-title text-lg font-semibold" style={{ color: 'var(--text-primary)' }}>
        Severity Distribution
      </h3>
      <div className="chart-wrapper">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              labelLine={false}
              label={false}
              outerRadius={100}
              fill="#8884d8"
              dataKey="value"
            >
              {chartData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={COLORS[entry.name as keyof typeof COLORS]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: '#FFFFFF',
                border: '1px solid var(--border)',
                borderRadius: '8px',
                color: '#111827'
              }}
              itemStyle={{
                color: '#111827',
                fontWeight: 600
              }}
              labelStyle={{
                color: '#4B5563',
                fontWeight: 500
              }}
            />
            <Legend
              wrapperStyle={{ color: 'var(--text-primary)' }}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
