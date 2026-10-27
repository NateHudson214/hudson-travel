import assert from 'node:assert/strict'
import test from 'node:test'
import { appendSkillsEvent, createSkillsSession, loadSkillsSession, loadSkillsSessions, SkillsApiError } from './skills.js'

test('creates only a skills session with explicit display settings and an abortable request', async (t) => {
  const mock = t.mock.method(globalThis, 'fetch', async () => ({ ok: true, status: 201, json: async () => ({ session: { status: 'ready' } }) }))
  const result = await createSkillsSession('test-id', { simpler_view: true, motion_mode: 'static' })
  const [path, options] = mock.mock.calls[0].arguments
  assert.equal(path, '/api/skills/sessions')
  assert.equal(options.method, 'POST')
  assert.equal(options.signal instanceof AbortSignal, true)
  assert.deepEqual(JSON.parse(options.body), { session_id: 'test-id', display_settings: { simpler_view: true, motion_mode: 'static' }, history_epoch: 0 })
  assert.equal(result.session.status, 'ready')
})

test('event bodies and UUIDs are preserved exactly for server idempotency', async (t) => {
  const mock = t.mock.method(globalThis, 'fetch', async () => ({ ok: true, status: 200, json: async () => ({ replayed: true }) }))
  const body = { event_id: 'stable-id', sequence: 2, expected_revision: 1, kind: 'stop', snapshot: { active_ms: 1200 }, reason: null }
  await appendSkillsEvent('id / one', body)
  assert.equal(mock.mock.calls[0].arguments[0], '/api/skills/sessions/id%20%2F%20one/events')
  assert.deepEqual(JSON.parse(mock.mock.calls[0].arguments[1].body), body)
})

test('history GETs use bounded pages, encoded cursors and event sequence without provider POSTs', async (t) => {
  const mock = t.mock.method(globalThis, 'fetch', async () => ({ ok: true, status: 200, json: async () => ({ sessions: [], events: [] }) }))
  await loadSkillsSessions('cursor+/=')
  await loadSkillsSession('id one', 50)
  assert.equal(mock.mock.calls[0].arguments[0], '/api/skills/sessions?limit=20&cursor=cursor%2B%2F%3D')
  assert.equal(mock.mock.calls[1].arguments[0], '/api/skills/sessions/id%20one?limit=50&after_sequence=50')
  assert.equal(mock.mock.calls.every((call) => call.arguments[1].method === undefined), true)
})

test('network, invalid JSON and storage failures have bounded user-facing errors', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => { throw new Error('PRIVATE_RAW_DETAIL') })
  await assert.rejects(loadSkillsSessions(), (error) => error instanceof SkillsApiError && !error.message.includes('PRIVATE_RAW_DETAIL'))
  t.mock.method(globalThis, 'fetch', async () => ({ ok: false, status: 503, json: async () => ({ detail: 'Skills session storage is unavailable.' }) }))
  await assert.rejects(loadSkillsSessions(), { message: 'Skills session storage is unavailable.' })
  t.mock.method(globalThis, 'fetch', async () => ({ ok: true, status: 200, json: async () => { throw new Error('bad JSON') } }))
  await assert.rejects(loadSkillsSessions(), SkillsApiError)
})

test('mock conversation and read-only history use skills-only routes and preserve retry IDs', async (t) => {
  const { sendSkillsTurn, loadSkillsConversations, loadSkillsConversation } = await import('./skills.js')
  const mock = t.mock.method(globalThis, 'fetch', async () => ({ ok: true, status: 200, json: async () => ({ messages: [] }) }))
  const body = { request_id: 'same-id', conversation_id: 'c1', placement: 'before', expected_revision: 0, session_id: null, message: 'Fictional' }
  await sendSkillsTurn(body)
  await loadSkillsConversations('a+/=')
  await loadSkillsConversation('id / one', 50)
  assert.equal(mock.mock.calls[0].arguments[0], '/api/skills/conversations/turns')
  assert.deepEqual(JSON.parse(mock.mock.calls[0].arguments[1].body), body)
  assert.equal(mock.mock.calls[1].arguments[0], '/api/skills/conversations?limit=20&cursor=a%2B%2F%3D')
  assert.equal(mock.mock.calls[2].arguments[0], '/api/skills/conversations/id%20%2F%20one?limit=50&after_sequence=50')
  assert.equal(mock.mock.calls.slice(1).every(c => c.arguments[1].method === undefined), true)
})

test('saved display preferences use only explicit skills GET/POST with stable revision and ID', async (t) => {
  const { loadSkillsPreferences, changeSkillsPreferences } = await import('./skills.js')
  const mock = t.mock.method(globalThis, 'fetch', async () => ({ ok: true, status: 200, json: async () => ({ preferences: { revision: 1 } }) }))
  const body = { request_id: 'same-request', expected_revision: 0, action: 'save', display_settings: { simpler_view: true, motion_mode: 'static' } }
  await loadSkillsPreferences(); await changeSkillsPreferences(body)
  assert.equal(mock.mock.calls[0].arguments[0], '/api/skills/preferences')
  assert.equal(mock.mock.calls[0].arguments[1].method, undefined)
  assert.equal(mock.mock.calls[1].arguments[0], '/api/skills/preferences')
  assert.equal(mock.mock.calls[1].arguments[1].method, 'POST')
  assert.deepEqual(JSON.parse(mock.mock.calls[1].arguments[1].body), body)
})

test('clear history requires explicit DELETE confirmation and generation; state reads are GET only', async (t) => {
  const { clearSkillsHistory, loadSkillsHistoryState } = await import('./skills.js')
  const mock = t.mock.method(globalThis, 'fetch', async () => ({ ok: true, status: 200, json: async () => ({ history_epoch: 4 }) }))
  await loadSkillsHistoryState()
  const body = { request_id: 'clear-only', expected_epoch: 3, confirm: true }
  await clearSkillsHistory(body)
  assert.equal(mock.mock.calls[0].arguments[0], '/api/skills/history')
  assert.equal(mock.mock.calls[0].arguments[1].cache, 'no-store')
  assert.equal(mock.mock.calls[0].arguments[1].method, undefined)
  assert.equal(mock.mock.calls[1].arguments[1].method, 'DELETE')
  assert.deepEqual(JSON.parse(mock.mock.calls[1].arguments[1].body), body)
  await createSkillsSession('new-session', { motion_mode: 'system' }, 4)
  assert.equal(JSON.parse(mock.mock.calls[2].arguments[1].body).history_epoch, 4)
})

test('model disclosure reads and cancellation are skills-only and preserve generation', async (t) => {
  const { loadSkillsModelStatus, cancelSkillsRun } = await import('./skills.js')
  const mock = t.mock.method(globalThis, 'fetch', async () => ({ ok: true, status: 200, json: async () => ({ mode: 'mock' }) }))
  await loadSkillsModelStatus()
  await cancelSkillsRun('id / one', 8)
  assert.equal(mock.mock.calls[0].arguments[0], '/api/skills/model-status')
  assert.equal(mock.mock.calls[0].arguments[1].method, undefined)
  assert.equal(mock.mock.calls[1].arguments[0], '/api/skills/runs/id%20%2F%20one/cancel')
  assert.deepEqual(JSON.parse(mock.mock.calls[1].arguments[1].body), { history_epoch: 8 })
})
