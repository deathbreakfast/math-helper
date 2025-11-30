type MathTypeDisplayProps = {
  mode: string
  operation?: string
}

const getMathTypeLabel = (mode: string, operation?: string): string => {
  if (mode === 'multiplication') {
    return 'Multiplication Practice'
  }
  if (mode === 'division') {
    return 'Division Practice'
  }
  if (operation) {
    return `${operation.charAt(0).toUpperCase() + operation.slice(1)} Practice`
  }
  return 'Math Practice'
}

export const MathTypeDisplay = ({ mode, operation }: MathTypeDisplayProps) => {
  const label = getMathTypeLabel(mode, operation)
  
  return (
    <div className="mb-6 text-center">
      <div className="inline-block rounded-full bg-gradient-to-r from-blue-500 to-purple-600 px-6 py-2 text-sm font-semibold text-white shadow-md">
        {label}
      </div>
    </div>
  )
}

