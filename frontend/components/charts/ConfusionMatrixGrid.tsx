export default function ConfusionMatrixGrid() {
  const confusionData = [
    [53226, 2774],
    [13154, 106187],
  ]

  const labels = ['Normal', 'Attack']

  const getColorIntensity = (value: number) => {
    const max = Math.max(...confusionData.flat())
    const intensity = value / max
    if (intensity > 0.8) return '#0D47A1'
    if (intensity > 0.5) return '#1976D2'
    if (intensity > 0.3) return '#42A5F5'
    return '#90CAF9'
  }

  return (
    <div 
      className="card p-6"
      style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)' }}
    >
      <h3 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
        Confusion Matrix
      </h3>
      <div className="flex flex-col items-center">
        <div className="mb-4">
          <p className="text-sm text-center" style={{ color: 'var(--text-muted)' }}>
            Predicted Label
          </p>
        </div>
        <div className="flex gap-2">
          <div className="flex flex-col justify-center mr-2">
            <p 
              className="text-sm transform -rotate-90 whitespace-nowrap"
              style={{ color: 'var(--text-muted)', width: '100px' }}
            >
              True Label
            </p>
          </div>
          <div>
            <div className="grid grid-cols-2 gap-2 mb-2">
              {labels.map((label) => (
                <div 
                  key={label}
                  className="w-32 h-8 flex items-center justify-center text-sm font-medium"
                  style={{ color: 'var(--text-muted)' }}
                >
                  {label}
                </div>
              ))}
            </div>
            <div className="grid grid-cols-2 gap-2">
              {confusionData.map((row, i) => (
                row.map((value, j) => (
                  <div
                    key={`${i}-${j}`}
                    className="w-32 h-32 flex flex-col items-center justify-center rounded-lg border"
                    style={{
                      backgroundColor: getColorIntensity(value),
                      borderColor: 'var(--border)',
                    }}
                  >
                    <span className="text-2xl font-bold text-white">
                      {value.toLocaleString()}
                    </span>
                    <span className="text-xs text-white/80 mt-1">
                      {labels[i]} → {labels[j]}
                    </span>
                  </div>
                ))
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
