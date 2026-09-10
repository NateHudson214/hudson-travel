import assert from 'node:assert/strict'
import test from 'node:test'

import { TripSearchError, searchTrips } from './trips.js'


test('searchTrips requests the encoded hotel name and returns results', async (context) => {
  const expected = [{ trip_id: 'T001', city: 'Boston' }]
  context.mock.method(globalThis, 'fetch', async (url) => {
    assert.equal(url, '/api/trips?hotel_name=Harbor+Lantern+Hotel')
    return { ok: true, json: async () => expected }
  })

  assert.deepEqual(await searchTrips('Harbor Lantern Hotel'), expected)
})


test('searchTrips exposes the backend error detail', async (context) => {
  context.mock.method(globalThis, 'fetch', async () => ({
    ok: false,
    json: async () => ({ detail: 'Enter a hotel name to search.' }),
  }))

  await assert.rejects(() => searchTrips(''), (error) => {
    assert.ok(error instanceof TripSearchError)
    assert.equal(error.message, 'Enter a hotel name to search.')
    return true
  })
})


test('searchTrips gives a friendly error when a response is not JSON', async (context) => {
  context.mock.method(globalThis, 'fetch', async () => ({
    ok: false,
    json: async () => {
      throw new SyntaxError('Unexpected end of JSON input')
    },
  }))

  await assert.rejects(
    () => searchTrips('Harbor Lantern Hotel'),
    new TripSearchError('Trips could not be loaded. Please try again.'),
  )
})
