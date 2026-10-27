// Application-owned timing. No model response or network request enters this module.
export const BREATHING_SKILL = Object.freeze({
  id: 'paced_breathing_4_6',
  version: '1',
  inhaleMs: 4000,
  exhaleMs: 6000,
  cycles: 6,
  plannedMs: 60000,
})

// Provisional software interruption threshold; real browser timing is still to be measured.
export const MAX_CUE_DELAY_MS = 250

export function createBreathingSession({ now = () => performance.now() } = {}) {
  const createdAt = now()
  if (!Number.isFinite(createdAt)) throw new RangeError('Clock must be finite.')
  let lastAt = createdAt
  let status = 'ready'
  let phase = 'inhale'
  let remainingMs = BREATHING_SKILL.inhaleMs
  let cyclesCompleted = 0
  let activeMs = 0
  let pauseMs = 0
  let supportMs = 0
  let setupMs = null
  let pauseReason = null
  let supportOpen = false

  function snapshot() {
    return Object.freeze({
      skillId: BREATHING_SKILL.id,
      skillVersion: BREATHING_SKILL.version,
      status,
      phase,
      phaseRemainingMs: Math.round(remainingMs),
      cycle: Math.min(cyclesCompleted + 1, BREATHING_SKILL.cycles),
      cyclesCompleted,
      activeMs: Math.round(activeMs),
      pauseMs: Math.round(pauseMs),
      supportMs: Math.round(supportMs),
      setupMs: setupMs === null ? null : Math.round(setupMs),
      pauseReason,
      supportOpen,
      withinDurationLimit: status === 'completed' && activeMs <= 90000,
    })
  }

  function sample() {
    const at = now()
    if (!Number.isFinite(at) || at < lastAt) {
      throw new RangeError('Clock must be finite and monotonic.')
    }
    const delta = at - lastAt
    lastAt = at
    if (status === 'paused') {
      if (supportOpen) supportMs += delta
      else pauseMs += delta
    } else if (status === 'running') {
      activeMs += delta
      if (delta > remainingMs + MAX_CUE_DELAY_MS) {
        // Retain the last presented phase instead of silently skipping cues.
        status = 'paused'
        pauseReason = 'timing'
      } else if (delta >= remainingMs) {
        const overshoot = delta - remainingMs
        if (phase === 'exhale') cyclesCompleted += 1
        if (cyclesCompleted === BREATHING_SKILL.cycles) {
          status = 'completed'
          remainingMs = 0
        } else {
          phase = phase === 'inhale' ? 'exhale' : 'inhale'
          remainingMs =
            (phase === 'inhale' ? BREATHING_SKILL.inhaleMs : BREATHING_SKILL.exhaleMs) - overshoot
        }
      } else {
        remainingMs -= delta
      }
    }
    return at
  }

  function tick() {
    sample()
    return snapshot()
  }

  function start() {
    const at = sample()
    if (status === 'ready' && !supportOpen) {
      setupMs = at - createdAt
      status = 'running'
    }
    return snapshot()
  }

  function pause(reason = 'user') {
    if (!['user', 'hidden'].includes(reason)) throw new TypeError('Invalid pause reason.')
    sample()
    if (status === 'running') {
      status = 'paused'
      pauseReason = reason
    }
    return snapshot()
  }

  function openSupport() {
    sample()
    supportOpen = true
    if (status === 'running') {
      status = 'paused'
      pauseReason = 'support'
    }
    return snapshot()
  }

  function closeSupport() {
    sample()
    supportOpen = false
    // Closing the panel deliberately leaves an active exercise paused.
    return snapshot()
  }

  function resume() {
    sample()
    if (status === 'paused' && !supportOpen) {
      status = 'running'
      pauseReason = null
    }
    return snapshot()
  }

  function stop() {
    const wasActive = ['ready', 'running', 'paused'].includes(status)
    sample()
    if (wasActive) {
      status = 'stopped'
      pauseReason = null
    }
    return snapshot()
  }

  return Object.freeze({ snapshot, tick, start, pause, resume, stop, openSupport, closeSupport })
}
