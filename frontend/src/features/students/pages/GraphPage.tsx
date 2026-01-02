import { useMemo, useCallback } from 'react'
import { ForceGraphCanvas } from '../components/journey/ForceGraphCanvas'
import { transformAchievementsToForceGraph, type ForceGraphNode } from '../utils/forceGraphData'
import { mockSpeedDemonAchievements } from '../data/mockAchievements'
import { mockMathConcepts } from '../data/mockMathConcepts'

export const GraphPage = () => {
  // Transform mock achievements into force graph data
  // Example edge metadata - in real usage, this would come from requirement data
  const edgeMetadata = {
    'speed-demon-bronze-speed-demon-silver': { quantity: 4 },
    'speed-demon-silver-speed-demon-gold': { quantity: 2 },
    'math-master-bronze-math-master-silver': { quantity: 1 },
    'math-master-silver-math-master-gold': { quantity: 1 },
    'math-master-gold-math-master-platinum': { quantity: 1 },
    'math-master-platinum-math-master-diamond': { quantity: 1 },
    'math-master-diamond-math-master-master': { quantity: 1 },
    'math-master-master-math-master-grandmaster': { quantity: 1 },
    'math-master-grandmaster-math-master-legendary': { quantity: 1 },
    'math-master-legendary-math-master-mythic': { quantity: 1 },
    'math-master-mythic-math-master-divine': { quantity: 1 },
    'math-master-divine-math-master-champion': { quantity: 1 },
  }
  
  const graphData = useMemo(() => {
    return transformAchievementsToForceGraph(mockSpeedDemonAchievements, mockMathConcepts, edgeMetadata)
  }, [])

  // Handle node click - console.log with type and id
  const handleNodeClick = useCallback((node: ForceGraphNode) => {
    console.log('Node clicked:', {
      type: node.type,
      id: node.id,
    })
  }, [])

  // Handle node hover
  const handleNodeHover = useCallback((node: ForceGraphNode | null) => {
    // Could add hover effects here in the future
  }, [])

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-purple-50 to-pink-50 p-8">
      <div className="mx-auto max-w-7xl">
        <h1 className="mb-6 text-3xl font-bold text-gray-900">Force Graph Test</h1>
        <ForceGraphCanvas
          nodes={graphData.nodes}
          edges={graphData.edges}
          onNodeClick={handleNodeClick}
          onNodeHover={handleNodeHover}
        />
      </div>
    </div>
  )
}
