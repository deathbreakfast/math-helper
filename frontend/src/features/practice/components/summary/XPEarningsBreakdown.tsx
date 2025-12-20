import { motion } from 'framer-motion'
import { Sparkles } from 'lucide-react'
import type { LevelUpResult } from '../../types'
import { useAchievementDefinitions } from '../../../../lib/levels/hooks'
import { getConceptDisplayNameByConceptId } from '../../../students/data/mathConcepts'

type XPEarningsBreakdownProps = {
  levelUp: LevelUpResult | null
}

export const XPEarningsBreakdown = ({ levelUp }: XPEarningsBreakdownProps) => {
  const breakdown = levelUp?.xp_breakdown
  if (!breakdown || levelUp?.earned_xp === undefined) return null

  const { definitions: achievementDefinitions } = useAchievementDefinitions()
  const conceptName = getConceptDisplayNameByConceptId(breakdown.concept_id) || breakdown.concept_id || '—'

  const multipliers = breakdown.multipliers || []
  const bonusSources = breakdown.bonus_xp_sources || []

  const getAchievementLabel = (code: string | null | undefined) => {
    if (!code) return 'Achievement'
    return achievementDefinitions[code]?.title || code
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.85 }}
      className="bg-white rounded-2xl p-6 shadow-lg"
    >
      <h3 className="text-xl font-semibold text-gray-800 mb-4 flex items-center gap-2">
        <Sparkles className="w-5 h-5 text-purple-600" />
        XP Earned
      </h3>

      <div className="space-y-4 text-sm text-gray-700">
        <div className="flex items-center justify-between rounded-xl bg-slate-50 p-3">
          <div>
            <div className="font-semibold">Base XP</div>
            <div className="text-xs text-gray-500">
              {breakdown.xp_per_correct ?? 0} × {breakdown.correct_count ?? 0} ({conceptName})
            </div>
          </div>
          <div className="font-bold">{(breakdown.base_xp ?? 0).toLocaleString()}xp</div>
        </div>

        <div className="flex items-center justify-between rounded-xl bg-slate-50 p-3">
          <div>
            <div className="font-semibold">Multiplier</div>
            <div className="text-xs text-gray-500">
              {multipliers.length > 0 ? `${multipliers.length} achievement(s)` : 'None'}
            </div>
          </div>
          <div className="font-bold">x{(breakdown.total_multiplier ?? 1).toFixed(2)}</div>
        </div>

        {multipliers.length > 0 && (
          <div className="rounded-xl border border-slate-100 p-3">
            <div className="text-xs font-semibold text-slate-500 mb-2">Multipliers</div>
            <div className="space-y-1">
              {multipliers.map((m, idx) => (
                <div key={`${m.achievement_code || 'ach'}-${idx}`} className="flex justify-between gap-3">
                  <div className="truncate text-gray-600">{getAchievementLabel(m.achievement_code)}</div>
                  <div className="font-semibold text-gray-800">x{(m.multiplier ?? 0).toFixed(2)}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex items-center justify-between rounded-xl bg-slate-50 p-3">
          <div>
            <div className="font-semibold">Bonus XP</div>
            <div className="text-xs text-gray-500">
              {bonusSources.length > 0 ? `${bonusSources.length} achievement(s)` : 'None'}
            </div>
          </div>
          <div className="font-bold">{(breakdown.bonus_xp ?? 0).toLocaleString()}xp</div>
        </div>

        {bonusSources.length > 0 && (
          <div className="rounded-xl border border-slate-100 p-3">
            <div className="text-xs font-semibold text-slate-500 mb-2">Bonus XP</div>
            <div className="space-y-1">
              {bonusSources.map((b, idx) => (
                <div key={`${b.achievement_code || 'ach'}-${idx}`} className="flex justify-between gap-3">
                  <div className="truncate text-gray-600">{getAchievementLabel(b.achievement_code)}</div>
                  <div className="font-semibold text-gray-800">{(b.bonus_xp ?? 0).toLocaleString()}xp</div>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex items-center justify-between rounded-xl bg-purple-50 p-3">
          <div className="font-semibold text-purple-800">Total</div>
          <div className="text-lg font-bold text-purple-900">{(levelUp.earned_xp ?? 0).toLocaleString()}xp</div>
        </div>
      </div>
    </motion.div>
  )
}

