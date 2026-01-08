import { useMemo, useCallback, useState } from 'react'
import { motion } from 'framer-motion'
import { AlertCircle, Save } from 'lucide-react'
import type { UserProgressData } from '../../utils/progressMapping'
import type { Achievement } from '../../data/achievements'
import type { BackendAchievementDefinition } from '../../../lib/levels/api'
import type { MathConcept } from '../../data/mathConcepts'
import { ForceGraphCanvas } from './ForceGraphCanvas'
import { transformAchievementsToForceGraph, type ForceGraphNode } from '../../utils/forceGraphData'
import { useMathConcepts } from '../../hooks/useMathConcepts'
import { useConceptRequirements } from '../../../../lib/concepts/hooks'
import { loadCachedPositions, downloadPositionsAsJson, exportPositionsFromNodes, type NodePositions } from '../../utils/forceGraphPositions'
import { isDevMode } from '../../../../utils/devMode'
import { useRouter } from '../../../../utils/routing'
import { MathConceptDetailModal } from './MathConceptDetailModal'
import { AchievementDetailModal } from './AchievementDetailModal'
import type { User } from '../../hooks/useLearners'

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
  
  const router = useRouter()
  
  // Modal state
  const [selectedConcept, setSelectedConcept] = useState<MathConcept | null>(null)
  const [isConceptModalOpen, setIsConceptModalOpen] = useState(false)
  const [selectedAchievement, setSelectedAchievement] = useState<Achievement | null>(null)
  const [isAchievementModalOpen, setIsAchievementModalOpen] = useState(false)
  const [achievementConceptId, setAchievementConceptId] = useState<string | undefined>(undefined)
  
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

  // Handle node click - open appropriate modal
  const handleNodeClick = useCallback((node: ForceGraphNode) => {
    if (node.type === 'math-concept') {
      // Find the concept by conceptId
      const concept = mathConcepts.find(c => c.conceptId === node.conceptId || c.conceptId === node.id)
      if (concept) {
        setSelectedConcept(concept)
        setIsConceptModalOpen(true)
      }
    } else if (node.type === 'achievement') {
      // Find the achievement by ID
      // Try node.achievementId first (base achievement ID), then node.id
      let achievement = achievements.find(a => a.id === node.achievementId)
      if (!achievement) {
        // Fallback: try to find by node.id (might be enriched ID)
        achievement = achievements.find(a => {
          // Check if node.id starts with achievement.id (e.g., "math-master-bronze-c_add_1s" starts with "math-master-bronze")
          return node.id.startsWith(a.id + '-') || node.id === a.id
        })
      }
      
      if (achievement) {
        setSelectedAchievement(achievement)
        
        // Extract concept_id from achievement metadata first (most reliable)
        let conceptId: string | undefined = achievement.metadata?.concept_id
        
        // If not in metadata, try to extract from node ID for concept-specific achievements
        // Enriched achievement IDs have format: baseCode-tier-sourceConceptId-required-by-requiringConceptId
        // Example: "math-master-bronze-c_add_2s-required-by-c_add_2s"
        // We want to extract the sourceConceptId (the concept the achievement is FOR)
        if (!conceptId && node.id.includes('-required-by-')) {
          // Pattern: ...-tier-sourceConceptId-required-by-...
          // Find the part between tier and "-required-by-"
          const requiredByIndex = node.id.indexOf('-required-by-')
          if (requiredByIndex > 0) {
            const beforeRequiredBy = node.id.substring(0, requiredByIndex)
            // Look for concept ID pattern (starts with 'c_')
            // It should be at the end of the string before "-required-by-"
            const conceptPattern = /-(c_[a-z0-9_]+)$/
            const match = beforeRequiredBy.match(conceptPattern)
            if (match) {
              // Found concept ID at the end - this is the source concept (what the achievement is FOR)
              conceptId = match[1]
            }
          }
        }
        
        setAchievementConceptId(conceptId)
        setIsAchievementModalOpen(true)
      }
    }
  }, [mathConcepts, achievements])
  
  // Handle start practice for concept modal
  const handleStartPractice = useCallback((concept: MathConcept) => {
    if (!userData) return
    
    router.navigate('/practice', {
      user: userData.name,
      userId: userData.id,
      avatar: userData.avatar,
      conceptId: concept.conceptId,
      isConcept: 'true',
    })
  }, [userData, router])
  
  // Convert userData to User type for modals
  const selectedUser: User | null = useMemo(() => {
    if (!userData) return null
    return {
      id: userData.id,
      name: userData.name,
      avatar: userData.avatar,
      level: userData.level,
      questionsAnswered: userData.totalQuestions,
      averageSpeed: 0,
      achievements: userData.achievements
        .filter(ach => ach.unlockedAt)
        .map(ach => ({
          id: ach.id,
          code: ach.id,
          title: ach.title,
          description: ach.description,
          icon: ach.icon,
          earnedAt: ach.unlockedAt!,
          category: ach.category,
        })),
      stats: {
        additionAccuracy: 0,
        subtractionAccuracy: 0,
        multiplicationAccuracy: 0,
        divisionAccuracy: 0,
        additionSpeed: 0,
        subtractionSpeed: 0,
        multiplicationSpeed: 0,
        divisionSpeed: 0,
        currentStreak: userData.currentStreak,
        bestStreak: userData.bestStreak,
      },
    }
  }, [userData])

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
      
      {/* Math Concept Detail Modal */}
      <MathConceptDetailModal
        concept={selectedConcept}
        isOpen={isConceptModalOpen}
        onClose={() => {
          setIsConceptModalOpen(false)
          setSelectedConcept(null)
        }}
        onStartPractice={handleStartPractice}
        selectedUser={selectedUser}
      />
      
      {/* Achievement Detail Modal */}
      <AchievementDetailModal
        achievement={selectedAchievement}
        achievementDefinition={selectedAchievement && achievementDefinitions
          ? achievementDefinitions[selectedAchievement.id]
          : null}
        userId={userId}
        isOpen={isAchievementModalOpen}
        onClose={() => {
          setIsAchievementModalOpen(false)
          setSelectedAchievement(null)
          setAchievementConceptId(undefined)
        }}
        conceptId={achievementConceptId}
        userData={userData}
      />
    </motion.div>
  )
}
