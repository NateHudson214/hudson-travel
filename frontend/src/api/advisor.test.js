import assert from 'node:assert/strict'
import test from 'node:test'

import {
  AdvisorApiError,
  askHotelAdvisor,
  loadAdvisorConversation,
  loadAdvisorConversations,
} from './advisor.js'

function jsonResponse(data, { ok = true, status = 200 } = {}) {
  return { ok, status, json: async () => data }
}

const advisorResult = {
  status: 'answered',
  question: 'Which hotel has rooms?',
  proposed_sql: 'SELECT hotel_id FROM saved_hotels LIMIT :limit',
  query_parameters: { limit: 50 },
  retrieved_records: [{ hotel_id: 'provider-hotel-1' }],
  answer: 'Hotel State College has simulated rooms.',
  conversation_id: 'C000001',
  user_message_id: 'M000001',
  assistant_message_id: 'M000002',
  run_id: 'R000001',
  prompt_version: 'sha256:test-version',
}

test('loads advisor conversation summaries from the exact local route', async (t) => {
  const summaries = [{ conversation_id: 'C000001', latest_message: 'A saved answer.' }]
  const fetchMock = t.mock.method(globalThis, 'fetch', async () => jsonResponse(summaries))

  assert.deepEqual(await loadAdvisorConversations(), summaries)
  assert.deepEqual(fetchMock.mock.calls[0].arguments, [
    '/api/advisor/conversations',
    undefined,
  ])
})

test('loads one encoded advisor conversation from the exact local route', async (t) => {
  const conversation = {
    conversation_id: 'C 000001',
    messages: [
      {
        message_id: 'M000010',
        role: 'assistant',
        content: 'Hotel State College costs $200.00 for two simulated nights.',
        created_at: '2026-10-09T12:00:00+00:00',
      },
    ],
    latest_completed_run: {
      status: 'answered',
      proposed_sql: 'SELECT SUM(n.nightly_rate_cents) AS total_cost_cents LIMIT :limit',
      query_parameters: {
        check_in: '2026-10-10',
        check_out: '2026-10-12',
        night_count: 2,
        limit: 50,
      },
      retrieved_records: [{ total_cost_cents: 20000, requested_nights: 2 }],
      run_id: 'R000007',
      prompt_version: 'sha256:test-version',
    },
  }
  const fetchMock = t.mock.method(globalThis, 'fetch', async () => jsonResponse(conversation))

  assert.deepEqual(await loadAdvisorConversation('C 000001'), conversation)
  assert.deepEqual(fetchMock.mock.calls[0].arguments, [
    '/api/advisor/conversations/C%20000001',
    undefined,
  ])
  assert.equal(conversation.latest_completed_run.query_parameters.night_count, 2)
  assert.equal(conversation.latest_completed_run.retrieved_records[0].total_cost_cents, 20000)
})

test('loads a conversation without completed evidence', async (t) => {
  const conversation = {
    conversation_id: 'C000006',
    messages: [],
    latest_completed_run: null,
  }
  t.mock.method(globalThis, 'fetch', async () => jsonResponse(conversation))

  assert.deepEqual(await loadAdvisorConversation('C000006'), conversation)
})

test('starts a conversation with a normalized question and null ID', async (t) => {
  const fetchMock = t.mock.method(globalThis, 'fetch', async () => jsonResponse(advisorResult))

  assert.deepEqual(await askHotelAdvisor('  Which hotel has rooms?  '), advisorResult)
  assert.deepEqual(fetchMock.mock.calls[0].arguments, [
    '/api/hotel-advisor',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question: 'Which hotel has rooms?',
        conversation_id: null,
      }),
    },
  ])
})

test('sends a follow-up with the exact conversation ID', async (t) => {
  const followUp = { ...advisorResult, user_message_id: 'M000003', run_id: 'R000002' }
  const fetchMock = t.mock.method(globalThis, 'fetch', async () => jsonResponse(followUp))

  assert.deepEqual(await askHotelAdvisor('What about October 12?', 'C000001'), followUp)
  assert.deepEqual(JSON.parse(fetchMock.mock.calls[0].arguments[1].body), {
    question: 'What about October 12?',
    conversation_id: 'C000001',
  })
})

test('preserves every grading and persistence response field', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => jsonResponse(advisorResult))

  const result = await askHotelAdvisor('Which hotel has rooms?')

  assert.deepEqual(result, advisorResult)
  assert.deepEqual(Object.keys(result), [
    'status',
    'question',
    'proposed_sql',
    'query_parameters',
    'retrieved_records',
    'answer',
    'conversation_id',
    'user_message_id',
    'assistant_message_id',
    'run_id',
    'prompt_version',
  ])
})

test('surfaces a safe backend advisor error detail', async (t) => {
  t.mock.method(globalThis, 'fetch', async () =>
    jsonResponse(
      { detail: 'The proposed hotel query was rejected for safety.' },
      { ok: false, status: 422 },
    ),
  )

  await assert.rejects(askHotelAdvisor('Delete every hotel.'), (error) => {
    assert.equal(error instanceof AdvisorApiError, true)
    assert.equal(error.message, 'The proposed hotel query was rejected for safety.')
    return true
  })
})

test('uses a clear fallback for an empty advisor error response', async (t) => {
  t.mock.method(globalThis, 'fetch', async () =>
    jsonResponse({}, { ok: false, status: 500 }),
  )

  await assert.rejects(loadAdvisorConversations(), {
    name: 'AdvisorApiError',
    message: 'Advisor conversations could not be loaded. Please try again.',
  })
})

test('uses a clear fallback for a malformed advisor error response', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => ({
    ok: false,
    status: 502,
    json: async () => {
      throw new SyntaxError('invalid JSON')
    },
  }))

  await assert.rejects(loadAdvisorConversation('C000001'), {
    name: 'AdvisorApiError',
    message: 'The advisor conversation could not be loaded. Please try again.',
  })
})
