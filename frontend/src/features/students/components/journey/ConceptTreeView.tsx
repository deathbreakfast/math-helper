import React, { useMemo, useRef } from 'react'
import { motion } from 'framer-motion'
import type { MathConcept } from '../../data/mathConcepts'
import type { Achievement } from '../../data/achievements'
import type { UserProgressData } from '../../utils/progressMapping'
import {
  buildConceptGraph,
  groupNodesByLevel,
  calculateHorizontalPositions,
  calculateVerticalPositions,
  type GraphNode,
  type GraphEdge,
} from '../../utils/conceptGraph'
import { MathConceptCard } from './MathConceptCard'
import type { BackendConceptRequirement } from '../../../lib/concepts/api'
import { useRouter } from '../../../../utils/routing'
import { extractTierFromCode, cleanTitle } from '../../utils/achievementUtils'

type ConceptTreeViewProps = {
  concepts: MathConcept[]
  userData: UserProgressData
  backendRequirements?: Record<string, BackendConceptRequirement[]>
  onConceptClick: (concept: MathConcept) => void
  onStartPractice?: (concept: MathConcept) => void
}

export const ConceptTreeView: React.FC<ConceptTreeViewProps> = ({
  concepts,
  userData,
  backendRequirements,
  onConceptClick,
  onStartPractice,
}) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const router = useRouter()

  // DEBUG: Filter to only show specific concepts for debugging
  const debugConcepts = useMemo(() => {
    return concepts.filter(c => 
      c.conceptId === 'c_concept_001' || c.conceptId === 'c_concept_003' || c.conceptId === 'c_concept_005' || c.conceptId === 'c_concept_006' || c.conceptId === 'c_concept_007' || c.conceptId === 'c_concept_008' || c.conceptId === 'c_concept_010' || c.conceptId === 'c_concept_011' || c.conceptId === 'c_concept_022' || c.conceptId === 'c_concept_023' || c.conceptId === 'c_add_0s' || c.conceptId === 'c_add_1s' || c.conceptId === 'c_add_2s' || c.conceptId === 'c_add_3s' || c.conceptId === 'c_add_4s' || c.conceptId === 'c_add_5s' || c.conceptId === 'c_add_6s' || c.conceptId === 'c_add_7s' || c.conceptId === 'c_add_8s' || c.conceptId === 'c_add_9s' || c.conceptId === 'c_add_10s' || c.conceptId === 'c_sub_0s' || c.conceptId === 'c_sub_1s' || c.conceptId === 'c_sub_2s' || c.conceptId === 'c_sub_3s' || c.conceptId === 'c_sub_4s' || c.conceptId === 'c_sub_5s' || c.conceptId === 'c_sub_6s' || c.conceptId === 'c_sub_7s' || c.conceptId === 'c_sub_8s' || c.conceptId === 'c_sub_9s' || c.conceptId === 'c_sub_10s' || c.conceptId === 'c_mul_2s' || c.conceptId === 'c_mul_3s'
    )
  }, [concepts])

  // Build the graph
  const graph = useMemo(() => {
    return buildConceptGraph(debugConcepts, userData.achievements || [], backendRequirements)
  }, [debugConcepts, userData.achievements, backendRequirements])

  // Group nodes by level and calculate positions in a grid
  const nodesByLevel = useMemo(() => {
    const grouped = groupNodesByLevel(graph.nodes)
    // Use grid layout: calculate positions in a grid
    const sortedLevels = Array.from(grouped.keys()).sort((a, b) => a - b)
    const gridSpacingX = 300 // Horizontal spacing between cards
    const gridSpacingY = 350 // Vertical spacing between levels
    
    sortedLevels.forEach((level, levelIndex) => {
      const nodesAtLevel = grouped.get(level) || []
      // Filter to only include concepts and achievements without concept_id metadata
      const renderableNodes = nodesAtLevel.filter(node => {
        if (node.type === 'concept') return true
        if (node.type === 'achievement') {
          // Check if achievement has concept_id metadata
          // Parse unique achievement node ID to get achievement code
          const parts = node.id.split(':')
          const achievementCode = parts.length >= 4 ? parts[1] : node.id
          
          for (const concept of debugConcepts) {
            if (backendRequirements && backendRequirements[concept.conceptId]) {
              const backendReqs = backendRequirements[concept.conceptId]
              const matchingReq = backendReqs.find(req => req.achievement_code === achievementCode)
              if (matchingReq?.metadata_filter?.concept_id) {
                return false // Don't render achievements with concept_id metadata
              }
            }
          }
          return true
        }
        return false
      })
      
      // Sort nodes within level: concepts first, then achievements next to their parent concepts
      const sortedNodes = [...renderableNodes].sort((a, b) => {
        // Concepts come first
        if (a.type === 'concept' && b.type === 'achievement') return -1
        if (a.type === 'achievement' && b.type === 'concept') return 1
        
        // Both are concepts: sort by ID
        if (a.type === 'concept' && b.type === 'concept') {
          return a.id.localeCompare(b.id)
        }
        
        // Both are achievements: position next to their parent concept
        if (a.type === 'achievement' && b.type === 'achievement') {
          // Find parent concepts for each achievement
          const aParent = a.dependents.length > 0 ? graph.nodes.get(a.dependents[0]) : null
          const bParent = b.dependents.length > 0 ? graph.nodes.get(b.dependents[0]) : null
          
          if (aParent && aParent.type === 'concept') {
            const aParentConceptId = aParent.dependencies.find(depId => {
              const depNode = graph.nodes.get(depId)
              return depNode && depNode.type === 'concept'
            })
            if (aParentConceptId) {
              const aParentConcept = renderableNodes.find(n => n.id === aParentConceptId)
              if (aParentConcept) {
                // Position this achievement after its parent concept
                const aParentIndex = renderableNodes.indexOf(aParentConcept)
                // We'll handle positioning in the next step
              }
            }
          }
          
          // Default: sort by ID
          return a.id.localeCompare(b.id)
        }
        
        return 0
      })
      
      // Position nodes: concepts first, then achievements after their parent concepts
      let currentIndex = 0
      const positionedNodes: GraphNode[] = []
      const nodePositions = new Map<string, number>()
      
      // First, position all concept nodes
      const conceptNodes = sortedNodes.filter(n => n.type === 'concept')
      conceptNodes.forEach((node) => {
        nodePositions.set(node.id, currentIndex)
        positionedNodes.push(node)
        currentIndex++
      })
      
      // Then, position achievement nodes next to their parent concepts
      const achievementNodes = sortedNodes.filter(n => n.type === 'achievement')
      achievementNodes.forEach((achievement) => {
        // Find the parent concept for this achievement
        if (achievement.dependents.length > 0) {
          const unlockedConcept = graph.nodes.get(achievement.dependents[0])
          if (unlockedConcept && unlockedConcept.type === 'concept') {
            // Find the parent concept (concept that the unlocked concept depends on)
            const parentConceptId = unlockedConcept.dependencies.find(depId => {
              const depNode = graph.nodes.get(depId)
              return depNode && depNode.type === 'concept'
            })
            
            if (parentConceptId && nodePositions.has(parentConceptId)) {
              // Position achievement right after its parent concept
              const parentIndex = nodePositions.get(parentConceptId)!
              // Insert after parent
              const insertIndex = parentIndex + 1
              // Shift all subsequent nodes
              for (const [nodeId, pos] of nodePositions.entries()) {
                if (pos >= insertIndex) {
                  nodePositions.set(nodeId, pos + 1)
                }
              }
              nodePositions.set(achievement.id, insertIndex)
              positionedNodes.splice(insertIndex, 0, achievement)
              currentIndex++
              return
            }
          }
        }
        
        // No parent concept found, append to end
        nodePositions.set(achievement.id, currentIndex)
        positionedNodes.push(achievement)
        currentIndex++
      })
      
      // Center nodes horizontally within each level
      const totalWidth = positionedNodes.length * gridSpacingX
      const startX = -totalWidth / 2 + gridSpacingX / 2
      
      positionedNodes.forEach((node, index) => {
        node.x = startX + index * gridSpacingX
        node.y = levelIndex * gridSpacingY
      })
    })
    
    return grouped
  }, [graph.nodes, debugConcepts, backendRequirements])

  // Calculate container dimensions and bounds
  const containerWidth = 1200 // Fixed width for consistency

  // Get concept nodes and achievement nodes (only achievements without concept_id metadata)
  const conceptNodes = useMemo(() => {
    const sorted: GraphNode[] = []
    const sortedLevels = Array.from(nodesByLevel.keys()).sort((a, b) => a - b)
    
    for (const level of sortedLevels) {
      const nodesAtLevel = nodesByLevel.get(level) || []
      // Include concept nodes
      sorted.push(...nodesAtLevel.filter(node => node.type === 'concept'))
      
      // Include achievement nodes that don't have concept_id metadata
      const achievementNodes = nodesAtLevel.filter(node => {
        if (node.type !== 'achievement') return false
        
        // Parse unique achievement node ID to get achievement code
        const parts = node.id.split(':')
        const achievementCode = parts.length >= 4 ? parts[1] : node.id
        
        // Check all concepts to see if this achievement has concept_id metadata
        for (const concept of debugConcepts) {
          if (backendRequirements && backendRequirements[concept.conceptId]) {
            const backendReqs = backendRequirements[concept.conceptId]
            const matchingReq = backendReqs.find(req => req.achievement_code === achievementCode)
            if (matchingReq?.metadata_filter?.concept_id) {
              // This achievement has concept_id metadata, don't render it
              return false
            }
          }
        }
        return true
      })
      sorted.push(...achievementNodes)
    }
    
    // DEBUG: Log nodes
    console.log('Nodes to render:', sorted.length, sorted.map(n => ({
      id: n.id,
      type: n.type,
      level: n.level,
      pos: { x: n.x, y: n.y },
    })))
    
    return sorted
  }, [nodesByLevel, debugConcepts, backendRequirements])

  const containerHeight = useMemo(() => {
    if (conceptNodes.length === 0) return 600
    const maxLevel = Math.max(...conceptNodes.map(n => n.level), 0)
    return (maxLevel + 1) * 350 + 200 // level height * number of levels + padding
  }, [conceptNodes])

  // Calculate SVG viewBox - use adjusted coordinates for all rendered nodes
  const svgBounds = useMemo(() => {
    if (conceptNodes.length === 0) {
      return { x: 0, y: 0, width: containerWidth, height: containerHeight }
    }

    let minX = Infinity
    let maxX = -Infinity
    let minY = Infinity
    let maxY = -Infinity

    for (const node of conceptNodes) {
      const adjustedX = node.x + containerWidth / 2
      const adjustedY = node.y + 100
      // Cards are 203x203, so half is 101.5
      const nodeHalfSize = 101.5
      minX = Math.min(minX, adjustedX - nodeHalfSize)
      maxX = Math.max(maxX, adjustedX + nodeHalfSize)
      minY = Math.min(minY, adjustedY - nodeHalfSize)
      maxY = Math.max(maxY, adjustedY + nodeHalfSize)
    }

    // Add padding
    const padding = 50
    return {
      x: minX - padding,
      y: minY - padding,
      width: maxX - minX + padding * 2,
      height: maxY - minY + padding * 2,
    }
  }, [conceptNodes, containerWidth, containerHeight])

  // Render achievement node
  const renderAchievementNode = (node: GraphNode, index: number) => {
    const achievement = node.data as Achievement

    // Parse unique achievement node ID: conceptId:achievementCode:tier:quantity:conceptIdInMetadata
    // Format: ${concept.conceptId}:${achievementCode}:${tier}:${quantity}:${conceptIdInMetadata}
    const parts = node.id.split(':')
    let achievementCode = node.id
    let tier: string | null = null
    let quantity: number | undefined = undefined
    
    if (parts.length >= 4) {
      // New format with unique ID
      achievementCode = parts[1] // achievementCode is second part
      tier = parts[2] !== 'none' ? parts[2] : null
      quantity = parseInt(parts[3], 10) || undefined
    } else {
      // Fallback: extract from achievement code
      const { tier: extractedTier } = extractTierFromCode(node.id)
      tier = extractedTier
      
      // Try to find quantity from backend requirements
      if (backendRequirements) {
        for (const [conceptId, reqs] of Object.entries(backendRequirements)) {
          const matchingReq = reqs.find(req => req.achievement_code === node.id)
          if (matchingReq?.quantity) {
            quantity = matchingReq.quantity
            break
          }
        }
      }
    }
    
    const requirementInfo: { tier?: string; quantity?: number } = {
      tier: tier || undefined,
      quantity: quantity && quantity > 1 ? quantity : undefined,
    }

    // Adjust position relative to container center
    const adjustedX = node.x + containerWidth / 2
    const adjustedY = node.y + 100 // Add top padding

    const handleClick = () => {
      // Navigate to achievements tab with text filter to show this achievement
      // Use the achievement code (not the unique node ID)
      const userId = userData?.id ? String(userData.id) : undefined
      if (userId) {
        router.navigate(`/journey/${userId}/achievements?text=${encodeURIComponent(achievementCode)}`)
      }
    }

    return (
      <motion.div
        key={node.id}
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: index * 0.05 }}
        className="absolute"
        style={{
          left: `${adjustedX}px`,
          top: `${adjustedY}px`,
          transform: 'translate(-50%, -50%)',
        }}
      >
        <motion.div
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="cursor-pointer rounded-2xl border-2 border-yellow-300 bg-gradient-to-br from-yellow-50 to-amber-50 p-4 shadow-md transition-all hover:shadow-lg flex flex-col items-center justify-center"
          style={{ width: '203px', height: '203px' }}
          onClick={handleClick}
        >
          <div className="text-center text-4xl mb-2">{achievement.icon}</div>
          <div className="text-sm font-semibold text-gray-900 text-center mb-1">
            {achievement.title}
          </div>
          {requirementInfo && (
            <div className="text-xs text-gray-600 text-center">
              {requirementInfo.tier && (
                <span className="font-semibold">{requirementInfo.tier}</span>
              )}
              {requirementInfo.tier && requirementInfo.quantity && ' • '}
              {requirementInfo.quantity && (
                <span>Qty: {requirementInfo.quantity}</span>
              )}
            </div>
          )}
        </motion.div>
      </motion.div>
    )
  }

  // Render concept node
  const renderConceptNode = (node: GraphNode, index: number) => {
    const concept = node.data as MathConcept

    // Get all dependencies for debug display
    // Format: Achievement Name (Tier) with concept requirement underneath
    type DebugDependency = {
      achievementName: string
      tier: string | null
      conceptRequirement: string | null
    }
    
    const debugDependencies: DebugDependency[] = []
    
    for (const depId of node.dependencies) {
      const depNode = graph.nodes.get(depId)
      // Only show achievement dependencies - concepts should only appear as metadata under achievements
      if (depNode?.type === 'achievement') {
        // Parse unique achievement node ID: conceptId:achievementCode:tier:quantity:conceptIdInMetadata
        const parts = depId.split(':')
        const achievementCode = parts.length >= 4 ? parts[1] : depId
        const tier = parts.length >= 4 && parts[2] !== 'none' ? parts[2] : null
        
        const achievement = depNode.data as Achievement
        // Use clean title without tier suffix
        const rawTitle = achievement.title || achievementCode.replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
        const achievementName = cleanTitle(rawTitle, tier)
        
        // Get concept requirement from metadata
        let conceptRequirement: string | null = null
        
        // Check if the unique ID includes concept_id in metadata (5th part)
        if (parts.length >= 5 && parts[4] !== 'none') {
          const conceptId = parts[4]
          const depConcept = debugConcepts.find(c => c.conceptId === conceptId)
          if (depConcept) {
            conceptRequirement = depConcept.displayName
          }
        } else if (backendRequirements && backendRequirements[concept.conceptId]) {
          // Fallback: check backend requirements if concept_id not in unique ID
          const backendReqs = backendRequirements[concept.conceptId]
          const matchingReq = backendReqs.find(req => req.achievement_code === achievementCode)
          if (matchingReq?.metadata_filter?.concept_id) {
            const conceptId = matchingReq.metadata_filter.concept_id
            const depConcept = debugConcepts.find(c => c.conceptId === conceptId)
            if (depConcept) {
              conceptRequirement = depConcept.displayName
            }
          }
        }
        
        // Add all achievements (with or without concept requirement)
        debugDependencies.push({
          achievementName,
          tier,
          conceptRequirement,
        })
      }
      // Skip direct concept dependencies - they should only appear as metadata under achievements
    }

    // Adjust position relative to container center
    const adjustedX = node.x + containerWidth / 2
    const adjustedY = node.y + 100 // Add top padding

    return (
      <motion.div
        key={node.id}
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ delay: index * 0.05 }}
        className="absolute"
        style={{
          left: `${adjustedX}px`,
          top: `${adjustedY}px`,
          transform: 'translate(-50%, -50%)',
        }}
      >
        <MathConceptCard
          concept={concept}
          index={index}
          onClick={onConceptClick}
          onStartPractice={onStartPractice}
          matchesFilter={true}
          debugDependencies={debugDependencies}
        />
      </motion.div>
    )
  }

  // Render SVG edge with straight lines and 90-degree turns
  const renderEdge = (edge: GraphEdge) => {
    const fromNode = graph.nodes.get(edge.from)
    const toNode = graph.nodes.get(edge.to)

    if (!fromNode || !toNode || toNode.type !== 'concept') return null

    // Check if fromNode is an achievement with concept_id metadata - if so, don't render edge
    // (the concept-to-concept edge will be rendered instead)
    if (fromNode.type === 'achievement' && backendRequirements && toNode.type === 'concept') {
      const concept = toNode.data as MathConcept
      if (backendRequirements[concept.conceptId]) {
        const backendReqs = backendRequirements[concept.conceptId]
        // Parse unique achievement node ID to get achievement code
        const parts = fromNode.id.split(':')
        const achievementCode = parts.length >= 4 ? parts[1] : fromNode.id
        const matchingReq = backendReqs.find(req => req.achievement_code === achievementCode)
        if (matchingReq?.metadata_filter?.concept_id) {
          // This achievement has concept_id metadata, don't render this edge
          return null
        }
      }
    }

    // Get node center positions (adjusted for container)
    const fromX = fromNode.x + containerWidth / 2
    const fromY = fromNode.y + 100
    const toX = toNode.x + containerWidth / 2
    const toY = toNode.y + 100

    // Card sizes - cards are 203x203, so half is 101.5
    const cardHalfSize = 101.5

    // Determine if line is going down (fromNode above toNode) or horizontal/up
    const isGoingDown = fromY < toY

    // Calculate connection points on card edges
    // Always connect to top center of target concept
    // Adjust for coordinate offset: add cardHalfSize to compensate
    const endX = toX + cardHalfSize // Top center X (adjusted)
    const endY = toY // Top center Y (adjusted: toY - cardHalfSize + cardHalfSize = toY)

    let startX: number
    let startY: number
    let path: string
    const offset = 20 // Small offset to make the turn visible

    if (isGoingDown) {
      // Line going down: start from bottom center of source
      // Cards use translate(-50%, -50%) so center is at (fromX, fromY)
      // Bottom center = center + half card height
      startX = fromX + cardHalfSize // Shift right to center (from left edge)
      startY = fromY + cardHalfSize + cardHalfSize // Shift down to bottom (from center)
      // Path: bottom center -> down -> horizontal -> to top center of target
      const midY = startY + offset // Go down a bit from source
      path = `M ${startX} ${startY} L ${startX} ${midY} L ${endX} ${midY} L ${endX} ${endY}`
    } else {
      // Line going horizontal/up: start from right center of source
      startX = fromX + cardHalfSize + cardHalfSize // Right center of source card
      startY = fromY + cardHalfSize // Center Y
      // Path: right center -> right -> vertical -> to top center of target
      const midX = startX + offset // Go right a bit from source
      path = `M ${startX} ${startY} L ${midX} ${startY} L ${midX} ${endY} L ${endX} ${endY}`
    }

    return (
      <path
        key={`${edge.from}-${edge.to}`}
        d={path}
        fill="none"
        stroke={edge.requirement.completed ? '#10b981' : '#9ca3af'}
        strokeWidth={edge.requirement.completed ? 2 : 1}
        strokeDasharray={edge.requirement.completed ? '0' : '5,5'}
        opacity={edge.requirement.completed ? 1 : 0.5}
      />
    )
  }

  // Filter edges - show all edges to concepts, but filter out achievement edges with concept_id metadata
  const visibleEdges = useMemo(() => {
    const filtered = graph.edges.filter(edge => {
      const fromNode = graph.nodes.get(edge.from)
      const toNode = graph.nodes.get(edge.to)
      
      // Must have both nodes and target must be a concept
      if (!fromNode || !toNode || toNode.type !== 'concept') return false
      
      // If fromNode is an achievement, check if it has concept_id metadata
      if (fromNode.type === 'achievement' && backendRequirements) {
        const concept = toNode.data as MathConcept
        if (backendRequirements[concept.conceptId]) {
          const backendReqs = backendRequirements[concept.conceptId]
          // Parse unique achievement node ID to get achievement code
          const parts = fromNode.id.split(':')
          const achievementCode = parts.length >= 4 ? parts[1] : fromNode.id
          const matchingReq = backendReqs.find(req => req.achievement_code === achievementCode)
          if (matchingReq?.metadata_filter?.concept_id) {
            // This achievement has concept_id metadata, don't show this edge
            return false
          }
        }
      }
      
      return true
    })
    
    // DEBUG: Log edges
    console.log('Visible edges:', filtered.length, filtered.map(e => ({
      from: e.from,
      to: e.to,
      fromNode: graph.nodes.get(e.from)?.type,
      toNode: graph.nodes.get(e.to)?.type,
    })))
    
    return filtered
  }, [graph.edges, graph.nodes, backendRequirements])

  return (
    <div
      ref={containerRef}
      className="relative w-full overflow-auto bg-gray-50 rounded-xl p-8"
      style={{ minHeight: '600px' }}
      data-testid="testid-concept-tree"
    >
      <div className="relative mx-auto" style={{ width: `${containerWidth}px`, height: `${containerHeight}px` }}>
        <svg
          className="absolute inset-0 pointer-events-none"
          viewBox={`0 0 ${containerWidth} ${containerHeight}`}
          style={{ width: `${containerWidth}px`, height: `${containerHeight}px` }}
        >
          {/* Render edges */}
          {visibleEdges.map((edge) => renderEdge(edge))}
        </svg>

        {/* Render nodes - concepts and achievements (without concept_id metadata) */}
        <div className="relative" style={{ width: `${containerWidth}px`, height: `${containerHeight}px` }}>
          {conceptNodes.map((node, index) => {
            if (node.type === 'achievement') {
              return renderAchievementNode(node, index)
            } else {
              return renderConceptNode(node, index)
            }
          })}
        </div>
      </div>
    </div>
  )
}

