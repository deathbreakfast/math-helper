# E2E Test Implementation Plan - Phases 1-3: UI Testing

This plan addresses implementation and testing for Achievements, Leveling, and Test Flow UI elements. Each phase includes specific file paths, detailed implementation steps, and code changes.

**Prerequisites**: Complete Step 0 before starting Phase 1, as it provides the test setup infrastructure needed for all UI tests.

---

## Step 0: Create Test Setup Infrastructure

**Goal**: Create helper functions and backend endpoints to set up test users in specific states (levels, achievements) for UI testing.

### Step 0.1: Create Backend Test Setup Endpoint

**File**: `backend/app/routes.py`

1. **Add dev-only test setup endpoint** (after line 696, before delete_user endpoint):
   ```python
   @api_bp.post("/users/<int:user_id>/test-setup")
   def test_setup_user(user_id: int):
       """Test setup endpoint - DEV ONLY. Set user state for E2E tests.
       
       Allows setting:
       - User level (directly, bypassing achievement requirements)
       - Awards achievements (directly, without meeting requirements)
       - Creates test data state
       
       Request body:
       {
           "level": 5,  # Optional: set user level directly
           "achievements": ["addition-basics", "level-2-mastery"],  # Optional: award achievements
       }
       
       Only available in development/test environments.
       """
       from flask import current_app
       
       # Check if in dev/test mode
       if not current_app.config.get('TESTING') and not current_app.debug:
           return jsonify({"error": "Not available in production"}), 403
       
       user = UserService.get_user(user_id)
       if not user:
           return jsonify({"error": "User not found"}), 404
       
       data = request.get_json() or {}
       
       # Set level if specified (bypasses achievement checks)
       if 'level' in data:
           level = data['level']
           if level < 1 or level > 45:
               return jsonify({"error": f"Invalid level: {level}. Must be 1-45."}), 400
           
           user.level = level
           user.updated_at = datetime.utcnow()
           db.session.add(user)
       
       # Award achievements if specified (bypasses requirement checks)
       if 'achievements' in data:
           from .models import Achievement, db
           from .config.achievements import ACHIEVEMENTS_CONFIG
           
           for achievement_code in data['achievements']:
               # Check if achievement exists in config
               if achievement_code not in ACHIEVEMENTS_CONFIG:
                   continue  # Skip invalid achievement codes
               
               # Check if user already has this achievement
               existing = Achievement.query.filter_by(
                   user_id=user_id,
                   code=achievement_code
               ).first()
               
               if not existing:
                   # Create achievement record directly
                   achievement = Achievement(
                       user_id=user_id,
                       code=achievement_code,
                       earned_at=datetime.utcnow()
                   )
                   db.session.add(achievement)
       
       db.session.commit()
       
       return jsonify({
           "success": True,
           "user_id": user_id,
           "level": user.level,
           "message": f"Test setup completed for user {user_id}"
       })
   ```

2. **Add helper function to award achievement directly in AchievementService** (if not exists):
   - Check if `AchievementService` has a method to award achievements directly
   - If not, may need to create achievement records directly in the endpoint above

### Step 0.2: Create Frontend Test Setup Helper Functions

**File**: `frontend/e2e/helpers/test-helpers.ts`

1. **Add function to set user level directly** (after line 160, after getUser function):
   ```typescript
   /**
    * Set user level directly via test setup endpoint (DEV ONLY)
    * Bypasses achievement requirements for test setup purposes
    */
   export async function setUserLevelDirectly(
     request: APIRequestContext,
     userId: number,
     level: number
   ): Promise<void> {
     const response = await request.post(`/api/users/${userId}/test-setup`, {
       data: {
         level: level
       }
     })
     
     if (!response.ok()) {
       const error = await response.json()
       throw new Error(`Failed to set user level: ${JSON.stringify(error)}`)
     }
   }
   ```

2. **Add function to award achievements directly** (after previous function):
   ```typescript
   /**
    * Award achievements directly via test setup endpoint (DEV ONLY)
    * Bypasses requirement checks for test setup purposes
    */
   export async function awardAchievements(
     request: APIRequestContext,
     userId: number,
     achievementCodes: string[]
   ): Promise<void> {
     const response = await request.post(`/api/users/${userId}/test-setup`, {
       data: {
         achievements: achievementCodes
       }
     })
     
     if (!response.ok()) {
       const error = await response.json()
       throw new Error(`Failed to award achievements: ${JSON.stringify(error)}`)
     }
   }
   ```

3. **Add function to set user level and achievements together** (after previous function):
   ```typescript
   /**
    * Set up user with level and achievements in one call (DEV ONLY)
    */
   export async function setupTestUserState(
     request: APIRequestContext,
     userId: number,
     options: {
       level?: number
       achievements?: string[]
     }
   ): Promise<void> {
     const response = await request.post(`/api/users/${userId}/test-setup`, {
       data: {
         level: options.level,
         achievements: options.achievements || []
       }
     })
     
     if (!response.ok()) {
       const error = await response.json()
       throw new Error(`Failed to setup test user state: ${JSON.stringify(error)}`)
     }
   }
   ```

4. **Add function to create user with specific state** (after previous function):
   ```typescript
   /**
    * Create a test user and set up their state (level, achievements) in one call
    * Returns the created user with the requested state
    */
   export async function createTestUserWithState(
     request: APIRequestContext,
     options: {
       name?: string
       avatar?: string
       pin?: string
       level?: number
       achievements?: string[]
     }
   ): Promise<TestUser> {
     // Create user first
     const user = await createTestUser(request, {
       name: options.name,
       avatar: options.avatar,
       pin: options.pin
     })
     
     // Set up state if provided
     if (options.level !== undefined || options.achievements) {
       await setupTestUserState(request, user.id, {
         level: options.level,
         achievements: options.achievements
       })
       
       // Refresh user to get updated level
       const updatedUser = await getUser(request, user.id)
       return updatedUser || user
     }
     
     return user
   }
   ```

5. **Add function to set up user for level up testing** (after previous function):
   ```typescript
   /**
    * Set up user with all required achievements for a target level
    * Useful for testing level up UI when requirements are met
    */
   export async function setupUserForLevelUp(
     request: APIRequestContext,
     userId: number,
     targetLevel: number
   ): Promise<void> {
     // Get level requirements from config (may need API endpoint for this)
     // For now, manually specify known requirements
     // TODO: Add API endpoint to get level requirements, or import from config
     
     // Example: Level 2 requires "addition-basics"
     // Level 3 requires "level-2-mastery"
     // This is a placeholder - actual implementation depends on how we access level requirements
     
     // For now, use direct achievement codes based on known requirements
     const levelRequirements: Record<number, string[]> = {
       2: ['addition-basics'],
       3: ['level-2-mastery'],
       4: ['subtraction-basics'],
       5: ['perfect-sessions-2', 'basic-math-test', 'level-5-mastery'],
       // Add more as needed for testing
     }
     
     const achievements = levelRequirements[targetLevel] || []
     if (achievements.length > 0) {
       await awardAchievements(request, userId, achievements)
     }
     
     // Set user to targetLevel - 1 so they're ready to level up
     await setUserLevelDirectly(request, userId, targetLevel - 1)
   }
   ```

### Step 0.3: Update Test Fixtures (Optional Enhancement)

**File**: `frontend/e2e/fixtures/test-user.ts`

1. **Add optional test user state setup** (optional - can be done per-test instead):
   - Could add a parameter to testUser fixture to optionally set up state
   - For now, individual tests can call helper functions as needed

### Step 0.4: Usage Examples

**Example 1: Create user with achievements for achievement display test**:
```typescript
test('ACH-002: Accuracy achievements display', async ({ page, request }) => {
  // Create user with accuracy achievement unlocked
  const testUser = await createTestUserWithState(request, {
    achievements: ['addition-basics', 'subtraction-basics']
  })
  
  await page.goto('/')
  // ... rest of test uses testUser
  // Cleanup handled automatically by fixture
})
```

**Example 2: Create user at specific level for leveling test**:
```typescript
test('LVL-003: Level up after requirements met', async ({ page, request }) => {
  // Create user at level 1 with all requirements for level 2
  const testUser = await createTestUserWithState(request, {
    level: 1,
    achievements: ['addition-basics'] // Required for level 2
  })
  
  // Now test that user can level up
  await openJourneyModal(page, testUser)
  // ... rest of test
})
```

**Example 3: Set up existing user for test**:
```typescript
test('ACH-005: Test tier achievements display', async ({ page, testUser, request }) => {
  // Award test achievements to existing test user
  await awardAchievements(request, testUser.id, [
    'multiply-by-two-test-a',
    'multiply-by-three-test-s'
  ])
  
  // Now test displays these achievements
  await openJourneyModal(page, testUser)
  // ... rest of test
})
```

---

## Phase 1: Achievements UI Testing

**Goal**: Implement comprehensive E2E tests for all achievement-related UI elements.

### Step 1.1: Add Test IDs to Achievement Components

**File**: `frontend/src/features/students/components/AchievementCard.tsx`

1. **Add test ID to achievement card container** (line 19):

   - Add `data-testid={`testid-achievement-card-${achievement.id}`}` to the motion.div wrapper

2. **Add test IDs for status indicators** (line 40-41):

   - Lock icon: `data-testid="testid-achievement-lock-icon"`
   - Unlock icon: `data-testid="testid-achievement-unlock-icon"`

3. **Add test ID to progress bar container** (line 86):

   - Add `data-testid="testid-achievement-progress-bar"` to the progress bar wrapper div

4. **Add test ID for achievement count badge** (line 46):

   - Add `data-testid="testid-achievement-count-badge"` to the count badge motion.div

**File**: `frontend/src/features/students/components/AchievementsList.tsx`

1. **Add test ID to achievements list container** (line 81):

   - Add `data-testid="testid-achievements-list"` to the motion.div wrapper

2. **Add test IDs to filter chips** (line 88):

   - FilterChips component should already have test IDs, verify they're accessible

**File**: `frontend/src/features/students/components/journey/AchievementsTab.tsx`

1. **Add test IDs to filter dropdowns** (lines 46, 63, 78):

   - Category filter: `data-testid="testid-achievement-filter-category"`
   - Status filter: `data-testid="testid-achievement-filter-status"`
   - Search input: `data-testid="testid-achievement-search-input"`

2. **Add test ID to achievements grid** (line 91):

   - Add `data-testid="testid-achievements-grid"` to the grid div

**File**: `frontend/src/features/students/components/journey/OverviewTab.tsx`

1. **Add test ID to recent achievements section** (line 92):

   - Add `data-testid="testid-recent-achievements"` to the section div

2. **Add test ID to "View All Achievements" button** (line 122):

   - Add `data-testid="testid-view-all-achievements-button"` to the button

**File**: `frontend/src/features/practice/components/summary/AchievementsSection.tsx`

1. **Read file to understand structure, then add**:

   - Test ID to achievements section container
   - Test IDs to newly earned achievement cards
   - Test ID to "no achievements" empty state

### Step 1.2: Create Helper Functions for Achievement Testing

**File**: `frontend/e2e/helpers/test-helpers.ts`

1. **Add function to open journey modal** (after line 734):
   ```typescript
   export async function openJourneyModal(page: Page, testUser: TestUser): Promise<void> {
     // Wait for dashboard to load
     await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
     
     // Select the test user
     const userCard = page.getByTestId(`testid-student-card-${testUser.id}`)
     await userCard.click()
     await page.waitForTimeout(500)
     
     // Click level card to open journey modal
     const levelCard = page.locator('text=/level/i').first()
     await levelCard.click()
     await page.waitForTimeout(500)
   }
   ```

2. **Add function to navigate to achievements tab** (after previous function):
   ```typescript
   export async function navigateToAchievementsTab(page: Page): Promise<void> {
     const achievementsTab = page.getByRole('tab', { name: /achievement/i })
     await achievementsTab.click()
     await page.waitForTimeout(300)
   }
   ```

3. **Add function to filter achievements by category** (after previous function):
   ```typescript
   export async function filterAchievementsByCategory(page: Page, category: string): Promise<void> {
     const categoryFilter = page.getByTestId('testid-achievement-filter-category')
     await categoryFilter.selectOption(category)
     await page.waitForTimeout(300)
   }
   ```

4. **Add function to check achievement status** (after previous function):
   ```typescript
   export async function getAchievementStatus(page: Page, achievementId: string): Promise<'locked' | 'unlocked' | 'in-progress'> {
     const achievementCard = page.getByTestId(`testid-achievement-card-${achievementId}`)
     const hasLockIcon = await achievementCard.locator('[data-testid="testid-achievement-lock-icon"]').isVisible()
     const hasUnlockIcon = await achievementCard.locator('[data-testid="testid-achievement-unlock-icon"]').isVisible()
     
     if (hasLockIcon) return 'locked'
     if (hasUnlockIcon) return 'unlocked'
     return 'in-progress'
   }
   ```


### Step 1.3: Implement Achievement Test Cases

**File**: `frontend/e2e/achievements.spec.ts`

1. **Replace ACH-001** (lines 4-20) with:
   ```typescript
   test('ACH-001: Milestone achievements display', async ({ page, request }) => {
     // Create user with milestone achievements for better test visibility
     const testUser = await createTestUserWithState(request, {
       achievements: ['first-victory', 'first-steps', 'century']
     })
     
     await openJourneyModal(page, testUser)
     await navigateToAchievementsTab(page)
     
     // Filter by milestone category
     await filterAchievementsByCategory(page, 'milestone')
     
     // Verify milestone achievements are visible
     const achievementsGrid = page.getByTestId('testid-achievements-grid')
     await expect(achievementsGrid).toBeVisible()
     
     // Verify at least one achievement card is present
     const achievementCards = page.locator('[data-testid^="testid-achievement-card-"]')
     const count = await achievementCards.count()
     expect(count).toBeGreaterThan(0)
     
     // Cleanup
     await deleteTestUser(request, testUser.id)
   })
   ```

2. **Replace ACH-002 through ACH-007** with similar implementations that:

   - Open journey modal
   - Navigate to achievements tab
   - Filter by appropriate category
   - Verify achievements display with correct status

3. **Replace ACH-008** (lines 95-111) with test that:

   - Opens journey modal
   - Navigates to achievements tab
   - Checks multiple achievement cards for correct status display
   - Verifies locked/unlocked/in-progress states render correctly

4. **Replace ACH-009** (lines 113-134) with test that:

   - Opens journey modal
   - Navigates to achievements tab
   - Finds in-progress achievements
   - Verifies progress bars are visible and show correct percentage

5. **Add new test ACH-010: Achievement filtering**:
   ```typescript
   test('ACH-010: Achievement filtering works', async ({ page, request }) => {
     // Create user with achievements in different categories
     const testUser = await createTestUserWithState(request, {
       achievements: [
         'first-victory', // milestone
         'addition-basics', // accuracy
         'fast-session-bronze', // speed
         'streak-2' // consistency
       ]
     })
     
     await openJourneyModal(page, testUser)
     await navigateToAchievementsTab(page)
     
     // Test category filter
     await filterAchievementsByCategory(page, 'speed')
     await page.waitForTimeout(500)
     
     // Verify filtered achievements are shown
     const achievementCards = page.locator('[data-testid^="testid-achievement-card-"]')
     const count = await achievementCards.count()
     expect(count).toBeGreaterThan(0)
     
     // Test status filter
     const statusFilter = page.getByTestId('testid-achievement-filter-status')
     await statusFilter.selectOption('unlocked')
     await page.waitForTimeout(500)
     
     // Test search filter
     const searchInput = page.getByTestId('testid-achievement-search-input')
     await searchInput.fill('speed')
     await page.waitForTimeout(500)
     
     // Cleanup
     await deleteTestUser(request, testUser.id)
   })
   ```

6. **Add new test ACH-011: Achievement display on dashboard**:
   ```typescript
   test('ACH-011: Achievements display on dashboard', async ({ page, request }) => {
     // Create user with some achievements for better test visibility
     const testUser = await createTestUserWithState(request, {
       achievements: ['first-victory', 'first-steps']
     })
     
     await page.goto('/')
     await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
     
     const userCard = page.getByTestId(`testid-student-card-${testUser.id}`)
     await userCard.click()
     await page.waitForTimeout(1000)
     
     // Verify achievements list is visible
     const achievementsList = page.getByTestId('testid-achievements-list')
     await expect(achievementsList).toBeVisible()
     
     // Cleanup
     await deleteTestUser(request, testUser.id)
   })
   ```


---

## Phase 2: Leveling UI Testing

**Goal**: Implement comprehensive E2E tests for level progression UI elements.

### Step 2.1: Add Test IDs to Level Components

**File**: `frontend/src/features/students/components/LearnerStatsCards.tsx`

1. **Add test ID to level card** (line 61):

   - Add `data-testid="testid-level-card"` to the StatCard for level

2. **Add test ID to level value display**:

   - Verify StatCard component accepts test ID prop, or add wrapper div with test ID

**File**: `frontend/src/features/students/components/LevelRequirementCard.tsx`

1. **Add test ID to level requirement card** (line 17):

   - Add `data-testid={`testid-level-requirement-${requirement.level}`}` to motion.div

2. **Add test ID to level up status indicator** (line 64):

   - Add `data-testid="testid-level-lock-icon"` to Lock icon

3. **Add test IDs to requirement items** (line 72):

   - Add `data-testid={`testid-requirement-${idx}`}` to each requirement div

4. **Add test ID to completion checkmarks** (line 75-80):

   - Add `data-testid="testid-requirement-completed"` when completed, `data-testid="testid-requirement-incomplete"` when not

**File**: `frontend/src/features/students/components/journey/LevelsTab.tsx`

1. **Add test ID to levels tab container**:

   - Add `data-testid="testid-levels-tab"` to motion.div

2. **Add test ID to level progression path header** (line 28):

   - Add `data-testid="testid-level-progression-header"` to the header div

**File**: `frontend/src/features/students/components/journey/JourneyStatsOverview.tsx`

1. **Add test ID to current level display**:

   - Find level display element and add `data-testid="testid-current-level-display"`

### Step 2.2: Add Helper Functions for Level Testing

**File**: `frontend/e2e/helpers/test-helpers.ts`

1. **Add function to navigate to levels tab** (after achievement helpers):
   ```typescript
   export async function navigateToLevelsTab(page: Page): Promise<void> {
     const levelsTab = page.getByRole('tab', { name: /level/i })
     await levelsTab.click()
     await page.waitForTimeout(300)
   }
   ```

2. **Add function to get level up eligibility** (after previous function):
   ```typescript
   export async function getLevelUpEligibility(request: APIRequestContext, userId: number): Promise<any> {
     const response = await request.get(`/api/users/${userId}/level-up/eligibility`)
     if (!response.ok()) {
       throw new Error(`Failed to get level up eligibility: ${response.status()}`)
     }
     return await response.json()
   }
   ```

3. **Add function to check level requirement status** (after previous function):
   ```typescript
   export async function getLevelRequirementStatus(page: Page, level: number): Promise<{
     isLocked: boolean
     completedCount: number
     totalCount: number
   }> {
     const requirementCard = page.getByTestId(`testid-level-requirement-${level}`)
     const isLocked = await requirementCard.locator('[data-testid="testid-level-lock-icon"]').isVisible()
     const completedRequirements = await requirementCard.locator('[data-testid="testid-requirement-completed"]').count()
     const allRequirements = await requirementCard.locator('[data-testid^="testid-requirement-"]').count()
     
     return {
       isLocked,
       completedCount: completedRequirements,
       totalCount: allRequirements
     }
   }
   ```


### Step 2.3: Implement Leveling Test Cases

**File**: `frontend/e2e/leveling.spec.ts`

1. **Enhance LVL-001** (lines 5-23) to include UI verification:
   ```typescript
   test('LVL-001: Level up eligibility', async ({ page, testUser, request }) => {
     await page.goto('/')
     await expect(page.getByTestId('testid-select-learner-header')).toBeVisible()
     
     const userCard = page.getByTestId(`testid-student-card-${testUser.id}`)
     await userCard.click()
     await page.waitForTimeout(1000)
     
     // Check via API
     const eligibility = await getLevelUpEligibility(request, testUser.id)
     expect(eligibility).toHaveProperty('eligible')
     expect(eligibility).toHaveProperty('current_level')
     expect(eligibility).toHaveProperty('next_level')
     
     // Verify UI displays current level
     const levelCard = page.getByTestId('testid-level-card')
     await expect(levelCard).toBeVisible()
   })
   ```

2. **Replace LVL-002** (lines 25-49) with:
   ```typescript
   test('LVL-002: Level up achievement requirements display', async ({ page, testUser }) => {
     await openJourneyModal(page, testUser)
     await navigateToLevelsTab(page)
     
     // Verify levels tab is visible
     const levelsTab = page.getByTestId('testid-levels-tab')
     await expect(levelsTab).toBeVisible()
     
     // Verify level requirements are displayed
     const requirementCards = page.locator('[data-testid^="testid-level-requirement-"]')
     const count = await requirementCards.count()
     expect(count).toBeGreaterThan(0)
     
     // Verify requirement items show completion status
     const completedRequirements = page.locator('[data-testid="testid-requirement-completed"]')
     const completedCount = await completedRequirements.count()
     // At least some requirements should be visible (even if not completed)
   })
   ```

3. **Replace LVL-003** (lines 51-67) with test that:
   ```typescript
   test('LVL-003: Level up after requirements met', async ({ page, request }) => {
     // Create user at level 1 with all requirements for level 2
     const testUser = await createTestUserWithState(request, {
       level: 1,
       achievements: ['addition-basics'] // Required for level 2
     })
     
     await openJourneyModal(page, testUser)
     await navigateToLevelsTab(page)
     
     // Verify level up button/eligibility
     const eligibility = await getLevelUpEligibility(request, testUser.id)
     expect(eligibility.eligible).toBe(true)
     
     // Attempt level up via API
     const levelUpResponse = await request.post(`/api/users/${testUser.id}/level-up`)
     expect(levelUpResponse.ok()).toBe(true)
     
     // Verify level increased
     const userAfter = await getUser(request, testUser.id)
     expect(userAfter?.level).toBe(2)
     
     // Cleanup
     await deleteTestUser(request, testUser.id)
   })
   ```

4. **Replace LVL-004** (lines 69-85) with test that:

   - Uses user without required achievements
   - Verifies level up is blocked
   - Checks API returns correct error
   - Verifies UI shows missing requirements

5. **Add new test LVL-005: Missing achievements display**:
   ```typescript
   test('LVL-005: Missing achievements are listed in requirements', async ({ page, testUser, request }) => {
     await openJourneyModal(page, testUser)
     await navigateToLevelsTab(page)
     
     // Get eligibility via API
     const eligibility = await getLevelUpEligibility(request, testUser.id)
     
     if (!eligibility.eligible && eligibility.missing_achievements) {
       // Verify missing achievements are shown in UI
       for (const missingAchievement of eligibility.missing_achievements) {
         const requirementText = page.locator(`text=/${missingAchievement}/i`)
         await expect(requirementText.first()).toBeVisible({ timeout: 2000 })
       }
     }
   })
   ```

6. **Add new test LVL-006: Level progression path**:
   ```typescript
   test('LVL-006: Level progression path shows correct next level', async ({ page, testUser, request }) => {
     await openJourneyModal(page, testUser)
     await navigateToLevelsTab(page)
     
     const eligibility = await getLevelUpEligibility(request, testUser.id)
     
     // Verify progression header shows next level
     const progressionHeader = page.getByTestId('testid-level-progression-header')
     await expect(progressionHeader).toBeVisible()
     
     // Verify current level is displayed correctly
     const currentLevelText = page.locator(`text=/level.*${eligibility.current_level}/i`)
     await expect(currentLevelText.first()).toBeVisible()
   })
   ```

7. **Add new test LVL-007: Level up notification**:

   - This test requires completing a session that triggers level up
   - Will be integrated with practice flow tests
   - Verify level up banner appears on summary page

---

## Phase 3: Test Flow UI Testing

**Goal**: Implement comprehensive E2E tests for test-taking flow UI elements.

### Step 3.1: Add Test IDs to Test Flow Components

**File**: `frontend/src/features/students/components/journey/TestsTab.tsx`

1. **Add test ID to tests tab container** (line 26):

   - Add `data-testid="testid-tests-tab"` to motion.div

2. **Add test IDs to filters** (lines 46, 61, 76):

   - Tier filter: `data-testid="testid-test-filter-tier"`
   - Status filter: `data-testid="testid-test-filter-status"`
   - Search input: `data-testid="testid-test-search-input"`

3. **Add test ID to test achievements grid** (line 89):

   - Add `data-testid="testid-test-achievements-grid"` to grid div

**File**: Need to find test eligibility display component

1. **Search for component that displays test eligibility/requirements**
2. **Add test IDs to**:

   - Test eligibility status indicator
   - Start Test button
   - Requirements list
   - Retake eligibility message

**File**: `frontend/src/features/practice/PracticePage.tsx`

1. **Add test ID for test mode indicator**:

   - Add `data-testid="testid-test-mode-indicator"` when isTest is true

2. **Add test ID for test question count**:

   - Add `data-testid="testid-test-question-count"` to question counter

### Step 3.2: Add Helper Functions for Test Flow

**File**: `frontend/e2e/helpers/test-helpers.ts`

1. **Add function to navigate to tests tab**:
   ```typescript
   export async function navigateToTestsTab(page: Page): Promise<void> {
     const testsTab = page.getByRole('tab', { name: /test/i })
     await testsTab.click()
     await page.waitForTimeout(300)
   }
   ```

2. **Add function to check test eligibility**:
   ```typescript
   export async function getTestEligibility(request: APIRequestContext, userId: number, level?: number): Promise<any> {
     const url = level 
       ? `/api/practice/test-eligibility?user_id=${userId}&level=${level}`
       : `/api/practice/test-eligibility?user_id=${userId}`
     const response = await request.get(url)
     if (!response.ok()) {
       throw new Error(`Failed to get test eligibility: ${response.status()}`)
     }
     return await response.json()
   }
   ```

3. **Add function to start test via API**:
   ```typescript
   export async function startTestSession(request: APIRequestContext, userId: number, testType: string): Promise<any> {
     const response = await request.post('/api/practice/sessions/start', {
       data: {
         user_id: userId,
         is_test: true,
         test_type: testType,
         mode: 'standard'
       }
     })
     if (!response.ok()) {
       throw new Error(`Failed to start test: ${response.status()}`)
     }
     return await response.json()
   }
   ```


### Step 3.3: Implement Test Flow Test Cases

**File**: `frontend/e2e/test-flow.spec.ts`

1. **Replace TEST-001** (lines 4-35) with:
   ```typescript
   test('TEST-001: Test eligibility check displays requirements', async ({ page, testUser, request }) => {
     await openJourneyModal(page, testUser)
     await navigateToTestsTab(page)
     
     // Verify tests tab is visible
     const testsTab = page.getByTestId('testid-tests-tab')
     await expect(testsTab).toBeVisible()
     
     // Check eligibility via API
     const eligibility = await getTestEligibility(request, testUser.id)
     
     // Verify eligibility information is displayed in UI
     // (Implementation depends on how eligibility is displayed)
   })
   ```

2. **Replace TEST-002** (lines 37-60) with test that:

   - Sets up user with test eligibility
   - Opens journey modal and tests tab
   - Verifies "Start Test" button is enabled
   - Clicks button and verifies navigation to practice page
   - Verifies test mode indicator is visible

3. **Replace TEST-003** (lines 62-71) with test that:

   - Starts a test session via API
   - Answers all questions
   - Submits test
   - Verifies summary page shows test results

4. **Replace TEST-004** (lines 73-103) with test that:

   - Creates user who has passed a test
   - Creates missed questions to trigger retake eligibility
   - Verifies retake eligibility displays correctly
   - Verifies retake can be started

5. **Add new tests for**:

   - TEST-005: Test results display on summary page
   - TEST-006: Test tier filtering in tests tab
   - TEST-007: Daily test limit enforcement
   - TEST-008: Test achievement unlock after completion

---

## Files to Modify Summary

### Step 0: Test Setup Infrastructure

1. `backend/app/routes.py` - Add `/api/users/<id>/test-setup` endpoint for dev-only test setup
2. `frontend/e2e/helpers/test-helpers.ts` - Add test setup helper functions:
   - `setUserLevelDirectly()` - Set user level for testing
   - `awardAchievements()` - Award achievements directly
   - `setupTestUserState()` - Set level and achievements together
   - `createTestUserWithState()` - Create user with initial state
   - `setupUserForLevelUp()` - Set up user ready to level up

### Phase 1: Achievements UI

1. `frontend/src/features/students/components/AchievementCard.tsx` - Add test IDs
2. `frontend/src/features/students/components/AchievementsList.tsx` - Add test IDs
3. `frontend/src/features/students/components/journey/AchievementsTab.tsx` - Add test IDs
4. `frontend/src/features/students/components/journey/OverviewTab.tsx` - Add test IDs
5. `frontend/src/features/practice/components/summary/AchievementsSection.tsx` - Add test IDs
6. `frontend/e2e/helpers/test-helpers.ts` - Add achievement helper functions
7. `frontend/e2e/achievements.spec.ts` - Replace placeholder tests with real implementations

### Phase 2: Leveling UI

1. `frontend/src/features/students/components/LearnerStatsCards.tsx` - Add test IDs
2. `frontend/src/features/students/components/LevelRequirementCard.tsx` - Add test IDs
3. `frontend/src/features/students/components/journey/LevelsTab.tsx` - Add test IDs
4. `frontend/src/features/students/components/journey/JourneyStatsOverview.tsx` - Add test IDs
5. `frontend/e2e/helpers/test-helpers.ts` - Add level helper functions
6. `frontend/e2e/leveling.spec.ts` - Enhance existing tests with UI verification

### Phase 3: Test Flow UI

1. `frontend/src/features/students/components/journey/TestsTab.tsx` - Add test IDs
2. Test eligibility display component (find and add test IDs)
3. `frontend/src/features/practice/PracticePage.tsx` - Add test IDs for test mode
4. `frontend/e2e/helpers/test-helpers.ts` - Add test flow helper functions
5. `frontend/e2e/test-flow.spec.ts` - Replace placeholder tests with real implementations

---

## Implementation Notes for Phases 1-3

1. **Test Data Setup**: Each phase will need careful test data setup. Use the test setup helper functions from Step 0 to create users in expected states:
   - **Option A - Use fixture + modify**: Use existing `testUser` fixture, then call `setupTestUserState()` or `awardAchievements()` to modify it
   - **Option B - Create with state**: Use `createTestUserWithState()` to create a new user with initial state, then cleanup manually
   - Prefer Option A when you need a basic user that you'll modify, prefer Option B when you need a user in a specific state from the start
   - Use `awardAchievements()` to add achievements without earning them naturally
   - Use `setUserLevelDirectly()` to set user level bypassing requirements

2. **Test Isolation**: Ensure each test creates its own test user and cleans up after itself (handled by fixtures). The test setup functions work with the existing `testUser` fixture pattern.

3. **User State Setup**: For UI tests, set up users in the expected state BEFORE testing UI elements:
   - Achievement display tests: Award achievements directly using `awardAchievements()`
   - Level up tests: Set user to level N-1 with all required achievements using `setupUserForLevelUp()`
   - Test eligibility tests: Set user level and award required achievements for test eligibility

4. **Timing**: Some tests may need delays to allow backend processing. Use `waitForTimeout` sparingly, prefer `waitForSelector` or `waitForResponse`.

5. **Test IDs**: All interactive UI elements should have `data-testid` attributes for reliable test targeting. Follow the naming convention `testid-{component}-{purpose}`.

6. **Dev-Only Endpoints**: The test setup endpoint (`/api/users/<id>/test-setup`) is only available in dev/test mode. It will return 403 in production. This is intentional for security.

