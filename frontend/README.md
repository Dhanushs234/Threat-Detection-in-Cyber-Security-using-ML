# ThreatSense Frontend

Network Intrusion Detection System - React + TypeScript + Vite Frontend

---

## 🚀 Tech Stack

### Core
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool & dev server
- **React Router DOM** - Client-side routing

### Styling
- **Tailwind CSS** - Utility-first CSS framework
- **Framer Motion** - Smooth animations & transitions

### Charts & Visualization
- **Recharts** - Primary charting library
- **d3-scale** - Scale helpers (no direct DOM manipulation)

### Real-time Communication
- **Socket.IO Client** - WebSocket connection to backend

### UI Components
- **Heroicons** - Icon library
- **clsx** - Conditional class names

---

## 📦 Installation

```bash
cd frontend
npm install
```

---

## 🏃 Development

```bash
npm run dev
```

Frontend runs on: **http://127.0.0.1:3000**

#### Windows (Command Prompt)

If `npm run dev` exits immediately, run it through `cmd /c` so Vite keeps running:

```bat
cmd /c npm run dev -- --host 0.0.0.0 --port 3000
```

Backend proxy configured for: **http://127.0.0.1:8000**

---

## 🏗️ Build

```bash
npm run build
```

Output: `dist/` directory

---

## 🔍 Preview Production Build

```bash
npm run preview
```

---

## 📁 Project Structure

```
frontend/
├── assets/
│   ├── logo/
│   │   └── logo.png
│   └── icons/
│
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx
│   │   ├── Topbar.tsx
│   │   └── Footer.tsx
│   │
│   ├── Logo/
│   │   ├── ThreatSenseLogo.jsx
│   │   └── ThreatSenseLogo.css
│   │
│   ├── kpi/
│   │   └── KpiCard.tsx
│   │
│   ├── charts/
│   │   ├── StackedTimeline.tsx
│   │   ├── SeverityPie.tsx
│   │   ├── ModelComparison.tsx
│   │   └── ConfusionMatrix.tsx
│   │
│   └── tables/
│       ├── MiniLogTable.tsx
│       ├── DetectionLogTable.tsx
│       └── BlockedThreatTable.tsx
│
├── pages/
│   ├── Dashboard.tsx
│   ├── ThreatMonitoring.tsx
│   ├── ManualDetection.tsx
│   ├── ModelMetrics.tsx
│   └── About.tsx
│
├── services/
│   ├── socket.ts
│   └── api.ts
│
├── store/
│   └── detectionStore.ts
│
├── styles/
│   └── theme.css
│
├── App.tsx
├── main.tsx
├── index.html
├── vite.config.ts
├── tsconfig.json
├── tailwind.config.js
└── package.json
```

---

## 🌐 Routes

- `/` - Dashboard (overview, KPIs, charts)
- `/monitoring` - Threat Monitoring (live detection feed)
- `/manual` - Manual Detection (user input form)
- `/metrics` - Model Metrics (RF/IF performance)
- `/about` - About (system info)

---

## 🔌 Backend Integration

### API Proxy

All `/api/*` requests are proxied to backend at `http://127.0.0.1:8000`

Example:
```typescript
// Frontend request
fetch('/api/health')

// Proxied to
http://127.0.0.1:8000/health
```

### WebSocket Connection

```typescript
import { io } from 'socket.io-client'

const socket = io('http://127.0.0.1:8000')
```

---

## 🎨 Tailwind Configuration

### Custom Colors

```javascript
colors: {
  threat: {
    critical: '#dc2626',
    high: '#ea580c',
    medium: '#f59e0b',
    low: '#10b981',
    normal: '#3b82f6',
  },
  dark: {
    bg: '#0a0a0a',
    card: '#1a1a1a',
    border: '#2a2a2a',
  },
}
```

### Custom Components

- `.card` - Card container
- `.card-header` - Card header
- `.card-body` - Card body
- `.btn-primary` - Primary button
- `.btn-danger` - Danger button
- `.btn-success` - Success button

---

## 🔒 Global Rules

### ❌ DO NOT

- Modify ML/detection logic
- Modify backend APIs
- Poll backend (use WebSocket)
- Overload UI (performance first)
- Hardcode data
- Use experimental chart libraries

### ✅ DO

- Use WebSocket for live updates
- Keep UI stable & smooth
- Follow TypeScript best practices
- Use Recharts for all charts
- Maintain performance optimization

---

## 📊 Performance Optimization

### Code Splitting

Configured in `vite.config.ts`:
- `react-vendor` - React core libraries
- `chart-vendor` - Recharts & d3-scale
- `ui-vendor` - Framer Motion & clsx

### Build Settings

- Minification: Terser
- Source maps: Disabled in production
- Manual chunks for optimal loading

---

## 🧪 Linting

```bash
npm run lint
```

ESLint configured with:
- TypeScript support
- React hooks rules
- React refresh plugin

---

## 🚨 Important Notes

1. **Dependencies must be installed** before running dev server
2. **Backend must be running** on port 8000 for API/WebSocket
3. **Logo image** should be placed at `assets/logo/logo.png`
4. **TypeScript errors** will resolve after `npm install`
5. **Tailwind warnings** in CSS are normal (PostCSS processes them)

---

## 🔧 Environment

- Node.js: 16+ recommended
- Package manager: npm
- Port: 3000 (frontend)
- Backend: 8000 (required)

---

## 📝 Next Steps

1. Install dependencies: `npm install`
2. Start backend: `cd ../backend && python main.py`
3. Start frontend: `npm run dev`
4. Open browser: `http://127.0.0.1:3000`

---

**Frontend Status:** ✅ CONFIGURED  
**Dependencies:** ⏳ PENDING INSTALL  
**Build Tool:** ✅ VITE  
**Styling:** ✅ TAILWIND CSS  
**Charts:** ✅ RECHARTS  
**Real-time:** ✅ SOCKET.IO
