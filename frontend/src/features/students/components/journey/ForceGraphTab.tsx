import { useMemo, useCallback, useState } from 'react'
import { motion } from 'framer-motion'
import { AlertCircle, Save } from 'lucide-react'
import type { UserProgressData } from '../../utils/progressMapping'
import type { Achievement } from '../../data/achievements'
import type { BackendAchievementDefinition } from '../../../lib/levels/api'
import { ForceGraphCanvas } from './ForceGraphCanvas'
import { transformAchievementsToForceGraph, type ForceGraphNode } from '../../utils/forceGraphData'
import { useMathConcepts } from '../../hooks/useMathConcepts'
import { useConceptRequirements } from '../../../../lib/concepts/hooks'
import { loadCachedPositions, downloadPositionsAsJson, exportPositionsFromNodes, type NodePositions } from '../../utils/forceGraphPositions'
import { isDevMode } from '../../../../utils/devMode'

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
  // Get math concepts for title formatting
  const { concepts: mathConcepts } = useMathConcepts({
    userData,
    isActive: true,
    userId,
  })
  
  // Get backend concept requirements for enriching achievements with concept-specific variants
  const conceptIds = useMemo(() => mathConcepts.map(c => c.conceptId), [mathConcepts])
  const { requirements: backendRequirements } = useConceptRequirements(conceptIds, true, userId)
  
  // Load cached positions
  const cachedPositions = useMemo(() => {
    try {
      const positions = loadCachedPositions()
      return Object.keys(positions).length > 0 ? positions : undefined
    } catch (error) {
      // File doesn't exist or is invalid, return undefined
      return undefined
    }
  }, [])
  
  // Transform achievements into force graph data
  const graphData = useMemo(() => {
    return transformAchievementsToForceGraph(achievements, mathConcepts, undefined, backendRequirements)
  }, [achievements, mathConcepts, backendRequirements])
  
  // Store function to get current positions from graph
  const [getCurrentPositions, setGetCurrentPositions] = useState<(() => NodePositions) | null>(null)
  
  // Handle position ready callback
  const handlePositionsReady = useCallback((positions: NodePositions) => {
    // Store positions when simulation completes
  }, [])
  
  // Handle get current positions callback
  const handleGetCurrentPositions = useCallback((getter: () => NodePositions) => {
    setGetCurrentPositions(() => getter)
  }, [])
  
  // Handle save button click
  const handleSavePositions = useCallback(() => {
    if (getCurrentPositions) {
      const positions = getCurrentPositions()
      if (Object.keys(positions).length > 0) {
        downloadPositionsAsJson(positions, 'forceGraphPositions.json')
      }
    } else {
      // Fallback: try to export from current graph data
      const positions = exportPositionsFromNodes(graphData.nodes)
      if (Object.keys(positions).length > 0) {
        downloadPositionsAsJson(positions, 'forceGraphPositions.json')
      }
    }
  }, [getCurrentPositions, graphData.nodes])

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
        <div className="flex items-center justify-between">
          <div>
            <h2 className="mb-2 text-2xl font-bold text-gray-900">Force Graph</h2>
            <p className="text-gray-600">
              Visualize achievement chains and their connections. Click on any achievement node to view details.
            </p>
          </div>
          {/* Save button (dev mode only) */}
          {isDevMode() && hasSpeedDemonAchievements && (
            <button
              onClick={handleSavePositions}
              className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              title="Save current node positions to JSON file"
            >
              <Save className="h-4 w-4" />
              Save Positions
            </button>
          )}
        </div>
      </div>

      {/* Graph Canvas */}
      {hasSpeedDemonAchievements ? (
        <ForceGraphCanvas
          nodes={graphData.nodes}
          edges={graphData.edges}
          onNodeClick={handleNodeClick}
          onNodeHover={handleNodeHover}
          initialPositions={cachedPositions}
          onPositionsReady={handlePositionsReady}
          onGetCurrentPositions={handleGetCurrentPositions}
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
