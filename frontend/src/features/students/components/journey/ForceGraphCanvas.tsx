import React, { useRef, useCallback, useState, useEffect } from 'react'
import ForceGraph2D from 'react-force-graph-2d'
import type { ForceGraphNode, ForceGraphEdge } from '../../utils/forceGraphData'
import { getTierColor } from '../../utils/achievementUtils'

type ForceGraphCanvasProps = {
  nodes: ForceGraphNode[]
  edges: ForceGraphEdge[]
  width?: number
  height?: number
  onNodeClick?: (node: ForceGraphNode) => void
  onNodeHover?: (node: ForceGraphNode | null) => void
}

export const ForceGraphCanvas: React.FC<ForceGraphCanvasProps> = ({
  nodes,
  edges,
  width = 800,
  height = 600,
  onNodeClick,
  onNodeHover,
}) => {
  const fgRef = useRef<any>()
  const containerRef = useRef<HTMLDivElement>(null)
  const [dimensions, setDimensions] = useState(() => ({ width, height }))

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
  }, [nodes, edges])

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
  const nodePaint = useCallback((node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
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
      // Math concepts have different styling
      if (forceNode.status === 'locked') {
        // Locked math concepts: grayed out
        gradient = '#e5e7eb' // gray-200
        borderColor = '#9ca3af' // gray-400
        iconOpacity = 0.3
        textOpacity = 0.5
        borderWidth = 2
      } else {
        // Unlocked math concepts: blue/purple gradient with green outline
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
        borderColor = '#86efac' // green-300 to match MathConceptCard
        iconOpacity = 1.0
        textOpacity = 1.0
        borderWidth = 2 // Thicker border for math concept nodes
      }
    } else {
      // Achievement nodes
      if (forceNode.status === 'locked') {
        // Locked nodes: grayed out
        gradient = '#e5e7eb' // gray-200
        borderColor = '#9ca3af' // gray-400
        iconOpacity = 0.3
        textOpacity = 0.5
        borderWidth = 1
      } else if (forceNode.status === 'unlocked') {
        // Unlocked nodes: full color with green outline
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
        }
        gradient = gradientObj
        borderColor = '#86efac' // green-300 to match MathConceptCard
        iconOpacity = 1.0
        textOpacity = 1.0
        borderWidth = 1.5 // Proportionally smaller
      } else if (forceNode.status === 'in-progress') {
        // In-progress nodes: blue styling (no green border)
        const gradientObj = ctx.createRadialGradient(
          node.x - radius * 0.3,
          node.y - radius * 0.3,
          0,
          node.x,
          node.y,
          radius
        )
        gradientObj.addColorStop(0, '#bfdbfe') // blue-200 (lighter)
        gradientObj.addColorStop(1, '#93c5fd') // blue-300 (darker)
        borderColor = '#60a5fa' // blue-400
        gradient = gradientObj
        iconOpacity = 1.0
        textOpacity = 1.0
        borderWidth = 1
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
    if (forceNode.icon) {
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
  const linkPaint = useCallback((link: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
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

    // Determine edge color based on target tier (the higher tier)
    let edgeColor = 'rgba(156, 163, 175, 0.6)' // Default gray
    if (target.tier === 'Gold') {
      edgeColor = 'rgba(251, 191, 36, 0.6)' // yellow-400
    } else if (target.tier === 'Silver') {
      edgeColor = 'rgba(156, 163, 175, 0.6)' // gray-400
    } else if (target.tier === 'Bronze') {
      edgeColor = 'rgba(217, 119, 6, 0.6)' // amber-600
    }

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
    const arrowWidth = 5
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
        graphData={{ nodes, links: edges }}
        width={dimensions.width}
        height={dimensions.height}
        nodeRelSize={4}
        nodeVal={(node: any) => (node as ForceGraphNode).size || 9}
        cooldownTicks={300}
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
      />
    </div>
  )
}
