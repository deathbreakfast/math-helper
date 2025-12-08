import { test, expect } from './fixtures/test-user'
import {
  getUser,
  navigateToJourneyTab,
  navigateToDashboard,
  getLevelUpEligibility,
  createTestUserWithState,
  deleteTestUser,
  waitForComponent,
  waitForDataLoad,
} from './helpers/test-helpers'

test.describe('Leveling', () => {
  test('LVL-001: Level up eligibility', async ({ page, request }) => {
    // Create user at level 1 with no achievements
    const testUser = await createTestUserWithState(request, {
      level: 1
      // No achievements - ensures predictable state
    })
    
    try {
      // Navigate directly to journey overview
      await navigateToJourneyTab(page, testUser.id, 'overview')
      
      // Check via API
      const eligibility = await getLevelUpEligibility(request, testUser.id)
      expect(eligibility).toHaveProperty('eligible')
      expect(eligibility).toHaveProperty('current_level')
      expect(eligibility).toHaveProperty('next_level')
      
      // Verify UI displays current level
      // Journey page shows level in JourneyHeader, not in LearnerStatsCards
      await waitForComponent(page, 'testid-current-level-display')
    } finally {
      // Cleanup
      await deleteTestUser(request, testUser.id)
    }
  })

  test('LVL-002: Level up achievement requirements display', async ({ page, request }) => {
    // Create user at level 1 with no achievements (ensures requirements are visible)
    const testUser = await createTestUserWithState(request, {
      level: 1
      // No achievements - ensures requirements are visible
    })
    
    try {
      // Navigate directly to levels tab
      await navigateToJourneyTab(page, testUser.id, 'levels')
      
      // Wait for levels tab and requirements to load
      await waitForComponent(page, 'testid-levels-tab')
      await waitForDataLoad(page, 'testid-levels-tab')
      
      // Wait for level requirements to load (lazy loaded)
      const requirementCards = page.locator('[data-testid^="testid-level-requirement-"]')
      await expect(requirementCards.first()).toBeVisible({ timeout: 10000 })
      
      // Verify level requirements are displayed
      const count = await requirementCards.count()
      expect(count).toBeGreaterThan(0)
    } finally {
      // Cleanup
      await deleteTestUser(request, testUser.id)
    }
  })

  test('LVL-003: Level up after requirements met', async ({ page, request }) => {
    // Create user at level 1 with all requirements for level 2
    // Level 2 requires (per level_progression_config.py):
    // 1. first-steps
    // 2. first-victory
    // 3. accuracy-ace-platinum with metadata {"test_type": "addition-1digit"}
    const testUser = await createTestUserWithState(request, {
      level: 1,
      achievements: [
        'first-steps' as any,
        'first-victory' as any,
        { code: 'accuracy-ace-platinum', metadata: { test_type: 'addition-1digit' } }
      ]
    })
    
    try {
      // Navigate directly to levels tab
      await navigateToJourneyTab(page, testUser.id, 'levels')
      
      // Wait for level requirements to load
      await waitForDataLoad(page, 'testid-levels-tab')
      const requirementCards = page.locator('[data-testid^="testid-level-requirement-"]')
      await expect(requirementCards.first()).toBeVisible({ timeout: 10000 })
      
      // Verify level up button/eligibility
      const eligibility = await getLevelUpEligibility(request, testUser.id)
      expect(eligibility.eligible).toBe(true)
      
      // Attempt level up via API
      const levelUpResponse = await request.post(`/api/users/${testUser.id}/level-up`)
      expect(levelUpResponse.ok()).toBe(true)
      
      // Verify level increased
      const userAfter = await getUser(request, testUser.id)
      expect(userAfter?.level).toBe(2)
    } finally {
      // Cleanup
      await deleteTestUser(request, testUser.id)
    }
  })

  test('LVL-004: Level up blocks when requirements not met', async ({ page, request }) => {
    // Create user without required achievements
    const testUser = await createTestUserWithState(request, {
      level: 1
      // No achievements - should not be able to level up
    })
    
    try {
      // Navigate directly to levels tab
      await navigateToJourneyTab(page, testUser.id, 'levels')
      
      // Wait for level requirements to load
      await waitForDataLoad(page, 'testid-levels-tab')
      const requirementCards = page.locator('[data-testid^="testid-level-requirement-"]')
      await expect(requirementCards.first()).toBeVisible({ timeout: 10000 })
      
      // Check eligibility via API
      const eligibility = await getLevelUpEligibility(request, testUser.id)
      expect(eligibility.eligible).toBe(false)
      
      // Try to level up anyway
      const levelUpResponse = await request.post(`/api/users/${testUser.id}/level-up`)
      
      // Should fail with 400
      expect(levelUpResponse.status()).toBe(400)
      
      const result = await levelUpResponse.json()
      expect(result).toHaveProperty('success', false)
      expect(result).toHaveProperty('missing_achievements')
      
      // Verify UI shows missing requirements
      const count = await requirementCards.count()
      expect(count).toBeGreaterThan(0)
    } finally {
      // Cleanup
      await deleteTestUser(request, testUser.id)
    }
  })

  test('LVL-005: Missing achievements are listed in requirements', async ({ page, request }) => {
    // Create user at level 1 with no achievements (guarantees missing achievements exist)
    const testUser = await createTestUserWithState(request, {
      level: 1
      // No achievements - guarantees missing achievements exist
    })
    
    try {
      // Navigate directly to levels tab
      await navigateToJourneyTab(page, testUser.id, 'levels')
      
      // Wait for level requirements to load
      await waitForDataLoad(page, 'testid-levels-tab')
      const requirementCards = page.locator('[data-testid^="testid-level-requirement-"]')
      await expect(requirementCards.first()).toBeVisible({ timeout: 10000 })
      
      // Get eligibility via API
      const eligibility = await getLevelUpEligibility(request, testUser.id)
      
      // Verify missing achievements are shown in UI
      expect(eligibility.eligible).toBe(false)
      expect(eligibility.missing_achievements).toBeDefined()
      expect(eligibility.missing_achievements.length).toBeGreaterThan(0)
      
      // Get the level 1 requirement card (user is at level 1, so this shows requirements for level 2)
      const level1RequirementCard = page.getByTestId('testid-level-requirement-1')
      await expect(level1RequirementCard).toBeVisible({ timeout: 10000 })
      
      // Find all requirement items within the level 1 card
      const requirementItems = level1RequirementCard.locator('[data-testid^="testid-requirement-"]')
      const requirementCount = await requirementItems.count()
      expect(requirementCount).toBeGreaterThan(0)
      
      // For each missing achievement, verify it appears in at least one requirement's text
      for (const missingAchievement of eligibility.missing_achievements) {
        // Extract just the achievement code (strip quantity info like "(need 1, have 0)")
        // API returns: "accuracy-ace-platinum with metadata {'test_type': 'addition-1digit'} (need 1, have 0)"
        // UI shows: "Complete achievement: accuracy ace platinum (1 Digit Addition)"
        const achievementCode = missingAchievement.split(' (')[0] // Gets base code or code with metadata
        
        // Check if achievement code includes metadata
        // Format: "accuracy-ace-platinum with metadata {'test_type': 'addition-1digit'}"
        let baseCode = achievementCode
        let metadata: Record<string, any> | null = null
        
        if (achievementCode.includes(' with metadata ')) {
          const parts = achievementCode.split(' with metadata ')
          baseCode = parts[0]
          // Parse metadata from string like "{'test_type': 'addition-1digit'}"
          try {
            const metadataStr = parts[1].replace(/'/g, '"') // Convert single quotes to double quotes
            metadata = JSON.parse(metadataStr)
          } catch {
            // If parsing fails, try to extract test_type manually
            const testTypeMatch = achievementCode.match(/test_type['"]:\s*['"]([^'"]+)['"]/)
            if (testTypeMatch) {
              metadata = { test_type: testTypeMatch[1] }
            }
          }
        }
        
        // The UI displays achievement codes with hyphens replaced by spaces
        // e.g., "accuracy-ace-platinum" becomes "accuracy ace platinum"
        // If metadata has test_type, UI shows: "Complete achievement: accuracy ace platinum (1 Digit Addition)"
        const normalizedCode = baseCode.replace(/-/g, ' ')
        
        // Get test display name if metadata has test_type
        let testDisplayName: string | null = null
        if (metadata?.test_type) {
          // Map test_type to display name
          const testTypeMap: Record<string, string> = {
            'addition-1digit': '1 Digit Addition',
            'addition-1digit-zeros': '1 Digit Addition w/ Zeros',
            'addition-2digit': '2 Digit Addition',
            'subtraction-1digit': '1 Digit Subtraction',
            'subtraction-1digit-zeros': '1 Digit Subtraction w/ Zeros',
            'subtraction-2digit': '2 Digit Subtraction',
            // Add more mappings as needed
          }
          testDisplayName = testTypeMap[metadata.test_type] || metadata.test_type.replace(/-/g, ' ')
        }
        
        // Debug logging
        console.log(`[LVL-005] Looking for missing achievement: "${missingAchievement}"`)
        console.log(`[LVL-005] Extracted achievement code: "${achievementCode}"`)
        console.log(`[LVL-005] Base code: "${baseCode}"`)
        console.log(`[LVL-005] Normalized code: "${normalizedCode}"`)
        console.log(`[LVL-005] Metadata:`, metadata)
        console.log(`[LVL-005] Test display name:`, testDisplayName)
        
        // Check if any requirement item contains this achievement code (in either format)
        // The UI may show it as "Complete achievement: {code}" or "Complete achievement: {code} ({test_name})"
        let found = false
        for (let i = 0; i < requirementCount; i++) {
          const requirementItem = requirementItems.nth(i)
          
          // Try to get text from the description element specifically (button or paragraph)
          // The description is in a div with class "flex-1" containing either a button or p element
          const descriptionElement = requirementItem.locator('.flex-1 button, .flex-1 p').first()
          const hasDescriptionElement = await descriptionElement.count() > 0
          
          let text: string | null = null
          if (hasDescriptionElement) {
            // Get text from the description element specifically
            text = await descriptionElement.textContent()
            console.log(`[LVL-005] Requirement ${i} description element text: "${text}"`)
          } else {
            // Fallback to getting text from the entire requirement item
            text = await requirementItem.textContent()
            console.log(`[LVL-005] Requirement ${i} full text (fallback): "${text}"`)
          }
          
          if (text) {
            // Normalize text: trim whitespace and replace multiple spaces/newlines with single space
            const normalizedText = text.replace(/\s+/g, ' ').trim()
            const lowerText = normalizedText.toLowerCase()
            const lowerCode = baseCode.toLowerCase()
            const lowerNormalized = normalizedCode.toLowerCase()
            
            // Debug logging for each requirement item
            console.log(`[LVL-005] Requirement ${i} normalized text: "${normalizedText}"`)
            console.log(`[LVL-005] Requirement ${i} lowerText: "${lowerText}"`)
            
            // Patterns to check
            const patterns = [
              lowerCode,
              lowerNormalized,
              `complete achievement: ${lowerNormalized}`,
              `complete: ${lowerNormalized}`
            ]
            
            // If metadata has test_type, also check for pattern with test display name
            if (testDisplayName) {
              patterns.push(
                `complete achievement: ${lowerNormalized} (${testDisplayName.toLowerCase()})`,
                `complete: ${lowerNormalized} (${testDisplayName.toLowerCase()})`
              )
            }
            
            // If metadata has level, also check for pattern with level
            if (metadata?.level) {
              patterns.push(
                `complete achievement: ${lowerNormalized} (level ${metadata.level})`,
                `complete: ${lowerNormalized} (level ${metadata.level})`
              )
            }
            
            console.log(`[LVL-005] Checking patterns:`, patterns)
            
            // Match if text contains the code (with or without hyphens) or the normalized version
            let matched = false
            for (const pattern of patterns) {
              if (lowerText.includes(pattern)) {
                console.log(`[LVL-005] ✓ Matched pattern: "${pattern}"`)
                matched = true
                break
              } else {
                console.log(`[LVL-005] ✗ Pattern "${pattern}" not found`)
              }
            }
            
            if (matched) {
              found = true
              break
            }
          } else {
            console.log(`[LVL-005] Requirement ${i} has no text content`)
          }
        }
        
        console.log(`[LVL-005] Final result for "${missingAchievement}": found=${found}`)
        expect(found).toBe(true)
      }
    } finally {
      // Cleanup
      await deleteTestUser(request, testUser.id)
    }
  })

  test('LVL-006: Level progression path shows correct next level', async ({ page, request }) => {
    // Create user at level 2 (ensures predictable progression to level 3)
    const testUser = await createTestUserWithState(request, {
      level: 2
      // No achievements - ensures predictable progression state
    })
    
    try {
      // Navigate directly to levels tab
      await navigateToJourneyTab(page, testUser.id, 'levels')
      
      // Wait for level requirements to load
      await waitForDataLoad(page, 'testid-levels-tab')
      const requirementCards = page.locator('[data-testid^="testid-level-requirement-"]')
      await expect(requirementCards.first()).toBeVisible({ timeout: 10000 })
      
      const eligibility = await getLevelUpEligibility(request, testUser.id)
      
      // Verify progression header shows next level
      await waitForComponent(page, 'testid-level-progression-header')
      
      // Verify current level is displayed correctly
      const currentLevelText = page.locator(`text=/level.*${eligibility.current_level}/i`)
      await expect(currentLevelText.first()).toBeVisible()
    } finally {
      // Cleanup
      await deleteTestUser(request, testUser.id)
    }
  })
})


