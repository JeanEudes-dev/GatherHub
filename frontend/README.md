# GatherHub Frontend

Welcome to the GatherHub Frontend! This application provides a modern, intuitive, and responsive user interface for interacting with the GatherHub platform. Built with cutting-edge technologies, it features a stunning aurora/glassmorphism design system, smooth animations, and a focus on user experience.

## 🌟 Project Overview

The GatherHub frontend is a single-page application (SPA) that allows users to:
- Discover, create, and manage community events.
- Collaborate on event-related tasks.
- Participate in polls and voting for collective decision-making.
- Manage their user profile and settings.
- Receive real-time updates for events, tasks, and votes.

It communicates with the GatherHub backend API for data persistence and real-time functionalities via WebSockets.

## 🚀 Tech Stack

- **React 19**: Leverages the latest features of React for building dynamic user interfaces.
- **Vite 6**: Provides a lightning-fast development server and optimized build process.
- **TypeScript**: Ensures type safety and improves code maintainability.
- **Tailwind CSS 3.4**: A utility-first CSS framework for rapid UI development.
- **shadcn/ui**: A collection of beautifully designed, accessible UI components.
- **Framer Motion**: Powers smooth animations and transitions throughout the application.
- **Zustand**: A lightweight and flexible state management solution.
- **React Router DOM v6**: Handles client-side routing and navigation.
- **Axios**: A promise-based HTTP client for making API requests.
- **Lucide React**: A comprehensive library of beautiful and consistent icons.
- **React Hot Toast**: Provides elegant notifications.

## 🎨 Design System & Styling

The frontend features a modern aurora/glassmorphism design:
- **Aurora Background**: Animated gradient orbs create a visually appealing backdrop.
- **Glassmorphism**: Translucent elements with blur effects give a sense of depth.
- **Neon Accents**: Glowing interactive elements enhance user engagement.
- **Responsive Design**: A mobile-first approach ensures seamless experience across all devices.
- **Dark Theme**: Optimized for dark mode interfaces, providing visual comfort.

### Styling Approach
- **Tailwind CSS**: The primary method for styling. Utility classes are used extensively for building layouts and components. See `tailwind.config.js` for configuration.
- **Custom CSS**: Global styles, custom utility classes, and aurora/glass effects are defined in `src/styles/globals.css` and `src/index.css`.
  - Key custom classes include `.glass-card`, `.btn-aurora`, `.shadow-aurora`, etc.
- **shadcn/ui Theme**: Components from `shadcn/ui` are themed to match the GatherHub design system. Configuration can be found in `components.json` and related CSS variables.

## 📁 Project Structure

The `src` directory is organized as follows:

```
src/
├── assets/            # Static assets like images, fonts.
├── components/        # Shared, reusable UI components.
│   ├── layout/       # Components defining the overall page structure (e.g., Navbar, Footer, Layout).
│   └── ui/           # Generic UI elements, often customized versions of shadcn/ui components or base elements.
├── features/         # Components specific to a particular feature or domain.
│   ├── auth/         # Authentication-related components (e.g., LoginForm, RegisterForm).
│   ├── events/       # Event-specific components (e.g., EventCard, EventForm).
│   ├── tasks/        # Task management components.
│   └── voting/       # Voting and polling components.
├── hooks/            # Custom React hooks for reusable logic.
├── lib/              # Utility functions, constants, and helper modules.
│   ├── constants.ts  # Application-wide constants.
│   └── utils.ts      # General utility functions.
├── pages/            # Top-level components representing application pages/routes.
├── services/         # Modules responsible for API communication.
│   ├── authService.ts
│   ├── eventService.ts
│   ├── taskService.ts
│   ├── votingService.ts
│   └── websocketService.ts # Handles WebSocket connections and messages.
├── store/            # Zustand state management stores.
│   ├── authStore.ts
│   ├── eventStore.ts
│   ├── taskStore.ts
│   └── votingStore.ts
├── styles/           # Global stylesheets and Tailwind CSS base.
│   └── globals.css
├── types/            # TypeScript type definitions and interfaces.
│   └── index.ts      # Main export for types.
├── App.tsx           # Main application component, sets up routing.
├── main.tsx          # Entry point of the application.
└── index.css         # Root CSS file, imports global styles.
```

## 🛠️ Development Setup

### Prerequisites

- Node.js 18+ (recommended: 20+)
- npm or yarn (this guide uses npm)

### Quick Start

1.  **Clone the repository** (if you haven't already):
    ```bash
    git clone https://github.com/JeanEudes-dev/GatherHub.git
    cd GatherHub/frontend
    ```
2.  **Install dependencies**:
    ```bash
    npm install
    ```
3.  **Configure Environment Variables**:
    Copy the `.env.example` file to a new file named `.env.local` in the `frontend` directory:
    ```bash
    cp .env.example .env.local
    ```
    Update `.env.local` with your backend API URL and WebSocket URL:
    ```env
    VITE_API_BASE_URL=http://localhost:8000/api/v1
    VITE_WS_URL=ws://localhost:8000/ws
    VITE_APP_NAME=GatherHub
    ```
    (Adjust if your backend runs on a different port or path)

4.  **Start the development server**:
    ```bash
    npm run dev
    ```
5.  **Open your browser** and navigate to `http://localhost:5173` (or the port Vite assigns).

### Available Scripts

- `npm run dev`: Starts the development server with Hot Module Replacement (HMR).
- `npm run build`: Builds the application for production in the `dist/` directory.
- `npm run preview`: Serves the production build locally for previewing.
- `npm run lint`: Lints the codebase using ESLint.
- `npm run lint:fix`: Automatically fixes ESLint errors and warnings.
- `npm run format`: Formats the code using Prettier.
- `npm run type-check`: Runs TypeScript type checking.

## 🧩 Component Library

GatherHub Frontend utilizes `shadcn/ui` for its base component library, providing beautiful, accessible, and customizable components.

### Using shadcn/ui Components
- Components are added via the `shadcn-ui` CLI.
- They are typically stored in `src/components/ui/`.
- These components are highly composable and can be styled using Tailwind CSS.

**To add a new `shadcn/ui` component:**
```bash
npx shadcn-ui@latest add [component-name]
```
Example: `npx shadcn-ui@latest add button card dialog`

### Custom Components
- **Shared Components**: Reusable components not specific to any single feature are placed in `src/components/ui/` (for general UI elements) or `src/components/layout/` (for structural elements).
- **Feature-Specific Components**: Components tied to a particular domain (e.g., event creation, task display) reside within the respective `src/features/[featureName]/` directory. This promotes modularity and co-location of feature-specific logic and UI.

When creating custom components, prioritize reusability, accessibility, and adherence to the established design system.

## ⚙️ Routing

Client-side routing is managed by **React Router DOM v6**.
- **Configuration**: Routes are defined in `src/App.tsx`.
- **Layouts**: A primary `<Layout />` component in `src/components/layout/` wraps page views, providing consistent navigation and structure.
- **Protected Routes**: The `<ProtectedRoute />` component in `src/App.tsx` handles authentication checks for routes requiring a logged-in user.
- **Page Components**: Each route typically maps to a component in the `src/pages/` directory.

Example of a route definition in `App.tsx`:
```tsx
<Route path="/events" element={<EventListPage />} />
<Route element={<ProtectedRoute />}>
  <Route path="/profile" element={<ProfilePage />} />
</Route>
```

## 🎯 State Management with Zustand

Zustand is used for global state management, offering a simple and unopinionated way to manage application state.

### Store Structure
- Stores are located in the `src/store/` directory (e.g., `authStore.ts`, `eventStore.ts`).
- Each store is created using Zustand's `create` function.
- Stores typically define:
    - **State**: The data held by the store.
    - **Actions**: Functions that modify the state.
    - **Selectors**: (Often implicitly part of the hook) Functions to access parts of the state.

### Using Stores in Components
Import the store's hook into your component to access state and actions:
```tsx
import { useAuthStore } from '../store/authStore';

function MyComponent() {
  const { user, login, logout } = useAuthStore();

  // Use state: user
  // Call actions: login(userData), logout()
}
```

### Persisting State
For state that needs to persist across sessions (like authentication status), Zustand's `persist` middleware can be used, often in conjunction with `localStorage`. The `authStore.ts` demonstrates this for rehydrating authentication state.

## 🌐 API Integration

Communication with the GatherHub backend API is handled through services defined in the `src/services/` directory.

- **Axios**: Used as the HTTP client. A pre-configured Axios instance can be found (or created) for base URL and request/response interceptors (e.g., for attaching JWT tokens).
- **Service Modules**: Each module (e.g., `eventService.ts`) groups API calls related to a specific resource.
- **Environment Variables**: The API base URL is configured via `VITE_API_BASE_URL` in `.env.local`.

Example of a service function in `src/services/eventService.ts`:
```typescript
import axios from 'axios'; // Or a pre-configured instance

// Example: If VITE_API_BASE_URL is 'http://localhost:8000/api/v1'
// then API_URL will be 'http://localhost:8000/api/v1/events'
const API_URL = `${import.meta.env.VITE_API_BASE_URL}/events`;

export const eventService = {
  getEvents: async () => {
    const response = await axios.get(API_URL);
    return response.data;
  },
  createEvent: async (data: CreateEventData) => {
    const response = await axios.post(API_URL, data);
    return response.data;
  },
};
```

## 🔌 Real-time Features with WebSockets

The frontend uses WebSockets for real-time communication with the backend (e.g., live updates for events, tasks, votes).
- **Setup**: `websocketService.ts` in `src/services/` manages WebSocket connections.
- **URL**: The WebSocket URL is configured via `VITE_WS_URL` in `.env.local`.
- **Integration**: Stores (like `eventStore.ts`) or components can subscribe to WebSocket messages to update the UI in real-time.

## 🏗️ Building for Production

To build the application for production:
```bash
npm run build
```
This command bundles the application, optimizes assets, and outputs the static files to the `dist/` directory.

To preview the production build locally:
```bash
npm run preview
```

## 🚀 Performance Optimization

Several strategies are employed to ensure optimal performance:
- **Code Splitting**: Vite automatically splits code by routes (dynamic imports for pages).
- **Tree Shaking**: Unused code is eliminated during the build process.
- **Asset Optimization**: Images and other assets are optimized.
- **Lazy Loading**: React.lazy and Suspense can be used for components that are not immediately needed.
- **Memoization**: `React.memo`, `useMemo`, and `useCallback` are used where appropriate to prevent unnecessary re-renders.

## ♿ Accessibility (A11y)

Accessibility is a priority. We strive to follow WCAG guidelines by:
- Using semantic HTML elements.
- Ensuring proper ARIA attributes where necessary.
- Providing keyboard navigation.
- Testing with screen readers.
- Maintaining good color contrast (though the aurora/glassmorphism design needs careful attention here).
- Managing focus for interactive elements.
`shadcn/ui` components are built with accessibility in mind.

## 🔄 Integration with Backend

- **API Endpoints**: The frontend consumes RESTful API endpoints provided by the Django backend.
- **Authentication**: JWT (JSON Web Tokens) are used for authentication. Tokens are stored securely (e.g., in `localStorage`) and sent with API requests. Token refresh mechanisms are handled by `authStore` and `authService`.
- **Data Flow**: Typically, components request data via service functions, which make API calls. State is updated in Zustand stores, and components re-render with new data.

## 📦 Deployment

The production build in the `dist/` directory consists of static assets and can be deployed to various platforms:
1.  **Static Hosting Services**: Vercel, Netlify, GitHub Pages.
2.  **CDN**: AWS CloudFront, Cloudflare.
3.  **Docker**: Containerize with a web server like Nginx to serve static files.
4.  **Traditional Web Server**: Serve the `dist/` folder using Nginx or Apache.

## 🤝 Contributing

Contributions are welcome! Please adhere to the following guidelines:
1.  Follow the established code style (ESLint, Prettier).
2.  Use TypeScript for all new code.
3.  Write clear, concise, and well-documented code.
4.  Ensure components are reusable and accessible.
5.  Test your changes thoroughly.
6.  Update documentation if your changes affect existing functionality or add new features.
7.  Create an issue to discuss significant changes before starting work.

---

**Built with ❤️ and modern web technologies to bring communities together.**
If you have questions or encounter issues, please raise them on the project's GitHub Issues page.
