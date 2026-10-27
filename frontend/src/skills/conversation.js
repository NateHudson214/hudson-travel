import { sendSkillsTurn, cancelSkillsRun } from '../api/skills.js'

// No timer/navigation/preferences callback exists in this boundary.
export function createConversation({ placement, sessionId = null, historyEpoch = 0, allowLive = false, onChange = () => {},
  send = sendSkillsTurn, cancel = cancelSkillsRun, makeId = () => crypto.randomUUID() }) {
  const id = makeId()
  let revision = 0
  let messages = []
  let pending = null
  let busy = false
  let error = ''
  let modeNotice = ''
  let disposed = false
  function publish() {
    if (!disposed) onChange({ messages: [...messages], busy, error, modeNotice, canRetry: !!pending && !busy })
  }
  async function dispatch() {
    if (disposed || busy || !pending) return
    busy = true; error = ''; publish()
    try {
      const result = await send(pending)
      if (disposed) return
      if (result.run?.status === 'pending') {
        error = 'This turn is still pending. Check the same turn again; no new model call will be sent.'
        return
      }
      modeNotice = result.mode_notice || (allowLive && result.run?.mode === 'mock' ? 'Live allowance reached; this reply uses the fixed mock.' : '')
      revision = result.conversation.revision
      messages = [...messages, ...result.messages]
      pending = null
    } catch (failure) {
      if (!disposed) error = failure.message || 'Conversation could not be saved. Continue without it or retry.'
    } finally {
      busy = false; publish()
    }
  }
  function submit(message) {
    if (disposed || busy || pending) return Promise.resolve()
    const normalized = message.trim()
    if (!normalized || message.length > 500) return Promise.resolve()
    pending = { history_epoch: historyEpoch, conversation_id: id, request_id: makeId(), expected_revision: revision,
      placement, session_id: sessionId, message: normalized, allow_live: allowLive }
    return dispatch()
  }
  return { submit, retry: dispatch, dispose() {
    disposed = true
    if (pending) Promise.resolve().then(() => cancel(pending.request_id, historyEpoch)).catch(() => {})
  }, }
}
