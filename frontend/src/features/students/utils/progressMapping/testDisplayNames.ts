/**
 * Legacy helper for rendering test_type metadata in requirement descriptions.
 *
 * The app no longer exposes a Tests feature, but some legacy unlock requirements may
 * still include metadata_filter.test_type. We keep this formatter to avoid breaking
 * UI descriptions while those configs are migrated to concept/stage metadata.
 */
export function getTestDisplayName(testType: string): string {
  if (!testType) return ''
  return testType.replace(/-/g, ' ')
}
