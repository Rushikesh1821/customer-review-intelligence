import { motion } from 'framer-motion';

// ===================================================================
// StatsCard — Animated stat display with icon and gradient accent
// ===================================================================

export default function StatsCard({
  title,
  value,
  subtitle,
  icon: Icon,
  gradient = 'gradient-accent',
  delay = 0,
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      className="glass-card card-hover p-5 relative overflow-hidden group"
    >
      {/* Background glow effect */}
      <div
        className={`absolute -top-8 -right-8 w-24 h-24 rounded-full ${gradient} opacity-10
          group-hover:opacity-20 transition-opacity duration-500 blur-2xl`}
      />

      <div className="relative flex items-start justify-between">
        <div className="min-w-0 flex-1">
          <p className="text-xs font-medium text-slate-400 uppercase tracking-wider mb-1.5">
            {title}
          </p>
          <p className="text-2xl font-bold text-slate-50 tracking-tight">
            {value}
          </p>
          {subtitle && (
            <p className="text-xs text-slate-500 mt-1 font-medium">
              {subtitle}
            </p>
          )}
        </div>

        {Icon && (
          <div className={`w-10 h-10 rounded-xl ${gradient} flex items-center justify-center flex-shrink-0 shadow-lg`}>
            <Icon className="w-5 h-5 text-white" />
          </div>
        )}
      </div>
    </motion.div>
  );
}
