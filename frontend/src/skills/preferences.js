import { changeSkillsPreferences, loadSkillsPreferences } from '../api/skills.js'

export const DEFAULT_DISPLAY = Object.freeze({ simpler_view: false, motion_mode: 'system' })
export const motionLabel = mode => ({ system: 'device motion setting', static: 'static cue', gentle: 'gentle pacing cue' })[mode]

// Reading/saving never applies choices. Only Use last setup and Reset invoke apply.
export function createDisplayPreferences({ onChange = () => {}, apply = () => {},
  load = loadSkillsPreferences, change = changeSkillsPreferences, makeId = () => crypto.randomUUID() } = {}) {
  let revision = null
  let lastSetup = null
  let pending = null
  let queued = 0
  let chain = Promise.resolve()
  let disposed = false
  let error = ''
  let notice = ''
  function publish() {
    if (!disposed) onChange({ busy: queued > 0, lastSetup: lastSetup && { ...lastSetup }, error, notice,
      canSave: revision !== null && pending === null, canRetry: pending !== null })
  }
  function accept(result) {
    revision = result.preferences.revision
    lastSetup = result.preferences.last_setup
  }
  function enqueue(operation) {
    queued++; publish()
    const task = chain.then(async () => {
      error = ''
      try { await operation() }
      catch (failure) { error = failure.message || 'Saved display choices are unavailable.'; notice = '' }
      finally { queued--; publish() }
    })
    chain = task
    return task
  }
  async function send(body) {
    pending = body
    accept(await change(body))
    pending = null
    notice = body.action === 'reset' ? 'Display defaults restored and saved choices cleared.' : 'Display choices saved. Reuse remains optional.'
  }
  function refresh() {
    return enqueue(async () => { accept(await load()); pending = null; notice = 'Saved choices refreshed; your current display has not changed.' })
  }
  function save(settings) {
    if (disposed || queued || revision === null || pending) return Promise.resolve()
    const body = { request_id: makeId(), expected_revision: revision, action: 'save', display_settings: { ...settings } }
    return enqueue(() => send(body))
  }
  function reset() {
    if (disposed) return Promise.resolve()
    apply({ ...DEFAULT_DISPLAY })
    notice = 'Display reset locally. Clearing saved choices…'
    lastSetup = null
    // Serialize behind earlier writes, then read a fresh revision. Never retry an
    // older failed save after reset; its stale revision cannot restore choices.
    return enqueue(async () => {
      pending = null
      accept(await load())
      await send({ request_id: makeId(), expected_revision: revision, action: 'reset', display_settings: null })
    })
  }
  function useLast() {
    if (disposed || queued || !lastSetup) return
    apply({ ...lastSetup })
    notice = 'Last setup applied. Start only when you choose.'
    publish()
  }
  function retry() {
    if (disposed || queued || !pending) return Promise.resolve()
    const body = pending
    return enqueue(() => send(body))
  }
  return { refresh, save, reset, useLast, retry, dispose() { disposed = true } }
}
