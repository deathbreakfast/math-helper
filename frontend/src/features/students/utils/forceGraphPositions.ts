/**
 * Utilities for loading and applying cached node positions for the force graph
 */

import type { ForceGraphNode } from './forceGraphData'

export type NodePositions = Record<string, { x: number; y: number }>

// Import JSON file - Vite handles this natively
// The file exists (created as empty object {}), so this import should work
import forceGraphPositionsData from '../data/forceGraphPositions.json'

/**
 * Load cached positions from the JSON file
 * Returns empty object if file doesn't exist or is invalid
 */
export function loadCachedPositions(): NodePositions {
  try {
    return (forceGraphPositionsData || {}) as NodePositions
  } catch {
    // Fallback to empty object if import fails
    return {}
  }
}

/**
 * Apply cached positions to nodes
 * Uses fx/fy (fixed positions) to prevent simulation from moving nodes,
 * but still allows manual dragging
 */
export function applyPositionsToNodes(
  nodes: ForceGraphNode[],
  positions: NodePositions
): ForceGraphNode[] {
  return nodes.map(node => {
    const position = positions[node.id]
    if (position) {
      return {
        ...node,
        fx: position.x, // Fixed x position (prevents simulation movement)
        fy: position.y, // Fixed y position (prevents simulation movement)
        x: position.x,  // Initial x position
        y: position.y,  // Initial y position
      }
    }
    return node
  })
}

/**
 * Export positions from nodes to JSON format
 */
export function exportPositionsFromNodes(nodes: ForceGraphNode[]): NodePositions {
  const positions: NodePositions = {}
  nodes.forEach(node => {
    // Use fx/fy if available (fixed positions), otherwise use x/y
    const x = node.fx !== undefined ? node.fx : node.x
    const y = node.fy !== undefined ? node.fy : node.y
    
    if (x !== undefined && y !== undefined && isFinite(x) && isFinite(y)) {
      positions[node.id] = { x, y }
    }
  })
  return positions
}

/**
 * Download positions as JSON file
 */
export function downloadPositionsAsJson(positions: NodePositions, filename: string = 'forceGraphPositions.json'): void {
  const json = JSON.stringify(positions, null, 2)
  const blob = new Blob([json], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}
