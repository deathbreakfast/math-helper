# Remove Legacy Level System - Third Attempt

**Goal**: Completely remove the legacy level system. Level should ONLY be used for UI display and should be calculated from XP. There should be ZERO requirements for level anywhere in the codebase.

## Current State

The codebase is transitioning from a level-based system to a concept-based system (`concept_id`). However, legacy level fields and logic are still present throughout the codebase, causing confusion and bugs.

### Key Principles
1. **Level is display-only**: Level should be calculated from XP using `XPService.level_for_total_xp()`
2. **No level requirements**: Nothing should require a specific level to unlock or access
3. **Concept-based**: All logic should use `concept_id`, not `level`
4. **Session level is legacy**: `PracticeSession.level` should be removed
5. **Question required_level is legacy**: `Question.required_level` should be removed

---

## Database Models

### PracticeSession.level
**Location**: `backend/app/models.py:42`

```python
level = db.Column(db.Integer, nullable=True)
```

**Current Usage**:
- Used in session generation (`SessionEngineService`)
- Used in session resuming (`SessionResumeService`)
- Used in achievement filtering (`AchievementQueryService`)
- Used in achievement checkers (multiple)
- Returned in API responses

**Action Required**:
- Remove all logic that sets or requires `session.level`
- Remove all queries that filter by `session.level`
- Field is already nullable - stop using it entirely
- Remove field from database schema after code changes are complete

**Files to Update**:
- `backend/app/services/session_engine_service.py` - Lines 24, 50, 72, 87, 92, 97
- `backend/app/services/session_resume_service.py` - Lines 80-81, 117-119
- `backend/app/services/session_completion_service.py` - Line 209
- `backend/app/services/practice_service.py` - Line 442
- `backend/app/routes/practice.py` - Line 98
- `backend/app/services/achievements/achievement_queries/achievement_query_service.py` - Lines 232-257
- `backend/app/services/achievements/achievement_checkers/accuracy_ace_checker.py` - Lines 99-101
- `backend/app/services/achievements/achievement_checkers/lightning_fast_checker.py` - Lines 59-61
- `backend/app/services/achievements/achievement_checkers/generic_accuracy_checker.py` - Lines 34, 59

### Question.required_level
**Location**: `backend/app/models.py:67`

```python
required_level = db.Column(db.Integer, default=1, nullable=False, index=True)  # minimum level to attempt
```

**Current Usage**:
- Used in `PracticeService.get_questions_for_level()` to filter questions
- Used in achievement checkers to filter by level
- Used in question generation to set required_level
- Has database index: `ix_questions_required_level`
- Has composite index: `ix_questions_operation_level`

**Action Required**:
- Remove `required_level` field entirely OR make it nullable/display-only
- Remove all queries that filter by `Question.required_level`
- Remove database indexes on `required_level`
- Stop setting `required_level` when creating questions

**Files to Update**:
- `backend/app/services/practice_service.py` - Lines 73, 95, 119-133 (entire `get_questions_for_level` method)
- `backend/app/services/question_service.py` - Lines 137, 194, 328, 348, 516, 524, 589, 678-693, 735
- `backend/app/services/achievements/achievement_checkers/level_master_checker.py` - Lines 39-41, 113, 119
- `backend/app/services/achievements/achievement_checkers/session_achievements_checker.py` - Lines 102, 115, 196, 209
- `backend/app/services/achievements/achievement_checkers/level_accuracy_checker.py` - Line 62
- `backend/app/services/achievements/achievement_checkers/level_correct_count_checker.py` - Line 66
- `backend/app/services/achievements/achievement_checkers/operation_count_checker.py` - Line 68
- `backend/migrate.py` - Lines 255, 304, 322, 480-487 (indexes)

### Question.level_tag
**Location**: `backend/app/models.py:68`

```python
level_tag = db.Column(db.String(32), nullable=True, index=True)
```

**Current Usage**:
- Set when creating questions (e.g., `level_tag="1"`)
- Has database index

**Action Required**:
- Remove `level_tag` field OR make it display-only
- Remove database index
- Stop setting `level_tag` when creating questions

**Files to Update**:
- `backend/app/services/question_service.py` - Line 693
- `backend/migrate.py` - Index removal

---

## Service Layer

### SessionEngineService.generate_session()
**Location**: `backend/app/services/session_engine_service.py`

**Issues**:
1. **Line 24**: Accepts `level: int | None = None` parameter
2. **Line 36**: Docstring says "Optional level override (defaults to user's level)"
3. **Line 50**: Sets `session_level = level if level is not None else (user.level if concept_id is None else None)`
4. **Line 72-73**: Updates `session_level` from extracted level
5. **Line 87**: Passes `level=session_level` to `SessionFactory`
6. **Line 91-92**: Calculates `response_level` using legacy level extraction
7. **Line 97**: Returns `"level": response_level` in response

**Action Required**:
- Remove `level` parameter from `generate_session()`
- Stop setting `session.level` (make it None or remove the assignment)
- Stop returning `level` in response (or make it display-only from XP)
- Remove all level extraction logic

### PracticeService.get_questions_for_level()
**Location**: `backend/app/services/practice_service.py:119-133`

**Issues**:
- Entire method filters questions by `Question.required_level <= level`
- This is a legacy method that should be removed
- Tests depend on this method

**Action Required**:
- **DELETE THIS METHOD ENTIRELY**
- Replace all callers with concept-based question selection
- Update or remove tests that use this method

**Files to Update**:
- `backend/app/services/practice_service.py` - Delete method
- `backend/tests/test_practice_service.py` - Remove or update tests (Lines 196-273)

### QuestionService methods using level
**Location**: `backend/app/services/question_service.py`

**Issues**:
1. **Line 137**: `generate_question()` accepts `level: int` parameter
2. **Line 194**: `generate_question_with_constraints()` accepts `level: int` parameter
3. **Line 328**: `_normalize_constraints()` accepts `level: int` parameter
4. **Line 348**: `generate_operands_with_constraints()` accepts `level: int` parameter and converts to concept_id (Line 370)
5. **Line 516**: `generate_question_with_layout()` accepts `level: int` parameter
6. **Line 524**: Converts level to concept_id for layout lookup
7. **Line 589**: `generate_question_with_speed()` accepts `level: int` parameter
8. **Line 603**: Converts level to concept_id for config lookup
9. **Line 678-693**: Sets `required_level = level` when creating Question
10. **Line 735**: Uses placeholder level = 1

**Action Required**:
- Replace all `level` parameters with `concept_id: str`
- Remove all level-to-concept_id conversions (callers should pass concept_id directly)
- Stop setting `Question.required_level` when creating questions
- Update all callers to pass `concept_id` instead of `level`

### SessionResumeService.find_resumable_session()
**Location**: `backend/app/services/session_resume_service.py`

**Issues**:
1. **Line 80-81**: Filters by `incomplete_session.level == session_level`
2. **Line 117-119**: Uses `incomplete_session.level` or `user.level` as fallback

**Action Required**:
- Remove level filtering from session resuming
- Filter only by `concept_id`, `mode`, and `user_id`
- Remove `session_level` parameter

### SessionCompletionService
**Location**: `backend/app/services/session_completion_service.py`

**Issues**:
1. **Line 159**: Uses `prev_level = int(user.level or 1)`
2. **Line 166**: Sets `user.level = new_level` (should use XP instead)
3. **Line 209**: Returns `"level": session.level` in response

**Action Required**:
- Remove level setting logic (level should be calculated from XP)
- Level up should be automatic based on XP (already handled by XPService)
- Stop returning `session.level` in response

---

## Achievement System

### Achievement Checkers Using Level

#### LevelMasterChecker
**Location**: `backend/app/services/achievements/achievement_checkers/level_master_checker.py`

**Issues**:
1. **Lines 39-41**: Queries `Question.required_level` to get all levels
2. **Line 95**: Accepts `level_filter: int | None = None` parameter
3. **Line 113**: Uses `level_filter` to create legacy concept_id
4. **Line 119**: Filters by `Question.required_level == level_filter`
5. **Line 232**: Accepts `level_filter` parameter
6. **Line 252**: Passes `level_filter` to other methods

**Action Required**:
- Remove all `level_filter` parameters
- Filter by `concept_id` from session metadata instead
- Remove queries that use `Question.required_level`

#### SessionAchievementsChecker
**Location**: `backend/app/services/achievements/achievement_checkers/session_achievements_checker.py`

**Issues**:
1. **Line 67**: Calls `_check_level_mastery()` with level from requirements
2. **Line 83**: Extracts `level = requirements.get("level")`
3. **Line 102**: Filters by `Question.required_level == level`
4. **Line 115**: Filters by `Question.required_level == level`
5. **Line 148**: Extracts `level = requirements.get("level")`
6. **Line 185**: Extracts `level = requirements.get("level")`
7. **Line 196**: Filters by `Question.required_level == level`
8. **Line 209**: Filters by `Question.required_level == level`

**Action Required**:
- Remove all level-based filtering
- Use `concept_id` from session or achievement metadata instead
- Remove `level` from achievement requirements

#### LevelAccuracyChecker
**Location**: `backend/app/services/achievements/achievement_checkers/level_accuracy_checker.py`

**Issues**:
1. **Line 53**: Extracts `level = requirements.get("level")`
2. **Line 62**: Filters by `Question.required_level == level`

**Action Required**:
- Remove level filtering
- Use concept_id instead

#### LevelCorrectCountChecker
**Location**: `backend/app/services/achievements/achievement_checkers/level_correct_count_checker.py`

**Issues**:
1. **Line 55**: Extracts `level = requirements.get("level")`
2. **Line 66**: Filters by `Question.required_level == level`

**Action Required**:
- Remove level filtering
- Use concept_id instead

#### OperationCountChecker
**Location**: `backend/app/services/achievements/achievement_checkers/operation_count_checker.py`

**Issues**:
1. **Line 57**: Extracts `level = requirements.get("level")`
2. **Line 68**: Filters by `Question.required_level == level`

**Action Required**:
- Remove level filtering
- Use concept_id instead

#### AccuracyAceChecker
**Location**: `backend/app/services/achievements/achievement_checkers/accuracy_ace_checker.py`

**Issues**:
1. **Line 99**: Checks `if not concept_id and session.level:`
2. **Line 101**: Creates concept_id from `session.level`

**Action Required**:
- Remove fallback to `session.level`
- Require `concept_id` to be set (should always be set for concept-based system)

#### LightningFastChecker
**Location**: `backend/app/services/achievements/achievement_checkers/lightning_fast_checker.py`

**Issues**:
1. **Line 59**: Checks `if not concept_id and session.level:`
2. **Line 61**: Creates concept_id from `session.level`

**Action Required**:
- Remove fallback to `session.level`
- Require `concept_id` to be set

#### GenericAccuracyChecker
**Location**: `backend/app/services/achievements/achievement_checkers/generic_accuracy_checker.py`

**Issues**:
1. **Line 34**: Checks `if not session.completed_at or not session.level:`
2. **Line 59**: Returns `"level": session.level` in metadata

**Action Required**:
- Remove `session.level` requirement check
- Remove level from metadata (use concept_id instead)

### AchievementQueryService
**Location**: `backend/app/services/achievements/achievement_queries/achievement_query_service.py`

**Issues**:
1. **Line 232**: `_apply_session_filters()` accepts `level: int | None = None`
2. **Line 240**: Docstring mentions "level filter (session level must match)"
3. **Line 257**: Filters by `session.level != level`
4. **Line 284**: `get_achievements_by_category()` accepts `level: int | None = None`
5. **Line 294**: Docstring mentions "level filter"
6. **Line 307**: Checks `has_session_filters = level is not None ...`
7. **Line 318-319**: Applies session-level filters
8. **Line 334**: `get_achievements_by_code()` accepts `level: int | None = None`
9. **Line 345**: Docstring mentions "level filter"
10. **Line 375-376**: Applies session-level filters
11. **Line 398**: `count_achievements_by_code()` accepts `level: int | None = None`
12. **Line 411**: Docstring mentions "level filter (session level must match)"
13. **Line 429**: Passes `level=level` to query
14. **Line 439**: Passes `level=level` to query

**Action Required**:
- Remove all `level` parameters from query methods
- Remove level filtering logic
- Filter by `concept_id` from achievement metadata instead

---

## API Routes

### /api/practice/sessions/start
**Location**: `backend/app/routes/practice.py`

**Issues**:
1. **Line 98**: Returns `"level": incomplete_session.level` in response

**Action Required**:
- Remove level from response OR calculate from XP for display

### /api/users endpoints
**Location**: `backend/app/routes/users.py`

**Issues**:
1. **Line 56**: Returns `"level": user.level` in user response
2. **Line 175**: Sets `user.level = 1` when creating user
3. **Line 225**: Sets `user.level = level` in PUT endpoint (should be removed)
4. **Line 312**: Returns `"level": user.level` in response

**Action Required**:
- Level should be calculated from XP, not stored
- Remove level setting endpoints
- Return level calculated from XP for display only

### /api/common/user-info
**Location**: `backend/app/routes/common.py`

**Issues**:
1. **Line 106**: Returns `"level": user.level` in response

**Action Required**:
- Calculate level from XP instead of returning stored level

---

## Test Files

### Test Helpers
**Location**: `backend/tests/helpers/data_helpers.py`

**Issues**:
1. **Line 72-87**: `set_user_level_directly()` function sets user.level
2. **Line 94**: `create_test_session_with_responses()` accepts `level: int = 1` parameter
3. **Line 119**: Sets `session.level = level`
4. **Line 172-222**: `create_test_questions()` accepts `level: int` parameter
5. **Line 215**: Sets `required_level=level` when creating questions

**Action Required**:
- Remove `level` parameters from test helpers
- Use `concept_id` instead
- Stop setting `required_level` on test questions

**Location**: `backend/tests/helpers/test_data_helpers.py`

**Issues**:
- Similar issues as `data_helpers.py`

**Action Required**:
- Same as above

### Test Files Using Level
**Files to Update**:
- `backend/tests/test_practice_service.py` - Lines 29, 47, 66, 72, 82, 105, 136, 145, 159, 161, 172, 196-273, 420, 428, 462, 559, 663, 671, 770, 790, 808, 831, 849
- `backend/tests/test_user_service.py` - Lines 29, 48, 137, 138, 152, 159
- `backend/tests/test_level_master_achievements.py` - Line 399
- `backend/tests/test_lightning_fast_achievements.py` - Lines 278-279, 331
- `backend/tests/test_achievement_query_service.py` - Lines 300-327
- `backend/tests/test_session_resuming_edge_cases.py` - Line 58
- `backend/tests/test_session_resuming_bug_reproduction.py` - Line 48
- `backend/tests/test_generic_achievements.py` - Line 52
- `backend/tests/conftest.py` - Line 85
- `backend/tests/test_analytics_service.py` - Lines 47, 277, 285
- `backend/tests/test_achievement_orchestrator.py` - Line 47

**Action Required**:
- Update all tests to use `concept_id` instead of `level`
- Remove tests that specifically test level-based functionality
- Update test assertions to not check for level requirements

---

## Frontend

### Level Requirements
**Location**: `frontend/src/features/students/data/levelRequirements.ts`

**Issues**:
- Type definition includes level requirements
- May still be used for concept unlock requirements

**Action Required**:
- Verify this is only used for concept unlock requirements (not level progression)
- If used for level progression, remove it

### Level Display
**Location**: `frontend/src/features/students/utils/progressMapping/index.ts`

**Issues**:
1. **Line 11**: `level: number` in type
2. **Line 14**: `level: number` in type
3. **Line 18**: `xp_into_level: number`
4. **Line 19**: `xp_to_next_level: number | null`
5. **Line 32**: `_levelRequirementsCache` (deprecated)
6. **Line 75-76**: Comments about level requirements removed
7. **Line 83**: `level: user.level`

**Action Required**:
- Level should be calculated from XP (already done via XPService)
- Keep level in types for display purposes only
- Remove any level requirement logic

### Concept Tree View
**Location**: `frontend/src/features/students/components/journey/ConceptTreeView.tsx`

**Issues**:
1. **Line 49**: Groups nodes by level
2. **Line 82**: Sorts nodes within level
3. **Line 193**: Iterates over levels
4. **Line 226**: `level: n.level`
5. **Line 235-236**: Calculates maxLevel for layout

**Action Required**:
- Verify this is for visual layout only (not requirements)
- If it's for requirements, change to concept-based grouping

---

## Legacy Mappings

### legacy_mappings.py
**Location**: `backend/app/utils/legacy_mappings.py`

**Current State**: Legacy mapping functions that convert between level and concept_id

**Action Required**:
- Remove all usages of these functions
- Delete file entirely - no longer needed

**Functions to Remove**:
- `concept_id_from_legacy_level()`
- `extract_legacy_level_from_concept_id()`

**Files Using These**:
- `backend/app/services/session_engine_service.py` - Line 13, 91
- `backend/app/services/question_generation_service.py` - Line 40

---

## Database Migrations

### Indexes to Remove
**Location**: `backend/migrate.py`

**Issues**:
1. **Line 322**: `CREATE INDEX ix_questions_required_level ON questions(required_level)`
2. **Lines 480-487**: Composite index `ix_questions_operation_level ON questions(operation, required_level)`
3. Index on `level_tag` (if exists)

**Action Required**:
- Create migration to drop these indexes
- Drop indexes after removing code that uses them

### Schema Changes
**Action Required**:
- Remove `PracticeSession.level` column entirely (already nullable, but remove it)
- Remove `Question.required_level` column entirely
- Remove `Question.level_tag` column entirely
- Create database migration to drop these columns

---

## Summary Checklist

### Phase 1: Remove Level Requirements
- [x] Remove `level` parameter from `SessionEngineService.generate_session()`
- [x] Remove `get_questions_for_level()` method from `PracticeService`
- [x] Remove all `level` parameters from `QuestionService` methods
- [x] Replace level parameters with `concept_id` in all question generation
- [x] Remove level filtering from `SessionResumeService`
- [x] Remove level setting from `SessionCompletionService` (use XP instead)

### Phase 2: Remove Level from Achievement System
- [x] Rename achievement codes: "level-master" → "math-master" and "level-grandmaster" → "math-grandmaster"
- [x] Remove `level_filter` from `LevelMasterChecker`
- [x] Remove level filtering from `SessionAchievementsChecker`
- [x] Remove level filtering from `LevelAccuracyChecker`
- [x] Remove level filtering from `LevelCorrectCountChecker`
- [x] Remove level filtering from `OperationCountChecker`
- [x] Remove `session.level` fallback from `AccuracyAceChecker`
- [x] Remove `session.level` fallback from `LightningFastChecker`
- [x] Remove `session.level` requirement from `GenericAccuracyChecker`
- [x] Remove `level` parameters from `AchievementQueryService` methods

### Phase 3: Remove Level from API
- [ ] Remove level from practice session responses
- [ ] Remove level setting endpoints from user routes
- [ ] Calculate level from XP in all user responses
- [ ] Remove level from achievement query parameters

### Phase 4: Update Tests
- [ ] Update all test helpers to use `concept_id` instead of `level`
- [ ] Remove level-based tests
- [ ] Update test assertions to not check level requirements
- [ ] Remove `get_questions_for_level()` tests

### Phase 5: Database Cleanup
- [ ] Drop `ix_questions_required_level` index
- [ ] Drop `ix_questions_operation_level` composite index
- [ ] Remove `Question.required_level` column entirely
- [ ] Remove `Question.level_tag` column entirely
- [ ] Remove `PracticeSession.level` column entirely

### Phase 6: Remove Legacy Code
- [ ] Remove `legacy_mappings.py` file
- [ ] Remove all imports of legacy mapping functions
- [ ] Clean up comments mentioning legacy level system

### Phase 7: Frontend Verification
- [ ] Verify level is only used for display (calculated from XP)
- [ ] Verify no level requirements in frontend
- [ ] Update concept tree view if it uses level for requirements

---

## Notes

1. **Level Calculation**: Level should ALWAYS be calculated from XP using `XPService.level_for_total_xp(user.total_xp)`. Never store or require a specific level.

2. **Concept-Based Everything**: All logic should use `concept_id`. If you need to filter by "level", you should be filtering by `concept_id` instead.

3. **Session Level**: `PracticeSession.level` should be removed entirely. All new sessions should have `concept_id` set, and `level` should not exist.

4. **Question Required Level**: `Question.required_level` should not be used for filtering. Questions are selected by `concept_id`, not level.

5. **Achievement Metadata**: Achievements should use `concept_id` in metadata, not level. The achievement names "level-master" and "level-grandmaster" are misleading - they should be renamed to "math-master" and "math-grandmaster" to reflect that they are concept-based, not level-based.

6. **Testing**: After removing level requirements, verify that:
   - Users can practice any unlocked concept regardless of level
   - Achievements are awarded based on concept_id, not level
   - Level up happens automatically when XP threshold is reached
   - No functionality is gated by level

---

## Files Requiring Changes (Summary)

### Backend Services (High Priority)
- `backend/app/services/session_engine_service.py`
- `backend/app/services/practice_service.py` (delete `get_questions_for_level`)
- `backend/app/services/question_service.py`
- `backend/app/services/session_resume_service.py`
- `backend/app/services/session_completion_service.py`
- `backend/app/services/achievements/achievement_checkers/level_master_checker.py`
- `backend/app/services/achievements/achievement_checkers/session_achievements_checker.py`
- `backend/app/services/achievements/achievement_checkers/level_accuracy_checker.py`
- `backend/app/services/achievements/achievement_checkers/level_correct_count_checker.py`
- `backend/app/services/achievements/achievement_checkers/operation_count_checker.py`
- `backend/app/services/achievements/achievement_checkers/accuracy_ace_checker.py`
- `backend/app/services/achievements/achievement_checkers/lightning_fast_checker.py`
- `backend/app/services/achievements/achievement_checkers/generic_accuracy_checker.py`
- `backend/app/services/achievements/achievement_queries/achievement_query_service.py`

### Backend Routes
- `backend/app/routes/practice.py`
- `backend/app/routes/users.py`
- `backend/app/routes/common.py`

### Backend Models
- `backend/app/models.py` (make fields nullable or remove)

### Backend Tests
- All test files listed above
- `backend/tests/helpers/data_helpers.py`
- `backend/tests/helpers/test_data_helpers.py`

### Backend Utils
- `backend/app/utils/legacy_mappings.py` (delete entirely)

### Database
- `backend/migrate.py` (drop indexes)

### Frontend (Verify Only)
- `frontend/src/features/students/data/levelRequirements.ts`
- `frontend/src/features/students/utils/progressMapping/index.ts`
- `frontend/src/features/students/components/journey/ConceptTreeView.tsx`

---

**END OF DOCUMENT**
