import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'

interface ManualDetectionResult {
  timestamp: string
  label: string
  severity: string
  hybrid_confidence: number
  risk_score: number
}

interface ManualHistoryItem {
  id: number
  timestamp: string
  detection_id: string
  label: string
  severity?: string
  hybrid_confidence: number
  risk_score: number
}

const REQUIRED_FEATURES = [
  { name: 'dur', label: 'Duration', type: 'number', placeholder: '0.001055' },
  { name: 'spkts', label: 'Source Packets', type: 'number', placeholder: '2' },
  { name: 'dpkts', label: 'Destination Packets', type: 'number', placeholder: '2' },
  { name: 'sbytes', label: 'Source Bytes', type: 'number', placeholder: '132' },
  { name: 'dbytes', label: 'Destination Bytes', type: 'number', placeholder: '164' },
  { name: 'sload', label: 'Source Load', type: 'number', placeholder: '500473.9375' },
  { name: 'dload', label: 'Destination Load', type: 'number', placeholder: '621800.9375' },
  { name: 'sinpkt', label: 'Source Inter-Packet Time', type: 'number', placeholder: '0.017' },
  { name: 'dinpkt', label: 'Destination Inter-Packet Time', type: 'number', placeholder: '0.013' },
  { name: 'sjit', label: 'Source Jitter', type: 'number', placeholder: '0.0' },
  { name: 'djit', label: 'Destination Jitter', type: 'number', placeholder: '0.0' },
  { name: 'smean', label: 'Source Mean', type: 'number', placeholder: '66' },
  { name: 'dmean', label: 'Destination Mean', type: 'number', placeholder: '82' },
  { name: 'synack', label: 'SYN-ACK Count', type: 'number', placeholder: '0.0' },
  { name: 'ackdat', label: 'ACK-DAT Count', type: 'number', placeholder: '0.0' },
  { name: 'proto', label: 'Protocol', type: 'text', placeholder: 'tcp' },
]

const deriveSeverity = (label: string, risk: number) => {
  const normalizedLabel = label.toLowerCase()
  if (normalizedLabel === 'attack') return 'High'
  if (normalizedLabel === 'suspicious') return 'Medium'
  if (risk >= 70) return 'High'
  if (risk >= 40) return 'Medium'
  return 'Low'
}

export default function ManualDetection() {
  const [formData, setFormData] = useState<Record<string, string>>({})
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [result, setResult] = useState<ManualDetectionResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [history, setHistory] = useState<ManualHistoryItem[]>([])

  // Fetch manual detection history on mount
  useEffect(() => {
    fetchHistory()
  }, [])

  const fetchHistory = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/history/manual?limit=50')
      if (!response.ok) {
        throw new Error(`History fetch failed with status ${response.status}`)
      }
      const data: { history?: ManualHistoryItem[] } = await response.json()
      const normalizedHistory = Array.isArray(data.history)
        ? data.history.map((entry: ManualHistoryItem) => ({
            ...entry,
            severity: entry.severity ?? deriveSeverity(entry.label, entry.risk_score),
          }))
        : []
      setHistory(normalizedHistory)
    } catch (error) {
      console.warn('Manual history unavailable:', error)
      setHistory([])
    }
  }

  const handleInputChange = (name: string, value: string) => {
    setFormData(prev => ({ ...prev, [name]: value }))
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError(null)
    setResult(null)

    try {
      // Validate all fields are filled
      const missingFields = REQUIRED_FEATURES.filter(f => !formData[f.name]?.trim())
      if (missingFields.length > 0) {
        setError(`Missing required fields: ${missingFields.map(f => f.label).join(', ')}`)
        setIsSubmitting(false)
        return
      }

      // Convert numeric fields
      const payload: Record<string, number | string> = {}
      REQUIRED_FEATURES.forEach(field => {
        if (field.type === 'number') {
          payload[field.name] = parseFloat(formData[field.name])
        } else {
          payload[field.name] = formData[field.name]
        }
      })

      // Submit to backend
      const response = await fetch('http://127.0.0.1:8000/detect/manual', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()
      setResult(data)
      
      // Refresh history
      fetchHistory()
      
      // Clear form
      setFormData({})
    } catch (error) {
      console.error('Detection failed:', error)
      setError('Detection failed. Please check your input and backend connection.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const getLabelColor = (label: string) => {
    const labelLower = label.toLowerCase()
    if (labelLower === 'attack') return '#EF4444'
    if (labelLower === 'suspicious') return '#F59E0B'
    return '#22C55E'
  }

  const getSeverityColor = (severity?: string) => {
    if (!severity) return '#9CA3AF'
    const severityLower = severity.toLowerCase()
    if (severityLower === 'high') return '#DC2626'
    if (severityLower === 'medium') return '#F59E0B'
    return '#22C55E'
  }

  return (
    <div className="min-h-screen p-8" style={{ backgroundColor: 'var(--bg-main)' }}>
      <div className="mb-6">
        <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
          Manual Detection
        </h1>
      </div>

      <div className="manual-page">
        {/* Input Form */}
        <div 
          className="card p-6 network-flow-card"
          style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)' }}
        >
          <h2 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
            Network Flow Features
          </h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="network-flow-grid">
              {REQUIRED_FEATURES.map((feature) => (
                <div 
                  key={feature.name} 
                  className={`flex flex-col gap-1 ${feature.name === 'sjit' ? 'md:mt-6' : ''}`}
                >
                  <label 
                    className="block text-sm font-medium mb-1"
                    style={{ color: 'var(--text-muted)' }}
                  >
                    {feature.label}
                  </label>
                  <input
                    type={feature.type}
                    value={formData[feature.name] || ''}
                    onChange={(e) => handleInputChange(feature.name, e.target.value)}
                    placeholder={feature.placeholder}
                    className="w-full px-3 py-2 rounded-md border focus:outline-none focus:ring-2 focus:ring-blue-500"
                    style={{
                      backgroundColor: 'var(--bg-panel)',
                      borderColor: 'var(--border)',
                      color: 'var(--text-primary)',
                    }}
                    step={feature.type === 'number' ? 'any' : undefined}
                  />
                </div>
              ))}
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white rounded-lg font-medium transition-colors"
            >
              {isSubmitting ? 'Detecting...' : 'Run Detection'}
            </button>

            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="px-4 py-3 rounded-lg text-sm"
                style={{ backgroundColor: '#DC262620', color: '#DC2626' }}
              >
                {error}
              </motion.div>
            )}
          </form>
        </div>

        {/* Result Display */}
        <div 
          className="card p-6 detection-result-card"
          style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)' }}
        >
          <h2 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
            Detection Result
          </h2>
          {result ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              className="space-y-4"
            >
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Timestamp</p>
                  <p className="text-lg font-medium mt-1" style={{ color: 'var(--text-primary)' }}>
                    {new Date(result.timestamp).toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Label</p>
                  <span 
                    className="inline-block px-3 py-1 rounded-full text-sm font-medium mt-1"
                    style={{ 
                      backgroundColor: `${getLabelColor(result.label)}20`,
                      color: getLabelColor(result.label)
                    }}
                  >
                    {result.label}
                  </span>
                </div>
                <div>
                  <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Hybrid Confidence</p>
                  <p className="text-2xl font-bold mt-1" style={{ color: 'var(--text-primary)' }}>
                    {result.hybrid_confidence}%
                  </p>
                </div>
                <div>
                  <p className="text-sm" style={{ color: 'var(--text-muted)' }}>Risk Score</p>
                  <p className="text-2xl font-bold mt-1" style={{ color: 'var(--text-primary)' }}>
                    {result.risk_score}
                  </p>
                </div>
              </div>
            </motion.div>
          ) : (
            <p className="text-center py-12" style={{ color: 'var(--text-muted)' }}>
              Submit the form to see detection results
            </p>
          )}
        </div>
        {/* Manual History Table */}
        <div 
          className="card p-6 manual-history-card"
          style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)' }}
        >
          <h2 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
            Manual Detection History
          </h2>
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
                {history.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-4 py-8 text-center text-sm" style={{ color: 'var(--text-muted)' }}>
                      No manual detections yet.
                    </td>
                  </tr>
                ) : (
                  history.map((item, index) => (
                    <motion.tr
                      key={item.id}
                      initial={{ opacity: 0, y: -10 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.2, delay: index * 0.02 }}
                      className="hover:bg-gray-800/30 transition-colors"
                    >
                      <td className="px-4 py-3 text-sm whitespace-nowrap" style={{ color: 'var(--text-muted)' }}>
                        {new Date(item.timestamp).toLocaleString()}
                      </td>
                      <td className="px-4 py-3 text-sm font-mono" style={{ color: 'var(--text-primary)' }}>
                        {item.detection_id || 'MANUAL'}
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <span 
                          className="px-2 py-1 rounded-full text-xs font-medium"
                          style={{ 
                            backgroundColor: `${getLabelColor(item.label)}20`,
                            color: getLabelColor(item.label)
                          }}
                        >
                          {item.label}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm">
                        <span 
                          className="px-2 py-1 rounded-full text-xs font-medium"
                          style={{ 
                            backgroundColor: `${getSeverityColor(item.severity)}20`,
                            color: getSeverityColor(item.severity)
                          }}
                        >
                          {item.severity ?? 'Unknown'}
                        </span>
                      </td>
                      <td className="px-4 py-3 text-sm" style={{ color: 'var(--text-primary)' }}>
                        {item.hybrid_confidence}%
                      </td>
                      <td className="px-4 py-3 text-sm" style={{ color: 'var(--text-primary)' }}>
                        {item.risk_score}
                      </td>
                    </motion.tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}
