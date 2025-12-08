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

# Set port via environment variable or use --port flag
export VITE_PORT=5173  # Optional: Vite defaults to 5173
npm run dev
```

The dev server runs on `http://localhost:5173` (or configured port). The UI proxies `/api/*` calls to the Flask backend.

**Environment Variables:**
- `VITE_BACKEND_URL` - Backend API URL (default: `http://localhost:5004`)
- `VITE_PORT` - Port for Vite dev server (default: `5173`)
- `VITE_DEV_MODE` - Set to `true` to enable dev mode features like user reset (default: `false`)
- `VITE_LOG_LEVEL` - Logging level: DEBUG, INFO, WARN, ERROR, NONE (default: DEBUG in dev, INFO in production)
- `VITE_LOGGING_ENABLED` - Set to `false` to disable logging (default: `true`)

See `.env.example` for all available configuration options.

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

## E2E Testing

The project uses [Playwright](https://playwright.dev/) for end-to-end testing. Tests are located in the `e2e/` directory.

### Prerequisites

- Playwright browsers must be installed (run once):
  ```bash
  npx playwright install chromium
  ```

### Running Tests

Both the backend and frontend servers must be running for E2E tests to work properly.

1. **Start the Flask backend** (in one terminal):
   ```bash
   cd ../backend
   source .venv/bin/activate  # or activate your virtual environment
   export FLASK_RUN_PORT=5004  # Optional
   flask --app app run --debug --port 5004 --host 0.0.0.0
   ```

2. **Start the frontend dev server** (in another terminal):
   ```bash
   cd frontend
   export VITE_PORT=5003  # Optional
   export FRONTEND_PORT=5003  # For Playwright tests
   npm run dev -- --port 5003
   ```

3. **Run the tests** (in a third terminal):
   ```bash
   cd frontend
   export BACKEND_PORT=5004  # Optional: defaults to 5004
   export FRONTEND_PORT=5003  # Optional: defaults to 5003
   export VITE_BACKEND_URL=http://localhost:5004  # Optional
   npm run test:e2e
   ```

   Or run with UI mode for debugging:
   ```bash
   npm run test:e2e:ui
   ```

### Test Structure

- Tests are located in the `e2e/` directory
- See `e2e/TEST_COVERAGE.md` for a comprehensive list of all tests organized by category
- Tests verify that pages load correctly and interactive elements have proper test IDs
- The Playwright config (`playwright.config.ts`) uses `FRONTEND_PORT` environment variable (default: 5003) and will reuse an existing dev server if one is running

### Test Files

- `page-load.spec.ts` - Basic page load verification
- `learner-management.spec.ts` - Learner CRUD operations
- `dashboard.spec.ts` - Dashboard UI and navigation
- `practice-flow.spec.ts` - Practice session interactions
- `session-submission.spec.ts` - Session completion and submission
- `test-flow.spec.ts` - Test sessions and eligibility
- `leveling.spec.ts` - Level progression functionality
- `achievements.spec.ts` - Achievement earning and display
- `journey-page.spec.ts` - Journey/Progress page features
- `summary-page.spec.ts` - Practice summary page

### Test Data IDs

Interactive UI elements have `data-testid` attributes for reliable test targeting:
- `testid-answer-input` - Answer input field
- `testid-check-answer-button` - Check Answer button
- `testid-next-button` / `testid-previous-button` - Navigation buttons
- `testid-flag-button` - Flag for Review button
- `testid-submit-session-button` - Submit Session button
- `testid-student-card-{id}` - Student selection cards
- And more - see component files for complete list

## Verification checklist

1. `npm run lint` – ESLint + TypeScript sanity check.
2. `npm run build` – Confirms Tailwind + Vite production output works.
3. `npm run test:e2e` – Run E2E tests (requires dev server running).
4. Manual – Run `npm run dev`, ensure the dashboard renders, add a mock student via the modal, and verify stats/achievements animate correctly.

Record additional UI or workflow changes here so backend and curriculum teams can follow along without digging through commit history.

