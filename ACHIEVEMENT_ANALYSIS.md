# Achievement Analysis

This document provides a comprehensive analysis of each achievement and its test coverage.

## First Steps

Achievement description: Answer your first question

### Expected Behavior

- Awarded when user answers their first question
- Should only be awarded once (unique achievement)
- Should not be awarded multiple times per session
- Requires minimum 1 question answered

### Test Coverage
Summary: Tests verify that first-steps is awarded on first question and only once.
Number of tests: 2

#### test_first_steps_achievement (ACH-AWARD-002)

Test description: Verifies first-steps achievement is awarded after 10 addition problems at level 1

Test setup: Creates 10 addition questions at level 1, all answered correctly

What is done to test: Creates a session with 10 correct responses, then calls AchievementService.ensure_achievements

What is expected in test: Achievement with code "first-steps" should be awarded

#### test_first_steps_only_awarded_once

Test description: Verifies first-steps is only awarded once, not on subsequent sessions

Test setup: Creates two separate sessions, each with 1 question answered correctly

What is done to test: Creates first session and checks achievements, then creates second session and checks again

What is expected in test: Only one first-steps achievement should exist after both sessions

### Changes

> Test description: Verifies first-steps achievement is awarded after 10 addition problems at level 1

Level one? This should be a math concept, what concept is it using?

---

## First Victory

Achievement description: Complete your first session

### Expected Behavior

- Awarded when user completes their first session
- Should only be awarded once (unique achievement)
- Should not be awarded multiple times per session
- Requires session to be completed (completed_at must be set)
- Should not be awarded for incomplete sessions

### Test Coverage
Summary: Tests verify that first-victory is awarded on first completed session and only once, and not for incomplete sessions.
Number of tests: 3

#### test_first_victory_achievement (ACH-AWARD-001)

Test description: Verifies first-victory achievement is awarded after answering 1 question in a completed session

Test setup: Creates 1 question and answer it correctly in a completed session

What is done to test: Creates a session with 1 correct response, then calls AchievementService.ensure_achievements

What is expected in test: Achievement with code "first-victory" should be awarded and linked to the session

#### test_first_victory_only_awarded_once

Test description: Verifies first-victory is only awarded once, not on subsequent sessions

Test setup: Creates two separate completed sessions, each with 1 question answered correctly

What is done to test: Creates first session and checks achievements, then creates second session and checks again

What is expected in test: Only one first-victory achievement should exist after both sessions

#### test_first_victory_not_awarded_on_incomplete_session

Test description: Verifies first-victory is NOT awarded when session is not completed

Test setup: Creates a session with responses but sets completed_at to None

What is done to test: Creates an incomplete session, then calls AchievementService.ensure_achievements

What is expected in test: No first-victory achievement should be awarded

### Changes
Intentionally left blank for after review.

---

## Question Master

Achievement description: Answer X+ total questions (tiered: 100, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000, 250000, 250000+champion)

### Expected Behavior

- Awarded based on total lifetime questions answered
- 11 tiers: bronze (100), silver (500), gold (1000), platinum (2500), diamond (5000), master (10000), grandmaster (25000), legendary (50000), mythic (100000), divine (250000), champion (250000+server record)
- Should award only the highest qualifying tier
- Counts questions across all sessions
- Champion tier requires server record check

### Test Coverage
Summary: Tests verify Question Master awards at different thresholds and only awards highest tier.
Number of tests: 4

#### test_question_master_bronze_achievement (ACH-AWARD-003)

Test description: Verifies question-master-bronze is awarded after 100+ questions total

Test setup: Creates 110 questions split across multiple sessions (20 questions per session)

What is done to test: Creates multiple sessions totaling 110 responses, calls AchievementService.ensure_achievements after each session

What is expected in test: Achievement with code "question-master-bronze" should be awarded

#### test_question_master_bronze_100_questions

Test description: Verifies question-master-bronze is awarded for exactly 100+ questions

Test setup: Creates 110 questions split across multiple sessions

What is done to test: Creates multiple sessions totaling 110 responses, checks achievements after each session

What is expected in test: Achievement with code "question-master-bronze" should be awarded

#### test_question_master_silver_500_questions

Test description: Verifies question-master-silver is awarded for 500+ questions

Test setup: Creates 510 questions split across multiple sessions (50 questions per session)

What is done to test: Creates multiple sessions totaling 510 responses, checks achievements after each session

What is expected in test: Achievement with code "question-master-silver" should be awarded (not bronze)

#### test_question_master_only_highest_tier_awarded

Test description: Verifies only the highest qualifying tier is awarded

Test setup: Creates 1000 questions split across multiple sessions

What is done to test: Creates multiple sessions totaling 1000 responses, checks achievements

What is expected in test: Only gold should be awarded, not bronze or silver

### Changes

There seems to be a requirement that was dropped here. The user should only be awarded one of each tier.

Expected behavior: Awnser 100 questions -> get bronze -> Anwser 100 more -> have only 1 bronze tier award.
Let's make sure we have test coverage for multiple tiers and verify only one of each.

---

## Speed Demon

Achievement description: Average <X seconds per question (tiered: 5.0s, 4.0s, 3.0s, 2.7s, 2.4s, 2.1s, 1.8s, 1.5s, 1.3s, 1.2s, 1.2s+champion)

### Expected Behavior

- Awarded based on lifetime average speed across all questions
- 11 tiers with decreasing max speed requirements
- Requires minimum 10 questions to qualify
- Should award only the highest qualifying tier
- Champion tier requires server record check (fastest on server)
- Speed multiplier from concept should be applied (e.g., 1.1x multiplier means 5.5s qualifies for bronze threshold of 5.0s)
- Uses lifetime average, not just session average

### Test Coverage
Summary: Tests verify Speed Demon awards at different speed thresholds, respects minimum questions, applies multipliers, and handles champion/divine flow.
Number of tests: 5

#### test_speed_demon_bronze_achievement (ACH-AWARD-005)

Test description: Verifies speed-demon-bronze is awarded for avg < 5.0s with 10+ questions

Test setup: Creates 10 questions with average time 4.5s per question

What is done to test: Creates session with 10 responses at 4.5s each, calls AchievementService.ensure_achievements

What is expected in test: Achievement with code "speed-demon-bronze" should be awarded

#### test_speed_demon_with_multiplier

Test description: Verifies speed multiplier is applied correctly (1.1x multiplier means 5.4s qualifies for bronze)

Test setup: Creates 10 questions with average time 5.4s, uses concept_id "c_add_3s" which has 1.1x speed multiplier

What is done to test: Creates session with concept_id "c_add_3s", calls AchievementService.ensure_achievements

What is expected in test: Achievement should be awarded because 5.4s < 5.0s * 1.1 = 5.5s

#### test_speed_demon_gold_achievement (ACH-AWARD-006)

Test description: Verifies speed-demon-gold is awarded for avg < 3.0s with 10+ questions

Test setup: Creates 10 questions with average time 2.8s per question

What is done to test: Creates session with 10 responses at 2.8s each, calls AchievementService.ensure_achievements

What is expected in test: Achievement with code "speed-demon-gold" (or higher) should be awarded

#### test_speed_demon_champion_divine_flow

Test description: Verifies champion/divine flow: champion when setting record, divine when qualifying but not breaking record, champion again when breaking record

Test setup: Creates three sessions: 1) 1500 questions at 1.1s (sets record), 2) 1500 questions at 1.15s (qualifies but doesn't break), 3) 1500 questions at 1.0s (breaks record)

What is done to test: Creates each session sequentially, checks achievements and server records after each

What is expected in test: Session 1 should award champion and set server record, session 2 should award divine (not champion), session 3 should award champion again and update record

### Changes
> - Awarded based on lifetime average speed across all questions

This is incorrect. It should be awarded based on the average speed of the session.

This seems to have a missing test, only one tier (the highest) should be awarded each session.

---

## Perfect Streak

Achievement description: X consecutive perfect sessions (100% accuracy) - awarded once per uninterrupted run (tiered: 3, 5, 10, 20, 50, 100, 250, 500, 1000, 2500, 2500+champion)

### Expected Behavior

- Awarded for consecutive perfect sessions (100% accuracy)
- 11 tiers with increasing session requirements
- Awarded once per uninterrupted run (not per session)
- When streak is broken by an imperfect session, a new run starts
- Can be re-awarded after a run is broken
- Only highest qualifying tier should be awarded per run
- Bronze should be awarded on 3rd perfect session, not on 4th if already awarded for this run

### Test Coverage
Summary: Tests verify Perfect Streak awards for consecutive perfect sessions, breaks on imperfect sessions, and can be re-earned.
Number of tests: 5

#### test_perfect_streak_bronze_achievement (ACH-AWARD-007)

Test description: Verifies perfect-streak-bronze is awarded for 3 consecutive perfect sessions

Test setup: Creates 3 consecutive sessions, each with 10 questions all answered correctly (100% accuracy)

What is done to test: Creates 3 perfect sessions sequentially, calls AchievementService.ensure_achievements after each

What is expected in test: Achievement with code "perfect-streak-bronze" should be awarded after 3rd session

#### test_perfect_streak_silver_5_sessions

Test description: Verifies perfect-streak-silver is awarded for 5 consecutive perfect sessions

Test setup: Creates 5 consecutive sessions, each with 10 questions all answered correctly

What is done to test: Creates 5 perfect sessions sequentially, calls AchievementService.ensure_achievements after each

What is expected in test: Achievement with code "perfect-streak-silver" should be awarded after 5th session

#### test_perfect_streak_broken_by_imperfect_session

Test description: Verifies one imperfect session breaks the perfect streak

Test setup: Creates 2 perfect sessions, then 1 imperfect session (9/10 correct)

What is done to test: Creates 2 perfect sessions, then 1 imperfect session, checks achievements

What is expected in test: No perfect-streak achievement should be awarded (streak broken before reaching 3)

#### test_perfect_streak_silver_with_bronze_exists_once

Test description: Verifies that when silver is awarded, exactly one bronze exists and bronze was NOT awarded/linked in the silver-award session

Test setup: Creates 5 consecutive perfect sessions

What is done to test: Creates 5 perfect sessions, checks achievements after each

What is expected in test: Silver should be awarded, exactly one bronze should exist, bronze should NOT be linked to session 5

#### test_perfect_streak_broken_then_re_earned_bronze

Test description: Verifies perfect streak can be re-earned after being broken

Test setup: Creates 3 perfect sessions (awards bronze), then 1 imperfect session (breaks streak), then 3 more perfect sessions

What is done to test: Creates sessions sequentially, checks achievements after each

What is expected in test: Bronze awarded after first 3, streak broken, bronze awarded again after 3 more perfect sessions (total bronze count = 2)

### Changes
Intentionally left blank for after review.

---

## Week Warrior

Achievement description: Complete a X day streak (tiered: 7, 14, 30, 60, 90, 180, 365, 730, 1000, 2000, 2000+champion)

### Expected Behavior

- Awarded for consecutive days with practice
- 11 tiers with increasing day requirements
- Streak is calculated from Response.answered_at dates
- Missing a day breaks the streak
- Requires daily stats to be aggregated
- Champion tier requires server record check

### Test Coverage
Summary: Tests verify Week Warrior awards for consecutive day streaks and breaks when a day is missed.
Number of tests: 3

#### test_week_warrior_bronze_achievement (ACH-AWARD-008)

Test description: Verifies week-warrior-bronze is awarded for 7 consecutive days with practice

Test setup: Creates responses on 7 consecutive days, aggregates daily stats for each day

What is done to test: Creates Response objects with answered_at dates spanning 7 days, calls AnalyticsService.aggregate_daily_stats for each day, then calls AchievementService.ensure_achievements

What is expected in test: Achievement with code "week-warrior-bronze" should be awarded

#### test_week_warrior_silver_14_days

Test description: Verifies week-warrior-silver is awarded for 14 consecutive days

Test setup: Creates responses on 14 consecutive days, aggregates daily stats for each day

What is done to test: Creates Response objects with answered_at dates spanning 14 days, calls AnalyticsService.aggregate_daily_stats for each day, then calls AchievementService.ensure_achievements

What is expected in test: Achievement with code "week-warrior-silver" should be awarded

#### test_week_warrior_streak_broken

Test description: Verifies missing a day breaks the streak

Test setup: Creates responses on 6 consecutive days, skips a day, then creates 1 more response

What is done to test: Creates Response objects with a gap in dates, aggregates daily stats, then calls AchievementService.ensure_achievements

What is expected in test: No week-warrior achievement should be awarded (streak broken)

### Changes
Intentionally left blank for after review.

---

## Level Master

Achievement description: X consecutive correct at any level (tiered: 30, 60, 120, 240, 480, 960, 1920, 3840, 7680, 15360, 15360+champion)

### Expected Behavior

- Awarded for consecutive correct answers at a specific level/concept
- 11 tiers with increasing consecutive requirements
- Should be tracked per concept_id (metadata)
- Only highest qualifying tier should be awarded
- Can be awarded multiple times for different concepts
- An incorrect answer breaks the streak
- 30 correct + 1 incorrect should still award bronze (max consecutive is 30)
- 29 correct + 1 incorrect should NOT award (max consecutive is 29)

### Test Coverage
Summary: Tests verify Level Master awards for consecutive correct answers, tracks per concept, and only awards highest tier.
Number of tests: 9

#### test_level_master_bronze_exactly_30

Test description: Verifies exactly 30 correct in a row awards Level Master (Bronze) with metadata

Test setup: Creates 30 questions at level 1, all answered correctly

What is done to test: Creates session with 30 correct responses, calls AchievementService.check_level_master_achievements

What is expected in test: Achievement with code "level-master-bronze" should be awarded with metadata containing concept_id

#### test_level_master_silver_exactly_60

Test description: Verifies exactly 60 correct in a row awards Level Master (Silver) only (highest tier) with metadata

Test setup: Creates 60 questions at level 1, all answered correctly

What is done to test: Creates session with 60 correct responses, calls AchievementService.check_level_master_achievements

What is expected in test: Only silver should be awarded (not bronze), with metadata containing concept_id

#### test_level_master_negative_29_correct_1_incorrect

Test description: Verifies 29 correct + 1 incorrect does NOT award Level Master

Test setup: Creates 30 questions: 29 correct, 1 incorrect

What is done to test: Creates session with 29 correct and 1 incorrect response, calls AchievementService.check_level_master_achievements

What is expected in test: No level-master achievement should be awarded

#### test_level_master_negative_30_correct_1_incorrect

Test description: Verifies 30 correct + 1 incorrect DOES award Level Master (max consecutive is 30) with metadata

Test setup: Creates 31 questions: 30 correct, then 1 incorrect

What is done to test: Creates session with 30 correct followed by 1 incorrect, calls AchievementService.check_level_master_achievements

What is expected in test: Achievement with code "level-master-bronze" should be awarded (max consecutive is 30)

#### test_level_master_multiple_awards_30_wrong_30

Test description: Verifies 30 correct → bronze → 1 wrong → 30 correct → bronze (multiple awards)

Test setup: Creates 30 correct, then 1 incorrect, then 30 more correct

What is done to test: Creates sessions sequentially, calls AchievementService.check_level_master_achievements after each

What is expected in test: Should have at least one bronze achievement (may have multiple if implementation allows)

#### test_level_master_only_bronze_silver_tested

Test description: Verifies only the highest qualifying tier is awarded (gold for 120 consecutive) with metadata

Test setup: Creates 120 questions at level 1, all answered correctly

What is done to test: Creates session with 120 correct responses, calls AchievementService.check_level_master_achievements

What is expected in test: Only gold should be awarded (not bronze or silver), with metadata containing concept_id

#### test_level_master_multiple_levels

Test description: Verifies achievements are awarded per level, and multiple levels can have achievements

Test setup: Creates 30 correct at level 1, then 30 correct at level 2

What is done to test: Creates two sessions with different levels, calls AchievementService.check_level_master_achievements

What is expected in test: Both levels should have separate bronze achievements with different concept_id metadata

#### test_level_master_silver_not_awarded_mixed_concepts

Test description: Verifies Level Master Silver is NOT awarded when mixing different descriptive concepts

Test setup: Creates 40 questions with c_add_1s concept, then 10 questions with c_add_2s concept

What is done to test: Creates two sessions with different concept_ids, calls AchievementService.check_level_master_achievements

What is expected in test: Silver should NOT be awarded (only 40 consecutive from c_add_1s, not 60 from same concept)

#### test_level_master_concept_isolation

Test description: Verifies c_add_1s and c_add_2s achievements are tracked separately

Test setup: Creates 30 correct with c_add_1s, then 30 correct with c_add_2s

What is done to test: Creates two sessions with different concept_ids, calls AchievementService.check_level_master_achievements after each

What is expected in test: Both concepts should have separate bronze achievements with correct concept_id metadata

### Changes

NOTE: This should have been relabed to math master

> #### test_level_master_silver_exactly_60

We don't seem to have a test that verifies this over multiple sessions. We should do six sessions at 10 questions each. and ensure only one bronze and one silver exist.

> #### test_level_master_silver_not_awarded_mixed_concepts

Same here. Let's also try this across multiple sessions to verify the same thing.

---

## Lightning Fast

Achievement description: Average <X seconds per question at a specific level (tiered: 5.0s/50q, 4.0s/100q, 3.0s/150q, 2.7s/200q, 2.4s/300q, 2.1s/400q, 1.8s/500q, 1.5s/750q, 1.3s/1000q, 1.2s/1500q, 1.2s/1500q+champion)

### Expected Behavior

- Awarded for lifetime average speed at a specific level/concept
- 11 tiers with decreasing speed and increasing minimum question requirements
- Should be tracked per concept_id (metadata)
- Only correct answers are included in speed calculation
- Incorrect answers are excluded
- Uses lifetime average across all sessions for the concept
- Speed multiplier from concept should be applied
- Champion tier requires server record check
- Should work with descriptive concept IDs (e.g., c_add_1s) even when level is None

### Test Coverage
Summary: Tests verify Lightning Fast awards at different speed thresholds, respects minimum questions, excludes incorrect answers, uses lifetime average, and works with concept IDs.
Number of tests: 7

#### test_lightning_fast_bronze_minimum_questions

Test description: Verifies Lightning Fast (Bronze) requires 50 correct questions for a concept

Test setup: Creates 50 questions with fast correct answers (4s average), uses concept_id "c_add_1s"

What is done to test: Creates session with 50 correct responses at 4s each, calls AchievementService.check_lightning_fast_achievements

What is expected in test: Achievement with code "lightning-fast-bronze" should be awarded with metadata containing concept_id

#### test_lightning_fast_bronze_not_awarded_below_minimum

Test description: Verifies Lightning Fast (Bronze) is NOT awarded with less than 50 questions

Test setup: Creates 49 questions with fast correct answers (4s average)

What is done to test: Creates session with 49 correct responses, calls AchievementService.check_lightning_fast_achievements

What is expected in test: No lightning-fast achievement should be awarded

#### test_lightning_fast_silver_minimum_questions

Test description: Verifies Lightning Fast (Silver) requires 100 correct questions for a concept

Test setup: Creates 100 questions with fast correct answers (3.5s average), uses concept_id "c_add_1s"

What is done to test: Creates session with 100 correct responses at 3.5s each, calls AchievementService.check_lightning_fast_achievements

What is expected in test: Achievement with code "lightning-fast-silver" should be awarded (not bronze)

#### test_lightning_fast_excludes_incorrect_answers

Test description: Verifies incorrect answers are excluded from Lightning Fast speed calculation

Test setup: Creates 75 questions: 50 correct at 1s, 25 incorrect at 1s

What is done to test: Creates session with mixed correct/incorrect responses, calls AchievementService.check_lightning_fast_achievements

What is expected in test: Achievement should be awarded based on correct answers only (1s average with 50+ correct qualifies for bronze)

#### test_lightning_fast_negative_quick_incorrect_answers

Test description: Verifies answering questions quickly but incorrectly does NOT award Lightning Fast

Test setup: Creates 50 questions, all answered incorrectly but very quickly (0.5s)

What is done to test: Creates session with all incorrect responses, calls AchievementService.check_lightning_fast_achievements

What is expected in test: No lightning-fast achievement should be awarded (no correct answers to calculate speed from)

#### test_lightning_fast_lifetime_average

Test description: Verifies Lightning Fast uses lifetime average, not just session average

Test setup: Creates first session with 30 questions at 6s average, then second session with 20 questions at 2s average (total 50 at ~4.4s average)

What is done to test: Creates two sessions sequentially, calls AchievementService.check_lightning_fast_achievements after second session

What is expected in test: Achievement should be awarded based on lifetime average (4.4s qualifies for bronze with 50+ questions)

#### test_lightning_fast_with_descriptive_concept_id

Test description: Verifies Lightning Fast works with descriptive concept IDs (e.g., c_add_1s) even when level is None

Test setup: Creates 6 sessions with c_add_1s concept, each with ~10 questions at 1.3s average (total 60 questions)

What is done to test: Creates multiple sessions with concept_id "c_add_1s" and level=None, calls AchievementService.check_lightning_fast_achievements

What is expected in test: Achievement should be awarded (1.3s < 5.0s qualifies for bronze with 50+ questions), with metadata containing concept_id

### Changes

There should be a min number of questions correct before awarding. E.g. if only one question was correct, we shouldn't grant this if the others were incorrect. Let's say a min number of 9 questions. Make sure we have tests to verify this as well.

We are missing tests that verify only one lightning fast achievement per tier per math concept. E.g. there is no need to grant two bronze for add 1s as example.

---

## Accuracy Ace

Achievement description: Session accuracy of X% or higher (tiered: 80%, 90%, 100%)

### Expected Behavior

- Awarded per session based on session accuracy
- Only 3 tiers: bronze (80%), silver (90%), gold (100%)
- Requires minimum 10 questions in session
- Only highest qualifying tier should be awarded per session
- Can be awarded multiple times across different sessions (same tier)
- Only one per session (not multiple tiers in same session)

### Test Coverage
Summary: Tests verify Accuracy Ace awards at different accuracy thresholds, respects minimum questions, and only awards highest tier per session.
Number of tests: 6

#### test_accuracy_ace_bronze_achievement

Test description: Verifies Accuracy Ace (Bronze) is awarded for 80%+ accuracy with 10+ questions

Test setup: Creates 10 questions, answers 8 correctly (80% accuracy)

What is done to test: Creates session with 8 correct and 2 incorrect responses, calls AchievementService.check_accuracy_ace_achievements

What is expected in test: Achievement with code "accuracy-ace-bronze" should be awarded and linked to session

#### test_accuracy_ace_silver_achievement

Test description: Verifies Accuracy Ace (Silver) is awarded for 90%+ accuracy with 10+ questions

Test setup: Creates 10 questions, answers 9 correctly (90% accuracy)

What is done to test: Creates session with 9 correct and 1 incorrect response, calls AchievementService.check_accuracy_ace_achievements

What is expected in test: Achievement with code "accuracy-ace-silver" should be awarded (not bronze)

#### test_accuracy_ace_gold_achievement

Test description: Verifies Accuracy Ace (Gold) is awarded for 100% accuracy with 10+ questions

Test setup: Creates 10 questions, answers all correctly (100% accuracy)

What is done to test: Creates session with 10 correct responses, calls AchievementService.check_accuracy_ace_achievements

What is expected in test: Achievement with code "accuracy-ace-gold" should be awarded

#### test_accuracy_ace_minimum_questions_requirement

Test description: Verifies Accuracy Ace is NOT awarded with less than 10 questions

Test setup: Creates 9 questions, answers all correctly (100% accuracy but < 10 questions)

What is done to test: Creates session with 9 correct responses, calls AchievementService.check_accuracy_ace_achievements

What is expected in test: No accuracy-ace achievement should be awarded

#### test_accuracy_ace_not_awarded_below_threshold

Test description: Verifies Accuracy Ace is NOT awarded for accuracy below 80%

Test setup: Creates 10 questions, answers 7 correctly (70% accuracy)

What is done to test: Creates session with 7 correct and 3 incorrect responses, calls AchievementService.check_accuracy_ace_achievements

What is expected in test: No accuracy-ace achievement should be awarded

#### test_accuracy_ace_highest_tier_only

Test description: Verifies only the highest qualifying tier is awarded

Test setup: Creates 10 questions, answers all correctly (100% accuracy)

What is done to test: Creates session with 10 correct responses, calls AchievementService.check_accuracy_ace_achievements

What is expected in test: Only gold should be awarded (not bronze or silver)

### Changes
Intentionally left blank for after review.

---

## So, Wow!

Achievement description: Acquire your first X tier achievement (tiered: bronze, silver, gold, platinum, diamond, master, grandmaster, legendary, mythic, divine, champion)

### Expected Behavior

- Awarded when user earns their first achievement of a tier
- 11 tiers, one for each tier level
- Should be awarded once per tier (not per achievement)
- If user skips tiers (e.g., goes from bronze to gold), should award both silver and gold So, Wow! achievements
- Should not be awarded if user already has achievements of that tier

### Test Coverage
Summary: Tests verify So, Wow! awards when first achievement of a tier is earned, and only once per tier.
Number of tests: 5

#### test_so_wow_bronze_first_bronze_achievement

Test description: Verifies So, Wow! (Bronze) is awarded when user earns first bronze achievement

Test setup: Awards a bronze achievement directly (speed-demon-bronze)

What is done to test: Awards achievement, then calls AchievementService.check_so_wow_achievements

What is expected in test: Achievement with code "so-wow-bronze" should be awarded

#### test_so_wow_silver_first_silver_achievement

Test description: Verifies So, Wow! (Silver) is awarded when user earns first silver achievement

Test setup: Awards a silver achievement directly (speed-demon-silver)

What is done to test: Awards achievement, then calls AchievementService.check_so_wow_achievements

What is expected in test: Achievement with code "so-wow-silver" should be awarded

#### test_so_wow_multiple_tiers_one_session

Test description: Verifies multiple So, Wow! tiers can be awarded in one session

Test setup: Awards both bronze and silver achievements in one session

What is done to test: Awards both achievements, then calls AchievementService.check_so_wow_achievements

What is expected in test: Both so-wow-bronze and so-wow-silver should be awarded

#### test_so_wow_only_awarded_once_per_tier

Test description: Verifies So, Wow! is only awarded once per tier, not per achievement

Test setup: Awards first bronze achievement, then second bronze achievement

What is done to test: Awards first achievement and checks So, Wow!, then awards second achievement and checks again

What is expected in test: Only one so-wow-bronze should exist after both achievements

#### test_so_wow_not_awarded_if_tier_already_exists

Test description: Verifies So, Wow! is NOT awarded if user already has achievements of that tier

Test setup: Awards first bronze achievement (triggers So, Wow!), then awards second bronze achievement

What is done to test: Awards first achievement and checks So, Wow!, then awards second achievement and checks again

What is expected in test: No new So, Wow! achievement should be created (already exists)

### Changes
Intentionally left blank for after review.

---

## Level Grandmaster

Achievement description: Level Master (Bronze) on all levels

### Expected Behavior

- Awarded when user has Level Master (Bronze) achievement for all levels
- Requires checking all levels have the required achievement
- Can be awarded multiple times per tier and per session
- Should check metadata to ensure achievements are for different levels

### Test Coverage
Summary: Tests verify Level Grandmaster checker logic (full implementation tests may be limited).
Number of tests: Limited (checker tests exist but full scenario tests may be missing)

#### test_level_grandmaster_checker_verifies_all_levels

Test description: Verifies Level Grandmaster checker correctly verifies all levels are qualified

Test setup: Creates Level Master (Bronze) achievement for just one level

What is done to test: Creates achievement for one level, then calls checker

What is expected in test: Should NOT award Level Grandmaster (only 1 level qualified out of 45)

### Changes

Should be using math concepts.

We are missing tests to check that it doesn't grant for other combinations e.g. missing one achievement did we get granted grandmaster?

We are missing tests to ensure higher tiers can be substituted. E.g. All silver for all math concepts but one, then bronze on the last one. It should grant bronze.

---

## Human Calculator

Achievement description: Lightning Fast (Bronze) on all levels (Bronze tier) or Lightning Fast (Silver) on all levels (Silver tier)

### Expected Behavior

- Bronze tier: Requires Lightning Fast (Bronze) on all levels
- Silver tier: Requires Lightning Fast (Silver) on all levels
- Higher tiers can substitute (e.g., Silver qualifies for Bronze requirement)
- Should check metadata to ensure achievements are for different levels
- Can be awarded multiple times per tier and per session

### Test Coverage
Summary: Tests verify Human Calculator checker logic (full implementation tests may be limited).
Number of tests: 2

#### test_human_calculator_checker_verifies_all_levels

Test description: Verifies Human Calculator checker correctly verifies all levels are qualified

Test setup: Creates Lightning Fast (Bronze) achievement for just one level

What is done to test: Creates achievement for one level, then calls checker

What is expected in test: Should NOT award Human Calculator (only 1 level qualified out of 45)

#### test_human_calculator_bronze_accepts_silver_as_higher_tier

Test description: Verifies Human Calculator (Bronze) accepts Silver tier as qualifying (higher tier qualifies)

Test setup: Creates Lightning Fast (Silver) achievement for one level

What is done to test: Creates silver achievement, then calls checker for bronze tier

What is expected in test: Should NOT award (not all levels qualified), but should correctly identify that silver qualifies for bronze requirement

### Changes

Should be using math concepts.

---

## Master of Times Tables

Achievement description: Level Master (X tier) and Lightning Fast (X tier) on all multiplication tables (tiered: bronze through champion)

### Expected Behavior

- 11 tiers, each requiring Level Master and Lightning Fast at that tier (or higher) on all multiplication tables
- Should check metadata to identify multiplication table test types
- Champion tier requires server record check
- Can be awarded multiple times per tier and per session

### Test Coverage
Summary: Tests verify config existence (checker implementation may not be complete).
Number of tests: 3

#### test_master_of_times_tables_bronze_requirements

Test description: Verifies Master of Times Tables (Bronze) requires Level Master and Lightning Fast (Bronze) on all multiplication tables

Test setup: Checks achievement config exists

What is done to test: Verifies achievement exists in config and has correct requirement type

What is expected in test: Achievement should exist with type "master_of_times_tables" and required_tier "bronze"

#### test_master_of_times_tables_all_tiers

Test description: Verifies all tiers of Master of Times Tables are defined

Test setup: Checks achievement config for all tiers

What is done to test: Verifies each tier exists in config

What is expected in test: All 11 tiers should exist in config

### Changes
Intentionally left blank for after review.

---

## Master of Division Tables

Achievement description: Level Master (X tier) and Lightning Fast (X tier) on all division tables (tiered: bronze through champion)

### Expected Behavior

- 11 tiers, each requiring Level Master and Lightning Fast at that tier (or higher) on all division tables
- Should check metadata to identify division table test types
- Champion tier requires server record check
- Can be awarded multiple times per tier and per session

### Test Coverage
Summary: Tests verify config existence (checker implementation may not be complete).
Number of tests: 2

#### test_master_of_division_tables_bronze_requirements

Test description: Verifies Master of Division Tables (Bronze) requires Level Master and Lightning Fast (Bronze) on all division tables

Test setup: Checks achievement config exists

What is done to test: Verifies achievement exists in config and has correct requirement type

What is expected in test: Achievement should exist with type "master_of_division_tables" and required_tier "bronze"

#### test_master_of_division_tables_all_tiers

Test description: Verifies all tiers of Master of Division Tables are defined

Test setup: Checks achievement config for all tiers

What is done to test: Verifies each tier exists in config

What is expected in test: All 11 tiers should exist in config

### Changes
Intentionally left blank for after review.

---

## Master of Basic Addition

Achievement description: Level Master (X tier) on all basic addition concepts (tiered: bronze through champion)

### Expected Behavior

- 11 tiers, each requiring Level Master at that tier (or higher) on all basic addition concepts
- Should check metadata to identify basic addition concepts (e.g., c_add_0s through c_add_10s)
- Champion tier requires server record check
- Can be awarded multiple times per tier and per session

### Test Coverage
Summary: Tests verify config existence (checker implementation may not be complete).
Number of tests: 1

#### test_generic_achievement_master_of_basic_all_tiers_present

Test description: Verifies Master of Basic Addition achievements are defined for all tiers

Test setup: Checks achievement config for all tiers

What is done to test: Verifies each tier exists in config

What is expected in test: All 11 tiers should exist in config

### Changes
Intentionally left blank for after review.

---

## Master of Basic Subtraction

Achievement description: Level Master (X tier) on all basic subtraction concepts (tiered: bronze through champion)

### Expected Behavior

- 11 tiers, each requiring Level Master at that tier (or higher) on all basic subtraction concepts
- Should check metadata to identify basic subtraction concepts (e.g., c_sub_0s through c_sub_10s)
- Champion tier requires server record check
- Can be awarded multiple times per tier and per session

### Test Coverage
Summary: Tests verify config existence (checker implementation may not be complete).
Number of tests: 1

#### test_generic_achievement_master_of_basic_all_tiers_present

Test description: Verifies Master of Basic Subtraction achievements are defined for all tiers

Test setup: Checks achievement config for all tiers

What is done to test: Verifies each tier exists in config

What is expected in test: All 11 tiers should exist in config

### Changes
Intentionally left blank for after review.
