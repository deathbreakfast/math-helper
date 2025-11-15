# Frontend (React + Vite)

The Math Helper frontend pairs Vite + React 19 with Tailwind CSS, Framer Motion, and Lucide icons to deliver the updated learner dashboard mock. The hero simply frames the experience, while the rest of the page animates between student cards, streak stats, and achievements using local-only prototype data.

## Prerequisites

| Tool | Version | Notes |
| --- | --- | --- |
| Node.js | >= 20.19.0 | Vite 7 + `@vitejs/plugin-react@5` require this. Using Node 20.10.0 works with warnings; upgrade when convenient to silence them. |
| npm | 10+ | Bundled with Node 20. |

## Install & run

```bash
cd frontend
npm install
npm run dev
```

The dev server runs on `http://localhost:5173`. During this local-only phase the UI does not call the backend, so you can iterate on visuals without needing Flask online.

## Styling system

- **Tailwind CSS v3** provides the utility-first layer. The config at `tailwind.config.js` scans `index.html` and every file in `src/`.
- **PostCSS + Autoprefixer** run through `postcss.config.js`.
- Global directives (`@tailwind base/components/utilities`) and the background gradient live in `src/index.css`.
- **Framer Motion** powers entrance/hover animations, while **Lucide React** supplies icons.

If you add new folders under `src/`, update `tailwind.config.js` so purge keeps the generated classes.

## App structure

- `src/components/MathDashboard.tsx` – bundles the hero copy, student selector grid, progress cards, achievements rail, and the modal for adding local-only mock learners. Everything runs against the `SAMPLE_USERS` seed while backend endpoints evolve.
- `src/App.tsx` – renders the dashboard.
- `src/main.tsx` – Vite bootstrapper with Strict Mode and global style import.

Replace `SAMPLE_USERS` with `GET /api/users` data when you are ready to wire up the backend. The component structure already matches the expected payload shape.

## Verification checklist

1. `npm run lint` – ESLint + TypeScript sanity check.
2. `npm run build` – Confirms Tailwind + Vite production output works.
3. Manual – Run `npm run dev`, ensure the dashboard renders, add a mock student via the modal, and verify stats/achievements animate correctly.

Record additional UI or workflow changes here so backend and curriculum teams can follow along without digging through commit history.

