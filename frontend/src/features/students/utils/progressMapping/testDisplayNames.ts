/**
 * Get test display name from test_type
 */
export function getTestDisplayName(testType: string): string {
  // Map common test types to display names
  const testTypeMap: Record<string, string> = {
    'addition-1digit': '1 Digit Addition',
    'addition-1digit-zeros': '1 Digit Addition w/ Zeros',
    'addition-2digit': '2 Digit Addition',
    'addition-3digit': '3 Digit Addition',
    'subtraction-1digit': '1 Digit Subtraction',
    'subtraction-1digit-zeros': '1 Digit Subtraction w/ Zeros',
    'subtraction-2digit': '2 Digit Subtraction',
    'subtraction-3digit': '3 Digit Subtraction',
    'multiplication-by-1': 'Multiplication by 1',
    'multiplication-by-2': 'Multiplication by 2',
    'multiplication-by-3': 'Multiplication by 3',
    'multiplication-by-4': 'Multiplication by 4',
    'multiplication-by-5': 'Multiplication by 5',
    'multiplication-by-6': 'Multiplication by 6',
    'multiplication-by-7': 'Multiplication by 7',
    'multiplication-by-8': 'Multiplication by 8',
    'multiplication-by-9': 'Multiplication by 9',
    'multiplication-by-10': 'Multiplication by 10',
    'multiplication-by-11': 'Multiplication by 11',
    'multiplication-by-12': 'Multiplication by 12',
    'division-by-1': 'Division by 1',
    'division-by-2': 'Division by 2',
    'division-by-3': 'Division by 3',
    'division-by-4': 'Division by 4',
    'division-by-5': 'Division by 5',
    'division-by-6': 'Division by 6',
    'division-by-7': 'Division by 7',
    'division-by-8': 'Division by 8',
    'division-by-9': 'Division by 9',
    'division-by-10': 'Division by 10',
    'division-by-11': 'Division by 11',
    'division-by-12': 'Division by 12',
  }
  
  return testTypeMap[testType] || testType.replace(/-/g, ' ')
}





