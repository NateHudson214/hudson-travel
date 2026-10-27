import assert from 'node:assert/strict'
import test from 'node:test'

import { BREATHING_SKILL, createBreathingSession, MAX_CUE_DELAY_MS } from './breathing.js'

function clockSession() {
  let time = 0
  const session = createBreathingSession({ now: () => time })
  return { session, advance: (ms) => { time += ms }, setTime: (ms) => { time = ms } }
}

function finish(session, advance) {
  for (let cycle = 0; cycle < 6; cycle += 1) {
    advance(4000)
    assert.equal(session.tick().phase, 'exhale')
    advance(6000)
    session.tick()
  }
}

test('setup has no breathing progress and start does not require an input or request', () => {
  const { session, advance } = clockSession()
  advance(12000)
  assert.equal(session.tick().status, 'ready')
  assert.equal(session.snapshot().activeMs, 0)
  const started = session.start()
  assert.equal(started.setupMs, 12000)
  assert.equal(started.phase, 'inhale')
  assert.equal(started.phaseRemainingMs, 4000)
})

test('all twelve ordered phases complete six 4/6 cycles in 60000 simulated active ms', () => {
  const { session, advance } = clockSession()
  session.start()
  const phases = []
  for (let cycle = 1; cycle <= 6; cycle += 1) {
    assert.equal(session.snapshot().cycle, cycle)
    phases.push(session.snapshot().phase)
    advance(4000)
    phases.push(session.tick().phase)
    advance(6000)
    session.tick()
  }
  assert.deepEqual(phases, Array.from({ length: 6 }, () => ['inhale', 'exhale']).flat())
  assert.equal(session.snapshot().status, 'completed')
  assert.equal(session.snapshot().cyclesCompleted, 6)
  assert.equal(session.snapshot().activeMs, 60000)
  assert.equal(session.snapshot().withinDurationLimit, true)
  advance(50000)
  assert.equal(session.tick().activeMs, 60000)
  assert.equal(session.start().status, 'completed')
})

test('repeated frame samples do not accumulate interval drift', () => {
  const { session, advance } = clockSession()
  session.start()
  for (let sample = 0; sample < 600; sample += 1) {
    advance(100)
    session.tick()
  }
  assert.equal(session.snapshot().activeMs, 60000)
  assert.equal(session.snapshot().cyclesCompleted, 6)
})

test('pause freezes the remaining exhale and resume excludes user pause time', () => {
  const { session, advance } = clockSession()
  session.start()
  advance(4000)
  session.tick()
  advance(1000)
  assert.equal(session.pause().phaseRemainingMs, 5000)
  advance(15000)
  assert.equal(session.tick().phaseRemainingMs, 5000)
  assert.equal(session.resume().pauseMs, 15000)
  advance(5000)
  assert.equal(session.tick().cyclesCompleted, 1)
  assert.equal(session.snapshot().activeMs, 10000)
})

test('support access blocks start, pauses active pacing and never resumes on close', () => {
  const { session, advance } = clockSession()
  session.openSupport()
  assert.equal(session.start().status, 'ready')
  session.closeSupport()
  session.start()
  advance(1000)
  session.openSupport()
  advance(8000)
  assert.equal(session.resume().status, 'paused')
  const closed = session.closeSupport()
  assert.equal(closed.status, 'paused')
  assert.equal(closed.supportMs, 8000)
  assert.equal(closed.activeMs, 1000)
  advance(2000)
  const resumed = session.resume()
  assert.equal(resumed.pauseMs, 2000)
  assert.equal(resumed.phaseRemainingMs, 3000)
})

test('nested user pause and support time use disjoint duration categories', () => {
  const { session, advance } = clockSession()
  session.start()
  session.pause()
  advance(1000)
  session.openSupport()
  advance(4000)
  session.openSupport()
  advance(3000)
  session.closeSupport()
  advance(2000)
  const state = session.resume()
  assert.equal(state.pauseMs, 3000)
  assert.equal(state.supportMs, 7000)
  assert.equal(state.activeMs, 0)
})

test('hidden-tab pause remains paused until explicitly resumed', () => {
  const { session, advance } = clockSession()
  session.start()
  advance(1500)
  assert.equal(session.pause('hidden').pauseReason, 'hidden')
  advance(100000)
  assert.equal(session.tick().status, 'paused')
  assert.equal(session.snapshot().activeMs, 1500)
})

test('a delayed callback interrupts instead of skipping an unpresented phase', () => {
  const { session, advance } = clockSession()
  session.start()
  advance(4000 + MAX_CUE_DELAY_MS + 1)
  const interrupted = session.tick()
  assert.equal(interrupted.status, 'paused')
  assert.equal(interrupted.pauseReason, 'timing')
  assert.equal(interrupted.phase, 'inhale')
  assert.equal(interrupted.phaseRemainingMs, 4000)
  assert.equal(interrupted.activeMs, 4251)
  advance(6000)
  session.resume()
  advance(4000)
  assert.equal(session.tick().phase, 'exhale')
})

test('completion records final callback delay instead of clamping to planned time', () => {
  const { session, advance } = clockSession()
  session.start()
  for (let cycle = 0; cycle < 5; cycle += 1) {
    advance(4000)
    session.tick()
    advance(6000)
    session.tick()
  }
  advance(4000)
  session.tick()
  advance(6100)
  const state = session.tick()
  assert.equal(state.status, 'completed')
  assert.equal(state.activeMs, 60100)
})

test('interruptions over the duration limit remain observable without forced exit', () => {
  const { session, advance } = clockSession()
  session.start()
  advance(35000)
  assert.equal(session.tick().status, 'paused')
  session.resume()
  finish(session, advance)
  assert.equal(session.snapshot().activeMs, 95000)
  assert.equal(session.snapshot().status, 'completed')
  assert.equal(session.snapshot().withinDurationLimit, false)
})

test('stop is immediate, idempotent, and terminal from running or paused states', () => {
  for (const shouldPause of [false, true]) {
    const { session, advance } = clockSession()
    session.start()
    advance(700)
    if (shouldPause) session.pause()
    assert.equal(session.stop().status, 'stopped')
    advance(90000)
    assert.equal(session.tick().status, 'stopped')
    assert.equal(session.start().status, 'stopped')
    assert.equal(session.resume().status, 'stopped')
    assert.equal(session.stop().activeMs, 700)
  }
})

test('snapshots and application configuration cannot be externally changed', () => {
  const { session } = clockSession()
  assert.throws(() => { session.snapshot().phase = 'exhale' }, TypeError)
  assert.throws(() => { BREATHING_SKILL.inhaleMs = 1 }, TypeError)
  assert.equal(session.snapshot().phase, 'inhale')
})

test('invalid or backward clocks are rejected without corrupting state', () => {
  assert.throws(() => createBreathingSession({ now: () => NaN }), RangeError)
  const { session, advance, setTime } = clockSession()
  session.start()
  advance(200)
  session.tick()
  setTime(100)
  assert.throws(() => session.tick(), RangeError)
  assert.equal(session.snapshot().activeMs, 200)
  setTime(Infinity)
  assert.throws(() => session.tick(), RangeError)
})
