# GatherHub Frontend

A modern, production-grade React frontend for GatherHub built with Vite, TypeScript, and Tailwind CSS. Features a stunning aurora/glassmorphism design system with smooth animations and responsive layouts.

## 🚀 Tech Stack

- **React 19** - Latest React with modern features
- **Vite 6** - Lightning-fast development and build tool
- **TypeScript** - Type-safe development
- **Tailwind CSS 3.4** - Utility-first CSS framework
- **shadcn/ui** - Beautiful, accessible UI components
- **Framer Motion** - Smooth animations and transitions
- **Zustand** - Lightweight state management
- **Axios** - HTTP client for API requests
- **Lucide React** - Beautiful icons

## 🎨 Design System

The frontend features a modern aurora/glassmorphism design system with:

- **Aurora Background**: Animated gradient orbs with smooth transitions
- **Glassmorphism**: Translucent cards with backdrop blur effects
- **Neon Accents**: Glowing buttons and interactive elements
- **Responsive Design**: Mobile-first, fully responsive layouts
- **Dark Theme**: Optimized for dark mode interfaces

### Color Palette

```css
/* Aurora Colors */
--aurora-blue: #60a5fa --aurora-purple: #a855f7 --aurora-pink: #ec4899
  --aurora-green: #10b981 --aurora-yellow: #f59e0b --aurora-red: #ef4444;
```

## 📁 Project Structure

```
frontend/
├── public/                 # Static assets
├── src/
│   ├── assets/            # Images, fonts, etc.
│   ├── components/        # Reusable components
│   │   ├── ui/           # shadcn/ui components
│   │   └── layout/       # Layout components
│   ├── features/         # Feature-specific components
│   │   ├── auth/         # Authentication
│   │   ├── events/       # Event management
│   │   ├── tasks/        # Task management
│   │   └── voting/       # Voting system
│   ├── hooks/            # Custom React hooks
│   ├── lib/              # Utilities and helpers
│   ├── pages/            # Page components
│   ├── services/         # API services
│   ├── store/            # State management
│   ├── styles/           # Global styles
│   └── types/            # TypeScript definitions
├── .env.example          # Environment variables template
├── .env.local           # Local environment variables
├── components.json      # shadcn/ui configuration
├── tailwind.config.js   # Tailwind configuration
├── vite.config.ts       # Vite configuration
└── package.json         # Dependencies and scripts
```

## 🛠️ Development

### Prerequisites

- Node.js 18+ (recommended: 20+)
- npm or yarn

### Quick Start

1. **Install dependencies**

   ```bash
   npm install
   ```

2. **Start development server**

   ```bash
   npm run dev
   ```

3. **Open browser**
   Navigate to `http://localhost:5173`

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint
- `npm run lint:fix` - Fix ESLint issues
- `npm run format` - Format code with Prettier
- `npm run type-check` - Run TypeScript type checking

## 🏗️ Building

### Development Build

```bash
npm run dev
```

### Production Build

```bash
npm run build
npm run preview
```

The build outputs to the `dist/` directory and is optimized for production with:

- Code splitting
- Tree shaking
- Minification
- Asset optimization

## 🧩 Adding Components

### Using shadcn/ui

Add new shadcn/ui components:

```bash
npx shadcn@latest add [component-name]
```

Example:

```bash
npx shadcn@latest add dialog
npx shadcn@latest add form
npx shadcn@latest add table
```

### Custom Components

Create components in the appropriate directory:

- `src/components/ui/` - Reusable UI components
- `src/components/layout/` - Layout components
- `src/features/[feature]/` - Feature-specific components

## 🎯 State Management

The project uses Zustand for state management. Create stores in `src/store/`:

```typescript
import { create } from 'zustand'

interface AuthState {
  user: User | null
  login: (user: User) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>(set => ({
  user: null,
  login: user => set({ user }),
  logout: () => set({ user: null }),
}))
```

## 🌐 API Integration

API services are located in `src/services/`. Use Axios for HTTP requests:

```typescript
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
})

export const eventService = {
  getEvents: () => api.get('/events'),
  createEvent: (data: CreateEventData) => api.post('/events', data),
}
```

## 🎨 Styling Guidelines

### Tailwind CSS

Use Tailwind utility classes for styling:

```tsx
<div className="glass-card shadow-aurora rounded-xl p-6">
  <h2 className="mb-4 text-2xl font-bold text-white">Title</h2>
  <p className="text-gray-300">Content</p>
</div>
```

### Custom CSS Classes

Custom utilities are defined in `src/styles/globals.css`:

- `.glass-card` - Glassmorphism card effect
- `.btn-aurora` - Aurora-styled button
- `.btn-glass` - Glass-styled button
- `.shadow-aurora` - Aurora glow shadow
- `.animate-aurora` - Aurora animation

## 🔧 Configuration

### Environment Variables

Copy `.env.example` to `.env.local` and configure:

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000/ws
VITE_APP_NAME=GatherHub
```

## 📱 Responsive Design

The application is mobile-first and responsive:

- **Mobile**: 320px - 768px
- **Tablet**: 768px - 1024px
- **Desktop**: 1024px+

Use Tailwind responsive prefixes:

```tsx
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">
  {/* Responsive grid */}
</div>
```

## ♿ Accessibility

- Semantic HTML elements
- ARIA attributes
- Keyboard navigation
- Screen reader support
- High contrast mode
- Focus management

## 🚀 Performance

### Optimization Features

- **Code Splitting**: Automatic route-based splitting
- **Tree Shaking**: Dead code elimination
- **Asset Optimization**: Image and font optimization
- **Lazy Loading**: Component lazy loading
- **Memoization**: React.memo and useMemo

## 🔄 Integration with Backend

The frontend is designed to integrate with the Django backend:

- **API**: RESTful API communication
- **WebSocket**: Real-time updates
- **Authentication**: JWT token-based auth
- **File Upload**: Media handling

## 📦 Deployment

### Build for Production

```bash
npm run build
```

### Deployment Options

1. **Static Hosting** (Vercel, Netlify)
2. **CDN** (Cloudflare, AWS CloudFront)
3. **Docker** (with nginx)
4. **Server** (Express.js, nginx)

## 🤝 Contributing

1. Follow the established code style
2. Use TypeScript for type safety
3. Write meaningful component names
4. Test your changes
5. Update documentation

---

**Built with ❤️ using modern web technologies**
