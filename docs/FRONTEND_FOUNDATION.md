# Frontend Foundation

The Phase 7 React frontend foundation is established for the Groundwater Quality Intelligence System. It serves as the framework for building out the comprehensive analytics dashboard in Phase 8.

## Stack & Technologies
- **React 18** + **TypeScript**
- **Vite** (Build tool)
- **Tailwind CSS v4** (Styling & Design System)
- **React Router** (Client-side routing)
- **TanStack Query v5** (Server state management & caching)
- **Axios** (API client)
- **React-Leaflet** / **Leaflet** (GIS Map foundation)
- **Lucide React** (Iconography)

## Project Structure
```
frontend/
├── src/
│   ├── api/
│   │   ├── client.ts         # Centralized Axios instance configuration
│   │   └── endpoints.ts      # Typed API service functions
│   ├── components/
│   │   ├── layout/           # AppLayout, Sidebar, TopNav
│   │   └── ui/               # Reusable primitives (Card, Badge, StatCard, EmptyState, etc.)
│   ├── hooks/
│   │   └── useWawqi.ts       # React Query custom hooks (useOverview, useStates, etc.)
│   ├── pages/                # Route components (Dashboard, StatesOverview, MapPage, etc.)
│   ├── types/                # TypeScript interfaces (ApiResponse, OverviewStats, WawqiCategory, etc.)
│   ├── App.tsx               # Route definitions
│   └── main.tsx              # QueryClient setup and App bootstrap
├── tailwind.config.js        # Custom design tokens & semantic colors
├── postcss.config.js         # PostCSS plugins (@tailwindcss/postcss)
└── tsconfig.json             # TypeScript compiler settings
```

## Architectural Principles

### 1. Separation of Concerns
- **API Fetching**: Handled strictly via Axios in `src/api/endpoints.ts`. UI components never fetch directly.
- **Server State**: `useQuery` hooks in `src/hooks/useWawqi.ts` manage caching, loading states, and retries.
- **Dumb Components**: UI primitives (`Card`, `Badge`) accept props and have no knowledge of the API.
- **Smart Pages**: Pages consume hooks and coordinate layout.

### 2. Design System
- Semantic WAWQI color mapping explicitly built into Tailwind config (`wawqi-excellent`, `wawqi-poor`, etc.).
- Dark-mode primary aesthetic: `#0F172A` (background), `#1E293B` (surfaces).
- Bordered, compact analytics layout optimized for dense data.

### 3. State Management & Query Strategy
- Global state managed entirely by **TanStack Query** (no Redux required).
- `staleTime` set to 5 minutes to prevent redundant requests across route transitions, given the underlying data (PostgreSQL analytical views) updates infrequently.
- Re-fetches disabled on window focus to conserve backend resources.

### 4. Resiliency & Type Safety
- Frontend explicitly mirrors backend interfaces (`total_samples`, `eligible_samples`, etc.).
- Centralized UI states: `Skeleton` for loading, `ErrorState` for failed queries, and `EmptyState` for missing data.

## Next Steps (Phase 8)
- Fully implement analytical charts using **Recharts**.
- Bind pagination params to `Extremes` and `GIS Map` views.
- Render actual GIS points via `React-Leaflet` on the `MapPage`.
