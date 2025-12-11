# Achievement Logic Fixes Required

**Created:** 2025-12-11  
**Status:** Pending Implementation

## Overview

This document identifies incorrect business logic in the achievement system that needs to be fixed. These are separate from the structural refactoring work and represent fundamental logic errors in how achievements are awarded and checked.

---

## 1. Level Master Achievement Logic

### Current Implementation (INCORRECT)

**File:** `backend/app/services/achievements/achievement_checkers/level_master_checker.py`

**Current Behavior:**
- Finds the maximum consecutive correct count across ALL levels
- Awards ONE global achievement (highest tier) based on the best streak across all levels
- Does NOT award per-level achievements
- Does NOT store level metadata

**Example of Current Behavior:**
- User gets 30 consecutive correct at level 1 → No achievement
- User gets 60 consecutive correct at level 2 → Awards `level-master-silver` (one global achievement)
- User can only have ONE level-master achievement per tier

### Correct Implementation (REQUIRED)

**Expected Behavior:**
- Track consecutive correct separately for EACH level
- Award separate achievements per level with metadata `{level: N}`
- A single session can grant multiple Level Master achievements (one per level that crosses threshold)
- User can have `level-master-bronze` for level 1, `level-master-silver` for level 2, etc.
- Each level can only have ONE tier (if user reaches silver for level 1, they can't also have bronze for level 1)
- If user reaches silver (60) then misses a question, the streak resets for that level

**Example of Correct Behavior:**
- User gets 30 consecutive correct at level 1 → Awards `level-master-bronze` with metadata `{level: 1}`
- User gets 60 consecutive correct at level 2 → Awards `level-master-silver` with metadata `{level: 2}`
- User can have multiple level-master achievements, each with different level metadata

**Key Requirements:**
1. Track streaks per level independently
2. Award achievements per level when threshold is crossed
3. Store metadata `{"level": N}` for each achievement
4. Only award highest tier per level (if silver is reached, don't also award bronze)
5. Reset streak for a level when user gets a question wrong at that level

**Database Constraint Issue:**
- Current unique constraint: `(user_id, code)` prevents multiple `level-master-bronze` achievements with different metadata
- **Solution Required:** Either:
  - Include metadata in unique constraint: `(user_id, code, achievement_metadata)`
  - Or use different code structure: `level-master-bronze-level-1`, `level-master-bronze-level-2`, etc.

---

## 2. Level Grandmaster Achievement Logic

### Current Implementation (INCORRECT)

**File:** `backend/app/services/achievements/achievement_checkers/level_grandmaster_checker.py`

**Current Behavior:**
- Checks if user has `level-master-bronze` achievement (prerequisite check)
- Then INDEPENDENTLY recalculates consecutive correct counts for each level
- Verifies that each level has at least 30 consecutive correct
- Does NOT check for existing Level Master achievements with metadata

**Example of Current Behavior:**
- User has `level-master-bronze` (global achievement)
- Checker recalculates: "Does user have 30 consecutive at level 1? Yes. Level 2? Yes. Level 3? No."
- Does NOT award Level Grandmaster

### Correct Implementation (REQUIRED)

**Expected Behavior:**
- Check if user has Level Master (Bronze) achievement with metadata for EACH level
- Simply verify existence of achievements: `level-master-bronze` with `{level: 1}`, `{level: 2}`, etc.
- NO independent quantity checks needed - the Level Master achievements already verify the quantity
- Award Level Grandmaster (Bronze) when user has Level Master (Bronze) for all defined levels

**Example of Correct Behavior:**
- User has `level-master-bronze` with `{level: 1}`
- User has `level-master-bronze` with `{level: 2}`
- User has `level-master-bronze` with `{level: 3}`
- Checker verifies: "Does user have level-master-bronze for level 1? Yes. Level 2? Yes. Level 3? Yes."
- Awards `level-grandmaster-bronze`

**Key Requirements:**
1. Check for existing Level Master (Bronze) achievements with metadata
2. Verify one achievement exists per level (levels 1 through max level)
3. NO recalculation of consecutive counts
4. NO quantity checks - just existence checks
5. Each tier can only be awarded once (user can't have multiple level-grandmaster-bronze)

**Levels to Check:**
- Should check all levels defined in `LEVELS_CONFIG` (1-45)
- Or check all levels that have questions in the database (current implementation)
- **Decision Needed:** Which approach is correct?

---

## 3. Human Calculator Achievement Logic

### Current Implementation (CORRECT)

**File:** `backend/app/services/achievements/achievement_checkers/human_calculator_checker.py`

**Current Behavior:**
- Checks for existing Lightning Fast (Bronze/Silver) achievements with metadata for each level
- Verifies one achievement exists per level
- NO independent quantity checks
- Correctly handles tier substitution (silver qualifies for bronze requirement)

**Status:** ✅ **This implementation is CORRECT**

**Example of Current Behavior:**
- User has `lightning-fast-bronze` with `{level: 1}`
- User has `lightning-fast-bronze` with `{level: 2}`
- User has `lightning-fast-silver` with `{level: 3}` (higher tier qualifies)
- Checker verifies: "Does user have lightning-fast-bronze (or higher) for level 1? Yes. Level 2? Yes. Level 3? Yes."
- Awards `human-calculator-bronze`

**Key Requirements (Already Met):**
1. ✅ Check for existing Lightning Fast achievements with metadata
2. ✅ Verify one achievement exists per level
3. ✅ NO recalculation of speed metrics
4. ✅ NO quantity checks - just existence checks
5. ✅ Handles tier substitution (silver qualifies for bronze)

---

## 4. Lightning Fast Achievement Logic

### Current Implementation (CORRECT)

**File:** `backend/app/services/achievements/achievement_checkers/lightning_fast_checker.py`

**Current Behavior:**
- Calculates average speed per level from user's responses
- Awards level-specific achievements with metadata `{level: N}`
- Awards highest qualifying tier per level
- Stores metadata correctly

**Status:** ✅ **This implementation is CORRECT**

**Example of Current Behavior:**
- User completes 50 questions at level 1 with <5s average → Awards `lightning-fast-bronze` with `{level: 1}`
- User completes 100 questions at level 2 with <4s average → Awards `lightning-fast-silver` with `{level: 2}`
- Each level gets its own achievement with metadata

**Key Requirements (Already Met):**
1. ✅ Track speed per level independently
2. ✅ Award achievements per level when threshold is crossed
3. ✅ Store metadata `{"level": N}` for each achievement
4. ✅ Only award highest tier per level

---

## 5. Summary of Required Fixes

### Priority 1: Level Master Checker
- **File:** `level_master_checker.py`
- **Issue:** Awards one global achievement instead of per-level achievements
- **Fix:** Track streaks per level, award separate achievements with metadata
- **Database:** May need schema change for unique constraint

### Priority 2: Level Grandmaster Checker
- **File:** `level_grandmaster_checker.py`
- **Issue:** Recalculates consecutive counts instead of checking existing achievements
- **Fix:** Check for existing Level Master (Bronze) achievements with metadata for each level
- **Dependency:** Requires Level Master Checker to be fixed first

### Priority 3: Human Calculator Checker
- **File:** `human_calculator_checker.py`
- **Status:** ✅ Already correct - no changes needed

### Priority 4: Lightning Fast Checker
- **File:** `lightning_fast_checker.py`
- **Status:** ✅ Already correct - no changes needed

---

## 6. Database Schema Considerations

### Current Constraint
```sql
UNIQUE CONSTRAINT (user_id, code)
```

### Problem
This prevents multiple achievements with the same code but different metadata:
- Cannot have `level-master-bronze` with `{level: 1}` AND `{level: 2}`
- Cannot have `lightning-fast-bronze` with `{level: 1}` AND `{level: 2}`

### Solutions

**Option 1: Include Metadata in Unique Constraint**
```sql
UNIQUE CONSTRAINT (user_id, code, achievement_metadata)
```
- Pros: Allows multiple achievements with same code, different metadata
- Cons: Requires migration, metadata must be normalized (sorted keys)

**Option 2: Different Code Structure**
- Use codes like `level-master-bronze-level-1`, `level-master-bronze-level-2`
- Pros: Works with current constraint
- Cons: More complex code generation, harder to query

**Option 3: Composite Key Table**
- Separate table for level-specific achievements
- Pros: Clean separation
- Cons: Major schema change, more complex queries

**Recommendation:** Option 1 (include metadata in unique constraint) is the cleanest solution.

---

## 7. Test Requirements

### Level Master Tests Needed
1. Test that achievements are awarded per level with metadata
2. Test that multiple levels can have achievements in the same session
3. Test that only highest tier is awarded per level
4. Test that streak resets when user gets question wrong at that level
5. Test that different levels can have different tiers

### Level Grandmaster Tests Needed
1. Test that it checks for existing Level Master achievements with metadata
2. Test that it does NOT recalculate consecutive counts
3. Test that it awards when all levels have Level Master (Bronze)
4. Test that it does NOT award when one level is missing
5. Test tier substitution (if Level Master Silver exists, it qualifies for Bronze requirement)

### Human Calculator Tests Needed
1. ✅ Already has tests (though limited due to schema constraint)
2. Test that it checks for existing Lightning Fast achievements with metadata
3. Test that it does NOT recalculate speed metrics
4. Test tier substitution

---

## 8. Implementation Notes

### Level Master Checker Changes

**Current Logic:**
```python
# Finds max across all levels
max_consecutive_any_level = max(max_consecutive_any_level, max_consecutive)
# Awards one achievement
achievement = AchievementService.create_achievement(...)
```

**Required Logic:**
```python
# Track streaks per level
for target_level in all_levels:
    level_responses = get_responses_for_level(target_level)
    max_consecutive = calculate_max_consecutive(level_responses)
    
    # Check if user already has achievement for this level
    existing = check_existing_achievement(user_id, "level-master-*", {level: target_level})
    
    # Award highest qualifying tier for this level
    if max_consecutive >= threshold:
        tier = determine_highest_tier(max_consecutive)
        if not existing or existing.tier < tier:
            award_achievement(user_id, f"level-master-{tier}", {level: target_level})
```

### Level Grandmaster Checker Changes

**Current Logic:**
```python
# Recalculates consecutive counts
for target_level in all_levels:
    level_responses = get_responses_for_level(target_level)
    max_consecutive = calculate_max_consecutive(level_responses)
    if max_consecutive < 30:
        return []  # Not qualified
```

**Required Logic:**
```python
# Check for existing achievements
for target_level in all_levels:
    achievement = find_achievement(user_id, "level-master-bronze", {level: target_level})
    if not achievement:
        # Also check if silver/gold exists (higher tier qualifies)
        achievement = find_achievement(user_id, "level-master-silver", {level: target_level})
        if not achievement:
            achievement = find_achievement(user_id, "level-master-gold", {level: target_level})
    if not achievement:
        return []  # Not qualified
```

---

## 9. Related Files

### Checkers
- `backend/app/services/achievements/achievement_checkers/level_master_checker.py` - **NEEDS FIX**
- `backend/app/services/achievements/achievement_checkers/level_grandmaster_checker.py` - **NEEDS FIX**
- `backend/app/services/achievements/achievement_checkers/human_calculator_checker.py` - ✅ Correct
- `backend/app/services/achievements/achievement_checkers/lightning_fast_checker.py` - ✅ Correct

### Tests
- `backend/tests/test_level_grandmaster_checker.py` - Test skipped, needs update
- `backend/tests/test_human_calculator_achievements.py` - Tests exist but limited by schema
- `backend/tests/test_level_master_achievements.py` - May need updates after fix

### Config
- `backend/app/config/achievements/accuracy.py` - Level Master achievement definitions
- `backend/app/config/achievements/milestone.py` - Level Grandmaster and Human Calculator definitions
- `backend/app/config/achievements/speed.py` - Lightning Fast achievement definitions
- `backend/app/config/level_progression_config.py` - References level-master with metadata filters

---

## 10. Migration Path

1. **Phase 1: Schema Update** (if needed)
   - Update unique constraint to include metadata
   - Migrate existing achievements if necessary

2. **Phase 2: Fix Level Master Checker**
   - Update to award per-level achievements
   - Add metadata support
   - Update tests

3. **Phase 3: Fix Level Grandmaster Checker**
   - Update to check existing achievements
   - Remove recalculation logic
   - Update tests

4. **Phase 4: Verification**
   - Run full test suite
   - Verify existing achievements still work
   - Check level progression requirements

---

## 11. Open Questions

1. **Levels to Check:** Should Level Grandmaster check:
   - All levels in `LEVELS_CONFIG` (1-45)?
   - All levels that have questions in the database?
   - All levels the user has attempted?

2. **Tier Substitution:** Should Level Grandmaster accept:
   - Only Bronze tier?
   - Bronze or higher (Silver/Gold qualify for Bronze requirement)?

3. **Schema Constraint:** Which solution for unique constraint:
   - Include metadata in constraint?
   - Different code structure?
   - Separate table?

4. **Existing Achievements:** How to handle users who already have global Level Master achievements?
   - Migrate to per-level achievements?
   - Keep both?
   - One-time conversion script?

---

## 12. References

- Level Master Config: `backend/app/config/achievements/accuracy.py`
- Level Grandmaster Config: `backend/app/config/achievements/milestone.py`
- Human Calculator Config: `backend/app/config/achievements/milestone.py`
- Lightning Fast Config: `backend/app/config/achievements/speed.py`
- Level Progression Config: `backend/app/config/level_progression_config.py` (shows expected metadata usage)



