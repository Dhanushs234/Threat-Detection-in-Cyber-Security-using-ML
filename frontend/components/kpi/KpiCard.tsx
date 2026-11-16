import { motion } from 'framer-motion'
import { ReactNode } from 'react'

interface KpiCardProps {
  title: string
  value: number
  icon: ReactNode
  containerClass: string
  labelClass: string
  valueClass: string
}

export default function KpiCard({
  title,
  value,
  icon,
  containerClass,
  labelClass,
  valueClass,
}: KpiCardProps) {
  return (
    <div
      className={`min-h-[90px] rounded-xl p-5 flex items-center justify-between shadow-md transition-transform duration-200 ease-out hover:-translate-y-1 hover:shadow-lg ${containerClass}`}
      style={{ willChange: 'transform' }}
    >
      <div>
        <p className={`text-sm ${labelClass}`}>
          {title}
        </p>
        <motion.p
          key={value}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.3 }}
          className={`text-2xl font-bold mt-2 ${valueClass}`}
        >
          {value.toLocaleString()}
        </motion.p>
      </div>
      <div className="ml-4 flex-shrink-0">
        {icon}
      </div>
    </div>
  )
}
