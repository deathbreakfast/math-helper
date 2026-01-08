import React, { useRef, useCallback, useState, useEffect, useMemo } from 'react'
import ForceGraph2D from 'react-force-graph-2d'
import type { ForceGraphNode, ForceGraphEdge } from '../../utils/forceGraphData'
import type { NodePositions } from '../../utils/forceGraphPositions'

type ForceGraphCanvasProps = {
  nodes: ForceGraphNode[]
  edges: ForceGraphEdge[]
  width?: number
  height?: number
  onNodeClick?: (node: ForceGraphNode) => void
  onNodeHover?: (node: ForceGraphNode | null) => void
  initialPositions?: NodePositions
  onPositionsReady?: (positions: NodePositions) => void
  onGetCurrentPositions?: (getter: () => NodePositions) => void
}

export const ForceGraphCanvas: React.FC<ForceGraphCanvasProps> = ({
  nodes,
  edges,
  width = 800,
  height = 600,
  onNodeClick,
  onNodeHover,
  initialPositions,
  onPositionsReady,
  onGetCurrentPositions,
}) => {
  const fgRef = useRef<any>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const [dimensions, setDimensions] = useState(() => ({ width, height }))
  const positionsReadyCalledRef = useRef(false)
  
  // Apply initial positions to nodes
  const nodesWithPositions = useMemo(() => {
    if (!initialPositions || Object.keys(initialPositions).length === 0) {
      return nodes
    }
    
    return nodes.map(node => {
      const position = initialPositions[node.id]
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
  }, [nodes, initialPositions])
  
  // Reset positions ready flag when nodes change
  useEffect(() => {
    positionsReadyCalledRef.current = false
  }, [nodesWithPositions])

  // Make canvas responsive
  useEffect(() => {
    const updateDimensions = () => {
      if (containerRef.current) {
        const containerWidth = containerRef.current.offsetWidth
        setDimensions({
          width: Math.max(containerWidth - 32, 600), // Account for padding
          height: Math.max(window.innerHeight * 0.6, 500),
        })
      }
    }

    updateDimensions()
    window.addEventListener('resize', updateDimensions)
    return () => window.removeEventListener('resize', updateDimensions)
  }, [])

  // Store ref to current nodes for position access
  // The force graph library mutates nodes in place, so we can read from the nodes array
  const nodesRef = useRef<ForceGraphNode[]>(nodesWithPositions)
  
  // Update ref when nodes change
  useEffect(() => {
    nodesRef.current = nodesWithPositions
  }, [nodesWithPositions])
  
  // Expose function to get current positions
  useEffect(() => {
    if (onGetCurrentPositions) {
      const getCurrentPositions = (): NodePositions => {
        const positions: NodePositions = {}
        // Access nodes from ref - the force graph mutates these nodes in place
        // so we can read the current x, y, fx, fy values directly
        const currentNodes = nodesRef.current
        currentNodes.forEach((node) => {
          // Read from the actual node object (mutated by force graph)
          const x = node.fx !== undefined ? node.fx : node.x
          const y = node.fy !== undefined ? node.fy : node.y
          
          if (x !== undefined && y !== undefined && isFinite(x) && isFinite(y)) {
            positions[node.id] = { x, y }
          }
        })
        return positions
      }
      onGetCurrentPositions(getCurrentPositions)
    }
  }, [onGetCurrentPositions])
  
  // Configure force graph forces using d3Force method
  useEffect(() => {
    if (fgRef.current) {
      // Get existing link force and modify it
      const linkForce = fgRef.current.d3Force('link')
      if (linkForce && typeof linkForce.distance === 'function') {
        linkForce.distance(72) // 120px reduced by 40% = 72px
      }
      if (linkForce && typeof linkForce.strength === 'function') {
        linkForce.strength(1.0)
      }
      
      // Get existing charge force and modify it
      const chargeForce = fgRef.current.d3Force('charge')
      if (chargeForce && typeof chargeForce.strength === 'function') {
        chargeForce.strength(-50)
      }
      
      // Get existing center force and modify it
      const centerForce = fgRef.current.d3Force('center')
      if (centerForce && typeof centerForce.strength === 'function') {
        centerForce.strength(0)
      }
      
      // Reheat simulation to apply changes
      fgRef.current.d3ReheatSimulation()
    }
  }, [nodesWithPositions, edges])
  
  // Detect when simulation stabilizes and call onPositionsReady
  useEffect(() => {
    if (!onPositionsReady || positionsReadyCalledRef.current) {
      return
    }
    
    if (!fgRef.current) {
      return
    }
    
    // If we have initial positions, skip simulation and call callback immediately
    if (initialPositions && Object.keys(initialPositions).length > 0) {
      positionsReadyCalledRef.current = true
      onPositionsReady(initialPositions)
      return
    }
    
    // Wait for simulation to complete (cooldownTicks = 300, which is ~5 seconds at 60fps)
    // Use a timeout to wait for simulation to stabilize
    const handleSimulationComplete = () => {
      if (positionsReadyCalledRef.current) {
        return
      }
      
      // Extract current positions from nodes
      // The force graph library mutates nodes in place, so we can read directly from nodesWithPositions
      const positions: NodePositions = {}
      nodesWithPositions.forEach((node) => {
        const x = node.fx !== undefined ? node.fx : node.x
        const y = node.fy !== undefined ? node.fy : node.y
        
        if (x !== undefined && y !== undefined && isFinite(x) && isFinite(y)) {
          positions[node.id] = { x, y }
        }
      })
      
      // Only call if we have valid positions for most nodes
      if (Object.keys(positions).length >= nodesWithPositions.length * 0.8) {
        positionsReadyCalledRef.current = true
        onPositionsReady(positions)
      }
    }
    
    // Wait for cooldown period (300 ticks at ~60fps = ~5 seconds) plus buffer
    const timeoutId = setTimeout(() => {
      if (!positionsReadyCalledRef.current) {
        handleSimulationComplete()
      }
    }, 6000) // Wait 6 seconds to ensure simulation has completed
    
    return () => {
      clearTimeout(timeoutId)
    }
  }, [onPositionsReady, nodesWithPositions, initialPositions])

  // Handle node click
  const handleNodeClick = useCallback((node: any) => {
    if (onNodeClick) {
      onNodeClick(node as ForceGraphNode)
    }
  }, [onNodeClick])

  // Handle node hover
  const handleNodeHover = useCallback((node: any | null) => {
    if (onNodeHover) {
      onNodeHover(node ? (node as ForceGraphNode) : null)
    }
  }, [onNodeHover])

  // Custom node paint function to render icons and styling
  const nodePaint = useCallback((node: any, ctx: CanvasRenderingContext2D, _globalScale: number) => {
    const forceNode = node as ForceGraphNode
    // Root category nodes are largest (27px), math concepts are 18px, achievements are 9px
    const size = forceNode.size || (
      forceNode.type === 'root-category' ? 27 :
      forceNode.type === 'math-concept' ? 18 : 9
    )
    const radius = size / 2

    // Check if node has valid position (might not be positioned yet by force simulation)
    if (typeof node.x !== 'number' || typeof node.y !== 'number' || 
        !isFinite(node.x) || !isFinite(node.y)) {
      return // Skip rendering if node position is invalid
    }

    // Determine colors and gradients based on status and type
    let gradient: CanvasGradient | string = '#e5e7eb' // Default gray for locked
    let borderColor = '#9ca3af'
    let iconOpacity = 1.0
    let textOpacity = 1.0
    let borderWidth = 1
    
    // Root category nodes have special styling
    if (forceNode.type === 'root-category') {
      // Root category nodes: purple/indigo gradient with thicker border
      const gradientObj = ctx.createRadialGradient(
        node.x - radius * 0.3,
        node.y - radius * 0.3,
        0,
        node.x,
        node.y,
        radius
      )
      gradientObj.addColorStop(0, '#e0e7ff') // indigo-100 (lighter)
      gradientObj.addColorStop(1, '#c7d2fe') // indigo-200 (darker)
      gradient = gradientObj
      borderColor = '#6366f1' // indigo-500
      iconOpacity = 1.0
      textOpacity = 1.0
      borderWidth = 3 // Thicker border for root nodes
    } else if (forceNode.type === 'math-concept') {
      // Math concepts: locked = grey/desaturated, unlocked = green stroke
      if (forceNode.status === 'locked') {
        // Locked math concepts: grey/desaturated, no green stroke
        gradient = '#e5e7eb' // gray-200
        borderColor = '#9ca3af' // gray-400
        iconOpacity = 0.4
        textOpacity = 0.5
        borderWidth = 2
      } else {
        // Unlocked math concepts: full color with green stroke
        const gradientObj = ctx.createRadialGradient(
          node.x - radius * 0.3,
          node.y - radius * 0.3,
          0,
          node.x,
          node.y,
          radius
        )
        gradientObj.addColorStop(0, '#c7d2fe') // blue-200 (lighter)
        gradientObj.addColorStop(1, '#a5b4fc') // blue-300 (darker)
        gradient = gradientObj
        borderColor = '#86efac' // green-300 (green stroke for unlocked)
        iconOpacity = 1.0
        textOpacity = 1.0
        borderWidth = 2
      }
    } else {
      // Achievement nodes
      const hasMetadata = forceNode.relatedConceptLocked !== undefined
      
      if (forceNode.status === 'unlocked') {
        // Awarded: full color with green stroke
        const gradientObj = ctx.createRadialGradient(
          node.x - radius * 0.3,
          node.y - radius * 0.3,
          0,
          node.x,
          node.y,
          radius
        )
        
        if (forceNode.tier === 'Bronze') {
          gradientObj.addColorStop(0, '#f59e0b') // amber-500 (lighter)
          gradientObj.addColorStop(1, '#d97706') // amber-600 (darker)
        } else if (forceNode.tier === 'Silver') {
          gradientObj.addColorStop(0, '#d1d5db') // gray-300 (lighter)
          gradientObj.addColorStop(1, '#9ca3af') // gray-400 (darker)
        } else if (forceNode.tier === 'Gold') {
          gradientObj.addColorStop(0, '#fde047') // yellow-300 (lighter)
          gradientObj.addColorStop(1, '#fbbf24') // yellow-400 (darker)
        } else {
          // Default gradient for other tiers
          gradientObj.addColorStop(0, '#e5e7eb') // gray-200
          gradientObj.addColorStop(1, '#d1d5db') // gray-300
        }
        gradient = gradientObj
        borderColor = '#86efac' // green-300 (green stroke for awarded)
        iconOpacity = 1.0
        textOpacity = 1.0
        borderWidth = 1.5
      } else if (forceNode.status === 'locked') {
        // Locked achievement
        if (hasMetadata) {
          // Achievement with metadata (concept requirement)
          if (forceNode.relatedConceptLocked === false) {
            // Discovered: concept unlocked but achievement not earned - grey stroke, saturated icon
            const gradientObj = ctx.createRadialGradient(
              node.x - radius * 0.3,
              node.y - radius * 0.3,
              0,
              node.x,
              node.y,
              radius
            )
            
            if (forceNode.tier === 'Bronze') {
              gradientObj.addColorStop(0, '#f59e0b') // amber-500 (lighter)
              gradientObj.addColorStop(1, '#d97706') // amber-600 (darker)
            } else if (forceNode.tier === 'Silver') {
              gradientObj.addColorStop(0, '#d1d5db') // gray-300 (lighter)
              gradientObj.addColorStop(1, '#9ca3af') // gray-400 (darker)
            } else if (forceNode.tier === 'Gold') {
              gradientObj.addColorStop(0, '#fde047') // yellow-300 (lighter)
              gradientObj.addColorStop(1, '#fbbf24') // yellow-400 (darker)
            } else {
              gradientObj.addColorStop(0, '#e5e7eb')
              gradientObj.addColorStop(1, '#d1d5db')
            }
            gradient = gradientObj
            borderColor = '#9ca3af' // grey stroke
            iconOpacity = 1.0 // Saturated
            textOpacity = 1.0
            borderWidth = 1
          } else {
            // Undiscovered: concept locked - grey stroke, desaturated/no icon
            gradient = '#e5e7eb' // gray-200
            borderColor = '#9ca3af' // gray-400 (grey stroke)
            iconOpacity = 0.2 // Very desaturated
            textOpacity = 0.4
            borderWidth = 1
          }
        } else {
          // Achievement without metadata: discovered state (grey stroke, no green)
          const gradientObj = ctx.createRadialGradient(
            node.x - radius * 0.3,
            node.y - radius * 0.3,
            0,
            node.x,
            node.y,
            radius
          )
          
          if (forceNode.tier === 'Bronze') {
            gradientObj.addColorStop(0, '#f59e0b') // amber-500 (lighter)
            gradientObj.addColorStop(1, '#d97706') // amber-600 (darker)
          } else if (forceNode.tier === 'Silver') {
            gradientObj.addColorStop(0, '#d1d5db') // gray-300 (lighter)
            gradientObj.addColorStop(1, '#9ca3af') // gray-400 (darker)
          } else if (forceNode.tier === 'Gold') {
            gradientObj.addColorStop(0, '#fde047') // yellow-300 (lighter)
            gradientObj.addColorStop(1, '#fbbf24') // yellow-400 (darker)
          } else {
            gradientObj.addColorStop(0, '#e5e7eb')
            gradientObj.addColorStop(1, '#d1d5db')
          }
          gradient = gradientObj
          borderColor = '#9ca3af' // grey stroke (not green)
          iconOpacity = 1.0
          textOpacity = 1.0
          borderWidth = 1
        }
      }
    }

    // Draw node circle with gradient
    ctx.beginPath()
    ctx.arc(node.x, node.y, radius, 0, 2 * Math.PI, false)
    ctx.fillStyle = gradient
    ctx.fill()
    ctx.strokeStyle = borderColor
    ctx.lineWidth = borderWidth
    ctx.stroke()

    // Draw icon (emoji) in center with opacity
    // For undiscovered achievements (with metadata and locked concept), don't show icon
    const shouldShowIcon = !(
      forceNode.type === 'achievement' &&
      forceNode.relatedConceptLocked === true &&
      forceNode.status === 'locked'
    )
    
    if (forceNode.icon && shouldShowIcon) {
      ctx.save()
      ctx.globalAlpha = iconOpacity
      ctx.font = `${size * 0.8}px Arial` // Slightly larger relative to node size
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      ctx.fillText(forceNode.icon, node.x, node.y)
      ctx.restore()
    }

    // Draw title below node with ellipsis for overflow and opacity
    if (forceNode.title) {
      ctx.save()
      ctx.globalAlpha = textOpacity
      ctx.font = '6px Arial' // Match edge text size
      ctx.textAlign = 'center'
      ctx.textBaseline = 'top'
      ctx.fillStyle = '#374151' // gray-700
      
      // Truncate text if too long (proportionally smaller max width)
      const maxWidth = 50
      let displayText = forceNode.title
      const metrics = ctx.measureText(displayText)
      if (metrics.width > maxWidth) {
        // Find the longest substring that fits
        while (ctx.measureText(displayText + '...').width > maxWidth && displayText.length > 0) {
          displayText = displayText.slice(0, -1)
        }
        displayText = displayText + '...'
      }
      
      ctx.fillText(displayText, node.x, node.y + radius + 3) // Less spacing below node
      ctx.restore()
    }
  }, [])

  // Custom link paint function to render edge labels
  const linkPaint = useCallback((link: any, ctx: CanvasRenderingContext2D, _globalScale: number) => {
    const forceEdge = link as ForceGraphEdge
    const source = link.source as ForceGraphNode
    const target = link.target as ForceGraphNode

    // Check if nodes have valid positions
    if (typeof source.x !== 'number' || typeof source.y !== 'number' ||
        typeof target.x !== 'number' || typeof target.y !== 'number' ||
        !isFinite(source.x) || !isFinite(source.y) ||
        !isFinite(target.x) || !isFinite(target.y)) {
      return // Skip rendering if node positions are invalid
    }

    // Determine edge color based on node states
    let edgeColor = 'rgba(156, 163, 175, 0.6)' // Default gray
    
    // Edge between math concepts: green if both unlocked, grey otherwise
    if (source.type === 'math-concept' && target.type === 'math-concept') {
      if (source.status === 'unlocked' && target.status === 'unlocked') {
        edgeColor = 'rgba(34, 197, 94, 0.6)' // green-500
      } else {
        edgeColor = 'rgba(156, 163, 175, 0.6)' // grey
      }
    }
    // Edge from achievement to math concept: green if achievement is awarded, grey otherwise
    else if (source.type === 'achievement' && target.type === 'math-concept') {
      if (source.status === 'unlocked') {
        edgeColor = 'rgba(34, 197, 94, 0.6)' // green-500
      } else {
        edgeColor = 'rgba(156, 163, 175, 0.6)' // grey
      }
    }
    // Achievement chain edges (achievement to achievement): keep default grey for now
    // (could be styled based on tier if needed, but user didn't specify)

    // Draw line with arrow
    ctx.beginPath()
    ctx.moveTo(source.x, source.y)
    ctx.lineTo(target.x, target.y)
    ctx.strokeStyle = edgeColor
    ctx.lineWidth = 2.5
    ctx.stroke()

    // Draw arrowhead
    const angle = Math.atan2(target.y - source.y, target.x - source.x)
    const arrowLength = 8
    const arrowX = target.x - Math.cos(angle) * (target.size || 9) / 2
    const arrowY = target.y - Math.sin(angle) * (target.size || 9) / 2

    ctx.beginPath()
    ctx.moveTo(arrowX, arrowY)
    ctx.lineTo(
      arrowX - arrowLength * Math.cos(angle - Math.PI / 6),
      arrowY - arrowLength * Math.sin(angle - Math.PI / 6)
    )
    ctx.lineTo(
      arrowX - arrowLength * Math.cos(angle + Math.PI / 6),
      arrowY - arrowLength * Math.sin(angle + Math.PI / 6)
    )
    ctx.closePath()
    ctx.fillStyle = edgeColor
    ctx.fill()

    // Draw label at midpoint
    if (forceEdge.label) {
      const midX = (source.x + target.x) / 2
      const midY = (source.y + target.y) / 2

      ctx.save()
      ctx.font = '6px Arial' // Even smaller font for edge labels
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      
      // Draw background for label
      const textMetrics = ctx.measureText(forceEdge.label)
      const textWidth = textMetrics.width
      const textHeight = 8 // Proportionally smaller
      const padding = 3 // Proportionally smaller
      
      // Draw rounded rectangle background (using manual path for compatibility)
      const x = midX - textWidth / 2 - padding
      const y = midY - textHeight / 2 - padding
      const w = textWidth + padding * 2
      const h = textHeight + padding * 2
      const r = 2 // Smaller corner radius for smaller text
      
      ctx.beginPath()
      ctx.moveTo(x + r, y)
      ctx.lineTo(x + w - r, y)
      ctx.quadraticCurveTo(x + w, y, x + w, y + r)
      ctx.lineTo(x + w, y + h - r)
      ctx.quadraticCurveTo(x + w, y + h, x + w - r, y + h)
      ctx.lineTo(x + r, y + h)
      ctx.quadraticCurveTo(x, y + h, x, y + h - r)
      ctx.lineTo(x, y + r)
      ctx.quadraticCurveTo(x, y, x + r, y)
      ctx.closePath()
      
      ctx.fillStyle = 'rgba(255, 255, 255, 0.95)'
      ctx.fill()
      ctx.strokeStyle = 'rgba(156, 163, 175, 0.3)'
      ctx.lineWidth = 1
      ctx.stroke()
      
      // Draw text with color based on labelColor prop
      const labelTextColor = forceEdge.labelColor === 'green' 
        ? '#22c55e' // green-500
        : '#374151' // gray-700 (default)
      ctx.fillStyle = labelTextColor
      ctx.font = '6px Arial' // Even smaller font to match smaller nodes
      ctx.fillText(forceEdge.label, midX, midY)
      ctx.restore()
    }
  }, [])

  return (
    <div 
      ref={containerRef}
      className="w-full rounded-xl border-2 border-gray-200 bg-gradient-to-br from-gray-50 to-white shadow-lg overflow-hidden"
    >
      <ForceGraph2D
        ref={fgRef}
        graphData={{ nodes: nodesWithPositions, links: edges }}
        width={dimensions.width}
        height={dimensions.height}
        nodeRelSize={4}
        nodeVal={(node: any) => (node as ForceGraphNode).size || 9}
        cooldownTicks={initialPositions && Object.keys(initialPositions).length > 0 ? 0 : 300}
        onNodeClick={handleNodeClick}
        onNodeHover={handleNodeHover}
        nodeLabel={(node: any) => {
          const forceNode = node as ForceGraphNode
          return forceNode.title
        }}
        nodeCanvasObject={nodePaint}
        linkCanvasObject={linkPaint}
        backgroundColor="rgba(0,0,0,0)"
        enablePanInteraction={true}
        enableZoomInteraction={true}
        enableNodeDrag={true}
        onNodeDragEnd={(node: any) => {
          // When node is dragged, release fixed position to allow it to stay where dragged
          if (node.fx !== undefined) node.fx = undefined
          if (node.fy !== undefined) node.fy = undefined
        }}
      />
    </div>
  )
}
