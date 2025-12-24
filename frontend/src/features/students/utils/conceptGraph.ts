/**
 * Utilities for building and analyzing concept dependency graphs
 */

import type { MathConcept, MathConceptUnlockRequirement } from '../data/mathConcepts'
import type { Achievement } from '../data/achievements'
import { extractTierFromCode } from './achievementUtils'

export type GraphNode = {
  id: string
  type: 'concept' | 'achievement'
  data: MathConcept | Achievement
  level: number // Hierarchical depth (0 = no dependencies)
  dependencies: string[] // IDs of nodes this depends on
  dependents: string[] // IDs of nodes that depend on this
  x: number // Horizontal position (calculated during layout)
  y: number // Vertical position (calculated during layout)
}

export type GraphEdge = {
  from: string // Source node ID
  to: string // Target node ID
  requirement: MathConceptUnlockRequirement
}

export type ConceptGraph = {
  nodes: Map<string, GraphNode>
  edges: GraphEdge[]
}

/**
 * Extract concept dependencies from unlock requirements
 * Looks for metadata_filter.concept_id in requirements
 */
function extractConceptDependencies(requirements: MathConceptUnlockRequirement[]): string[] {
  const conceptIds: string[] = []
  
  for (const req of requirements) {
    // Check if requirement has concept_id in metadata
    // This is typically stored in the description or we need to parse it
    // For now, we'll look for concept IDs in the description or check if there's a way to get metadata
    // The backend requirements have metadata_filter.concept_id, but frontend requirements may not expose this directly
    // We'll need to parse the description or check if there's metadata available
  }
  
  return conceptIds
}

/**
 * Extract achievement dependencies from unlock requirements
 */
function extractAchievementDependencies(requirements: MathConceptUnlockRequirement[]): string[] {
  const achievementCodes: string[] = []
  
  for (const req of requirements) {
    if (req.achievementCode) {
      achievementCodes.push(req.achievementCode)
    }
    if (req.achievementIds && req.achievementIds.length > 0) {
      achievementCodes.push(...req.achievementIds)
    }
  }
  
  return [...new Set(achievementCodes)] // Remove duplicates
}

/**
 * Parse concept ID from requirement description
 * Requirements like "Complete: Level Master (Bronze) (Single Digit Addition (1s))" 
 * contain concept names in parentheses
 */
function parseConceptIdFromDescription(
  description: string,
  allConcepts: MathConcept[]
): string | null {
  // Try to find concept name in description
  // The description format is typically: "Complete: Achievement Name (Concept Name)"
  // We need to match the concept name that appears in parentheses
  
  // First, try exact match with display name
  for (const concept of allConcepts) {
    if (description.includes(`(${concept.displayName})`)) {
      return concept.conceptId
    }
  }
  
  // Fallback: try partial match (concept name might be truncated)
  for (const concept of allConcepts) {
    // Check if description contains a significant portion of the concept name
    const words = concept.displayName.toLowerCase().split(' ')
    if (words.length > 0 && words.every(word => word.length > 2 && description.toLowerCase().includes(word))) {
      return concept.conceptId
    }
  }
  
  return null
}

/**
 * Build a dependency graph from concepts and achievements
 * Optionally accepts raw backend requirements to extract concept_id from metadata_filter
 */
export function buildConceptGraph(
  concepts: MathConcept[],
  achievements: Achievement[] = [],
  backendRequirements?: Record<string, Array<{
    achievement_code: string
    quantity?: number
    metadata_filter?: Record<string, any>
  }>>
): ConceptGraph {
  const nodes = new Map<string, GraphNode>()
  const edges: GraphEdge[] = []
  
  // Create concept nodes
  for (const concept of concepts) {
    nodes.set(concept.conceptId, {
      id: concept.conceptId,
      type: 'concept',
      data: concept,
      level: -1, // Will be calculated
      dependencies: [],
      dependents: [],
      x: 0,
      y: 0,
    })
  }
  
  // Create achievement nodes (only for achievements that are referenced)
  const referencedAchievements = new Set<string>()
  
  // Process each concept's requirements to build edges
  for (const concept of concepts) {
    const conceptNode = nodes.get(concept.conceptId)!
    
    for (const requirement of concept.unlockRequirements) {
      // Extract achievement dependencies
      if (requirement.achievementCode) {
        // Get tier and quantity from backend requirements or requirement
        let tier: string | null = null
        let quantity: number | undefined = requirement.maxProgress && requirement.maxProgress > 1 ? requirement.maxProgress : undefined
        
        // Extract tier from achievement code
        const { tier: extractedTier } = extractTierFromCode(requirement.achievementCode)
        tier = extractedTier
        
        // Get quantity from backend requirements if available
        if (backendRequirements && backendRequirements[concept.conceptId]) {
          const backendReqs = backendRequirements[concept.conceptId]
          const matchingBackendReq = backendReqs.find(
            br => br.achievement_code === requirement.achievementCode
          )
          if (matchingBackendReq?.quantity) {
            quantity = matchingBackendReq.quantity
          }
        }
        
        // Create unique achievement node ID: concept:achievementCode:tier:quantity:conceptId
        // Include concept_id from metadata_filter to distinguish requirements with same achievement code
        // This ensures each requirement gets its own achievement node
        let conceptIdInMetadata: string | undefined = undefined
        if (backendRequirements && backendRequirements[concept.conceptId]) {
          const backendReqs = backendRequirements[concept.conceptId]
          const matchingBackendReq = backendReqs.find(
            br => br.achievement_code === requirement.achievementCode
          )
          conceptIdInMetadata = matchingBackendReq?.metadata_filter?.concept_id
        }
        const achievementNodeId = `${concept.conceptId}:${requirement.achievementCode}:${tier || 'none'}:${quantity || 1}:${conceptIdInMetadata || 'none'}`
        referencedAchievements.add(achievementNodeId)
        
        // Find or create achievement node with unique ID
        if (!nodes.has(achievementNodeId)) {
          const achievement = achievements.find(a => a.id === requirement.achievementCode)
          if (achievement) {
            // Clone achievement data and update with requirement-specific info
            nodes.set(achievementNodeId, {
              id: achievementNodeId,
              type: 'achievement',
              data: {
                ...achievement,
                // Store original achievement code for reference
                id: achievementNodeId,
              },
              level: -1,
              dependencies: [],
              dependents: [],
              x: 0,
              y: 0,
            })
          } else {
            // Create placeholder achievement node if not found
            nodes.set(achievementNodeId, {
              id: achievementNodeId,
              type: 'achievement',
              data: {
                id: achievementNodeId,
                title: requirement.achievementCode.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
                description: requirement.description || '',
                icon: '🏆',
                type: 'milestone',
                tier: tier || 'bronze',
                requirement: requirement.description || '',
                status: 'locked',
                isHidden: false,
                category: 'progression',
              } as Achievement,
              level: -1,
              dependencies: [],
              dependents: [],
              x: 0,
              y: 0,
            })
          }
        }
        
        // Create edge from achievement to concept
        const achievementNode = nodes.get(achievementNodeId)!
        if (!conceptNode.dependencies.includes(achievementNodeId)) {
          conceptNode.dependencies.push(achievementNodeId)
        }
        if (!achievementNode.dependents.includes(concept.conceptId)) {
          achievementNode.dependents.push(concept.conceptId)
        }
        
        edges.push({
          from: achievementNodeId,
          to: concept.conceptId,
          requirement,
        })
      }
      
      // Extract concept dependencies
      // First try to get from backend requirements metadata_filter.concept_id (most accurate)
      let conceptId: string | null = null
      if (backendRequirements && backendRequirements[concept.conceptId]) {
        const backendReqs = backendRequirements[concept.conceptId]
        const matchingBackendReq = backendReqs.find(
          br => br.achievement_code === requirement.achievementCode
        )
        if (matchingBackendReq?.metadata_filter?.concept_id) {
          conceptId = matchingBackendReq.metadata_filter.concept_id
        }
      }
      
      // Fallback: parse from description if not found in backend requirements
      if (!conceptId) {
        conceptId = parseConceptIdFromDescription(requirement.description, concepts)
      }
      
      if (conceptId && conceptId !== concept.conceptId) {
        const depConceptNode = nodes.get(conceptId)
        if (depConceptNode) {
          // Only add if not already present
          if (!conceptNode.dependencies.includes(conceptId)) {
            conceptNode.dependencies.push(conceptId)
          }
          if (!depConceptNode.dependents.includes(concept.conceptId)) {
            depConceptNode.dependents.push(concept.conceptId)
          }
          
          // Check if edge already exists
          const edgeExists = edges.some(e => e.from === conceptId && e.to === concept.conceptId)
          if (!edgeExists) {
            edges.push({
              from: conceptId,
              to: concept.conceptId,
              requirement,
            })
          }
        }
      }
    }
  }
  
  // Calculate hierarchical levels using BFS
  calculateLevels(nodes)
  
  return { nodes, edges }
}

/**
 * Calculate hierarchical levels for all nodes using BFS
 * Nodes with no dependencies are level 0
 * Achievement nodes are assigned the same level as the concept they unlock
 */
function calculateLevels(nodes: Map<string, GraphNode>): void {
  // Reset all levels
  for (const node of nodes.values()) {
    node.level = -1
  }
  
  // Find all nodes with no dependencies (level 0)
  // For achievement nodes, we'll assign their level later based on the concept they unlock
  const queue: string[] = []
  for (const [id, node] of nodes.entries()) {
    // Only start with concept nodes that have no dependencies
    // Achievement nodes will get their level from the concept they unlock
    if (node.dependencies.length === 0 && node.type === 'concept') {
      node.level = 0
      queue.push(id)
    }
  }
  
  // BFS to assign levels to concept nodes
  while (queue.length > 0) {
    const currentId = queue.shift()!
    const currentNode = nodes.get(currentId)!
    
    // Update all dependents (concepts that depend on this node)
    for (const dependentId of currentNode.dependents) {
      const dependentNode = nodes.get(dependentId)!
      // Only process concept nodes in BFS
      if (dependentNode.type === 'concept') {
        if (dependentNode.level === -1 || dependentNode.level <= currentNode.level) {
          dependentNode.level = currentNode.level + 1
          queue.push(dependentId)
        }
      }
    }
  }
  
  // Now assign levels to achievement nodes: they should be at the same level as the parent concept
  // (the concept that the unlocked concept depends on), or at the same level as the unlocked concept if no parent
  for (const node of nodes.values()) {
    if (node.type === 'achievement' && node.level === -1) {
      // Find the concept(s) this achievement unlocks
      if (node.dependents.length > 0) {
        const unlockedConcept = nodes.get(node.dependents[0])
        if (unlockedConcept && unlockedConcept.type === 'concept' && unlockedConcept.level >= 0) {
          // Find the parent concept (concept that the unlocked concept depends on)
          // Look for concept dependencies of the unlocked concept
          const parentConceptId = unlockedConcept.dependencies.find(depId => {
            const depNode = nodes.get(depId)
            return depNode && depNode.type === 'concept'
          })
          
          if (parentConceptId) {
            const parentConcept = nodes.get(parentConceptId)
            if (parentConcept && parentConcept.level >= 0) {
              // Achievement should be at the same level as the parent concept
              node.level = parentConcept.level
            } else {
              // No parent concept, use the unlocked concept's level (but one level before)
              node.level = Math.max(0, unlockedConcept.level - 1)
            }
          } else {
            // No parent concept, achievement should be at level 0 (or same as unlocked concept if it's level 0)
            node.level = unlockedConcept.level > 0 ? unlockedConcept.level - 1 : 0
          }
        } else {
          node.level = 0 // Fallback
        }
      } else {
        node.level = 0 // No dependents, default to level 0
      }
    }
  }
  
  // Handle any remaining nodes (shouldn't happen in acyclic graph, but handle gracefully)
  for (const node of nodes.values()) {
    if (node.level === -1) {
      node.level = 0 // Default to level 0 if not reachable
    }
  }
}

/**
 * Group nodes by level for hierarchical layout
 */
export function groupNodesByLevel(nodes: Map<string, GraphNode>): Map<number, GraphNode[]> {
  const byLevel = new Map<number, GraphNode[]>()
  
  for (const node of nodes.values()) {
    const level = node.level
    if (!byLevel.has(level)) {
      byLevel.set(level, [])
    }
    byLevel.get(level)!.push(node)
  }
  
  // Sort each level's nodes
  for (const nodesAtLevel of byLevel.values()) {
    nodesAtLevel.sort((a, b) => {
      // Sort concepts before achievements
      if (a.type !== b.type) {
        return a.type === 'concept' ? -1 : 1
      }
      // Then sort by ID for consistency
      return a.id.localeCompare(b.id)
    })
  }
  
  return byLevel
}

/**
 * Calculate horizontal positions for nodes within each level
 * Uses simple even distribution
 */
export function calculateHorizontalPositions(
  nodesByLevel: Map<number, GraphNode[]>,
  nodeWidth: number = 250,
  horizontalSpacing: number = 50
): void {
  for (const [level, nodes] of nodesByLevel.entries()) {
    const totalWidth = nodes.length * nodeWidth + (nodes.length - 1) * horizontalSpacing
    const startX = -totalWidth / 2
    
    nodes.forEach((node, index) => {
      node.x = startX + index * (nodeWidth + horizontalSpacing) + nodeWidth / 2
    })
  }
}

/**
 * Calculate vertical positions for nodes
 */
export function calculateVerticalPositions(
  nodesByLevel: Map<number, GraphNode[]>,
  levelHeight: number = 350
): void {
  const sortedLevels = Array.from(nodesByLevel.keys()).sort((a, b) => a - b)
  
  for (const level of sortedLevels) {
    const nodes = nodesByLevel.get(level)!
    const y = level * levelHeight
    
    for (const node of nodes) {
      node.y = y
    }
  }
}

