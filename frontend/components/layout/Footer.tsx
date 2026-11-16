export default function Footer() {
  return (
    <footer 
      className="py-4 px-8 border-t text-center text-sm"
      style={{ 
        backgroundColor: 'var(--bg-panel)', 
        borderColor: 'var(--border)',
        color: 'var(--text-muted)'
      }}
    >
      <p>© 2025 IDS Monitoring Dashboard | Powered by Machine Learning</p>
    </footer>
  )
}
