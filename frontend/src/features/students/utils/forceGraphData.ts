/**
 * Utilities for transforming achievements into force graph data structures
 */

import type { Achievement } from '../data/achievements'
import { extractTierFromCode, TIER_ORDER } from './achievementUtils'

export type ForceGraphNode = {
  id: string                    // Achievement ID (e.g., "speed-demon-bronze")
  achievementId: string         // Same as id, for clarity
  title: string                 // Achievement title
  icon: string                  // Achievement icon emoji/character
  tier: string                  // bronze, silver, gold (capitalized)
  status: 'locked' | 'unlocked' | 'in-progress'
  chainId: string               // Grouping ID (e.g., "speed-demon")
  isRoot: boolean               // true for bronze tier (root nodes)
  size: number                  // Node size (smaller for achievements)
  type: 'achievement' | 'math-concept'  // Node type identifier
  x?: number                    // Force graph x position
  y?: number                    // Force graph y position
  vx?: number                   // Velocity x
  vy?: number                   // Velocity y
}

export type ForceGraphEdge = {
  id: string                    // Unique edge ID
  source: string | ForceGraphNode  // Source node ID
  target: string | ForceGraphNode  // Target node ID
  label: string                 // Text to display on edge
  chainId: string               // Which achievement chain this belongs to
  labelColor?: string           // Optional color for edge label text (e.g., 'green')
}

/**
 * Filter achievements to only Speed Demon (bronze, silver, gold) for initial build
 */
function filterSpeedDemonAchievements(achievements: Achievement[]): Achievement[] {
  return achievements.filter(achievement => {
    const { baseCode, tier } = extractTierFromCode(achievement.id)
    // Only include speed-demon achievements with bronze, silver, or gold tiers
    return baseCode === 'speed-demon' && 
           tier !== null && 
           ['Bronze', 'Silver', 'Gold'].includes(tier)
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
    
    return {
      id: achievement.id,
      achievementId: achievement.id,
      title: achievement.title,
      icon: achievement.icon,
      tier: tier || 'Unknown',
      status: achievement.status,
      chainId: baseCode,
      isRoot: tier === 'Bronze',
      size: 35, // Smaller than math concepts (30-40px as specified)
      type: 'achievement' as const,
      // x, y, vx, vy will be set by force graph simulation
    }
  })
}

/**
 * Create edges between consecutive tiers in achievement chains
 */
export function createForceGraphEdges(nodes: ForceGraphNode[]): ForceGraphEdge[] {
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
      
      // Create label showing tier progression
      const label = `${source.tier} → ${target.tier}`
      
      edges.push({
        id: `${source.id}-${target.id}`,
        source: source.id,
        target: target.id,
        label,
        chainId,
      })
    }
  })
  
  return edges
}

/**
 * Transform achievements into complete force graph data
 */
export function transformAchievementsToForceGraph(achievements: Achievement[]): {
  nodes: ForceGraphNode[]
  edges: ForceGraphEdge[]
} {
  const nodes = createForceGraphNodes(achievements)
  const edges = createForceGraphEdges(nodes)
  
  return { nodes, edges }
}
