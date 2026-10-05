import assert from 'node:assert/strict'
import test from 'node:test'

import {
  SavedHotelsApiError,
  loadSavedHotelIds,
  removeSavedHotel,
  saveHotelLocally,
  searchSavedHotels,
} from './savedHotels.js'

function jsonResponse(data, { ok = true, status = 200 } = {}) {
  return { ok, status, json: async () => data }
}

const location = {
  postcode: '16802',
  country_code: 'us',
  latitude: 40.803167822,
  longitude: -77.861384958,
  locality: 'State College',
}

const hotel = {
  place_id: 'provider/place 1',
  name: 'Example Hotel',
  formatted_address: null,
  latitude: 40.8,
  longitude: -77.86,
  distance_meters: 420,
}

test('loads saved provider IDs from the exact status route', async (t) => {
  const result = { place_ids: ['provider-place-1'] }
  const fetchMock = t.mock.method(globalThis, 'fetch', async () => jsonResponse(result))

  assert.deepEqual(await loadSavedHotelIds(), result)
  assert.deepEqual(fetchMock.mock.calls[0].arguments, [
    '/api/saved-hotels/ids',
    { method: 'GET' },
  ])
})

test('requests the exact encoded local-first ZIP route', async (t) => {
  const result = { searched_zip_code: '02113', location: null, hotels: [] }
  const fetchMock = t.mock.method(globalThis, 'fetch', async () => jsonResponse(result))

  assert.deepEqual(await searchSavedHotels('02113'), result)
  assert.deepEqual(fetchMock.mock.calls[0].arguments, [
    '/api/saved-hotels?zip_code=02113',
    { method: 'GET' },
  ])
})

test('saves only the provider hotel and current ZIP location context', async (t) => {
  const result = { searched_zip_code: '16802', location, hotel: { ...hotel, nights: [] } }
  const fetchMock = t.mock.method(globalThis, 'fetch', async () => jsonResponse(result, { status: 201 }))

  assert.deepEqual(await saveHotelLocally(hotel, '16802', location), result)
  assert.deepEqual(fetchMock.mock.calls[0].arguments, [
    '/api/saved-hotels',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        zip_code: '16802',
        location,
        hotel: {
          place_id: 'provider/place 1',
          name: 'Example Hotel',
          formatted_address: null,
          latitude: 40.8,
          longitude: -77.86,
        },
      }),
    },
  ])
})

test('deletes the encoded provider ID and accepts an empty 204 response', async (t) => {
  const fetchMock = t.mock.method(globalThis, 'fetch', async () => ({ ok: true, status: 204 }))

  assert.equal(await removeSavedHotel('provider/place 1'), null)
  assert.deepEqual(fetchMock.mock.calls[0].arguments, [
    '/api/saved-hotels/provider%2Fplace%201',
    { method: 'DELETE' },
  ])
})

test('surfaces safe local-storage backend details', async (t) => {
  t.mock.method(globalThis, 'fetch', async () =>
    jsonResponse(
      { detail: 'Local hotel storage is temporarily unavailable.' },
      { ok: false, status: 500 },
    ),
  )

  await assert.rejects(searchSavedHotels('16802'), {
    name: 'SavedHotelsApiError',
    message: 'Local hotel storage is temporarily unavailable.',
  })
})

test('uses a clear saved-status fallback for a malformed response', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => ({
    ok: false,
    status: 500,
    json: async () => {
      throw new SyntaxError('invalid JSON')
    },
  }))

  await assert.rejects(loadSavedHotelIds(), (error) => {
    assert.equal(error instanceof SavedHotelsApiError, true)
    assert.equal(error.message, 'Saved hotel status could not be loaded. Please try again.')
    return true
  })
})
