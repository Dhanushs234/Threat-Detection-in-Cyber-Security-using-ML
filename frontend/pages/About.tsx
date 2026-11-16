export default function About() {
  return (
    <div className="min-h-screen p-8" style={{ backgroundColor: 'var(--bg-main)' }}>
      <div className="mb-6">
        <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
          About
        </h1>
      </div>

      {/* System Description */}
      <div 
        className="card p-6 mb-6"
        style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)' }}
      >
        <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
          System Description
        </h2>
        <div className="space-y-4" style={{ color: 'var(--text-muted)' }}>
          <p>
            Threat Sense is a real-time network intrusion detection system (IDS) designed to monitor, 
            analyze, and classify network traffic patterns. Built with modern web technologies and 
            powered by machine learning, it provides comprehensive threat detection and visualization 
            capabilities for network security monitoring.
          </p>
          <p>
            The system processes network flow data in real-time, extracting 16 critical features 
            including packet counts, byte volumes, inter-packet timing, jitter, and protocol information. 
            These features are analyzed by our hybrid detection engine to identify potential security threats.
          </p>
          <p>
            The dashboard provides live updates via WebSocket connections, ensuring security teams 
            have immediate visibility into network activity, detection events, and blocked threats 
            without manual refreshing or polling.
          </p>
        </div>
      </div>

      {/* Hybrid IDS Explanation */}
      <div 
        className="card p-6 mb-6"
        style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)' }}
      >
        <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
          Hybrid IDS Architecture
        </h2>
        <div className="space-y-4" style={{ color: 'var(--text-muted)' }}>
          <p>
            Our hybrid intrusion detection system combines two complementary machine learning approaches 
            to achieve superior detection accuracy:
          </p>
          
          <div className="ml-4 space-y-3">
            <div>
              <h3 className="font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
                1. Random Forest Classifier
              </h3>
              <p>
                The Random Forest model serves as the primary classifier, trained on labeled network 
                traffic data to distinguish between normal, suspicious, and attack patterns. It achieves 
                91% accuracy with 98% precision, making it highly reliable for threat identification.
              </p>
            </div>

            <div>
              <h3 className="font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
                2. Isolation Forest (Anomaly Detection)
              </h3>
              <p>
                The Isolation Forest operates as an unsupervised anomaly detector, identifying unusual 
                patterns that may indicate zero-day attacks or novel threat vectors. It complements the 
                Random Forest by catching anomalies that don't match known attack signatures.
              </p>
            </div>

            <div>
              <h3 className="font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
                3. Cascade Decision Logic
              </h3>
              <p>
                The hybrid system uses a cascade approach: Random Forest predictions are validated 
                against Isolation Forest anomaly scores. This dual-layer verification reduces false 
                positives while maintaining high detection rates, achieving an overall AUC of 0.9838.
              </p>
            </div>
          </div>

          <p className="mt-4">
            Each detection includes confidence scores, risk assessments, and severity classifications, 
            providing security analysts with actionable intelligence for incident response.
          </p>
        </div>
      </div>

      {/* Use Cases */}
      <div 
        className="card p-6"
        style={{ backgroundColor: 'var(--bg-card)', borderColor: 'var(--border)' }}
      >
        <h2 className="text-xl font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
          Use Cases
        </h2>
        <div className="space-y-4" style={{ color: 'var(--text-muted)' }}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-lg" style={{ backgroundColor: 'var(--bg-panel)' }}>
              <h3 className="font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
                🏢 Enterprise Network Security
              </h3>
              <p className="text-sm">
                Monitor corporate networks for intrusion attempts, data exfiltration, and insider threats 
                with real-time alerting and automatic blocking capabilities.
              </p>
            </div>

            <div className="p-4 rounded-lg" style={{ backgroundColor: 'var(--bg-panel)' }}>
              <h3 className="font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
                🔬 Security Research
              </h3>
              <p className="text-sm">
                Analyze network traffic patterns, test detection algorithms, and study attack behaviors 
                using manual detection mode and comprehensive metrics visualization.
              </p>
            </div>

            <div className="p-4 rounded-lg" style={{ backgroundColor: 'var(--bg-panel)' }}>
              <h3 className="font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
                🎓 Educational Training
              </h3>
              <p className="text-sm">
                Teach cybersecurity concepts, demonstrate ML-based threat detection, and provide 
                hands-on experience with real-world intrusion detection systems.
              </p>
            </div>

            <div className="p-4 rounded-lg" style={{ backgroundColor: 'var(--bg-panel)' }}>
              <h3 className="font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
                🛡️ Threat Intelligence
              </h3>
              <p className="text-sm">
                Collect and analyze threat data, identify attack trends, and build threat intelligence 
                feeds from detected malicious activities and blocked IPs.
              </p>
            </div>

            <div className="p-4 rounded-lg" style={{ backgroundColor: 'var(--bg-panel)' }}>
              <h3 className="font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
                📊 Compliance Monitoring
              </h3>
              <p className="text-sm">
                Meet regulatory requirements for network monitoring, maintain audit logs of security 
                events, and generate reports for compliance documentation.
              </p>
            </div>

            <div className="p-4 rounded-lg" style={{ backgroundColor: 'var(--bg-panel)' }}>
              <h3 className="font-semibold mb-2" style={{ color: 'var(--text-primary)' }}>
                🚨 Incident Response
              </h3>
              <p className="text-sm">
                Rapidly identify and respond to security incidents with detailed detection logs, 
                IP-based search capabilities, and historical threat analysis.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
