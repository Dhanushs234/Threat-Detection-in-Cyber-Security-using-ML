import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const modelData = [
  {
    model: 'Random Forest',
    Accuracy: 0.91,
    Precision: 0.98,
    Recall: 0.89,
    'F1 Score': 0.93,
  },
  {
    model: 'SVM',
    Accuracy: 0.76,
    Precision: 0.96,
    Recall: 0.67,
    'F1 Score': 0.79,
  },
  {
    model: 'Decision Tree',
    Accuracy: 0.89,
    Precision: 0.96,
    Recall: 0.87,
    'F1 Score': 0.91,
  },
  {
    model: 'KNN',
    Accuracy: 0.90,
    Precision: 0.96,
    Recall: 0.79,
    'F1 Score': 0.87,
  },
]

export default function ModelComparisonChart() {
  return (
    <div 
      className="card p-6"
      style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)' }}
    >
      <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
        Model Comparison Metrics
      </h3>
      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={modelData}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
          <XAxis 
            dataKey="model" 
            stroke="var(--text-muted)"
            style={{ fontSize: '12px' }}
          />
          <YAxis 
            stroke="var(--text-muted)"
            style={{ fontSize: '12px' }}
            domain={[0, 1]}
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
          <Bar dataKey="Accuracy" fill="#1E88E5" />
          <Bar dataKey="Precision" fill="#FB8C00" />
          <Bar dataKey="Recall" fill="#43A047" />
          <Bar dataKey="F1 Score" fill="#E53935" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
