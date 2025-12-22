# Test & Code Review

We are reviewing each test after major changes to ensure relevance, and we have proper positive and negative test coverage over the features.

The tests will be broken up into four sections: Statistics, backend tests, frontend tests, and e2e tests. Each section will contain detailed information about the test.

## Statistics

### Line Coverage

**Backend Coverage:**
- Total Line Coverage: 77.21%
- Lines Covered: 3,157
- Total Lines: 4,089
- Target: ≥80% (currently below target, improvements needed)

**Frontend Coverage:**
- Overall Coverage: ~69% (statement coverage)
- Branch Coverage: ~70%
- Function Coverage: ~77%
- Line Coverage: ~77%

### Test Counts

**Backend Tests:**
- Total Test Files: 38
- Total Test Functions: 579
- Framework: pytest
- Recent additions: Achievement XP Service tests (+65 tests), XP breakdown tests (+4 tests)

**Frontend Unit Tests:**
- Total Test Files: 16
- Total Test Cases: 224
- Framework: Vitest
- Recent additions: XPEarningsBreakdown tests (+10 tests), ProblemDetailModal tests (+9 tests)

**E2E Tests:**
- Total Test Files: 16
- Total Test Cases: ~115 (reduced from 118 after consolidation)
- Framework: Playwright
- Recent changes: Consolidated SUB-002 and SUB-003 into SUM-002, removed redundant PRAC-006

The backend and frontend tests will break down each test as follows:

```
## Test Name

Purpose of test: To verify the feature X does not cause Y, under Z conditions.

Test Setup:
* Create a User
* Grant Achievement X, Y
* Start a session
...

Action: Call X function

Expect:
* X to happen
```

E2E tests will follow the same format, but include all frontend interactions as well.

```
## Test Name

Purpose of test: To verify the feature X does not cause Y, under Z conditions.

Test Setup:
* Create a User
* Grant Achievement X, Y
* Start a session
...

Actions: 
* Click this
* Click that
* Enter this
...

Expect:
* X to happen
```

## Backend Tests

### API Protection Tests (`test_api_protection.py`)

#### test_api_protection_001_test_setup_with_testing_enabled

Purpose of test: To verify that test setup endpoint works when TESTING=true.

Test Setup:
* Create Flask app with TESTING=True
* Create a test user

Action: POST to `/api/users/{user_id}/test-setup` with level=5

Expect:
* Response status 200
* Response includes success=true and level=5

#### test_api_protection_002_test_setup_with_testing_disabled

Purpose of test: To verify that test setup endpoint returns 403 when TESTING=false.

Test Setup:
* Create Flask app with TESTING=False
* Create a test user

Action: POST to `/api/users/{user_id}/test-setup` with level=5

Expect:
* Response status 403
* Response includes error message about not available in production

#### test_api_protection_003_reset_user_with_testing_enabled

Purpose of test: To verify that reset user endpoint works when TESTING=true.

Test Setup:
* Create Flask app with TESTING=True
* Create a test user

Action: DELETE to `/api/users/{user_id}/reset`

Expect:
* Response status 200
* Response includes success=true

#### test_api_protection_004_reset_user_with_testing_disabled

Purpose of test: To verify that reset user endpoint returns 403 when TESTING=false.

Test Setup:
* Create Flask app with TESTING=False
* Create a test user

Action: DELETE to `/api/users/{user_id}/reset`

Expect:
* Response status 403
* Response includes error message

#### test_api_protection_005_delete_user_with_testing_enabled

Purpose of test: To verify that delete user endpoint works when TESTING=true.

Test Setup:
* Create Flask app with TESTING=True
* Create a test user

Action: DELETE to `/api/users/{user_id}`

Expect:
* Response status 200
* Response includes success=true

#### test_api_protection_006_delete_user_with_testing_disabled

Purpose of test: To verify that delete user endpoint returns 403 when TESTING=false.

Test Setup:
* Create Flask app with TESTING=False
* Create a test user

Action: DELETE to `/api/users/{user_id}`

Expect:
* Response status 403
* Response includes error message

#### test_api_protection_007_reset_all_with_testing_enabled

Purpose of test: To verify that reset all data endpoint works when TESTING=true.

Test Setup:
* Create Flask app with TESTING=True

Action: DELETE to `/api/reset`

Expect:
* Response status 200
* Response includes success=true

#### test_api_protection_008_reset_all_with_testing_disabled

Purpose of test: To verify that reset all data endpoint returns 403 when TESTING=false.

Test Setup:
* Create Flask app with TESTING=False

Action: DELETE to `/api/reset`

Expect:
* Response status 403
* Response includes error message

#### test_api_protection_009_default_testing_is_true

Purpose of test: To verify that default TESTING config is True (until v1.0).

Test Setup:
* None (test default config)

Action: Create app without test_config

Expect:
* app.config.get('TESTING') is True

#### test_api_protection_010_test_setup_awards_achievements_with_testing

Purpose of test: To verify that test setup can award achievements when TESTING=true.

Test Setup:
* Create Flask app with TESTING=True
* Create a test user

Action: POST to `/api/users/{user_id}/test-setup` with achievements=['first-steps']

Expect:
* Response status 200
* Response includes success=true

### Achievement Model Tests (`test_achievement_model.py`)

#### test_achievement_model_001_create_without_session_id

Purpose of test: To verify that Achievement can be created without session_id (nullable).

Test Setup:
* Create Flask app
* Create a test user

Action: Create Achievement with session_id=None

Expect:
* Achievement is created successfully
* achievement.id is not None
* achievement.session_id is None
* achievement.user_id matches test user

#### test_achievement_model_002_create_with_session_id

Purpose of test: To verify that Achievement can be created with session_id.

Test Setup:
* Create Flask app
* Create a test user
* Create a test practice session

Action: Create Achievement with session_id=test_session.id

Expect:
* Achievement is created successfully
* achievement.session_id matches test_session.id
* achievement.user_id matches test user

#### test_achievement_model_003_query_by_session_id

Purpose of test: To verify that Achievements can be queried by session_id.

Test Setup:
* Create Flask app
* Create a test user
* Create a test practice session
* Create two achievements - one with session_id, one without

Action: Query achievements by session_id

Expect:
* Only achievement with matching session_id is returned
* Achievement without session_id is not included

#### test_achievement_model_004_foreign_key_constraint

Purpose of test: To verify that foreign key constraint prevents invalid session_id.

Test Setup:
* Create Flask app
* Create a test user

Action: Try to create Achievement with non-existent session_id (99999)

Expect:
* IntegrityError is raised when committing

#### test_achievement_model_005_session_relationship

Purpose of test: To verify that Achievement has relationship to PracticeSession.

Test Setup:
* Create Flask app
* Create a test user
* Create a test practice session

Action: Create Achievement with session_id and check relationship

Expect:
* achievement.session is not None
* achievement.session.id matches test_session.id

#### test_achievement_model_006_index_on_session_id

Purpose of test: To verify that index exists on session_id for query performance.

Test Setup:
* Create Flask app
* Create a test user
* Create a test practice session
* Create 5 achievements with same session_id

Action: Query achievements by session_id

Expect:
* All 5 achievements are returned
* Query performs efficiently (index exists)

### User Service Tests (`test_user_service.py`)

(Note: This file contains 33 tests covering UserService methods including create_user, get_user, verify_pin, can_level_up, level_up, update_user, delete_user, etc. Tests verify validation, error handling, cascading deletes, and level progression logic.)

### Practice Service Tests (`test_practice_service.py`)

(Note: This file contains 33 tests covering PracticeService methods including create_session, complete_session, create_question, record_response, flag_question, get_incomplete_session, validate_answer, etc. Tests verify session management, question handling, response recording, and validation logic.)

### Question Service Tests (`test_question_service.py`)

(Note: This file contains 24 tests covering QuestionService methods including get_operation_symbol, solve, format_answer, validate_constraints, generate_operands_with_constraints, create_work_steps, generate_question, etc. Tests verify question generation, answer formatting, constraint validation, and work step creation.)

### Achievement Tests

#### Achievement Awarding Tests (`test_achievements_awarding.py`)

**14 tests** covering achievement awarding for:
- first-victory achievement
- first-steps achievement  
- question-master-bronze achievement
- speed-demon-bronze/gold achievements
- perfect-streak-bronze achievement
- week-warrior-bronze achievement
- Unique constraint verification (first-steps and first-victory only awarded once)
- Session completion requirements

#### Accuracy Ace Achievement Tests (`test_accuracy_ace_achievements.py`)

**9 tests** covering:
- Accuracy Ace bronze/silver/gold tier awarding (80%+/90%+/100% accuracy with 10+ questions)
- Minimum questions requirement (not awarded with <10 questions)
- Below threshold handling (not awarded for <80% accuracy)
- Highest tier only awarding
- Multiple instances across sessions
- One per session limitation

#### Accuracy Ace Checker Tests (`test_accuracy_ace_checker.py`)

**12 tests** covering:
- Checker initialization
- No session/incomplete session handling
- User fetching and validation
- Config validation
- Question count requirements
- Already earned checks
- Highest tier awarding
- Champion tier eligibility
- None accuracy handling

#### Achievement Constraints Tests (`test_achievement_constraints.py`)

**15 tests** covering constraint rules for all achievement types:
- Accuracy Ace: multiple instances across sessions, one per session, highest tier only
- Speed Demon: highest tier calculation, multiple instances across sessions
- First Steps/First Victory: unique constraints
- Level Master: multiple per tier, multiple per session
- Lightning Fast: practice metadata usage
- Question Master: one per tier, once per session
- So Wow: one per tier, multiple per session
- Week Warrior: multiple per tier, once per session
- Master Tables: one per tier, multiple per session

#### Achievement Query Service Tests (`test_achievement_query_service.py`)

**13 tests** covering:
- Getting user achievements (with/without limit)
- Getting achievements by session
- Getting achievements by category (all users)
- Getting achievement codes for user
- Counting achievements by code (with filters: level, accuracy, concept_id)
- Legacy level metadata matching with concept_id

#### Achievement Service Session Tracking Tests (`test_achievement_service_session_tracking.py`)

**7 tests** covering:
- Creating achievements without session_id (optional)
- Creating achievements with session_id
- Querying achievements by session
- Serializing achievements with/without session_id

#### Achievement Utils Tests (`test_achievement_utils.py`)

**18 tests** covering:
- Getting achievement configs (with caching)
- Clearing config cache
- Debug print functionality
- Creating achievements (basic, with metadata, with session_id, custom earned_at)
- Returning existing achievements
- Updating session_id on existing achievements
- Metadata handling and constraint checks
- Serializing achievements (with metadata, user_name, session_id)

#### Achievement XP Service Tests (`test_achievement_xp_service.py`)

**3 tests** covering:
- XP reward for tiered achievements (only `speed-demon-diamond` tested)
- XP reward for non-tiered unique achievements (only `first-steps` tested)
- Default zero reward for unknown achievements

### Achievement XP Service Test Coverage Improvements

**Current Status:** Only 3 tests exist, covering just 2 achievement codes out of 107 total achievements. The tests verify basic lookup functionality but do not comprehensively test bonus XP amounts, multiplier values, or tier variations.

#### Priority 1: Test All Achievement Base Types (16 total)

Currently tested: 2 base types (`speed-demon`, `first-steps`)

**Achievements WITH multipliers (9 types - need comprehensive testing):**
- `accuracy-ace` - 3 tiers (bronze, silver, gold) - **NEEDS TESTS**
- `first-steps` - 1 tier (bronze) - ✅ Tested
- `first-victory` - 1 tier (silver) - **NEEDS TESTS**
- `level-master` - 11 tiers - **NEEDS TESTS** (verify multiplier progression: 1.5, 2.0, 2.5... 6.5)
- `lightning-fast` - 11 tiers - **NEEDS TESTS** (verify multiplier progression: 1.4, 1.8, 2.3... 9.9)
- `perfect-streak` - 11 tiers - **NEEDS TESTS** (verify multiplier progression: 1.4, 1.8, 2.3... 9.9)
- `question-master` - 11 tiers - **NEEDS TESTS** (verify multiplier progression: 2, 3, 4... 12)
- `speed-demon` - 11 tiers - ⚠️ Only diamond tier tested - **NEEDS MORE TESTS**
- `week-warrior` - 11 tiers - **NEEDS TESTS** (verify multiplier progression: 1.2, 1.4, 1.7... 8.5)

**Achievements WITHOUT multipliers (7 types - bonus XP only):**
- `human-calculator` - 11 tiers - **NEEDS TESTS** (verify bonus_xp values, multiplier=0)
- `level-grandmaster` - 11 tiers - **NEEDS TESTS** (verify bonus_xp values, multiplier=0)
- `master-of-basic-addition` - 11 tiers - **NEEDS TESTS**
- `master-of-basic-subtraction` - 11 tiers - **NEEDS TESTS**
- `master-of-division-tables` - 11 tiers - **NEEDS TESTS**
- `master-of-times-tables` - 11 tiers - **NEEDS TESTS**
- `so-wow` - 11 tiers - **NEEDS TESTS** (verify bonus_xp values, multiplier=None)

#### Priority 2: Test Multiplier Calculations

**Current Coverage:** No explicit tests for multiplier factor to delta conversion

**Needed Tests:**

1. **Multiplier Factor to Delta Conversion:**
   - Test that multiplier factors (e.g., 1.03, 1.32) are correctly converted to deltas (0.03, 0.32)
   - Verify: `delta = factor - 1.0`
   - Test across different achievement types and tiers

2. **Total Multiplier Calculation:**
   - Test that multiple achievements combine multipliers correctly: `total = 1.0 + sum(deltas)`
   - Example: first-steps (1.01) + accuracy-ace-gold (1.03) = 1.0 + 0.01 + 0.03 = 1.04
   - Verify NOT using sum of factors (would be 2.04, incorrect)

3. **Multiplier Edge Cases:**
   - Achievements with multiplier = None (should contribute 0 to multiplier sum)
   - Achievements with multiplier = 0.0 (should contribute 0 to multiplier sum)
   - Multiple achievements with same multiplier (should all contribute)
   - Very large multipliers (e.g., speed-demon-champion: 11.24 factor)

4. **Multiplier Progression Across Tiers:**
   - Verify multiplier values increase correctly across tiers
   - Test representative tiers (bronze, gold, platinum, champion) for each achievement type
   - Ensure multiplier array matches tier array length

#### Priority 3: Test Bonus XP Values

**Current Coverage:** Basic verification only (speed-demon-diamond: 50, first-steps: 50)

**Needed Tests:**

1. **Bonus XP for All Achievement Types:**
   - Verify bonus_xp values match `ACHIEVEMENT_XP_TABLE` config
   - Test at least bronze, gold, and champion tiers for each achievement type
   - Verify bonus XP increases across tiers where applicable

2. **Bonus XP Edge Cases:**
   - Achievements with no bonus_xp (should return 0)
   - Very large bonus_xp values (e.g., question-master-champion: 800000)
   - Multiple achievements (bonus XP should sum correctly)

3. **Bonus XP Progression:**
   - Verify bonus_xp array matches tier array length
   - Test that bonus XP values are consistent with expected progression patterns

#### Priority 4: Test Tier Index Lookup

**Current Coverage:** Basic tier extraction tested indirectly

**Needed Tests:**

1. **Tier Extraction and Index Matching:**
   - Test `extract_base_code_and_tier()` correctly separates base code and tier
   - Test tier index lookup for all tiers (bronze=0, silver=1, gold=2, etc.)
   - Test invalid tier handling (should default to index 0)

2. **Edge Cases:**
   - Achievement codes without tier suffix (e.g., `first-steps`)
   - Achievement codes with tier that doesn't exist in config (should use index 0)
   - Achievement codes with tier in wrong position

3. **Single-Tier Achievements:**
   - Verify single-tier achievements (like `first-steps`, `first-victory`) work correctly
   - Ensure tier is set correctly even when only one tier exists

#### Priority 5: Integration with XP Calculation

**Current Coverage:** `test_complete_session_xp_breakdown.py` has one test with multipliers

**Needed Tests:**

1. **XP Calculation Formula Verification:**
   - Test: `total_xp = (base_xp * total_multiplier) + bonus_xp`
   - Verify base_xp calculation (correct_count * xp_per_correct)
   - Verify multiplier application happens before bonus XP addition
   - Test with multiple achievements contributing multipliers and bonus XP

2. **Session Achievement Contribution:**
   - Verify only achievements earned DURING the session contribute to XP
   - Test that pre-existing achievements don't affect session XP
   - Verify achievement rewards are fetched correctly from session achievements

3. **XP Breakdown Response Format:**
   - Verify `xp_breakdown.multipliers` returns deltas (not factors)
   - Verify `xp_breakdown.total_multiplier` is calculated correctly
   - Verify `xp_breakdown.bonus_xp` and `xp_breakdown.bonus_xp_sources` are correct
   - Test response includes all contributing achievements

#### Test Strategy Recommendations

1. **Create Comprehensive Test Suite:**
   - Test all 16 achievement base types
   - For 11-tier achievements: test bronze, gold, platinum, champion (representative tiers)
   - For 3-tier achievements: test all tiers
   - For 1-tier achievements: test the single tier

2. **Test Pattern for Multiplier Achievements:**
   ```python
   def test_[achievement]_[tier]_multiplier_and_bonus(app):
       """Test that [achievement] [tier] returns correct multiplier and bonus XP."""
       reward = AchievementXPService.reward_for_achievement_code("[achievement]-[tier]")
       expected_factor = [expected_factor_from_config]
       expected_delta = expected_factor - 1.0
       expected_bonus = [expected_bonus_from_config]
       
       assert reward.multiplier == expected_factor
       assert reward.multiplier - 1.0 == expected_delta  # Verify delta calculation
       assert reward.bonus_xp == expected_bonus
   ```

3. **Test Pattern for Non-Multiplier Achievements:**
   ```python
   def test_[achievement]_[tier]_bonus_only(app):
       """Test that [achievement] [tier] returns bonus XP but no multiplier."""
       reward = AchievementXPService.reward_for_achievement_code("[achievement]-[tier]")
       expected_bonus = [expected_bonus_from_config]
       
       assert reward.bonus_xp == expected_bonus
       assert reward.multiplier == 0.0 or reward.multiplier is None
   ```

4. **Integration Test Pattern:**
   ```python
   def test_xp_calculation_with_multiple_achievements(app, test_user):
       """Test XP calculation with multiple achievements contributing multipliers and bonus."""
       # Setup: Create session with multiple achievements
       # Verify: base_xp, total_multiplier, bonus_xp, total_awarded_xp
       # Verify: multipliers array contains deltas, not factors
   ```

5. **Use Test Data from Config:**
   - Read directly from `ACHIEVEMENT_XP_TABLE` to ensure tests match actual config
   - This makes tests maintainable if config changes
   - Consider parametrized tests for tier-based achievements

#### Estimated Test Count

- **Achievement Type Coverage:** ~50 tests (16 base types × ~3 representative tiers each)
- **Multiplier Calculation:** ~10 tests (factor-to-delta, total calculation, edge cases)
- **Bonus XP Verification:** ~30 tests (bonus XP values, progression, edge cases)
- **Tier Index Lookup:** ~10 tests (extraction, matching, edge cases)
- **Integration Tests:** ~15 tests (XP calculation, session contribution, response format)

**Total Estimated:** ~115 additional tests needed for comprehensive coverage

#### Priority Order for Implementation

1. **Phase 1 (Critical):** Multiplier calculation tests (factor-to-delta conversion, total calculation)
2. **Phase 2 (High):** Test all achievement base types with at least bronze tier
3. **Phase 3 (Medium):** Test tier progression (gold, platinum, champion) for key achievements
4. **Phase 4 (Complete):** Test all tiers for all achievements, edge cases, integration tests

#### Achievement Orchestrator Tests (`test_achievement_orchestrator.py`)

**23 tests** covering:
- Orchestrator initialization
- Ensuring achievements with/without responses
- New activity detection
- Metrics usage
- Session ID passing
- Calling all checkers
- Committing on new achievements
- Batch processing (single/multiple users)
- Data loading optimization
- Level-specific achievement awarding (Level Master, Level Grandmaster, Human Calculator)

#### Generic Achievement Tests (`test_generic_achievements.py`)

**18 tests** covering:
- Tier utility functions (hierarchy, all tiers, old tier mapping, tier comparison, tier values)
- Counting achievements by code
- Champion eligibility checking
- Level accuracy with max_speed support
- Achievement config inclusion verification
- All tier presence validation

#### Human Calculator Achievement Tests (`test_human_calculator_achievements.py`)

**3 tests** covering:
- Verification of all levels qualified
- Higher tier acceptance (Silver qualifies for Bronze requirement)

#### Level Grandmaster Checker Tests (`test_level_grandmaster_checker.py`)

**5 tests** covering:
- Level Master Bronze requirement
- Awarding when all levels qualified
- Not awarding if level missing consecutively
- No duplication
- Tier substitution (higher tiers qualify)

#### Level Master Achievement Tests (`test_level_master_achievements.py`)

**8 tests** covering:
- Bronze awarded for exactly 30 correct in a row
- Silver awarded for exactly 60 correct (highest tier only)
- Not awarded for 29 correct + 1 incorrect
- Awarded for 30 correct + 1 incorrect (max consecutive is 30)
- Multiple awards (30 correct → bronze → 1 wrong → 30 correct → bronze)
- Only highest tier awarded (gold for 120 consecutive)
- Multiple levels support (achievements per level)

#### Level Specific Checkers Tests (`test_level_specific_checkers.py`)

**4 tests** covering:
- Perfect Streak checker awards bronze for 3 perfect sessions
- No award for imperfect session
- Four perfect sessions yields one achievement, not two

#### Lightning Fast Achievement Tests (`test_lightning_fast_achievements.py`)

**9 tests** covering:
- Bronze minimum questions requirement
- Not awarded below minimum
- Silver minimum questions
- Excludes incorrect answers from speed calculation

#### Master Times/Division Tables Achievement Tests (`test_master_times_division_achievements.py`)

**5 tests** covering:
- Master of Times Tables bronze requirements
- Master of Division Tables bronze requirements
- All tiers for both achievement types

#### Milestone Checker Tests (`test_milestone_checker.py`)

**11 tests** covering:
- Question Master bronze/silver achievements
- Highest tier only
- Speed Demon bronze achievement
- Week Warrior bronze (7 consecutive days)
- Not awarded below streak requirements
- Multiple milestone types in one check

#### Perfect Streak Achievement Tests (`test_perfect_streak_achievements.py`)

**6 tests** covering:
- Bronze for 3 perfect sessions
- Silver for 5 perfect sessions
- Streak broken by imperfect session
- Silver with bronze exists (only once)

#### Question Master Achievement Tests (`test_question_master_achievements.py`)

**5 tests** covering:
- Bronze for 100 questions
- Silver for 500 questions
- Gold for 1000 questions
- Only highest tier awarded

#### So Wow Achievement Tests (`test_so_wow_achievements.py`)

**7 tests** covering:
- Bronze for first bronze achievement
- Silver for first silver achievement
- Multiple tiers in one session
- Only awarded once per tier
- Not awarded if tier already exists
- Integration with session completion

#### So Wow Checker Tests (`test_so_wow_checker.py`)

**5 tests** covering:
- Awards So Wow for first tier achievement
- Doesn't award if user already has tier achievements
- Awards multiple tiers in one session
- Skips non-tiered achievements
- Doesn't duplicate So Wow achievements

#### Week Warrior Achievement Tests (`test_week_warrior_achievements.py`)

**4 tests** covering:
- Bronze for 7 consecutive days
- Silver for 14 consecutive days
- Streak broken by missing day

### Achievement Test Coverage Improvements

**Current Status:** Out of 107 total achievements, only 22 have explicit tests verifying they are granted. This means **85 achievements (79%) lack explicit granting verification tests**.

#### Priority 1: Completely Untested Achievement Types

These achievement types have NO tests verifying they're granted:

**Master of Times Tables** (11 tiers - ALL untested):
- `master-of-times-tables-bronze` through `master-of-times-tables-champion`
- Current status: Only config existence verified in `test_master_times_division_achievements.py`
- **Action Needed:** Add tests to verify granting logic for at least bronze tier, ideally multiple tiers

**Master of Division Tables** (11 tiers - ALL untested):
- `master-of-division-tables-bronze` through `master-of-division-tables-champion`
- Current status: Only config existence verified in `test_master_times_division_achievements.py`
- **Action Needed:** Add tests to verify granting logic for at least bronze tier, ideally multiple tiers

#### Priority 2: Missing Higher Tier Tests

The following achievement types need tests for higher tiers (platinum, diamond, master, grandmaster, legendary, mythic, divine, champion):

**Question Master** (8 missing tiers):
- Missing: `question-master-platinum`, `question-master-diamond`, `question-master-master`, `question-master-grandmaster`, `question-master-legendary`, `question-master-mythic`, `question-master-divine`, `question-master-champion`
- Current: bronze, silver, gold tested
- **Action Needed:** Add tests for at least platinum and champion tiers

**Speed Demon** (9 missing tiers):
- Missing: `speed-demon-silver`, `speed-demon-platinum`, `speed-demon-diamond`, `speed-demon-master`, `speed-demon-grandmaster`, `speed-demon-legendary`, `speed-demon-mythic`, `speed-demon-divine`, `speed-demon-champion`
- Current: bronze, gold tested (gold test checks for gold/platinum/diamond but doesn't verify specific tier)
- **Action Needed:** Add explicit test for silver tier, and tests for higher tiers

**Perfect Streak** (9 missing tiers):
- Missing: `perfect-streak-gold` through `perfect-streak-champion` (all higher tiers)
- Current: bronze, silver tested
- **Action Needed:** Add tests for gold, platinum, and champion tiers at minimum

**Week Warrior** (9 missing tiers):
- Missing: `week-warrior-gold` through `week-warrior-champion` (all higher tiers)
- Current: bronze, silver tested
- **Action Needed:** Add tests for gold, platinum, and champion tiers at minimum

**Lightning Fast** (9 missing tiers):
- Missing: `lightning-fast-gold` through `lightning-fast-champion` (all higher tiers)
- Current: bronze, silver tested
- **Action Needed:** Add tests for gold, platinum, and champion tiers at minimum

**Level Master** (9 missing tiers):
- Missing: `level-master-gold`, `level-master-platinum`, `level-master-diamond`, `level-master-master`, `level-master-grandmaster`, `level-master-legendary`, `level-master-mythic`, `level-master-divine`, `level-master-champion`
- Current: bronze, silver tested
- **Action Needed:** Add tests for gold tier explicitly, and higher tiers

**So Wow** (9 missing tiers):
- Missing: `so-wow-gold` through `so-wow-champion` (all higher tiers)
- Current: bronze, silver tested
- **Action Needed:** Add tests for gold, platinum, and champion tiers at minimum

#### Priority 3: Missing Specific Tier Tests

**Human Calculator Silver**:
- Missing: `human-calculator-silver`
- Current: `human-calculator` (bronze) tested
- **Action Needed:** Add test for silver tier

#### Test Strategy Recommendations

1. **Focus on Representative Tiers First:**
   - Test bronze (entry tier) for all achievement types
   - Test gold (middle tier) for verification of tier progression
   - Test champion (highest tier) for verification of champion eligibility and server records

2. **Use Test Data Helpers:**
   - Leverage `create_test_session_with_responses()` from `tests/helpers/data_helpers.py`
   - Use `award_achievement_directly()` for setup when needed
   - Create reusable fixtures for complex achievement requirements

3. **Test Pattern to Follow:**
   ```
   def test_[achievement-code]_granted(app, test_user):
       """Test that [achievement] is awarded when requirements are met."""
       # Setup: Create session/data that meets requirements
       # Action: Trigger achievement checking
       # Expect: Achievement with correct code is created and saved
   ```

4. **Consider Integration Tests:**
   - Some achievements (especially Master of Times/Division Tables) may require complex multi-session setups
   - Consider integration-style tests that verify the full flow rather than just unit tests

5. **Champion Tier Testing:**
   - Champion tier achievements require server record verification
   - Use `test_champion_validator.py` and `test_server_record_service.py` as reference
   - Test both when user qualifies for champion and when they don't

#### Estimated Test Coverage Goals

- **Short-term:** Add tests for all bronze tiers (covers entry-level achievements)
- **Medium-term:** Add tests for gold tier of each achievement type (verifies tier progression)
- **Long-term:** Add tests for champion tier of each achievement type (verifies highest tier and server records)

### Analytics Service Tests (`test_analytics_service.py`)

**44 tests** covering:
- Speed formatting (None and with value)
- Operation stats building (empty, with data, zero attempts, unknown operation)
- Consecutive run calculations (empty, single date, consecutive, with gaps, multiple streaks)
- Current run calculations (empty, today, yesterday, two days ago, consecutive ending today/yesterday, with gap)
- User metrics computation (no responses, with responses, multiple operations)
- Daily stats aggregation (single date, all dates, updating existing)
- Time series data (default range, date range, operation filter)
- Weekly gain calculations (no responses, this week only, last week only, both weeks)
- Batch processing (empty, single user, multiple users)
- Streaks calculation (using daily stats, fallback to responses)

### Champion Validator Tests (`test_champion_validator.py`)

**10 tests** covering:
- Returns false for non-Champion tier
- Returns false for non-qualifying achievements
- Sets record when no existing record
- Updates record when beating existing
- Returns false when not beating record
- Handles accuracy-based achievements
- Handles volume-based achievements
- Returns false when record value cannot be determined

### Complete Session XP Breakdown Tests (`test_complete_session_xp_breakdown.py`)

**6 tests** covering:
- Correct count matches session
- Counts unique questions only
- Cross-session isolation
- Uses latest response per question
- Multiplier delta calculation

### Concept Requirements Endpoint Tests (`test_concept_requirements_endpoint.py`)

**2 tests** covering:
- Enriches counts for descriptive concepts
- Uses explicit overrides for legacy concepts

### Level Up Eligibility Tests (`test_level_up_eligibility.py`)

**8 tests** covering:
- Requires all specified achievements for each level
- Cannot level up backwards
- Cannot level up to same level
- Level 1 has no requirements
- API endpoint success/failure
- Multiple requirements (level 5 requires multiple achievements with metadata)

### Levels Requirements Endpoint Tests (`test_levels_requirements_endpoint.py`)

**1 test** covering:
- Translates test_type to concept_id and enriches counts

### Session Engine Service Tests (`test_session_engine_service.py`)

**3 tests** covering:
- Generate session with concept_id returns concept_id and questions
- Default selects concept
- Selects only unlocked concepts

### Server Record Service Tests (`test_server_record_service.py`)

**19 tests** covering:
- Creating server records
- Getting current record (none exists, exists)
- Record model validation
- Champion tier record management

### Tier Substitution Tests (`test_tier_substitution.py`)

**5 tests** covering:
- Converting tier to base units
- Converting base units to tier count
- Extracting base code and tier
- Tier substitution conversion rates
- Counting achievements with tier substitution

### Tier Utils Comprehensive Tests (`test_tier_utils_comprehensive.py`)

**41 tests** covering comprehensive tier utility functions:
- Tier hierarchy retrieval
- All tiers retrieval
- Old tier mapping (B→bronze, A→silver, S→gold, SS→platinum, SSS→diamond)
- Tier comparison (higher than, case insensitive, unknown tiers)
- Tier value retrieval (case insensitive, unknown tiers)
- Highest tier selection (single, empty, case insensitive, unknown tiers)
- Tier to base units conversion (all tiers, unknown)
- Base units to tier count conversion (all tiers, unknown)
- Base code and tier extraction (with tier, no tier, longest first)
- Achievement counting with tier substitution (no tier, exact match, higher tier, multiple tiers, metadata filters, invalid JSON, different base codes)

### Coverage Baseline Test (`test_coverage_baseline.py`)

**1 test** - Dummy test to enable coverage collection

### Achievement Checkers Base Tests (`test_achievement_checkers_base.py`)

**5 tests** covering:
- Base checker is abstract
- Base checker has check method
- Concrete checker must implement check
- Concrete checker can be instantiated
- Concrete checker returns achievements list

## Frontend Tests

### Practice Hook Tests

#### usePracticeState Tests (`usePracticeState.test.ts`)

**16 tests** covering practice state management:
- Initializes with default state (empty problems, index 0, no feedback, etc.)
- Updates problems
- Updates currentQuestionIndex
- Updates userAnswer
- Updates feedback (correct, incorrect, null)
- Updates showAnswer
- Updates flaggedQuestions (object and function updates)
- Updates questionAnswers (object and function updates)
- Updates questionStartTimes
- Updates sessionId
- Updates sessionMode
- Updates sessionError
- Updates isLoadingProblems
- Resets state

#### usePracticeSession Tests (`usePracticeSession.test.ts`)

**12 tests** covering practice session management:
- Initializes session from URL params
- Loads incomplete session from localStorage
- Starts new session with API
- Handles session errors
- Loads session state from API
- Restores session from localStorage
- Handles navigation between questions
- Submits session
- Handles session completion

#### usePracticeAPI Tests (`usePracticeAPI.test.ts`)

**4 tests** covering practice API calls:
- startSession API call
- checkAnswer API call
- completeSession API call
- createSessionSummary API call
- Error handling for API failures

### Student/Learner Hook Tests

#### useLearners Tests (`useLearners.test.ts`)

**15 tests** covering learner management:
- Initializes with default state
- Sets selected user
- Clears selected user if user removed from list
- Shows/hides add user modal
- Filters by category
- Filters by level
- Loads users from API
- Handles loading states
- Handles errors
- Refetches users
- Fetches full user data

### Progress Mapping Utility Tests

#### achievementConverters Tests (`achievementConverters.test.ts`)

**2 tests** covering:
- Converting backend achievements to frontend format
- Handling achievement metadata and tier information

#### levelRequirementConverters Tests (`levelRequirementConverters.test.ts`)

**1 test** covering:
- Converting level requirements from backend to frontend format
- Handling concept IDs and requirement counts

#### testDisplayNames Tests (`testDisplayNames.test.ts`)

**5 tests** covering:
- Converting unknown test types by replacing dashes with spaces
- Converting known legacy test types
- Handling single-word test types
- Handling empty string
- Handling test types with multiple dashes

#### progressMapping/index Tests (`progressMapping/index.test.ts`)

**1 test** covering:
- Overall progress mapping functionality

### Test Mapping Utility Tests

#### testMapping/index Tests (`testMapping/index.test.ts`)

**1 test** covering:
- Mapping test definitions to frontend format
- Handling locked/unlocked status from unlock_status
- Determining unlocked status
- Setting attempt counts

#### testConverters Tests (`testConverters.test.ts`)

**5 tests** covering:
- Converting test definitions
- Handling test constraints
- Processing display names
- Managing unlock requirements

#### tierUtils Tests (`tierUtils.test.ts`)

**3 tests** covering:
- Tier utility functions
- Tier comparison logic
- Tier value calculations

### Practice Utility Tests

#### questionTransformers Tests (`questionTransformers.test.ts`)

**1 test** covering:
- Transforming questions from backend to frontend format
- Handling question layouts and formats

#### sessionReconstruction Tests (`sessionReconstruction.test.ts`)

**1 test** covering:
- Reconstructing session state from API data
- Rebuilding question arrays and responses

### Component Tests

#### EncouragementBanner Tests (`EncouragementBanner.test.tsx`)

**1 test** covering:
- Displaying encouragement messages
- Conditional rendering based on session performance

## E2E Tests

### Page Load Tests (`page-load.spec.ts`)

**4 tests** covering:
- Main dashboard page loads
- Practice page loads
- Summary page loads
- Test IDs present on interactive elements

### Learner Management Tests (`learner-management.spec.ts`)

**5 tests** covering:
- LM-001: Create new learner with valid name, avatar, PIN
- LM-002: Create learner validation (short name, wrong PIN)
- LM-003: Delete learner
- LM-004: Select learner by clicking card
- LM-005: Duplicate name prevention

### Dashboard Tests (`dashboard.spec.ts`)

**4 tests** covering:
- DASH-001: Dashboard loads with learner grid or "No learners yet" message
- DASH-002: Learner stats display when learner selected
- DASH-003: Start Practice button shows PIN modal
- DASH-004: PIN verification (incorrect PIN shows error, correct PIN navigates to practice)

### Practice Flow Tests (`practice-flow.spec.ts`)

**6 tests** covering:
- PRAC-001: Start practice session - verify practice page elements present
- PRAC-002: Answer question - enter answer and verify feedback shown
- PRAC-003: Navigate questions - use Next/Previous buttons
- PRAC-004: Flag question - flag a question for review
- PRAC-005: Progress indicator - verify progress bar updates as questions answered
- PRAC-006: Submit session - complete all questions and submit

### Practice Keyboard Tests

#### Start Practice Keyboard (`start-practice-keyboard.spec.ts`)

**Tests** covering keyboard interactions when starting practice:
- Keyboard navigation in PIN entry
- Keyboard shortcuts for starting practice

#### Practice Keyboard (`practice-keyboard.spec.ts`)

**Tests** covering keyboard interactions during practice:
- Keyboard input for answers
- Keyboard navigation between questions
- Keyboard shortcuts

### Session Submission Tests (`session-submission.spec.ts`)

**4 tests** covering:
- SUB-001: Submit practice session - complete session and verify submission
- SUB-002: Session accuracy calculation - verify correct accuracy shown
- SUB-003: Session time tracking - verify time is recorded
- SUB-004: Incomplete session handling - navigate away mid-session

### Test Flow Tests (`test-flow.spec.ts`)

**Tests** covering:
- TEST-001: Test eligibility check displays requirements
- TEST-002: Start eligible test
- Test session completion
- Test results display

### Tests Tab Tests (`tests-tab.spec.ts`)

**Tests** covering the tests/journey tab:
- Test definitions display
- Test eligibility indicators
- Test attempt tracking
- Test locking/unlocking

### Leveling Tests (`leveling.spec.ts`)

**Tests** covering level progression:
- Level up eligibility display
- Level up requirements
- Level progression after achievements
- Level unlock requirements

### Achievements Tests (`achievements.spec.ts`)

**10+ tests** covering:
- ACH-001: Milestone achievements display
- ACH-002: Accuracy achievements display
- ACH-003: Speed achievements display
- ACH-004: Consistency achievements display
- ACH-005: Test tier achievements display
- Achievement filtering by category
- Achievement status display (earned/locked)
- Achievement modal display

### Achievement Modal Tests (`achievement-modal.spec.ts`)

**Tests** covering:
- Achievement modal opens on achievement earned
- Achievement details display
- Modal closing/dismissal
- Multiple achievements in sequence

### Summary Page Tests (`summary-page.spec.ts`)

**Tests** covering:
- Summary page loads after session completion
- Session statistics display (accuracy, time, questions)
- Achievement notifications
- Navigation from summary page

### Summary New Best Tests (`summary-new-best.spec.ts`)

**Tests** covering:
- New best performance indicators
- Best streak display
- Best accuracy display
- Best speed display

### Journey Page Tests (`journey-page.spec.ts`)

**Tests** covering:
- Journey page navigation
- Progress tracking display
- Level progression visualization
- Achievement gallery
- Test progress display

### Dev Mode Tests (`dev-mode.spec.ts`)

**Tests** covering:
- Dev mode features (if applicable)
- Test setup utilities
- Debug information display

## Test Overlap and Redundancy Analysis

This section identifies tests that have overlapping coverage between backend, frontend, and E2E test suites. While some overlap is intentional (e.g., E2E tests verify integration), excessive redundancy can be inefficient and increase maintenance burden.

### PIN Verification Tests

**Backend Tests:**
- `test_user_service.py`: `test_verify_pin_correct`, `test_verify_pin_incorrect`
  - **Purpose:** Unit tests for `UserService.verify_pin()` method
  - **Coverage:** PIN matching logic (correct PIN returns True, incorrect returns False)

**E2E Tests:**
- `dashboard.spec.ts`: `DASH-004: PIN verification`
  - **Purpose:** E2E test of PIN verification flow through UI
  - **Coverage:** PIN modal interaction, incorrect PIN shows error, correct PIN navigates to practice

**Analysis:** ✅ **Justified Overlap**
- Backend tests verify the core logic (unit level)
- E2E test verifies the full user flow (integration level)
- Both are necessary: backend tests catch logic bugs, E2E tests catch UI/flow bugs
- **Recommendation:** Keep both, no redundancy

### User Creation/Learner Management Tests

**Backend Tests:**
- `test_user_service.py`: `test_create_user_basic`, `test_create_user_no_avatar`, `test_create_user_name_too_short`, `test_create_user_name_whitespace`, `test_create_user_pin_not_digits`, `test_create_user_pin_wrong_length`, `test_create_user_duplicate_name`
  - **Purpose:** Comprehensive unit tests for `UserService.create_user()` method
  - **Coverage:** All validation rules, edge cases, error handling

**E2E Tests:**
- `learner-management.spec.ts`: `LM-001: Create new learner`, `LM-002: Create learner validation`, `LM-005: Duplicate name prevention`
  - **Purpose:** E2E tests of user creation through UI
  - **Coverage:** UI flow, name/PIN validation visible to user, duplicate name prevention

**Analysis:** ✅ **Justified Overlap**
- Backend tests verify validation logic comprehensively (7 tests covering all validation rules)
- E2E tests verify UI behavior and user experience
- E2E tests don't exhaustively test all validation cases (e.g., whitespace trimming, exact PIN format rules)
- **Recommendation:** Keep both, but consider if E2E tests could reduce coverage if backend tests are comprehensive

### Session Submission/Completion Tests

**Backend Tests:**
- `test_complete_session_xp_breakdown.py`: 6 tests covering XP breakdown calculation
  - `test_xp_breakdown_correct_count_matches_session`
  - `test_xp_breakdown_counts_unique_questions_only`
  - `test_xp_breakdown_uses_latest_response_per_question`
  - `test_xp_breakdown_multiplier_delta_calculation`
  - Tests for cross-session isolation
  - **Purpose:** Verify XP calculation logic, multiplier calculations, question counting
  - **Coverage:** Detailed mathematical correctness of XP calculation

**E2E Tests:**
- `session-submission.spec.ts`: `SUB-001: Submit practice session`, `SUB-002: Session accuracy calculation`, `SUB-003: Session time tracking`, `SUB-004: Incomplete session handling`
- `practice-flow.spec.ts`: `PRAC-006: Submit session`
- `summary-page.spec.ts`: Multiple tests verifying summary page displays stats correctly
  - **Purpose:** Verify session submission flow works end-to-end
  - **Coverage:** UI flow, navigation to summary page, stats display

**Analysis:** ⚠️ **Partial Overlap - Consider Optimization**
- Backend tests focus on **calculation correctness** (XP math, multipliers, question counting)
- E2E tests focus on **user flow** (submission works, summary displays data)
- E2E tests don't verify XP calculation correctness in detail (they just verify stats appear)
- **Potential Redundancy:** `SUB-002` and `SUB-003` are somewhat redundant with summary page tests
- **Recommendation:**
  - ✅ Keep backend XP calculation tests (critical for correctness)
  - ✅ Keep E2E submission flow tests (critical for user experience)
  - ⚠️ Consider consolidating `SUB-002`/`SUB-003` into summary-page.spec.ts if they're just checking stats display
  - ⚠️ Consider if E2E tests should verify actual XP values match expected (currently just check that stats appear)

### Achievement Awarding Tests

**Backend Tests:**
- Extensive backend test suite (240+ tests) covering:
  - Individual achievement checkers (accuracy-ace, speed-demon, perfect-streak, etc.)
  - Achievement constraints (unique, tier progression)
  - Achievement service methods
  - Achievement orchestrator
  - **Purpose:** Verify achievement logic is correct
  - **Coverage:** Comprehensive coverage of achievement awarding logic

**E2E Tests:**
- `achievements.spec.ts`: Achievement display tests (`ACH-001` through `ACH-005`)
- `achievement-modal.spec.ts`: Achievement modal display tests
- `summary-page.spec.ts`: Achievement notifications on summary page
  - **Purpose:** Verify achievements appear in UI correctly
  - **Coverage:** UI display, filtering, modal behavior

**Analysis:** ✅ **Justified Overlap (Minimal)**
- Backend tests verify **awarding logic** (when achievements should be granted)
- E2E tests verify **display logic** (how achievements appear in UI)
- **No real overlap:** Backend tests don't verify UI, E2E tests don't verify awarding logic
- **Recommendation:** Keep both, they test different concerns

### Question Answering and Validation Tests

**Backend Tests:**
- `test_practice_service.py`: Tests for answer validation logic
  - **Purpose:** Verify answer checking logic is correct

**E2E Tests:**
- `practice-flow.spec.ts`: `PRAC-002: Answer question` - Verifies feedback shown
- **Purpose:** Verify UI shows feedback correctly

**Analysis:** ✅ **Justified Overlap**
- Backend tests verify validation logic
- E2E tests verify UI feedback display
- **Recommendation:** Keep both

### Test Flow (Test Sessions) Tests

**Backend Tests:**
- Limited backend tests for test session eligibility (`test_level_up_eligibility.py`)

**E2E Tests:**
- `test-flow.spec.ts`: `TEST-001`, `TEST-002`, `TEST-003`, `TEST-004`
  - Tests test session eligibility, starting tests, test submission
  - **Purpose:** E2E verification of test flow

**Analysis:** ⚠️ **Potential Gap**
- E2E tests have more coverage than backend tests for test sessions
- This may be intentional (E2E tests are integration tests), but suggests backend could have more unit tests
- **Recommendation:** Consider adding more backend unit tests for test session logic

### Summary: Redundant Tests

#### Tests with Potential Redundancy:

1. **Session Submission Stats Display:**
   - `session-submission.spec.ts`: `SUB-002` (accuracy calculation) and `SUB-003` (time tracking)
   - These verify stats appear on summary page
   - `summary-page.spec.ts` also tests summary page stats display
   - **Recommendation:** Consider consolidating into summary-page.spec.ts or making SUB-002/SUB-003 verify actual values match expected

2. **Practice Session Submission:**
   - `session-submission.spec.ts`: `SUB-001` (Submit practice session)
   - `practice-flow.spec.ts`: `PRAC-006` (Submit session)
   - Both test submitting a practice session
   - **Recommendation:** Review if both are necessary or if they test different aspects (e.g., SUB-001 focuses on submission flow, PRAC-006 focuses on completing session)

3. **Incomplete Session Handling:**
   - `session-submission.spec.ts`: `SUB-004` (Incomplete session handling with backend restoration)
   - `summary-page.spec.ts`: Tests for incomplete session restoration
   - **Analysis:** Both test incomplete session handling, but from different angles
   - **Recommendation:** Ensure they test different aspects (e.g., SUB-004 tests navigation away, summary-page tests restoration)

### Summary: Justified Overlap

The following overlaps are **justified and should be kept:**

1. ✅ **PIN Verification:** Backend (logic) vs E2E (flow) - different concerns
2. ✅ **User Creation:** Backend (validation) vs E2E (UI flow) - different concerns
3. ✅ **Achievement Awarding:** Backend (logic) vs E2E (display) - different concerns
4. ✅ **Question Validation:** Backend (logic) vs E2E (UI feedback) - different concerns
5. ✅ **Session Completion XP Calculation:** Backend (math correctness) vs E2E (user experience) - different concerns

### Recommendations for Optimization

1. **Review E2E Test Consolidation:**
   - Consider if `SUB-002` and `SUB-003` can be merged with summary-page tests
   - Review if `SUB-001` and `PRAC-006` serve different purposes or can be consolidated

2. **Enhance E2E Tests to Verify Values:**
   - Currently E2E tests often just verify that data appears, not that values are correct
   - Consider adding assertions that verify actual XP values, achievement codes, etc. match expected values
   - This would make E2E tests more valuable while still testing the full flow

3. **Add Backend Tests for Test Sessions:**
   - E2E tests have more coverage for test sessions than backend tests
   - Consider adding more backend unit tests for test session logic to improve test pyramid balance

4. **Document Test Boundaries:**
   - Clearly document what each test suite is responsible for
   - Backend: Logic correctness
   - Frontend: Component behavior and state management
   - E2E: User flows and integration

## Code Review

### Route: `/` - Learners Dashboard

#### Data Fetched:
- **Users/Learners List** - Fetched from `/api/users` via `useLearners` hook
  - Coverage: ✅ Frontend (useLearners tests), ✅ Backend (UserService tests), ✅ E2E (learner-management.spec.ts)
- **Recent Achievements (all learners)** - Fetched from `/api/achievements?limit=6` when no user selected
  - Coverage: ✅ Backend (AchievementQueryService tests), ⚠️ Frontend (limited), ⚠️ E2E (achievements.spec.ts covers user-specific)
- **Selected User Full Data** - Fetched when user selected from URL parameter
  - Coverage: ✅ Frontend (useLearners tests), ✅ Backend (UserService tests), ✅ E2E (dashboard.spec.ts)

#### Interactive Features:

1. **Add Learner Button** (`testid-add-learner-button`)
   - Opens AddLearnerModal
   - Coverage: ✅ Frontend (useLearners tests), ✅ Backend (UserService.create_user tests), ✅ E2E (LM-001, LM-002)

2. **Learner Grid** (`testid-student-grid`)
   - Displays all learners as cards
   - Click learner card to select (`testid-student-card-{id}`)
   - Coverage: ✅ Frontend (useLearners tests), ✅ E2E (LM-004, DASH-002)

3. **Selected User Display**
   - **Level Card** - Clickable, navigates to Journey page
     - Coverage: ✅ E2E (leveling.spec.ts)
   - **Stats Cards** - Displays user statistics
     - Coverage: ✅ Frontend (useLearners tests), ✅ E2E (DASH-002)

4. **Accuracy Chart**
   - Displays accuracy over time by operation
   - Level filter dropdown
   - Coverage: ⚠️ Frontend (limited), ⚠️ E2E (dashboard.spec.ts partial)

5. **Speed Chart**
   - Displays speed over time by operation
   - Level filter dropdown
   - Coverage: ⚠️ Frontend (limited), ⚠️ E2E (dashboard.spec.ts partial)

6. **Achievements List** (for selected user)
   - Displays recent achievements
   - Category filter (all, speed, consistency, milestone)
   - Coverage: ✅ Frontend (achievementConverters tests), ✅ Backend (AchievementQueryService tests), ✅ E2E (ACH-001 to ACH-005)

7. **Recent Achievements List** (when no user selected)
   - Displays most recent 6 achievements across all learners
   - Coverage: ✅ Backend (AchievementQueryService tests), ⚠️ Frontend (limited), ⚠️ E2E (limited)

8. **Start Practice Button** (`testid-start-practice-button`)
   - Opens PIN verification modal
   - Coverage: ✅ E2E (DASH-003, DASH-004, PRAC-001)

9. **PIN Verification Modal** (`testid-pin-display`)
   - Enter PIN via PinPad buttons
   - Verify PIN and navigate to practice
   - Coverage: ✅ E2E (DASH-004, start-practice-keyboard.spec.ts)

10. **Add Learner Modal**
    - Input fields: name, PIN (4 digits), avatar (optional)
    - Validation (name length, PIN format, duplicate name)
    - Coverage: ✅ Frontend (useLearners tests), ✅ Backend (UserService.create_user validation tests), ✅ E2E (LM-001, LM-002, LM-005)

11. **Dev Mode Features** (when `VITE_DEV_MODE=true`)
    - **Reset User Button** - Resets all user data to level 1
      - Coverage: ✅ Backend (API protection tests), ✅ E2E (dev-mode.spec.ts)
    - **Delete User Button** - Permanently deletes user
      - Coverage: ✅ Backend (API protection tests, UserService.delete_user tests), ✅ E2E (dev-mode.spec.ts, LM-003)

#### Features Summary:
- ✅ Frontend Test Coverage: Good (useLearners hooks, state management)
- ✅ Backend Test Coverage: Excellent (UserService, AchievementQueryService)
- ✅ E2E Test Coverage: Good (learner management, dashboard, PIN verification)

---

### Route: `/practice` - Practice Session Page

#### Data Fetched:
- **Learners List** - Via `useLearners` hook
  - Coverage: ✅ Frontend (useLearners tests), ✅ Backend (UserService tests), ✅ E2E
- **Session Start/Resume** - POST to `/api/practice/sessions/start`
  - Returns: sessionId, problems, sessionState
  - Coverage: ✅ Frontend (usePracticeAPI.startSession tests), ✅ Backend (PracticeService tests), ✅ E2E (PRAC-001)
- **Check Answer** - POST to `/api/practice/sessions/{sessionId}/check`
  - Returns: isCorrect, feedback
  - Coverage: ✅ Frontend (usePracticeAPI.checkAnswer tests), ✅ Backend (PracticeService.validate_answer tests), ✅ E2E (PRAC-002)
- **Complete Session** - POST to `/api/practice/sessions/{sessionId}/complete`
  - Returns: summary data, achievements, level up info
  - Coverage: ✅ Frontend (usePracticeAPI.completeSession tests), ✅ Backend (PracticeService.complete_session tests), ✅ E2E (PRAC-006, SUB-001)

#### Interactive Features:

1. **Practice Header**
   - User info display
   - Progress indicator (`testid-progress-bar`)
   - Coverage: ✅ E2E (PRAC-005)

2. **Question Display**
   - Shows current question with operation, operands
   - Supports different layouts: vertical, partial products, long division
   - Coverage: ✅ Frontend (usePracticeSession tests), ✅ E2E (PRAC-001, PRAC-002)

3. **Answer Input** (`testid-answer-input`)
   - Text input for answer
   - Keyboard input support
   - Coverage: ✅ Frontend (usePracticeState tests), ✅ E2E (PRAC-002, practice-keyboard.spec.ts)

4. **Check Answer Button** (`testid-check-answer-button`)
   - Submits answer for validation
   - Shows feedback (correct/incorrect)
   - Coverage: ✅ Frontend (usePracticeSession tests), ✅ Backend (PracticeService.validate_answer tests), ✅ E2E (PRAC-002)

5. **Feedback Display**
   - Shows if answer is correct or incorrect
   - Shows correct answer when incorrect
   - Coverage: ✅ Frontend (usePracticeState tests), ✅ E2E (PRAC-002)

6. **Flag Question Button** (`testid-flag-button`)
   - Flags question for review
   - Toggle flag state
   - Coverage: ✅ Frontend (usePracticeState tests), ✅ Backend (PracticeService.flag_question tests), ✅ E2E (PRAC-004)

7. **Navigation Buttons**
   - **Next Button** (`testid-next-button`) - Move to next question
   - **Previous Button** (`testid-previous-button`) - Move to previous question
   - Coverage: ✅ Frontend (usePracticeSession tests), ✅ E2E (PRAC-003, practice-keyboard.spec.ts)

8. **Progress Bar** (`testid-progress-bar`)
   - Shows progress through session (question X of Y)
   - Updates as questions are answered
   - Coverage: ✅ E2E (PRAC-005)

9. **Card Counter Display**
   - Shows "Card X of Y" format
   - Coverage: ✅ Frontend (usePracticeSession tests), ⚠️ E2E (limited)

10. **Submit Session Button** (`testid-submit-session-button`)
    - Completes session and navigates to summary
    - Only enabled when all questions answered
    - Coverage: ✅ Frontend (usePracticeSession tests), ✅ Backend (PracticeService.complete_session tests), ✅ E2E (PRAC-006, SUB-001)

11. **Session Error Display**
    - Shows error messages if session fails to load
    - Coverage: ✅ Frontend (usePracticeSession tests), ⚠️ E2E (limited)

12. **Keyboard Navigation**
    - Enter to check answer
    - Arrow keys for navigation
    - Coverage: ✅ E2E (practice-keyboard.spec.ts, start-practice-keyboard.spec.ts)

13. **Resume Incomplete Session**
    - Automatically resumes oldest incomplete session when starting from dashboard
    - Loads existing answers and state
    - Coverage: ✅ Backend (PracticeService.get_incomplete_session tests), ⚠️ E2E (limited)

14. **Concept-Based Practice**
    - Navigate with conceptId parameter
    - Practice specific math concept
    - Coverage: ✅ Backend (SessionEngineService tests), ⚠️ E2E (limited)

#### Features Summary:
- ✅ Frontend Test Coverage: Excellent (usePracticeState, usePracticeSession, usePracticeAPI)
- ✅ Backend Test Coverage: Excellent (PracticeService, QuestionService)
- ✅ E2E Test Coverage: Good (practice flow, keyboard interactions, session submission)

---

### Route: `/summary` - Practice Session Summary Page

#### Data Fetched:
- **Session Summary** - From localStorage (`lastPracticeSession`) or URL parameter (`sessionId`)
  - Contains: user info, attempts, achievements, level up info
  - Coverage: ✅ Frontend (useSummaryData tests), ✅ E2E (SUB-001, summary-page.spec.ts)

#### Interactive Features:

1. **Summary Header**
   - Student name and level display
   - Back to Dashboard button
   - Coverage: ✅ E2E (summary-page.spec.ts)

2. **Encouragement Banner**
   - Motivational message based on performance
   - Coverage: ✅ Frontend (EncouragementBanner.test.tsx), ✅ E2E (summary-page.spec.ts)

3. **Summary Stats Cards**
   - Accuracy percentage
   - Total time
   - Total problems
   - Coverage: ✅ E2E (SUB-002, SUB-003, summary-page.spec.ts)

4. **XP Earnings Breakdown**
   - Shows XP breakdown (correct count, multipliers)
   - Coverage: ✅ Backend (complete_session_xp_breakdown tests), ⚠️ Frontend (limited), ⚠️ E2E (limited)

5. **Performance by Difficulty**
   - Chart showing performance breakdown by difficulty level
   - Coverage: ⚠️ Frontend (limited), ⚠️ E2E (limited)

6. **Achievements Section**
   - Displays achievements earned in session
   - Achievement cards with animations
   - Coverage: ✅ E2E (ACH-001 to ACH-005, achievement-modal.spec.ts, summary-page.spec.ts)

7. **Session Stats**
   - Additional session statistics
   - Coverage: ⚠️ Frontend (limited), ⚠️ E2E (limited)

8. **Problem Grid**
   - Filter buttons: All, Correct, Incorrect, Flagged
   - Displays all problems from session
   - Click problem to view details
   - Coverage: ✅ E2E (summary-page.spec.ts)

9. **Problem Detail Modal**
   - Shows detailed view of selected problem
   - Shows user answer, correct answer, time spent
   - Coverage: ⚠️ Frontend (limited), ⚠️ E2E (limited)

10. **Level Up Celebration Modal**
    - Shows when user levels up
    - Displays new level and achievements
    - Coverage: ✅ E2E (summary-page.spec.ts, leveling.spec.ts)

11. **Action Buttons**
    - **Back to Dashboard** - Navigate to dashboard
    - **Practice Again** - Start new practice session
    - **Try Next Level** - Navigate to concepts tab with unlocked filter
    - **Review Flagged** - Filter to show flagged problems
    - Coverage: ✅ E2E (summary-page.spec.ts)

12. **New Best Indicators**
    - Shows when new best accuracy/speed achieved
    - Coverage: ✅ E2E (summary-new-best.spec.ts)

#### Features Summary:
- ✅ Frontend Test Coverage: Good (EncouragementBanner, useSummaryData)
- ✅ Backend Test Coverage: Good (complete_session_xp_breakdown, session completion)
- ✅ E2E Test Coverage: Good (summary page, achievement modal, level up)

---

### Route: `/journey/:userId` - Journey/Progress Page

#### Data Fetched:
- **User Full Data** - Fetched on mount via `fetchUserFullData`
  - Coverage: ✅ Frontend (useLearners tests), ✅ Backend (UserService tests), ✅ E2E (journey-page.spec.ts)
- **Level Requirements** - Lazy loaded via `useLevelRequirements`
  - Coverage: ✅ Backend (LevelProgression tests, levels_requirements_endpoint tests), ⚠️ Frontend (limited), ✅ E2E (leveling.spec.ts)
- **Achievement Definitions** - Via `useAchievementDefinitions`
  - Coverage: ✅ Backend (AchievementQueryService tests), ⚠️ Frontend (limited), ✅ E2E (achievements.spec.ts)

#### Interactive Features:

1. **Journey Header**
   - User name and avatar
   - Back button to dashboard
   - Coverage: ✅ E2E (journey-page.spec.ts)

2. **Journey Stats Overview**
   - Unlocked achievements count
   - Total achievements count
   - Unlocked concepts count
   - Total concepts count
   - In-progress achievements count
   - Coverage: ⚠️ Frontend (limited), ⚠️ E2E (limited)

3. **Tab Navigation** (`testid-journey-tab-{tabId}`)
   - **Overview Tab** - Recent achievements overview
   - **Achievements Tab** - All achievements with filters
   - **Math Concepts Tab** - Math concept practice options
   - Coverage: ✅ E2E (journey-page.spec.ts, tests-tab.spec.ts)

#### Tab: Overview (`/journey/:userId/overview`)

1. **Recent Achievements Section** (`testid-recent-achievements`)
   - Displays 6 most recent unlocked achievements
   - Achievement cards with status
   - Coverage: ✅ E2E (ACH-001 to ACH-005)

2. **View All Achievements Button** (`testid-view-all-achievements-button`)
   - Navigates to Achievements tab
   - Coverage: ✅ E2E (journey-page.spec.ts)

3. **Dev Mode: Reset User Button** (when enabled)
   - Resets all user data
   - Coverage: ✅ Backend (API protection tests), ✅ E2E (dev-mode.spec.ts)

#### Tab: Achievements (`/journey/:userId/achievements`)

1. **Category Filter** (`testid-achievement-filter-category`)
   - Options: All, Milestones, Accuracy, Progression, Consistency, Speed, Test, Test Mastery
   - Coverage: ✅ E2E (ACH-001 to ACH-005)

2. **Status Filter** (`testid-achievement-filter-status`)
   - Options: All, Unlocked, In Progress, Locked
   - Coverage: ✅ E2E (achievements.spec.ts)

3. **Search Input** (`testid-achievement-search-input`)
   - Text search for achievements
   - Coverage: ⚠️ E2E (limited)

4. **Achievement Grid** (`testid-achievements-grid`)
   - Displays all filtered achievements as cards
   - Click achievement card to view details
   - Coverage: ✅ E2E (ACH-001 to ACH-005, achievement-modal.spec.ts)

5. **Achievement Detail Modal**
   - Shows achievement details, requirements, progress
   - Deep linking support via URL parameter (`?achievement=code`)
   - Coverage: ✅ E2E (achievement-modal.spec.ts)

#### Tab: Math Concepts (`/journey/:userId/concepts`)

1. **Status Filter** (URL query: `?status={status}`)
   - Options: all, locked, unlocked, attempted
   - Default: unlocked
   - Updates URL on change
   - Coverage: ⚠️ E2E (limited)

2. **Text Search Filter**
   - Search concepts by display name or concept ID
   - Coverage: ⚠️ E2E (limited)

3. **Concept Cards** (`testid-concept-card-{conceptId}`)
   - Display concept info: name, description, unlock status
   - Shows attempt count and progress
   - Click to view details
   - Coverage: ⚠️ E2E (limited)

4. **Concept Detail Modal**
   - Shows concept details and requirements
   - **Start Practice Button** - Opens PIN modal then starts concept practice
   - Coverage: ⚠️ E2E (limited)

5. **PIN Verification Modal**
   - Enter PIN to start concept practice
   - Coverage: ✅ E2E (PIN verification in dashboard tests)

#### Features Summary:
- ✅ Frontend Test Coverage: Good (progress mapping utilities, achievement converters)
- ✅ Backend Test Coverage: Excellent (UserService, AchievementQueryService, LevelProgression, Concepts)
- ✅ E2E Test Coverage: Good (journey page, achievements, leveling, concepts partial)

---

### Cross-Route Features

1. **Navigation/Routing**
   - URL-based navigation with query parameters
   - Back button support
   - Coverage: ✅ E2E (page-load.spec.ts, navigation in all specs)

2. **Loading States**
   - Loading indicators during data fetch
   - Coverage: ✅ Frontend (hook tests), ✅ E2E (page-load.spec.ts)

3. **Error Handling**
   - Error messages for failed API calls
   - Retry mechanisms
   - Coverage: ✅ Frontend (API hook tests), ⚠️ E2E (limited)

4. **LocalStorage Usage**
   - Stores last practice session (`lastPracticeSession`)
   - Stores incomplete session state for resume
   - Coverage: ✅ Frontend (usePracticeSession tests), ⚠️ E2E (limited)

---

### Overall Test Coverage Summary

**Frontend Unit Tests:**
- ✅ Excellent: Practice hooks (usePracticeState, usePracticeSession, usePracticeAPI)
- ✅ Good: Learner hooks (useLearners)
- ✅ Good: Utility functions (progress mapping, test mapping, achievement converters)
- ✅ Improved: Component rendering tests (EncouragementBanner, XPEarningsBreakdown, ProblemDetailModal)
- ⚠️ Limited: Additional component tests (charts, other summary components)

**Backend Tests:**
- ✅ Excellent coverage across all services and endpoints
- ✅ Comprehensive achievement system tests
- ✅ Recent enhancements: Achievement XP Service tests expanded (+65 tests), XP breakdown endpoint tests added (+4 tests)

---

## Test Suite Enhancement Summary (Recent Changes)

This section documents the enhancements made to the test suite based on TEST_REVIEW.md analysis.

### Backend Test Enhancements

#### Achievement XP Service Tests (test_achievement_xp_service.py)
- **Added**: Comprehensive test coverage for all 16 achievement base types in ACHIEVEMENT_XP_TABLE
- **Added**: Tests for achievements with multipliers (level-master, lightning-fast, question-master, speed-demon, perfect-streak, week-warrior, accuracy-ace)
- **Added**: Tests for achievements without multipliers (so-wow, level-grandmaster, human-calculator, master-of-times-tables, master-of-division-tables, master-of-basic-addition, master-of-basic-subtraction)
- **Added**: Multiplier factor-to-delta conversion tests
- **Added**: Parametrized tier progression tests for level-master, accuracy-ace, and so-wow
- **Result**: Expanded from 3 tests to 68 tests

#### XP Breakdown Endpoint Tests (test_complete_session_xp_breakdown.py)
- **Added**: `test_xp_breakdown_base_xp_calculation` - Verifies base_xp = correct_count * xp_per_correct
- **Added**: `test_xp_breakdown_bonus_xp_only_no_multiplier` - Tests XP calculation with bonus XP only
- **Added**: `test_xp_breakdown_multiple_achievements_multiplier_and_bonus` - Tests combined multipliers and bonus XP
- **Added**: `test_xp_breakdown_session_only_achievements_contribute` - Verifies only session achievements contribute to XP
- **Result**: Added 4 new comprehensive XP calculation tests

#### Master Tables Achievement Tests
- **Updated**: Added documentation note that checker implementation is still pending
- **Status**: Config verification tests remain; actual granting tests pending checker implementation

### Frontend Test Enhancements

#### XPEarningsBreakdown Component Tests (XPEarningsBreakdown.test.tsx)
- **Added**: Test coverage for XP breakdown display component
- **Tests**: Null handling, base XP display, multiplier display, bonus XP display, complete breakdown, edge cases
- **Result**: Added 10 new component tests

#### ProblemDetailModal Component Tests (ProblemDetailModal.test.tsx)
- **Added**: Test coverage for problem detail modal component
- **Tests**: Rendering, correct/incorrect answer display, operation symbols, flagged indicator, user interactions
- **Result**: Added 9 new component tests

### E2E Test Consolidation

#### Removed Redundant Tests
- **Removed**: `PRAC-006` (practice-flow.spec.ts) - Redundant with SUB-001; only verified submit button enabled state
- **Consolidated**: `SUB-002` and `SUB-003` (session-submission.spec.ts) into `SUM-002` (summary-page.spec.ts)
  - SUB-002 (accuracy calculation) and SUB-003 (time tracking) merged into single comprehensive stats display test
- **Result**: Reduced E2E test count from 118 to ~115 while maintaining coverage

#### Enhanced Tests
- **Enhanced**: `SUM-002` now verifies both accuracy and time stats display (previously separate tests)

### Coverage Improvements

**Backend:**
- Line coverage: 77.21% (up from 77.11%)
- Test count: 579 tests (up from ~240, includes parametrized tests)

**Frontend:**
- Test files: 16 (up from 14)
- Test cases: 216 (up from 64)
- Component test coverage improved with new tests for XPEarningsBreakdown and ProblemDetailModal

### Files Modified

**Backend:**
- `backend/tests/test_achievement_xp_service.py` - Completely rewritten with comprehensive coverage
- `backend/tests/test_complete_session_xp_breakdown.py` - Added 4 new XP calculation tests
- `backend/tests/test_master_times_division_achievements.py` - Added documentation note

**Frontend:**
- `frontend/src/features/practice/components/summary/XPEarningsBreakdown.test.tsx` - New file
- `frontend/src/features/practice/components/summary/ProblemDetailModal.test.tsx` - New file
- `frontend/e2e/session-submission.spec.ts` - Removed SUB-002 and SUB-003
- `frontend/e2e/practice-flow.spec.ts` - Removed PRAC-006
- `frontend/e2e/summary-page.spec.ts` - Enhanced SUM-002

### Remaining Work

1. **Backend Coverage Target**: Currently 77.21%, target is ≥80%. Need to identify and test low-coverage modules.
2. **Master Tables Achievements**: Checker implementation needed for master_of_times_tables and master_of_division_tables requirement types.
3. **Frontend Component Tests**: Additional component tests could be added for charts (AccuracyChart, SpeedChart) and other summary components.
4. **E2E Test Stability**: Consider further reduction of waitForTimeout calls in favor of more deterministic waits.
- ✅ Full API endpoint coverage

**E2E Tests:**
- ✅ Excellent: Practice flow, session submission, learner management
- ✅ Good: Dashboard, achievements, leveling, journey page
- ⚠️ Partial: Concepts tab, detailed stats displays, error scenarios

