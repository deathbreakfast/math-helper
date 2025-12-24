# Code Review

We are reviewing the codebase after major changes to ensure it remains maintainable, coherent, and free of stale or dead code. This document focuses on **dead code**, **complexity hotspots**, **large files/functions**, **antipatterns**, **directory structure**, and **missed architectural patterns**.

This is intended to be a living document (similar to `TEST_REVIEW.md`) that gets updated whenever major refactors or feature shifts occur.

## Scope & Method

This review is based on:
- Static repo inspection (directory map, file sizes/line counts)
- Heuristic complexity analysis for Python backend functions (approximate cyclomatic complexity)
- Targeted greps for deprecated/test-removed code paths and likely stale frontend mappings

## Statistics

### Largest Source Files (by lines)

These are the **largest “real source” files** (excluding `__pycache__`, `.venv`, Playwright artifacts, coverage output):

**Backend**
- `backend/app/services/question_service.py` (~676 LOC)
- `backend/app/services/practice_service.py` (~562 LOC)
- `backend/app/config/achievements/milestone.py` (~541 LOC)
- `backend/app/services/achievement_service.py` (~524 LOC)
- `backend/app/routes/practice.py` (~516 LOC)
- `backend/app/config/levels_config.py` (~470 LOC)
- `backend/app/services/achievements/achievement_queries/achievement_query_service.py` (~404 LOC)

**Frontend**
- `frontend/src/features/practice/hooks/usePracticeSession.ts` (~403 LOC)
- `frontend/src/features/students/LearnersDashboard.tsx` (~383 LOC)
- `frontend/src/features/students/data/mathConcepts.ts` (~390 LOC)

**Note:** Several large frontend files are *tests*; those are less concerning than large production modules, but still worth keeping tidy.

### Largest / Most Complex Backend Functions (Python)

Heuristic analysis (AST-based) found these as top hotspots in `backend/app`:

**Largest functions (LOC)**
- ✅ `AchievementQueryService.count_achievements_by_code_with_filters` (~207 LOC, **CC~54**) in `backend/app/services/achievements/achievement_queries/achievement_query_service.py` — **REFACTORED**: Split into smaller helper methods
- `complete_session` (~175 LOC, **CC~19**) in `backend/app/routes/practice.py`
- ✅ `SessionEngineService.generate_session` (~168 LOC, **CC~32**) in `backend/app/services/session_engine_service.py` — **REFACTORED**: Split into SessionResumeService, QuestionGenerationService, SessionFactory, and ConceptSelectionService
- ✅ `LevelMasterChecker.check` (~167 LOC, **CC~22**) in `backend/app/services/achievements/achievement_checkers/level_master_checker.py` — **REFACTORED**: Split into focused helper methods for level/concept queries, consecutive calculation, and tier determination
- ✅ `GenericAccuracyChecker.check` (~143 LOC, **CC~35**) in `backend/app/services/achievements/achievement_checkers/generic_accuracy_checker.py` — **REFACTORED**: Split complex decision tree into focused helper methods
- ✅ `QuestionService.generate_operands_with_constraints` (~129 LOC, **CC~31**) in `backend/app/services/question_service.py` — **REFACTORED**: Converted to pipeline pattern with strategy selection
- `QuestionService.generate_question` (~129 LOC, **CC~13**) in `backend/app/services/question_service.py`

**Most complex (estimated cyclomatic complexity)**
- ✅ `AchievementQueryService.count_achievements_by_code_with_filters` (**CC~54**) — **REFACTORED**: Split into smaller helper methods reducing complexity
- ✅ `GenericAccuracyChecker.check` (**CC~35**) — **REFACTORED**: Split complex decision tree into focused helper methods reducing complexity
- ✅ `SessionEngineService.generate_session` (**CC~32**) — **REFACTORED**: Split into focused services (SessionResumeService, QuestionGenerationService, SessionFactory, ConceptSelectionService) reducing complexity
- ✅ `QuestionService.generate_operands_with_constraints` (**CC~31**) — **REFACTORED**: Converted to pipeline pattern reducing complexity

**Interpretation:** These are the primary candidates for refactors that reduce cognitive load and defect risk.

## Repo Hygiene / Generated Artifacts

The following **generated/runtime artifacts** are present in the workspace and have shown up as “largest files”:
- **SQLite runtime files**: `backend/instance/math_helper.db*` (e.g. `*.db`, `*.db-wal`, `*.db-shm`)
- **Python virtual environment**: `backend/.venv/...`
- **Coverage output**: `backend/coverage/`, `backend/coverage.json`
- **Playwright artifacts**: `frontend/playwright-report/`, `frontend/test-results/`

The root `.gitignore` already ignores most of these (notably `instance/`, `.venv/`, `frontend/playwright-report/`, `frontend/test-results/`), but **coverage outputs are not fully covered**.

### Recommendations
- ✅ **P0:** Ensure no runtime artifacts are tracked in git (if any are tracked, remove them from the index) — **COMPLETED**: Removed tracked coverage files.
- ✅ **P0:** Expand `.gitignore` to ignore coverage outputs consistently — **COMPLETED**:
  - ✅ `backend/coverage/`
  - ✅ `backend/coverage.json`
  - ✅ `backend/.coverage` and `*.coverage`
- **P1:** Consider keeping all generated artifacts under a consistent ignored directory (e.g., `./.artifacts/`) to reduce repo clutter.

## Dead Code / Stale Code Candidates

This section lists code that appears unused or out-of-date, based on reference searches and “feature drift” signals.

### Frontend: Legacy Achievement Definitions Likely Dead

File: `frontend/src/features/students/data/achievements.ts`
- Contains large constant arrays like `STREAK_ACHIEVEMENTS` / `MILESTONE_ACHIEVEMENTS`.
- Repo comments indicate definitions are fetched from the backend, but the file still exports large static definitions.
- **Observed:** `STREAK_ACHIEVEMENTS` and similar constants appear to have **no imports/usage** elsewhere (type imports exist, but not the constants).

**Recommendation (P1):**
- ✅ Remove unused exported arrays (or move them to a historical reference doc if you still want the old definitions preserved).
- ✅ Keep only the TypeScript types if that’s the intended purpose.

### Frontend: Unused Level Requirements Constant

File: `frontend/src/features/students/data/levelRequirements.ts`
- Exports `LEVEL_REQUIREMENTS` but appears unused (only `LevelRequirement` type is referenced elsewhere).
- Contains text like “Complete any 5 test achievements” despite “test achievements removed” elsewhere.

**Recommendation (P1):**
- ✅ Delete `LEVEL_REQUIREMENTS` if backend-driven requirements are the source of truth.
- If it’s meant to be fallback/seed data, rename + document it explicitly and keep it in a non-production path.

### Frontend: “Test Achievements Removed” Drift Still Leaks Through

Files show inconsistent state around “test achievements”:
- ✅ `frontend/src/features/students/hooks/useFilteredAchievements.ts` no longer has special handling for test achievements.
- ✅ `frontend/src/features/students/utils/progressMapping/achievementConverters.ts` no longer maps a `test` category to a special achievement type.
- ✅ `frontend/src/features/students/data/levelRequirements.ts` no longer references “test achievements”.
- Various comments point at backend `achievements_config.py`, but that file is **deprecated** (see backend notes below).

**Recommendation (P0/P1):**
- ✅ Decide whether “test achievements” is truly gone as a product concept.
  - ✅ Yes: removed remaining type/category handling and updated UX copy.

### Backend: Deprecated Compatibility Module

File: `backend/app/config/achievements_config.py`
- Marked **DEPRECATED**, re-exports `app.config.achievements`.
- Emits a `DeprecationWarning` at import time.

**Recommendation (P2):**
- ✅ Confirm nothing imports it (or keep it until you’re sure no external consumers exist).
- ✅ Removed `backend/app/config/achievements_config.py` (no remaining importers).

### Backend: Stub/Deprecated Methods That Can Be Removed

File: `backend/app/services/achievement_service.py`
- `validate_and_cleanup_tier_achievements` is **deprecated** and returns `0`.

**Recommendation (P2):**
- ✅ Remove deprecated stubs once you’re confident nothing calls them (or keep but fence behind explicit “legacy cleanup” module).

### Backend: Likely Dead/Legacy Endpoint

File: `backend/app/routes/practice.py`
- Endpoint `POST /practice/submissions` exists.
- Frontend practice flow uses:
  - `POST /api/practice/sessions/start`
  - `POST /api/practice/questions/check`
  - `POST /api/practice/sessions/:id/complete`
- No obvious frontend usage of `/practice/submissions`.

**Recommendation (P1):**
- ✅ Deleted `POST /practice/submissions` (no runtime callers; references were limited to docs/E2E helpers).

## Complexity Hotspots & Refactor Targets

### Backend: `complete_session` is a “God Function”

File: `backend/app/routes/practice.py`, function `complete_session`

**Problems**
- ✅ **RESOLVED**: Previously combined many responsibilities:
  - compute session stats
  - persist completion
  - compute analytics
  - award achievements (multiple checkers)
  - commit/flush sequencing
  - compute XP and update user
  - shape API response
- ✅ **RESOLVED**: Error handling previously included `traceback.print_exc()` and returned a 500 mid-flow, which risked partial updates.

**Recommendation (P0):**
- ✅ **COMPLETED**: Extracted orchestration service `SessionCompletionService.complete_session(session_id, total_duration_ms) -> DTO`.
- ✅ **COMPLETED**: Wrapped the full workflow in a single transaction boundary using `with transaction():`.
- ✅ **COMPLETED**: Centralized logging using `logger.exception()` instead of `print_exc`, with consistent error payloads.

### Backend: `AchievementQueryService.count_achievements_by_code_with_filters` is Overly Branchy

File: `backend/app/services/achievements/achievement_queries/achievement_query_service.py`

**Problems**
- ✅ **RESOLVED**: Very high branching (**CC~54**) — refactored into smaller helpers.
- Falls back to in-Python filtering for metadata + session-level filters.
- Works around metadata stored as JSON strings (hard to query efficiently, easy to get wrong).

**Recommendation (P0/P1):**
- If you can change the schema: store `achievement_metadata` as a real JSON column (SQLite JSON1 / Postgres JSONB) and query it.
- Otherwise: normalize a small set of frequently queried metadata keys into explicit columns (e.g., `concept_id`, `level`, `operation`), keep the blob for the rest.
- ✅ **COMPLETED**: Split into smaller internal helpers:
  - ✅ "non-tiered exact count" path — `_count_non_tiered_achievements`
  - ✅ "tiered substitution" path — `_count_tiered_achievements`
  - ✅ "metadata filter parse/match" path — `_parse_achievement_metadata`, `_apply_metadata_filter`
  - ✅ "session filter join" path — `_apply_session_filters`

### Backend: `QuestionService.generate_operands_with_constraints` Has Many Special Cases

File: `backend/app/services/question_service.py`

**Problems**
- ✅ **RESOLVED**: Many special-cased branches for division, `fixed_operand2`, `multiple_of`, test constraints, etc. — refactored into pipeline pattern.
- ✅ **RESOLVED**: Hard to reason about correctness and "edge-case coverage" — split into focused strategy methods.

**Recommendation (P1):**
- ✅ **COMPLETED**: Convert to a pipeline:
  - ✅ Build a "constraints object" (normalized) — `_normalize_constraints`
  - ✅ Choose a generator strategy (division/no-remainder, fixed operand, general random) — `_generate_with_test_constraints`, `_generate_with_fixed_operand2`, `_generate_with_general_strategy`
  - ✅ Validate constraints at the end — integrated into `_generate_with_general_strategy`
- Create a targeted unit test matrix for the generator strategies (edge-case oriented).

### Backend: `SessionEngineService.generate_session` Has Mixed Responsibilities

File: `backend/app/services/session_engine_service.py`

**Problems**
- ✅ Handles resume rules, concept picking, question generation retries, session persistence, and response shaping — **REFACTORED**
- ✅ Uses multiple legacy compatibility rules (concept_id formats + "legacy level") — **REFACTORED**

**Recommendation (P1):**
- ✅ Split into:
  - ✅ `SessionResumeService` (resume selection and validation) — **COMPLETED**
  - ✅ `QuestionGenerationService` (pure generation, deterministic inputs) — **COMPLETED**
  - ✅ `SessionFactory` (persist + attach question IDs) — **COMPLETED**
  - ✅ `ConceptSelectionService` (concept selection logic) — **COMPLETED**
- ✅ Make "legacy mappings" a single module with tests — **COMPLETED**: `backend/app/utils/legacy_mappings.py`

## Antipatterns / Code Smells

### Transaction & Consistency Risks
- Routes sometimes perform commits/flushes mid-handler, then continue doing more work.
- Error handling in the middle of long flows can leave partial state.

**Recommendation:**
- Prefer “single orchestration + single commit” patterns for complex flows.
- If partial commits are unavoidable, document invariants and idempotency expectations explicitly.

### Circular Import Pressure
Several routes import models inside functions “to avoid circular imports”.

**Recommendation:**
- Make dependency direction explicit:
  - `routes -> services -> repositories/models`
  - Avoid `services -> routes` (should never happen)
- Consider a `repositories/` layer to remove DB coupling from higher-level services.

### Frontend Hook Complexity / Mixed Concerns

File: `frontend/src/features/practice/hooks/usePracticeSession.ts`
- ✅ Mixes API orchestration, state transitions, navigation, and persistence concerns — **REFACTORED**: Extracted helper functions for state synchronization
- ✅ Uses `// eslint-disable-next-line react-hooks/exhaustive-deps` (can hide legitimate dependency bugs) — **FIXED**: Removed all eslint-disable comments and properly managed dependencies
- ✅ Falls back to client-side answer checking if the server check fails (risk: silently masking backend errors) — **FIXED**: Removed client-side fallbacks, now shows errors and requires retry

**Recommendation (P1):**
- ✅ Extract "session state machine" logic into a pure reducer (or Zustand/Redux slice) and keep the hook thin — **PARTIALLY COMPLETED**: Extracted state synchronization helpers (`usePracticeSessionHelpers.ts`)
- ✅ Consider removing client-side fallback for correctness-critical flows; show an error and allow retry instead — **COMPLETED**: Removed fallbacks from `handleCheckAnswer` and `handleSubmit`, now show errors

## Directory Structure & Architecture Notes

### What’s Good
- Backend already separates `routes/`, `services/`, `config/`, `utils/`.
- Achievements are broken down into checkers/queries/validators, which is a solid “policy object” direction.

### Missed Patterns / Opportunities

**Backend**
- **DTO/schema validation**: request/response payloads are hand-validated. Consider introducing schema validation (e.g., Marshmallow/Pydantic) to reduce route boilerplate and improve correctness.
- **Repository pattern**: heavy query logic (especially around achievements) would benefit from dedicated repository/query objects that hide SQLAlchemy details.
- **Domain orchestration layer**: `complete_session` shows the need for a workflow service that composes multiple domain services safely.

**Frontend**
- **Single source of truth for “definitions”**: achievements + level requirements appear to have legacy static definitions that conflict with backend-driven APIs.
- **Typed API client**: a small client layer (with runtime validation) would reduce drift and clarify contracts.

## Priority Action Plan

### P0 (Do next)
- ✅ Remove/stop tracking generated artifacts; add missing ignores for backend coverage output — **COMPLETED**: Added `.coverage` and `*.coverage` to `.gitignore`, removed tracked coverage files from git.
- ✅ Refactor `complete_session` into a dedicated orchestration service with cleaner transaction/error handling.
- ✅ Resolve "test achievements removed" drift (update frontend behavior + copy, and remove dead filtering paths).

### P1 (High value)
- ✅ Break up `AchievementQueryService.count_achievements_by_code_with_filters` — **COMPLETED**.
- ✅ Simplify/strategy-ize `QuestionService.generate_operands_with_constraints` — **COMPLETED**.
- ✅ Refactor `SessionEngineService.generate_session` — **COMPLETED**: Split into SessionResumeService, QuestionGenerationService, SessionFactory, ConceptSelectionService, and legacy_mappings module.
- ✅ Remove unused frontend constants: `LEVEL_REQUIREMENTS`, `STREAK_ACHIEVEMENTS`, etc. — **COMPLETED**: Verified - these constants have been removed, files now only contain TypeScript types.
- ✅ Audit and deprecate/remove `/practice/submissions` if unused — **COMPLETED**: Endpoint has been removed.

### P2 (Nice-to-have / cleanup)
- Audit usage of deprecated `backend/app/config/achievements_config.py` and remove when safe.
- Remove deprecated stubs (e.g., `validate_and_cleanup_tier_achievements`) after confirming no call sites.

## Suggested Tooling (Optional)

If you want this review to become more automated:
- **Python dead code**: `vulture`
- **Python complexity**: `radon` (cc + maintainability index)
- **TS/JS dead exports**: `ts-prune`
- **Frontend dependency graph**: `madge` (cycles + unused files)
- **Repo hygiene**: pre-commit hooks to prevent committing `coverage/`, Playwright reports, `__pycache__`, DB WALs


