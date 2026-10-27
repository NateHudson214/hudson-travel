import { clearSkillsHistory, loadSkillsHistoryState } from '../api/skills.js'

export function createHistoryClear({ load = loadSkillsHistoryState, clear = clearSkillsHistory,
  onChange = () => {}, onIntent = () => {}, onCleared = () => {}, makeId = () => crypto.randomUUID() } = {}) {
  let pending = null
  let busy = false
  let ready = false
  let attempted = false
  let error = ''
  let success = false
  let disposed = false
  function publish() { if (!disposed) onChange({ busy, ready, attempted, error, success }) }
  async function prepare() {
    if (disposed || busy || (pending && attempted && !success)) return
    busy = true; ready = false; error = ''; success = false; pending = null; attempted = false; publish()
    try {
      const result = await load()
      if (disposed) return
      pending = { request_id: makeId(), expected_epoch: result.history_epoch, confirm: true }
      ready = true
    } catch (failure) { error = failure.message || 'History status is unavailable.' }
    finally { busy = false; publish() }
  }
  async function confirm() {
    if (disposed || busy || !ready || !pending || success) return
    if (!attempted) onIntent()
    attempted = true; busy = true; error = ''; publish()
    try {
      const result = await clear(pending)
      if (disposed) return
      success = true; ready = false; pending = null
      onCleared(result)
    } catch (failure) { error = failure.message || 'Could not confirm whether history was cleared.' }
    finally { busy = false; publish() }
  }
  return { prepare, confirm, dispose() { disposed = true } }
}
