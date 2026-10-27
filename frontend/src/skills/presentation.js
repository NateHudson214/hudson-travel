export function useStaticCue(motionMode, prefersReducedMotion) {
  return prefersReducedMotion || motionMode === 'static'
}
