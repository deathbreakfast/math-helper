# Remove Legacy Level System - Fourth Attempt

**Goal**: Completely remove all remaining references to `level`, `required_level`, level requirements, and the old leveling system from test fixtures, helper functions, API endpoints, and frontend code. Fix all test failures related to level/required_level parameters.

## Current State

After three attempts to remove the legacy level system, there are still many references causing test failures:
- **Backend**: 143 failed tests, 77 errors - failures related to level/required_level parameters in test fixtures
- **Frontend**: 4 failed tests - failures related to level requirements mapping

The remaining issues are primarily in:
1. Test fixtures using `level` and `required_level` parameters
2. Test helper functions accepting `level` parameters
3. API endpoints for level requirements
4. Frontend level requirement mapping code
5. Distribution test helpers using level concepts

---

## Test Fixtures

### conftest.py
**Location**: `backend/tests/conftest.py`

**Issues**:
1. **Line 31**: `user = User(..., level=1)` - Setting user.level in test_user fixture
2. **Line 43**: `def _create_user_with_achievements(..., level: int = 1)` - level parameter
3. **Line 45**: `user = User(..., level=level)` - Setting user.level
4. **Line 85**: `required_level=1` - Setting required_level in test_question fixture
5. **Line 105**: `level=1` - Setting session.level in test_session fixture

**Action Required**:
- Remove `level=1` from User creation (level is calculated from XP)
- Remove `level` parameter from `_create_user_with_achievements`
- Remove `required_level=1` from Question creation (field doesn't exist)
- Remove `level=1` from PracticeSession creation (field doesn't exist)
- Update all test files that use these fixtures

---

## Test Helper Functions

### data_helpers.py
**Location**: `backend/tests/helpers/data_helpers.py`

**Issues**:
1. **Line 197-202**: `create_test_questions(..., level: Optional[int] = None, ...)` - level parameter still exists
2. **Line 207-208**: Docstring mentions "DEPRECATED - Legacy level parameter"
3. **Line 215-222**: Logic maps level to concept_id if provided
4. **Line 94**: `create_test_session_with_responses(..., level: Optional[int] = None, ...)` - level parameter
5. **Line 133**: Docstring mentions "DEPRECATED - Session level"
6. **Line 144**: `level=None` - Explicitly setting level to None (should just not set it)

**Action Required**:
- Remove `level` parameter from `create_test_questions()` entirely
- Remove level-to-concept_id mapping logic
- Remove `level` parameter from `create_test_session_with_responses()` entirely
- Remove level=None assignment (just don't set the field)
- Update all callers to use `concept_id` instead of `level`

**Files Using These**:
- All test files that call `create_test_questions(..., level=...)`
- All test files that call `create_test_session_with_responses(..., level=...)`

### test_data_helpers.py
**Location**: `backend/tests/helpers/test_data_helpers.py`

**Issues**:
- Same issues as `data_helpers.py` (duplicate file?)

**Action Required**:
- Same as `data_helpers.py`

### distribution_test_helpers.py
**Location**: `backend/tests/helpers/distribution_test_helpers.py`

**Issues**:
1. **Line 27**: `self.user_level = test_user.level` - Storing user level
2. **Line 29**: `self.expected_levels = []` - Expected levels list
3. **Line 45-55**: `with_user_level(self, level: int)` - Method to set user level
4. **Line 57-67**: `expecting_levels(self, levels: list[int])` - Method for expected levels
5. **Line 154-175**: `_extract_level()` - Method to extract level from questions
6. **Line 178-182**: `verify_level_distribution()` - Function to verify level distribution

**Action Required**:
- Remove `user_level` from DistributionTestScenario
- Remove `expected_levels` from DistributionTestScenario
- Remove `with_user_level()` method
- Remove `expecting_levels()` method
- Remove `_extract_level()` method (or update to extract from concept_id)
- Remove or update `verify_level_distribution()` to use concept_id
- Update distribution tests to use concept_id instead of level

---

## Test Files with level/required_level Usage

### Direct User.level Assignment
**Files**:
- `backend/tests/test_user_service.py` - Lines 29, 137, 138, 152, 159
- `backend/tests/test_accuracy_ace_checker.py` - Lines 29, 68, 86, 110, 133, 151, 170, 205, 227, 248
- `backend/tests/test_achievement_service_session_tracking.py` - Lines 29, 42
- `backend/tests/test_accuracy_ace_achievements.py` - Line 34
- `backend/tests/test_lightning_fast_achievements.py` - Lines 34, 290
- `backend/tests/test_achievements_awarding.py` - Lines 35, 88, 151, 541, 562, 640
- `backend/tests/test_level_specific_checkers.py` - Line 33
- `backend/tests/test_champion_validator.py` - Lines 25, 43, 180, 223, 266
- `backend/tests/test_session_resuming_bug_reproduction.py` - Line 29
- `backend/tests/test_achievement_constraints.py` - Lines 39, 358, 364, 427, 476
- `backend/tests/test_analytics_service.py` - Lines 30, 47, 647, 648, 815, 816
- `backend/tests/test_achievement_utils.py` - Lines 37, 126, 205, 347
- `backend/tests/test_api_protection.py` - Lines 36, 61, 90, 116
- `backend/tests/test_question_master_achievements.py` - Line 34
- `backend/tests/test_server_record_service.py` - Lines 29, 44
- `backend/tests/test_session_engine_service.py` - Line 22
- `backend/tests/test_week_warrior_achievements.py` - Line 33
- `backend/tests/test_session_resuming_edge_cases.py` - Lines 29, 39
- `backend/tests/test_complete_session_xp_breakdown.py` - Lines 31, 105, 266
- `backend/tests/test_level_master_achievements.py` - Lines 35, 224, 395, 414, 466, 516, 536
- `backend/tests/test_achievement_orchestrator.py` - Lines 30, 47, 393, 394
- `backend/tests/test_achievement_query_service.py` - Lines 26, 38
- `backend/tests/test_master_times_division_achievements.py` - Line 38
- `backend/tests/test_achievement_model.py` - Lines 28, 43
- `backend/tests/test_milestone_checker.py` - Lines 25, 165
- `backend/tests/test_so_wow_achievements.py` - Line 35
- `backend/tests/test_practice_service.py` - Lines 29, 47, 137, 346
- `backend/tests/test_perfect_streak_achievements.py` - Line 34
- `backend/tests/test_generic_achievements.py` - Lines 51, 239

**Action Required**:
- Remove `level=1` (or other values) from all `User(...)` constructor calls
- Level should be calculated from XP, not set directly
- If tests need a specific level, set `experience` to the required XP value instead

### required_level in Question Creation
**Files**:
- `backend/tests/conftest.py` - Line 85
- `backend/tests/test_session_resuming_bug_reproduction.py` - Line 48
- `backend/tests/test_analytics_service.py` - Line 47
- `backend/tests/test_achievement_orchestrator.py` - Line 47
- `backend/tests/test_session_resuming_edge_cases.py` - Line 58
- `backend/tests/test_practice_service.py` - Lines 47, 137, 346

**Action Required**:
- Remove `required_level=...` from all `Question(...)` constructor calls
- The `required_level` field no longer exists in the Question model

### level in PracticeSession Creation
**Files**:
- `backend/tests/conftest.py` - Line 105
- `backend/tests/test_accuracy_ace_checker.py` - Lines 68, 86, 110, 133, 151, 170, 205, 227, 248
- `backend/tests/test_achievement_service_session_tracking.py` - Line 42
- `backend/tests/test_achievements_awarding.py` - Lines 88, 151, 541, 562, 640
- `backend/tests/test_complete_session_xp_breakdown.py` - Lines 105, 266
- `backend/tests/test_level_master_achievements.py` - Lines 224, 395, 414, 466, 516, 536

**Action Required**:
- Remove `level=...` from all `PracticeSession(...)` constructor calls
- The `level` field no longer exists in the PracticeSession model
- Use `concept_id` instead

### level Parameter in Helper Function Calls
**Files**:
- `backend/tests/test_lightning_fast_achievements.py` - Line 290: `create_test_questions(..., level=1)`
- `backend/tests/test_achievements_awarding.py` - Lines 88, 151, 541, 562, 640: `create_test_session_with_responses(..., level=1)`
- `backend/tests/test_level_master_achievements.py` - Lines 224, 395, 414, 466, 516, 536: `create_test_session_with_responses(..., level=1)`

**Action Required**:
- Update all calls to `create_test_questions()` to use `concept_id` instead of `level`
- Update all calls to `create_test_session_with_responses()` to use `concept_id` instead of `level`
- Remove `level=...` parameter from all calls

---

## API Endpoints

### /api/levels/requirements
**Location**: **NOT FOUND** - Endpoint may have already been removed, but test still exists

**Issues**:
- Test file `backend/tests/test_levels_requirements_endpoint.py` tests `/api/levels/requirements` endpoint
- Test expects endpoint at line 55: `resp = client.get(f"/api/levels/requirements?levels=2&user_id={user.id}")`
- Endpoint is not found in any route files (searched routes/, no levels.py found)
- Endpoint may have been removed but test was not deleted

**Action Required**:
- **DELETE** `backend/tests/test_levels_requirements_endpoint.py` (endpoint doesn't exist, test is invalid)
- Verify frontend doesn't call this endpoint (should use `/api/concepts/requirements` instead)
- If endpoint exists elsewhere, find and delete it

**Files to Check**:
- `backend/tests/test_levels_requirements_endpoint.py` - DELETE (tests non-existent endpoint)
- Frontend code - Search for `/api/levels/requirements` calls

---

## Frontend Level Requirements

### levelRequirementConverters
**Location**: `frontend/src/features/students/utils/progressMapping/levelRequirementConverters.ts`

**Issues**:
- Still converts backend requirements to LevelRequirement format
- Uses level/nextLevel parameters (lines 33-34)
- Creates LevelRequirement with level-based locking (line 129)

**Action Required**:
- This file is used for concept unlock requirements (repurposed)
- Verify it's not actually creating level requirements
- If it is, remove level-based logic entirely
- Ensure it only handles concept unlock requirements

### levelRequirementConverters.test.ts
**Location**: `frontend/src/features/students/utils/progressMapping/levelRequirementConverters.test.ts`

**Issues**:
- Tests level requirement conversion
- May test level-based locking logic

**Action Required**:
- Update tests to not test level-based locking
- Remove tests for level requirements if they exist
- Keep tests for concept unlock requirements only

### progressMapping/index.test.ts
**Location**: `frontend/src/features/students/utils/progressMapping/index.test.ts`

**Issues**:
- Lines 154-266: Tests for level requirements
- Tests level requirements cache building
- Tests level-based locking

**Action Required**:
- Remove all level requirement tests
- Remove level requirements cache tests
- Update tests to not reference level requirements

### LevelRequirementCard Component
**Location**: `frontend/src/features/students/components/LevelRequirementCard.tsx`

**Issues**:
- Component still exists and displays level requirements
- Uses LevelRequirement type with level/nextLevel

**Action Required**:
- Verify if this component is actually used
- If not used: **DELETE THIS FILE**
- If used: Update to handle concept unlock requirements only (not level requirements)

---

## Summary Checklist

### Phase 1: Fix Test Fixtures
- [x] Remove `level=1` from `conftest.py` test_user fixture
- [x] Remove `level` parameter from `_create_user_with_achievements` in conftest.py
- [x] Remove `required_level=1` from `conftest.py` test_question fixture
- [x] Remove `level=1` from `conftest.py` test_session fixture

### Phase 2: Fix Test Helper Functions
- [x] Remove `level` parameter from `create_test_questions()` in data_helpers.py
- [x] Remove level-to-concept_id mapping from `create_test_questions()`
- [x] Remove `level` parameter from `create_test_session_with_responses()` in data_helpers.py
- [x] Remove `level=None` assignment from `create_test_session_with_responses()`
- [x] Update test_data_helpers.py (same changes)
- [x] Remove level-related methods from distribution_test_helpers.py
- [x] Update distribution tests to use concept_id

### Phase 3: Fix Test Files - User.level
- [x] Remove `level=...` from all User() constructor calls in test files
- [x] Replace with `experience=...` if specific level needed (calculate XP from level)
- [x] Update ~30+ test files

### Phase 4: Fix Test Files - Question.required_level
- [x] Remove `required_level=...` from all Question() constructor calls
- [x] Update ~7 test files

### Phase 5: Fix Test Files - PracticeSession.level
- [x] Remove `level=...` from all PracticeSession() constructor calls
- [x] Add `concept_id=...` instead
- [x] Update ~10+ test files

### Phase 6: Fix Test Files - Helper Function Calls
- [x] Update all `create_test_questions(..., level=...)` calls to use `concept_id`
- [x] Update all `create_test_session_with_responses(..., level=...)` calls to use `concept_id`
- [x] Update ~5+ test files

### Phase 7: Remove Level Requirements API
- [x] Find and delete `/api/levels/requirements` endpoint (endpoint doesn't exist, only test existed)
- [x] Delete `backend/tests/test_levels_requirements_endpoint.py`
- [x] Remove endpoint registration (no endpoint to remove)

### Phase 8: Fix Frontend Level Requirements
- [x] Verify levelRequirementConverters is only for concept unlocks
- [x] Remove level-based locking logic if present (set isLocked: false)
- [x] Update levelRequirementConverters.test.ts (no changes needed - function still used for concept unlocks)
- [x] Remove level requirement tests from progressMapping/index.test.ts
- [x] Verify/delete LevelRequirementCard component (component exists but appears unused - no imports found)

---

## Files Requiring Changes (Summary)

### Backend Test Fixtures (High Priority)
- `backend/tests/conftest.py` - Remove level/required_level from fixtures

### Backend Test Helpers (High Priority)
- `backend/tests/helpers/data_helpers.py` - Remove level parameters
- `backend/tests/helpers/test_data_helpers.py` - Remove level parameters
- `backend/tests/helpers/distribution_test_helpers.py` - Remove level methods

### Backend Test Files (High Priority - ~50+ files)
- All test files with `User(..., level=...)` - Remove level parameter
- All test files with `Question(..., required_level=...)` - Remove required_level
- All test files with `PracticeSession(..., level=...)` - Remove level, add concept_id
- All test files calling helpers with `level=...` - Use concept_id instead

### Backend Routes
- Find and delete `/api/levels/requirements` endpoint
- Remove endpoint registration

### Backend Test Files for Deletion
- `backend/tests/test_levels_requirements_endpoint.py` - DELETE

### Frontend Test Files
- `frontend/src/features/students/utils/progressMapping/levelRequirementConverters.test.ts` - Update
- `frontend/src/features/students/utils/progressMapping/index.test.ts` - Remove level requirement tests

### Frontend Components
- `frontend/src/features/students/components/LevelRequirementCard.tsx` - Verify usage, delete if unused

---

## Notes

1. **User.level**: The `User.level` field still exists in the database model but should NOT be set directly. Level is calculated from XP. In tests, if a specific level is needed, calculate the required XP using `XPService.total_xp_for_level(level)` and set `experience` instead.

2. **Question.required_level**: This field was removed in Phase 5. All references to it in test fixtures and helper functions should be removed.

3. **PracticeSession.level**: This field was removed in Phase 5. All references to it should be removed. Use `concept_id` instead.

4. **Test Helpers**: The `level` parameter in test helpers is deprecated and should be removed entirely. All callers should use `concept_id` instead.

5. **Level Requirements API**: The `/api/levels/requirements` endpoint is legacy and should be completely removed. The frontend should use `/api/concepts/requirements` instead.

6. **Frontend Level Requirements**: The LevelRequirement type and related code should only be used for concept unlock requirements (repurposed), not for actual level progression requirements.

---

**END OF DOCUMENT**
