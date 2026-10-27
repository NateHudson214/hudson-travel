<script setup>
import { computed, nextTick, onActivated, onBeforeUnmount, onDeactivated, ref, watch } from 'vue'
import { createBreathingSession } from '../../skills/breathing.js'
import { createSessionJournal } from '../../skills/sessionJournal.js'
import { useStaticCue } from '../../skills/presentation.js'
import CrisisSupportPanel from './CrisisSupportPanel.vue'
import SkillsHistory from './SkillsHistory.vue'
import SkillsConversation from './SkillsConversation.vue'
import SkillsConversationHistory from './SkillsConversationHistory.vue'
import SkillsDisplayPreferences from './SkillsDisplayPreferences.vue'
import ClearSkillsHistory from './ClearSkillsHistory.vue'
import { loadSkillsHistoryState } from '../../api/skills.js'

let engine = createBreathingSession()
let journal = null
let frame = null
let active = false
let journalContext = null
const state = ref(engine.snapshot())
const page = ref('exercise')
const historyEpoch = ref(0)
const historyVersion = ref(0)
const conversationEpoch = ref(0)
let epochRequest = 0
const conversationPlacement = ref('before')
const conversationSession = ref(null)
const simpler = ref(false)
const motion = ref('system')
const reducedQuery = window.matchMedia('(prefers-reduced-motion: reduce)')
const reducedMotion = ref(reducedQuery.matches)
const staticCue = computed(() => useStaticCue(motion.value, reducedMotion.value))
const support = ref(null)
const saveState = ref({ state: 'none', error: '' })
const notice = ref('')
const sessionId = ref('')
const recoveredId = ref(readMarker())
const historyInitialId = ref('')
const renderedPhases = ref([])
const renderStart = ref(null)
const renderEnd = ref(null)
let renderPause = null
let excludedRenderMs = 0
const renderedActiveMs = ref(null)

function readMarker() { try { return sessionStorage.getItem('skills-active-session') || '' } catch { return '' } }
function writeMarker(id) { try { sessionStorage.setItem('skills-active-session', id) } catch { /* Storage is optional. */ } }
function clearMarker(id) { try { if (readMarker() === id) sessionStorage.removeItem('skills-active-session') } catch { /* Optional. */ } }
const terminal = (status) => ['completed', 'stopped'].includes(status)

function persist(kind, reason = null) {
  if (!journal) return
  if (terminal(state.value.status) || kind === 'interrupt') journalContext.terminal = true
  journal.enqueue(kind, state.value, reason)
}

function beginJournal() {
  const id = crypto.randomUUID()
  sessionId.value = id
  writeMarker(id)
  const context = { terminal: false }
  journalContext = context
  journal = createSessionJournal({
    sessionId: id, historyEpoch: historyEpoch.value, settings: { simpler_view: simpler.value, motion_mode: motion.value },
    onChange(result) {
      if (sessionId.value === id) saveState.value = result
      if (result.state === 'saved' && context.terminal) clearMarker(id)
    },
  })
}

function cancelFrame() { if (frame !== null) cancelAnimationFrame(frame); frame = null }
function schedule() { cancelFrame(); if (active && state.value.status === 'running') frame = requestAnimationFrame(tick) }
function tick() {
  const previous = state.value
  state.value = engine.tick()
  if (state.value.status === 'completed' && previous.status === 'running') persist('complete')
  else if (state.value.status === 'paused' && previous.status === 'running') persist('pause', 'timing')
  else if (state.value.phase !== previous.phase || state.value.cyclesCompleted !== previous.cyclesCompleted) persist('checkpoint')
  schedule()
}

function applyDisplayChoices(settings) {
  if (state.value.status !== 'ready' || page.value !== 'exercise') return
  simpler.value = settings.simpler_view
  motion.value = settings.motion_mode
}
function start() {
  if (state.value.status !== 'ready') return
  beginJournal()
  state.value = engine.start()
  persist('start')
  schedule()
}
function pause(reason = 'user') {
  if (state.value.status !== 'running') return
  state.value = engine.pause(reason)
  persist(state.value.status === 'completed' ? 'complete' : 'pause', state.value.status === 'completed' ? null : state.value.pauseReason ?? reason)
  cancelFrame()
}
function resume() {
  state.value = engine.resume()
  if (state.value.status === 'running') { persist('resume'); schedule() }
}
function stop(kind = 'stop') {
  if (terminal(state.value.status)) return
  state.value = engine.stop()
  persist(kind)
  cancelFrame()
}
function leave() { stop(); page.value = 'idle'; support.value?.close() }

function openSupport() {
  const previous = state.value.status
  state.value = engine.openSupport()
  if (!terminal(previous) && journal) {
    if (state.value.status === 'completed') persist('complete')
    else persist('support_open')
  }
  cancelFrame()
  support.value.open()
}
function closeSupport() {
  const wasOpen = state.value.supportOpen
  state.value = engine.closeSupport()
  if (wasOpen && !terminal(state.value.status)) persist('support_close')
}

async function refreshHistoryEpoch() {
  const request = ++epochRequest
  try {
    const result = await loadSkillsHistoryState()
    if (active && request === epochRequest) historyEpoch.value = Math.max(historyEpoch.value, result.history_epoch)
  } catch { /* Earlier epochs fail closed; local exercise controls remain available. */ }
}
function discardHistoryDrafts() {
  epochRequest++
  journal?.dispose()
  journal = null; journalContext = null; sessionId.value = ''
  cancelFrame(); state.value = engine.stop()
  saveState.value = { state: 'none', error: '' }
  recoveredId.value = ''; historyInitialId.value = ''
  try { sessionStorage.removeItem('skills-active-session') } catch { /* Optional marker. */ }
}
function historyCleared(result) {
  epochRequest++
  historyEpoch.value = Math.max(historyEpoch.value, result.history_epoch)
  historyVersion.value++
}
function reset() {
  if (saveState.value.state === 'error' || saveState.value.state === 'saving') {
    notice.value = 'An earlier session may have unsaved changes. Check saved history to confirm its last checkpoint.'
  }
  cancelFrame()
  journal = null; journalContext = null; sessionId.value = ''
  engine = createBreathingSession(); state.value = engine.snapshot()
  refreshHistoryEpoch()
  page.value = 'exercise'; saveState.value = { state: 'none', error: '' }
  renderedPhases.value = []; renderStart.value = null; renderEnd.value = null
  renderedActiveMs.value = null; renderPause = null; excludedRenderMs = 0
}
function showConversation() {
  conversationEpoch.value = historyEpoch.value
  conversationPlacement.value = terminal(state.value.status) ? 'after' : 'before'
  conversationSession.value = terminal(state.value.status) && saveState.value.state === 'saved' ? sessionId.value : null
  page.value = 'conversation'
}
function showHistory(id = '') { if (state.value.status === 'running') pause(); historyInitialId.value = id; page.value = 'history' }

watch(() => `${page.value}:${state.value.status}:${state.value.phase}:${state.value.cycle}`, async () => {
  await nextTick()
  if (!active) return
  const at = performance.now()
  const snapshot = state.value
  if (snapshot.status === 'running' && page.value === 'exercise') {
    if (renderStart.value === null) renderStart.value = at
    if (renderPause !== null) { excludedRenderMs += at - renderPause; renderPause = null }
    const key = `${snapshot.cycle}:${snapshot.phase}`
    if (renderedPhases.value.at(-1) !== key) renderedPhases.value.push(key)
  } else if (snapshot.status === 'paused' && renderStart.value !== null && renderPause === null) {
    renderPause = at
  } else if (terminal(snapshot.status) && renderStart.value !== null) {
    if (renderPause !== null) { excludedRenderMs += at - renderPause; renderPause = null }
    renderEnd.value = at
    renderedActiveMs.value = Math.round(at - renderStart.value - excludedRenderMs)
  }
})

const cueScale = computed(() => {
  if (staticCue.value) return 'none'
  const progress = state.value.phase === 'inhale'
    ? 1 - state.value.phaseRemainingMs / 4000 : state.value.phaseRemainingMs / 6000
  return `scale(${0.7 + 0.3 * progress})`
})
function hidden() { if (document.hidden) pause('hidden') }
function pageHidden() { stop('interrupt') }
function preferenceChanged() { reducedMotion.value = reducedQuery.matches }
function deactivate() {
  active = false; stop(); cancelFrame(); support.value?.close()
  if (page.value === 'conversation') page.value = 'idle'
  document.removeEventListener('visibilitychange', hidden)
  window.removeEventListener('pagehide', pageHidden)
  reducedQuery.removeEventListener('change', preferenceChanged)
}
onActivated(() => {
  active = true
  refreshHistoryEpoch()
  reducedMotion.value = reducedQuery.matches
  document.addEventListener('visibilitychange', hidden)
  window.addEventListener('pagehide', pageHidden)
  reducedQuery.addEventListener('change', preferenceChanged)
})
onDeactivated(deactivate)
onBeforeUnmount(deactivate)
</script>

<template>
  <div class="skills-experience">
    <header class="skills-safety-bar">
      <span>Coursework prototype</span>
      <div>
        <button type="button" class="support-button" @click="openSupport">Crisis support</button>
        <button type="button" @click="leave">Leave</button>
      </div>
    </header>
    <main class="skills-content">
      <h1>Skills Prototype</h1>
      <p class="boundary">For fictional testing only. Not therapy or monitored support.</p>
      <button type="button" class="quiet" :aria-pressed="simpler" @click="simpler = !simpler">{{ simpler ? 'Show more' : 'Simpler view' }}</button>
      <p v-if="notice" role="status">{{ notice }}</p>
      <p v-if="recoveredId && page !== 'history'" class="recovery">An earlier exercise will not restart automatically. <button type="button" class="quiet" @click="showHistory(recoveredId); recoveredId = ''">Review earlier session</button></p>

      <section v-if="page === 'idle'" class="exercise-card">
        <h2>You have left the experience</h2>
        <p>Nothing else is required.</p>
        <button type="button" @click="reset">Return to skills</button>
      </section>
      <SkillsConversation v-else-if="page === 'conversation'" :placement="conversationPlacement" :session-id="conversationSession" :history-epoch="conversationEpoch" @back="page = 'exercise'" />
      <template v-else-if="page === 'conversation-history'">
        <button type="button" class="quiet" @click="page = 'exercise'">Back to exercise options</button>
        <SkillsConversationHistory :key="historyVersion" />
      </template>
      <template v-else-if="page === 'history'">
        <button type="button" class="quiet" @click="page = 'exercise'">Back to exercise</button>
        <SkillsHistory :key="historyVersion" :initial-id="historyInitialId" @reconciled="clearMarker" />
      </template>
      <section v-else class="exercise-card" aria-label="Paced breathing exercise"
               :data-status="state.status" :data-active-ms="state.activeMs" :data-rendered-phases="renderedPhases.join(',')"
               :data-rendered-active-ms="renderedActiveMs" :data-static-cue="staticCue">
        <template v-if="state.status === 'ready'">
          <h2>Paced breathing · 60 seconds</h2>
          <p v-if="!simpler">Six cycles: four-second inhale, six-second exhale. Pause or stop is available throughout.</p>
          <label v-if="!simpler" class="motion-choice">Pacing display
            <select v-model="motion"><option value="system">Follow device motion preference</option><option value="static">Static cue</option><option value="gentle">Gentle pacing cue</option></select>
          </label>
          <p v-if="reducedMotion">Your reduced-motion preference is active. The cue stays still.</p>
          <button type="button" @click="start">Start 60-second exercise</button>
          <SkillsDisplayPreferences :simpler="simpler" :motion="motion" @apply="applyDisplayChoices" />
        </template>
        <template v-else-if="['running', 'paused'].includes(state.status)">
          <p id="breathing-phase" class="phase" aria-live="polite" aria-atomic="true">{{ state.status === 'paused' ? 'Paused' : state.phase === 'inhale' ? 'Inhale' : 'Exhale' }}</p>
          <div class="cue-space" aria-hidden="true"><div class="pacing-cue" :style="{ transform: cueScale }" /></div>
          <p class="seconds">{{ Math.ceil(state.phaseRemainingMs / 1000) }} {{ state.phaseRemainingMs > 1000 ? 'seconds' : 'second' }} {{ state.status === 'paused' ? 'remaining in this phase' : '' }}</p>
          <p>Cycle {{ state.cycle }} of 6</p>
          <p v-if="state.pauseReason === 'timing'">Timing paused after a delayed cue. Resume when ready, or stop.</p>
          <div class="exercise-actions">
            <button v-if="state.status === 'running'" type="button" @click="pause()">Pause</button>
            <button v-else type="button" @click="resume">Resume</button>
            <button type="button" @click="stop()">Stop</button>
          </div>
          <p v-if="reducedMotion">Reduced motion is active; the cue stays still.</p>
          <button v-else type="button" class="quiet" @click="motion = staticCue ? 'system' : 'static'">{{ staticCue ? 'Use device motion setting' : 'Use static cue' }}</button>
        </template>
        <template v-else>
          <h2>{{ state.status === 'completed' ? 'Exercise finished' : 'Exercise stopped' }}</h2>
          <p>You can leave, review history, or choose again.</p>
          <button type="button" @click="reset">Choose again</button>
          <details v-if="state.status === 'completed'">
            <summary>Session timing details</summary>
            <p>Rendered cue interval, excluding pauses: {{ (renderedActiveMs / 1000).toFixed(2) }} seconds. {{ renderedPhases.length }} phase cues observed.</p>
            <p>Clock active time: {{ (state.activeMs / 1000).toFixed(2) }} seconds. Setup: {{ (state.setupMs / 1000).toFixed(2) }} seconds.</p>
          </details>
        </template>
      </section>

      <button v-if="page === 'exercise' && (state.status === 'ready' || terminal(state.status))" type="button" class="quiet" @click="showConversation">Optional conversation {{ terminal(state.status) ? 'after' : 'before' }} breathing</button>
      <button v-if="page === 'exercise' && state.status !== 'running' && !simpler" type="button" class="quiet" @click="page = 'conversation-history'">Conversation history</button>
      <ClearSkillsHistory v-if="['history', 'conversation-history'].includes(page)" @intent="discardHistoryDrafts" @cleared="historyCleared" @crisis="openSupport" @leave="leave" />
      <div class="save-feedback" aria-live="polite">
        <p v-if="saveState.state === 'saving'">Saving checkpoints… Exercise controls remain available.</p>
        <p v-if="saveState.state === 'saved'">Latest checkpoint saved.</p>
        <template v-if="saveState.state === 'error'"><p role="alert">Not saved. {{ saveState.error }}</p><button type="button" class="quiet" @click="journal?.retry()">Retry saving</button></template>
      </div>
      <button v-if="page !== 'history' && state.status !== 'running' && !simpler" type="button" class="quiet" @click="showHistory()">Session history</button>
    </main>
    <CrisisSupportPanel ref="support" @closed="closeSupport" @leave="leave" />
  </div>
</template>

<style scoped>
.skills-experience { min-height: 100dvh; background: #f3f4ef; color: #263e35; }
.skills-safety-bar { position: sticky; top: 0; z-index: 20; display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 0.5rem; padding: 0.8rem max(1rem, calc((100% - 52rem) / 2)); background: #f8f9f4; border-bottom: 1px solid #c7d2c9; }
.skills-safety-bar > div { display: flex; gap: 0.5rem; }
.skills-content { max-width: 48rem; margin: 0 auto; padding: 1.7rem 1.25rem 6rem; }
h1 { font-size: clamp(1.8rem, 5vw, 2.5rem); letter-spacing: -0.03em; }
.boundary { font-size: 0.9rem; color: #4c6056; }
button { background: #355e51; padding: 0.75rem 1rem; font-weight: 650; }
button:hover:not(:disabled) { background: #294b40; }
.quiet { background: transparent; color: #294f42; border: 1px solid #8a9f91; margin: 0.5rem 0; }
.quiet:hover:not(:disabled) { color: #fff; }
.support-button { border: 1px solid #355e51; }
.exercise-card { margin-top: 1.3rem; padding: 1.5rem 1rem; border: 1px solid #c5d0c6; border-radius: 1rem; background: #fafbf7; text-align: center; }
.motion-choice { display: grid; gap: 0.5rem; max-width: 25rem; margin: 1rem auto; text-align: left; }
.motion-choice select { padding: 0.65rem; color: #294f42; border-color: #8a9f91; }
.phase { margin: 0.5rem 0; font-size: 2.5rem; font-weight: 600; }
.cue-space { display: grid; place-items: center; height: 10rem; }
.pacing-cue { width: 9rem; height: 9rem; border-radius: 50%; background: #9ab6a8; border: 2px solid #537c69; }
.seconds { font-size: 1.2rem; font-variant-numeric: tabular-nums; }
.exercise-actions { position: fixed; bottom: 0; left: 0; z-index: 19; width: 100%; display: flex; justify-content: center; gap: 1rem; padding: 0.65rem; background: #f8f9f4; border-top: 1px solid #c7d2c9; }
.save-feedback { min-height: 2rem; font-size: 0.9rem; }
details { margin: 1rem 0; text-align: left; } summary { cursor: pointer; }
.recovery { padding: 0.75rem; border-left: 3px solid #7b9785; }
button:focus-visible, select:focus-visible { outline: 3px solid #547e71; outline-offset: 4px; }
@media (prefers-reduced-motion: reduce) { .pacing-cue { transform: none !important; } }
@media (max-width: 25rem) { .skills-safety-bar { padding: 0.6rem; } .skills-safety-bar > span { font-size: 0.8rem; } .skills-safety-bar button { padding: 0.6rem; } }
</style>
