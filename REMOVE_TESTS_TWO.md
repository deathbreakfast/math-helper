# Remove Test/Quiz System - Second Attempt

**Goal**: Completely remove the test/quiz system from the codebase. Remove all references to tests, quizzes, tiered achievements based on test performance (B/A/S/SS/SSS), test definitions, test attempts, test sessions, and any related functionality.

## Current State

The codebase contains a legacy test/quiz system that allows users to take structured math assessments with fixed question counts, tiered performance ratings (B/A/S/SS/SSS), and achievement tracking. This system is separate from the practice session system and should be completely removed.

### Key Principles
1. **No Tests/Quizzes**: Remove all test definitions, test attempts, and test-related UI
2. **No Tiered Test Achievements**: Remove B/A/S/SS/SSS tier system for test performance
3. **Practice Only**: The application should only use practice sessions, not structured tests
4. **Remove Test Definitions**: All test type definitions and configurations should be removed
5. **Remove Test Attempts**: All test attempt tracking and storage should be removed

---

## Database Models

### Test Attempt Models
**Location**: Need to verify if test attempts are stored separately or use PracticeSession

**Current Usage**:
- Test attempts may be stored in a separate table or use PracticeSession with test_type metadata
- Test attempts track: test_type, tier (B/A/S/SS/SSS), accuracy, speed, question_count
- Test attempts are linked to users and may have detailed question responses

**Action Required**:
- Identify all database tables/columns related to test attempts
- Remove test attempt storage
- Remove test attempt queries and relationships
- Clean up any test-related data in existing tables

**Files to Check**:
- `backend/app/models.py` - Check for TestAttempt model or test-related fields
- `backend/migrate.py` - Check for test-related table creation/migrations
- Database schema - Verify if test attempts use PracticeSession or separate table

---

## Frontend Components

### TestCard Component
**Location**: `frontend/src/features/students/components/journey/TestCard.tsx`

**Issues**:
- Displays test cards with test information
- Shows unlock requirements, tier badges, attempt counts
- Handles test start/view actions

**Action Required**:
- **DELETE THIS FILE ENTIRELY**
- Remove all imports and usages of TestCard

**Files Using This**:
- Search for imports of `TestCard` in journey components
- Check `MathConceptsTab.tsx`, `OverviewTab.tsx`, or other journey components

### AttemptCard Component
**Location**: `frontend/src/features/students/components/journey/AttemptCard.tsx`

**Issues**:
- Displays test attempt results
- Shows tier badges (B/A/S/SS/SSS), accuracy, speed
- Displays question-by-question breakdown

**Action Required**:
- **DELETE THIS FILE ENTIRELY**
- Remove all imports and usages of AttemptCard

**Files Using This**:
- Search for imports of `AttemptCard` in journey components

### Test Definitions
**Location**: `frontend/src/lib/tests/testDefinitions.ts`

**Issues**:
- Defines all test types (addition-1digit, subtraction-2digit, etc.)
- Contains test tier requirements (B/A/S/SS/SSS)
- Maps test types to display names, question counts, constraints

**Action Required**:
- **DELETE THIS FILE ENTIRELY**
- Remove all imports of test definitions

**Files Using This**:
- `frontend/src/features/students/utils/testMapping/types.ts`
- `frontend/src/features/students/utils/testMapping/testConverters.ts`
- Any other files importing from `lib/tests/testDefinitions`

### Test Mapping Utilities
**Location**: `frontend/src/features/students/utils/testMapping/`

**Files in Directory**:
- `index.ts` - Maps backend test definitions to frontend format
- `types.ts` - TypeScript types for tests (BackendTestDefinition, FrontendTest, BackendTestAttempt, etc.)
- `testConverters.ts` - Converts test attempts, calculates tiers
- `tierUtils.ts` - Tier mapping utilities (B/A/S/SS/SSS to Bronze/Silver/Gold/etc.)
- `index.test.ts` - Tests for test mapping
- `testConverters.test.ts` - Tests for test converters
- `tierUtils.test.ts` - Tests for tier utilities

**Issues**:
- All files in this directory are test-related
- Handles test definition mapping, attempt conversion, tier calculation
- Maps old tier system (B/A/S/SS/SSS) to new tier system

**Action Required**:
- **DELETE ENTIRE DIRECTORY**: `frontend/src/features/students/utils/testMapping/`
- Remove all imports from this directory
- Update any files that reference test mapping utilities

**Files Using These**:
- `frontend/src/features/students/components/journey/TestCard.tsx`
- `frontend/src/features/students/components/journey/AttemptCard.tsx`
- Any journey components that display tests

---

## Backend Services

### Test-Related Services
**Location**: Need to identify test-specific services

**Current Usage**:
- Services may handle test session creation, test attempt storage, tier calculation
- Test services may be separate from practice services or integrated

**Action Required**:
- Identify all test-related service methods
- Remove test session creation logic
- Remove test attempt storage logic
- Remove tier calculation for tests
- Clean up test-related service methods

**Files to Check**:
- `backend/app/services/session_engine_service.py` - May have test session generation
- `backend/app/services/question_service.py` - May have test constraint handling
- Any test-specific service files

### Legacy Test Type Mapping
**Location**: `backend/app/config/legacy_test_type_to_level.py`

**Issues**:
- Maps test_type identifiers to concept levels
- Used for translating test_type metadata to concept_id
- Contains mapping for all test types (addition-1digit, subtraction-2digit, etc.)

**Action Required**:
- **DELETE THIS FILE ENTIRELY**
- Remove all imports and usages
- Remove test_type translation logic from routes/services

**Files Using This**:
- `backend/app/routes/users.py` - Line 245: Translates test_type to concept_id
- Any other files that import `legacy_test_type_to_level`

---

## Backend Routes

### Test Setup Endpoint
**Location**: `backend/app/routes/users.py`

**Issues**:
- Line 184: `@users_bp.post("/users/<int:user_id>/test-setup")`
- Line 243-255: Translates test_type to concept_id in metadata
- This endpoint is for E2E test setup, but contains test_type translation logic

**Action Required**:
- Remove test_type translation logic (lines 243-255)
- Keep endpoint if needed for E2E tests, but remove test_type handling
- Or remove endpoint entirely if not needed

### Test API Endpoints
**Location**: Need to identify test-specific API endpoints

**Current Usage**:
- Endpoints may exist for:
  - Getting test definitions
  - Starting test sessions
  - Submitting test attempts
  - Getting test results/attempts

**Action Required**:
- Identify all test-related API endpoints
- Remove test definition endpoints
- Remove test attempt endpoints
- Remove test result endpoints
- Update API documentation

**Files to Check**:
- `backend/app/routes/practice.py` - May have test session endpoints
- `backend/app/routes/achievements.py` - May have test achievement endpoints
- Any test-specific route files

---

## Frontend Hooks and Utilities

### Test-Related Hooks
**Location**: Need to identify test-specific hooks

**Current Usage**:
- Hooks may fetch test definitions, test attempts, test results
- Hooks may handle test session state

**Action Required**:
- Identify all test-related hooks
- Remove test data fetching hooks
- Remove test state management hooks
- Update components that use these hooks

**Files to Check**:
- `frontend/src/features/students/hooks/` - Check for test-related hooks
- `frontend/src/features/practice/hooks/` - Check for test session hooks

### Test Utilities
**Location**: `frontend/src/features/students/utils/achievementUtils.ts`

**Issues**:
- May contain tier mapping utilities (OLD_TIER_MAP)
- Maps old tier system (B/A/S/SS/SSS) to new tier system

**Action Required**:
- Remove old tier mapping if only used for tests
- Keep if used for other achievement types
- Verify usage before removing

---

## Backend Configuration

### Test Definitions Config
**Location**: Need to identify backend test definition storage

**Current Usage**:
- Backend may have test definitions in config files
- Test definitions may be in database or code

**Action Required**:
- Identify where test definitions are stored
- Remove test definition configs
- Remove test definition loading logic

**Files to Check**:
- `backend/app/config/` - Check for test definition files
- Database migrations - Check for test definition tables

### Test Tier Requirements
**Location**: `frontend/src/lib/tests/testDefinitions.ts` (already identified)

**Issues**:
- Defines tier requirements (B/A/S/SS/SSS) for tests
- Maps accuracy, speed, question count to tiers

**Action Required**:
- Remove tier requirement definitions
- Remove tier calculation logic

---

## E2E Tests

### Test Flow Tests
**Location**: `frontend/e2e/test-flow.spec.ts`

**Issues**:
- Tests the test/quiz flow
- Tests test session creation, question answering, submission
- Tests tier calculation and achievement awarding

**Action Required**:
- **DELETE THIS FILE ENTIRELY**
- Remove test flow from test coverage documentation

**Files to Update**:
- `frontend/e2e/TEST_COVERAGE.md` - Remove test flow coverage
- `frontend/e2e/FRAMEWORK_GUIDE.md` - Remove test flow references

### Test Helpers
**Location**: `frontend/e2e/helpers/test-helpers.ts`

**Issues**:
- May contain test session helpers
- Functions like `startTestSession`, `answerQuestionViaAPI` for tests

**Action Required**:
- Remove test-specific helper functions
- Keep practice session helpers if they exist separately

**Files to Check**:
- `frontend/e2e/helpers/api/test-setup-api.ts` - May have test setup functions

---

## Achievement System

### Test-Based Achievements
**Location**: Need to identify test-specific achievements

**Current Usage**:
- Achievements may be awarded based on test performance
- Test tier achievements (B/A/S/SS/SSS) may exist
- Test completion achievements may exist

**Action Required**:
- Identify all test-related achievements
- Remove test achievement definitions
- Remove test achievement checkers
- Remove test achievement awarding logic
- Clean up achievement configs

**Files to Check**:
- `backend/app/config/achievements/` - Check for test-specific achievements
- `backend/app/services/achievements/achievement_checkers/` - Check for test checkers
- Achievement config files - Check for test_type metadata filters

### Tier System
**Location**: `backend/app/utils/tier_utils.py` and `frontend/src/features/students/utils/testMapping/tierUtils.ts`

**Issues**:
- Tier utilities map old tier system (B/A/S/SS/SSS) to new tier system
- Used for test performance tiers
- May also be used for other achievement types

**Action Required**:
- Verify if tier utils are only used for tests
- If only for tests: **DELETE THESE FILES**
- If used elsewhere: Keep but remove test-specific logic
- Update any achievement types that use old tier system

**Files Using These**:
- `backend/app/services/achievement_xp_service.py` - Uses tier utils
- `backend/app/config/achievement_xp.py` - Uses tier utils
- Various achievement checkers - May use tier utils

---

## Documentation

### Test Coverage Documentation
**Location**: `frontend/e2e/TEST_COVERAGE.md`

**Issues**:
- Documents test flow coverage
- References test-related test IDs

**Action Required**:
- Remove test flow coverage section
- Remove test-related test IDs
- Update coverage tables

### Framework Guide
**Location**: `frontend/e2e/FRAMEWORK_GUIDE.md`

**Issues**:
- May contain test flow testing guidelines
- May reference test helpers

**Action Required**:
- Remove test flow sections
- Remove test helper references
- Update testing guidelines

### README Files
**Location**: Various README files

**Issues**:
- May mention test/quiz features
- May document test functionality

**Action Required**:
- Remove test/quiz mentions from READMEs
- Update feature documentation
- Update API documentation

---

## Summary Checklist

### Phase 1: Remove Frontend Test Components
- [x] Delete `frontend/src/features/students/components/journey/TestCard.tsx`
- [x] Delete `frontend/src/features/students/components/journey/AttemptCard.tsx`
- [x] Remove all imports and usages of TestCard and AttemptCard
- [x] Remove test cards from journey tabs/components

### Phase 2: Remove Test Definitions and Mapping
- [x] Delete `frontend/src/lib/tests/testDefinitions.ts`
- [x] Delete entire directory `frontend/src/features/students/utils/testMapping/`
- [x] Remove all imports of test definitions and mapping utilities
- [x] Update components that reference test types

### Phase 3: Remove Backend Test Services
- [x] Remove test session creation logic
- [x] Remove test attempt storage logic
- [x] Remove tier calculation for tests
- [x] Remove test-related service methods

### Phase 4: Remove Backend Test Routes
- [x] Remove test definition endpoints
- [x] Remove test attempt endpoints
- [x] Remove test result endpoints
- [x] Remove test_type translation logic from routes

### Phase 5: Remove Test Configuration
- [x] Delete `backend/app/config/legacy_test_type_to_level.py`
- [x] Remove test definition configs
- [x] Remove test tier requirements
- [x] Clean up test-related configs

### Phase 6: Remove Test Achievements
- [x] Identify and remove test-based achievements
- [x] Remove test achievement checkers
- [x] Remove test achievement awarding logic
- [x] Clean up achievement configs with test_type metadata

### Phase 7: Remove Tier System (if test-only)
- [x] Verify tier utils usage
- [x] Remove tier utils if only used for tests
- [x] Update achievement types if tier utils removed
- [x] Remove old tier mapping (B/A/S/SS/SSS)

### Phase 8: Remove E2E Tests
- [x] Delete `frontend/e2e/test-flow.spec.ts`
- [x] Remove test helpers from E2E framework
- [x] Update test coverage documentation
- [x] Update framework guide

### Phase 9: Clean Up Documentation
- [x] Remove test/quiz mentions from READMEs
- [x] Update feature documentation
- [x] Update API documentation
- [x] Remove test flow from coverage docs

### Phase 10: Database Cleanup
- [ ] Identify test attempt storage
- [ ] Remove test attempt tables/columns
- [ ] Create migration to drop test-related schema
- [ ] Clean up test-related data

---

## Files Requiring Changes (Summary)

### Frontend Components (High Priority)
- `frontend/src/features/students/components/journey/TestCard.tsx` - DELETE
- `frontend/src/features/students/components/journey/AttemptCard.tsx` - DELETE
- `frontend/src/lib/tests/testDefinitions.ts` - DELETE
- `frontend/src/features/students/utils/testMapping/` - DELETE ENTIRE DIRECTORY
- Journey components that use TestCard/AttemptCard - UPDATE

### Frontend Utilities
- `frontend/src/features/students/utils/achievementUtils.ts` - Remove old tier mapping if test-only
- Test-related hooks - IDENTIFY AND REMOVE

### Backend Services
- `backend/app/services/session_engine_service.py` - Remove test session logic
- `backend/app/services/question_service.py` - Remove test constraint handling
- Test-specific services - IDENTIFY AND REMOVE

### Backend Routes
- `backend/app/routes/users.py` - Remove test_type translation
- Test-specific routes - IDENTIFY AND REMOVE

### Backend Configuration
- `backend/app/config/legacy_test_type_to_level.py` - DELETE
- Test definition configs - IDENTIFY AND REMOVE
- Test achievement configs - IDENTIFY AND REMOVE

### Backend Utils
- `backend/app/utils/tier_utils.py` - Verify usage, remove if test-only
- `frontend/src/features/students/utils/testMapping/tierUtils.ts` - DELETE (in testMapping dir)

### E2E Tests
- `frontend/e2e/test-flow.spec.ts` - DELETE
- `frontend/e2e/helpers/test-helpers.ts` - Remove test helpers
- `frontend/e2e/TEST_COVERAGE.md` - Remove test coverage
- `frontend/e2e/FRAMEWORK_GUIDE.md` - Remove test references

### Database
- Test attempt models/tables - IDENTIFY AND REMOVE
- Test-related migrations - IDENTIFY AND REMOVE

---

## Notes

1. **Test vs Practice**: Tests are structured assessments with fixed question counts and tiered performance ratings. Practice sessions are flexible practice with variable question counts. Only practice sessions should remain.

2. **Tier System**: The old tier system (B/A/S/SS/SSS) was primarily used for test performance. The new tier system (Bronze/Silver/Gold/Platinum/Diamond/Master/etc.) is used for achievements. If tier utils are only used for tests, they should be removed entirely.

3. **Test Definitions**: Test definitions specify test types (addition-1digit, subtraction-2digit, etc.) with question counts, constraints, and tier requirements. All of this should be removed.

4. **Test Attempts**: Test attempts track user performance on tests, including tier achieved, accuracy, speed, and question-by-question results. All test attempt tracking should be removed.

5. **Achievements**: Some achievements may be awarded based on test performance. These should be identified and removed, or converted to practice-based achievements if appropriate.

6. **Legacy Mapping**: The `legacy_test_type_to_level.py` file translates test_type metadata to concept_id. This translation should be removed, and any remaining test_type references should be cleaned up.

---

**END OF DOCUMENT**
