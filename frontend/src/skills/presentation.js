export function useStaticCue(motionMode, prefersReducedMotion) {
  return prefersReducedMotion || motionMode === 'static'
}

// Optional entry points never interrupt pacing or displace a chosen conversation.
export function canOfferConversation(page, status, simpler) {
  return !simpler && page === 'exercise' && ['ready', 'completed', 'stopped'].includes(status)
}
