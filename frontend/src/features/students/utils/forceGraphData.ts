/**
 * Utilities for transforming achievements and math concepts into force graph data structures
 */

import type { Achievement } from '../data/achievements'
import type { MathConcept } from '../data/mathConcepts'
import { extractTierFromCode, TIER_ORDER } from './achievementUtils'

export type ForceGraphNode = {
  id: string                    // Node ID (achievement ID or concept ID)
  achievementId?: string         // Achievement ID (if type is 'achievement')
  conceptId?: string            // Concept ID (if type is 'math-concept')
  title: string                 // Node title
  icon: string                  // Node icon emoji/character
  tier: string                  // bronze, silver, gold (capitalized) or 'Concept' for math concepts
  status: 'locked' | 'unlocked' | 'in-progress'
  chainId: string               // Grouping ID (e.g., "speed-demon" or conceptId for concepts)
  isRoot: boolean               // true for bronze tier (root nodes) or math concepts
  size: number                  // Node size (smaller for achievements, larger for concepts)
  type: 'achievement' | 'math-concept' | 'root-category'  // Node type identifier
  x?: number                    // Force graph x position
  y?: number                    // Force graph y position
  vx?: number                   // Velocity x
  vy?: number                   // Velocity y
}

export type ForceGraphEdge = {
  id: string                    // Unique edge ID
  source: string | ForceGraphNode  // Source node ID
  target: string | ForceGraphNode  // Target node ID
  label: string                 // Text to display on edge (e.g., "qty 4")
  chainId: string               // Which achievement chain this belongs to
  labelColor?: string           // Optional color for edge label text (e.g., 'green')
  metadata?: Record<string, any> // Metadata for the edge (e.g., { quantity: 4 })
}

/**
 * Filter achievements for force graph display
 * Includes: speed-demon, first-steps, first-victory, level-master (bronze, silver, gold only)
 */
function filterSpeedDemonAchievements(achievements: Achievement[]): Achievement[] {
  // Track which math-master tiers we've already included (to avoid duplicates with metadata)
  const includedMathMasterTiers = new Set<string>()
  
  return achievements.filter(achievement => {
    const { baseCode, tier } = extractTierFromCode(achievement.id)
    
    // Include speed-demon with bronze, silver, or gold tiers
    if (baseCode === 'speed-demon' && tier !== null && ['Bronze', 'Silver', 'Gold'].includes(tier)) {
      return true
    }
    
    // Include first-steps (no tier)
    if (achievement.id === 'first-steps') {
      return true
    }
    
    // Include first-victory (no tier)
    if (achievement.id === 'first-victory') {
      return true
    }
    
    // Include math-master with all tiers, but only one per tier (prefer generic over metadata-specific)
    if (baseCode === 'math-master' && tier !== null) {
      // If we haven't seen this tier yet, include it
      if (!includedMathMasterTiers.has(tier)) {
        includedMathMasterTiers.add(tier)
        return true
      }
      // If we've already included this tier, only include if this is the generic one (not metadata-specific)
      return !achievement.metadata?.concept_id
    }
    
    return false
  })
}

/**
 * Get tier hierarchy value for sorting
 */
function getTierValue(tier: string): number {
  const index = TIER_ORDER.indexOf(tier)
  return index >= 0 ? index + 1 : 999
}

/**
 * Transform achievements into force graph nodes
 */
export function createForceGraphNodes(achievements: Achievement[]): ForceGraphNode[] {
  const filtered = filterSpeedDemonAchievements(achievements)
  
  return filtered.map(achievement => {
    const { baseCode, tier } = extractTierFromCode(achievement.id)
    const tierValue = tier ? getTierValue(tier) : 999
    
    // For non-tiered achievements (first-steps, first-victory), use the achievement ID as chainId
    // For tiered achievements, use the baseCode
    const chainId = tier ? baseCode : achievement.id
    
    return {
      id: achievement.id,
      achievementId: achievement.id,
      title: achievement.title,
      icon: achievement.icon,
      tier: tier || achievement.tier || 'Unknown', // Use tier from extraction or fallback to achievement.tier
      status: achievement.status,
      chainId,
      isRoot: tier === 'Bronze' || !tier, // Root nodes are bronze tier or non-tiered achievements
      size: 9, // Achievement nodes are small (about 1/4 of original 35px)
      type: 'achievement' as const,
      // x, y, vx, vy will be set by force graph simulation
    }
  })
}

/**
 * Transform math concepts into force graph nodes
 */
export function createForceGraphNodesFromConcepts(concepts: MathConcept[]): ForceGraphNode[] {
  return concepts.map(concept => ({
    id: concept.conceptId,
    conceptId: concept.conceptId,
    title: concept.displayName,
    icon: '📚', // Default icon for math concepts
    tier: 'Concept',
    status: concept.isLocked ? 'locked' : 'unlocked',
    chainId: concept.conceptId, // Each concept is its own chain
    isRoot: true, // Math concepts are root nodes
    size: 18, // Math concepts are larger (2x achievement size)
    type: 'math-concept' as const,
    // x, y, vx, vy will be set by force graph simulation
  }))
}

/**
 * Create edges between consecutive tiers in achievement chains
 * @param nodes - Array of force graph nodes
 * @param edgeMetadata - Optional metadata for edges keyed by edge ID
 */
export function createForceGraphEdges(
  nodes: ForceGraphNode[],
  edgeMetadata?: Record<string, { quantity?: number; [key: string]: any }>
): ForceGraphEdge[] {
  const edges: ForceGraphEdge[] = []
  
  // Group nodes by chainId
  const nodesByChain = new Map<string, ForceGraphNode[]>()
  nodes.forEach(node => {
    if (!nodesByChain.has(node.chainId)) {
      nodesByChain.set(node.chainId, [])
    }
    nodesByChain.get(node.chainId)!.push(node)
  })
  
  // For each chain, create edges between consecutive tiers
  nodesByChain.forEach((chainNodes, chainId) => {
    // Sort nodes by tier hierarchy
    const sortedNodes = [...chainNodes].sort((a, b) => {
      const aValue = getTierValue(a.tier)
      const bValue = getTierValue(b.tier)
      return aValue - bValue
    })
    
    // Create edges: bronze → silver, silver → gold
    for (let i = 0; i < sortedNodes.length - 1; i++) {
      const source = sortedNodes[i]
      const target = sortedNodes[i + 1]
      const edgeId = `${source.id}-${target.id}`
      
      // Get metadata for this edge if provided
      const metadata = edgeMetadata?.[edgeId] || {}
      
      // Achievement chain edges (tier progression) don't need labels
      const label = ''
      
      edges.push({
        id: edgeId,
        source: source.id,
        target: target.id,
        label,
        chainId,
        metadata,
      })
    }
  })
  
  return edges
}

/**
 * Create edges from achievements to math concepts based on unlock requirements
 * @param achievementNodes - Array of achievement nodes
 * @param conceptNodes - Array of math concept nodes
 * @param achievements - Original achievement data (for metadata lookup)
 */
export function createAchievementToConceptEdges(
  achievementNodes: ForceGraphNode[],
  conceptNodes: ForceGraphNode[],
  achievements: Achievement[]
): ForceGraphEdge[] {
  const edges: ForceGraphEdge[] = []
  const conceptNodeMap = new Map(conceptNodes.map(n => [n.conceptId!, n]))
  const achievementMap = new Map(achievements.map(a => [a.id, a]))
  
  // Find the generic math-master-bronze node (the one shown in the graph)
  const mathMasterBronzeNode = achievementNodes.find(n => n.id === 'math-master-bronze')
  
  // Check if there's a math-master-bronze achievement with concept_id: c_add_1s metadata
  // (even if it's not shown as a separate node, we use the generic node for the connection)
  const hasMathMasterBronzeFor1s = achievements.some(a => 
    a.id.includes('math-master-bronze') && a.metadata?.concept_id === 'c_add_1s'
  )
  
  // Create edges based on unlock requirements
  // c_add_2s requires:
  // 1. math-master-bronze with concept_id: c_add_1s
  // 2. speed-demon-bronze (any)
  
  const c_add_2s = conceptNodeMap.get('c_add_2s')
  if (c_add_2s) {
    // Link math-master-bronze (for c_add_1s) -> c_add_2s
    // Use the generic math-master-bronze node, but only if we have the achievement with metadata
    if (mathMasterBronzeNode && hasMathMasterBronzeFor1s) {
      edges.push({
        id: `${mathMasterBronzeNode.id}-${c_add_2s.id}`,
        source: mathMasterBronzeNode.id,
        target: c_add_2s.id,
        label: 'qty 1',
        chainId: 'unlock-requirement',
        labelColor: 'green',
      })
    }
    
    // Link speed-demon-bronze -> c_add_2s
    const speedDemonBronze = achievementNodes.find(n => n.id === 'speed-demon-bronze')
    if (speedDemonBronze) {
      edges.push({
        id: `${speedDemonBronze.id}-${c_add_2s.id}`,
        source: speedDemonBronze.id,
        target: c_add_2s.id,
        label: 'qty 1',
        chainId: 'unlock-requirement',
        labelColor: 'green',
      })
    }
  }
  
  return edges
}

/**
 * Create root category nodes (Math Concepts and Achievements)
 */
export function createRootCategoryNodes(): ForceGraphNode[] {
  return [
    {
      id: 'root-math-concepts',
      title: 'Math Concepts',
      icon: '📚',
      tier: 'Root',
      status: 'unlocked',
      chainId: 'root-categories',
      isRoot: true,
      size: 27, // Slightly larger than math concept nodes (18px)
      type: 'root-category' as const,
    },
    {
      id: 'root-achievements',
      title: 'Achievements',
      icon: '🏆',
      tier: 'Root',
      status: 'unlocked',
      chainId: 'root-categories',
      isRoot: true,
      size: 27, // Same size as Math Concepts root
      type: 'root-category' as const,
    },
  ]
}

/**
 * Create edges from root category nodes to their respective root items
 * @param achievementNodes - Array of achievement nodes
 * @param conceptNodes - Array of math concept nodes
 */
export function createRootCategoryEdges(
  achievementNodes: ForceGraphNode[],
  conceptNodes: ForceGraphNode[]
): ForceGraphEdge[] {
  const edges: ForceGraphEdge[] = []
  
  // Connect all root achievement nodes to "Achievements" root node
  const rootAchievementNode = achievementNodes.filter(node => node.isRoot && node.type === 'achievement')
  rootAchievementNode.forEach(node => {
    edges.push({
      id: `root-achievements-${node.id}`,
      source: 'root-achievements',
      target: node.id,
      label: '',
      chainId: 'root-category',
    })
  })
  
  // Connect Single Digit Addition (1s) to "Math Concepts" root node
  const c_add_1s = conceptNodes.find(n => n.conceptId === 'c_add_1s')
  if (c_add_1s) {
    edges.push({
      id: `root-math-concepts-${c_add_1s.id}`,
      source: 'root-math-concepts',
      target: c_add_1s.id,
      label: '',
      chainId: 'root-category',
    })
  }
  
  return edges
}

/**
 * Create edges from math concepts to other math concepts based on prerequisites
 * @param conceptNodes - Array of math concept nodes
 */
export function createConceptToConceptEdges(
  conceptNodes: ForceGraphNode[]
): ForceGraphEdge[] {
  const edges: ForceGraphEdge[] = []
  const conceptNodeMap = new Map(conceptNodes.map(n => [n.conceptId!, n]))
  
  // c_add_2s requires mastery of c_add_1s
  const c_add_1s = conceptNodeMap.get('c_add_1s')
  const c_add_2s = conceptNodeMap.get('c_add_2s')
  
  if (c_add_1s && c_add_2s) {
    edges.push({
      id: `${c_add_1s.id}-${c_add_2s.id}`,
      source: c_add_1s.id,
      target: c_add_2s.id,
      label: '', // No label for concept-to-concept edges
      chainId: 'concept-prerequisite',
    })
  }
  
  return edges
}

/**
 * Transform achievements and math concepts into complete force graph data
 * @param achievements - Array of achievements to transform
 * @param concepts - Array of math concepts to transform
 * @param edgeMetadata - Optional metadata for edges (e.g., { "speed-demon-bronze-speed-demon-silver": { quantity: 4 } })
 */
export function transformAchievementsToForceGraph(
  achievements: Achievement[],
  concepts: MathConcept[] = [],
  edgeMetadata?: Record<string, { quantity?: number; [key: string]: any }>
): {
  nodes: ForceGraphNode[]
  edges: ForceGraphEdge[]
} {
  const achievementNodes = createForceGraphNodes(achievements)
  const conceptNodes = createForceGraphNodesFromConcepts(concepts)
  const rootCategoryNodes = createRootCategoryNodes()
  const nodes = [...rootCategoryNodes, ...achievementNodes, ...conceptNodes]
  
  // Create all types of edges
  const achievementChainEdges = createForceGraphEdges(achievementNodes, edgeMetadata)
  const achievementToConceptEdges = createAchievementToConceptEdges(achievementNodes, conceptNodes, achievements)
  const conceptToConceptEdges = createConceptToConceptEdges(conceptNodes)
  const rootCategoryEdges = createRootCategoryEdges(achievementNodes, conceptNodes)
  
  const edges = [...rootCategoryEdges, ...achievementChainEdges, ...achievementToConceptEdges, ...conceptToConceptEdges]
  
  return { nodes, edges }
}
