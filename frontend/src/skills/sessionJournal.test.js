import assert from 'node:assert/strict'
import test from 'node:test'
import { createBreathingSession } from './breathing.js'
import { checkpoint, createSessionJournal } from './sessionJournal.js'

function setup(overrides = {}) {
  const calls = []
  let id = 0
  const journal = createSessionJournal({ sessionId: 'session-one', settings: { motion_mode: 'static' },
    makeId: () => `event-${++id}`,
    create: async (...args) => { calls.push(['create', ...args]) },
    append: async (...args) => { calls.push(['event', ...args]) },
    ...overrides,
  })
  return { journal, calls }
}

test('serial queue saves create then all events in local order with increasing revisions', async () => {
  const engine = createBreathingSession({ now: () => 0 })
  const { journal, calls } = setup()
  journal.enqueue('start', engine.start())
  journal.enqueue('pause', engine.pause(), 'user')
  journal.enqueue('stop', engine.stop())
  await journal.settled()
  assert.deepEqual(calls.map((call) => call[0]), ['create', 'event', 'event', 'event'])
  assert.deepEqual(calls.slice(1).map((call) => [call[2].sequence, call[2].expected_revision]), [[1, 0], [2, 1], [3, 2]])
  assert.equal(journal.status().state, 'saved')
})

test('slow creation never blocks local start or stop and checkpoints cannot overtake it', async () => {
  let release
  const created = new Promise((resolve) => { release = resolve })
  const { journal, calls } = setup({ create: () => created })
  const engine = createBreathingSession({ now: () => 0 })
  journal.enqueue('start', engine.start())
  journal.enqueue('stop', engine.stop())
  assert.equal(engine.snapshot().status, 'stopped')
  assert.equal(journal.status().state, 'saving')
  assert.equal(calls.length, 0)
  release()
  await journal.settled()
  assert.equal(calls.length, 2)
})

test('failed event is not retried automatically; explicit retry preserves UUID and exact body', async () => {
  const calls = []
  let fail = true
  const { journal } = setup({ append: async (_, body) => {
    calls.push(structuredClone(body))
    if (fail) throw new Error('Storage is unavailable.')
  } })
  const engine = createBreathingSession({ now: () => 0 })
  journal.enqueue('start', engine.start())
  await journal.settled()
  assert.equal(journal.status().state, 'error')
  journal.enqueue('stop', engine.stop())
  await journal.settled()
  assert.equal(calls.length, 1)
  fail = false
  await journal.retry()
  assert.deepEqual(calls[0], calls[1])
  assert.equal(calls[2].kind, 'stop')
  assert.equal(journal.status().state, 'saved')
})

test('creation failures keep the same session and settings for explicit retry', async () => {
  const calls = []
  let fail = true
  const { journal } = setup({ create: async (...args) => {
    calls.push(structuredClone(args))
    if (fail) throw new Error('Unavailable')
  } })
  await journal.settled()
  assert.equal(journal.status().state, 'error')
  fail = false
  await journal.retry()
  assert.deepEqual(calls[0], calls[1])
})

test('independent queues cannot replace each other’s session IDs or sequence', async () => {
  const a = setup()
  const calls = []
  const b = setup({ sessionId: 'session-two', append: async (...args) => calls.push(args) })
  const engine = createBreathingSession({ now: () => 0 })
  a.journal.enqueue('start', engine.start())
  b.journal.enqueue('start', engine.snapshot())
  await Promise.all([a.journal.settled(), b.journal.settled()])
  assert.equal(a.calls[1][1], 'session-one')
  assert.equal(calls[0][0], 'session-two')
  assert.equal(calls[0][1].sequence, 1)
})

test('snapshots copy only the seven fields accepted by the session API', () => {
  const engine = createBreathingSession({ now: () => 0 })
  assert.deepEqual(checkpoint(engine.snapshot()), { active_ms: 0, pause_ms: 0, support_ms: 0,
    setup_ms: 0, cycles_completed: 0, phase: 'inhale', phase_remaining_ms: 4000 })
  assert.equal(Object.keys(checkpoint(engine.start())).length, 7)
})

test('journal pins history generation and discards queued saves after local clear', async () => {
  let release, changes = 0
  const { journal, calls } = setup({ historyEpoch: 7, onChange: () => changes++, create: async (...args) => {
    calls.push(['create', ...args]); await new Promise(resolve => { release = resolve })
  } })
  const engine = createBreathingSession({ now: () => 0 })
  journal.enqueue('start', engine.start()); await Promise.resolve()
  assert.equal(calls[0][3], 7)
  journal.dispose(); const before = changes
  release(); await journal.settled(); await journal.retry()
  journal.enqueue('stop', engine.stop())
  assert.equal(calls.length, 1)
  assert.equal(changes, before)
})

test('every queued event keeps its original history generation on retry', async () => {
  const { journal, calls } = setup({ historyEpoch: 9 })
  journal.enqueue('start', createBreathingSession({ now: () => 0 }).start())
  await journal.settled()
  assert.equal(calls[1][2].history_epoch, 9)
})
