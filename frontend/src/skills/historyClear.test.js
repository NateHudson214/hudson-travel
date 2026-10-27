import assert from 'node:assert/strict'
import test from 'node:test'
import { createHistoryClear } from './historyClear.js'

test('opening/cancelling confirmation never deletes; only explicit confirm dispatches', async () => {
  let state, calls = [], intents = 0, complete
  const controller = createHistoryClear({ load: async () => ({ history_epoch: 3 }), makeId: () => 'clear-id',
    clear: async body => { calls.push(body); return { history_epoch: 4 } }, onIntent: () => intents++,
    onCleared: value => { complete = value }, onChange: value => { state = value } })
  await controller.confirm()
  await controller.prepare()
  assert.equal(calls.length, 0)
  assert.equal(state.ready, true)
  await controller.confirm(); await controller.confirm()
  assert.deepEqual(calls, [{ request_id: 'clear-id', expected_epoch: 3, confirm: true }])
  assert.equal(intents, 1)
  assert.equal(state.success, true)
  assert.equal(complete.history_epoch, 4)
})

test('failed clear retries the exact generation and ID without reloading or a second local discard', async () => {
  let calls = [], loads = 0, intents = 0
  const controller = createHistoryClear({ load: async () => { loads++; return { history_epoch: 5 } },
    onIntent: () => intents++, clear: async body => { calls.push(body); if (calls.length === 1) throw new Error('lost response'); return { history_epoch: 6 } } })
  await controller.prepare(); await controller.confirm()
  await controller.prepare() // Reopening unknown-outcome confirmation retains original request.
  await controller.confirm()
  assert.equal(loads, 1)
  assert.strictEqual(calls[0], calls[1])
  assert.equal(intents, 1)
})

test('loading failure and disposal prevent deletion and ignore late responses', async () => {
  let calls = 0, state, resolve, complete = 0
  const failed = createHistoryClear({ load: async () => { throw new Error('unavailable') }, clear: async () => calls++ })
  await failed.prepare(); await failed.confirm()
  assert.equal(calls, 0)
  const controller = createHistoryClear({ load: async () => ({ history_epoch: 0 }), clear: () => new Promise(r => { resolve = r }),
    onChange: value => { state = value }, onCleared: () => complete++ })
  await controller.prepare()
  const pending = controller.confirm()
  assert.equal(state.busy, true)
  controller.dispose(); const lastState = state
  resolve({ history_epoch: 1 }); await pending
  assert.equal(complete, 0)
  assert.strictEqual(state, lastState)
})
