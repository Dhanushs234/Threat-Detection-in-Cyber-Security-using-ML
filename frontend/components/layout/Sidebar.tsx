import { useEffect, useState } from 'react'
import { NavLink } from 'react-router-dom'
import { 
  HomeIcon, 
  ShieldCheckIcon, 
  PencilSquareIcon, 
  ChartBarIcon, 
  InformationCircleIcon 
} from '@heroicons/react/24/outline'
import { Shield } from 'lucide-react'
import { useDetectionStore } from '@store/detectionStore'
import { socketService } from '../../services/socket'

const navigation = [
  { name: 'Dashboard', href: '/', icon: HomeIcon },
  { name: 'Threat Monitoring', href: '/monitoring', icon: ShieldCheckIcon },
  { name: 'Manual Detection', href: '/manual', icon: PencilSquareIcon },
  { name: 'Model Metrics', href: '/metrics', icon: ChartBarIcon },
  { name: 'About', href: '/about', icon: InformationCircleIcon },
]

export default function Sidebar() {
  const [isConnected, setIsConnected] = useState(socketService.isConnected())
  const monitoring = useDetectionStore((state) => state.monitoringStatus)

  useEffect(() => {
    const unsubscribe = socketService.subscribeConnectionStatus(setIsConnected)
    return () => unsubscribe()
  }, [])

  return (
    <div
      className="w-48 h-screen flex flex-col pt-4 pb-6"
      style={{
        backgroundColor: 'var(--bg-panel)',
        borderRight: '1px solid rgba(255, 255, 255, 0.06)'
      }}
    >
      <div className="flex items-center gap-2 px-3 mb-4">
        <div
          className={`flex items-center justify-center w-9 h-9 rounded-md transition-all duration-500 ${
            monitoring ? 'shield-glow' : ''
          }`}
        >
          <Shield size={24} strokeWidth={2.1} className="text-red-500" />
        </div>

        <span
          className="text-[1.12rem] font-semibold text-white leading-tight tracking-tight"
          style={{ textShadow: '0 0 10px rgba(239, 68, 68, 0.22)' }}
        >
          ThreatSense
        </span>
      </div>

      <div className="h-px bg-white/10 mx-3 mb-5" />

      {/* Navigation Links */}
      <nav className="flex-1 px-3 py-4 space-y-1.5">
        {navigation.map((item) => (
          <NavLink
            key={item.name}
            to={item.href}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-200 ${
                isActive
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'hover:bg-gray-800/60'
              }`
            }
            style={({ isActive }) => ({
              color: isActive ? '#ffffff' : 'var(--text-muted)',
            })}
          >
            {({ isActive }) => (
              <>
                <item.icon className="w-[18px] h-[18px]" />
                <span className="font-medium">{item.name}</span>
                {isActive && (
                  <div className="ml-auto w-1.5 h-1.5 rounded-full bg-white animate-pulse" />
                )}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div
        className="px-3 pt-4 mt-auto text-xs"
        style={{
          borderTop: '1px solid rgba(255, 255, 255, 0.05)',
          color: 'var(--text-muted)'
        }}
      >
        <p>ThreatSense v1.0</p>
        <p className="mt-1">Network Intrusion Detection</p>
        <div className="mt-3 flex items-center gap-2 text-xs font-medium">
          <span
            className={`w-2.5 h-2.5 rounded-full ${
              isConnected ? 'bg-green-400 shadow-green-400/40' : 'bg-red-500 shadow-red-500/40'
            } transition-all duration-300 shadow-md`}
          />
          <span>{isConnected ? 'Backend Connected' : 'Backend Disconnected'}</span>
        </div>
      </div>
    </div>
  )
}
