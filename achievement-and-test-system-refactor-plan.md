# Achievement and Test System Refactor - Multi-Phase Plan

## Table of Contents
1. [Raw Notes](#raw-notes)
2. [Organized Goals and Objectives](#organized-goals-and-objectives)
3. [Design Requirements](#design-requirements)
4. [Implementation Phases](#implementation-phases)
5. [Work Division and Execution Order](#work-division-and-execution-order)

---

## Raw Notes

> **Note**: This section contains the exact, unedited notes from the user to preserve original intent.

```
When we implement this, did we remove all the old acheivements and them under level requirements?

Did you also add these new tests as level requirements to replace them?

Another thing, looking at the filters. Do they make sense? Why is there a rank filter, what does it do, is it what ranks you achieve on completed tests? What about status, when I select locked, I don't see anything below. Maybe we shouldn't make any of them hidden and display all tests there. Just have them disabled.

Also the level requirement for the tests, 1 digit addition w/ zeros is wrong. This concept isn't introduced yet. It should be introduced later. 1 digit addition w/ negative numbers is similar, it's introduced before the concept is introduced. I'm thinking the test shouldn't just have a level requirement (it can , I'm thinking 100% accuracy on a specific level n number of times. E.g. 1 Digit Addition requires the user to complete 5 level 1 practice session with 100% accuracy to unlock. These should be able to be tracked with acheivements. Achivements should be trackable to the session they were earned in. If they are not today this may require a data model change. This is also starting to sound like we have a lot of connections a graph db might make sense, maybe? Take note to create a plan on what should be explored, what could it improve about our codebase, maintainability, cost benifit analysis, and how we can be objective about it.

Also the level requirements for reaching level two is way too easy. That means you only have to awnser 8 questions based on the acheivement requirements. One of the original requirements of this product was for level requirements to require aquiring multiple quantities of the same achivements. So can we bump the number of "addition basics" required to advance to level 2, it should be qty 10. The achivevement list in the level card should link to the achievements tab and apply a name filter automatically. This means we should migrate the entire application to a router. This will also greatly simplify testing since we shouldn't need to have all of the navigation utilities to click to navigate. They can be replaced with navigating to components using URL routing and derive state from there.

We support UI features based on `?env=dev` in the url to reset character levels. Let's enhance this. For level requirements, this should display all level requirements for all levels. (Include tests for this)

Also, in the achievements, a lot look like we should have more. E.g. accuracy Ace is visiable in the UI but locked. There should be a bronze version of this. Which I think is just called addition basics. Since we should be tracking which sessions awarded which basics, thus should have a count. We should be able to make "Addition Basics" the bronze version of this and can elimiate a specific achievement to advance to the next level. There should be lots of cases of acheivements that can be replaced with these generics if we are tracking the session they are awarded at. Let's also take advantage of env=dev here and display all acheivements here.

Speaking of env=dev and all of the APIs used to set up test users. These should not be included unless we are running the server with an env variable. TESTING=true. (We should default this to true until product enters version 1)

I already mentioned something like this already, but here is another example. 1 Digit Addition w/ Negative Numbers - Rank A, 100% accuracy (under 30 questions), there are these for every type of math from B-SSS. We can greatly simplify all of these if we made the achievement itself generic and the level requirement or test requirement just checked the qty of acheivements earned at a specific level. Let's make sure we get all of these mapped out, new level and test requirements. Let's try to consolidate as many acheivement definitions as possible, but still provide the tiers. We can have seperate practice and test versions of acheivements. Let's see all the new acheivement list broken down by category and what the requirements are for each that way we know the expected product outcome.

Problems with the test modal, when you start a new test: 1, it doesn't ask for the pin to verify the user. 2, nothing loads. Should load the same interface as what we do to render practice. The UI flow should be exactly the same, but instead of labed as practice, it's labeled as test. Make sure we include all the details needed to acheive this and which tests need to be introduced. With the router we can probably make shallower tests.

I'm not sure if I mentioned this about tests yet, but the UI tests. If you look at acheivements, test flow, and leveling, they were completed recently and use APIs to set up test users. Which of the existing tests can be updated to take advantage of this? Can we create abstractions to help with alot of this, like common things we need to support, e.g. animations & waiting for components or pages to load, the new routing features we are introducing, data prep ahead of time, can we create like a framework, run before, the main test logic, and the cleanup or run after.  We may be able to create more, but shallower tests to have better coverage, what coverage do we have now based on all the flows, and what could we achive, could this help us better test multiple positive and negitive samples?

Oh, don't think I mentioned this, the progress bar in the level requirements should reflect the qty of each required acheivement. Sounds like requirements for levels and tests is similar, could they share some underlying infastructure.

Let's also have a project running to get a baseline for backend test coverage.

Milestone acheivements like "First Steps" and "First Victory" and "Century Club" still make sense, we shouldn't expect anymore than one of those. Let's come up with some new exciting milestones that could have some different tiers for power users or people who have used it a long time.

Not sure if I mentioned this but a query we can use to determine if a test was completed (as level requirements) is if they have an acheivement of a certin rank.

Can we consolidate ranks from metals etc to letters. Make sure we have the same number of tiers as the MAX between the two.

**UPDATE**: After review, we'll use a metal/prestige tier system instead:
Bronze > Silver > Gold > Platinum > Diamond > Master > Grandmaster > Legendary > Mythic > Divine > Champion

Champion tier is unique - requires same as Divine but must set a new server record (first place, no ties). Not all achievements qualify for Champion tier.
```

---

## Organized Goals and Objectives

### High-Level Goals
1. **Achievement System Refactoring**: Consolidate and simplify achievement definitions using generic, quantity-based achievements tracked per session
2. **Test Unlocking System**: Replace simple level requirements with achievement-based unlocking (e.g., "complete 5 level 1 sessions with 100% accuracy")
3. **Level Requirements Enhancement**: Increase difficulty and add quantity requirements (e.g., 10 "addition-basics" achievements for level 2)
4. **Application Routing**: Migrate to a proper router to simplify navigation and testing
5. **Test UI Flow**: Fix test modal to require PIN verification and load practice interface
6. **Testing Infrastructure**: Create testing framework abstractions and improve coverage
7. **Data Model Enhancement**: Track which sessions awarded which achievements
8. **Tier System Consolidation**: Unify all achievement tiers to a metal/prestige tier system (Bronze > Silver > Gold > Platinum > Diamond > Master > Grandmaster > Legendary > Mythic > Divine > Champion)

### Objectives

#### Objective 1: Achievement Data Model Enhancement
- **Goal**: Link achievements to the sessions that awarded them
- **Outcome**: Ability to query achievements by session, count achievements per level/type, support quantity-based requirements
- **Verification**: 
  - Database schema includes `session_id` in `Achievement` model
  - API can return session information for each achievement
  - Achievement queries can filter/count by session metadata

#### Objective 2: Generic Achievement System
- **Goal**: Replace specific achievement definitions with generic, tiered achievements based on quantity
- **Outcome**: Reduced achievement definitions, quantity-based unlocking for tests and levels
- **Verification**:
  - Achievement definitions reduced by 50%+
  - Test unlocking uses achievement quantity checks
  - Level requirements use achievement quantity (e.g., "10 addition-basics")

#### Objective 3: Test Unlocking Requirements
- **Goal**: Tests unlock based on achievement quantities (e.g., "5 level 1 sessions with 100% accuracy")
- **Outcome**: Tests unlock at appropriate times, aligned with concept introduction
- **Verification**:
  - Test definitions include achievement-based requirements
  - Tests are locked until requirements met
  - Test unlocking logic correctly evaluates achievement quantities

#### Objective 4: Level Requirements Enhancement
- **Goal**: Level 2 requires 10 "addition-basics" achievements (not just 1)
- **Outcome**: More challenging progression, quantity-based requirements throughout
- **Verification**:
  - Level 2 config requires quantity: 10
  - Progress bars show quantity progress (e.g., "7/10")
  - Achievement links navigate to achievements tab with filter

#### Objective 5: Application Router Migration
- **Goal**: Implement proper routing (React Router) for all pages/components
- **Outcome**: URL-based navigation, simplified testing, deep linking support
- **Verification**:
  - All pages accessible via URL routes
  - Navigation uses router, not manual clicks
  - Tests use URL navigation instead of click helpers
  - Achievement links use router navigation with filters

#### Objective 6: Test Modal and Flow Fixes
- **Goal**: Test modal requires PIN, loads practice interface correctly
- **Outcome**: Secure test access, consistent UI between practice and tests
- **Verification**:
  - PIN verification required before test start
  - Test interface loads same as practice (labeled "Test")
  - Test completion flows correctly

#### Objective 7: Tests Tab UI Improvements
- **Goal**: Show all tests (not hidden), disabled state for locked tests, fix filters
- **Outcome**: Better UX, all tests visible, clear lock states
- **Verification**:
  - All tests visible in tests tab
  - Locked tests shown but disabled
  - Filters work correctly (rank, status, search)
  - Tier filter shows best achieved tier per test (Bronze through Champion)

#### Objective 8: Dev/Test Mode Enhancements
- **Goal**: Enhanced dev mode features, protected test APIs
- **Outcome**: Better development experience, secure production deployment
- **Verification**:
  - `?env=dev` shows all achievements (including locked)
  - `?env=dev` shows all level requirements (for all levels)
  - Single `?env=dev` flag controls all UI dev features
  - Test setup APIs only available with `TESTING=true` env var (backend)
  - Default `TESTING=true` until v1.0

#### Objective 9: Testing Framework and Coverage
- **Goal**: Create testing abstractions, improve coverage, baseline backend tests
- **Outcome**: Easier test writing, better coverage, measurable improvement
- **Verification**:
  - Testing framework supports: animations, routing, data prep, cleanup
  - Coverage report shows current state
  - Backend test coverage baseline established
  - Existing tests migrated to use new patterns

#### Objective 10: Tier System Consolidation
- **Goal**: Unify all achievement tiers to metal/prestige tier system
- **Outcome**: Consistent, thrilling tier system across all achievements
- **Tier System**: Bronze > Silver > Gold > Platinum > Diamond > Master > Grandmaster > Legendary > Mythic > Divine > Champion
- **Champion Tier**: Special tier requiring same as Divine but must set a new server record (first place, no ties). Not all achievements qualify.
- **Verification**:
  - All achievements use metal/prestige tiers
  - Champion tier logic implemented for qualifying achievements
  - Server record tracking for Champion tier
  - Tier progression is clear and consistent

---

## Design Requirements

### Current State Analysis

#### Achievement System
- **Location**: `backend/app/config/achievements/`, `backend/app/models.py` (Achievement model)
- **Current Structure**: 
  - Achievement model: `id`, `user_id`, `code`, `title`, `description`, `icon`, `category`, `earned_at`
  - **Missing**: `session_id` field to track which session awarded the achievement
  - Achievement definitions in separate files by category (accuracy, test, milestone, etc.)
  - Level requirements in `backend/app/config/level_progression_config.py` reference achievement codes
- **Current Level 2 Requirement**: 
  ```python
  2: [{"achievement_code": "addition-basics", "order": 1}]
  ```
  - Only requires 1 achievement (too easy)

#### Test System
- **Location**: `backend/app/config/tests/test_definitions.py`, `frontend/src/features/students/components/journey/TestsTab.tsx`
- **Current Structure**:
  - Tests have `level_requirement` field
  - Tests can be locked/unlocked based on level
  - Test definitions include: `test_type`, `operation`, `level_requirement`, `question_count`, `constraints`
- **Issues**:
  - Tests like "1 digit addition w/ zeros" unlock too early (concept not introduced)
  - No achievement-based unlocking
  - Test modal doesn't require PIN
  - Test interface doesn't load correctly

#### Routing System
- **Location**: `frontend/src/App.tsx`, `frontend/src/utils/routing.ts`
- **Current Structure**:
  - Basic route detection using `window.location.pathname`
  - No proper router library (React Router)
  - Navigation uses `window.location.href` or manual clicks
- **Limitations**:
  - No deep linking to specific tabs/filters
  - Tests require click-based navigation helpers
  - No URL state management

#### Progress Tracking
- **Location**: `frontend/src/features/students/components/LevelRequirementCard.tsx`, `frontend/src/features/students/utils/progressMapping.ts`
- **Current Structure**:
  - Progress bars show `progress/maxProgress` but only for binary completion (0/1 or 1/1)
  - Level requirements show individual requirement completion
- **Missing**: Quantity-based progress (e.g., "7/10 addition-basics")

#### Test Setup APIs
- **Location**: `backend/app/routes.py` (lines 930-1010)
- **Current Protection**: 
  ```python
  if not current_app.config.get('TESTING') and not current_app.debug:
      return jsonify({"error": "Not available in production"}), 403
  ```
- **Issue**: Should use `TESTING` env var explicitly, default to `true` until v1.0

#### Tier System
- **Current State**: Mixed systems
  - Test achievements: B/A/S/SS/SSS (letters) - to be replaced with metal/prestige system
  - Some achievements: Bronze/Silver/Gold (metals)
  - Need consolidation to unified metal/prestige system
- **New Tier System**: Bronze > Silver > Gold > Platinum > Diamond > Master > Grandmaster > Legendary > Mythic > Divine > Champion
- **Champion Tier Requirements**:
  - Same requirements as Divine tier
  - Must set a new server record (first place, no ties)
  - Only qualifying achievements can have Champion tier
  - Examples: Fastest session on server, highest accuracy on server, most questions answered, longest streak, etc.
  - Requires server record tracking system
  - Real-time record checking on achievement award
  - Display of current server records in UI
- **Champion Tier Qualification**:
  - Not all achievements qualify (e.g., "first-steps" cannot have Champion)
  - Only achievements with measurable, comparable metrics qualify
  - Qualifying types: Speed, Accuracy, Volume, Streaks
  - Requires new data model: `ServerRecord` table to track current records

### Expected Outcomes

#### Data Model Changes
1. **Achievement Model Enhancement**:
   ```python
   # Add to Achievement model
   session_id = db.Column(db.Integer, db.ForeignKey("practice_sessions.id"), nullable=True, index=True)
   ```
   - Migration required to add column
   - Update achievement awarding logic to record `session_id`
   - Update queries to support session-based filtering

2. **Server Record Model (New)**:
   ```python
   class ServerRecord(db.Model):
       __tablename__ = "server_records"
       
       id = db.Column(db.Integer, primary_key=True)
       achievement_type = db.Column(db.String(64), nullable=False, unique=True, index=True)
       record_type = db.Column(db.String(32), nullable=False)  # 'speed', 'accuracy', 'volume', 'streak'
       record_value = db.Column(db.Float, nullable=False)  # The actual record value
       user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
       achieved_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
       session_id = db.Column(db.Integer, db.ForeignKey("practice_sessions.id"), nullable=True)
   ```
   - Tracks current server records for Champion tier qualification
   - One record per achievement type
   - Updated when new record is set (first place, no ties)
   - Migration required to create table

3. **Level Progression Config Enhancement**:
   ```python
   # Change from:
   2: [{"achievement_code": "addition-basics", "order": 1}]
   
   # To:
   2: [{"achievement_code": "addition-basics", "quantity": 10, "order": 1}]
   ```

4. **Test Definition Enhancement**:
   ```python
   # Add to test definitions:
   "unlock_requirements": {
       "type": "achievement_quantity",
       "achievement_code": "addition-basics",
       "quantity": 5,
       "level": 1,
       "min_accuracy": 1.0  # 100%
   }
   ```

#### UI Changes
1. **Tests Tab**:
   - All tests visible (not hidden)
   - Locked tests shown with disabled state
   - Tier filter shows best achieved tier (Bronze through Champion)
   - Status filter works correctly

2. **Level Requirements**:
   - Progress bars show quantity (e.g., "7/10")
   - Achievement names link to achievements tab with filter
   - `?env=dev` shows all level requirements (for all levels)

3. **Test Modal**:
   - PIN verification required
   - Loads practice interface (labeled "Test")
   - Same UI flow as practice

4. **Achievements Tab**:
   - `?env=dev` shows all achievements (including locked)
   - Generic achievements show count
   - All tier versions visible for achievements (Bronze through Champion where applicable)

#### Routing Changes
1. **React Router Integration**:
   - Routes: `/`, `/practice`, `/summary`, `/journey/:userId`, `/journey/:userId/:tab`, `/journey/:userId/:tab?filter=...`
   - Navigation uses `useNavigate()` instead of `window.location`
   - Deep linking to tabs with filters

#### Testing Changes
1. **Testing Framework**:
   - Abstractions for: animations, routing, data prep, cleanup
   - Pattern: `beforeEach` (data prep) → test logic → `afterEach` (cleanup)
   - URL-based navigation in tests

2. **Coverage**:
   - Baseline backend test coverage report
   - Migrate existing tests to new patterns
   - Add tests for new features

---

## Implementation Phases

### Phase 1: Data Model Foundation
**Goal**: Enable achievement-to-session tracking and quantity-based requirements

**Files to Modify**:
- `backend/app/models.py` - Add `session_id` to Achievement model
- `backend/migrate.py` - Add migration for new column
- `backend/app/services/achievement_service.py` - Update awarding logic to record `session_id`
- `backend/app/config/level_progression_config.py` - Add `quantity` field to requirements

**Key Functions**:
- `AchievementService.award_achievement()` - Record `session_id`
- `LevelConfigService.get_level_progression_config()` - Support quantity requirements
- Database migration function

**Dependencies**: None (foundation phase)

**Verification**:
- Migration runs successfully
- Achievements include `session_id` when awarded
- Level config supports quantity field
- API returns session info for achievements

---

### Phase 2: Generic Achievement System
**Goal**: Consolidate achievement definitions using generic, tiered achievements

**Files to Modify**:
- `backend/app/config/achievements/accuracy.py` - Consolidate to generic achievements
- `backend/app/config/achievements/test.py` - Consolidate test achievements
- `backend/app/config/achievements/__init__.py` - Update aggregation
- `backend/app/services/achievement_service.py` - Support quantity-based checking, Champion tier logic
- `backend/app/models.py` - Add server record tracking model (if needed)
- `backend/app/services/server_record_service.py` - New service for Champion tier record tracking

**Key Functions**:
- Achievement definition consolidation logic
- Quantity-based achievement checking
- Tier mapping to new metal/prestige system
- Champion tier qualification logic
- Server record tracking for Champion tier
- `ServerRecordService.checkAndUpdateRecord()` - Check if achievement qualifies for Champion, update records
- `ServerRecordService.getCurrentRecord()` - Get current server record for an achievement type
- `AchievementService.checkChampionEligibility()` - Check if user's performance qualifies for Champion tier

**Dependencies**: Phase 1 (needs session tracking)

**Verification**:
- Achievement definitions reduced significantly
- Generic achievements work (e.g., "addition-basics" with count)
- Tier consolidation complete
- All achievements use metal/prestige tiers (Bronze through Champion)
- Champion tier qualification logic works correctly
- Server records tracked and updated
- Champion tier only awarded when new record set (first place, no ties)

**Achievement Categories to Consolidate**:
1. **Accuracy Achievements**: 
   - Generic: `{operation}-basics` (Bronze tier)
   - Tiered: `{operation}-basics-{tier}` (Silver/Gold/Platinum/Diamond/Master/Grandmaster/Legendary/Mythic/Divine/Champion)
   - Requirements: Accuracy thresholds, speed thresholds, question counts (see Achievement List section)
   - Champion: Server record for qualifying achievements
2. **Test Achievements**:
   - Generic: `{test-type}-{tier}` (Bronze through Champion)
   - Requirements: Test completion with specific accuracy/speed thresholds
   - Champion: Server record for qualifying achievements
3. **Practice vs Test**: Separate achievement codes for practice vs test completions
4. **Champion Tier Qualification**: 
   - Only achievements that can have measurable server records qualify
   - Examples: Speed (fastest session), Accuracy (highest accuracy), Volume (most questions), Streaks (longest streak)
   - Not all achievements qualify (e.g., "first-steps" cannot have Champion tier)

---

### Phase 3: Test Unlocking System
**Goal**: Replace level-based test unlocking with achievement-based unlocking

**Files to Modify**:
- `backend/app/config/tests/test_definitions.py` - Add `unlock_requirements`
- `backend/app/services/test_service.py` - Check unlock requirements
- `frontend/src/features/students/components/journey/TestsTab.tsx` - Show unlock status
- `frontend/src/features/students/components/journey/TestCard.tsx` - Display requirements

**Key Functions**:
- `TestService.check_test_unlock_requirements()` - Evaluate achievement quantities
- Test definition unlock requirement structure
- UI display of unlock requirements

**Dependencies**: Phase 1, Phase 2

**Verification**:
- Tests unlock based on achievement quantities
- Test cards show unlock requirements
- Tests lock correctly until requirements met
- Test unlocking aligned with concept introduction

**Test Unlock Requirements Mapping**:
- "1 Digit Addition": 5 level 1 sessions with 100% accuracy
- "1 Digit Addition w/ Zeros": After zeros concept introduced + 5 sessions
- "1 Digit Addition w/ Negative Numbers": After negatives introduced + 5 sessions
- (Map all tests with appropriate requirements)

---

### Phase 4: Level Requirements Enhancement
**Goal**: Add quantity requirements and progress tracking

**Files to Modify**:
- `backend/app/config/level_progression_config.py` - Add quantities (e.g., level 2: 10 addition-basics)
- `frontend/src/features/students/utils/progressMapping.ts` - Calculate quantity progress
- `frontend/src/features/students/components/LevelRequirementCard.tsx` - Show quantity progress
- `frontend/src/features/students/components/journey/LevelsTab.tsx` - Link achievements

**Key Functions**:
- `convertBackendRequirementsToFrontend()` - Support quantity
- Progress calculation with quantities
- Achievement link navigation

**Dependencies**: Phase 1, Phase 2

**Verification**:
- Level 2 requires 10 addition-basics
- Progress bars show "7/10" format
- Achievement names link to achievements tab
- Links apply correct filter

---

### Phase 5: Application Router Migration
**Goal**: Implement React Router for all navigation

**Files to Modify**:
- `frontend/package.json` - Add `react-router-dom`
- `frontend/src/App.tsx` - Set up router
- `frontend/src/utils/routing.ts` - Replace with router
- `frontend/src/features/students/components/journey/LevelRequirementCard.tsx` - Use router links
- `frontend/src/features/students/components/journey/AchievementsTab.tsx` - Router navigation
- All navigation helpers - Replace with router

**Key Functions**:
- Router setup and route definitions
- `useNavigate()` for programmatic navigation
- Route parameters for tabs/filters
- Deep linking support

**Dependencies**: None (can be parallel)

**Verification**:
- All pages accessible via URL
- Navigation uses router
- Deep links work (e.g., `/journey/123/achievements?filter=addition-basics`)
- Browser back/forward works

**Testing Navigation Principle**:
- Use URL navigation in tests when the navigation mechanism (button click, link, etc.) is already tested in a dedicated test
- This allows tests to focus on the destination state/feature rather than the navigation path
- Still test with clicks when:
  - The button/click handler itself is what you're testing
  - The navigation interaction is part of the feature being tested
  - You're testing the complete user flow that includes navigation
- Example: If "clicking achievements tab" is tested elsewhere, other tests can navigate directly to `/journey/123/achievements` to test achievement display functionality

**Route Structure**:
```
/ - Dashboard
/practice - Practice session
/summary - Session summary
/journey/:userId - Journey modal (defaults to overview)
/journey/:userId/:tab - Specific tab (overview|achievements|levels|tests)
/journey/:userId/:tab?filter=... - Tab with filter
```

---

### Phase 6: Test Modal and Flow Fixes
**Goal**: Fix test modal PIN requirement and interface loading

**Files to Modify**:
- `frontend/src/features/students/components/journey/TestDetailModal.tsx` - Add PIN verification
- `frontend/src/features/students/components/LevelProgressionSystem.tsx` - PIN check before test start
- `frontend/src/features/practice/PracticeSessionPage.tsx` - Handle test mode
- `frontend/src/features/practice/components/PracticeHeader.tsx` - Show "Test" label

**Key Functions**:
- PIN verification before test start
- Test session initialization
- UI labeling for test mode

**Dependencies**: Phase 5 (router helps with navigation)

**Verification**:
- PIN required before test start
- Test interface loads correctly
- UI shows "Test" instead of "Practice"
- Test completion flows work

---

### Phase 7: Tests Tab UI Improvements
**Goal**: Show all tests, fix filters, improve UX

**Files to Modify**:
- `frontend/src/features/students/components/journey/TestsTab.tsx` - Show all tests, fix filters
- `frontend/src/features/students/components/journey/TestCard.tsx` - Disabled state for locked
- `frontend/src/features/students/hooks/useTests.ts` - Filter logic

**Key Functions**:
- Test visibility logic (show all, disable locked)
- Filter implementation (tier, status, search)
- Best tier calculation per test (Bronze through Champion)

**Dependencies**: Phase 3 (unlock requirements)

**Verification**:
- All tests visible
- Locked tests disabled (not hidden)
- Tier filter works (shows best achieved tier: Bronze through Champion)
- Status filter works correctly
- Search works

---

### Phase 8: Dev/Test Mode Enhancements
**Goal**: Enhanced dev features and API protection

**Files to Modify**:
- `backend/app/routes.py` - Protect test APIs with `TESTING` env var
- `backend/app/__init__.py` - Set `TESTING=true` by default
- `frontend/src/features/students/components/journey/AchievementsTab.tsx` - `?env=dev` shows all achievements
- `frontend/src/features/students/components/journey/LevelsTab.tsx` - `?env=dev` shows all level requirements

**Key Functions**:
- Environment variable checking
- Dev mode UI enhancements
- API protection logic

**Dependencies**: None (can be parallel)

**Verification**:
- `?env=dev` shows all achievements (including locked)
- `?env=dev` shows all level requirements (for all levels)
- Test setup APIs only available with `TESTING=true` env var (backend)
- Default `TESTING=true` until v1.0
- Single `?env=dev` flag controls all UI dev features (achievements, level requirements, etc.)

---

### Phase 9: Testing Framework and Coverage
**Goal**: Create testing abstractions and improve coverage

**Files to Create/Modify**:
- `frontend/e2e/helpers/test-framework.ts` - Testing abstractions
- `frontend/e2e/helpers/routing-helpers.ts` - Router navigation helpers
- `frontend/e2e/*.spec.ts` - Migrate existing tests
- `backend/tests/conftest.py` - Backend test fixtures
- `backend/tests/test_coverage_baseline.py` - Coverage baseline

**Key Functions**:
- `setupTestUser()` - Data preparation
- `navigateToRoute()` - Router-based navigation (use when navigation is tested elsewhere)
- `waitForAnimation()` - Animation handling
- `cleanupTestData()` - Cleanup
- Coverage reporting

**Testing Navigation Principle**:
- Use `navigateToRoute()` when the navigation mechanism is already tested in a dedicated test
- This allows tests to focus on the feature being tested rather than the navigation path
- Still use click-based navigation when testing the navigation itself or complete user flows

**Dependencies**: Phase 5 (router), Phase 1-4 (features to test)

**Verification**:
- Testing framework supports all patterns
- Existing tests migrated
- Coverage baseline established
- New tests use framework
- Coverage improved

**Testing Framework Structure**:
```typescript
// test-framework.ts
export async function setupTestScenario(request, scenario) {
  // Data prep
}

export async function navigateToRoute(page, route, params) {
  // Router navigation
}

export async function waitForComponent(page, testId) {
  // Wait for animations/loads
}

export async function cleanupScenario(request, scenario) {
  // Cleanup
}
```

---

### Phase 10: Milestone Achievements and Final Polish
**Goal**: Add new milestone achievements and finalize tier consolidation

**Files to Modify**:
- `backend/app/config/achievements/milestone.py` - New milestone achievements
- `backend/app/config/achievements/__init__.py` - Final tier consolidation
- `frontend/src/features/students/components/AchievementCard.tsx` - Display tiers

**Key Functions**:
- New milestone definitions
- Tier consolidation verification
- Achievement display updates

**Dependencies**: Phase 2 (tier system)

**Verification**:
- New milestones added
- All tiers use metal/prestige system (Bronze > Silver > Gold > Platinum > Diamond > Master > Grandmaster > Legendary > Mythic > Divine > Champion)
- Champion tier implemented for qualifying achievements
- Server record tracking functional
- Tier progression is clear and consistent

**New Milestone Ideas** (see Achievement List section for full breakdown):
- "Week Warrior" - Streak achievements (Bronze through Champion)
- "Question Master" - Total questions answered (Bronze through Champion)
- "Speed Demon" - Average speed achievements (Bronze through Champion)
- "Perfect Streak" - Consecutive perfect sessions (Bronze through Champion)

**Champion Tier Implementation**:
- Server record tracking table/model
- Real-time record checking on achievement award
- Champion tier qualification logic per achievement type
- Display of current server records in UI

---

## Work Division and Execution Order

### Parallel Work Streams

#### Stream A: Data Model & Backend (Phases 1-4, 8)
**Agent 1**: Data Model Foundation (Phase 1)
- Database migration
- Model updates
- Achievement awarding logic

**Agent 2**: Achievement System (Phase 2)
- Achievement consolidation
- Generic achievement definitions
- Tier system unification

**Agent 3**: Test & Level Requirements (Phases 3-4)
- Test unlock requirements
- Level quantity requirements
- Progress calculation

**Agent 4**: API Protection (Phase 8)
- Environment variable handling
- API protection
- Dev mode features

#### Stream B: Frontend & UI (Phases 5-7)
**Agent 5**: Router Migration (Phase 5)
- React Router setup
- Route definitions
- Navigation updates

**Agent 6**: Test UI Fixes (Phase 6)
- PIN verification
- Test interface loading
- UI labeling

**Agent 7**: Tests Tab Improvements (Phase 7)
- Filter fixes
- Visibility logic
- UX improvements

#### Stream C: Testing & Quality (Phase 9)
**Agent 8**: Testing Framework (Phase 9)
- Framework abstractions
- Test migration
- Coverage baseline

#### Stream D: Polish (Phase 10)
**Agent 9**: Milestones & Finalization (Phase 10)
- New milestones
- Final tier consolidation
- Documentation

### Execution Order

#### Week 1: Foundation
1. **Phase 1** (Agent 1) - Data model foundation
2. **Phase 8** (Agent 4) - API protection (parallel)
3. **Phase 5** (Agent 5) - Router migration (parallel, no dependencies)

#### Week 2: Core Features
4. **Phase 2** (Agent 2) - Achievement system (depends on Phase 1)
5. **Phase 3** (Agent 3) - Test unlocking (depends on Phase 1, 2)
6. **Phase 4** (Agent 3) - Level requirements (depends on Phase 1, 2)

#### Week 3: UI & Integration
7. **Phase 6** (Agent 6) - Test modal fixes (depends on Phase 5)
8. **Phase 7** (Agent 7) - Tests tab improvements (depends on Phase 3)

#### Week 4: Testing & Polish
9. **Phase 9** (Agent 8) - Testing framework (depends on Phases 1-7)
10. **Phase 10** (Agent 9) - Milestones & polish (depends on Phase 2)

### Critical Path
1. Phase 1 → Phase 2 → Phase 3 → Phase 4 (Backend features)
2. Phase 5 → Phase 6 (Frontend navigation)
3. Phase 1-7 → Phase 9 (Testing depends on features)

### Dependencies Graph
```
Phase 1 (Data Model)
  ├─> Phase 2 (Achievements)
  │     └─> Phase 3 (Test Unlocking)
  │     └─> Phase 4 (Level Requirements)
  │     └─> Phase 10 (Milestones)
  │
Phase 5 (Router) - Independent
  └─> Phase 6 (Test Modal)
  └─> Phase 9 (Testing Framework)

Phase 3 (Test Unlocking)
  └─> Phase 7 (Tests Tab UI)

Phase 8 (API Protection) - Independent

Phase 1-7
  └─> Phase 9 (Testing Framework)
```

### Risk Mitigation
- **Data Migration Risk**: Phase 1 includes migration - test thoroughly in dev
- **Breaking Changes**: Phases 2-4 change achievement system - coordinate with frontend
- **Router Migration**: Phase 5 affects all navigation - test all routes
- **Testing Framework**: Phase 9 depends on all features - start framework design early

### Success Metrics
- Achievement definitions reduced by 50%+
- All tests unlock based on achievements
- Level 2 requires 10 achievements (verified)
- Router enables URL-based navigation
- Test coverage baseline established
- All tiers consolidated to metal/prestige system
- PIN required for tests
- All tests visible in tests tab

---

## Appendix: Code References

### Key Files and Functions

#### Backend
- **Achievement Model**: `backend/app/models.py:100-115`
- **Level Progression Config**: `backend/app/config/level_progression_config.py:6-159`
- **Test Definitions**: `backend/app/config/tests/test_definitions.py:1-115`
- **Achievement Service**: `backend/app/services/achievement_service.py`
- **Test Service**: `backend/app/services/test_service.py:20-272`
- **Test Setup API**: `backend/app/routes.py:930-1010`

#### Frontend
- **Level Requirements Card**: `frontend/src/features/students/components/LevelRequirementCard.tsx:1-130`
- **Progress Mapping**: `frontend/src/features/students/utils/progressMapping.ts:127-172`
- **Tests Tab**: `frontend/src/features/students/components/journey/TestsTab.tsx:1-109`
- **Test Card**: `frontend/src/features/students/components/journey/TestCard.tsx:1-109`
- **Routing Utils**: `frontend/src/utils/routing.ts:1-17`
- **App Component**: `frontend/src/App.tsx:1-18`

#### Testing
- **E2E Helpers**: `frontend/e2e/helpers/test-helpers.ts:1-135`
- **Journey Helpers**: `frontend/e2e/helpers/ui/journey-helpers.ts:1-113`
- **Test Flow Tests**: `frontend/e2e/test-flow.spec.ts:1-224`

---

## Graph Database Exploration Plan

### Questions to Explore
1. **Current Relationship Complexity**: How many relationships exist between entities?
   - User → Achievements (1:many)
   - User → PracticeSessions (1:many)
   - PracticeSession → Responses (1:many)
   - Achievement → Session (many:1, after Phase 1)
   - Level → Requirements → Achievements (complex)

2. **Query Patterns**: What queries are complex in SQL?
   - "Find all achievements earned in sessions at level N"
   - "Count achievements by type for user"
   - "Find users who earned achievement X in session Y"
   - "Calculate achievement progress for level requirements"

3. **Maintainability**: Would graph queries be clearer?
   - Current: Multiple JOINs, subqueries
   - Graph: Pattern matching, path queries

### Cost-Benefit Analysis

#### Benefits
- **Query Clarity**: Graph queries more intuitive for relationships
- **Flexibility**: Easy to add new relationship types
- **Performance**: Graph DBs optimized for relationship queries
- **Schema Evolution**: Easier to evolve relationship structure

#### Costs
- **Migration Effort**: Significant refactoring required
- **Learning Curve**: Team needs graph DB knowledge
- **Infrastructure**: Additional database to maintain
- **Data Sync**: If keeping SQLite, need sync mechanism
- **Tooling**: Different tooling ecosystem

#### Objective Evaluation Criteria
1. **Query Complexity**: Count complex queries (>3 JOINs)
2. **Relationship Growth**: Project future relationship types
3. **Team Expertise**: Assess graph DB knowledge
4. **Migration Cost**: Estimate refactoring effort
5. **Performance**: Benchmark current vs graph queries

### Recommendation
**Phase 1**: Complete current refactoring (Phases 1-10) with SQLite
**Phase 2**: After v1.0, evaluate graph DB if:
- Query complexity increases significantly
- New relationship types needed frequently
- Performance becomes bottleneck
- Team has graph DB expertise

**Exploration Task**: Create proof-of-concept with Neo4j or similar, benchmark 5 complex queries, compare with SQLite implementation.

---

## Achievement List by Category (Target State)

### Tier System
**Tier Progression**: Bronze > Silver > Gold > Platinum > Diamond > Master > Grandmaster > Legendary > Mythic > Divine > Champion

**Champion Tier**: 
- Requires same as Divine tier
- Must set a new server record (first place, no ties)
- Only qualifying achievements can have Champion tier
- Examples: Fastest session on server, highest accuracy on server, most questions answered, longest streak, etc.

### Accuracy Achievements (Generic, Tiered)
- `{operation}-basics-bronze`: Complete level N with 80%+ accuracy
- `{operation}-basics-silver`: Complete level N with 85%+ accuracy, <30 questions
- `{operation}-basics-gold`: Complete level N with 90%+ accuracy, 31-59 questions
- `{operation}-basics-platinum`: Complete level N with 95%+ accuracy, 60-89 questions, <5s/question
- `{operation}-basics-diamond`: Complete level N with 98%+ accuracy, 90+ questions, <4s/question
- `{operation}-basics-master`: Complete level N with 100% accuracy, 50+ questions, <3.5s/question
- `{operation}-basics-grandmaster`: Complete level N with 100% accuracy, 75+ questions, <3s/question
- `{operation}-basics-legendary`: Complete level N with 100% accuracy, 100+ questions, <2.5s/question
- `{operation}-basics-mythic`: Complete level N with 100% accuracy, 100+ questions, <2s/question
- `{operation}-basics-divine`: Complete level N with 100% accuracy, 100+ questions, <1.5s/question
- `{operation}-basics-champion`: Same as Divine + new server record (if qualifying)

**Operations**: addition, subtraction, multiplication, division
**Levels**: 1-45 (as appropriate)

### Test Achievements (Generic, Tiered)
- `{test-type}-bronze`: Complete test
- `{test-type}-silver`: 90%+ accuracy, <30 questions
- `{test-type}-gold`: 95%+ accuracy, 31-59 questions
- `{test-type}-platinum`: 98%+ accuracy, 60-89 questions, <5s/question
- `{test-type}-diamond`: 100% accuracy, 90+ questions, <4s/question
- `{test-type}-master`: 100% accuracy, 100+ questions, <3.5s/question
- `{test-type}-grandmaster`: 100% accuracy, 100+ questions, <3s/question
- `{test-type}-legendary`: 100% accuracy, 100+ questions, <2.5s/question
- `{test-type}-mythic`: 100% accuracy, 100+ questions, <2s/question
- `{test-type}-divine`: 100% accuracy, 100+ questions, <1.5s/question
- `{test-type}-champion`: Same as Divine + new server record (if qualifying)

**Test Types**: All from `test_definitions.py`
**Note**: Exact thresholds may need adjustment based on test question counts and difficulty

### Milestone Achievements (Unique, Tiered)
- `first-steps`: Answer first question (Bronze)
- `first-victory`: Complete first session (Silver)
- `century-club`: Answer 100 questions (Gold)
- `week-warrior-bronze`: 7 day streak
- `week-warrior-silver`: 14 day streak
- `week-warrior-gold`: 30 day streak
- `week-warrior-platinum`: 60 day streak
- `week-warrior-diamond`: 90 day streak
- `week-warrior-master`: 180 day streak
- `week-warrior-grandmaster`: 365 day streak
- `week-warrior-legendary`: 730 day streak
- `week-warrior-mythic`: 1000 day streak
- `week-warrior-divine`: 2000 day streak
- `week-warrior-champion`: Longest streak on server (if qualifying)
- `question-master-bronze`: 100 total questions
- `question-master-silver`: 500 total questions
- `question-master-gold`: 1000 total questions
- `question-master-platinum`: 2500 total questions
- `question-master-diamond`: 5000 total questions
- `question-master-master`: 10000 total questions
- `question-master-grandmaster`: 25000 total questions
- `question-master-legendary`: 50000 total questions
- `question-master-mythic`: 100000 total questions
- `question-master-divine`: 250000 total questions
- `question-master-champion`: Most questions answered on server (if qualifying)
- `speed-demon-bronze`: Average <5s per question
- `speed-demon-silver`: Average <4s per question
- `speed-demon-gold`: Average <3s per question
- `speed-demon-platinum`: Average <2.5s per question
- `speed-demon-diamond`: Average <2s per question
- `speed-demon-master`: Average <1.5s per question
- `speed-demon-grandmaster`: Average <1s per question
- `speed-demon-legendary`: Average <0.8s per question
- `speed-demon-mythic`: Average <0.6s per question
- `speed-demon-divine`: Average <0.5s per question
- `speed-demon-champion`: Fastest average speed on server (if qualifying)
- `perfect-streak-bronze`: 3 consecutive perfect sessions
- `perfect-streak-silver`: 5 consecutive perfect sessions
- `perfect-streak-gold`: 10 consecutive perfect sessions
- `perfect-streak-platinum`: 20 consecutive perfect sessions
- `perfect-streak-diamond`: 50 consecutive perfect sessions
- `perfect-streak-master`: 100 consecutive perfect sessions
- `perfect-streak-grandmaster`: 250 consecutive perfect sessions
- `perfect-streak-legendary`: 500 consecutive perfect sessions
- `perfect-streak-mythic`: 1000 consecutive perfect sessions
- `perfect-streak-divine`: 2500 consecutive perfect sessions
- `perfect-streak-champion`: Longest perfect streak on server (if qualifying)

### Practice vs Test Distinction
- Practice achievements: `{operation}-basics-{tier}` (from practice sessions)
- Test achievements: `{test-type}-{tier}` (from test sessions)
- Separate tracking allows different requirements

---

**Document Version**: 1.0  
**Last Updated**: 2024-01-XX  
**Status**: Ready for Implementation

