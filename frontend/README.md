<<<<<<< HEAD
# EduTwin — Adaptive Learning Platform

> A modern, gamified coding-education web app that adapts explanations to each learner's style while tracking confidence, quiz scores, and progress — all wrapped in a candy-pastel glassmorphism UI.

![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.9-3178C6?logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-7-646CFF?logo=vite&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/Tailwind_CSS-3.4-06B6D4?logo=tailwindcss&logoColor=white)
![Framer Motion](https://img.shields.io/badge/Framer_Motion-12-FF0055?logo=framer&logoColor=white)

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [Available Scripts](#available-scripts)
- [Pages & Routes](#pages--routes)
- [Architecture Overview](#architecture-overview)
- [Configuration](#configuration)
- [Contributing](#contributing)
- [License](#license)

---

## Features

| Category | Highlights |
|---|---|
| **Adaptive Explanations** | Four learning modes — Visual, Simplified, Logical, Analogy — so every concept clicks |
| **Confidence Tracker** | Slider-based self-assessment with emoji feedback, persisted via context |
| **Interactive Quizzes** | Timed question flow with glitter celebrations, wrong-answer popups, and score review |
| **Video Learning** | Embedded React Player with custom play/pause overlay & progress bar |
| **Analytics Dashboard** | Area charts (Recharts), stat cards, weak-topic identification |
| **Leaderboard** | Global ranking with XP, badges, and avatar display |
| **Progress Page** | Per-topic understanding feedback, completion rings, streak stats |
| **User Profile** | Avatar picker (DiceBear), wallpaper themes (160+ options), notes with CRUD, motivational quotes |
| **Notifications** | Context-driven reminders for pending topics & congrats for completed ones |
| **Responsive Design** | Desktop sidebar + mobile slide-out drawer with search & difficulty toggle |
| **Glassmorphism UI** | Reusable `GlassCard`, `GradientButton`, `InputField`, `ProgressRing`, `StatCard` components |
| **Animated Backgrounds** | Configurable blob gradients & full-screen wallpaper images |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Framework** | React 19 with TypeScript |
| **Build Tool** | Vite 7 |
| **Styling** | Tailwind CSS 3.4 + custom candy/brand tokens |
| **Animations** | Framer Motion 12 |
| **Routing** | React Router DOM 7 |
| **Charts** | Recharts 3 |
| **Video** | React Player 3 |
| **HTTP Client** | Axios (pre-configured with interceptor for future auth) |
| **Utilities** | clsx + tailwind-merge (`cn()` helper) |
| **Icons** | Lucide React |
| **Linting** | ESLint 9 + typescript-eslint |

---

## Project Structure

```
edutwin-frontend/
├── index.html                          # Entry HTML
├── package.json                        # Dependencies & scripts
├── vite.config.ts                      # Vite configuration
├── tailwind.config.ts                  # Tailwind theme (brand colors, candy palette, blob animation)
├── postcss.config.js                   # PostCSS (Tailwind + Autoprefixer)
├── tsconfig.json                       # TypeScript project references
├── tsconfig.app.json                   # TS config for src/
├── tsconfig.node.json                  # TS config for Vite config
├── eslint.config.js                    # ESLint flat config
├── public/                             # Static assets served at root
│   └── vite.svg
│
└── src/
    ├── main.tsx                        # App entry — providers & root render
    ├── App.tsx                         # Route definitions
    ├── index.css                       # Global Tailwind directives & utilities
    │
    ├── components/
    │   ├── layout/                     # Shell / navigation components
    │   │   ├── Navbar.tsx              # Fixed top bar with logo, nav, notifications, avatar
    │   │   ├── Sidebar.tsx             # Desktop left sidebar with links & search
    │   │   ├── MobileDrawer.tsx        # Slide-out drawer for mobile navigation
    │   │   └── PageWrapper.tsx         # Page container with animated background
    │   │
    │   ├── learning/                   # Topic-learning interaction components
    │   │   ├── ConfidenceSlider.tsx    # Self-assessment slider with emoji feedback
    │   │   ├── ExplanationSelector.tsx # Four-mode explanation type picker
    │   │   └── VideoTrackerUI.tsx      # Video player with custom controls
    │   │
    │   ├── profile/                    # User profile related components
    │   │   ├── ProfileAvatar.tsx       # Avatar display & DiceBear picker modal
    │   │   ├── WallpaperSettings.tsx   # 160+ wallpaper themes (pastel, dark, gaming, aesthetic)
    │   │   ├── NoteSection.tsx         # CRUD notes with importance, pinning, search
    │   │   └── MotivationalQuotes.tsx  # Auto-rotating quote cards with daily challenge
    │   │
    │   ├── ui/                         # Reusable presentational components
    │   │   ├── GlassCard.tsx           # Frosted-glass container with optional hover effect
    │   │   ├── GradientButton.tsx      # Primary / secondary / outline animated button
    │   │   ├── InputField.tsx          # Form input with icon, label, error state
    │   │   ├── ProgressRing.tsx        # SVG circular progress indicator
    │   │   └── StatCard.tsx            # Metric card with icon & trend badge
    │   │
    │   └── visuals/
    │       └── BackgroundBlobs.tsx     # Animated gradient blobs / wallpaper backgrounds
    │
    ├── context/                        # React Context providers (global state)
    │   ├── NotificationContext.tsx     # Notification CRUD with localStorage persistence
    │   ├── UnderstandingContext.tsx    # Per-topic confidence scores & averages
    │   └── UserPreferencesContext.tsx  # Avatar & wallpaper preferences
    │
    ├── lib/
    │   └── utils.ts                   # cn() — clsx + tailwind-merge helper
    │
    ├── pages/                         # Route-level page components
    │   ├── SignIn.tsx                  # Login page
    │   ├── SignUp.tsx                  # Registration page
    │   ├── Dashboard.tsx              # Main hub — stats, topic list, search history, videos
    │   ├── TopicView.tsx              # Topic detail — explanation modes, video, confidence
    │   ├── QuizPage.tsx               # Interactive quiz with scoring & review
    │   ├── Analytics.tsx              # Performance charts & weak areas
    │   ├── Leaderboard.tsx            # Global XP ranking
    │   ├── Progress.tsx               # Self-assessment history & completion stats
    │   └── UserProfile.tsx            # Profile editor, badges, notes, wallpaper
    │
    └── services/
        └── api.ts                     # Axios instance with base URL & interceptor stub
```

---

## Getting Started

### Prerequisites

- **Node.js** ≥ 18
- **npm** ≥ 9 (or **yarn** / **pnpm**)

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd edutwin-frontend

# Install dependencies
npm install
```

### Run Development Server

```bash
npm run dev
```

The app starts at **http://localhost:5173** (default Vite port).

---

## Available Scripts

| Command | Description |
|---|---|
| `npm run dev` | Start Vite dev server with HMR |
| `npm run build` | Type-check with `tsc` then build for production |
| `npm run preview` | Preview the production build locally |
| `npm run lint` | Run ESLint across all TS/TSX files |

---

## Pages & Routes

| Route | Page Component | Description |
|---|---|---|
| `/signin` | `SignIn` | Email & password login (navigates to dashboard) |
| `/signup` | `SignUp` | Account creation form |
| `/dashboard` | `Dashboard` | Learning hub — stats, topics, search history, watched videos |
| `/topic` | `TopicView` | Topic detail with 4 explanation modes, video player, confidence slider |
| `/quiz` | `QuizPage` | Interactive quiz — timed questions, celebrations, review |
| `/analytics` | `Analytics` | XP charts, accuracy stats, weak areas |
| `/leaderboard` | `Leaderboard` | Global ranking by XP and badges |
| `/progress` | `Progress` | Understanding history with self-assessment data |
| `/profile` | `UserProfile` | Avatar, wallpaper, badges, language skills, notes, quotes |
| `*` | — | Redirects to `/signin` |

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                     main.tsx                        │
│  UserPreferencesProvider → NotificationProvider     │
│    → UnderstandingProvider → <App />                │
└────────────────────────┬────────────────────────────┘
                         │
                    React Router
                         │
          ┌──────────────┼──────────────┐
          │              │              │
     Auth Pages     App Pages     Profile Page
    (SignIn/Up)   (Dashboard,     (UserProfile)
                   TopicView,
                   Quiz, etc.)
                         │
              ┌──────────┼──────────┐
              │          │          │
          Layout     Learning     UI Components
         (Navbar,   (Confidence,  (GlassCard,
         Sidebar,   Explanation,   GradientButton,
         Drawer)    VideoTracker)  ProgressRing)
```

**State Management**: Three React Context providers handle global state with `localStorage` persistence:

- **UserPreferencesContext** — avatar & wallpaper theme
- **NotificationContext** — in-app notifications (reminders & congrats)
- **UnderstandingContext** — per-topic confidence scores

---

## Configuration

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `VITE_API_URL` | `http://localhost:5000/api` | Backend API base URL |

Create a `.env` file in the project root:

```env
VITE_API_URL=http://localhost:5000/api
```

### Tailwind Theme

The custom design system is defined in `tailwind.config.ts`:

- **Brand colors**: `brand`, `brand-light`, `brand-dark`, `brand-accent`
- **Status colors**: `success`, `warning`, `error`, `info`
- **Candy palette**: `pink`, `peach`, `mint`, `lavender`, `lemon`, `sky`
- **Animations**: `blob` keyframe for floating background blobs

---

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m "feat: add my feature"`
4. Push to the branch: `git push origin feature/my-feature`
5. Open a Pull Request

---

## License

This project is for educational purposes. All rights reserved.
=======
# React + TypeScript + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) (or [oxc](https://oxc.rs) when used in [rolldown-vite](https://vite.dev/guide/rolldown)) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```

You can also install [eslint-plugin-react-x](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://github.com/Rel1cx/eslint-react/tree/main/packages/plugins/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])
```
>>>>>>> fff541230f2ea326096f9f7bf3bb0b31c06d86a8
