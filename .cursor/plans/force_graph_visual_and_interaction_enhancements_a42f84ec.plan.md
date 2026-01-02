---
name: Force Graph Visual and Interaction Enhancements
overview: Enhance the force graph with improved visual styling (grayed out locked nodes, green outline for unlocked nodes) and update the click handler to console.log with node type and id. Add support for green edge label text via props.
todos:
  - id: update-node-type
    content: Add 'type' field to ForceGraphNode data structure
    status: completed
  - id: update-edge-color
    content: Add optional labelColor prop to ForceGraphEdge
    status: completed
  - id: update-node-styling
    content: Update nodePaint to gray out locked nodes and add green outline for unlocked
    status: completed
  - id: update-edge-styling
    content: Update linkPaint to support green label text color
    status: completed
  - id: update-click-handler
    content: Replace modal with console.log handler that includes type and id
    status: completed
---

# Force Graph Visual and Interaction Enhancements

## Overview
Enhance the force graph visualization with proper status-based styling (grayed out locked nodes, green outline for unlocked) and update the click handler API to support node type and id logging. Add edge label color customization.

## Changes Required

### 1. Update Node Data Structure

**File: `frontend/src/features/students/utils/forceGraphData.ts`**

Add `type` field to `ForceGraphNode`:
```typescript
export type ForceGraphNode = {
  // ... existing fields
  type: 'achievement' | 'math-concept'  // NEW: Node type identifier
}
```

Update `createForceGraphNodes` to set `type: 'achievement'` for all nodes (math concepts will be added later).

### 2. Update Edge Data Structure

**File: `frontend/src/features/students/utils/forceGraphData.ts`**

Add optional `labelColor` field to `ForceGraphEdge`:
```typescript
export type ForceGraphEdge = {
  // ... existing fields
  labelColor?: string  // NEW: Optional color for edge label text (e.g., 'green')
}
```

### 3. Update Node Styling (Locked vs Unlocked)

**File: `frontend/src/features/students/components/journey/ForceGraphCanvas.tsx`**

In `nodePaint` callback:
- **Locked nodes**: Apply gray styling with reduced opacity
  - Use gray fill: `#e5e7eb` (gray-200)
  - Use gray border: `#9ca3af` (gray-400)
  - Reduce icon opacity to 0.3-0.4
  - Reduce title text opacity
  
- **Unlocked nodes**: Add green outline/border
  - Keep existing gradient fills based on tier
  - Change border color to green: `#22c55e` (green-500) or `#86efac` (green-300) to match MathConceptCard styling
  - Border width: 2.5-3px for visibility
  - Full opacity for icon and text

- **In-progress nodes**: Keep existing blue styling (no green border)

### 4. Update Edge Label Color Support

**File: `frontend/src/features/students/components/journey/ForceGraphCanvas.tsx`**

In `linkPaint` callback:
- Check for `forceEdge.labelColor` prop
- If set to 'green', use green text color: `#22c55e` (green-500) or `#16a34a` (green-600)
- Default to gray text: `#374151` (gray-700) if not specified

### 5. Update Click Handler

**File: `frontend/src/features/students/components/journey/ForceGraphTab.tsx`**

Replace the modal-opening click handler with console.log:
```typescript
const handleNodeClick = useCallback((node: ForceGraphNode) => {
  console.log('Node clicked:', {
    type: node.type,  // 'achievement' or 'math-concept'
    id: node.id       // Node ID
  })
}, [])
```

Remove the AchievementDetailModal integration (keep the component but don't use it for now).

### 6. Update ForceGraphCanvas Props

**File: `frontend/src/features/students/components/journey/ForceGraphCanvas.tsx`**

The `onNodeClick` prop signature should remain the same, but the implementation in ForceGraphTab will change to use the new node structure with `type` field.

## Visual Design Details

### Locked Node Styling
- Fill: `#e5e7eb` (gray-200)
- Border: `#9ca3af` (gray-400), 2.5px width
- Icon opacity: 0.3
- Title text opacity: 0.5
- Overall appearance: Muted, grayed out

### Unlocked Node Styling
- Fill: Existing tier-based gradients (Bronze amber, Silver gray, Gold yellow)
- Border: `#86efac` (green-300) or `#22c55e` (green-500), 3px width for visibility
- Icon: Full opacity
- Title text: Full opacity, `#374151` (gray-700)
- Overall appearance: Vibrant with green outline matching MathConceptCard

### Edge Label Colors
- Default: `#374151` (gray-700)
- Green (when `labelColor: 'green'`): `#22c55e` (green-500)

## Implementation Notes

1. The green border for unlocked nodes should be clearly visible but not overpowering
2. Locked nodes should be visually distinct but still recognizable
3. The console.log format should be clear and structured for future backend integration
4. Edge label color prop is optional to maintain backward compatibility

## Testing Considerations

- Verify locked nodes appear grayed out
- Verify unlocked nodes have green outline
- Verify click handler logs correct type and id
- Verify edge labels can be colored green when prop is set
- Verify in-progress nodes maintain blue styling without green border