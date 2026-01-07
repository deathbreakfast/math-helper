/**
 * Utilities for transforming achievements and math concepts into force graph data structures
 */

import type { Achievement } from '../data/achievements'
import type { MathConcept } from '../data/mathConcepts'
import { extractTierFromCode, TIER_ORDER } from './achievementUtils'

/**
 * Normalize achievements for force graph display.
 * 
 * Backend achievements have IDs like "math-master-bronze" with metadata { concept_id: "c_add_1s" }.
 * Force graph expects IDs like "math-master-bronze-c_add_1s" for concept-specific achievements.
 * 
 * This function transforms achievements with metadata into the expected format:
 * - Achievements WITH metadata.concept_id get their ID transformed to include the concept_id
 *   e.g., "math-master-bronze" + metadata.concept_id="c_add_1s" → "math-master-bronze-c_add_1s"
 * - Achievements WITHOUT metadata keep their original ID
 * 
 * This ensures live data works the same as mock data in the force graph.
 */
function normalizeAchievementsForGraph(achievements: Achievement[]): Achievement[] {
  return achievements.map(achievement => {
    // Skip normalization if ID already contains "-required-by-" (enriched achievements)
    // These have already been properly formatted in enrichAchievementsWithConceptVariants
    if (achievement.id.includes('-required-by-')) {
      return achievement
    }
    
    // If achievement has concept_id in metadata, create a combined ID
    const conceptId = achievement.metadata?.concept_id
    if (conceptId && typeof conceptId === 'string') {
      // Extract base code and tier from original ID
      const { baseCode, tier } = extractTierFromCode(achievement.id)
      
      // Check if ID already has concept_id suffix (from mock data)
      if (achievement.id.endsWith(`-${conceptId}`)) {
        return achievement // Already in correct format
      }
      
      // Create new ID: baseCode-tier-conceptId (e.g., "math-master-bronze-c_add_1s")
      const newId = tier && baseCode 
        ? `${baseCode}-${tier.toLowerCase()}-${conceptId}`
        : `${achievement.id}-${conceptId}`
      
      return {
        ...achievement,
        id: newId,
      }
    }
    
    return achievement
  })
}

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
  relatedConceptLocked?: boolean // For achievements with metadata: whether the related concept is locked
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
 * Extract required achievement codes and maximum tiers from backend concept requirements
 */
function getRequiredAchievementData(
  backendRequirements?: Record<string, Array<{
    achievement_code: string
    quantity?: number
    metadata_filter?: Record<string, any>
  }>>
): {
  requiredCodes: Set<string>
  maxTierByBaseCode: Map<string, number> // baseCode -> max tier value
  maxTierByBaseCodeAndConcept: Map<string, number> // "baseCode:conceptId" -> max tier value
} {
  const requiredCodes = new Set<string>()
  const maxTierByBaseCode = new Map<string, number>()
  const maxTierByBaseCodeAndConcept = new Map<string, number>()
  
  if (!backendRequirements) {
    return { requiredCodes, maxTierByBaseCode, maxTierByBaseCodeAndConcept }
  }
  
  // Extract all unique achievement codes from requirements and track max tiers
  for (const reqs of Object.values(backendRequirements)) {
    for (const req of reqs) {
      if (req.achievement_code) {
        requiredCodes.add(req.achievement_code)
        
        const { baseCode, tier } = extractTierFromCode(req.achievement_code)
        if (baseCode && tier) {
          const tierValue = getTierValue(tier)
          
          // Track max tier for base code (for achievements without metadata)
          const currentMax = maxTierByBaseCode.get(baseCode) || 0
          if (tierValue > currentMax) {
            maxTierByBaseCode.set(baseCode, tierValue)
          }
          
          // Track max tier for base code + concept (for achievements with metadata)
          if (req.metadata_filter?.concept_id) {
            const conceptId = req.metadata_filter.concept_id as string
            const key = `${baseCode}:${conceptId}`
            const currentMaxWithConcept = maxTierByBaseCodeAndConcept.get(key) || 0
            if (tierValue > currentMaxWithConcept) {
              maxTierByBaseCodeAndConcept.set(key, tierValue)
            }
          }
        }
        
        // Also extract base code (e.g., "math-master-bronze" -> "math-master")
        if (baseCode) {
          requiredCodes.add(baseCode)
        }
      }
    }
  }
  
  return { requiredCodes, maxTierByBaseCode, maxTierByBaseCodeAndConcept }
}

/**
 * Filter achievements for force graph display
 * Only includes achievements that are required by at least one math concept,
 * and only shows tiers up to the maximum required tier for each achievement base code
 */
function filterSpeedDemonAchievements(
  achievements: Achievement[],
  backendRequirements?: Record<string, Array<{
    achievement_code: string
    quantity?: number
    metadata_filter?: Record<string, any>
  }>>
): Achievement[] {
  // If backendRequirements is not provided, return empty (requirements not loaded yet)
  if (!backendRequirements) {
    return []
  }
  
  // Get required achievement codes and max tiers from backend requirements
  const { requiredCodes, maxTierByBaseCode, maxTierByBaseCodeAndConcept } = getRequiredAchievementData(backendRequirements)
  
  // If no requirements found, return empty (no concepts require any achievements)
  if (requiredCodes.size === 0) {
    return []
  }
  
  return achievements.filter(achievement => {
    let { baseCode, tier } = extractTierFromCode(achievement.id)
    
    // Handle concept-specific achievements where tier is in the middle
    // Formats: "math-master-bronze-c_add_1s" or "math-master-bronze-c_add_1s-required-by-c_add_2s"
    // If extraction failed (tier is in middle), manually extract baseCode and tier
    if (!tier || baseCode === achievement.id) {
      const tierNames = ['bronze', 'silver', 'gold', 'platinum', 'diamond', 'master', 'grandmaster', 'legendary', 'mythic', 'divine', 'champion']
      for (const tierName of tierNames) {
        const tierIndex = achievement.id.indexOf(`-${tierName}-`)
        if (tierIndex > 0) {
          baseCode = achievement.id.substring(0, tierIndex)
          tier = tierName.charAt(0).toUpperCase() + tierName.slice(1)
          break
        }
      }
    }
    
    // If still no baseCode or tier, check if it's a non-tiered achievement
    if (!baseCode) {
      baseCode = achievement.id
    }
    
    // Check if achievement is required
    let isRequired = false
    if (requiredCodes.has(baseCode)) {
      isRequired = true
    } else if (tier && baseCode) {
      const fullCode = `${baseCode}-${tier.toLowerCase()}`
      if (requiredCodes.has(fullCode)) {
        isRequired = true
      }
    }
    
    // Check if achievement ID itself is required (for concept-specific variants)
    if (!isRequired && requiredCodes.has(achievement.id)) {
      isRequired = true
    }
    
    // Check if achievement starts with a required code (for concept-specific variants like "math-master-bronze-c_add_1s")
    if (!isRequired) {
      for (const code of requiredCodes) {
        if (achievement.id.startsWith(`${code}-`)) {
          isRequired = true
          break
        }
      }
    }
    
    if (!isRequired) {
      return false
    }
    
    // Now check tier limits - only show tiers up to the maximum required tier
    if (tier && baseCode) {
      const tierValue = getTierValue(tier)
      
      // For achievements with metadata, check max tier per baseCode+conceptId
      if (achievement.metadata?.concept_id) {
        const conceptId = achievement.metadata.concept_id as string
        const key = `${baseCode}:${conceptId}`
        const maxTier = maxTierByBaseCodeAndConcept.get(key)
        if (maxTier !== undefined && tierValue > maxTier) {
          return false // Tier is higher than required, don't show
        }
      } else {
        // For achievements without metadata, check max tier per baseCode
        const maxTier = maxTierByBaseCode.get(baseCode)
        if (maxTier !== undefined && tierValue > maxTier) {
          return false // Tier is higher than required, don't show
        }
      }
    }
    
    return true
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
export function createForceGraphNodes(
  achievements: Achievement[],
  concepts: MathConcept[] = [],
  backendRequirements?: Record<string, Array<{
    achievement_code: string
    quantity?: number
    metadata_filter?: Record<string, any>
  }>>
): ForceGraphNode[] {
  const filtered = filterSpeedDemonAchievements(achievements, backendRequirements)
  const conceptMap = new Map(concepts.map(c => [c.conceptId, c]))
  
  return filtered.map(achievement => {
    const { baseCode, tier } = extractTierFromCode(achievement.id)
    const tierValue = tier ? getTierValue(tier) : 999
    
    // For non-tiered achievements (first-steps, first-victory), use the achievement ID as chainId
    // For tiered achievements with required_by metadata, create unique chain per requirement
    // Otherwise use the baseCode
    let chainId: string
    if (tier && achievement.metadata?.required_by) {
      // Create unique chain for each requirement: baseCode-conceptId-required-by-requiringConceptId
      const conceptId = achievement.metadata.concept_id || ''
      const requiredBy = achievement.metadata.required_by
      chainId = `${baseCode}-${conceptId}-required-by-${requiredBy}`
    } else {
      chainId = tier ? baseCode : achievement.id
    }
    
    // Format title: "Achievement Name (Tier) - Math Concept" if there's concept_id metadata
    let title = achievement.title
    let relatedConceptLocked: boolean | undefined = undefined
    if (achievement.metadata?.concept_id) {
      const concept = conceptMap.get(achievement.metadata.concept_id)
      if (concept) {
        title = `${achievement.title} - ${concept.displayName}`
        relatedConceptLocked = concept.isLocked
      }
    }
    
    // Determine icon with fallbacks
    let icon = achievement.icon
    if (!icon) {
      // Fallback to icon based on achievement base code
      if (baseCode === 'math-master') {
        icon = '🎯'
      } else if (baseCode === 'speed-demon') {
        icon = '⚡'
      } else if (baseCode === 'lightning-fast') {
        icon = '⚡'
      } else if (baseCode === 'perfect-streak') {
        icon = '🔥'
      } else if (baseCode === 'accuracy-ace') {
        icon = '🎯'
      } else if (baseCode === 'question-master') {
        icon = '📚'
      } else if (baseCode === 'week-warrior') {
        icon = '📅'
      } else if (baseCode?.startsWith('master-of-')) {
        icon = '👑'
      } else {
        icon = '🏆' // Default fallback
      }
    }
    
    return {
      id: achievement.id,
      achievementId: achievement.id,
      title,
      icon,
      tier: tier || achievement.tier || 'Unknown', // Use tier from extraction or fallback to achievement.tier
      status: achievement.status,
      chainId,
      isRoot: tier === 'Bronze' || !tier, // Root nodes are bronze tier or non-tiered achievements
      size: 9, // Achievement nodes are small (about 1/4 of original 35px)
      type: 'achievement' as const,
      relatedConceptLocked,
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
 * @param achievements - Original achievement data (for metadata lookup)
 * @param edgeMetadata - Optional metadata for edges keyed by edge ID
 */
export function createForceGraphEdges(
  nodes: ForceGraphNode[],
  achievements: Achievement[],
  edgeMetadata?: Record<string, { quantity?: number; [key: string]: any }>
): ForceGraphEdge[] {
  const edges: ForceGraphEdge[] = []
  const achievementMap = new Map(achievements.map(a => [a.id, a]))
  
  // First, handle achievements with metadata (concept_id) - these need to be grouped by baseCode + concept_id + required_by
  // This ensures each requirement chain has its own separate tier progression
  const achievementNodes = nodes.filter(n => n.type === 'achievement')
  const nodesByConceptAndBase = new Map<string, ForceGraphNode[]>()
  const nodesWithMetadata = new Set<string>() // Track which nodes have metadata
  
  achievementNodes.forEach(node => {
    if (node.achievementId) {
      const achievement = achievementMap.get(node.achievementId)
      if (achievement?.metadata?.concept_id) {
        nodesWithMetadata.add(node.id)
        // For metadata-specific achievements like "math-master-bronze-c_add_1s-required-by-c_add_2s",
        // we need to extract the baseCode differently since the tier is in the middle
        // Try to extract baseCode, but if tier is null, manually extract it
        let baseCode = extractTierFromCode(achievement.id).baseCode
        // If extraction failed (tier is in middle), manually extract baseCode
        // Pattern: "math-master-bronze-c_add_1s-required-by-c_add_2s" -> baseCode should be "math-master"
        if (!baseCode || baseCode === achievement.id) {
          // Find the tier in the ID and extract everything before it
          const tierNames = ['bronze', 'silver', 'gold', 'platinum', 'diamond', 'master', 'grandmaster', 'legendary', 'mythic', 'divine', 'champion']
          for (const tierName of tierNames) {
            const tierIndex = achievement.id.indexOf(`-${tierName}-`)
            if (tierIndex > 0) {
              baseCode = achievement.id.substring(0, tierIndex)
              break
            }
          }
        }
        // Group by baseCode + concept_id + required_by to create separate chains for each requirement
        const requiredBy = achievement.metadata.required_by || 'shared'
        const key = `${baseCode}-${achievement.metadata.concept_id}-required-by-${requiredBy}`
        if (!nodesByConceptAndBase.has(key)) {
          nodesByConceptAndBase.set(key, [])
        }
        nodesByConceptAndBase.get(key)!.push(node)
      }
    }
  })
  
  // Create edges between tiers for achievements with the same base code and concept_id
  // e.g., math-master-bronze-c_add_1s -> math-master-silver-c_add_1s
  nodesByConceptAndBase.forEach((conceptNodes, key) => {
    // Sort by tier - ensure tier is capitalized for getTierValue
    const sorted = [...conceptNodes].sort((a, b) => {
      // Ensure tier is capitalized (first letter uppercase)
      const aTier = a.tier ? a.tier.charAt(0).toUpperCase() + a.tier.slice(1) : a.tier
      const bTier = b.tier ? b.tier.charAt(0).toUpperCase() + b.tier.slice(1) : b.tier
      const aValue = getTierValue(aTier)
      const bValue = getTierValue(bTier)
      return aValue - bValue
    })
    
    // Create edges between consecutive tiers
    for (let i = 0; i < sorted.length - 1; i++) {
      const source = sorted[i]
      const target = sorted[i + 1]
      const edgeId = `${source.id}-${target.id}`
      
      // Only create edge if tiers are actually consecutive (not skipping tiers)
      // This ensures we don't create edges like bronze -> gold (skipping silver)
      const sourceTier = source.tier ? source.tier.charAt(0).toUpperCase() + source.tier.slice(1) : source.tier
      const targetTier = target.tier ? target.tier.charAt(0).toUpperCase() + target.tier.slice(1) : target.tier
      const sourceValue = getTierValue(sourceTier)
      const targetValue = getTierValue(targetTier)
      
      // Only create edge if target is exactly one tier higher
      if (targetValue === sourceValue + 1) {
        edges.push({
          id: edgeId,
          source: source.id,
          target: target.id,
          label: '',
          chainId: key,
          metadata: {},
        })
      }
    }
  })
  
  // Then, handle achievements without metadata - group by chainId (baseCode)
  const nodesByChain = new Map<string, ForceGraphNode[]>()
  nodes.forEach(node => {
    // Skip nodes that already have metadata (they were handled above)
    if (node.type === 'achievement' && nodesWithMetadata.has(node.id)) {
      return
    }
    
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
      
      // Skip if edge already exists (shouldn't happen for non-metadata nodes, but be safe)
      if (edges.find(e => e.id === edgeId)) {
        continue
      }
      
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
 * @param backendRequirements - Backend concept requirements with metadata filters
 */
export function createAchievementToConceptEdges(
  achievementNodes: ForceGraphNode[],
  conceptNodes: ForceGraphNode[],
  achievements: Achievement[],
  backendRequirements?: Record<string, Array<{
    achievement_code: string
    quantity?: number
    metadata_filter?: Record<string, any>
  }>>
): ForceGraphEdge[] {
  const edges: ForceGraphEdge[] = []
  const conceptNodeMap = new Map(conceptNodes.map(n => [n.conceptId!, n]))
  const achievementMap = new Map(achievements.map(a => [a.id, a]))
  const achievementNodeMap = new Map(achievementNodes.map(n => [n.id, n]))
  
  // If backend requirements are available, use them to dynamically create edges
  if (backendRequirements) {
    for (const [conceptId, reqs] of Object.entries(backendRequirements)) {
      const conceptNode = conceptNodeMap.get(conceptId)
      if (!conceptNode) continue
      
      for (const req of reqs) {
        const achievementCode = req.achievement_code
        const quantity = req.quantity || 1
        const sourceConceptId = req.metadata_filter?.concept_id
        
        // Build the expected unique achievement node ID
        // Format: baseCode-tier-sourceConceptId-required-by-requiringConceptId (with concept_id)
        // Format: baseCode-tier-required-by-requiringConceptId (without concept_id)
        const { baseCode, tier } = extractTierFromCode(achievementCode)
        let expectedAchievementId: string
        
        if (sourceConceptId && tier && baseCode) {
          // Concept-specific achievement: math-master-bronze-c_add_1s-required-by-c_add_2s
          expectedAchievementId = `${baseCode}-${tier.toLowerCase()}-${sourceConceptId}-required-by-${conceptId}`
        } else if (sourceConceptId && !tier) {
          // Concept-specific non-tiered achievement
          expectedAchievementId = `${achievementCode}-${sourceConceptId}-required-by-${conceptId}`
        } else if (tier && baseCode) {
          // Non-concept-specific achievement: perfect-streak-bronze-required-by-c_add_7s
          expectedAchievementId = `${baseCode}-${tier.toLowerCase()}-required-by-${conceptId}`
        } else {
          // Non-tiered achievement: first-steps-required-by-...
          expectedAchievementId = `${achievementCode}-required-by-${conceptId}`
        }
        
        const achievementNode = achievementNodeMap.get(expectedAchievementId)
        if (achievementNode) {
          edges.push({
            id: `${achievementNode.id}-${conceptNode.id}`,
            source: achievementNode.id,
            target: conceptNode.id,
            label: quantity > 1 ? `qty ${quantity}` : '',
            chainId: 'unlock-requirement',
            labelColor: 'green',
          })
          if (import.meta.env.DEV && conceptId === 'c_add_2s') {
            console.log(`✅ Edge created: ${expectedAchievementId} -> ${conceptId}`)
          }
        } else if (import.meta.env.DEV) {
          // Debug logging in development
          const availableNodeIds = Array.from(achievementNodeMap.keys())
            .filter(id => id.includes(achievementCode) || id.includes(baseCode || ''))
            .slice(0, 10)
          console.warn(`⚠️ Edge creation failed for ${conceptId}:`, {
            achievementCode,
            sourceConceptId,
            expectedAchievementId,
            availableSimilarNodes: availableNodeIds,
            allNodeIds: Array.from(achievementNodeMap.keys()).length,
            fullNodeIds: Array.from(achievementNodeMap.keys()).filter(id => 
              id.includes(achievementCode) || id.includes(baseCode || '')
            ),
          })
        }
      }
    }
    
    return edges
  }
  
  // Fallback to hardcoded edges if backend requirements not available
  // Helper function to create an edge from an achievement to a concept
  const createEdge = (achievementId: string, conceptId: string, quantity: number = 1) => {
    // Find achievement node that matches the base achievement ID and is required by this concept
    // The unique ID format is: baseCode-tier-sourceConceptId-required-by-requiringConceptId
    const achievementNode = achievementNodes.find(n => {
      // Check if the node ID starts with the achievementId and ends with -required-by-conceptId
      return n.id.startsWith(achievementId) && n.id.endsWith(`-required-by-${conceptId}`)
    })
    const conceptNode = conceptNodeMap.get(conceptId)
    if (achievementNode && conceptNode) {
      edges.push({
        id: `${achievementNode.id}-${conceptNode.id}`,
        source: achievementNode.id,
        target: conceptNode.id,
        label: `qty ${quantity}`,
        chainId: 'unlock-requirement',
        labelColor: 'green',
      })
    }
  }
  
  // Helper function to find the highest tier achievement for a given base code and concept_id
  const findHighestTierForConcept = (baseCode: string, conceptId: string): string | null => {
    const matchingAchievements = achievements.filter(a => {
      const { baseCode: aBaseCode } = extractTierFromCode(a.id)
      return aBaseCode === baseCode && a.metadata?.concept_id === conceptId
    })
    
    if (matchingAchievements.length === 0) return null
    
    // Sort by tier and return the highest
    const sorted = matchingAchievements.sort((a, b) => {
      const { tier: aTier } = extractTierFromCode(a.id)
      const { tier: bTier } = extractTierFromCode(b.id)
      const aValue = aTier ? getTierValue(aTier) : 0
      const bValue = bTier ? getTierValue(bTier) : 0
      return bValue - aValue // Descending order
    })
    
    return sorted[0].id
  }
  
  // c_add_2s requires:
  // 1. math-master-bronze with concept_id: c_add_1s
  // 2. speed-demon-bronze (for c_add_2s)
  createEdge('math-master-bronze-c_add_1s', 'c_add_2s')
  createEdge('speed-demon-bronze-c_add_2s', 'c_add_2s')
  
  // c_add_3s requires:
  // 1. math-master-bronze with concept_id: c_add_2s
  createEdge('math-master-bronze-c_add_2s', 'c_add_3s')
  
  // c_add_4s requires:
  // 1. math-master-bronze with concept_id: c_add_3s
  // 2. lightning-fast-bronze with concept_id: c_add_1s
  createEdge('math-master-bronze-c_add_3s', 'c_add_4s')
  createEdge('lightning-fast-bronze-c_add_1s', 'c_add_4s')
  
  // c_add_5s requires:
  // 1. math-master-bronze with concept_id: c_add_4s
  // 2. speed-demon-bronze (for c_add_5s, quantity: 2)
  createEdge('math-master-bronze-c_add_4s', 'c_add_5s')
  createEdge('speed-demon-bronze-c_add_5s', 'c_add_5s', 2)
  
  // c_add_6s requires:
  // 1. math-master-bronze with concept_id: c_add_5s
  // 2. math-master-silver with concept_id: c_add_1s
  // Link both requirements directly to the concept
  // The prerequisite chain (bronze -> silver for c_add_1s) will be created by createForceGraphEdges
  createEdge('math-master-bronze-c_add_5s', 'c_add_6s')
  createEdge('math-master-silver-c_add_1s', 'c_add_6s')
  
  // c_add_7s requires:
  // 1. math-master-bronze with concept_id: c_add_6s
  // 2. perfect-streak-bronze
  createEdge('math-master-bronze-c_add_6s', 'c_add_7s')
  createEdge('perfect-streak-bronze', 'c_add_7s')
  
  // c_add_8s requires:
  // 1. math-master-bronze with concept_id: c_add_7s
  // 2. lightning-fast-bronze with concept_id: c_add_2s
  createEdge('math-master-bronze-c_add_7s', 'c_add_8s')
  createEdge('lightning-fast-bronze-c_add_2s', 'c_add_8s')
  
  // c_add_9s requires:
  // 1. math-master-bronze with concept_id: c_add_8s
  // 2. math-master-silver with concept_id: c_add_1s (gold was removed, so silver is now highest)
  // Link both requirements directly to the concept
  // The prerequisite chain (bronze -> silver for c_add_1s) will be created by createForceGraphEdges
  createEdge('math-master-bronze-c_add_8s', 'c_add_9s')
  createEdge('math-master-silver-c_add_1s', 'c_add_9s')
  
  // c_add_0s requires:
  // 1. math-master-bronze with concept_id: c_add_9s
  // 2. speed-demon-silver (for c_add_0s)
  createEdge('math-master-bronze-c_add_9s', 'c_add_0s')
  createEdge('speed-demon-silver-c_add_0s', 'c_add_0s')
  
  // c_add_10s requires:
  // 1. math-master-bronze with concept_id: c_add_9s
  // 2. math-master-bronze with concept_id: c_add_1s
  // 3. accuracy-ace-bronze (quantity: 20)
  createEdge('math-master-bronze-c_add_9s', 'c_add_10s')
  createEdge('math-master-bronze-c_add_1s', 'c_add_10s')
  createEdge('accuracy-ace-bronze', 'c_add_10s', 20)
  
  // c_concept_001 (Basic Single Digit Addition) requires:
  // 1. math-master-bronze with concept_id: c_add_10s
  // 2. math-master-bronze with concept_id: c_add_0s
  // 3. master-of-basic-addition-bronze
  createEdge('math-master-bronze-c_add_10s', 'c_concept_001')
  createEdge('math-master-bronze-c_add_0s', 'c_concept_001')
  createEdge('master-of-basic-addition-bronze', 'c_concept_001')
  
  // c_concept_005 (Single and Two Digit Addition) requires:
  // 1. math-master-bronze with concept_id: c_concept_001
  createEdge('math-master-bronze-c_concept_001', 'c_concept_005')
  
  // c_concept_007 (Two Digit Addition) requires:
  // 1. math-master-bronze with concept_id: c_concept_005
  createEdge('math-master-bronze-c_concept_005', 'c_concept_007')
  
  // c_concept_022 (Three Digit Addition) requires:
  // 1. math-master-bronze with concept_id: c_concept_007
  createEdge('math-master-bronze-c_concept_007', 'c_concept_022')
  
  // c_sub_1s requires:
  // 1. math-master-bronze with concept_id: c_add_2s
  createEdge('math-master-bronze-c_add_2s', 'c_sub_1s')
  
  // c_sub_2s requires:
  // 1. math-master-bronze with concept_id: c_sub_1s
  // 2. math-master-bronze with concept_id: c_add_2s
  createEdge('math-master-bronze-c_sub_1s', 'c_sub_2s')
  createEdge('math-master-bronze-c_add_2s', 'c_sub_2s')
  
  // c_sub_3s requires:
  // 1. math-master-bronze with concept_id: c_sub_2s
  createEdge('math-master-bronze-c_sub_2s', 'c_sub_3s')
  
  // c_sub_4s requires:
  // 1. math-master-bronze with concept_id: c_sub_3s
  // 2. lightning-fast-bronze with concept_id: c_sub_1s
  createEdge('math-master-bronze-c_sub_3s', 'c_sub_4s')
  createEdge('lightning-fast-bronze-c_sub_1s', 'c_sub_4s')
  
  // c_sub_5s requires:
  // 1. math-master-bronze with concept_id: c_sub_4s
  // 2. speed-demon-bronze (quantity: 4)
  createEdge('math-master-bronze-c_sub_4s', 'c_sub_5s')
  createEdge('speed-demon-bronze', 'c_sub_5s', 4)
  
  // c_sub_6s requires:
  // 1. math-master-bronze with concept_id: c_sub_5s
  // 2. math-master-silver with concept_id: c_sub_1s
  createEdge('math-master-bronze-c_sub_5s', 'c_sub_6s')
  createEdge('math-master-silver-c_sub_1s', 'c_sub_6s')
  
  // c_sub_7s requires:
  // 1. math-master-bronze with concept_id: c_sub_6s
  // 2. perfect-streak-bronze (quantity: 2)
  createEdge('math-master-bronze-c_sub_6s', 'c_sub_7s')
  createEdge('perfect-streak-bronze', 'c_sub_7s', 2)
  
  // c_sub_8s requires:
  // 1. math-master-bronze with concept_id: c_sub_7s
  // 2. lightning-fast-bronze with concept_id: c_sub_2s
  createEdge('math-master-bronze-c_sub_7s', 'c_sub_8s')
  createEdge('lightning-fast-bronze-c_sub_2s', 'c_sub_8s')
  
  // c_sub_9s requires:
  // 1. math-master-bronze with concept_id: c_sub_8s
  // 2. math-master-gold with concept_id: c_sub_1s
  createEdge('math-master-bronze-c_sub_8s', 'c_sub_9s')
  createEdge('math-master-gold-c_sub_1s', 'c_sub_9s')
  
  // c_sub_10s requires:
  // 1. math-master-bronze with concept_id: c_sub_9s
  // 2. math-master-silver with concept_id: c_add_10s
  createEdge('math-master-bronze-c_sub_9s', 'c_sub_10s')
  createEdge('math-master-silver-c_add_10s', 'c_sub_10s')
  
  // c_sub_0s requires:
  // 1. math-master-silver with concept_id: c_add_0s
  // 2. math-master-bronze with concept_id: c_sub_9s
  // 3. speed-demon-silver (quantity: 2)
  createEdge('math-master-silver-c_add_0s', 'c_sub_0s')
  createEdge('math-master-bronze-c_sub_9s', 'c_sub_0s')
  createEdge('speed-demon-silver', 'c_sub_0s', 2)
  
  // c_concept_003 (Basic Single Digit Subtraction) requires:
  // 1. master-of-basic-subtraction-bronze
  // 2. math-master-bronze with concept_id: c_sub_10s
  createEdge('master-of-basic-subtraction-bronze', 'c_concept_003')
  createEdge('math-master-bronze-c_sub_10s', 'c_concept_003')
  
  // c_concept_006 (Single and Two Digit Subtraction) requires:
  // 1. math-master-bronze with concept_id: c_concept_003
  createEdge('math-master-bronze-c_concept_003', 'c_concept_006')
  
  // c_concept_008 (Two Digit Subtraction) requires:
  // 1. math-master-bronze with concept_id: c_concept_006
  // 2. math-master-bronze with concept_id: c_concept_010
  createEdge('math-master-bronze-c_concept_006', 'c_concept_008')
  createEdge('math-master-bronze-c_concept_010', 'c_concept_008')
  
  // c_concept_010 (Negative Number Subtraction) requires:
  // 1. math-master-bronze with concept_id: c_concept_003
  createEdge('math-master-bronze-c_concept_003', 'c_concept_010')
  
  // c_concept_023 (Three Digit Subtraction) requires:
  // 1. math-master-bronze with concept_id: c_concept_008
  createEdge('math-master-bronze-c_concept_008', 'c_concept_023')
  
  // Multiplication by 1 (c_concept_011) requires:
  // 1. math-master-silver with concept_id: c_concept_007 (Two Digit Addition)
  createEdge('math-master-silver-c_concept_007', 'c_concept_011')
  
  // Multiplication by 2 (c_mul_2s) requires:
  // 1. math-master-bronze with concept_id: c_concept_011 (Multiplication by 1)
  createEdge('math-master-bronze-c_concept_011', 'c_mul_2s')
  
  // Multiplication by 3 (c_mul_3s) requires:
  // 1. math-master-bronze with concept_id: c_mul_2s (Multiplication by 2)
  createEdge('math-master-bronze-c_mul_2s', 'c_mul_3s')
  
  // Multiplication by 4 (c_concept_012) requires:
  // 1. math-master-bronze with concept_id: c_mul_3s (Multiplication by 3)
  createEdge('math-master-bronze-c_mul_3s', 'c_concept_012')
  
  // Multiplication by 5 (c_concept_013) requires:
  // 1. math-master-bronze with concept_id: c_concept_012 (Multiplication by 4)
  createEdge('math-master-bronze-c_concept_012', 'c_concept_013')
  
  // Multiplication by 6 (c_concept_014) requires:
  // 1. math-master-bronze with concept_id: c_concept_013 (Multiplication by 5)
  createEdge('math-master-bronze-c_concept_013', 'c_concept_014')
  
  // Multiplication by 7 (c_concept_015) requires:
  // 1. math-master-bronze with concept_id: c_concept_014 (Multiplication by 6)
  createEdge('math-master-bronze-c_concept_014', 'c_concept_015')
  
  // Multiplication by 8 (c_concept_016) requires:
  // 1. math-master-bronze with concept_id: c_concept_015 (Multiplication by 7)
  createEdge('math-master-bronze-c_concept_015', 'c_concept_016')
  
  // Multiplication by 9 (c_concept_017) requires:
  // 1. math-master-bronze with concept_id: c_concept_016 (Multiplication by 8)
  createEdge('math-master-bronze-c_concept_016', 'c_concept_017')
  
  // Multiplication by 10 (c_concept_019) requires:
  // 1. math-master-bronze with concept_id: c_concept_017 (Multiplication by 9)
  createEdge('math-master-bronze-c_concept_017', 'c_concept_019')
  
  // Multiplication by 11 (c_concept_020) requires:
  // 1. math-master-bronze with concept_id: c_concept_019 (Multiplication by 10)
  createEdge('math-master-bronze-c_concept_019', 'c_concept_020')
  
  // Multiplication by 12 (c_concept_021) requires:
  // 1. math-master-bronze with concept_id: c_concept_020 (Multiplication by 11)
  createEdge('math-master-bronze-c_concept_020', 'c_concept_021')
  
  // Multiplication by 0 (c_concept_018) requires:
  // 1. math-master-bronze with concept_id: c_concept_021 (Multiplication by 12)
  createEdge('math-master-bronze-c_concept_021', 'c_concept_018')
  
  // Division by 1 (c_concept_026) requires:
  // 1. math-master-bronze with concept_id: c_concept_021 (Multiplication by 12) - as base requirement
  createEdge('math-master-bronze-c_concept_021', 'c_concept_026')
  
  // Division by 2 (c_concept_027) requires:
  // 1. math-master-bronze with concept_id: c_concept_026 (Division by 1)
  createEdge('math-master-bronze-c_concept_026', 'c_concept_027')
  
  // Division by 3 (c_concept_028) requires:
  // 1. math-master-bronze with concept_id: c_concept_027 (Division by 2)
  createEdge('math-master-bronze-c_concept_027', 'c_concept_028')
  
  // Division by 4 (c_concept_029) requires:
  // 1. math-master-bronze with concept_id: c_concept_028 (Division by 3)
  createEdge('math-master-bronze-c_concept_028', 'c_concept_029')
  
  // Division by 5 (c_concept_030) requires:
  // 1. math-master-bronze with concept_id: c_concept_029 (Division by 4)
  createEdge('math-master-bronze-c_concept_029', 'c_concept_030')
  
  // Division by 6 (c_concept_031) requires:
  // 1. math-master-bronze with concept_id: c_concept_030 (Division by 5)
  createEdge('math-master-bronze-c_concept_030', 'c_concept_031')
  
  // Division by 7 (c_concept_032) requires:
  // 1. math-master-bronze with concept_id: c_concept_031 (Division by 6)
  createEdge('math-master-bronze-c_concept_031', 'c_concept_032')
  
  // Division by 8 (c_concept_033) requires:
  // 1. math-master-bronze with concept_id: c_concept_032 (Division by 7)
  createEdge('math-master-bronze-c_concept_032', 'c_concept_033')
  
  // Division by 9 (c_concept_034) requires:
  // 1. math-master-bronze with concept_id: c_concept_033 (Division by 8)
  createEdge('math-master-bronze-c_concept_033', 'c_concept_034')
  
  // Division by 10 (c_concept_035) requires:
  // 1. math-master-bronze with concept_id: c_concept_034 (Division by 9)
  createEdge('math-master-bronze-c_concept_034', 'c_concept_035')
  
  // Division by 11 (c_concept_036) requires:
  // 1. math-master-bronze with concept_id: c_concept_035 (Division by 10)
  createEdge('math-master-bronze-c_concept_035', 'c_concept_036')
  
  // Division by 0 (c_concept_037) requires:
  // 1. math-master-bronze with concept_id: c_concept_036 (Division by 11)
  createEdge('math-master-bronze-c_concept_036', 'c_concept_037')
  
  // Division by 10 (Repeated) (c_concept_038) requires:
  // 1. math-master-bronze with concept_id: c_concept_037 (Division by 0)
  createEdge('math-master-bronze-c_concept_037', 'c_concept_038')
  
  // Division with Remainders (Single Digit Divisors) (c_concept_039) requires:
  // 1. math-master-bronze with concept_id: c_concept_038 (Division by 10 Repeated)
  createEdge('math-master-bronze-c_concept_038', 'c_concept_039')
  
  // Division with Remainders (Two Digit Dividends) (c_concept_040) requires:
  // 1. math-master-bronze with concept_id: c_concept_039 (Division with Remainders Single Digit)
  createEdge('math-master-bronze-c_concept_039', 'c_concept_040')
  
  // Division with Fractional Answers (Single Digit Divisors) (c_concept_041) requires:
  // 1. math-master-bronze with concept_id: c_concept_040 (Division with Remainders Two Digit)
  createEdge('math-master-bronze-c_concept_040', 'c_concept_041')
  
  // Division with Fractional Answers (Two Digit Dividends) (c_concept_042) requires:
  // 1. math-master-bronze with concept_id: c_concept_041 (Division with Fractional Answers Single Digit)
  createEdge('math-master-bronze-c_concept_041', 'c_concept_042')
  
  // Division with Fractional Answers (Three Digit Dividends) (c_concept_044) requires:
  // 1. math-master-bronze with concept_id: c_concept_042 (Division with Fractional Answers Two Digit)
  createEdge('math-master-bronze-c_concept_042', 'c_concept_044')
  
  // Division with Decimal Answers (Single Digit Divisors) (c_concept_045) requires:
  // 1. math-master-bronze with concept_id: c_concept_044 (Division with Fractional Answers Three Digit)
  createEdge('math-master-bronze-c_concept_044', 'c_concept_045')
  
  return edges
}

/**
 * Create root category nodes (Math Concepts only)
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
  
  // Create concept prerequisite chain: 1s -> 2s -> 3s -> 4s -> 5s -> 6s -> 7s -> 8s -> 9s -> 0s -> 10s
  const conceptChain = ['c_add_1s', 'c_add_2s', 'c_add_3s', 'c_add_4s', 'c_add_5s', 'c_add_6s', 'c_add_7s', 'c_add_8s', 'c_add_9s', 'c_add_0s', 'c_add_10s']
  
  for (let i = 0; i < conceptChain.length - 1; i++) {
    const sourceConcept = conceptNodeMap.get(conceptChain[i])
    const targetConcept = conceptNodeMap.get(conceptChain[i + 1])
    
    if (sourceConcept && targetConcept) {
      edges.push({
        id: `${sourceConcept.id}-${targetConcept.id}`,
        source: sourceConcept.id,
        target: targetConcept.id,
        label: '', // No label for concept-to-concept edges
        chainId: 'concept-prerequisite',
      })
    }
  }
  
  // Create concept prerequisite chain for subtraction: 1s -> 2s -> 3s -> 4s -> 5s -> 6s -> 7s -> 8s -> 9s -> 0s -> 10s
  const subConceptChain = ['c_sub_1s', 'c_sub_2s', 'c_sub_3s', 'c_sub_4s', 'c_sub_5s', 'c_sub_6s', 'c_sub_7s', 'c_sub_8s', 'c_sub_9s', 'c_sub_0s', 'c_sub_10s']
  
  for (let i = 0; i < subConceptChain.length - 1; i++) {
    const sourceConcept = conceptNodeMap.get(subConceptChain[i])
    const targetConcept = conceptNodeMap.get(subConceptChain[i + 1])
    
    if (sourceConcept && targetConcept) {
      edges.push({
        id: `${sourceConcept.id}-${targetConcept.id}`,
        source: sourceConcept.id,
        target: targetConcept.id,
        label: '', // No label for concept-to-concept edges
        chainId: 'concept-prerequisite',
      })
    }
  }
  
  // Create concept prerequisite chain for c_concept_XXX addition: 001 -> 005 -> 007 -> 022
  const additionConceptChain = ['c_concept_001', 'c_concept_005', 'c_concept_007', 'c_concept_022']
  
  for (let i = 0; i < additionConceptChain.length - 1; i++) {
    const sourceConcept = conceptNodeMap.get(additionConceptChain[i])
    const targetConcept = conceptNodeMap.get(additionConceptChain[i + 1])
    
    if (sourceConcept && targetConcept) {
      edges.push({
        id: `${sourceConcept.id}-${targetConcept.id}`,
        source: sourceConcept.id,
        target: targetConcept.id,
        label: '', // No label for concept-to-concept edges
        chainId: 'concept-prerequisite',
      })
    }
  }
  
  // Create concept prerequisite chain for c_concept_XXX subtraction: 003 -> 006 -> 008 -> 023
  // Also: 003 -> 010 (for Negative Number Subtraction)
  // Also: 010 and 006 -> 008 (Two Digit Subtraction requires both)
  const subtractionConceptChain = ['c_concept_003', 'c_concept_006', 'c_concept_008', 'c_concept_023']
  
  for (let i = 0; i < subtractionConceptChain.length - 1; i++) {
    const sourceConcept = conceptNodeMap.get(subtractionConceptChain[i])
    const targetConcept = conceptNodeMap.get(subtractionConceptChain[i + 1])
    
    if (sourceConcept && targetConcept) {
      edges.push({
        id: `${sourceConcept.id}-${targetConcept.id}`,
        source: sourceConcept.id,
        target: targetConcept.id,
        label: '', // No label for concept-to-concept edges
        chainId: 'concept-prerequisite',
      })
    }
  }
  
  // c_concept_003 -> c_concept_010 (Negative Number Subtraction)
  const c_concept_003 = conceptNodeMap.get('c_concept_003')
  const c_concept_010 = conceptNodeMap.get('c_concept_010')
  if (c_concept_003 && c_concept_010) {
    edges.push({
      id: `${c_concept_003.id}-${c_concept_010.id}`,
      source: c_concept_003.id,
      target: c_concept_010.id,
      label: '',
      chainId: 'concept-prerequisite',
    })
  }
  
  // c_concept_010 -> c_concept_008 (Two Digit Subtraction also requires Negative Number Subtraction)
  const c_concept_008 = conceptNodeMap.get('c_concept_008')
  if (c_concept_010 && c_concept_008) {
    edges.push({
      id: `${c_concept_010.id}-${c_concept_008.id}`,
      source: c_concept_010.id,
      target: c_concept_008.id,
      label: '',
      chainId: 'concept-prerequisite',
    })
  }
  
  // Basic Single Digit Addition (c_concept_001) is a child of Single Digit Addition (10s) and (0s)
  const c_add_10s = conceptNodeMap.get('c_add_10s')
  const c_add_0s = conceptNodeMap.get('c_add_0s')
  const c_concept_001 = conceptNodeMap.get('c_concept_001')
  
  if (c_add_10s && c_concept_001) {
    edges.push({
      id: `${c_add_10s.id}-${c_concept_001.id}`,
      source: c_add_10s.id,
      target: c_concept_001.id,
      label: '',
      chainId: 'concept-prerequisite',
    })
  }
  
  if (c_add_0s && c_concept_001) {
    edges.push({
      id: `${c_add_0s.id}-${c_concept_001.id}`,
      source: c_add_0s.id,
      target: c_concept_001.id,
      label: '',
      chainId: 'concept-prerequisite',
    })
  }
  
  // Basic Single Digit Subtraction (c_concept_003) is a child of Single Digit Subtraction (10s)
  const c_sub_10s = conceptNodeMap.get('c_sub_10s')
  
  if (c_sub_10s && c_concept_003) {
    edges.push({
      id: `${c_sub_10s.id}-${c_concept_003.id}`,
      source: c_sub_10s.id,
      target: c_concept_003.id,
      label: '',
      chainId: 'concept-prerequisite',
    })
  }
  
  // Multiplication concept prerequisite chain: 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9 -> 10 -> 11 -> 12 -> 0
  const multiplicationChain = [
    'c_concept_011', // 1
    'c_mul_2s',      // 2
    'c_mul_3s',      // 3
    'c_concept_012', // 4
    'c_concept_013', // 5
    'c_concept_014', // 6
    'c_concept_015', // 7
    'c_concept_016', // 8
    'c_concept_017', // 9
    'c_concept_019', // 10
    'c_concept_020', // 11
    'c_concept_021', // 12
    'c_concept_018', // 0
  ]
  
  for (let i = 0; i < multiplicationChain.length - 1; i++) {
    const sourceConcept = conceptNodeMap.get(multiplicationChain[i])
    const targetConcept = conceptNodeMap.get(multiplicationChain[i + 1])
    
    if (sourceConcept && targetConcept) {
      edges.push({
        id: `${sourceConcept.id}-${targetConcept.id}`,
        source: sourceConcept.id,
        target: targetConcept.id,
        label: '',
        chainId: 'concept-prerequisite',
      })
    }
  }
  
  // Advanced multiplication concept prerequisite chain: 24 -> 25 -> 43
  const advancedMultiplicationChain = [
    'c_concept_024', // Two Digit by Single Digit
    'c_concept_025', // Two Digit by Two Digit
    'c_concept_043', // Three Digit by Two Digit
  ]
  
  for (let i = 0; i < advancedMultiplicationChain.length - 1; i++) {
    const sourceConcept = conceptNodeMap.get(advancedMultiplicationChain[i])
    const targetConcept = conceptNodeMap.get(advancedMultiplicationChain[i + 1])
    
    if (sourceConcept && targetConcept) {
      edges.push({
        id: `${sourceConcept.id}-${targetConcept.id}`,
        source: sourceConcept.id,
        target: targetConcept.id,
        label: '',
        chainId: 'concept-prerequisite',
      })
    }
  }
  
  // Division concept prerequisite chain: 26 -> 27 -> 28 -> 29 -> 30 -> 31 -> 32 -> 33 -> 34 -> 35 -> 36 -> 37 -> 38 -> 39 -> 40 -> 41 -> 42 -> 44 -> 45
  const divisionChain = [
    'c_concept_026', // Division by 1
    'c_concept_027', // Division by 2
    'c_concept_028', // Division by 3
    'c_concept_029', // Division by 4
    'c_concept_030', // Division by 5
    'c_concept_031', // Division by 6
    'c_concept_032', // Division by 7
    'c_concept_033', // Division by 8
    'c_concept_034', // Division by 9
    'c_concept_035', // Division by 10
    'c_concept_036', // Division by 11
    'c_concept_037', // Division by 0
    'c_concept_038', // Division by 10 (Repeated)
    'c_concept_039', // Division with Remainders (Single Digit Divisors)
    'c_concept_040', // Division with Remainders (Two Digit Dividends)
    'c_concept_041', // Division with Fractional Answers (Single Digit Divisors)
    'c_concept_042', // Division with Fractional Answers (Two Digit Dividends)
    'c_concept_044', // Division with Fractional Answers (Three Digit Dividends)
    'c_concept_045', // Division with Decimal Answers (Single Digit Divisors)
  ]
  
  for (let i = 0; i < divisionChain.length - 1; i++) {
    const sourceConcept = conceptNodeMap.get(divisionChain[i])
    const targetConcept = conceptNodeMap.get(divisionChain[i + 1])
    
    if (sourceConcept && targetConcept) {
      edges.push({
        id: `${sourceConcept.id}-${targetConcept.id}`,
        source: sourceConcept.id,
        target: targetConcept.id,
        label: '',
        chainId: 'concept-prerequisite',
      })
    }
  }
  
  return edges
}

/**
 * Enrich achievements with concept-specific variants based on concept requirements.
 * This ensures all required achievement-concept combinations exist in the graph,
 * even if they're locked (not yet earned).
 */
function enrichAchievementsWithConceptVariants(
  achievements: Achievement[],
  concepts: MathConcept[],
  backendRequirements?: Record<string, Array<{
    achievement_code: string
    quantity?: number
    metadata_filter?: Record<string, any>
  }>>
): Achievement[] {
  if (!backendRequirements) {
    return achievements
  }

  const existingAchievementIds = new Set(achievements.map(a => a.id))
  const enrichedAchievements = [...achievements]
  
  // Create a map of achievement code to achievement for lookup
  const achievementByCode = new Map<string, Achievement>()
  for (const achievement of achievements) {
    const { baseCode, tier } = extractTierFromCode(achievement.id)
    
    // Handle concept-specific IDs (e.g., "math-master-bronze-c_add_1s")
    // Extract base code and tier from the base achievement part (before concept_id)
    let effectiveBaseCode = baseCode
    let effectiveTier = tier
    
    // If extraction failed (tier is null or baseCode equals full ID), check if it's a concept-specific ID
    if (!tier || baseCode === achievement.id) {
      // Try to find tier in the middle of the ID (e.g., "math-master-bronze-c_add_1s")
      const tierNames = ['bronze', 'silver', 'gold', 'platinum', 'diamond', 'master', 'grandmaster', 'legendary', 'mythic', 'divine', 'champion']
      for (const tierName of tierNames) {
        const tierIndex = achievement.id.indexOf(`-${tierName}-`)
        if (tierIndex > 0) {
          effectiveBaseCode = achievement.id.substring(0, tierIndex)
          effectiveTier = tierName.charAt(0).toUpperCase() + tierName.slice(1)
          break
        }
      }
    }
    
    // Map both full code (e.g., "math-master-bronze") and base code (e.g., "math-master")
    if (effectiveTier && effectiveBaseCode) {
      const fullCode = `${effectiveBaseCode}-${effectiveTier.toLowerCase()}`
      if (!achievementByCode.has(fullCode)) {
        achievementByCode.set(fullCode, achievement)
      }
      if (!achievementByCode.has(effectiveBaseCode)) {
        achievementByCode.set(effectiveBaseCode, achievement)
      }
    }
    // Also map the full ID as code
    if (!achievementByCode.has(achievement.id)) {
      achievementByCode.set(achievement.id, achievement)
    }
  }

  // For each concept, check its requirements
  // Create separate achievement nodes for each concept that requires them (unique chains)
  for (const concept of concepts) {
    const reqs = backendRequirements[concept.conceptId] || []
    const requiringConceptId = concept.conceptId // The concept that requires this achievement
    
    for (const req of reqs) {
      const achievementCode = req.achievement_code
      const sourceConceptId = req.metadata_filter?.concept_id as string | undefined // The concept the achievement is for (if any)
      
      // Find base achievement by code
      const baseAchievement = achievementByCode.get(achievementCode)
      
      if (!baseAchievement) {
        if (import.meta.env.DEV) {
          console.warn(`⚠️ enrichAchievementsWithConceptVariants: Base achievement not found for code "${achievementCode}" (required by ${requiringConceptId})`, {
            availableCodes: Array.from(achievementByCode.keys()).slice(0, 10),
            totalAchievements: achievements.length,
          })
        }
        continue // Can't create variant without base achievement
      }

      // Create unique ID that includes both the source concept (what the achievement is for, if any)
      // and the requiring concept (what concept needs this achievement)
      // Format: baseCode-tier-sourceConceptId-required-by-requiringConceptId (with concept_id)
      // Format: baseCode-tier-required-by-requiringConceptId (without concept_id)
      const { baseCode, tier } = extractTierFromCode(achievementCode)
      let uniqueId: string
      
      if (sourceConceptId) {
        // Concept-specific achievement
        uniqueId = tier && baseCode
          ? `${baseCode}-${tier.toLowerCase()}-${sourceConceptId}-required-by-${requiringConceptId}`
          : `${achievementCode}-${sourceConceptId}-required-by-${requiringConceptId}`
      } else {
        // Non-concept-specific achievement (like perfect-streak-bronze)
        uniqueId = tier && baseCode
          ? `${baseCode}-${tier.toLowerCase()}-required-by-${requiringConceptId}`
          : `${achievementCode}-required-by-${requiringConceptId}`
      }

      // Skip if already exists
      if (existingAchievementIds.has(uniqueId)) {
        continue
      }
      
      // Check if an achievement exists with matching code and metadata (for status lookup)
      const existingWithMetadata = achievements.find(a => {
        // Check if base code matches
        const { baseCode: aBaseCode, tier: aTier } = extractTierFromCode(a.id)
        const codeMatches = (aTier && aBaseCode ? `${aBaseCode}-${aTier.toLowerCase()}` : a.id) === achievementCode ||
                           a.id === achievementCode
        // If sourceConceptId exists, also check metadata matches
        if (sourceConceptId) {
          return codeMatches && a.metadata?.concept_id === sourceConceptId
        } else {
          // For non-concept-specific achievements, check that they don't have concept_id metadata
          return codeMatches && !a.metadata?.concept_id
        }
      })
      
      // Create variant with unique ID for this requirement chain
      const enrichedAchievement: Achievement = {
        ...baseAchievement,
        id: uniqueId,
        status: existingWithMetadata?.status || 'locked',
        metadata: sourceConceptId ? {
          concept_id: sourceConceptId,
          required_by: requiringConceptId, // Track which concept requires this
        } : {
          required_by: requiringConceptId, // Track which concept requires this
        },
        unlockedAt: existingWithMetadata?.unlockedAt,
        progress: existingWithMetadata?.progress || 0,
        maxProgress: existingWithMetadata?.maxProgress || baseAchievement.maxProgress || 1,
        count: existingWithMetadata?.count || 0,
      }

      enrichedAchievements.push(enrichedAchievement)
      existingAchievementIds.add(uniqueId)
    }
  }

  return enrichedAchievements
}

/**
 * Transform achievements and math concepts into complete force graph data
 * @param achievements - Array of achievements to transform
 * @param concepts - Array of math concepts to transform
 * @param edgeMetadata - Optional metadata for edges (e.g., { "speed-demon-bronze-speed-demon-silver": { quantity: 4 } })
 * @param backendRequirements - Optional backend concept requirements with metadata filters
 */
export function transformAchievementsToForceGraph(
  achievements: Achievement[],
  concepts: MathConcept[] = [],
  edgeMetadata?: Record<string, { quantity?: number; [key: string]: any }>,
  backendRequirements?: Record<string, Array<{
    achievement_code: string
    quantity?: number
    metadata_filter?: Record<string, any>
  }>>
): {
  nodes: ForceGraphNode[]
  edges: ForceGraphEdge[]
} {
  // Enrich achievements with concept-specific variants based on requirements
  const enrichedAchievements = enrichAchievementsWithConceptVariants(
    achievements,
    concepts,
    backendRequirements
  )
  
  // Normalize achievements: transform "math-master-bronze" + metadata.concept_id="c_add_1s"
  // into "math-master-bronze-c_add_1s" to match expected force graph format
  const normalizedAchievements = normalizeAchievementsForGraph(enrichedAchievements)
  
  const achievementNodes = createForceGraphNodes(normalizedAchievements, concepts, backendRequirements)
  const conceptNodes = createForceGraphNodesFromConcepts(concepts)
  const rootCategoryNodes = createRootCategoryNodes()
  const nodes = [...rootCategoryNodes, ...achievementNodes, ...conceptNodes]

  // Create all types of edges
  const achievementChainEdges = createForceGraphEdges(achievementNodes, normalizedAchievements, edgeMetadata)
  const achievementToConceptEdges = createAchievementToConceptEdges(achievementNodes, conceptNodes, normalizedAchievements, backendRequirements)
  const conceptToConceptEdges = createConceptToConceptEdges(conceptNodes)
  const rootCategoryEdges = createRootCategoryEdges(achievementNodes, conceptNodes)

  const edges = [...rootCategoryEdges, ...achievementChainEdges, ...achievementToConceptEdges, ...conceptToConceptEdges]

  return { nodes, edges }
}
