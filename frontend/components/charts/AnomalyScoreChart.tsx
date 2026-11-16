import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine, ZAxis } from 'recharts'

type AnomalyPoint = {
  sample: number
  score: number
}

type ScatterData = {
  normal: AnomalyPoint[]
  attack: AnomalyPoint[]
}

// Generate anomaly score data approximated from the "Anomaly Scores per Sample" chart
const generateAnomalyData = (): ScatterData => {
  const normal: AnomalyPoint[] = []
  const attack: AnomalyPoint[] = []

  // Normal samples cluster around >0.05
  for (let i = 0; i < 120; i++) {
    normal.push({
      sample: i * 2 + 1,
      score: 0.065 + Math.random() * 0.08,
    })
  }

  // Attack samples cluster near threshold
  for (let i = 0; i < 80; i++) {
    attack.push({
      sample: i * 2 + 2,
      score: 0.015 + Math.random() * 0.04,
    })
  }

  return { normal, attack }
}

export default function AnomalyScoreChart() {
  const anomalyData = generateAnomalyData()

  return (
    <div 
      className="card p-6"
      style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)' }}
    >
      <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
        Anomaly Scores per Sample
      </h3>
      <div style={{ backgroundColor: '#fff', borderRadius: '12px', padding: '12px' }}>
        <ResponsiveContainer width="100%" height={360}>
          <ScatterChart>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis 
            type="number"
            dataKey="sample" 
            stroke="var(--text-muted)"
            style={{ fontSize: '12px' }}
            label={{ value: 'Sample Index', position: 'insideBottom', offset: -5, fill: 'var(--text-muted)' }}
          />
          <YAxis 
            type="number"
            dataKey="score"
            stroke="var(--text-muted)"
            style={{ fontSize: '12px' }}
            label={{ value: 'Anomaly Score', angle: -90, position: 'insideLeft', fill: 'var(--text-muted)' }}
            domain={[-0.15, 0.15]}
          />
          <ZAxis range={[50, 150]} />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'var(--bg-panel)', 
              border: '1px solid var(--border)',
              borderRadius: '8px',
              color: 'var(--text-primary)'
            }}
            formatter={(value: number) => value.toFixed(4)}
          />
          <ReferenceLine 
            y={0.05} 
            stroke="#1E88E5" 
            strokeDasharray="3 3" 
            label={{ value: 'Threshold=0.05', fill: 'var(--text-muted)', fontSize: 12 }}
          />
          <Scatter
            name="Normal"
            data={anomalyData.normal}
            dataKey="score"
            fill="#43A047"
            line={{ strokeWidth: 0 }}
            shape="circle"
          />
          <Scatter
            name="Attack"
            data={anomalyData.attack}
            dataKey="score"
            fill="#E53935"
            line={{ strokeWidth: 0 }}
            shape="circle"
          />
        </ScatterChart>
        </ResponsiveContainer>
      </div>
    </div>
  )
}
