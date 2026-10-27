import assert from 'node:assert/strict'
import test from 'node:test'
import { createDisplayPreferences, DEFAULT_DISPLAY } from './preferences.js'
import { useStaticCue } from './presentation.js'
const result = (last_setup = null, revision = 0) => ({ preferences: { last_setup, revision } })
const saved = { simpler_view: true, motion_mode: 'gentle' }

test('loading/saving never applies choices; use last setup is explicit and reduced motion wins', async () => {
  let state, applies = []
  const controller = createDisplayPreferences({ load: async () => result(saved, 1), change: async body => result(body.display_settings, 2),
    onChange: value => { state = value }, apply: value => applies.push(value) })
  await controller.refresh()
  assert.deepEqual(applies, [])
  assert.deepEqual(state.lastSetup, saved)
  controller.useLast()
  assert.deepEqual(applies, [saved])
  assert.equal(useStaticCue(applies[0].motion_mode, true), true)
  await controller.save({ simpler_view: false, motion_mode: 'static' })
  assert.equal(applies.length, 1)
})

test('a delayed read never overwrites current settings; disposal ignores late notifications', async () => {
  let resolve, changes = 0, applies = 0
  const controller = createDisplayPreferences({ load: () => new Promise(r => { resolve = r }), apply: () => applies++, onChange: () => changes++ })
  const pending = controller.refresh()
  await Promise.resolve()
  controller.dispose()
  const before = changes
  resolve(result(saved, 1)); await pending
  controller.useLast()
  assert.equal(changes, before)
  assert.equal(applies, 0)
})

test('reset is local immediately, serializes after an in-flight save and uses fresh revision', async () => {
  let resolveSave, state, stored = result(null, 0), calls = [], applies = []
  const controller = createDisplayPreferences({ load: async () => stored, onChange: value => { state = value }, apply: value => applies.push(value),
    change: body => { calls.push(body); if (body.action === 'save') return new Promise(r => { resolveSave = r }); return Promise.resolve(result(null, 2)) } })
  await controller.refresh()
  const saving = controller.save(saved)
  await Promise.resolve()
  const reset = controller.reset()
  assert.deepEqual(applies, [DEFAULT_DISPLAY])
  assert.equal(calls.length, 1)
  stored = result(saved, 1); resolveSave(stored)
  await saving; await reset
  assert.deepEqual(calls.map(c => c.action), ['save', 'reset'])
  assert.equal(calls[1].expected_revision, 1)
  assert.equal(state.lastSetup, null)
  controller.useLast()
  assert.equal(applies.length, 1)
})

test('failed writes require explicit exact retry', async () => {
  let state, stored = result(), count = 0, calls = []
  const controller = createDisplayPreferences({ load: async () => stored, onChange: value => { state = value }, change: async body => {
    calls.push(body); count++
    if (count === 1) throw new Error('Offline')
    stored = result(body.action === 'reset' ? null : body.display_settings, count)
    return stored
  } })
  await controller.refresh(); await controller.save(saved)
  assert.equal(count, 1); assert.equal(state.canRetry, true)
  await controller.retry()
  assert.strictEqual(calls[0], calls[1])
  await controller.reset()
  assert.equal(state.canRetry, false); assert.equal(state.lastSetup, null)
  await controller.retry()
  assert.equal(count, 3)
})

test('storage failure cannot block a local reset or apply saved choices', async () => {
  let applied, state
  const controller = createDisplayPreferences({ load: async () => { throw new Error('Unavailable') }, apply: value => { applied = value }, onChange: value => { state = value } })
  await controller.refresh(); await controller.reset()
  assert.deepEqual(applied, DEFAULT_DISPLAY)
  assert.equal(state.error, 'Unavailable')
  assert.equal(state.notice, '')
  assert.equal(state.canSave, false)
})


test('reset abandons a failed save retry and cannot resend it later', async () => {
  let calls = [], state
  const controller = createDisplayPreferences({ load: async () => result(), onChange: value => { state = value },
    change: async body => { calls.push(body); if (body.action === 'save') throw new Error('Offline'); return result(null, 1) } })
  await controller.refresh(); await controller.save(saved)
  assert.equal(state.canRetry, true)
  await controller.reset(); await controller.retry()
  assert.deepEqual(calls.map(c => c.action), ['save', 'reset'])
  assert.equal(state.lastSetup, null)
  assert.equal(state.canRetry, false)
})
