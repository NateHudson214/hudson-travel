import { appendSkillsEvent, createSkillsSession } from '../api/skills.js'

export function checkpoint(state) {
  return {
    active_ms: state.activeMs, pause_ms: state.pauseMs, support_ms: state.supportMs,
    setup_ms: state.setupMs ?? 0, cycles_completed: state.cyclesCompleted,
    phase: state.phase, phase_remaining_ms: state.phaseRemainingMs,
  }
}

// Failed requests retain their exact UUID/body for explicit retry in this exercise's queue.
export function createSessionJournal({
  sessionId, settings, historyEpoch = 0, onChange = () => {}, makeId = () => crypto.randomUUID(),
  create = createSkillsSession, append = appendSkillsEvent,
}) {
  const operations = [{ type: 'create', settings: { ...settings } }]
  let disposed = false
  let sequence = 0
  let failure = ''
  let pumping = null

  function status() {
    return { state: failure ? 'error' : operations.length ? 'saving' : 'saved', error: failure }
  }
  function publish() { if (!disposed) onChange(status()) }
  async function run() {
    while (operations.length && !failure && !disposed) {
      const operation = operations[0]
      try {
        if (operation.type === 'create') await create(sessionId, operation.settings, historyEpoch)
        else await append(sessionId, operation.body)
        if (disposed) return
        operations.shift()
      } catch (error) {
        failure = error.message || 'Your latest checkpoint was not saved.'
      }
      publish()
    }
  }
  function pump() {
    if (!pumping) pumping = Promise.resolve().then(run).finally(() => { pumping = null })
    publish()
    return pumping
  }
  function enqueue(kind, state, reason = null) {
    if (disposed) return
    sequence += 1
    operations.push({ type: 'event', body: {
      history_epoch: historyEpoch, event_id: makeId(), sequence, expected_revision: sequence - 1, kind,
      snapshot: checkpoint(state), reason,
    } })
    pump()
  }
  function retry() { if (disposed) return Promise.resolve(); failure = ''; return pump() }
  pump()
  return { enqueue, retry, status, dispose() { disposed = true; operations.length = 0 }, settled: () => pumping ?? Promise.resolve() }
}
