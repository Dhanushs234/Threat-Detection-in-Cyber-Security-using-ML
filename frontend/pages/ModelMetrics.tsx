import ModelComparisonChart from '../components/charts/ModelComparisonChart'
import ConfusionMatrixGrid from '../components/charts/ConfusionMatrixGrid'
import ROCCurveChart from '../components/charts/ROCCurveChart'
import AnomalyScoreChart from '../components/charts/AnomalyScoreChart'

export default function ModelMetrics() {
  return (
    <div className="min-h-screen p-8" style={{ backgroundColor: 'var(--bg-main)' }}>
      <div className="mb-6">
        <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
          Model Metrics
        </h1>
      </div>

      {/* Header */}
      <div className="mb-8">
        <p className="text-sm" style={{ color: 'var(--text-muted)' }}>
          Hybrid IDS: Random Forest + Isolation Forest
        </p>
      </div>

      {/* Model Comparison Chart */}
      <div className="mb-6">
        <ModelComparisonChart />
      </div>

      {/* Confusion Matrix and ROC Curve */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        <ConfusionMatrixGrid />
        <ROCCurveChart />
      </div>

      {/* Anomaly Score Chart */}
      <div>
        <AnomalyScoreChart />
      </div>
    </div>
  )
}
