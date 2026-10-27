import { ApiRequestError, requestJson } from './http.js'

export class SkillsApiError extends ApiRequestError {}

async function request(path, body, method = 'POST') {
  const controller = new AbortController()
  const timeout = setTimeout(() => controller.abort(), 5000)
  try {
    return await requestJson(path, {
      signal: controller.signal, cache: 'no-store',
      ...(body === undefined ? {} : {
        method, headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      }),
    }, SkillsApiError, 'Skills storage is unavailable. Your latest changes may not be saved.')
  } finally {
    clearTimeout(timeout)
  }
}

export function createSkillsSession(sessionId, displaySettings, historyEpoch = 0) {
  return request('/api/skills/sessions', { session_id: sessionId, display_settings: displaySettings, history_epoch: historyEpoch })
}

export function appendSkillsEvent(sessionId, event) {
  return request(`/api/skills/sessions/${encodeURIComponent(sessionId)}/events`, event)
}

export function loadSkillsSessions(cursor = null) {
  const params = new URLSearchParams({ limit: '20' })
  if (cursor) params.set('cursor', cursor)
  return request(`/api/skills/sessions?${params}`)
}

export function loadSkillsSession(sessionId, afterSequence = 0) {
  return request(`/api/skills/sessions/${encodeURIComponent(sessionId)}?limit=50&after_sequence=${afterSequence}`)
}

export function sendSkillsTurn(body) {
  return request('/api/skills/conversations/turns', body)
}

export function loadSkillsConversations(cursor = null) {
  const params = new URLSearchParams({ limit: '20' })
  if (cursor) params.set('cursor', cursor)
  return request(`/api/skills/conversations?${params}`)
}

export function loadSkillsConversation(id, afterSequence = 0) {
  return request(`/api/skills/conversations/${encodeURIComponent(id)}?limit=50&after_sequence=${afterSequence}`)
}

export function loadSkillsPreferences() {
  return request('/api/skills/preferences')
}

export function changeSkillsPreferences(body) {
  return request('/api/skills/preferences', body)
}


export function loadSkillsHistoryState() {
  return request('/api/skills/history')
}

export function clearSkillsHistory(body) {
  return request('/api/skills/history', body, 'DELETE')
}

export function loadSkillsModelStatus() {
  return request('/api/skills/model-status')
}

export function cancelSkillsRun(id, historyEpoch) {
  return request(`/api/skills/runs/${encodeURIComponent(id)}/cancel`, { history_epoch: historyEpoch })
}
