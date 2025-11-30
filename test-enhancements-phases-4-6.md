# E2E Test Implementation Plan - Phases 4-6: Backend & Distribution Testing

This plan addresses backend validation for Achievement Awarding, Level Up Eligibility, and Question Distribution verification. Each phase includes specific file paths, detailed implementation steps, and code changes.

**Prerequisites**: Complete Step 0 before starting Phase 4, as it provides the test setup infrastructure needed for backend tests.

---

## Step 0: Create Test Setup Infrastructure

**Goal**: Create helper functions and backend endpoints to set up test users in specific states (levels, achievements) for backend testing.

### Step 0.1: Backend Test Setup Endpoint (Already in Plan for Phases 1-3)

**File**: `backend/app/routes.py`

- The `/api/users/<id>/test-setup` endpoint created in Step 0.1 of phases 1-3 can be reused for backend tests
- Backend tests can also directly manipulate the database using test fixtures
- For Phase 4-5, we'll use both approaches: direct DB manipulation for speed, API endpoints when needed

### Step 0.2: Backend Test Helper Functions

**File**: Create `backend/tests/helpers/test_data_helpers.py`

1. **Create helper to award achievement directly in tests**:
   ```python
   from app.models import Achievement, db
   from datetime import datetime
   
   def award_achievement_directly(user_id: int, achievement_code: str, earned_at: datetime = None):
       """Award achievement directly without checking requirements (for testing)."""
       existing = Achievement.query.filter_by(
           user_id=user_id,
           code=achievement_code
       ).first()
       
       if not existing:
           achievement = Achievement(
               user_id=user_id,
               code=achievement_code,
               earned_at=earned_at or datetime.utcnow()
           )
           db.session.add(achievement)
           db.session.commit()
           return achievement
       return existing
   ```

2. **Create helper to set user level directly**:
   ```python
   from app.models import User
   
   def set_user_level_directly(user_id: int, level: int):
       """Set user level directly without checking requirements (for testing)."""
       user = User.query.get(user_id)
       if user:
           user.level = level
           user.updated_at = datetime.utcnow()
           db.session.commit()
           return user
       return None
   ```

3. **Create helper to create test session with responses**:
   ```python
   from app.models import PracticeSession, Response, Question, db
   
   def create_test_session_with_responses(
       user_id: int,
       responses_data: list[dict],
       mode: str = "standard",
       level: int = 1,
       is_test: bool = False
   ) -> PracticeSession:
       """Create a practice session with responses for testing."""
       session = PracticeSession(
           user_id=user_id,
           mode=mode,
           level=level,
           is_test=is_test
       )
       db.session.add(session)
       db.session.flush()
       
       for resp_data in responses_data:
           question = Question.query.get(resp_data['question_id'])
           if not question:
               continue
           response = Response(
               session_id=session.id,
               user_id=user_id,
               question_id=question.id,
               submitted_answer=resp_data.get('answer', ''),
               is_correct=resp_data.get('is_correct', False),
               duration_ms=resp_data.get('duration_ms', 3000),
               answered_at=resp_data.get('answered_at', datetime.utcnow())
           )
           db.session.add(response)
       
       session.completed_at = datetime.utcnow()
       db.session.commit()
       return session
   ```

4. **Create helper to create test questions**:
   ```python
   def create_test_questions(
       count: int,
       level: int,
       operation: str = "addition"
   ) -> list[Question]:
       """Create test questions for achievement testing."""
       questions = []
       for i in range(count):
           question = Question(
               operation=operation,
               operand1=1 + i,
               operand2=1,
               correct_answer=str(2 + i),
               prompt=f"{1+i} + 1",
               required_level=level,
               level_tag=f"Level {level}"
           )
           db.session.add(question)
           questions.append(question)
       db.session.commit()
       return questions
   ```

---

## Phase 4: Achievement Awarding Validation (Backend Testing)

**Goal**: Validate achievements are correctly awarded. Create backend-focused tests.

### Step 4.1: Create Backend Test File Structure

**File**: Create `backend/tests/test_achievements_awarding.py`

1. **Create test file with structure**:
   ```python
   import pytest
   from datetime import datetime, timedelta
   from app import create_app, db
   from app.models import User, PracticeSession, Response, Question
   from app.services.achievement_service import AchievementService
   
   @pytest.fixture
   def app():
       app = create_app(testing=True)
       with app.app_context():
           db.create_all()
           yield app
           db.drop_all()
   
   @pytest.fixture
   def test_user(app):
       with app.app_context():
           user = User(display_name="TestUser", pin="1234", avatar="🐯")
           db.session.add(user)
           db.session.commit()
           return user
   ```


### Step 4.2: Implement Test Setup Helpers

**File**: `backend/tests/test_achievements_awarding.py`

1. **Add helper function to create practice session with responses**:
   ```python
   def create_session_with_responses(user_id, responses_data):
       """Create a practice session with responses for testing."""
       session = PracticeSession(user_id=user_id, mode="standard", level=1, is_test=False)
       db.session.add(session)
       db.session.flush()
       
       for resp_data in responses_data:
           question = Question.query.filter_by(id=resp_data['question_id']).first()
           if not question:
               continue
           response = Response(
               session_id=session.id,
               user_id=user_id,
               question_id=question.id,
               submitted_answer=resp_data['answer'],
               is_correct=resp_data['is_correct'],
               duration_ms=resp_data.get('duration_ms', 3000)
           )
           db.session.add(response)
       
       session.completed_at = datetime.utcnow()
       db.session.commit()
       return session
   ```

2. **Add helper to create questions for testing**:
   ```python
   def create_test_questions(count, level, operation="addition"):
       """Create test questions for achievement testing."""
       questions = []
       for i in range(count):
           question = Question(
               operation=operation,
               operand1=1 + i,
               operand2=1,
               correct_answer=str(2 + i),
               prompt=f"{1+i} + 1",
               required_level=level,
               level_tag=f"Level {level}"
           )
           db.session.add(question)
           questions.append(question)
       db.session.commit()
       return questions
   ```


### Step 4.3: Implement Achievement Test Cases

**Complete List of Achievements Requiring Tests** (organized by category):

#### 4.3.1: Milestone Achievement Tests

1. **`first-victory`** (`test_first_victory_achievement`):
   - Requirement: Answer 1 question
   - Test: Create 1 response (correct or incorrect), verify achievement awarded

2. **`first-steps`** (`test_first_steps_achievement`):
   - Requirement: Complete 10 addition problems at level 1
   - Test: Create session with 10 addition questions at level 1, all answered, verify achievement

3. **`century`** (`test_century_achievement`):
   - Requirement: Answer 100+ questions total
   - Test: Create multiple sessions totaling 100+ responses, verify achievement

#### 4.3.2: Accuracy Achievement Tests

1. **`addition-basics`**: Level 1, 80%+ accuracy, 10+ questions
2. **`subtraction-basics`**: Level 3, 80%+ accuracy, 10+ questions
3. **`double-addition`**: Level 5, 80%+ accuracy, 10+ questions
4. **`double-subtraction`**: Level 6, 80%+ accuracy, 10+ questions
5. **`triple-subtraction`**: Level 22, 80%+ accuracy, 10+ questions
6. **`divide-by-one`**: Level 25, 80%+ accuracy, 10+ questions
7. **`division-double-remainder`**: Level 38, 80%+ accuracy, 10+ questions
8. **`division-double-fraction`**: Level 40, 80%+ accuracy, 10+ questions
9. **`division-triple-fraction`**: Level 41, 80%+ accuracy, 10+ questions
10. **`division-double-decimal`**: Level 44, 80%+ accuracy, 10+ questions
11. **`accuracy-ace`**: 95%+ accuracy for any operation, 20+ questions

**Test Pattern for Accuracy Achievements**:
```python
def test_accuracy_achievement(app, test_user, achievement_code, level, min_accuracy, min_questions):
    """Generic test for accuracy achievements."""
    # Create questions at specified level
    questions = create_test_questions(min_questions + 2, level)
    
    # Create responses with target accuracy
    correct_count = int(min_questions * min_accuracy)
    responses_data = []
    for i, q in enumerate(questions[:min_questions]):
        is_correct = i < correct_count
        responses_data.append({
            'question_id': q.id,
            'answer': q.correct_answer if is_correct else '999',
            'is_correct': is_correct,
            'duration_ms': 3000
        })
    
    # Create session and verify achievement
    create_test_session_with_responses(test_user.id, responses_data, level=level)
    AchievementService.check_and_award_achievements(test_user.id)
    # Verify achievement awarded
```

#### 4.3.3: Speed Achievement Tests

**Fast Session Achievements** (average time per question for a single session):
1. **`fast-session-bronze`**: Avg < 5.0s, 10+ questions
2. **`fast-session-silver`**: Avg < 4.0s, 10+ questions
3. **`fast-session-gold`**: Avg < 3.0s, 10+ questions
4. **`fast-session-platinum`**: Avg < 2.5s, 10+ questions
5. **`fast-session-diamond`**: Avg < 2.0s, 10+ questions
6. **`fast-session-champion`**: Avg < 1.5s, 10+ questions

**Fast Question Achievements** (consecutive questions with average time):
1. **`fast-question-bronze`**: 10 consecutive, avg < 4.0s
2. **`fast-question-silver`**: 15 consecutive, avg < 3.5s
3. **`fast-question-gold`**: 20 consecutive, avg < 3.0s
4. **`fast-question-platinum`**: 25 consecutive, avg < 2.5s
5. **`fast-question-diamond`**: 30 consecutive, avg < 2.0s
6. **`fast-question-champion`**: 50 consecutive, avg < 1.5s

**Other Speed Achievements**:
7. **`speed-demon`**: Average response time under 3 seconds (global), 10+ questions

#### 4.3.4: Consistency Achievement Tests

**Streak Achievements** (consecutive days with practice):
1. **`streak-2`**: 2 consecutive days
2. **`streak-3`**: 3 consecutive days
3. **`streak-5`**: 5 consecutive days
4. **`streak-10`**: 10 consecutive days
5. **`perfect-week`**: 7 consecutive days (same as streak-7)

**Perfect Sessions Achievements** (consecutive sessions with 100% accuracy):
1. **`perfect-sessions-2`**: 2 consecutive perfect sessions
2. **`perfect-sessions-4`**: 4 consecutive perfect sessions
3. **`perfect-sessions-8`**: 8 consecutive perfect sessions
4. **`perfect-sessions-16`**: 16 consecutive perfect sessions

#### 4.3.5: Progression Achievement Tests

1. **`level-2-mastery`**: 4 sessions with 90%+ accuracy AND 10 consecutive correct at level 2
2. **`mixed-addition`**: Level 2, 20 correct answers
3. **`mixed-subtraction`**: Level 4, 20 correct answers
4. **`multiply-by-one`**: Level 7, 30 correct answers
5. **`triple-addition`**: Level 8, 50 correct answers
6. **`multiplication-work`**: (Check progression.py for details)

#### 4.3.6: Level Mastery Achievement Tests

Level Mastery achievements (levels 5-25): Each requires:
- 90%+ accuracy for the level
- 15+ questions at that level
- 50 consecutive correct answers at that level

1. **`level-5-mastery`** through **`level-25-mastery`**: 21 total achievements
   - Levels: 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25

#### 4.3.7: Test Achievement Tests

**Test Completion Achievements** (complete specific tests with 90%+ accuracy):
- `multiply-by-two` through `multiply-by-twelve` (multiplication tables 1-12)
- `divide-by-two` through `divide-by-twelve` (division tables 1-12)
- `basic-math-test`: 50 problems covering levels 1-4, 80%+ accuracy

**Test Tier Achievements** (complete tests with specific tiers):
- For each multiplication test (1-12): `multiply-by-{N}-test-{tier}` where tier is b, a, s, ss, sss
- For each division test (1-12): `divide-by-{N}-test-{tier}` where tier is b, a, s, ss, sss
- Tier requirements vary by tier (B, A, S, SS, SSS)

**Special Test Achievements**:
- `multiplication-mastery`: Complete all multiplication tests 1-12 with Rank S
- `addition-mastery`, `subtraction-mastery`, etc. (check test.py for all)

**Note**: Test achievements require creating test sessions via `SessionEngineService.generate_session` with `is_test=True` and specific `test_type` values. Use helper functions to create test attempts with specific accuracy/tier results.

### Step 4.4: Test Setup Strategies for Complex Achievements

**File**: `backend/tests/test_achievements_awarding.py`

1. **For speed achievements**, create helper:
   ```python
   def create_speed_session(user_id, avg_time_seconds, question_count=10):
       """Create session with specific average response time."""
       questions = create_test_questions(question_count, 1)
       responses = []
       for q in questions:
           responses.append({
               'question_id': q.id,
               'answer': q.correct_answer,
               'is_correct': True,
               'duration_ms': int(avg_time_seconds * 1000)
           })
       return create_session_with_responses(user_id, responses)
   ```

2. **For consecutive achievements**, create helper:
   ```python
   def create_consecutive_correct_responses(user_id, count, level):
       """Create consecutive correct responses for consecutive achievements."""
       questions = create_test_questions(count, level)
       sessions = []
       current_session_responses = []
       
       for q in questions:
           current_session_responses.append({
               'question_id': q.id,
               'answer': q.correct_answer,
               'is_correct': True,
               'duration_ms': 2000
           })
           # Create new session every 10 questions
           if len(current_session_responses) == 10:
               sessions.append(create_session_with_responses(user_id, current_session_responses))
               current_session_responses = []
       
       if current_session_responses:
           sessions.append(create_session_with_responses(user_id, current_session_responses))
       
       return sessions
   ```

3. **For streak achievements**, create helper:
   ```python
   def create_streak_sessions(user_id, days):
       """Create practice sessions on consecutive days."""
       sessions = []
       for i in range(days):
           date = datetime.utcnow() - timedelta(days=days-i-1)
           session = PracticeSession(
               user_id=user_id,
               mode="standard",
               level=1,
               is_test=False,
               created_at=date,
               completed_at=date
           )
           db.session.add(session)
           sessions.append(session)
       db.session.commit()
       return sessions
   ```

4. **For high-level test achievements**, create helper:
   ```python
   def create_test_attempt_directly(user_id, level, accuracy, test_type):
       """Create test attempt directly without leveling up user."""
       # Use API or direct database creation to make test attempt
       # Set user level to required level temporarily
       # Create test session with specific accuracy
       # Restore user level
       pass
   ```


---

## Phase 5: Level Up Eligibility Validation (Backend Testing)

**Goal**: Validate level up eligibility logic.

### Step 5.1: Create Backend Test File

**File**: Create `backend/tests/test_level_up_eligibility.py`

1. **Create test file with fixtures** (similar structure to Phase 4)

### Step 5.2: Create Test Cases for Each Level

For each level (2-45), create test cases:

1. **Test user cannot level up without required achievements**:
   ```python
   def test_level_2_requires_addition_basics(app, test_user):
       """Test level 2 requires addition-basics achievement."""
       with app.app_context():
           # User should not have achievement
           can_level, missing = UserService.can_level_up(test_user, 2)
           assert can_level == False
           assert "addition-basics" in missing
   ```

2. **Test user can level up when all achievements present**:
   ```python
   def test_level_2_unlocks_with_addition_basics(app, test_user):
       """Test level 2 unlocks when addition-basics achieved."""
       with app.app_context():
           # Award achievement
           AchievementService.award_achievement(test_user.id, "addition-basics")
           
           # User should be able to level up
           can_level, missing = UserService.can_level_up(test_user, 2)
           assert can_level == True
           assert len(missing) == 0
   ```

3. **Test level up API endpoint**:
   ```python
   def test_level_up_endpoint_success(app, test_user):
       """Test level up endpoint when eligible."""
       with app.app_context():
           # Award required achievements
           # Call level up endpoint
           # Verify level increases
           pass
   ```

4. **Test level up API endpoint failure**:
   ```python
   def test_level_up_endpoint_failure(app, test_user):
       """Test level up endpoint when not eligible."""
       with app.app_context():
           # Don't award achievements
           # Call level up endpoint
           # Verify 400 response with missing achievements
           pass
   ```


### Step 5.3: Test All Level Requirements

**Complete List of Level Requirements** (from `level_progression_config.py`):

Create test cases for all levels 2-45:

- **Level 2**: `addition-basics`
- **Level 3**: `level-2-mastery`
- **Level 4**: `subtraction-basics`
- **Level 5**: `perfect-sessions-2`, `basic-math-test`, `level-5-mastery`
- **Level 6**: `level-6-mastery`
- **Level 7**: `level-7-mastery`
- **Level 8**: `level-8-mastery`
- **Level 9**: `level-9-mastery`
- **Level 10**: `level-10-mastery`, `multiply-by-two-test-a`
- **Level 11**: `level-11-mastery`, `multiply-by-three-test-a`
- **Level 12**: `level-12-mastery`, `multiply-by-four-test-a`
- **Level 13**: `level-13-mastery`, `multiply-by-five-test-a`
- **Level 14**: `level-14-mastery`, `multiply-by-six-test-a`
- **Level 15**: `level-15-mastery`, `multiply-by-seven-test-a`
- **Level 16**: `level-16-mastery`, `multiply-by-eight-test-a`
- **Level 17**: `level-17-mastery`, `multiply-by-nine-test-a`
- **Level 18**: `level-18-mastery`, `multiply-by-zero-test-a`
- **Level 19**: `level-19-mastery`, `multiply-by-ten-test-a`
- **Level 20**: `level-20-mastery`, `multiply-by-eleven-test-a`
- **Level 21**: `level-21-mastery`, `multiply-by-twelve-test-a`
- **Level 22**: `level-22-mastery`
- **Level 23**: `level-23-mastery`
- **Level 24**: `level-24-mastery`
- **Level 25**: `level-25-mastery`
- **Level 26**: `level-25-mastery`, `multiplication-mastery`, `addition-mastery`, `subtraction-mastery`, `addition-subtraction-advanced-mastery`
- **Level 27**: `divide-by-two`
- **Level 28**: `divide-by-three`
- **Level 29**: `divide-by-four`
- **Level 30**: `divide-by-five`
- **Level 31**: `divide-by-six`
- **Level 32**: `divide-by-seven`
- **Level 33**: `divide-by-eight`
- **Level 34**: `divide-by-nine`
- **Level 35**: `divide-by-ten`
- **Level 36**: `divide-by-eleven`
- **Level 37**: `divide-by-twelve`
- **Level 38**: `division-remainder`
- **Level 39**: `division-double-remainder`
- **Level 40**: `division-fraction`
- **Level 41**: `division-double-fraction`
- **Level 42**: `multiplication-triple`
- **Level 43**: `division-triple-fraction`
- **Level 44**: `division-decimal`
- **Level 45**: `division-double-decimal`

**Test Pattern for Level Requirements**:
```python
@pytest.mark.parametrize("target_level,required_achievements", [
    (2, ["addition-basics"]),
    (3, ["level-2-mastery"]),
    (4, ["subtraction-basics"]),
    (5, ["perfect-sessions-2", "basic-math-test", "level-5-mastery"]),
    # ... continue for all levels
])
def test_level_up_requires_achievements(app, test_user, target_level, required_achievements):
    """Test that level up requires all specified achievements."""
    # User should not have achievements initially
    can_level, missing = UserService.can_level_up(test_user, target_level)
    assert can_level == False
    assert set(missing) == set(required_achievements)
    
    # Award all required achievements
    for achievement_code in required_achievements:
        award_achievement_directly(test_user.id, achievement_code)
    
    # User should now be able to level up
    can_level, missing = UserService.can_level_up(test_user, target_level)
    assert can_level == True
    assert len(missing) == 0
```

---

## Phase 6: Question Distribution Verification

**Goal**: Verify question distribution logic works correctly.

### Implementation Status

**What IS Implemented**:

1. **Standard Distribution** (default for practice sessions):
   - 70% current level
   - 20% level-1 (if available)
   - 10% level-2 (if available)
   - Used when adaptive distribution is not triggered

2. **Adaptive Distribution** (triggered after failed test retake):
   - **Trigger condition**: User has passed a test at a level, then fails a retake at that level
   - **Distribution**:
     - 50% around user's level (22.5% current level, 13.75% level-1, 13.75% level+1)
     - 20% slowest questions (levels 1-37, based on average response time from last 30 days)
     - 30% random (levels 1 to user's level)
   - Focuses on **slowest questions** (based on response time), not missed questions (based on correctness)

3. **Missed Questions Tracking**:
   - Tracked by `TestEligibilityService.count_missed_questions_by_level()` for retake eligibility
   - Used to trigger retake requirements (3+ missed questions in last 7 days)
   - **NOT directly used** in adaptive question distribution

4. **Lower-Level Questions**:
   - Appear in adaptive distribution via "slowest questions" (20%) and "random" (30%) components
   - Total: 50% of adaptive distribution includes levels 1-37

**What Needs Testing**:

1. Verify standard distribution percentages
2. Verify adaptive distribution activates after failed retake
3. Verify adaptive distribution percentages match expected values
4. Verify slowest questions are included in adaptive distribution
5. Verify lower-level questions (1-37) appear in significant percentage
6. Verify retake eligibility triggers when missing too many questions (uses missed questions tracking, not adaptive distribution)

### Step 6.1: Create Distribution Test File

**File**: Create E2E test in `frontend/e2e/question-distribution.spec.ts`

**Decision**: Use E2E approach to test actual user experience and verify distribution through actual session generation

### Step 6.2: Create Helper Functions

**File**: `frontend/e2e/helpers/test-helpers.ts`

1. **Add function to analyze question distribution**:
   ```typescript
   export async function analyzeQuestionDistribution(questions: any[]): Promise<{
     levelCounts: Record<number, number>
     levelPercentages: Record<number, number>
     totalQuestions: number
   }> {
     const levelCounts: Record<number, number> = {}
     const totalQuestions = questions.length
     
     for (const q of questions) {
       const level = q.level || q.required_level || 1
       levelCounts[level] = (levelCounts[level] || 0) + 1
     }
     
     const levelPercentages: Record<number, number> = {}
     for (const level in levelCounts) {
       levelPercentages[level] = (levelCounts[level] / totalQuestions) * 100
     }
     
     return { levelCounts, levelPercentages, totalQuestions }
   }
   ```

2. **Add function to complete session via API**:
   ```typescript
   export async function completeSessionViaAPI(
     request: APIRequestContext,
     sessionId: number
   ): Promise<any> {
     const response = await request.post(`/api/practice/sessions/${sessionId}/complete`)
     if (!response.ok()) {
       const error = await response.json()
       throw new Error(`Failed to complete session: ${JSON.stringify(error)}`)
     }
     return await response.json()
   }
   ```

3. **Add function to create missed questions**:
   ```typescript
   export async function createMissedQuestions(
     request: APIRequestContext,
     sessionId: number,
     questionIds: number[]
   ): Promise<void> {
     // Answer questions incorrectly
     for (const qId of questionIds) {
       await answerQuestionViaAPI(request, sessionId, qId, '999', 5000)
     }
   }
   ```

4. **Add function to create slow responses**:
   ```typescript
   export async function createSlowResponses(
     request: APIRequestContext,
     sessionId: number,
     questionIds: number[],
     durationMs: number
   ): Promise<void> {
     // Answer questions correctly but slowly
     for (const qId of questionIds) {
       const question = await getQuestion(request, qId)
       await answerQuestionViaAPI(request, sessionId, qId, question.correct_answer, durationMs)
     }
   }
   ```

5. **Add function to get question details** (if not exists):
   ```typescript
   export async function getQuestion(
     request: APIRequestContext,
     questionId: number
   ): Promise<any> {
     // Question details may be available from session response
     // Or may need to query separately
     // Implementation depends on available endpoints
     throw new Error('getQuestion helper needs implementation based on available API')
   }
   ```

6. **Add function to create test attempt** (for Phase 6 DIST-004, DIST-006):
   ```typescript
   /**
    * Create a test attempt directly (for testing purposes)
    * Requires backend test endpoint or direct DB access in E2E tests
    */
   export async function createTestAttempt(
     request: APIRequestContext,
     userId: number,
     level: number,
     accuracy: number, // 0.0 to 1.0
     passed: boolean
   ): Promise<any> {
     // This may require a dev-only backend endpoint to create test attempts
     // Similar to test-setup endpoint
     // For now, this is a placeholder - actual implementation needed
     throw new Error('createTestAttempt helper needs backend endpoint implementation')
   }
   ```
   
   **Note**: This helper may need a backend dev-only endpoint similar to `/api/users/<id>/test-setup` to create test attempts directly.


### Step 6.3: Implement Distribution Test Cases

**File**: Create `frontend/e2e/question-distribution.spec.ts`

1. **DIST-001: Verify distribution focuses on user's level**:
   ```typescript
   test('DIST-001: Question distribution focuses on user level', async ({ page, testUser, request }) => {
     // Start multiple practice sessions
     // Analyze question distribution across sessions
     // Verify ~50% of questions are around user's level
     
     const sessions = []
     for (let i = 0; i < 5; i++) {
       const session = await startPracticeSessionViaAPI(request, testUser.id)
       sessions.push(session)
       // Complete session quickly
       for (const q of session.questions) {
         await answerQuestionViaAPI(request, session.session_id, q.question_id, q.correct_answer, 2000)
       }
       await completeSessionViaAPI(request, session.session_id)
     }
     
     // Analyze distribution
     const allQuestions = sessions.flatMap(s => s.questions)
     const distribution = await analyzeQuestionDistribution(allQuestions)
     
     // Verify user's level has significant percentage
     const userLevel = testUser.level
     expect(distribution.levelPercentages[userLevel]).toBeGreaterThan(15) // At least 15%
   })
   ```

2. **DIST-002: Verify slow responses increase question frequency (adaptive distribution)**:
   ```typescript
   test('DIST-002: Slow responses cause questions to appear in adaptive distribution', async ({ page, testUser, request }) => {
     // Prerequisite: User must have passed a test, then failed a retake to trigger adaptive distribution
     // Set up user at level 5, pass test, then fail retake
     await setUserLevelDirectly(request, testUser.id, 5)
     
     // Pass initial test (requires creating test session and passing it)
     // Then fail retake (create another test session and fail it)
     // This triggers adaptive distribution
     
     // Create multiple sessions with slow responses on level 2 to establish it as "slowest"
     for (let i = 0; i < 5; i++) {
       const session = await startPracticeSessionViaAPI(request, testUser.id)
       const level2Questions = session.questions.filter(q => q.level === 2 || q.required_level === 2)
       if (level2Questions.length > 0) {
         await createSlowResponses(request, session.session_id, level2Questions.slice(0, 2).map(q => q.question_id), 10000)
       }
       // Complete session with mix of speeds
       for (const q of session.questions) {
         const isSlow = level2Questions.some(lq => lq.question_id === q.question_id)
         await answerQuestionViaAPI(request, session.session_id, q.question_id, q.correct_answer, isSlow ? 10000 : 2000)
       }
       await completeSessionViaAPI(request, session.session_id)
     }
     
     // Wait for data to be processed (slowest levels calculated from last 30 days)
     await page.waitForTimeout(2000)
     
     // Create new session - should use adaptive distribution (if triggered)
     // Note: Adaptive distribution only activates after failed retake, not just from slow responses
     // This test verifies that slowest levels are tracked, which will be used when adaptive distribution activates
   })
   ```
   
   **Note**: This test verifies that slow response times are tracked. However, adaptive distribution only activates after a failed retake. The slowest levels are used in adaptive distribution, but the test needs to ensure adaptive distribution is triggered first.

3. **DIST-003: Verify standard distribution percentages**:
   ```typescript
   test('DIST-003: Standard distribution follows 70/20/10 rule', async ({ page, testUser, request }) => {
     // Set user to level 5 (no adaptive distribution triggered)
     await setUserLevelDirectly(request, testUser.id, 5)
     
     // Create multiple practice sessions
     const sessions = []
     for (let i = 0; i < 10; i++) {
       const session = await startPracticeSessionViaAPI(request, testUser.id)
       sessions.push(session)
       // Complete session quickly
       for (const q of session.questions) {
         await answerQuestionViaAPI(request, session.session_id, q.question_id, q.correct_answer, 2000)
       }
       await completeSessionViaAPI(request, session.session_id)
     }
     
     // Analyze distribution
     const allQuestions = sessions.flatMap(s => s.questions)
     const distribution = await analyzeQuestionDistribution(allQuestions)
     
     // Verify level 5 has ~70%, level 4 has ~20%, level 3 has ~10%
     // Allow some variance for randomness (e.g., 65-75%, 15-25%, 5-15%)
     expect(distribution.levelPercentages[5] || 0).toBeGreaterThan(60)
     expect(distribution.levelPercentages[5] || 0).toBeLessThan(80)
     if (distribution.levelPercentages[4]) {
       expect(distribution.levelPercentages[4]).toBeGreaterThan(10)
       expect(distribution.levelPercentages[4]).toBeLessThan(30)
     }
   })
   ```

4. **DIST-004: Verify re-test requirement triggers**:
   ```typescript
   test('DIST-004: Missing too many questions triggers re-test eligibility', async ({ page, testUser, request }) => {
     // Set user at level 5 and pass initial test
     await setUserLevelDirectly(request, testUser.id, 5)
     
     // Pass test at level 5 (requires creating test session and passing)
     // TODO: Create helper to create test attempt with passing score
     
     // Create practice sessions and miss 3+ questions on level 5 in last 7 days
     for (let i = 0; i < 3; i++) {
       const session = await startPracticeSessionViaAPI(request, testUser.id)
       const level5Questions = session.questions.filter(q => q.level === 5 || q.required_level === 5)
       // Miss at least one question per session
       if (level5Questions.length > 0) {
         const questionToMiss = level5Questions[0]
         await answerQuestionViaAPI(request, session.session_id, questionToMiss.question_id, '999', 5000)
       }
       // Answer rest correctly
       for (const q of session.questions) {
         if (q.question_id !== level5Questions[0]?.question_id) {
           await answerQuestionViaAPI(request, session.session_id, q.question_id, q.correct_answer, 2000)
         }
       }
       await completeSessionViaAPI(request, session.session_id)
     }
     
     // Verify retake eligibility is triggered
     const eligibility = await getTestEligibility(request, testUser.id, 5)
     expect(eligibility.is_retake_eligible || eligibility.is_eligible).toBe(true)
     expect(eligibility.missed_questions_count).toBeGreaterThanOrEqual(3)
   })
   ```
   
   **Note**: This tests the missed questions tracking for retake eligibility. This is separate from adaptive distribution - missed questions trigger retake eligibility, but adaptive distribution focuses on slowest questions (response time).

5. **DIST-005: Verify lower-level questions appear in adaptive distribution**:
   ```typescript
   test('DIST-005: Lower-level questions appear in adaptive distribution', async ({ page, testUser, request }) => {
     // Set high-level user (e.g., level 15)
     await setUserLevelDirectly(request, testUser.id, 15)
     
     // Trigger adaptive distribution: pass test, then fail retake
     // TODO: Create helper to set up adaptive distribution trigger state
     
     // Create multiple practice sessions with adaptive distribution active
     const sessions = []
     for (let i = 0; i < 10; i++) {
       const session = await startPracticeSessionViaAPI(request, testUser.id)
       sessions.push(session)
       // Complete session
       for (const q of session.questions) {
         await answerQuestionViaAPI(request, session.session_id, q.question_id, q.correct_answer, 2000)
       }
       await completeSessionViaAPI(request, session.session_id)
     }
     
     // Analyze distribution
     const allQuestions = sessions.flatMap(s => s.questions)
     const distribution = await analyzeQuestionDistribution(allQuestions)
     
     // Verify levels 1-37 appear in significant percentage (20% slowest + 30% random = 50%)
     // Note: This only works if adaptive distribution is active
     let lowerLevelPercentage = 0
     for (let level = 1; level <= 37; level++) {
       lowerLevelPercentage += distribution.levelPercentages[level] || 0
     }
     // In adaptive distribution, 50% should be lower levels (1-37)
     // Allow variance: expect at least 40%
     expect(lowerLevelPercentage).toBeGreaterThan(35)
   })
   ```
   
   **Note**: This test only works if adaptive distribution is active (triggered by failed retake). Otherwise, standard distribution doesn't include lower levels.

6. **DIST-006: Verify adaptive distribution activates after failed retake**:
   ```typescript
   test('DIST-006: Adaptive distribution activates after failed retake', async ({ page, testUser, request }) => {
     // Set user at level 5
     await setUserLevelDirectly(request, testUser.id, 5)
     
     // Step 1: Pass initial test at level 5
     // TODO: Create test attempt with passing score
     // const testAttempt1 = await createTestAttempt(request, testUser.id, 5, 0.85, true)
     
     // Step 2: Fail retake at level 5 (score < passing score or slower than historical average)
     // const testAttempt2 = await createTestAttempt(request, testUser.id, 5, 0.70, false)
     
     // Step 3: Create practice session - should use adaptive distribution
     const session = await startPracticeSessionViaAPI(request, testUser.id)
     
     // Step 4: Verify distribution includes slowest questions and lower levels
     const distribution = await analyzeQuestionDistribution(session.questions)
     
     // Adaptive distribution should have:
     // - 50% around user's level (22.5% level 5, 13.75% level 4, 13.75% level 6)
     // - 20% slowest questions (levels 1-37)
     // - 30% random (levels 1-5)
     
     // Verify user's level (5) appears
     expect(distribution.levelPercentages[5] || 0).toBeGreaterThan(15)
     
     // Verify lower levels (1-4) appear (from slowest + random components)
     let lowerLevelPercentage = 0
     for (let level = 1; level <= 4; level++) {
       lowerLevelPercentage += distribution.levelPercentages[level] || 0
     }
     expect(lowerLevelPercentage).toBeGreaterThan(20) // At least 20% from slowest/random
   })
   ```
   
   **Implementation Notes**:
   - Adaptive distribution is checked in `SessionEngineService.generate_session()` (lines 271-279)
   - It checks all levels up to user's level for failed retakes
   - `AdaptiveDistributionService.should_apply_adaptive_distribution()` returns True if:
     - User has passed test before
     - Most recent attempt failed (score < passing score OR slower than historical average)
   - When active, uses `AdaptiveDistributionService.generate_adaptive_question_distribution()` for question selection


---

## Files to Modify Summary

### Phase 4: Achievement Awarding (Backend)

1. Create `backend/tests/test_achievements_awarding.py` - New file with all achievement tests
2. Add test fixtures and helpers for creating test data
3. Implement tests for all achievement types (milestone, accuracy, speed, consistency, progression, level mastery, test)

### Phase 5: Level Up Eligibility (Backend)

1. Create `backend/tests/test_level_up_eligibility.py` - New file with level up tests
2. Test all levels (2-45) for correct requirement checking
3. Test level up API endpoints

### Phase 6: Question Distribution

1. `frontend/e2e/helpers/test-helpers.ts` - Add distribution analysis helpers
2. Create `frontend/e2e/question-distribution.spec.ts` - New file with distribution tests
3. Create helper functions for creating test scenarios (missed questions, slow responses)

---

## Implementation Notes for Phases 4-6

1. **Test Data Setup**: Each phase will need careful test data setup. Use API calls to create users, sessions, and responses with specific characteristics.

2. **Test Isolation**: Ensure each test creates its own test user and cleans up after itself (handled by fixtures).

3. **Timing**: Some tests may need delays to allow backend processing. Use `waitForTimeout` sparingly, prefer `waitForSelector` or `waitForResponse`.

4. **Statistical Validation**: Distribution tests (Phase 6) may need multiple sessions to verify percentages. Consider running tests multiple times or analyzing larger datasets.

5. **Backend Test Structure**: For Phases 4 and 5, follow existing backend test patterns if they exist, or create new structure following pytest conventions.

6. **Complex Achievement Testing**: Some achievements require complex setups (streaks, consecutive correct answers, speed requirements). Use helper functions to create these scenarios reliably.

7. **Level Up Testing**: Test all 44 levels (2-45) systematically. Consider parameterized tests to avoid code duplication.

8. **Distribution Testing**: Question distribution is probabilistic, so tests may need statistical validation over multiple runs or larger sample sizes.

---

## Open Questions & Decisions Needed

### Phase 4: Achievement Awarding

1. **Test Achievement Setup**: How do we create test attempts with specific accuracy/tier results for testing achievements?
   - **Option A**: Create dev-only endpoint `/api/test-attempts/create` to create test attempts directly
   - **Option B**: Use existing test session creation flow and answer questions to achieve desired accuracy
   - **Recommendation**: Option A for speed, but Option B is more realistic

2. **High-Level Test Achievements**: For testing achievements that require high levels (e.g., level 25 mastery), do we:
   - Set user level directly and create test attempts?
   - Or create a more comprehensive test setup that simulates leveling up naturally?
   - **Recommendation**: Set level directly for speed, but document that real-world requires natural progression

3. **Consecutive Achievement Testing**: For achievements requiring consecutive correct answers across sessions:
   - How do we handle session boundaries?
   - Should we test that consecutive count resets on incorrect answer?
   - **Recommendation**: Test both single-session and multi-session consecutive scenarios

### Phase 5: Level Up Eligibility

1. **Level Requirements Source**: Should tests import directly from `level_progression_config.py` or hardcode requirements?
   - **Recommendation**: Import from config to avoid duplication, but add validation that config is complete

2. **Parameterized Tests**: Should we use pytest parameterization for all 44 levels or create separate test functions?
   - **Recommendation**: Use parameterization for efficiency, but keep individual tests for complex levels (like level 5 with 3 requirements, level 26 with 5 requirements)

3. **Level Up API Endpoint**: What's the exact endpoint and request format for level up?
   - Need to verify: `/api/users/<id>/level-up` POST endpoint exists and format
   - **Action Needed**: Check routes.py for existing endpoint

### Phase 6: Question Distribution

1. **Test Attempt Creation**: How do we create test attempts for triggering adaptive distribution?
   - Need dev-only endpoint or helper to create test attempts with specific scores
   - **Action Needed**: Create `/api/test-attempts/create` endpoint or similar test helper

2. **Statistical Validation**: For distribution tests, what variance is acceptable?
   - Standard distribution: 70/20/10 rule - what variance (e.g., 65-75/15-25/5-15)?
   - Adaptive distribution: 50/20/30 split - what variance?
   - **Recommendation**: Document acceptable variance ranges in test comments

3. **Adaptive Distribution Timing**: How long does it take for slowest questions data to be available?
   - Slowest questions calculated from last 30 days
   - Do we need to wait/refresh or is it real-time?
   - **Action Needed**: Check if `get_user_slowest_levels()` uses cached data or calculates on-the-fly

4. **E2E vs Backend Testing**: Should distribution logic be tested in backend tests or E2E tests?
   - **Current Decision**: E2E tests (already made)
   - **Rationale**: Tests actual user experience and full stack integration
   - **Note**: Consider adding backend unit tests for distribution algorithm itself

5. **Missed Questions vs Slowest Questions**: Phase 6 originally asked to verify "missed questions appear more in future sessions", but implementation focuses on "slowest questions" (based on time, not correctness).
   - **Clarification Needed**: Is this the intended behavior, or should missed questions also be prioritized?
   - **Current Implementation**: Only slowest questions (by response time) are prioritized in adaptive distribution
   - **Missed questions** are tracked separately for retake eligibility only

6. **Helper Function Dependencies**: Some helper functions (like `getQuestion()`, `createTestAttempt()`) depend on API endpoints that may not exist.
   - **Action Needed**: 
     - Verify which endpoints exist
     - Create missing endpoints or adapt helpers to use existing endpoints
     - Document any limitations

### General

1. **Test Data Cleanup**: Should backend tests clean up test data automatically or rely on fixtures?
   - **Recommendation**: Use pytest fixtures with automatic cleanup (already in plan)

2. **Performance**: Will creating many test users/sessions for Phase 4-6 tests be slow?
   - **Action Needed**: Consider parallel test execution or test data optimization
   - **Recommendation**: Use pytest-xdist for parallel execution if available

3. **Test Environment**: Do we have a dedicated test database, or do we use the same DB as dev?
   - **Action Needed**: Verify test environment setup
   - **Recommendation**: Separate test database with automatic cleanup

4. **Backend Test Fixtures**: Are there existing backend test fixtures we should reuse?
   - **Action Needed**: Check `backend/tests/` for existing fixture patterns
   - **Recommendation**: Follow existing patterns if they exist

---

## Files to Modify Summary (Updated)

### Step 0: Test Setup Infrastructure

1. `backend/app/routes.py` - Add `/api/users/<id>/test-setup` endpoint (already in phases 1-3 plan)
2. Create `backend/tests/helpers/test_data_helpers.py` - New file with test data helper functions
3. `frontend/e2e/helpers/test-helpers.ts` - Add test setup helper functions (already in phases 1-3 plan)

### Phase 4: Achievement Awarding (Backend)

1. Create `backend/tests/test_achievements_awarding.py` - New file with all achievement tests
2. Create `backend/tests/helpers/test_data_helpers.py` - Shared test data helpers (if not created in Step 0)
3. **Optional**: Create `/api/test-attempts/create` endpoint for creating test attempts directly (if needed)

### Phase 5: Level Up Eligibility (Backend)

1. Create `backend/tests/test_level_up_eligibility.py` - New file with level up tests
2. Use shared helpers from `backend/tests/helpers/test_data_helpers.py`
3. **Verify**: Check if `/api/users/<id>/level-up` endpoint exists in `backend/app/routes.py`

### Phase 6: Question Distribution (E2E)

1. `frontend/e2e/helpers/test-helpers.ts` - Add distribution analysis helpers and session helpers
2. Create `frontend/e2e/question-distribution.spec.ts` - New file with distribution tests
3. **Optional**: Create `/api/test-attempts/create` endpoint for creating test attempts directly (for DIST-004, DIST-006)
4. **Verify**: Check if `completeSessionViaAPI` function already exists in test-helpers.ts

