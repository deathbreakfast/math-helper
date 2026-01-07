/**
 * Utility to compare mock data structure with live data structure
 * This helps ensure the journey tab behaves the same way as the mock data test
 */

import type { Achievement } from '../data/achievements'
import type { MathConcept } from '../data/mathConcepts'
import { mockSpeedDemonAchievements } from '../data/mockAchievements'
import { mockMathConcepts } from '../data/mockMathConcepts'
import { transformAchievementsToForceGraph, type ForceGraphNode, type ForceGraphEdge } from './forceGraphData'
import type { User } from '../../hooks/useLearners'
import type { AchievementDefinitionsCache } from '../../../../lib/levels/hooks'
import { mapUserToProgressData } from './progressMapping'

/**
 * Compare the structure of mock data vs live data to ensure they're compatible
 */
export function compareDataStructures(
  liveAchievements: Achievement[],
  liveConcepts: MathConcept[]
): {
  achievementsMatch: boolean
  conceptsMatch: boolean
  differences: {
    achievements?: string[]
    concepts?: string[]
  }
} {
  const differences: { achievements?: string[]; concepts?: string[] } = {}
  const achievementDiffs: string[] = []
  const conceptDiffs: string[] = []

  // Check if mock achievements structure matches live achievements structure
  if (mockSpeedDemonAchievements.length > 0 && liveAchievements.length > 0) {
    const mockSample = mockSpeedDemonAchievements[0]
    const liveSample = liveAchievements[0]
    
    const mockKeys = Object.keys(mockSample).sort()
    const liveKeys = Object.keys(liveSample).sort()
    
    if (JSON.stringify(mockKeys) !== JSON.stringify(liveKeys)) {
      achievementDiffs.push(`Key mismatch: mock has [${mockKeys.join(', ')}], live has [${liveKeys.join(', ')}]`)
    }
    
    // Check specific important fields
    const importantFields = ['id', 'title', 'status', 'icon', 'tier', 'metadata']
    for (const field of importantFields) {
      if (field in mockSample && !(field in liveSample)) {
        achievementDiffs.push(`Live data missing field: ${field}`)
      }
      if (!(field in mockSample) && field in liveSample) {
        achievementDiffs.push(`Mock data missing field: ${field}`)
      }
    }
  }

  // Check if mock concepts structure matches live concepts structure
  if (mockMathConcepts.length > 0 && liveConcepts.length > 0) {
    const mockSample = mockMathConcepts[0]
    const liveSample = liveConcepts[0]
    
    const mockKeys = Object.keys(mockSample).sort()
    const liveKeys = Object.keys(liveSample).sort()
    
    if (JSON.stringify(mockKeys) !== JSON.stringify(liveKeys)) {
      conceptDiffs.push(`Key mismatch: mock has [${mockKeys.join(', ')}], live has [${liveKeys.join(', ')}]`)
    }
    
    // Check specific important fields
    const importantFields = ['conceptId', 'displayName', 'isLocked', 'operation']
    for (const field of importantFields) {
      if (field in mockSample && !(field in liveSample)) {
        conceptDiffs.push(`Live data missing field: ${field}`)
      }
      if (!(field in mockSample) && field in liveSample) {
        conceptDiffs.push(`Mock data missing field: ${field}`)
      }
    }
  }

  if (achievementDiffs.length > 0) {
    differences.achievements = achievementDiffs
  }
  if (conceptDiffs.length > 0) {
    differences.concepts = conceptDiffs
  }

  return {
    achievementsMatch: achievementDiffs.length === 0,
    conceptsMatch: conceptDiffs.length === 0,
    differences,
  }
}

/**
 * Log a snapshot of mock data structure for comparison
 */
export function logMockDataSnapshot() {
  console.group('📊 Mock Data Snapshot for Force Graph')
  
  const withMetadata = mockSpeedDemonAchievements.filter(a => a.metadata?.concept_id)
  const withoutMetadata = mockSpeedDemonAchievements.filter(a => !a.metadata?.concept_id)
  
  console.log('Mock Achievements:', {
    count: mockSpeedDemonAchievements.length,
    statusValues: [...new Set(mockSpeedDemonAchievements.map(a => a.status))],
    withMetadata: withMetadata.length,
    withoutMetadata: withoutMetadata.length,
  })
  
  console.log('Sample Achievements WITH metadata (concept_id):', 
    withMetadata.slice(0, 15).map(a => ({
      id: a.id,
      title: a.title,
      concept_id: a.metadata?.concept_id,
      status: a.status,
    }))
  )
  
  console.log('Sample Achievements WITHOUT metadata:', 
    withoutMetadata.slice(0, 15).map(a => ({
      id: a.id,
      title: a.title,
      status: a.status,
    }))
  )
  
  console.log('Mock Math Concepts:', {
    count: mockMathConcepts.length,
    sample: mockMathConcepts[0],
    unlockedCount: mockMathConcepts.filter(c => !c.isLocked).length,
    lockedCount: mockMathConcepts.filter(c => c.isLocked).length,
    unlockedConcepts: mockMathConcepts.filter(c => !c.isLocked).map(c => c.conceptId),
  })
  
  console.groupEnd()
}

/**
 * Log a snapshot of live data structure for comparison
 */
export function logLiveDataSnapshot(
  liveAchievements: Achievement[],
  liveConcepts: MathConcept[]
) {
  console.group('📊 Live Data Snapshot for Force Graph')
  
  const withMetadata = liveAchievements.filter(a => a.metadata?.concept_id)
  const withoutMetadata = liveAchievements.filter(a => !a.metadata?.concept_id)
  
  console.log('Live Achievements:', {
    count: liveAchievements.length,
    statusValues: [...new Set(liveAchievements.map(a => a.status))],
    withMetadata: withMetadata.length,
    withoutMetadata: withoutMetadata.length,
  })
  
  // Debug: Show raw achievement objects to see if metadata exists
  console.log('🔍 DEBUG: Raw achievement samples (first 5):', 
    liveAchievements.slice(0, 5).map(a => ({
      id: a.id,
      code: a.id, // Same as id in frontend
      title: a.title,
      metadata: a.metadata, // Show raw metadata
      hasMetadata: !!a.metadata,
      metadataKeys: a.metadata ? Object.keys(a.metadata) : [],
    }))
  )
  
  console.log('Sample Achievements WITH metadata (concept_id):', 
    withMetadata.slice(0, 15).map(a => ({
      id: a.id,
      title: a.title,
      concept_id: a.metadata?.concept_id,
      status: a.status,
    }))
  )
  
  console.log('Sample Achievements WITHOUT metadata:', 
    withoutMetadata.slice(0, 15).map(a => ({
      id: a.id,
      title: a.title,
      status: a.status,
      metadataField: a.metadata, // Show if metadata exists but no concept_id
    }))
  )
  
  console.log('Live Math Concepts:', {
    count: liveConcepts.length,
    sample: liveConcepts[0],
    unlockedCount: liveConcepts.filter(c => !c.isLocked).length,
    lockedCount: liveConcepts.filter(c => c.isLocked).length,
    unlockedConcepts: liveConcepts.filter(c => !c.isLocked).map(c => c.conceptId),
  })
  
  console.groupEnd()
}

/**
 * Compare the force graph output between mock and live data
 * This is the key comparison to ensure edges connect the same way
 */
export function compareForceGraphOutput(
  liveAchievements: Achievement[],
  liveConcepts: MathConcept[]
): {
  nodeCountMatch: boolean
  edgeCountMatch: boolean
  missingLiveEdges: string[]
  extraLiveEdges: string[]
  nodeIdComparison: {
    mockOnlyNodeIds: string[]
    liveOnlyNodeIds: string[]
    sharedNodeIds: string[]
  }
} {
  // Transform both mock and live data
  const mockGraph = transformAchievementsToForceGraph(mockSpeedDemonAchievements, mockMathConcepts)
  const liveGraph = transformAchievementsToForceGraph(liveAchievements, liveConcepts)
  
  // Compare node IDs
  const mockNodeIds = new Set(mockGraph.nodes.map(n => n.id))
  const liveNodeIds = new Set(liveGraph.nodes.map(n => n.id))
  
  const mockOnlyNodeIds = [...mockNodeIds].filter(id => !liveNodeIds.has(id))
  const liveOnlyNodeIds = [...liveNodeIds].filter(id => !mockNodeIds.has(id))
  const sharedNodeIds = [...mockNodeIds].filter(id => liveNodeIds.has(id))
  
  // Compare edge IDs (source-target pairs)
  const getEdgeKey = (edge: ForceGraphEdge) => {
    const sourceId = typeof edge.source === 'string' ? edge.source : edge.source.id
    const targetId = typeof edge.target === 'string' ? edge.target : edge.target.id
    return `${sourceId} → ${targetId}`
  }
  
  const mockEdgeKeys = new Set(mockGraph.edges.map(getEdgeKey))
  const liveEdgeKeys = new Set(liveGraph.edges.map(getEdgeKey))
  
  const missingLiveEdges = [...mockEdgeKeys].filter(key => !liveEdgeKeys.has(key))
  const extraLiveEdges = [...liveEdgeKeys].filter(key => !mockEdgeKeys.has(key))
  
  // Analyze which achievements link to concepts vs which don't
  const getAchievementToConceptEdges = (graph: { edges: ForceGraphEdge[] }) => {
    return graph.edges.filter(e => {
      const sourceId = typeof e.source === 'string' ? e.source : e.source.id
      const targetId = typeof e.target === 'string' ? e.target : e.target.id
      // Achievement to concept edges have source as achievement and target as concept (starts with 'c_')
      return e.chainId === 'unlock-requirement' && targetId.startsWith('c_')
    })
  }
  
  const mockAchievementEdges = getAchievementToConceptEdges(mockGraph)
  const liveAchievementEdges = getAchievementToConceptEdges(liveGraph)
  
  const getLinkedAchievementIds = (edges: ForceGraphEdge[]) => {
    return new Set(edges.map(e => {
      const sourceId = typeof e.source === 'string' ? e.source : e.source.id
      return sourceId
    }))
  }
  
  const mockLinkedIds = getLinkedAchievementIds(mockAchievementEdges)
  const liveLinkedIds = getLinkedAchievementIds(liveAchievementEdges)
  
  // Get achievement nodes (not concepts or root categories)
  const mockAchievementNodes = mockGraph.nodes.filter(n => n.type === 'achievement')
  const liveAchievementNodes = liveGraph.nodes.filter(n => n.type === 'achievement')
  
  const mockLinkedAchievements = mockAchievementNodes.filter(n => mockLinkedIds.has(n.id))
  const mockUnlinkedAchievements = mockAchievementNodes.filter(n => !mockLinkedIds.has(n.id))
  const liveLinkedAchievements = liveAchievementNodes.filter(n => liveLinkedIds.has(n.id))
  const liveUnlinkedAchievements = liveAchievementNodes.filter(n => !liveLinkedIds.has(n.id))
  
  console.group('🔗 Force Graph Data Comparison')
  
  console.log('Nodes:', {
    mockCount: mockGraph.nodes.length,
    liveCount: liveGraph.nodes.length,
    mockOnlyCount: mockOnlyNodeIds.length,
    liveOnlyCount: liveOnlyNodeIds.length,
    sharedCount: sharedNodeIds.length,
  })
  
  // Show achievement linking analysis
  console.log('📊 Achievement Linking Analysis:')
  console.log('Mock:', {
    totalAchievements: mockAchievementNodes.length,
    linkedToConcepts: mockLinkedAchievements.length,
    unlinked: mockUnlinkedAchievements.length,
    sampleLinked: mockLinkedAchievements.slice(0, 10).map(n => n.id),
    sampleUnlinked: mockUnlinkedAchievements.slice(0, 10).map(n => n.id),
  })
  
  console.log('Live:', {
    totalAchievements: liveAchievementNodes.length,
    linkedToConcepts: liveLinkedAchievements.length,
    unlinked: liveUnlinkedAchievements.length,
    sampleLinked: liveLinkedAchievements.slice(0, 10).map(n => n.id),
    sampleUnlinked: liveUnlinkedAchievements.slice(0, 10).map(n => n.id),
  })
  
  if (mockOnlyNodeIds.length > 0) {
    console.log('⚠️ Nodes in MOCK but not in LIVE (first 20):', mockOnlyNodeIds.slice(0, 20))
  }
  if (liveOnlyNodeIds.length > 0) {
    console.log('ℹ️ Nodes in LIVE but not in MOCK (first 20):', liveOnlyNodeIds.slice(0, 20))
  }
  
  console.log('Edges:', {
    mockCount: mockGraph.edges.length,
    liveCount: liveGraph.edges.length,
    mockAchievementToConcept: mockAchievementEdges.length,
    liveAchievementToConcept: liveAchievementEdges.length,
    missingInLive: missingLiveEdges.length,
    extraInLive: extraLiveEdges.length,
  })
  
  if (missingLiveEdges.length > 0) {
    console.log('⚠️ Edges in MOCK but not in LIVE (first 20):', missingLiveEdges.slice(0, 20))
  }
  if (extraLiveEdges.length > 0) {
    console.log('ℹ️ Edges in LIVE but not in MOCK (first 20):', extraLiveEdges.slice(0, 20))
  }
  
  // Show sample achievement-to-concept edges
  console.log('Sample Achievement-to-Concept Edges:')
  console.log('Mock (first 10):', mockAchievementEdges.slice(0, 10).map(e => {
    const sourceId = typeof e.source === 'string' ? e.source : e.source.id
    const targetId = typeof e.target === 'string' ? e.target : e.target.id
    return `${sourceId} → ${targetId}`
  }))
  console.log('Live (first 10):', liveAchievementEdges.slice(0, 10).map(e => {
    const sourceId = typeof e.source === 'string' ? e.source : e.source.id
    const targetId = typeof e.target === 'string' ? e.target : e.target.id
    return `${sourceId} → ${targetId}`
  }))
  
  console.groupEnd()
  
  return {
    nodeCountMatch: mockGraph.nodes.length === liveGraph.nodes.length,
    edgeCountMatch: mockGraph.edges.length === liveGraph.edges.length,
    missingLiveEdges,
    extraLiveEdges,
    nodeIdComparison: {
      mockOnlyNodeIds,
      liveOnlyNodeIds,
      sharedNodeIds,
    },
  }
}

/**
 * Comprehensive data flow tracing function
 * Traces achievement data through all transformation steps and compares with mock data
 */
export function traceAchievementDataFlow(
  user: User,
  achievementDefinitions?: AchievementDefinitionsCache
): void {
  if (!import.meta.env.DEV) {
    return // Only run in development
  }

  console.group('🔬 Achievement Data Flow Trace')
  
  // Step 1: Raw user achievements (from API mapping)
  const rawAchievements = user.achievements || []
  const rawWithMetadata = rawAchievements.filter(a => a.metadata?.concept_id)
  const rawWithoutMetadata = rawAchievements.filter(a => !a.metadata?.concept_id)
  
  console.log('📥 Step 1: Raw User Achievements (from API):', {
    total: rawAchievements.length,
    withMetadata: rawWithMetadata.length,
    withoutMetadata: rawWithoutMetadata.length,
    sampleWithMetadata: rawWithMetadata.slice(0, 3).map(a => ({
      id: a.id,
      code: a.code,
      concept_id: a.metadata?.concept_id,
    })),
  })
  
  // Step 2: After mapUserToProgressData conversion
  const userProgressData = mapUserToProgressData(user, undefined, achievementDefinitions)
  const convertedAchievements = userProgressData.achievements || []
  const convertedWithMetadata = convertedAchievements.filter(a => a.metadata?.concept_id)
  const convertedWithoutMetadata = convertedAchievements.filter(a => !a.metadata?.concept_id)
  
  console.log('🔄 Step 2: After mapUserToProgressData Conversion:', {
    total: convertedAchievements.length,
    withMetadata: convertedWithMetadata.length,
    withoutMetadata: convertedWithoutMetadata.length,
    sampleWithMetadata: convertedWithMetadata.slice(0, 3).map(a => ({
      id: a.id,
      concept_id: a.metadata?.concept_id,
    })),
  })
  
  // Step 3: Compare with mock data
  const mockWithMetadata = mockSpeedDemonAchievements.filter(a => a.metadata?.concept_id)
  const mockWithoutMetadata = mockSpeedDemonAchievements.filter(a => !a.metadata?.concept_id)
  
  console.log('📊 Step 3: Comparison with Mock Data:')
  console.log('Raw API vs Mock:', {
    rawTotal: rawAchievements.length,
    mockTotal: mockSpeedDemonAchievements.length,
    rawWithMetadata: rawWithMetadata.length,
    mockWithMetadata: mockWithMetadata.length,
    metadataLoss: rawWithMetadata.length - convertedWithMetadata.length,
  })
  
  // Step 4: Identify duplicate codes that might be collapsed
  const codeGroups = new Map<string, typeof rawAchievements>()
  rawAchievements.forEach(a => {
    if (a.code) {
      if (!codeGroups.has(a.code)) {
        codeGroups.set(a.code, [])
      }
      codeGroups.get(a.code)!.push(a)
    }
  })
  const duplicateCodes = Array.from(codeGroups.entries())
    .filter(([_, achievements]) => achievements.length > 1)
    .filter(([code, achievements]) => {
      // Only show if they have different metadata
      const metadataVariants = new Set(achievements.map(a => 
        JSON.stringify(a.metadata || {})
      ))
      return metadataVariants.size > 1
    })
  
  if (duplicateCodes.length > 0) {
    console.log('⚠️ Step 4: Duplicate Codes with Different Metadata (Data Loss Risk):', {
      count: duplicateCodes.length,
      examples: duplicateCodes.slice(0, 5).map(([code, achievements]) => ({
        code,
        count: achievements.length,
        metadataVariants: achievements.map(a => ({
          concept_id: a.metadata?.concept_id || 'no metadata',
          fullMetadata: a.metadata,
        })),
      })),
    })
    
    // Check if these duplicates are being collapsed
    const collapsedCodes = duplicateCodes.filter(([code]) => {
      const converted = convertedAchievements.find(a => a.id === code)
      return converted && !converted.metadata?.concept_id
    })
    
    if (collapsedCodes.length > 0) {
      console.error('❌ DATA LOSS DETECTED: These codes have metadata in raw data but lost it after conversion:', 
        collapsedCodes.slice(0, 10).map(([code]) => code)
      )
    }
  } else {
    console.log('✅ Step 4: No duplicate codes with different metadata found')
  }
  
  // Step 5: Check normalization
  const normalizedWithMetadata = convertedWithMetadata.filter(a => {
    // Check if ID would be normalized (has concept_id in metadata)
    return a.metadata?.concept_id && !a.id.includes(`-${a.metadata.concept_id}`)
  })
  
  console.log('🔧 Step 5: Normalization Check:', {
    achievementsNeedingNormalization: normalizedWithMetadata.length,
    sample: normalizedWithMetadata.slice(0, 3).map(a => ({
      currentId: a.id,
      expectedId: a.metadata?.concept_id ? `${a.id}-${a.metadata.concept_id}` : a.id,
      concept_id: a.metadata?.concept_id,
    })),
  })
  
  console.groupEnd()
}
