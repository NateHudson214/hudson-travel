import assert from 'node:assert/strict'
import test from 'node:test'
import { createConversation } from './conversation.js'
const response = (revision = 2) => ({ conversation: { revision }, messages: [{ message_id: `m${revision}`, content: 'Approved mock reply' }] })

test('failed turn retries exact request ID and body, then next turn advances revision', async () => {
  let state, n = 0
  const calls = []
  const chat = createConversation({ placement: 'before', makeId: () => `id-${++n}`, onChange: value => { state = value }, send: async body => {
    calls.push(body)
    if (calls.length === 1) throw new Error('Offline')
    return response(body.expected_revision + 2)
  } })
  await chat.submit('  Fictional message  ')
  assert.equal(state.error, 'Offline')
  assert.equal(state.canRetry, true)
  await chat.submit('Must not replace failed draft')
  assert.equal(calls.length, 1)
  await chat.retry()
  assert.strictEqual(calls[0], calls[1])
  assert.equal(calls[1].message, 'Fictional message')
  await chat.submit('Next fictional message')
  assert.equal(calls[2].expected_revision, 2)
  assert.notEqual(calls[2].request_id, calls[1].request_id)
  assert.equal(state.messages.length, 2)
})

test('busy state blocks duplicate submits; leaving ignores a late reply', async () => {
  let release, state, published = 0, count = 0
  const chat = createConversation({ placement: 'after', sessionId: 's1', onChange: s => { state = s; published++ }, send: body => {
    count++
    assert.equal(body.session_id, 's1')
    return new Promise(resolve => { release = resolve })
  } })
  const pending = chat.submit('Fictional message')
  assert.equal(state.busy, true)
  await chat.submit('Duplicate')
  assert.equal(count, 1)
  chat.dispose()
  const before = published
  release(response())
  await pending
  assert.equal(published, before)
  assert.equal(state.messages.length, 0)
  await chat.retry(); await chat.submit('After leaving')
  assert.equal(count, 1)
})

test('invalid input does not send and retry is never automatic', async () => {
  let calls = 0
  const chat = createConversation({ placement: 'before', send: async () => { calls++; throw new Error('failed') } })
  await chat.submit('  '); await chat.submit('x'.repeat(501))
  assert.equal(calls, 0)
  await chat.submit('Fictional')
  await Promise.resolve()
  assert.equal(calls, 1)
})

test('conversation binds its original history generation, including retries', async () => {
  let bodies = []
  const chat = createConversation({ placement: 'before', historyEpoch: 8, send: async body => {
    bodies.push(body); if (bodies.length === 1) throw new Error('lost response'); return response()
  } })
  await chat.submit('Fictional stale request'); await chat.retry()
  assert.equal(bodies[0].history_epoch, 8)
  assert.strictEqual(bodies[0], bodies[1])
})

test('pending reply keeps the exact request for explicit status retry without duplicating messages', async () => {
  const calls = []
  let state
  const chat = createConversation({ placement: 'before', allowLive: true, onChange: s => { state = s },
    send: async body => {
      calls.push(body)
      return calls.length === 1 ? { run: { status: 'pending' } } : response()
    } })
  await chat.submit('Fictional question')
  assert.equal(calls[0].allow_live, true)
  assert.equal(state.canRetry, true)
  assert.equal(state.messages.length, 0)
  assert.match(state.error, /pending/)
  await chat.retry()
  assert.strictEqual(calls[0], calls[1])
  assert.equal(state.canRetry, false)
  assert.equal(state.messages.length, 1)
})

test('leaving sends best-effort cancellation with the pinned epoch and ignores late success', async () => {
  let release, state
  const cancelled = []
  const chat = createConversation({ placement: 'before', historyEpoch: 7, onChange: s => { state = s },
    send: () => new Promise(resolve => { release = resolve }),
    cancel: async (...args) => { cancelled.push(args); throw new Error('Offline') } })
  const sending = chat.submit('Fictional')
  chat.dispose()
  await Promise.resolve()
  assert.equal(cancelled.length, 1)
  assert.equal(cancelled[0][1], 7)
  release(response())
  await sending
  assert.deepEqual(state.messages, [])
})

test('budget fallback is visibly labeled as a mock and cannot change display choices', async () => {
  let state
  const chat = createConversation({ placement: 'after', allowLive: true, onChange: s => { state = s },
    send: async () => ({ ...response(), run: { mode: 'mock', status: 'completed' } }) })
  await chat.submit('Fictional')
  assert.match(state.modeNotice, /fixed mock/)
  assert.equal(state.canRetry, false)
})
