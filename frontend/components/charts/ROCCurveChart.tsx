import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

// Generate ROC curve data points (approximated from the image)
const generateROCData = (): Array<{ fpr: number; 'ROC Curve': number; 'Random Classifier': number }> => {
  const data: Array<{ fpr: number; 'ROC Curve': number; 'Random Classifier': number }> = []
  // ROC curve starts at (0,0) and goes to (1,1) with high TPR early on
  const points = [
    { fpr: 0.00, tpr: 0.00 },
    { fpr: 0.01, tpr: 0.75 },
    { fpr: 0.02, tpr: 0.85 },
    { fpr: 0.03, tpr: 0.90 },
    { fpr: 0.05, tpr: 0.95 },
    { fpr: 0.10, tpr: 0.98 },
    { fpr: 0.15, tpr: 0.99 },
    { fpr: 0.20, tpr: 0.995 },
    { fpr: 0.50, tpr: 1.00 },
    { fpr: 1.00, tpr: 1.00 },
  ]
  
  points.forEach(point => {
    data.push({
      fpr: point.fpr,
      'ROC Curve': point.tpr,
      'Random Classifier': point.fpr,
    })
  })
  
  return data
}

export default function ROCCurveChart() {
  const rocData = generateROCData()

  return (
    <div 
      className="card p-6"
      style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)' }}
    >
      <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
        ROC Curve (AUC = 0.9838)
      </h3>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={rocData}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis 
            dataKey="fpr" 
            stroke="var(--text-muted)"
            style={{ fontSize: '12px' }}
            label={{ value: 'False Positive Rate', position: 'insideBottom', offset: -5, fill: 'var(--text-muted)' }}
            domain={[0, 1]}
          />
          <YAxis 
            stroke="var(--text-muted)"
            style={{ fontSize: '12px' }}
            label={{ value: 'True Positive Rate', angle: -90, position: 'insideLeft', fill: 'var(--text-muted)' }}
            domain={[0, 1]}
          />
          <Tooltip 
            contentStyle={{ 
              backgroundColor: 'var(--bg-panel)', 
              border: '1px solid var(--border)',
              borderRadius: '8px',
              color: 'var(--text-primary)'
            }}
            formatter={(value: number) => value.toFixed(3)}
          />
          <Legend 
            wrapperStyle={{ color: 'var(--text-primary)' }}
          />
          <Line 
            type="monotone" 
            dataKey="ROC Curve" 
            stroke="#FB8C00" 
            strokeWidth={3}
            dot={false}
          />
          <Line 
            type="monotone" 
            dataKey="Random Classifier" 
            stroke="#1E88E5" 
            strokeWidth={2}
            strokeDasharray="5 5"
            dot={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
