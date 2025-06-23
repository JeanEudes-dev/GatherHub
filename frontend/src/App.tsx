import { useState } from 'react'
import { motion } from 'framer-motion'
import { Sparkles, Zap, Rocket, Star } from 'lucide-react'
import { cn } from '@/lib/utils'

function App() {
  const [activeCard, setActiveCard] = useState<number | null>(null)

  return (
    <div className="relative min-h-screen overflow-hidden bg-background">
      {/* Aurora Background Animation */}
      <div className="absolute inset-0 opacity-30">
        <div className="absolute left-1/4 top-1/4 h-96 w-96 animate-aurora rounded-full bg-aurora-blue/20 blur-3xl"></div>
        <div
          className="absolute right-1/4 top-1/3 h-80 w-80 animate-aurora rounded-full bg-aurora-purple/20 blur-3xl"
          style={{ animationDelay: '2s' }}
        ></div>
        <div
          className="absolute bottom-1/4 left-1/3 h-72 w-72 animate-aurora rounded-full bg-aurora-pink/20 blur-3xl"
          style={{ animationDelay: '4s' }}
        ></div>
        <div
          className="absolute bottom-1/3 right-1/3 h-64 w-64 animate-aurora rounded-full bg-aurora-green/20 blur-3xl"
          style={{ animationDelay: '6s' }}
        ></div>
      </div>

      {/* Floating Particles */}
      <div className="pointer-events-none absolute inset-0">
        {Array.from({ length: 20 }).map((_, i) => (
          <motion.div
            key={i}
            className="absolute h-1 w-1 rounded-full bg-aurora-blue/30"
            initial={{
              x:
                Math.random() *
                (typeof window !== 'undefined' ? window.innerWidth : 1200),
              y:
                Math.random() *
                (typeof window !== 'undefined' ? window.innerHeight : 800),
              opacity: 0,
            }}
            animate={{
              y: [0, -20, 0],
              opacity: [0, 1, 0],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
          />
        ))}
      </div>

      <div className="container-glass relative z-10 py-20">
        {/* Header */}
        <motion.div
          className="mb-16 text-center"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <div className="mb-6 flex items-center justify-center gap-3">
            <div className="relative">
              <Sparkles className="h-8 w-8 animate-glow text-aurora-blue" />
              <div className="absolute inset-0 h-8 w-8 animate-glow text-aurora-blue blur-sm"></div>
            </div>
            <h1 className="bg-gradient-to-r from-aurora-blue via-aurora-purple to-aurora-pink bg-clip-text text-6xl font-bold text-transparent">
              GatherHub
            </h1>
          </div>
          <p className="mx-auto max-w-2xl text-xl text-gray-300">
            A beautiful, modern collaboration platform built with React, Vite,
            TypeScript, and Tailwind CSS v4
          </p>
        </motion.div>

        {/* Feature Cards */}
        <div className="mb-16 grid gap-8 md:grid-cols-2 lg:grid-cols-3">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              className={cn(
                'glass-card group cursor-pointer p-6 transition-all duration-300',
                activeCard === index && 'scale-105 shadow-aurora'
              )}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              onHoverStart={() => setActiveCard(index)}
              onHoverEnd={() => setActiveCard(null)}
              whileHover={{ y: -5 }}
            >
              <div className="mb-4 flex items-center gap-3">
                <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-gradient-to-br from-aurora-blue/20 to-aurora-purple/20 transition-transform group-hover:scale-110">
                  <feature.icon className="h-6 w-6 text-aurora-blue" />
                </div>
                <h3 className="text-xl font-semibold text-white">
                  {feature.title}
                </h3>
              </div>
              <p className="leading-relaxed text-gray-300">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>

        {/* Demo Buttons */}
        <motion.div
          className="mb-16 flex flex-wrap justify-center gap-4"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 0.6 }}
        >
          <button className="btn-aurora">
            <Rocket className="mr-2 h-5 w-5" />
            Get Started
          </button>
          <button className="btn-glass">
            <Star className="mr-2 h-5 w-5" />
            View Demo
          </button>
        </motion.div>

        {/* Stats Section */}
        <motion.div
          className="glass-card p-8 text-center"
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.8, delay: 0.8 }}
        >
          <h2 className="mb-6 text-2xl font-bold text-white">Project Status</h2>
          <div className="grid grid-cols-2 gap-6 md:grid-cols-4">
            {stats.map((stat, index) => (
              <div key={stat.label} className="text-center">
                <motion.div
                  className="mb-2 bg-gradient-to-r from-aurora-blue to-aurora-green bg-clip-text text-3xl font-bold text-transparent"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ duration: 0.5, delay: 1 + index * 0.1 }}
                >
                  {stat.value}
                </motion.div>
                <div className="text-sm text-gray-400">{stat.label}</div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Footer */}
        <motion.div
          className="mt-16 text-center text-gray-400"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.8, delay: 1.2 }}
        >
          <p>Built with ❤️ using modern web technologies</p>
          <div className="mt-4 flex justify-center gap-4">
            <span className="rounded-full bg-glass-light px-3 py-1 text-xs">
              React 18
            </span>
            <span className="rounded-full bg-glass-light px-3 py-1 text-xs">
              Vite 5
            </span>
            <span className="rounded-full bg-glass-light px-3 py-1 text-xs">
              TypeScript
            </span>
            <span className="rounded-full bg-glass-light px-3 py-1 text-xs">
              Tailwind v4
            </span>
          </div>
        </motion.div>
      </div>
    </div>
  )
}

const features = [
  {
    title: 'Events',
    description:
      'Create and manage events with real-time collaboration features.',
    icon: Sparkles,
  },
  {
    title: 'Tasks',
    description:
      'Organize and track tasks with powerful assignment capabilities.',
    icon: Zap,
  },
  {
    title: 'Voting',
    description: 'Democratic decision making with various voting mechanisms.',
    icon: Star,
  },
  {
    title: 'Real-time',
    description: 'WebSocket-powered real-time updates across all features.',
    icon: Rocket,
  },
  {
    title: 'Responsive',
    description: 'Beautiful design that works perfectly on all devices.',
    icon: Sparkles,
  },
  {
    title: 'Modern',
    description: 'Built with the latest technologies and best practices.',
    icon: Zap,
  },
]

const stats = [
  { label: 'Components', value: '20+' },
  { label: 'Features', value: '6' },
  { label: 'TypeScript', value: '100%' },
  { label: 'Performance', value: 'A+' },
]

export default App
