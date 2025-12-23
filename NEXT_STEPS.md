# Next Steps for Code Refactoring

Based on CODE_REVIEW.md analysis, here are the recommended next steps organized by priority and impact.

## High Priority (P1) - Complexity & Maintainability

### 1. Refactor `LevelMasterChecker.check` (CC~22, ~167 LOC)
**File:** `backend/app/services/achievements/achievement_checkers/level_master_checker.py`

**Why:** Large function with nested logic handling both legacy levels and concept-based achievements.

**Recommendation:**
- Extract helper methods:
  - `_get_all_levels()` - Query distinct levels
  - `_get_user_concept_ids()` - Get concept IDs from user sessions
  - `_calculate_consecutive_correct()` - Calculate consecutive correct for a bucket
  - `_find_qualifying_tier()` - Determine highest qualifying tier
  - `_award_for_bucket()` - Already exists but could be extracted as a method

**Impact:** Medium - Reduces complexity, improves testability

---

### 2. Refactor Frontend Hook: `usePracticeSession.ts` (~403 LOC)
**File:** `frontend/src/features/practice/hooks/usePracticeSession.ts`

**Why:** Mixes API orchestration, state transitions, navigation, and persistence. Uses eslint-disable which can hide bugs.

**Recommendation:**
- Extract state machine logic into a pure reducer (or Zustand/Redux slice)
- Keep the hook thin - just compose the reducer with API calls
- Remove client-side fallback for answer checking - show error and allow retry instead
- Fix dependency arrays instead of disabling eslint rules

**Impact:** High - Improves maintainability and reduces bug risk in critical practice flow

---

### 3. Clean Up Frontend Constants (Already Mostly Done)
**Files:** 
- `frontend/src/features/students/data/achievements.ts` ✅ (already cleaned)
- `frontend/src/features/students/data/levelRequirements.ts` ✅ (already cleaned)

**Status:** These files already have comments indicating they only contain types and are backend-driven. The constants (`LEVEL_REQUIREMENTS`, `STREAK_ACHIEVEMENTS`) appear to have already been removed. Verify no remaining references exist.

**Action:** Quick audit to confirm no dead code remains.

---

## Medium Priority (P2) - Architecture Improvements

### 4. Transaction & Consistency Improvements
**Scope:** Multiple routes and services

**Why:** Some routes perform commits/flushes mid-handler, risking partial state on errors.

**Recommendation:**
- Audit routes for mid-handler commits
- Document invariants and idempotency expectations where partial commits are necessary
- Prefer single orchestration + single commit patterns (like `SessionCompletionService`)

**Impact:** Medium - Reduces data consistency risks

---

### 5. Address Circular Import Pressure
**Scope:** Multiple backend files

**Why:** Several routes import models inside functions "to avoid circular imports".

**Recommendation:**
- Make dependency direction explicit: `routes -> services -> repositories/models`
- Consider a `repositories/` layer to remove DB coupling from higher-level services
- Refactor imports to follow proper dependency hierarchy

**Impact:** Medium - Improves code organization and reduces import issues

---

## Lower Priority - Nice to Have

### 6. Consider Repository Pattern
**Scope:** Heavy query logic (especially achievements)

**Why:** Would hide SQLAlchemy details and improve testability.

**Recommendation:**
- Create repository/query objects for complex queries
- Start with achievement-related queries as they're most complex

**Impact:** Low-Medium - Architectural improvement, not urgent

---

### 7. Schema Validation (DTO/schema validation)
**Scope:** Request/response payloads

**Why:** Currently hand-validated, could use Marshmallow/Pydantic.

**Recommendation:**
- Consider introducing schema validation library
- Reduce route boilerplate and improve correctness

**Impact:** Low - Quality of life improvement

---

## Recommended Order of Execution

1. **Start with `LevelMasterChecker.check`** - Medium complexity, clear pattern from previous refactors
2. **Then tackle `usePracticeSession.ts`** - Higher impact, more complex but critical for user experience
3. **Quick audit of frontend constants** - Verify cleanup is complete
4. **Address transaction patterns** - Important for data integrity
5. **Address circular imports** - Improves code organization

## Summary

**Immediate next steps (P1):**
- ✅ Refactor `LevelMasterChecker.check` (follows established patterns)
- ✅ Refactor `usePracticeSession.ts` (high user impact)
- ✅ Quick audit of frontend dead code

**Follow-up (P2):**
- Transaction/consistency improvements
- Circular import resolution

**Future (Nice-to-have):**
- Repository pattern
- Schema validation

