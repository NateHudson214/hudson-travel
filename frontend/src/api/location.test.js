import assert from 'node:assert/strict'
import test from 'node:test'

import { LocationApiError, lookupDemoZipLocation, lookupZipLocation } from './location.js'

function jsonResponse(data, { ok = true, status = 200 } = {}) {
  return { ok, status, json: async () => data }
}

test('looks up the demonstration ZIP through the exact local GET route', async (t) => {
  const location = {
    postcode: '16802',
    country_code: 'us',
    latitude: 40.803167822,
    longitude: -77.861384958,
    locality: 'State College',
  }
  const fetchMock = t.mock.method(globalThis, 'fetch', async () => jsonResponse(location))

  assert.deepEqual(await lookupDemoZipLocation(), location)
  assert.deepEqual(fetchMock.mock.calls[0].arguments, [
    '/api/demo/zip-location',
    { method: 'GET' },
  ])
})

test('looks up an entered ZIP through the encoded dynamic local GET route', async (t) => {
  const location = {
    postcode: '16802',
    country_code: 'us',
    latitude: 40.803167822,
    longitude: -77.861384958,
    locality: 'State College',
  }
  const fetchMock = t.mock.method(globalThis, 'fetch', async () => jsonResponse(location))

  assert.deepEqual(await lookupZipLocation(' 16802 '), location)
  assert.deepEqual(fetchMock.mock.calls[0].arguments, [
    '/api/zip-location?zip_code=+16802+',
    { method: 'GET' },
  ])
})

test('preserves a leading zero in the dynamic ZIP request', async (t) => {
  const location = { postcode: '02113', country_code: 'us' }
  const fetchMock = t.mock.method(globalThis, 'fetch', async () => jsonResponse(location))

  assert.deepEqual(await lookupZipLocation('02113'), location)
  assert.deepEqual(fetchMock.mock.calls[0].arguments, [
    '/api/zip-location?zip_code=02113',
    { method: 'GET' },
  ])
})

test('dynamic lookup surfaces a safe backend error detail', async (t) => {
  t.mock.method(globalThis, 'fetch', async () =>
    jsonResponse(
      { detail: 'The location service is temporarily unavailable.' },
      { ok: false, status: 502 },
    ),
  )

  await assert.rejects(lookupZipLocation('16802'), {
    name: 'LocationApiError',
    message: 'The location service is temporarily unavailable.',
  })
})

test('dynamic lookup uses a clear fallback for an empty error response', async (t) => {
  t.mock.method(globalThis, 'fetch', async () =>
    jsonResponse({}, { ok: false, status: 500 }),
  )

  await assert.rejects(lookupZipLocation('16802'), {
    name: 'LocationApiError',
    message: 'The ZIP code could not be looked up. Please try again.',
  })
})

test('dynamic lookup uses a clear fallback for a malformed error response', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => ({
    ok: false,
    status: 500,
    json: async () => {
      throw new SyntaxError('invalid JSON')
    },
  }))

  await assert.rejects(lookupZipLocation('16802'), (error) => {
    assert.equal(error instanceof LocationApiError, true)
    assert.equal(error.message, 'The ZIP code could not be looked up. Please try again.')
    return true
  })
})
