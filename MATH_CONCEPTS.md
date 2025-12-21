# Math Concepts

This document lists all math concepts available for practice. Each concept has independent unlock requirements and can be practiced in any order once unlocked.

## Migration Plan: Removing Level-Based System

This section documents the migration from the old sequential leveling system to the new free-form math concepts system. Follow these steps in order to complete the migration.

### Migration Status Checklist (living)

These are the remaining phases/stages of work, tracked as a checklist. Keep this list up to date as features ship.

#### Decisions (locked in)
- **Stages**: Not used. Learners choose a concept/stage bucket or “random”; no stage progression system is required.
- **Concept source of truth**: Keep in the repo as code/config (not generated from this markdown).
- **MVP scope**: Implement the full concept system we already have defined here (not just a minimal subset).

#### Completed
- [x] **Concept IDs**: migrate `c_level_X` → `c_concept_###` and add parsing helpers where needed (frontend + backend + tests)
- [x] **Remove test mode**: delete Tests UI + API + services/config; remove `is_test`/`test_type` usage throughout
- [x] **Remove adaptive distribution**: default practice is concept-based selection; no distribution service
- [x] **XP system end-to-end**:
  - [x] add `User.experience` and XP→level curve
  - [x] calculate per-session XP from concept XP + achievement rewards
  - [x] return `level_up` payload with `xp_breakdown` and `xp_progress`
- [x] **Frontend XP UI**:
  - [x] Journey header shows total XP + XP-to-next + progress bar
  - [x] Practice summary shows detailed XP breakdown
  - [x] Concepts: show “XP: X per correct answer” (card + detail modal)
  - [x] Achievements: show XP rewards (bonus + multiplier)
  - [x] Level-up celebration/animation on summary when `leveled_up` is true

#### Remaining (next phases)
- [x] **Replace placeholder concept catalog with real catalog (doc-driven → code/config)**
  - [x] stop generating concepts via placeholder `getAllMathConcepts()` level mapping
  - [x] create a real concept list in code/config including: id, name, category, operation, layout, answer formats, unlock requirements
  - [x] ensure the Math Concepts tab uses this catalog (sorting/filtering/search)
- [x] **Backend concept configuration as source of truth for question generation**
  - [x] add concept configs (operation, operand ranges, constraints, layout, answer formats, special rules) keyed by `concept_id`
  - [x] update session engine to generate questions from concept config directly (not via legacy level config)
  - [x] ensure constraints from this doc are enforced (no-remainder, multiples, fixed divisor, etc.)
- [x] **Unlock requirements fully concept-aware**
  - [x] ensure unlock requirements support `quantity` + `metadata_filter` (especially `concept_id`)
  - [x] verify/expand backend endpoints so frontend can show `progress` + `completed` reliably
  - [x] ensure requirement descriptions render correctly in UI (no legacy “test_type” phrasing)
- [x] **Descriptive concept IDs end-to-end**
  - [x] support non-legacy ids (e.g. `c_add_1s`) through: catalog → practice start → session engine → XP lookup → attempt history
  - [x] remove remaining assumptions that `concept_id` implies a legacy `level`
- [x] **Doc-format parity / UI polish**
  - [x] Summary: show Concept Name and Achievement Name + Tier in the XP breakdown (not just raw codes/ids)
  - [x] ensure tier naming/casing is consistent across the app
- [x] **Legacy cleanup**
  - [x] remove remaining `legacyLevel` plumbing once concept configs and descriptive IDs are fully supported
  - [x] migration strategy for existing persisted data (if not using full DB resets)

  **Migration strategy (no full DB reset):**
  - **Keep existing rows**: Do not backfill or rewrite historical `PracticeSession.level` or `Question.required_level`.
  - **Use runtime compatibility matching**:
    - Unlock/requirement counting uses `metadata_filter.concept_id` and will match both new `{concept_id: ...}` and legacy `{level: N}` metadata where applicable.
    - For descriptive concepts, requirement metadata should use `{concept_id: "<descriptive_id>"}` going forward.
  - **Concept catalog changes**:
    - New concepts can be added without migrating old concept ids; old `c_concept_###` remain valid forever.
    - If a concept is renamed, keep the old `concept_id` as an alias in config (don’t rename persisted IDs).
  - **Optional one-time data cleanup (safe)**:
    - For any achievements currently stored with `{"level": N}` metadata, optionally *add* a parallel achievement entry with `{"concept_id": "c_concept_###"}` when re-earned (no destructive migration).
  - **Future improvement (optional)**:
    - Add a background job/management command to backfill `achievement_metadata.concept_id` for legacy rows where `level` is present and unambiguous.

---

## Bugs / RCA / Next Steps (log)

This section captures bugs discovered during live testing so we don’t lose context. Each entry includes:
- a **verbatim quote** from the original report
- **current behavior**
- **expected behavior**
- **RCA / investigation notes**
- a **TODO checklist** for follow-up work

---

### Bug 1 — "First Victory" awarded before session completion (and verify session-summary attribution)

**User report (verbatim):**
> I was awarded First Victory and First Stepts when I exited out of the session. This should only be awared after the session is completed. Do we have tests to verify this?

**Current behavior (observed):**
- `first-victory` was awarded before the first session was completed (observed when exiting the session).
- `first-steps` may award during a session (this is acceptable), but we need to ensure it is attributed to the session where it was earned for accurate XP display.

**Expected behavior:**
- `first-victory` should only award when the session is **completed** (e.g. on `/api/practice/sessions/<id>/complete`).
- `first-steps` can award as soon as it happens, but it must:
  - appear in the **session summary** for the session it was earned in, and
  - contribute the correct XP reward in that session's XP breakdown.

**RCA / investigation notes:**
- The `first-victory` achievement was using `question_count >= 1` requirement, which meant it could award as soon as a user answered one question, even if the session wasn't completed.
- The `/practice/submissions` endpoint was calling `ensure_achievements` without passing `session_id`, which could cause attribution issues.

**Resolution:**
- ✅ Modified `BasicMilestoneChecker` to check for completed sessions when awarding `first-victory` (checks `PracticeSession.completed_at IS NOT NULL`).
- ✅ Updated `/practice/submissions` endpoint to pass `session_id` when calling `ensure_achievements` for proper session attribution.
- ✅ Added backend tests to verify `first-victory` only awards when sessions are completed.

**Files changed:**
- `backend/app/services/achievements/achievement_checkers/basic_milestone_checker.py` - Added special handling for `first-victory` to check completed sessions
- `backend/app/routes/practice.py` - Updated `/practice/submissions` to pass `session_id` to `ensure_achievements`
- `backend/tests/test_achievements_awarding.py` - Added tests for incomplete session behavior

---

### Bug 2 — Concept selection: only c_add_1s unlocked but session starts a different concept

**User report (verbatim):**
> The only math concept I have unlocked is addition (1s). But it started some other addition.

**Current behavior (observed):**
- Starting practice can yield a concept that is not currently unlocked.

**Expected behavior:**
- visit "/" and page should load
- I should be able to select a user
- Then start practice
- Enter Pin & continue
- Start a session with an unlocked math concept

**RCA / investigation notes:**
- The session engine was choosing a random concept for "general practice" based on a random legacy level (not unlock state).
- When `concept_id` was None, it would randomly select a level and convert it to a concept_id without checking unlock status.

**Resolution:**
- ✅ Created `ConceptUnlockService` to check if concepts are unlocked for users
- ✅ Updated `SessionEngineService.generate_session()` to only select from unlocked concepts when `concept_id` is None
- ✅ Added test to verify only unlocked concepts are selected
- ✅ Updated existing test to handle descriptive concept IDs (c_add_1s, etc.)

**Files changed:**
- `backend/app/services/concept_unlock_service.py` - New service for checking concept unlock status
- `backend/app/services/session_engine_service.py` - Updated to filter by unlocked concepts
- `backend/tests/test_session_engine_service.py` - Added test for unlocked concept selection

---

### Bug 3 — XP breakdown count mismatch (shows 15 instead of 10)

**User report (verbatim):**
> Looking at XP earned `37 × 15 (Single Digit Addition (1s))` But there was only 10 of 10 correct. Shouldn't this be `37 x 10 (Single Digit Addition (1s))` ?

**Current behavior (observed):**
- XP breakdown displays `xp_per_correct × correct_count`, but `correct_count` is not matching the session’s “10 of 10 correct”.

**Expected behavior:**
- `correct_count` in XP breakdown should match the completed session’s correct count.

**RCA / investigation notes (hypotheses):**
- We may be using the user's "daily stats" correct count, or aggregating across more than the session (e.g. resumed session + new session combined).
- The backend XP breakdown may be populated from a different count than the session completion payload.
- The frontend may be displaying a field not scoped to the session (e.g. `breakdown.correct_count` vs `session.correct_count`).

**Root cause:**
- The `/complete` endpoint was counting all Response records for the session, not unique questions.
- When a user answered the same question multiple times (e.g., by checking their answer multiple times via `/api/practice/questions/check`), multiple Response records were created.
- The code counted all correct responses, not unique questions answered correctly, inflating the correct_count (e.g., 15 responses for 10 unique questions would show 15 instead of 10).

**Resolution:**
- ✅ Fixed XP breakdown to count unique questions instead of all responses
- ✅ When multiple responses exist for the same question, use the latest response per question
- ✅ Added tests to verify correct_count matches session responses (unique questions)
- ✅ Added test for cross-session isolation (Session B not inflated by Session A)
- ✅ Added test to verify latest response per question is used when multiple responses exist

**Files changed:**
- `backend/app/routes/practice.py` - Updated `complete_session` endpoint to group responses by question_id and use latest response per question
- `backend/tests/test_complete_session_xp_breakdown.py` - New test file with comprehensive tests for XP breakdown correct_count

**TODOs / next steps:**
- [x] Compare backend `/complete` response fields:
  - `session.correct_count`
  - `level_up.xp_breakdown.correct_count`
  - `level_up.earned_xp` inputs
- [x] Add a backend test: completing a 10-question session with 10 correct returns `xp_breakdown.correct_count == 10`.
- [x] Add a backend test to cover cross-session aggregation bugs:
  - create Session A in concept X, answer some questions, **do not complete**
  - create Session B in concept Y, complete with exactly 10/10 correct
  - assert Session B returns `xp_breakdown.correct_count == 10` (not inflated by Session A or daily stats)
- [x] Ensure XP breakdown calculation uses **session-local** correct count, not global/aggregate stats.

---

### Bug 4 — XP multipliers: representation and math mismatch (additive “bonus multipliers”)

**User report (verbatim):**
> This is not how I wanted these added or it needs to be represented differently. `1.03 + 1.32` in my mind was 1.35 when added together. I suppose this is the behavior I envisoned, but captured in the requirements incorrectly.
>
> Should have been: `0.03 + 0.32 = 0.35` as a subtotal. So
>
> ```
> 2 achievement(s)            x1.35
>
> Multipliers
> Accuracy Ace (Gold)        x0.03
> Speed Demon (Master)    x0.32
> ```
> NOTE: We need to figure out what we need to change to get to this behavior.

**Current behavior (observed):**
- We display multipliers as `x1.03`, `x1.32` and sum them to get a `total_multiplier` (e.g. `1.03 + 1.32 = 2.35`).

**Expected behavior:**
- Treat each achievement multiplier as a **bonus delta** over 1.0:
  - store/display as `0.03`, `0.32`
  - compute `total_multiplier = 1.0 + sum(deltas)`
  - display overall as `x1.35`

**RCA / investigation notes:**
- This is primarily a **spec mismatch** between how multipliers were encoded vs how they were intended to be applied/presented.

**Resolution:**
- ✅ Multipliers are stored as factors (1.03, 1.32) in config but treated as bonus deltas in calculation
- ✅ Backend converts factors to deltas: `delta = factor - 1.0`
- ✅ Backend calculates total multiplier as: `total_multiplier = 1.0 + sum(deltas)` instead of `sum(factors)`
- ✅ Backend returns deltas (0.03, 0.32) in API response instead of factors (1.03, 1.32)
- ✅ Frontend displays deltas correctly (x0.03, x0.32) and total as x1.35
- ✅ Added backend test to verify multiplier delta calculation

**Files changed:**
- `backend/app/routes/practice.py` - Updated multiplier calculation to use deltas
- `backend/tests/test_complete_session_xp_breakdown.py` - Added test for multiplier delta calculation

**TODOs / next steps:**
- [x] Decide canonical model:
  - store multipliers as **factor** (1.03) in config, but treat as **delta** (0.03) in calculation/display
  - adjust both calculation + presentation
- [x] Update backend XP calculation to:
  - convert factors to deltas: `delta = factor - 1.0`
  - sum deltas → `1 + sum(delta)`
  - apply that multiplier to base XP
- [x] Update backend API to return deltas instead of factors
- [x] Frontend already displays multiplier values correctly (shows deltas as x0.03, total as x1.35)
- [x] Add backend tests for multiplier math.
- [x] Update doc section(s) that define multiplier semantics to remove ambiguity.

---

### Bug 6 — Summary CTA “Try Next Level” should route to Journey unlocked concepts

**User report (verbatim):**
> Summary page shows `Try Next Level`. Let's change it's behavior. It should say "Try something else". Once clicked it will take them to the journey page with the math concepts tab selected and searched for unlocked concepts.

**Current behavior (observed):**
- Summary CTA says “Try Next Level” and routes to a next-level flow.

**Expected behavior:**
- CTA label: **“Try something else”**
- On click: navigate to **Journey** page, **Math Concepts tab selected**, filter/search set to show unlocked concepts.

**Resolution:**
- ✅ Updated Summary CTA label from "Try Next Level" to "Try something else"
- ✅ Updated CTA navigation to route to Journey page with Math Concepts tab selected
- ✅ Implemented query param support for status filter in MathConceptsTab
- ✅ Navigation uses `/journey/:userId/concepts?status=unlocked` to show unlocked concepts

**Files changed:**
- `frontend/src/features/practice/components/summary/SummaryActionButtons.tsx` - Updated button label
- `frontend/src/features/practice/SummaryPage.tsx` - Updated navigation route
- `frontend/src/features/students/components/journey/MathConceptsTab.tsx` - Added query param support for status filter

**TODOs / next steps:**
- [x] Update Summary CTA label and destination route.
- [x] Implement a Journey route param (or query param) to select tab + preset filters:
  - `tab=concepts` (via route param)
  - `status=unlocked` (via query param)
- [ ] Add a frontend test for the Summary CTA routing behavior.

## 1. Concept ID Migration

### Overview
Update all concept IDs to remove references to "level" and use a consistent naming scheme. The new format should be `c_concept_XXX` for concepts that were previously levels, and descriptive IDs like `c_add_1s`, `c_sub_2s` for new granular concepts.

### Current State
- Old format: `c_level_1`, `c_level_2`, etc.
- New format: `c_concept_001`, `c_concept_002`, etc. (for concepts that map to old levels)
- Descriptive IDs: `c_add_1s`, `c_sub_2s`, etc. (for new granular concepts)

### Files to Update

#### Frontend
1. **`frontend/src/features/students/data/mathConcepts.ts`**
   - Update `createConceptFromLevel()` function to generate new concept IDs
   - Change `conceptId: \`c_level_${level}\`` to `conceptId: \`c_concept_${String(level).padStart(3, '0')}\``
   - Update `CONCEPT_DISPLAY_NAMES` mapping if needed

2. **`frontend/src/features/practice/hooks/usePracticeAPI.ts`**
   - Update regex pattern for extracting level from conceptId
   - Change `conceptId.match(/c_level_(\d+)/)` to `conceptId.match(/c_concept_(\d+)/)`
   - Or better: create a mapping function that doesn't rely on parsing concept IDs

3. **`frontend/src/features/students/hooks/useConceptAttempts.ts`**
   - Update regex pattern: `conceptId.match(/c_level_(\d+)/)` to `c_concept_(\d+)`
   - Update conceptId generation: `c_level_${session.level}` to use new format

#### Backend
1. **`backend/app/models.py`**
   - Update comment: `# e.g., "c_level_1", "c_add_1s"` to `# e.g., "c_concept_001", "c_add_1s"`

2. **`backend/app/services/practice_service.py`**
   - Update docstring: `# e.g., "c_level_1", "c_add_1s"` to new format

3. **`backend/app/services/session_engine_service.py`**
   - Update docstring: `# e.g., "c_level_1", "c_add_1s"` to new format

4. **`backend/tests/test_practice_service.py`**
   - Update test concept IDs from `"c_level_1"` to `"c_concept_001"`, etc.

5. **`backend/tests/test_session_engine_service.py`**
   - Update test concept IDs from `"c_level_1"` to `"c_concept_001"`, etc.

### Search Commands
```bash
# Find all references to old concept ID format
grep -r "c_level_" --include="*.ts" --include="*.tsx" --include="*.py" frontend/ backend/

# Find concept ID generation
grep -r "c_level_\${" --include="*.ts" --include="*.tsx" frontend/
grep -r 'c_level_' --include="*.py" backend/
```

---

## 2. Removing Legacy Level References

### Overview
Remove all references to `legacyLevel` field from the codebase. This field was a temporary bridge to the old leveling system and is no longer needed.

### Migration Order

#### Step 1: Remove from Type Definitions
1. **`frontend/src/features/students/data/mathConcepts.ts`**
   - Remove `legacyLevel: number` from `MathConcept` type definition
   - Remove `legacyLevel: level` from `createConceptFromLevel()` function
   - Update comment: Remove "The level number this concept maps to (1:1 for now)"

#### Step 2: Update Code That Uses legacyLevel
1. **`frontend/src/features/students/hooks/useMathConcepts.ts`**
   - Replace `concept.legacyLevel` with a new approach
   - **Option A**: Create a mapping from conceptId to level number for unlock requirements lookup
   - **Option B**: Store unlock requirements directly in concept data structure
   - Update: `const targetLevel = concept.legacyLevel` to use conceptId-based lookup

2. **`frontend/src/features/students/components/journey/MathConceptDetailModal.tsx`**
   - Remove the "Level:" display that shows `{concept.legacyLevel}`
   - Either remove the field entirely or replace with concept ID display if needed

#### Step 3: Remove from Documentation
1. **`MATH_CONCEPTS.md`**
   - Remove all `- **Legacy Level**: X` entries from concept metadata sections

### Search Commands
```bash
# Find all references to legacyLevel
grep -r "legacyLevel" --include="*.ts" --include="*.tsx" --include="*.md" frontend/ MATH_CONCEPTS.md

# Find legacy level in type definitions
grep -r "legacy.*level\|Legacy.*Level" --include="*.ts" --include="*.tsx" -i frontend/

# Find usage in components
grep -r "concept\.legacyLevel\|\.legacyLevel" --include="*.ts" --include="*.tsx" frontend/
```

### Files to Update (in order)
1. `frontend/src/features/students/data/mathConcepts.ts` - Remove from type and function
2. `frontend/src/features/students/hooks/useMathConcepts.ts` - Replace usage with conceptId-based lookup
3. `frontend/src/features/students/components/journey/MathConceptDetailModal.tsx` - Remove UI display
4. `MATH_CONCEPTS.md` - Remove from all concept entries

---

## 3. Removing Old Level Selection Logic

### Overview
Remove the old adaptive distribution system that selected levels based on categories (level, requirements, bottom_performers, random). This system was designed for sequential leveling and is incompatible with the free-form concept system.

### Components to Remove/Update

#### Backend: Adaptive Distribution Service

**File: `backend/app/services/adaptive_distribution_service.py`**

**Methods to Remove or Refactor:**
1. `get_requirements_category_levels(user: User) -> list[int]`
   - **Purpose**: Extracted levels from level progression (note: test unlock requirements are being removed - see section 7)
   - **Why Remove**: Uses level-based thinking and `level-master` achievements with level metadata
   - **Search**: `grep -r "get_requirements_category_levels" backend/`

2. `generate_requirements_category_distribution(user: User) -> list[dict]`
   - **Purpose**: Generated question distribution for "requirements" category
   - **Why Remove**: Based on level progression requirements
   - **Search**: `grep -r "generate_requirements_category_distribution" backend/`

3. `generate_level_category_distribution(user_level: int, mode: str) -> list[dict]`
   - **Purpose**: Generated distribution for "level" category (Type A/B)
   - **Why Remove**: Level-based selection incompatible with concepts
   - **Search**: `grep -r "generate_level_category_distribution" backend/`

4. `generate_bottom_performers_category_distribution(user: User) -> list[dict]`
   - **Purpose**: Selected levels based on worst performance
   - **Why Remove**: Level-based, should be concept-based if kept
   - **Search**: `grep -r "generate_bottom_performers" backend/`

5. `select_category() -> str`
   - **Purpose**: Selected category (level/requirements/bottom_performers/random)
   - **Why Remove**: Category system is level-based
   - **Search**: `grep -r "select_category" backend/`

6. `generate_adaptive_question_distribution(user: User, session_level: int) -> dict`
   - **Purpose**: Main entry point that selected category and generated distribution
   - **Why Update**: Should select concepts instead of levels
   - **Search**: `grep -r "generate_adaptive_question_distribution" backend/`

**How to Identify Level-Based Logic:**
- Look for methods that take `user_level: int` or `session_level: int` as parameters
- Look for methods that return `list[int]` (level numbers) or `list[dict]` with `"level"` keys
- Look for references to `LEVEL_PROGRESSION_CONFIG` or `LEVELS_CONFIG`
- Look for category names: "level", "requirements", "bottom_performers", "random"

**Replacement Strategy:**
- Instead of selecting levels, select math concepts
- Use concept unlock status to determine available concepts
- Use concept performance data (if available) for adaptive selection
- Consider keeping "random" category but make it concept-based

#### Backend: Session Engine Service

**File: `backend/app/services/session_engine_service.py`**

**Code to Update:**
1. **Practice session generation** (around line 245-330)
   - Currently calls: `AdaptiveDistributionService.generate_adaptive_question_distribution(user, session_level)`
   - **Action**: Replace with concept-based question generation
   - **Search**: `grep -r "generate_adaptive_question_distribution" backend/`

2. **Level extraction from concept_id**
   - Currently extracts level from conceptId for backward compatibility
   - **Action**: Use concept_id directly, don't convert to level
   - **Search**: `grep -r "c_level_\|c_concept_" backend/app/services/session_engine_service.py`

#### Backend: Test Definitions

**File: `backend/app/config/tests/test_definitions.py`**

**Status**: ⚠️ **To be removed** - See section 7 "Removing Tests from the Codebase"
- This entire file will be deleted as tests are being removed from the system
- No updates needed - file will be removed

#### Frontend: Practice Start Strategies

**File: `frontend/src/features/practice/utils/practiceStartStrategies.ts`**

**Status**: ✅ Already concept-based - no changes needed
- Uses `getUnlockedConcepts()` which is concept-aware
- Selects from `MathConcept[]` not levels
- This is the correct pattern to keep

### Search Commands
```bash
# Find all adaptive distribution methods
grep -r "AdaptiveDistributionService\." --include="*.py" backend/

# Find category selection
grep -r "select_category\|requirements.*category\|level.*category" --include="*.py" -i backend/

# Find level-based distribution generation
grep -r "generate.*distribution\|generate.*category" --include="*.py" -i backend/app/services/adaptive_distribution_service.py

# Find level progression config usage
grep -r "LEVEL_PROGRESSION_CONFIG\|level_progression" --include="*.py" backend/

# Find level-master achievements
grep -r "level-master" --include="*.py" --include="*.ts" --include="*.tsx" backend/ frontend/

# Find level-based requirements (note: test definitions will be removed - see section 7)
grep -r "metadata_filter.*level\|level_requirement" --include="*.py" backend/
```

### Files to Update (in order)
1. `backend/app/services/session_engine_service.py` - Replace adaptive distribution call
2. `backend/app/services/adaptive_distribution_service.py` - Remove/refactor level-based methods
3. `backend/app/config/tests/test_definitions.py` - Update test unlock requirements
4. `backend/tests/test_question_distribution.py` - Update or remove level-based tests
5. `backend/tests/test_distribution_stats.py` - Update or remove category tests

---

## 4. Adding New Math Concepts and Unlock Requirements

### Overview
Ensure all new math concepts are properly added to the system and their unlock requirements match the design documented in this file.

### Checklist for Adding a New Concept

#### 1. Documentation (`MATH_CONCEPTS.md`)
- Add concept entry with all required sections:
  - Name
  - Category
  - Unlock Requirements (achievements with quantities and metadata filters)
  - Math Type & Range (operation, operand ranges, answer range)
  - Constraints
  - Metadata (Layout Type, Answer Format, Concept ID)
  - Example Problems

#### 2. Frontend Data (`frontend/src/features/students/data/mathConcepts.ts`)
- Add concept to `getAllMathConcepts()` function
- If using display name mapping, add to `CONCEPT_DISPLAY_NAMES`
- Ensure `createConceptFromLevel()` or equivalent creates concept with correct:
  - `conceptId` (matches Concept ID in doc)
  - `displayName` (matches Name in doc)
  - `operation` (matches Category/Operation in doc)

#### 3. Backend Configuration (`backend/app/config/levels_config.py`)
- Add level config entry (if concept maps to a level number)
- Ensure operation, ranges, constraints match documentation
- Verify layout_type and answer_format match metadata

#### 4. Unlock Requirements (`backend/app/config/level_progression_config.py`)
- Add unlock requirements entry
- Map achievement codes to concept unlock requirements
- Ensure quantities and metadata filters match documentation
- Verify order of requirements matches documentation

#### 5. Frontend Unlock Logic (`frontend/src/features/students/utils/conceptUnlock.ts`)
- Verify `evaluateConceptUnlock()` handles all achievement types used
- Ensure metadata filters are properly evaluated
- Verify unlock status calculation

#### 6. Testing
- Add test for concept creation
- Add test for unlock requirement evaluation
- Add test for concept practice session generation
- Verify concept appears in Math Concepts tab when unlocked

### Unlock Requirements Format

Unlock requirements in `MATH_CONCEPTS.md` should match the format used in `level_progression_config.py`:

```python
{
    "achievement_code": "achievement-name-tier",
    "quantity": 1,  # Number of achievements needed
    "order": 1,  # Order in which requirement must be met
    "metadata_filter": {  # Optional: filter by metadata
        "concept_id": "c_concept_001",
        "level": 5,  # NOTE: Update to concept_id or remove
        "stage": 5,  # New: concept-based stage identifier
    }
}
```

### Achievement Code Updates

**Old (Level-based):**
- `level-master-bronze` with `metadata_filter: {"level": X}`

**New (Concept-based):**
- `stage-master-bronze` with `metadata_filter: {"stage": X}` OR
- `concept-master-bronze` with `metadata_filter: {"concept_id": "c_concept_XXX"}` OR
- Remove level-specific achievements and use general achievements

### Verification Commands
```bash
# Verify all concepts in doc have corresponding code entries
grep -r "c_concept_\|c_add_\|c_sub_" frontend/src/features/students/data/mathConcepts.ts

# Check unlock requirements format consistency
grep -A 5 "Unlock Requirements" MATH_CONCEPTS.md | grep -E "achievement|quantity|metadata"

# Verify achievement codes exist
grep -r "level-master\|stage-master\|concept-master" backend/app/config/ --include="*.py"
```

---

## 6. Levels Going Forward: Experience-Based Progression

### Overview
Levels will remain as a motivational system but will be decoupled from concept unlocking. Levels 1-99 will use an experience-based progression system matching Diablo 2's leveling curve. Players earn XP from:
- Answering questions correctly (varies by concept)
- Earning achievements

### Level Requirements (Diablo 2 XP Table)

Levels 1-99 require the following total experience to reach:

| Level | Total XP Required | XP to Next Level |
|-------|------------------|------------------|
| 1 | 0 | 500 |
| 2 | 500 | 1,000 |
| 3 | 1,500 | 2,250 |
| 4 | 3,750 | 4,125 |
| 5 | 7,875 | 6,300 |
| 6 | 14,175 | 8,505 |
| 7 | 22,680 | 10,206 |
| 8 | 32,886 | 11,510 |
| 9 | 44,396 | 13,319 |
| 10 | 57,715 | 14,429 |
| 11 | 72,144 | 18,036 |
| 12 | 90,180 | 22,545 |
| 13 | 112,725 | 28,181 |
| 14 | 140,906 | 35,226 |
| 15 | 176,132 | 44,033 |
| 16 | 220,165 | 55,042 |
| 17 | 275,207 | 68,801 |
| 18 | 344,008 | 86,002 |
| 19 | 430,010 | 107,503 |
| 20 | 537,513 | 134,378 |
| 21 | 671,891 | 167,973 |
| 22 | 839,864 | 209,966 |
| 23 | 1,049,830 | 262,457 |
| 24 | 1,312,287 | 328,072 |
| 25 | 1,640,359 | 410,090 |
| 26 | 2,050,449 | 512,612 |
| 27 | 2,563,061 | 640,765 |
| 28 | 3,203,826 | 698,434 |
| 29 | 3,902,260 | 761,293 |
| 30 | 4,663,553 | 829,810 |
| 31 | 5,493,363 | 904,492 |
| 32 | 6,397,855 | 985,900 |
| 33 | 7,383,755 | 1,074,624 |
| 34 | 8,458,379 | 1,171,344 |
| 35 | 9,629,723 | 1,276,765 |
| 36 | 10,906,488 | 1,391,674 |
| 37 | 12,298,162 | 1,516,924 |
| 38 | 13,815,086 | 1,653,448 |
| 39 | 15,468,534 | 1,802,257 |
| 40 | 17,270,791 | 1,964,461 |
| 41 | 19,235,252 | 2,141,263 |
| 42 | 21,376,515 | 2,333,976 |
| 43 | 23,710,491 | 2,544,034 |
| 44 | 26,254,525 | 2,772,997 |
| 45 | 29,027,522 | 3,022,566 |
| 46 | 32,050,088 | 3,294,598 |
| 47 | 35,344,686 | 3,591,112 |
| 48 | 38,935,798 | 3,914,311 |
| 49 | 42,850,109 | 4,266,600 |
| 50 | 47,116,709 | 4,650,593 |
| 51 | 51,767,302 | 5,069,147 |
| 52 | 56,836,449 | 5,525,370 |
| 53 | 62,361,819 | 6,022,654 |
| 54 | 68,384,473 | 6,564,692 |
| 55 | 74,949,165 | 7,155,515 |
| 56 | 82,104,680 | 7,799,511 |
| 57 | 89,904,191 | 8,501,467 |
| 58 | 98,405,658 | 9,266,598 |
| 59 | 107,672,256 | 10,100,593 |
| 60 | 117,772,849 | 11,009,646 |
| 61 | 128,782,495 | 12,000,515 |
| 62 | 140,783,010 | 13,080,560 |
| 63 | 153,863,570 | 14,257,811 |
| 64 | 168,121,381 | 15,541,015 |
| 65 | 183,662,396 | 16,939,705 |
| 66 | 200,602,101 | 18,464,279 |
| 67 | 219,066,380 | 20,126,064 |
| 68 | 239,192,444 | 21,937,409 |
| 69 | 261,129,853 | 23,911,777 |
| 70 | 285,041,630 | 26,063,836 |
| 71 | 311,105,466 | 28,409,582 |
| 72 | 339,515,048 | 30,966,444 |
| 73 | 370,481,492 | 33,753,424 |
| 74 | 404,234,916 | 36,791,232 |
| 75 | 441,026,148 | 40,102,443 |
| 76 | 481,128,591 | 43,711,663 |
| 77 | 524,840,254 | 47,645,713 |
| 78 | 572,485,967 | 51,933,826 |
| 79 | 624,419,793 | 56,607,872 |
| 80 | 681,027,665 | 61,702,579 |
| 81 | 742,730,244 | 67,255,812 |
| 82 | 809,986,056 | 73,308,835 |
| 83 | 883,294,891 | 79,906,630 |
| 84 | 963,201,521 | 87,098,226 |
| 85 | 1,050,299,747 | 94,937,067 |
| 86 | 1,145,236,814 | 103,481,403 |
| 87 | 1,248,718,217 | 112,794,729 |
| 88 | 1,361,512,946 | 122,946,255 |
| 89 | 1,484,459,201 | 134,011,418 |
| 90 | 1,618,470,619 | 146,072,446 |
| 91 | 1,764,543,065 | 159,218,965 |
| 92 | 1,923,762,030 | 173,548,673 |
| 93 | 2,097,310,703 | 189,168,053 |
| 94 | 2,286,478,756 | 206,193,177 |
| 95 | 2,492,671,933 | 224,750,564 |
| 96 | 2,717,422,497 | 244,978,115 |
| 97 | 2,962,400,612 | 267,026,144 |
| 98 | 3,229,426,756 | 291,058,498 |
| 99 | 3,520,485,254 | - |

*Source: https://diablo.fandom.com/wiki/Character_Level*

### Implementation Requirements

#### Backend Changes
1. **Add XP tracking to User model**
   - Add `experience` field (integer, default 0)
   - Add method to calculate level from experience
   - Add method to award XP and check for level ups

2. **XP Award System**
   - XP is awarded **after the session is completed** (not during)
   - Each correct question is worth the XP value from its math concept
   - XP calculation order:
     1. Calculate total XP for all correct questions in the session
     2. Add up all bonus XP multipliers from earned achievements to get a final multiplier
     3. Multiply the XP earned by the multiplier
     4. Total all bonus XP from all achievements
     5. Add bonus XP to session XP (Correct answers × multipliers)
   - Store XP amounts in concept/achievement configs

3. **Level Calculation**
   - Create lookup table or formula based on Diablo 2 XP requirements
   - Update user level when XP threshold is reached
   - Trigger level-up notifications/animations

#### Frontend Changes
1. **Journey Page - XP Display**
   - Display current total XP amount
   - Show XP required to reach next level
   - Display XP progress bar (current XP / XP needed for next level)
   - Update in real-time as user earns XP

2. **Summary Page - XP Earned**
   - Display detailed XP breakdown in the following format:
     ```
     XP                  [Concept Name] x [Count]    [Total XP]xp
     
     Multipliers    [Achievement Name] [Tier]              x[Multiplier]
                     [Achievement Name] [Tier]              x[Multiplier]
                     ...                                                      [Total]xp
     
     Bonus XP    [Achievement Name] [Tier]                    [XP]xp
                     [Achievement Name] [Tier]                    [XP]xp
                     ...
     
     Total                                                                        [Total]xp
     ```
   - Example display:
     ```
     XP                  Single Digit Addition (1s) x 10    370xp
     
     Multipliers    First Steps                                   x1.01
                     First Victory                                x1.02
                     Accuracy Ace [Gold]                   x1.03
                     Speed Demon [Diamond]          x1.16
                                                                        451xp
     
     Bonus XP    First Steps                                      50xp
                   First Victory                                  100xp
                   Speed Demon Diamond                50xp
                   So Wow! [Bronze]                          10xp
                   So Wow! [Silver]                            25xp
                   So Wow! [Gold]                             50xp
                   So Wow! [Diamond]                    100xp
     
     Total                                                                836xp
     ```
   - Display level-up notification if user leveled up during session
   - Show new level and remaining XP if level-up occurred

3. **Math Concepts Tab - XP Display**
   - Show XP value for each concept in the concept card
   - Display XP in concept detail modal
   - Format: "XP: X per correct answer"

4. **Achievements Tab - XP Display**
   - Show XP value for each achievement tier
   - Display XP in achievement detail view
   - Format: "XP: X" for each tier

6. **Level-Up Animations**
   - Show level-up animation when threshold is reached
   - Display new level prominently
   - Show XP progress bar reset for new level

2. **XP Display in Concepts**
   - Show XP value in concept detail modal
   - Display XP gained after answering questions

### XP Sources and Calculation

XP is awarded **after the session is completed** from two sources:

1. **Correct Answers**: Each math concept grants different XP per correct answer
   - XP value is stored in the concept's metadata
   - Awarded based on the number of correct answers in the session

2. **Achievement Unlocks**: Achievements provide two types of XP bonuses:
   - **XP Multipliers**: Applied to the base XP from correct answers
   - **Bonus XP**: Flat XP amounts added after multipliers are applied

#### XP Calculation Order

When a session is completed, XP is calculated in this order:

1. **Calculate base XP**: Sum of XP from all correct questions (concept XP × number correct)
2. **Calculate multiplier total**: 
   - Convert each achievement's multiplier factor to a delta: `delta = factor - 1.0`
   - Sum all deltas: `sum_deltas = sum(all deltas)`
   - Calculate total multiplier: `total_multiplier = 1.0 + sum_deltas`
   - Example: factors 1.03 and 1.32 → deltas 0.03 and 0.32 → total = 1.0 + 0.03 + 0.32 = 1.35
3. **Apply multipliers**: Multiply base XP by the total multiplier
4. **Calculate bonus XP**: Sum all bonus XP from achievements earned during the session
5. **Final total**: Add bonus XP to the multiplied XP

**Formula**: `Total XP = (Base XP × Total Multiplier) + Bonus XP`

**Note**: Multipliers are stored as factors (e.g., 1.03, 1.32) but are treated as bonus deltas in calculation. The total multiplier is always `1.0 + sum(deltas)`, not `sum(factors)`.

#### Example Calculation

- Session: 10 correct answers on "Single Digit Addition (1s)" (37 XP each)
- Base XP: 10 × 37 = 370 XP
- Achievements earned:
  - First Steps: multiplier factor 1.01 (delta 0.01), bonus 50 XP
  - First Victory: multiplier factor 1.02 (delta 0.02), bonus 100 XP
  - Accuracy Ace [Gold]: multiplier factor 1.03 (delta 0.03), bonus 0 XP
  - Speed Demon [Diamond]: multiplier factor 1.16 (delta 0.16), bonus 50 XP
  - So Wow! [Bronze]: multiplier factor 0 (no multiplier), bonus 10 XP
  - So Wow! [Silver]: multiplier factor 0 (no multiplier), bonus 25 XP
  - So Wow! [Gold]: multiplier factor 0 (no multiplier), bonus 50 XP
  - So Wow! [Diamond]: multiplier factor 0 (no multiplier), bonus 100 XP
- Total Multiplier calculation:
  - Deltas: 0.01 + 0.02 + 0.03 + 0.16 = 0.22
  - Total Multiplier: 1.0 + 0.22 = 1.22
- Multiplied XP: 370 × 1.22 = 451.4 XP
- Bonus XP: 50 + 100 + 0 + 50 + 10 + 25 + 50 + 100 = 385 XP
- **Total XP**: 451.4 + 385 = **836.4 XP**

---

## 7. Removing Tests from the Codebase

### Overview
Tests are being removed from the system. The focus will be on math concepts and achievements only. All test-related code, UI components, and configuration should be removed.

### Files to Remove or Update

#### Backend
1. **`backend/app/config/tests/test_definitions.py`**
   - Remove entire file or mark for deletion
   - Contains `TEST_UNLOCK_REQUIREMENTS` dictionary

2. **`backend/app/services/test_service.py`**
   - Remove entire file or mark for deletion
   - Contains test unlock requirement checking logic

3. **`backend/app/routes/practice.py`**
   - Remove `test_type` parameter handling
   - Remove test session creation logic
   - Remove `is_test` flag handling

4. **`backend/app/services/session_engine_service.py`**
   - Remove `test_type` parameter
   - Remove `is_test` flag handling
   - Remove test-specific session generation logic

5. **`backend/app/services/practice_service.py`**
   - Remove `test_type` parameter from `create_session`
   - Remove test-related queries

6. **`backend/app/models.py`**
   - Remove `test_type` field from `PracticeSession` model (if exists)
   - Remove `is_test` field from `PracticeSession` model (if exists)

7. **Test Files**
   - `backend/tests/test_test_service.py` - Remove entire file
   - Update other test files to remove test-related test cases

#### Frontend
1. **`frontend/src/features/students/components/journey/`**
   - Remove `TestsTab.tsx` or entire Tests tab component
   - Remove test-related UI components

2. **`frontend/src/features/students/components/journey/JourneyTabNavigation.tsx`**
   - Remove "Tests" tab from navigation

3. **`frontend/src/features/practice/hooks/usePracticeAPI.ts`**
   - Remove `test_type` parameter handling
   - Remove `isTest` flag handling

4. **Test-related hooks and utilities**
   - Remove any test-specific hooks
   - Remove test unlock requirement checking logic

### Search Commands
```bash
# Find all test-related code
grep -r "test_type\|is_test\|isTest\|TEST_UNLOCK" --include="*.py" --include="*.ts" --include="*.tsx" backend/ frontend/

# Find test service references
grep -r "test_service\|TestService" --include="*.py" backend/

# Find test definitions
grep -r "test_definitions\|TEST_UNLOCK_REQUIREMENTS" --include="*.py" backend/

# Find test UI components
grep -r "test.*tab\|Test.*Tab\|TestsTab" --include="*.tsx" --include="*.ts" frontend/ -i
```

### Migration Steps
1. Remove test unlock requirements from concept unlock requirements (replace with concept-based achievements)
2. Remove test-related UI components
3. Remove test-related backend services and routes
4. Remove test-related database fields
5. Update all references to remove test parameters
6. Clean up test-related tests

---

## Reference & XP Awards


### Achievements & EXP Awards Requirements

**Level Master** - n consecutive correct at any level [30, 50, 84, 139, 233, 388, 648, 1080, 1803, 3000, 3000] (bronze through champion)
    - EXP: [832, 1850, 4040, 8229, 16380, 31583, 59940, 111888, 206804, 377400, 821400]
    - XP Multiplier: [1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 5.5, 6.0, 6.5]
    - NOTE: Terminology / function is going to have to change. Should not mention level, should be math concept.
    - NOTE: Rename to Math Master
 
**Accuracy Ace** - Session accuracy of X% or higher (min 10 questions) [80%, 90%, 100%] (bronze, silver, gold)
    - EXP: [10, 25, 50]
    - XP Multiplier: [1.01, 1.02, 1.03]

**Lightning Fast** - Average <X seconds per question at a specific level (min questions: [50, 100, 150, 200, 300, 400, 500, 750, 1000, 1500, 1500]) [5.0s, 4.0s, 3.0s, 2.5s, 2.0s, 1.5s, 1.0s, 0.85s, 0.7s, 0.6s, 0.6s] (bronze through champion)
    - EXP: [357, 810, 2065, 4794, 10753, 23258, 48890, 100291, 204274, 407202, 1000000]
    - XP Multiplier: [1.4, 1.8, 2.3, 2.9, 3.6, 4.4, 5.3, 6.3, 7.4, 8.6, 9.9]
    - NOTE: This term will have to change. Specific level should change to math concept
    - NOTE: Fine tuned the speed

**Question Master** - Answer n+ total questions [100, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000, 250000, 250000] (bronze through champion)
    - EXP: [160, 800, 1600, 4000, 8000, 16000, 40000, 80000, 160000, 400000, 800000]
    - XP Multiplier: [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

**Speed Demon** - Average <X seconds per question (min 10 questions) [5.0s, 4.0s, 3.0s, 2.5s, 2.0s, 1.5s, 1.0s, 0.85s, 0.7s, 0.6s, 0.6s] (bronze through champion)
    - EXP: [6, 14, 26, 40, 50, 80, 160, 360, 860, 2060, 4860]
    - XP Multiplier: [1.01, 1.02, 1.04, 1.08, 1.16, 1.32, 1.64, 2.28, 3.56, 6.12, 11.24]
    - NOTE: Finetuned the speed

**Perfect Streak** - n consecutive perfect sessions (awarded once per uninterrupted run) [3, 5, 10, 20, 50, 100, 250, 500, 1000, 2500, 2500] (bronze through champion)
    - EXP: [1554, 3330, 7148, 14915, 31036, 63166, 127073, 251748, 493661, 954600, 1098900]
    - XP Multiplier: [1.4, 1.8, 2.3, 2.9, 3.6, 4.4, 5.3, 6.3, 7.4, 8.6, 9.9]

**First Steps** - Answer your first question (bronze, unique)
    - EXP: [50]
    - XP Multiplier: [1.01]

**First Victory** - Complete your first session (silver, unique)
    - EXP: [100]
    - XP Multiplier: [1.02]

**Week Warrior** - Practice n days in a row [3, 7, 14, 30, 60, 90, 180, 365, 730, 1095, 1095] (bronze through champion)
    - EXP: [466, 1269, 3082, 8159, 20202, 37296, 93240, 236338, 586117, 1063519, 1205321]
    - XP Multiplier: [1.2, 1.4, 1.7, 2.1, 2.6, 3.2, 4.0, 5.0, 6.2, 7.5, 8.5]
    - NOTE: Adjusted champion rank. Should be the same as divine.

**Level Grandmaster** - Level Master (Bronze) on all levels (bronze)
    - EXP: [15540, 25900, 43512, 72002, 120694, 200984, 335664, 559440, 933954, 1554000, 1554000]
    - XP Multiplier: None
    - NOTE: There should be tiers with this. E.g. Silver requires silver for all levels
    - NOTE: Terminology should change, should require n tier achievement on all math concepts.
    - NOTE: Rename to Math Grand Master

**So, Wow!** - Acquire your first X tier achievement (all tiers)
    - EXP: [12, 28, 52, 78, 100, 180, 420, 980, 2300, 5400, 12500]
    - XP Multiplier: None
    - NOTE: User should only be allowed one per tier. Do we have a test to confirm this?

**Human Calculator** - Lightning Fast (Bronze) on all levels (bronze)
    - EXP: [4641, 10530, 26845, 62322, 139789, 302354, 635570, 1303783, 2655562, 5293626, 13000000]s
    - XP Multiplier: None
    - NOTE: Change termonlogy to math concept
    - NOTE: Like Level Grandmaster should have one for all tiers

**Master of Times Tables** - Level Master (X) and Lightning Fast (X) on all multiplication tables [bronze, silver, gold, platinum, diamond, master, grandmaster, legendary, mythic, divine, divine] (bronze through champion)
    - EXP: [12210, 22040, 42567, 81266, 157593, 304519, 587597, 1127241, 2171657, 4142814, 8805170]
    - XP Multiplier: None

**Master of Division Tables** - Level Master (X) and Lightning Fast (X) on all division tables [bronze, silver, gold, platinum, diamond, master, grandmaster, legendary, mythic, divine, divine] (bronze through champion)
    - EXP: [13431, 24244, 46823, 89393, 173352, 334971, 646356, 1239965, 2388823, 4557095, 9685687]
    - XP Multiplier: None

**Master of Basic Addition** - Level Master (X) and Lightning Fast (X) on all Single Digit Addition (0s-10s) tables [bronze, silver, gold, platinum, diamond, master, grandmaster, legendary, mythic, divine, divine] (bronze through champion)
    - EXP: [10091, 18215, 35179, 67162, 130242, 251669, 485617, 931612, 1794758, 3423813, 7277000]
    - XP Multiplier: None
    - NOTE: NEW
    - NOTE: Should use math concept terms

**Master of Basic Subtraction** - Level Master (X) and Lightning Fast (X) on all Single Digit Subtracition (0s-10s) tables [bronze, silver, gold, platinum, diamond, master, grandmaster, legendary, mythic, divine, divine] (bronze through champion)
    - EXP: [11100, 20037, 38697, 73878, 143266, 276836, 534179, 1024773, 1974234, 3766194, 8004700]
    - XP Multiplier: None
    - NOTE: NEW
    - NOTE: Should use math concept terms

---

## XP Multipliers

### Overview
Achievements provide XP multipliers that are applied to the base XP earned from correct answers. Each achievement tier has its own multiplier value that contributes to the total multiplier for the session.

### How It Works
- Each achievement tier has an **XP Multiplier** value stored in an array matching the EXP array size
- Multipliers are stored as **factors** (e.g., 1.01, 1.03, 1.32) but treated as **bonus deltas** in calculation
- Multipliers are **additive as deltas** - all multipliers from achievements earned during a session are converted to deltas (factor - 1.0) and summed
- Total multiplier calculation: `total_multiplier = 1.0 + sum(deltas)`
  - Example: factors 1.03 and 1.32 → deltas 0.03 and 0.32 → total = 1.0 + 0.03 + 0.32 = 1.35
- The total multiplier is then applied to the base XP from correct answers
- Display: Individual multipliers shown as deltas (x0.03, x0.32), total shown as full multiplier (x1.35)

### Achievement XP Multiplier Format
- Stored as an array matching the EXP array size
- Example for 11-tier achievement: `[1.01, 1.02, 1.03, 1.04, 1.05, 1.06, 1.07, 1.08, 1.09, 1.10, 4.50]`
- Example for 3-tier achievement: `[1.01, 1.02, 4.50]`
- Example for 1-tier achievement: `[1.01]` or `[4.50]` depending on tier

### XP Calculation
When a session is completed:
1. Base XP = Sum of (concept XP × number of correct answers for that concept)
2. Total Multiplier calculation:
   - Convert each multiplier factor to delta: `delta = factor - 1.0`
   - Sum all deltas: `sum_deltas = sum(all deltas)`
   - Total Multiplier = `1.0 + sum_deltas`
3. Multiplied XP = Base XP × Total Multiplier
4. Bonus XP = Sum of all EXP values from achievements earned during the session
5. Total XP = Multiplied XP + Bonus XP

### Example
Session with 10 correct answers on "Single Digit Addition (1s)" (37 XP each):
- Base XP: 10 × 37 = 370 XP
- Achievements earned:
  - First Steps: multiplier factor 1.01 (delta 0.01), bonus 50 XP
  - First Victory: multiplier factor 1.02 (delta 0.02), bonus 100 XP
  - Accuracy Ace [Gold]: multiplier factor 1.03 (delta 0.03), bonus 3 XP
  - Speed Demon [Diamond]: multiplier factor 1.16 (delta 0.16), bonus 6 XP
- Total Multiplier calculation:
  - Deltas: 0.01 + 0.02 + 0.03 + 0.16 = 0.22
  - Total Multiplier: 1.0 + 0.22 = 1.22
- Multiplied XP: 370 × 1.22 = 451.4 XP
- Bonus XP: 50 + 100 + 3 + 6 = 159 XP
- **Total XP**: 451.4 + 159 = **610.4 XP**

**Note**: Multipliers are displayed as deltas (x0.01, x0.02, etc.) in the UI, with the total shown as the full multiplier (x1.22).

---

## Concept Structure

Each concept includes:
- **Name**: Display name for the concept
- **Category**: Type of math operation (addition, subtraction, multiplication, division)
- **Unlock Requirements**: Achievements needed to unlock this concept
- **Math Type & Range**: Operation type and operand ranges
- **Metadata**: Additional configuration (layout, answer format, constraints, XP value)
  - **Layout Type**: How the problem is displayed (vertical, horizontal, long division, partial products)
  - **Answer Format**: Expected answer format (integer, remainder, fraction, decimal)
  - **Concept ID**: Unique identifier for the concept (e.g., `c_concept_001`, `c_add_1s`)
  - **XP**: Experience points awarded per correct answer (see "Experience Points (XP) Values" section)

---

## Single Digit Addition (1s)

### Name
Single Digit Addition (1s)

### Category
Addition

### Unlock Requirements
**None** - This is the starting concept, available from the beginning.

### Math Type & Range
- **Operation**: Addition
- **Operand 1 Range**: 1 to 9
- **Operand 2 Range**: 1
- **Answer Range**: Minimum 2

### Constraints
- Exclude zeros: Yes
- Minimum answer: 2

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_add_1s`
- **XP**: 37
### Example Problems
- 3 + 1 = ?
- 7 + 1 = ?
- 4 + 1 = ?

---

## Single Digit Addition (2s)

### Name
Single Digit Addition (2s)

### Category
Addition

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_add_1s` (1x)
2. **speed-demon-bronze** (1x)

### Math Type & Range
- **Operation**: Addition
- **Operand 1 Range**: 1 to 9
- **Operand 2 Range**: 2
- **Answer Range**: Minimum 3

### Constraints
- Exclude zeros: Yes
- Minimum answer: 3

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_add_2s`
- **XP**: 57
### Example Problems
- 3 + 2 = ?
- 7 + 2 = ?
- 4 + 2 = ?

---

## Single Digit Addition (3s)

### Name
Single Digit Addition (3s)

### Category
Addition

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_add_2s` (1x)

### Math Type & Range
- **Operation**: Addition
- **Operand 1 Range**: 1 to 9
- **Operand 2 Range**: 3
- **Answer Range**: Minimum 4

### Constraints
- Exclude zeros: Yes
- Minimum answer: 4

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_add_3s`
- **XP**: 62
### Example Problems
- 3 + 3 = ?
- 7 + 3 = ?
- 4 + 3 = ?

---

## Single Digit Addition (4s)

### Name
Single Digit Addition (4s)

### Category
Addition

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_add_3s` (1x)
2. **lightning-fast-bronze** with concept_id: `c_add_1s` (1x)

### Math Type & Range
- **Operation**: Addition
- **Operand 1 Range**: 1 to 9
- **Operand 2 Range**: 4
- **Answer Range**: Minimum 5

### Constraints
- Exclude zeros: Yes
- Minimum answer: 5

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_add_4s`
- **XP**: 67
### Example Problems
- 3 + 4 = ?
- 7 + 4 = ?
- 4 + 4 = ?

---

## Single Digit Addition (5s)

### Name
Single Digit Addition (5s)

### Category
Addition

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_add_4s` (1x)
2. **speed-demon-bronze** (2x)

### Math Type & Range
- **Operation**: Addition
- **Operand 1 Range**: 1 to 9
- **Operand 2 Range**: 5
- **Answer Range**: Minimum 6

### Constraints
- Exclude zeros: Yes
- Minimum answer: 6

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_add_5s`
- **XP**: 72
### Example Problems
- 3 + 5 = ?
- 7 + 5 = ?
- 4 + 5 = ?

---

## Single Digit Addition (6s)

### Name
Single Digit Addition (6s)

### Category
Addition

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_add_5s` (1x)
2. **level-master-silver** with concept_id: `c_add_1s` (1x)

### Math Type & Range
- **Operation**: Addition
- **Operand 1 Range**: 1 to 9
- **Operand 2 Range**: 6
- **Answer Range**: Minimum 7

### Constraints
- Exclude zeros: Yes
- Minimum answer: 7

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_add_6s`
- **XP**: 77
### Example Problems
- 3 + 6 = ?
- 7 + 6 = ?
- 4 + 6 = ?

---

## Single Digit Addition (7s)

### Name
Single Digit Addition (7s)

### Category
Addition

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_add_6s` (1x)
2. **perfect-streak-bronze** (1x)

### Math Type & Range
- **Operation**: Addition
- **Operand 1 Range**: 1 to 9
- **Operand 2 Range**: 7
- **Answer Range**: Minimum 8

### Constraints
- Exclude zeros: Yes
- Minimum answer: 8

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_add_7s`
- **XP**: 82
### Example Problems
- 3 + 7 = ?
- 7 + 7 = ?
- 4 + 7 = ?

---

## Single Digit Addition (8s)

### Name
Single Digit Addition (8s)

### Category
Addition

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_add_7s` (1x)
2. **lightning-fast-bronze** with concept_id: `c_add_2s` (1x)

### Math Type & Range
- **Operation**: Addition
- **Operand 1 Range**: 1 to 9
- **Operand 2 Range**: 8
- **Answer Range**: Minimum 9

### Constraints
- Exclude zeros: Yes
- Minimum answer: 9

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_add_8s`
- **XP**: 87
### Example Problems
- 3 + 8 = ?
- 7 + 8 = ?
- 4 + 8 = ?

---

## Single Digit Addition (9s)

### Name
Single Digit Addition (9s)

### Category
Addition

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_add_8s` (1x)
2. **level-master-gold** with concept_id: `c_add_1s` (1x)

### Math Type & Range
- **Operation**: Addition
- **Operand 1 Range**: 1 to 9
- **Operand 2 Range**: 9
- **Answer Range**: Minimum 10

### Constraints
- Exclude zeros: Yes
- Minimum answer: 10

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_add_9s`
- **XP**: 92
### Example Problems
- 3 + 9 = ?
- 7 + 9 = ?
- 4 + 9 = ?

---

## Single Digit Addition (10s)

### Name
Single Digit Addition (10s)

### Category
Addition

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_add_0s` (1x)
2. **level-master-bronze** with concept_id: `c_add_1s` (1x)
3. **accuracy-ace-bronze** (20x)

### Math Type & Range
- **Operation**: Addition
- **Operand 1 Range**: 1 to 9
- **Operand 2 Range**: 10
- **Answer Range**: Minimum 11

### Constraints
- Exclude zeros: Yes
- Minimum answer: 11

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_add_10s`
- **XP**: 52
### Example Problems
- 3 + 10 = ?
- 7 + 10 = ?
- 4 + 10 = ?

---

## Single Digit Addition (0s)

### Name
Single Digit Addition (0s)

### Category
Addition

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_002` (1x)
2. **speed-demon-silver** (1x)

### Math Type & Range
- **Operation**: Addition
- **Operand 1 Range**: 1 to 9
- **Operand 2 Range**: 0
- **Answer Range**: Minimum 1

### Constraints
- Exclude zeros: Yes
- Minimum answer: 1

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_add_0s`
- **XP**: 47
### Example Problems
- 3 + 0 = ?
- 7 + 0 = ?
- 4 + 0 = ?

---

## Basic Single Digit Addition

### Name
Basic Single Digit Addition

### Category
Addition

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_add_9s` (1x)
2. **master-of-basic-addition-bronze** (1x)

### Math Type & Range
- **Operation**: Addition
- **Operand 1 Range**: 1 to 9
- **Operand 2 Range**: 1 to 9
- **Answer Range**: Minimum 2

### Constraints
- Exclude zeros: Yes
- Minimum answer: 2

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_concept_001`
- **XP**: 97
### Example Problems
- 3 + 5 = ?
- 7 + 2 = ?
- 4 + 6 = ?

---

## Addition with Zero (Adding 0)

### Name
Addition with Zero (Adding 0)

### Category
Addition

### Unlock Requirements
1. **first-steps** (1x)
2. **first-victory** (1x)
3. **level-master-bronze** with concept_id: `c_add_1s` (1x)

### Math Type & Range
- **Operation**: Addition
- **Operand 1 Range**: 0 to 10
- **Operand 2 Range**: 0 (fixed)
- **Answer Range**: Minimum 0

### Constraints
- Exclude zeros: Yes
- Minimum answer: 0

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_concept_002`
- **XP**: 42
### Example Problems
- 5 + 0 = ?
- 0 + 0 = ?
- 10 + 0 = ?

---

## Single Digit Subtraction (1s)

### Name
Single Digit Subtraction (1s)

### Category
Subtraction

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_add_2s` (1x)
2. **level-master-bronze** with concept_id: `c_sub_0s` (1x)

### Math Type & Range
- **Operation**: Subtraction
- **Operand 1 Range**: 2 to 11
- **Operand 2 Range**: 1
- **Answer Range**: Minimum 1

### Constraints
- Exclude zeros: Yes
- Minimum answer: 1

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_sub_1s`
- **XP**: 127
### Example Problems
- 8 - 1 = ?
- 10 - 1 = ?
- 7 - 1 = ?

---

## Single Digit Subtraction (2s)

### Name
Single Digit Subtraction (2s)

### Category
Subtraction

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_sub_1s` (1x)
2. **level-master-bronze** with concept_id: `c_add_2s` (1x)

### Math Type & Range
- **Operation**: Subtraction
- **Operand 1 Range**: 3 to 12
- **Operand 2 Range**: 2
- **Answer Range**: Minimum 1

### Constraints
- Exclude zeros: Yes
- Minimum answer: 1

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_sub_2s`
- **XP**: 132
### Example Problems
- 9 - 2 = ?
- 12 - 2 = ?
- 8 - 2 = ?

---

## Single Digit Subtraction (3s)

### Name
Single Digit Subtraction (3s)

### Category
Subtraction

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_sub_2s` (1x)

### Math Type & Range
- **Operation**: Subtraction
- **Operand 1 Range**: 4 to 13
- **Operand 2 Range**: 3
- **Answer Range**: Minimum 1

### Constraints
- Exclude zeros: Yes
- Minimum answer: 1

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_sub_3s`
- **XP**: 137
### Example Problems
- 10 - 3 = ?
- 13 - 3 = ?
- 9 - 3 = ?

---

## Single Digit Subtraction (4s)

### Name
Single Digit Subtraction (4s)

### Category
Subtraction

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_sub_3s` (1x)
2. **lightning-fast-bronze** with concept_id: `c_sub_1s` (1x)

### Math Type & Range
- **Operation**: Subtraction
- **Operand 1 Range**: 5 to 14
- **Operand 2 Range**: 4
- **Answer Range**: Minimum 1

### Constraints
- Exclude zeros: Yes
- Minimum answer: 1

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_sub_4s`
- **XP**: 142
### Example Problems
- 11 - 4 = ?
- 14 - 4 = ?
- 10 - 4 = ?

---

## Single Digit Subtraction (5s)

### Name
Single Digit Subtraction (5s)

### Category
Subtraction

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_sub_4s` (1x)
2. **speed-demon-bronze** (4x)

### Math Type & Range
- **Operation**: Subtraction
- **Operand 1 Range**: 6 to 15
- **Operand 2 Range**: 5
- **Answer Range**: Minimum 1

### Constraints
- Exclude zeros: Yes
- Minimum answer: 1

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_sub_5s`
- **XP**: 147
### Example Problems
- 12 - 5 = ?
- 15 - 5 = ?
- 11 - 5 = ?

---

## Single Digit Subtraction (6s)

### Name
Single Digit Subtraction (6s)

### Category
Subtraction

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_sub_5s` (1x)
2. **level-master-silver** with concept_id: `c_sub_1s` (1x)

### Math Type & Range
- **Operation**: Subtraction
- **Operand 1 Range**: 7 to 16
- **Operand 2 Range**: 6
- **Answer Range**: Minimum 1

### Constraints
- Exclude zeros: Yes
- Minimum answer: 1

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_sub_6s`
- **XP**: 152
### Example Problems
- 13 - 6 = ?
- 16 - 6 = ?
- 12 - 6 = ?

---

## Single Digit Subtraction (7s)

### Name
Single Digit Subtraction (7s)

### Category
Subtraction

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_sub_6s` (1x)
2. **perfect-streak-bronze** (2x)

### Math Type & Range
- **Operation**: Subtraction
- **Operand 1 Range**: 8 to 17
- **Operand 2 Range**: 7
- **Answer Range**: Minimum 1

### Constraints
- Exclude zeros: Yes
- Minimum answer: 1

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_sub_7s`
- **XP**: 157
### Example Problems
- 14 - 7 = ?
- 17 - 7 = ?
- 13 - 7 = ?

---

## Single Digit Subtraction (8s)

### Name
Single Digit Subtraction (8s)

### Category
Subtraction

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_sub_7s` (1x)
2. **lightning-fast-bronze** with concept_id: `c_sub_2s` (1x)

### Math Type & Range
- **Operation**: Subtraction
- **Operand 1 Range**: 9 to 18
- **Operand 2 Range**: 8
- **Answer Range**: Minimum 1

### Constraints
- Exclude zeros: Yes
- Minimum answer: 1

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_sub_8s`
- **XP**: 162
### Example Problems
- 15 - 8 = ?
- 18 - 8 = ?
- 14 - 8 = ?

---

## Single Digit Subtraction (9s)

### Name
Single Digit Subtraction (9s)

### Category
Subtraction

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_sub_8s` (1x)
2. **level-master-gold** with concept_id: `c_sub_1s` (1x)

### Math Type & Range
- **Operation**: Subtraction
- **Operand 1 Range**: 10 to 19
- **Operand 2 Range**: 9
- **Answer Range**: Minimum 1

### Constraints
- Exclude zeros: Yes
- Minimum answer: 1

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_sub_9s`
- **XP**: 167
### Example Problems
- 16 - 9 = ?
- 19 - 9 = ?
- 15 - 9 = ?

---

## Single Digit Subtraction (10s)

### Name
Single Digit Subtraction (10s)

### Category
Subtraction

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_sub_9s` (1x)
2. **level-master-silver** with concept_id: `c_add_10s` (1x)

### Math Type & Range
- **Operation**: Subtraction
- **Operand 1 Range**: 11 to 20
- **Operand 2 Range**: 10
- **Answer Range**: Minimum 1

### Constraints
- Exclude zeros: Yes
- Minimum answer: 1

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_sub_10s`
- **XP**: 172
### Example Problems
- 18 - 10 = ?
- 20 - 10 = ?
- 17 - 10 = ?

---

## Single Digit Subtraction (0s)

### Name
Single Digit Subtraction (0s)

### Category
Subtraction

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_004` (1x)
2. **speed-demon-silver** (2x)

### Math Type & Range
- **Operation**: Subtraction
- **Operand 1 Range**: 1 to 10
- **Operand 2 Range**: 0
- **Answer Range**: Minimum 1

### Constraints
- Exclude zeros: Yes
- Minimum answer: 1

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_sub_0s`
- **XP**: 122
### Example Problems
- 8 - 0 = ?
- 10 - 0 = ?
- 7 - 0 = ?

---

## Basic Single Digit Subtraction

### Name
Basic Single Digit Subtraction

### Category
Subtraction

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_sub_10s` (1x)
2. **master-of-basic-subtraction-bronze** (1x)

### Math Type & Range
- **Operation**: Subtraction
- **Operand 1 Range**: 1 to 10
- **Operand 2 Range**: 1 to 10
- **Answer Range**: Minimum 1

### Constraints
- Exclude zeros: Yes
- Minimum answer: 1

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_concept_003`
- **XP**: 177
### Example Problems
- 8 - 3 = ?
- 10 - 5 = ?
- 7 - 2 = ?

---

## Subtraction with Zero (Subtracting 0)

### Name
Subtraction with Zero (Subtracting 0)

### Category
Subtraction

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_add_2s` (1x)
2. **lightning-fast-bronze** with concept_id: `c_add_1s` (1x)

### Math Type & Range
- **Operation**: Subtraction
- **Operand 1 Range**: 0 to 10
- **Operand 2 Range**: 0 (fixed)
- **Answer Range**: Minimum 0

### Constraints
- Exclude zeros: No
- Minimum answer: 0

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_concept_004`
- **XP**: 117
### Example Problems
- 5 - 0 = ?
- 0 - 0 = ?
- 10 - 0 = ?

---

## Single and Two Digit Addition

### Name
Single and Two Digit Addition

### Category
Addition

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_001` (1x)
2. **master-of-basic-addition-bronze** (1x)
3. **lightning-fast-silver** with concept_id: `c_add_1s` (1x)

### Math Type & Range
- **Operation**: Addition
- **Operand 1 Range**: 0 to 9
- **Operand 2 Range**: 10 to 99
- **Answer Range**: No minimum

### Constraints
- None

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_concept_005`
- **XP**: 102
### Example Problems
- 5 + 23 = ?
- 9 + 45 = ?
- 0 + 67 = ?

---

## Single and Two Digit Subtraction

### Name
Single and Two Digit Subtraction

### Category
Subtraction

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_003` (1x)
2. **master-of-basic-subtraction-bronze** (1x)
3. **lightning-fast-silver** with concept_id: `c_sub_1s` (1x)

### Math Type & Range
- **Operation**: Subtraction
- **Operand 1 Range**: 0 to 9
- **Operand 2 Range**: 10 to 99
- **Answer Range**: Minimum 0

### Constraints
- Minimum answer: 0

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_concept_006`
- **XP**: 182
### Example Problems
- 9 - 12 = ? (negative result)
- 5 - 15 = ? (negative result)
- 8 - 11 = ? (negative result)

---

## Two Digit Addition

### Name
Two Digit Addition

### Category
Addition

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_005` (1x)
2. **master-of-basic-addition-silver** (1x)
3. **speed-demon-gold** (1x)

### Math Type & Range
- **Operation**: Addition
- **Operand 1 Range**: 10 to 99
- **Operand 2 Range**: 10 to 99
- **Answer Range**: No minimum

### Constraints
- None

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_concept_007`
- **XP**: 107
### Example Problems
- 23 + 45 = ?
- 67 + 89 = ?
- 34 + 56 = ?

---

## Two Digit Subtraction

### Name
Two Digit Subtraction

### Category
Subtraction

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_006` (1x)
2. **master-of-basic-subtraction-silver** (1x)
3. **speed-demon-bronze** (8x)

### Math Type & Range
- **Operation**: Subtraction
- **Operand 1 Range**: 10 to 99
- **Operand 2 Range**: 10 to 99
- **Answer Range**: Minimum 0

### Constraints
- Minimum answer: 0

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_concept_008`
- **XP**: 187
### Example Problems
- 45 - 23 = ?
- 89 - 67 = ?
- 56 - 34 = ?

---

## Subtraction with Borrowing (Small Numbers)

### Name
Subtraction with Borrowing (Small Numbers)

### Category
Subtraction

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_023` (1x)
2. **accuracy-ace-silver** (40x)
3. **lightning-fast-silver** with concept_id: `c_sub_1s` (1x)

### Math Type & Range
- **Operation**: Subtraction
- **Operand 1 Range**: 0 to 1
- **Operand 2 Range**: 1 to 10
- **Answer Range**: No minimum

### Constraints
- None

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_concept_009`
- **XP**: 197
### Example Problems
- 1 - 5 = ? (negative result)
- 0 - 3 = ? (negative result)
- 1 - 10 = ? (negative result)

---

## Negative Number Subtraction

### Name
Negative Number Subtraction

### Category
Subtraction

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_009` (1x)
2. **speed-demon-silver** (4x)
3. **perfect-streak-silver** (1x)

### Math Type & Range
- **Operation**: Subtraction
- **Operand 1 Range**: -99 to 0
- **Operand 2 Range**: 0 to 99
- **Answer Range**: Minimum -100

### Constraints
- Minimum answer: -100

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_concept_010`
- **XP**: 202
### Example Problems
- -5 - 10 = ?
- -23 - 45 = ?
- -67 - 12 = ?

---

## Multiplication by 1

### Name
Multiplication by 1

### Category
Multiplication

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_018` (1x)
2. **lightning-fast-platinum** with concept_id: `c_add_1s` (1x)
3. **level-master-silver** with concept_id: `c_sub_1s` (1x)

### Math Type & Range
- **Operation**: Multiplication
- **Operand 1 Range**: 1 to 12
- **Operand 2 Range**: 1 (fixed)
- **Answer Range**: No minimum

### Constraints
- Fixed operand 2: 1

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_concept_011`
- **XP**: 212
### Example Problems
- 5 × 1 = ?
- 12 × 1 = ?
- 7 × 1 = ?

---

## Multiplication by 2

### Name
Multiplication by 2

### Category
Multiplication

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_011` (1x)
2. **speed-demon-gold** (2x)

### Math Type & Range
- **Operation**: Multiplication
- **Operand 1 Range**: 1 to 12
- **Operand 2 Range**: 2 (fixed)
- **Answer Range**: No minimum

### Constraints
- Fixed operand 2: 2

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_mul_2s`
- **XP**: 215
### Example Problems
- 5 × 2 = ?
- 12 × 2 = ?
- 7 × 2 = ?

---

## Multiplication by 3

### Name
Multiplication by 3

### Category
Multiplication

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_mul_2s` (1x)
2. **speed-demon-platinum** (1x)

### Math Type & Range
- **Operation**: Multiplication
- **Operand 1 Range**: 1 to 12
- **Operand 2 Range**: 3 (fixed)
- **Answer Range**: No minimum

### Constraints
- Fixed operand 2: 3

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_mul_3s`
- **XP**: 220
### Example Problems
- 5 × 3 = ?
- 12 × 3 = ?
- 7 × 3 = ?

---

## Multiplication by 4

### Name
Multiplication by 4

### Category
Multiplication

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_013` (1x)
2. **level-master-silver** with concept_id: `c_add_4s` (1x)

### Math Type & Range
- **Operation**: Multiplication
- **Operand 1 Range**: 1 to 12
- **Operand 2 Range**: 4 (fixed)
- **Answer Range**: No minimum

### Constraints
- Fixed operand 2: 4

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_concept_012`
- **XP**: 227
### Example Problems
- 3 × 4 = ?
- 7 × 4 = ?
- 12 × 4 = ?

---

## Multiplication by 5

### Name
Multiplication by 5

### Category
Multiplication

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_019` (1x)
2. **lightning-fast-gold** with concept_id: `c_add_5s` (1x)

### Math Type & Range
- **Operation**: Multiplication
- **Operand 1 Range**: 1 to 12
- **Operand 2 Range**: 5 (fixed)
- **Answer Range**: No minimum

### Constraints
- Fixed operand 2: 5

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_concept_013`
- **XP**: 222
### Example Problems
- 6 × 5 = ?
- 9 × 5 = ?
- 12 × 5 = ?

---

## Multiplication by 6

### Name
Multiplication by 6

### Category
Multiplication

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_021` (1x)
2. **level-master-gold** with concept_id: `c_add_1s` (1x)

### Math Type & Range
- **Operation**: Multiplication
- **Operand 1 Range**: 1 to 12
- **Operand 2 Range**: 6 (fixed)
- **Answer Range**: No minimum

### Constraints
- Fixed operand 2: 6

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_concept_014`
- **XP**: 242
### Example Problems
- 4 × 6 = ?
- 8 × 6 = ?
- 11 × 6 = ?

---

## Multiplication by 7

### Name
Multiplication by 7

### Category
Multiplication

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_014` (1x)
2. **level-master-silver** with concept_id: `c_sub_1s` (1x)

### Math Type & Range
- **Operation**: Multiplication
- **Operand 1 Range**: 1 to 12
- **Operand 2 Range**: 7 (fixed)
- **Answer Range**: No minimum

### Constraints
- Fixed operand 2: 7

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_concept_015`
- **XP**: 247
### Example Problems
- 5 × 7 = ?
- 9 × 7 = ?
- 12 × 7 = ?

---

## Multiplication by 8

### Name
Multiplication by 8

### Category
Multiplication

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_015` (1x)
2. **speed-demon-bronze** (16x)

### Math Type & Range
- **Operation**: Multiplication
- **Operand 1 Range**: 1 to 12
- **Operand 2 Range**: 8 (fixed)
- **Answer Range**: No minimum

### Constraints
- Fixed operand 2: 8

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_concept_016`
- **XP**: 252
### Example Problems
- 3 × 8 = ?
- 7 × 8 = ?
- 11 × 8 = ?

---

## Multiplication by 9

### Name
Multiplication by 9

### Category
Multiplication

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_016` (1x)
2. **lightning-fast-gold** with concept_id: `c_add_1s` (1x)

### Math Type & Range
- **Operation**: Multiplication
- **Operand 1 Range**: 1 to 12
- **Operand 2 Range**: 9 (fixed)
- **Answer Range**: No minimum

### Constraints
- Fixed operand 2: 9

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_concept_017`
- **XP**: 257
### Example Problems
- 4 × 9 = ?
- 8 × 9 = ?
- 12 × 9 = ?

---

## Multiplication by 0

### Name
Multiplication by 0

### Category
Multiplication

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_010` (1x)
2. **level-master-master** with concept_id: `c_add_0s` (1x)
3. **master-of-basic-addition-silver** (1x)

### Math Type & Range
- **Operation**: Multiplication
- **Operand 1 Range**: 1 to 12
- **Operand 2 Range**: 0 (fixed)
- **Answer Range**: No minimum

### Constraints
- Fixed operand 2: 0

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_concept_018`
- **XP**: 207
### Example Problems
- 5 × 0 = ?
- 12 × 0 = ?
- 7 × 0 = ?

---

## Multiplication by 10

### Name
Multiplication by 10

### Category
Multiplication

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_mul_3s` (1x)
2. **level-master-silver** with concept_id: `c_add_10s` (1x)

### Math Type & Range
- **Operation**: Multiplication
- **Operand 1 Range**: 1 to 12
- **Operand 2 Range**: 10 (fixed)
- **Answer Range**: No minimum

### Constraints
- Fixed operand 2: 10

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_concept_019`
- **XP**: 217
### Example Problems
- 6 × 10 = ?
- 9 × 10 = ?
- 12 × 10 = ?

---

## Multiplication by 11

### Name
Multiplication by 11

### Category
Multiplication

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_012` (1x)
2. **speed-demon-silver** (8x)

### Math Type & Range
- **Operation**: Multiplication
- **Operand 1 Range**: 1 to 12
- **Operand 2 Range**: 11 (fixed)
- **Answer Range**: No minimum

### Constraints
- Fixed operand 2: 11

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_concept_020`
- **XP**: 232
### Example Problems
- 5 × 11 = ?
- 8 × 11 = ?
- 12 × 11 = ?

---

## Multiplication by 12

### Name
Multiplication by 12

### Category
Multiplication

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_020` (1x)
2. **perfect-streak-bronze** (4x)

### Math Type & Range
- **Operation**: Multiplication
- **Operand 1 Range**: 1 to 12
- **Operand 2 Range**: 12 (fixed)
- **Answer Range**: No minimum

### Constraints
- Fixed operand 2: 12

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_concept_021`
- **XP**: 237
### Example Problems
- 7 × 12 = ?
- 10 × 12 = ?
- 12 × 12 = ?

---

## Three Digit Addition

### Name
Three Digit Addition

### Category
Addition

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_007` (1x)
2. **master-of-basic-addition-gold** (1x)
3. **perfect-streak-silver** (2x)

### Math Type & Range
- **Operation**: Addition
- **Operand 1 Range**: 100 to 999
- **Operand 2 Range**: 100 to 999
- **Answer Range**: No minimum

### Constraints
- None

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_concept_022`
- **XP**: 112
### Example Problems
- 234 + 567 = ?
- 456 + 789 = ?
- 123 + 456 = ?

---

## Three Digit Subtraction

### Name
Three Digit Subtraction

### Category
Subtraction

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_008` (1x)
2. **master-of-basic-subtraction-gold** (1x)
3. **perfect-streak-gold** (1x)

### Math Type & Range
- **Operation**: Subtraction
- **Operand 1 Range**: 100 to 999
- **Operand 2 Range**: 100 to 999
- **Answer Range**: Minimum 0

### Constraints
- Minimum answer: 0

### Metadata
- **Layout Type**: Vertical
- **Answer Format**: Integer
- **Concept ID**: `c_concept_023`
- **XP**: 192
### Example Problems
- 567 - 234 = ?
- 789 - 456 = ?
- 456 - 123 = ?

---

## Two Digit by Single Digit Multiplication (Partial Products)

### Name
Two Digit by Single Digit Multiplication (Partial Products)

### Category
Multiplication

### Unlock Requirements
1. **level-master-silver** with concept_id: `c_concept_017` (1x)
2. **master-of-times-tables-bronze** (1x)
3. **question-master-master** (1x)
4. **perfect-streak-bronze** (8x)

### Math Type & Range
- **Operation**: Multiplication
- **Operand 1 Range**: 10 to 99
- **Operand 2 Range**: 2 to 9
- **Answer Range**: No minimum

### Constraints
- None

### Metadata
- **Layout Type**: Partial Products
- **Partial Products Mode**: Easy
- **Answer Format**: Integer
- **Concept ID**: `c_concept_024`
- **XP**: 262
### Example Problems
- 23 × 4 = ?
- 45 × 6 = ?
- 67 × 8 = ?

---

## Two Digit by Two Digit Multiplication (Partial Products)

### Name
Two Digit by Two Digit Multiplication (Partial Products)

### Category
Multiplication

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_024` (1x)
2. **master-of-times-tables-silver** (1x)
3. **so-wow-diamond** (1x)
4. **perfect-streak-silver** (4x)

### Math Type & Range
- **Operation**: Multiplication
- **Operand 1 Range**: 10 to 99
- **Operand 2 Range**: 10 to 99
- **Answer Range**: No minimum

### Constraints
- None

### Metadata
- **Layout Type**: Partial Products
- **Partial Products Mode**: Normal
- **Answer Format**: Integer
- **Concept ID**: `c_concept_025`
- **XP**: 267
### Example Problems
- 23 × 45 = ?
- 56 × 78 = ?
- 34 × 67 = ?

---

## Division by 1

### Name
Division by 1

### Category
Division

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_043` (1x)
2. **level-master-silver** with concept_id: `c_concept_011` (1x)
3. **lightning-fast-gold** with concept_id: `c_add_1s` (1x)

### Math Type & Range
- **Operation**: Division
- **Operand 1 Range**: 1 to 12
- **Operand 2 Range**: 1 (fixed)
- **Answer Range**: No minimum

### Constraints
- Fixed operand 2: 1
- No remainder: Yes

### Metadata
- **Layout Type**: Long Division
- **Answer Format**: Integer
- **Concept ID**: `c_concept_026`
- **XP**: 277
### Example Problems
- 5 ÷ 1 = ?
- 12 ÷ 1 = ?
- 7 ÷ 1 = ?

---

## Division by 2

### Name
Division by 2

### Category
Division

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_026` (1x)
2. **level-master-bronze** with concept_id: `c_concept_014` (1x)
3. **question-master-grandmaster** (1x)

### Math Type & Range
- **Operation**: Division
- **Operand 1 Range**: 2 to 24
- **Operand 2 Range**: 2 (fixed)
- **Answer Range**: No minimum

### Constraints
- Fixed operand 2: 2
- No remainder: Yes
- Multiple of: 2

### Metadata
- **Layout Type**: Long Division
- **Answer Format**: Integer
- **Concept ID**: `c_concept_027`
- **XP**: 282
### Example Problems
- 4 ÷ 2 = ?
- 12 ÷ 2 = ?
- 24 ÷ 2 = ?

---

## Division by 3

### Name
Division by 3

### Category
Division

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_038` (1x)
2. **level-master-bronze** with concept_id: `c_concept_021` (1x)
3. **master-of-basic-subtraction-silver** (1x)

### Math Type & Range
- **Operation**: Division
- **Operand 1 Range**: 3 to 36
- **Operand 2 Range**: 3 (fixed)
- **Answer Range**: No minimum

### Constraints
- Fixed operand 2: 3
- No remainder: Yes
- Multiple of: 3

### Metadata
- **Layout Type**: Long Division
- **Answer Format**: Integer
- **Concept ID**: `c_concept_028`
- **XP**: 297
### Example Problems
- 6 ÷ 3 = ?
- 15 ÷ 3 = ?
- 36 ÷ 3 = ?

---

## Division by 4

### Name
Division by 4

### Category
Division

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_028` (1x)
2. **level-master-bronze** with concept_id: `c_concept_012` (1x)

### Math Type & Range
- **Operation**: Division
- **Operand 1 Range**: 4 to 48
- **Operand 2 Range**: 4 (fixed)
- **Answer Range**: No minimum

### Constraints
- Fixed operand 2: 4
- No remainder: Yes
- Multiple of: 4

### Metadata
- **Layout Type**: Long Division
- **Answer Format**: Integer
- **Concept ID**: `c_concept_029`
- **XP**: 302
### Example Problems
- 8 ÷ 4 = ?
- 20 ÷ 4 = ?
- 48 ÷ 4 = ?

---

## Division by 5

### Name
Division by 5

### Category
Division

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_029` (1x)
2. **level-master-bronze** with concept_id: `c_concept_013` (1x)

### Math Type & Range
- **Operation**: Division
- **Operand 1 Range**: 5 to 60
- **Operand 2 Range**: 5 (fixed)
- **Answer Range**: No minimum

### Constraints
- Fixed operand 2: 5
- No remainder: Yes
- Multiple of: 5

### Metadata
- **Layout Type**: Long Division
- **Answer Format**: Integer
- **Concept ID**: `c_concept_030`
- **XP**: 307
### Example Problems
- 10 ÷ 5 = ?
- 25 ÷ 5 = ?
- 60 ÷ 5 = ?

---

## Division by 6

### Name
Division by 6

### Category
Division

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_030` (1x)
2. **level-master-bronze** with concept_id: `c_concept_014` (1x)

### Math Type & Range
- **Operation**: Division
- **Operand 1 Range**: 6 to 72
- **Operand 2 Range**: 6 (fixed)
- **Answer Range**: No minimum

### Constraints
- Fixed operand 2: 6
- No remainder: Yes
- Multiple of: 6

### Metadata
- **Layout Type**: Long Division
- **Answer Format**: Integer
- **Concept ID**: `c_concept_031`
- **XP**: 312
### Example Problems
- 12 ÷ 6 = ?
- 30 ÷ 6 = ?
- 72 ÷ 6 = ?

---

## Division by 7

### Name
Division by 7

### Category
Division

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_031` (1x)
2. **level-master-bronze** with concept_id: `c_concept_015` (1x)
3. **question-master-legendary** (1x)

### Math Type & Range
- **Operation**: Division
- **Operand 1 Range**: 7 to 84
- **Operand 2 Range**: 7 (fixed)
- **Answer Range**: No minimum

### Constraints
- Fixed operand 2: 7
- No remainder: Yes
- Multiple of: 7

### Metadata
- **Layout Type**: Long Division
- **Answer Format**: Integer
- **Concept ID**: `c_concept_032`
- **XP**: 317
### Example Problems
- 14 ÷ 7 = ?
- 35 ÷ 7 = ?
- 84 ÷ 7 = ?

---

## Division by 8

### Name
Division by 8

### Category
Division

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_032` (1x)
2. **level-master-bronze** with concept_id: `c_concept_016` (1x)

### Math Type & Range
- **Operation**: Division
- **Operand 1 Range**: 8 to 96
- **Operand 2 Range**: 8 (fixed)
- **Answer Range**: No minimum

### Constraints
- Fixed operand 2: 8
- No remainder: Yes
- Multiple of: 8

### Metadata
- **Layout Type**: Long Division
- **Answer Format**: Integer
- **Concept ID**: `c_concept_033`
- **XP**: 322
### Example Problems
- 16 ÷ 8 = ?
- 40 ÷ 8 = ?
- 96 ÷ 8 = ?

---

## Division by 9

### Name
Division by 9

### Category
Division

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_033` (1x)
2. **level-master-bronze** with concept_id: `c_concept_017` (1x)

### Math Type & Range
- **Operation**: Division
- **Operand 1 Range**: 9 to 108
- **Operand 2 Range**: 9 (fixed)
- **Answer Range**: No minimum

### Constraints
- Fixed operand 2: 9
- No remainder: Yes
- Multiple of: 9

### Metadata
- **Layout Type**: Long Division
- **Answer Format**: Integer
- **Concept ID**: `c_concept_034`
- **XP**: 327
### Example Problems
- 18 ÷ 9 = ?
- 45 ÷ 9 = ?
- 108 ÷ 9 = ?

---

## Division by 10

### Name
Division by 10

### Category
Division

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_027` (1x)
2. **level-master-silver** with concept_id: `c_concept_019` (1x)

### Math Type & Range
- **Operation**: Division
- **Operand 1 Range**: 10 to 120
- **Operand 2 Range**: 10 (fixed)
- **Answer Range**: No minimum

### Constraints
- Fixed operand 2: 10
- No remainder: Yes
- Multiple of: 10

### Metadata
- **Layout Type**: Long Division
- **Answer Format**: Integer
- **Concept ID**: `c_concept_035`
- **XP**: 287
### Example Problems
- 20 ÷ 10 = ?
- 50 ÷ 10 = ?
- 120 ÷ 10 = ?

---

## Division by 11

### Name
Division by 11

### Category
Division

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_034` (1x)
2. **level-master-bronze** with concept_id: `c_concept_020` (1x)

### Math Type & Range
- **Operation**: Division
- **Operand 1 Range**: 11 to 132
- **Operand 2 Range**: 11 (fixed)
- **Answer Range**: No minimum

### Constraints
- Fixed operand 2: 11
- No remainder: Yes
- Multiple of: 11

### Metadata
- **Layout Type**: Long Division
- **Answer Format**: Integer
- **Concept ID**: `c_concept_036`
- **XP**: 332
### Example Problems
- 22 ÷ 11 = ?
- 55 ÷ 11 = ?
- 132 ÷ 11 = ?

---

## Division by 0 (Special Case)

### Name
Division by 0 (Special Case)

### Category
Division

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_036` (1x)
2. **accuracy-ace-gold** (80x)

### Math Type & Range
- **Operation**: Division
- **Operand 1 Range**: 0 (fixed)
- **Operand 2 Range**: 0 (fixed)
- **Answer Range**: No minimum

### Constraints
- Fixed operand 2: 0
- No remainder: Yes

### Metadata
- **Layout Type**: Long Division
- **Answer Format**: Integer
- **Concept ID**: `c_concept_037`
- **XP**: 337
### Example Problems
- 0 ÷ 0 = ? (undefined/indeterminate)

---

## Division by 10 (Repeated)

### Name
Division by 10 (Repeated)

### Category
Division

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_035` (1x)
2. **speed-demon-gold** (4x)
3. **perfect-streak-platinum** (1x)

### Math Type & Range
- **Operation**: Division
- **Operand 1 Range**: 10 to 120
- **Operand 2 Range**: 10 (fixed)
- **Answer Range**: No minimum

### Constraints
- Fixed operand 2: 10
- No remainder: Yes
- Multiple of: 10

### Metadata
- **Layout Type**: Long Division
- **Answer Format**: Integer
- **Concept ID**: `c_concept_038`
- **XP**: 292
### Example Problems
- 20 ÷ 10 = ?
- 50 ÷ 10 = ?
- 120 ÷ 10 = ?

---

## Division with Remainders (Single Digit Divisors)

### Name
Division with Remainders (Single Digit Divisors)

### Category
Division

### Unlock Requirements
1. **level-master-silver** with concept_id: `c_concept_036` (1x)
2. **master-of-division-tables-bronze** (1x)

### Math Type & Range
- **Operation**: Division
- **Operand 1 Range**: 1 to 99
- **Operand 2 Range**: 2 to 9
- **Answer Range**: No minimum

### Constraints
- None

### Metadata
- **Layout Type**: Long Division
- **Answer Format**: Remainder
- **Concept ID**: `c_concept_039`
- **XP**: 342
### Example Problems
- 17 ÷ 5 = ? (remainder 2)
- 23 ÷ 7 = ? (remainder 2)
- 31 ÷ 4 = ? (remainder 3)

---

## Division with Remainders (Two Digit Dividends)

### Name
Division with Remainders (Two Digit Dividends)

### Category
Division

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_039` (1x)
2. **master-of-division-tables-silver** (1x)

### Math Type & Range
- **Operation**: Division
- **Operand 1 Range**: 10 to 99
- **Operand 2 Range**: 2 to 9
- **Answer Range**: No minimum

### Constraints
- None

### Metadata
- **Layout Type**: Long Division
- **Answer Format**: Remainder
- **Concept ID**: `c_concept_040`
- **XP**: 347
### Example Problems
- 45 ÷ 7 = ? (remainder 3)
- 67 ÷ 8 = ? (remainder 3)
- 89 ÷ 6 = ? (remainder 5)

---

## Division with Fractional Answers (Single Digit Divisors)

### Name
Division with Fractional Answers (Single Digit Divisors)

### Category
Division

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_040` (1x)
2. **question-master-mythic** (1x)

### Math Type & Range
- **Operation**: Division
- **Operand 1 Range**: 1 to 99
- **Operand 2 Range**: 2 to 9
- **Answer Range**: No minimum

### Constraints
- None

### Metadata
- **Layout Type**: Long Division
- **Answer Format**: Fraction
- **Concept ID**: `c_concept_041`
- **XP**: 352
### Example Problems
- 5 ÷ 3 = ? (1 2/3)
- 7 ÷ 4 = ? (1 3/4)
- 11 ÷ 6 = ? (1 5/6)

---

## Division with Fractional Answers (Two Digit Dividends)

### Name
Division with Fractional Answers (Two Digit Dividends)

### Category
Division

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_041` (1x)
2. **so-wow-master** (1x)

### Math Type & Range
- **Operation**: Division
- **Operand 1 Range**: 10 to 99
- **Operand 2 Range**: 2 to 9
- **Answer Range**: No minimum

### Constraints
- None

### Metadata
- **Layout Type**: Long Division
- **Answer Format**: Fraction
- **Concept ID**: `c_concept_042`
- **XP**: 357
### Example Problems
- 23 ÷ 7 = ? (3 2/7)
- 45 ÷ 8 = ? (5 5/8)
- 67 ÷ 9 = ? (7 4/9)

---

## Three Digit by Two Digit Multiplication (Partial Products)

### Name
Three Digit by Two Digit Multiplication (Partial Products)

### Category
Multiplication

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_025` (1x)
2. **master-of-times-tables-gold** (1x)
3. **accuracy-ace-gold** (160x)
4. **perfect-streak-gold** (2x)

### Math Type & Range
- **Operation**: Multiplication
- **Operand 1 Range**: 10 to 99
- **Operand 2 Range**: 100 to 999
- **Answer Range**: No minimum

### Constraints
- None

### Metadata
- **Layout Type**: Partial Products
- **Partial Products Mode**: Normal
- **Answer Format**: Integer
- **Concept ID**: `c_concept_043`
- **XP**: 272
### Example Problems
- 23 × 456 = ?
- 45 × 789 = ?
- 67 × 234 = ?

---

## Division with Fractional Answers (Three Digit Dividends)

### Name
Division with Fractional Answers (Three Digit Dividends)

### Category
Division

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_042` (1x)
2. **so-wow-grandmaster** (1x)

### Math Type & Range
- **Operation**: Division
- **Operand 1 Range**: 100 to 999
- **Operand 2 Range**: 2 to 9
- **Answer Range**: No minimum

### Constraints
- None

### Metadata
- **Layout Type**: Long Division
- **Answer Format**: Fraction
- **Concept ID**: `c_concept_044`
- **XP**: 362
### Example Problems
- 234 ÷ 7 = ? (33 3/7)
- 456 ÷ 8 = ? (57)
- 789 ÷ 9 = ? (87 2/3)

---

## Division with Decimal Answers (Single Digit Divisors)

### Name
Division with Decimal Answers (Single Digit Divisors)

### Category
Division

### Unlock Requirements
1. **level-master-bronze** with concept_id: `c_concept_044` (1x)
2. **master-of-division-tables-gold** (1x)

### Math Type & Range
- **Operation**: Division
- **Operand 1 Range**: 1 to 99
- **Operand 2 Range**: 2 to 9
- **Answer Range**: No minimum

### Constraints
- None

### Metadata
- **Layout Type**: Long Division
- **Answer Format**: Decimal
- **Concept ID**: `c_concept_045`
- **XP**: 367
### Example Problems
- 5 ÷ 3 = ? (1.666...)
- 7 ÷ 4 = ? (1.75)
- 11 ÷ 6 = ? (1.833...)

---

