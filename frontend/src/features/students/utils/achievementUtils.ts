export const getTierColor = (tier: string): string => {
  const colors: Record<string, string> = {
    B: 'from-blue-400 to-blue-500',
    A: 'from-green-400 to-green-600',
    S: 'from-yellow-400 to-yellow-600',
    SS: 'from-orange-400 to-orange-600',
    SSS: 'from-purple-500 to-pink-600',
    Starter: 'from-gray-400 to-gray-500',
    Bronze: 'from-amber-600 to-amber-700',
    Silver: 'from-gray-400 to-gray-500',
    Gold: 'from-yellow-400 to-yellow-600',
    Platinum: 'from-cyan-400 to-blue-500',
    Diamond: 'from-blue-500 to-purple-600',
  }
  return colors[tier] || 'from-gray-400 to-gray-500'
}

