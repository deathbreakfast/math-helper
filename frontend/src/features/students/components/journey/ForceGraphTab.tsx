import { useMemo, useCallback } from 'react'
import { motion } from 'framer-motion'
import { AlertCircle } from 'lucide-react'
import type { UserProgressData } from '../../utils/progressMapping'
import type { Achievement } from '../../data/achievements'
import type { BackendAchievementDefinition } from '../../../lib/levels/api'
import { ForceGraphCanvas } from './ForceGraphCanvas'
import { transformAchievementsToForceGraph, type ForceGraphNode } from '../../utils/forceGraphData'

type ForceGraphTabProps = {
  achievements: Achievement[]
  userData: UserProgressData
  userId: string
  achievementDefinitions?: Record<string, BackendAchievementDefinition>
}

export const ForceGraphTab: React.FC<ForceGraphTabProps> = ({
  achievements,
  userData,
  userId,
  achievementDefinitions,
}) => {
  // Transform achievements into force graph data
  const graphData = useMemo(() => {
    return transformAchievementsToForceGraph(achievements)
  }, [achievements])

  // Handle node click - console.log with type and id
  const handleNodeClick = useCallback((node: ForceGraphNode) => {
    console.log('Node clicked:', {
      type: node.type,  // 'achievement' or 'math-concept'
      id: node.id        // Node ID
    })
  }, [])

  // Handle node hover (for future enhancements)
  const handleNodeHover = useCallback((node: ForceGraphNode | null) => {
    // Could add hover effects here in the future
  }, [])

  // Check if we have any Speed Demon achievements
  const hasSpeedDemonAchievements = graphData.nodes.length > 0

  return (
    <motion.div
      key="force-graph"
      data-testid="testid-force-graph-tab"
      initial={{
        opacity: 0,
        y: 20,
      }}
      animate={{
        opacity: 1,
        y: 0,
      }}
      exit={{
        opacity: 0,
        y: -20,
      }}
    >
      {/* Header */}
      <div className="mb-6">
        <h2 className="mb-2 text-2xl font-bold text-gray-900">Force Graph</h2>
        <p className="text-gray-600">
          Visualize achievement chains and their connections. Click on any achievement node to view details.
        </p>
      </div>

      {/* Graph Canvas */}
      {hasSpeedDemonAchievements ? (
        <ForceGraphCanvas
          nodes={graphData.nodes}
          edges={graphData.edges}
          onNodeClick={handleNodeClick}
          onNodeHover={handleNodeHover}
        />
      ) : (
        <div className="py-16 text-center">
          <AlertCircle className="mx-auto mb-4 h-16 w-16 text-gray-300" />
          <p className="text-lg text-gray-500">No Speed Demon achievements available</p>
          <p className="mt-2 text-sm text-gray-400">
            Complete practice sessions to earn Speed Demon achievements and see them in the graph.
          </p>
        </div>
      )}
    </motion.div>
  )
}
