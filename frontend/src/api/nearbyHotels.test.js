import assert from 'node:assert/strict'
import test from 'node:test'

import { NearbyHotelsApiError, searchNearbyHotels } from './nearbyHotels.js'

function jsonResponse(data, { ok = true, status = 200 } = {}) {
  return { ok, status, json: async () => data }
}

const successfulSearch = {
  location: {
    postcode: '16802',
    country_code: 'us',
    latitude: 40.803167822,
    longitude: -77.861384958,
    locality: 'State College',
  },
  radius_meters: 5000,
  result_limit: 20,
  hotels: [
    {
      place_id: 'provider-place-1',
      name: 'Example Hotel',
      formatted_address: '100 Example Street',
      latitude: 40.8,
      longitude: -77.86,
      distance_meters: 420,
    },
  ],
}

test('requests the exact encoded local nearby-hotel GET route', async (t) => {
  const fetchMock = t.mock.method(globalThis, 'fetch', async () =>
    jsonResponse(successfulSearch),
  )

  assert.deepEqual(await searchNearbyHotels(' 16802 '), successfulSearch)
  assert.deepEqual(fetchMock.mock.calls[0].arguments, [
    '/api/hotels/nearby?zip_code=+16802+',
    { method: 'GET' },
  ])
})

test('preserves a leading-zero ZIP in the nearby-hotel request', async (t) => {
  const leadingZeroResult = {
    ...successfulSearch,
    location: { ...successfulSearch.location, postcode: '02113' },
  }
  const fetchMock = t.mock.method(globalThis, 'fetch', async () =>
    jsonResponse(leadingZeroResult),
  )

  assert.deepEqual(await searchNearbyHotels('02113'), leadingZeroResult)
  assert.deepEqual(fetchMock.mock.calls[0].arguments, [
    '/api/hotels/nearby?zip_code=02113',
    { method: 'GET' },
  ])
})

test('returns a successful empty nearby-hotel result', async (t) => {
  const emptyResult = { ...successfulSearch, hotels: [] }
  t.mock.method(globalThis, 'fetch', async () => jsonResponse(emptyResult))

  const result = await searchNearbyHotels('16802')

  assert.deepEqual(result, emptyResult)
  assert.deepEqual(result.hotels, [])
})

test('surfaces safe nearby-hotel backend error details', async (t) => {
  t.mock.method(globalThis, 'fetch', async () =>
    jsonResponse(
      { detail: 'ZIP 00000 could not be resolved.' },
      { ok: false, status: 404 },
    ),
  )

  await assert.rejects(searchNearbyHotels('00000'), {
    name: 'NearbyHotelsApiError',
    message: 'ZIP 00000 could not be resolved.',
  })
})

test('uses a clear fallback for an empty nearby-hotel error response', async (t) => {
  t.mock.method(globalThis, 'fetch', async () =>
    jsonResponse({}, { ok: false, status: 502 }),
  )

  await assert.rejects(searchNearbyHotels('16802'), {
    name: 'NearbyHotelsApiError',
    message: 'Nearby hotels could not be loaded. Please try again.',
  })
})

test('uses a clear fallback for a malformed nearby-hotel error response', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => ({
    ok: false,
    status: 502,
    json: async () => {
      throw new SyntaxError('invalid JSON')
    },
  }))

  await assert.rejects(searchNearbyHotels('16802'), (error) => {
    assert.equal(error instanceof NearbyHotelsApiError, true)
    assert.equal(error.message, 'Nearby hotels could not be loaded. Please try again.')
    return true
  })
})
