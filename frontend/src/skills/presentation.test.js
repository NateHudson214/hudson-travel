import assert from 'node:assert/strict'
import test from 'node:test'
import { useStaticCue } from './presentation.js'
import { CRISIS_RESOURCES } from './crisisResources.js'

test('reduced motion always produces a stationary cue, including an earlier gentle choice', () => {
  for (const mode of ['system', 'static', 'gentle']) assert.equal(useStaticCue(mode, true), true)
  assert.equal(useStaticCue('static', false), true)
  assert.equal(useStaticCue('system', false), false)
  assert.equal(useStaticCue('gentle', false), false)
})

test('crisis contacts are independently bundled, geographically labeled, and immutable', () => {
  assert.equal(CRISIS_RESOURCES.region, 'United States')
  assert.equal(CRISIS_RESOURCES.reviewed, '2026-10-26')
  assert.match(CRISIS_RESOURCES.call, /^tel:988\?/)
  assert.match(CRISIS_RESOURCES.text, /^sms:988\?/)
  assert.match(CRISIS_RESOURCES.chat, /^https:\/\/988lifeline.org\/chat\//)
  assert.throws(() => { CRISIS_RESOURCES.region = 'Anywhere' }, TypeError)
})
