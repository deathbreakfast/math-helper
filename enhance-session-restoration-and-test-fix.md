# Restore Incomplete Sessions from Backend (Remove localStorage Dependency)

## Problem Analysis

Currently, the frontend uses localStorage as the primary mechanism for session restoration, with a separate `/api/practice/sessions/incomplete` endpoint. This creates:

- Sync issues between localStorage and backend
- Doesn't work across devices/browsers
- Unnecessary complexity with separate endpoints
- localStorage can be cleared/corrupted

## Solution Overview

1. **Backend**: Store question IDs with session when created
2. **Backend**: Enhance `/api/practice/sessions/start` to check for incomplete sessions first
3. **Backend**: Return existing incomplete session OR create new one (single endpoint handles both)
4. **Frontend**: Remove all localStorage session state logic
5. **Frontend**: Simply call start endpoint - it returns all data needed (existing or new)

## Implementation Plan

### Phase 1: Backend - Store Question IDs with Session

**File**: `backend/app/models.py` (lines 34-52)

1. **Add `question_ids` field to `PracticeSession` model**:

   - Add `question_ids = db.Column(db.Text, nullable=True)` 
   - Stores JSON array of question IDs: `[1, 2, 3, ...]`
   - Nullable for backward compatibility with existing sessions
   - This enables other features (adaptive distribution, analytics) to work properly

2. **Create database migration**:

   - Add `question_ids` column to `practice_sessions` table
   - Type: TEXT (stores JSON array)
   - Existing sessions will have NULL (can populate from responses if needed)

**File**: `backend/app/services/session_engine_service.py` (lines 135-308)

3. **Update `generate_session` to store question IDs**:

   - After generating questions and creating session
   - Extract question IDs from question data (each question has `question_id` from `generate_question`)
   - Store as JSON array: `session.question_ids = json.dumps([q['question_id'] for q in questions])`
   - Question count can be inferred from `len(question_ids)` array

### Phase 2: Backend - Enhance Start Session Endpoint

**File**: `backend/app/services/practice_service.py`

4. **Enhance `get_session_with_details`** (lines 308-375):

   - Use stored `question_ids` from session to fetch ALL questions
   - Query: `Question.query.filter(Question.id.in_(question_ids)).all()`
   - Order questions: answered first (by response `answered_at` time), then unanswered
   - Build response map for answered questions
   - Return full question list with response data attached where available

5. **Create helper function to check for incomplete session**:

   - Use existing `get_incomplete_session` logic (lines 278-306)
   - Return session with full question details if found

**File**: `backend/app/services/session_engine_service.py`

6. **Update `generate_session` to check for incomplete first**:

   - Before creating new session, check for incomplete session using `PracticeService.get_incomplete_session`
   - If incomplete session exists:
     - Get full session details with all questions using `get_session_with_details`
     - Return existing session data (same format as new session)
   - If no incomplete session:
     - Create new session as before
     - Store question IDs
     - Return new session data

**File**: `backend/app/routes.py` (lines 281-306)

7. **Update `/api/practice/sessions/start` endpoint**:

   - The endpoint already calls `SessionEngineService.generate_session`
   - No changes needed - `generate_session` now handles incomplete check internally
   - Returns same format whether existing or new session

**File**: `backend/app/routes.py` (lines 202-234)

8. **Remove or deprecate `/api/practice/sessions/incomplete` endpoint**:

   - No longer needed - start endpoint handles this
   - Can be removed or kept for backward compatibility (but not used by frontend)

### Phase 3: Frontend - Remove localStorage and Simplify

**File**: `frontend/src/features/practice/hooks/usePracticeSession.ts`

9. **Remove all localStorage session state functions**:

   - Remove `saveSessionState` function (lines 62-93)
   - Remove `loadSessionState` function (lines 95-131)
   - Remove `clearSessionState` function (lines 143-149)
   - Remove `getStorageKey` function (lines 58-60)
   - Remove `SavedSessionState` type (lines 45-56) - no longer needed

10. **Remove localStorage save on state changes** (lines 167-183):

    - Remove the `useEffect` that saves to localStorage whenever session state changes
    - Remove the `useEffect` that saves on navigation away (lines 185-200)

11. **Simplify session initialization** (lines 237-384):

    - Remove all incomplete session checking logic (lines 245-306)
    - Remove localStorage fallback logic (lines 308-343)
    - Simply call `/api/practice/sessions/start` endpoint
    - Endpoint returns existing incomplete session OR new session
    - Transform response to `PracticeQuestion[]` format
    - Set session state from response

12. **Create helper function** to transform backend question format:
    ```typescript
    function transformBackendQuestionsToPracticeQuestions(
      backendQuestions: any[],
      sessionMode: string
    ): PracticeQuestion[]
    ```


    - Map backend question fields to `PracticeQuestion` type
    - Handle layout config parsing (may be JSON string or object)
    - Ensure all required fields are present
    - Questions are already ordered: answered first, then unanswered

13. **Create helper function** to reconstruct session state from response:
    ```typescript
    function reconstructSessionStateFromResponse(
      responseData: any
    ): {
      problems: PracticeQuestion[]
      questionAnswers: Record<string, QuestionAnswer>
      currentQuestionIndex: number
      questionStartTimes: Record<string, number>
      flaggedQuestions: Record<string, boolean>
    }
    ```


    - Transform questions to `PracticeQuestion[]`
    - Build `questionAnswers` from response data (questions with responses)
    - Find latest unanswered question index (or last answered if all are answered)
    - Questions are already ordered: answered first, then unanswered
    - Initialize empty `questionStartTimes` and `flaggedQuestions`

14. **Update session completion logic** (lines 600-660):

    - Remove localStorage clearing calls
    - Keep `lastPracticeSession` for summary page (this is different - it's for displaying results, not session state)

### Phase 4: Handle Edge Cases

1. **Question ordering**: Questions ordered by answered status

   - Backend returns: answered questions first (ordered by `answered_at`), then unanswered
   - Frontend maintains this order
   - Resume on latest unanswered question (or last answered if all are answered)

2. **Partial responses**: Handle cases where some questions are answered

   - Mark answered questions as `isChecked: true`
   - Set `feedback` based on `is_correct` from response
   - Set `userAnswer` from `submitted_answer`

3. **Missing question data**: If backend can't reconstruct full question list

   - Fall back to creating new session
   - Log warning for debugging

4. **Backward compatibility**: Existing sessions without `question_ids`

   - If `question_ids` is NULL, try to infer from responses
   - If no responses exist, cannot restore (start new session)

### Phase 5: Testing

1. **Update SUM-001 test** to verify backend restoration works for API-created sessions
2. **Update SUB-004 test** to use API to create session (speed up test) and verify restoration works
3. **Add test case** for API-created session restoration
4. **Verify** that sessions work across page refreshes without localStorage

## Files to Modify

1. `backend/app/models.py` - Add `question_ids` field to `PracticeSession`
2. `backend/app/services/session_engine_service.py` - Check for incomplete session first, store question IDs
3. `backend/app/services/practice_service.py` - Enhance `get_session_with_details` to use stored question IDs
4. `backend/app/routes.py` - Remove/deprecate incomplete endpoint (optional)
5. `frontend/src/features/practice/hooks/usePracticeSession.ts` - Remove localStorage, simplify to just call start endpoint
6. `frontend/e2e/summary-page.spec.ts` - Update SUM-001 to verify restoration
7. `frontend/e2e/session-submission.spec.ts` - Update SUB-004 to use API for session creation

## Notes

- `lastPracticeSession` in `useSummaryData.ts` is kept - this is for displaying summary results, not session state
- All session state restoration now comes from backend via single start endpoint
- Much simpler codebase with single source of truth
- Frontend just calls start endpoint - backend handles all the logic