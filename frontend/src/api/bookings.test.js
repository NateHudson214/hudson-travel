import assert from 'node:assert/strict'
import test from 'node:test'

import {
  BookingApiError,
  cancelBooking,
  createBooking,
  deleteBooking,
  loadBookings,
  loadUsers,
} from './bookings.js'

function jsonResponse(data, { ok = true, status = 200 } = {}) {
  return { ok, status, json: async () => data }
}

test('loads users from the users endpoint', async (t) => {
  const users = [{ user_id: 'U006', display_name: 'Taylor Reed' }]
  const fetchMock = t.mock.method(globalThis, 'fetch', async () => jsonResponse(users))

  assert.deepEqual(await loadUsers(), users)
  assert.deepEqual(fetchMock.mock.calls[0].arguments, ['/api/users', undefined])
})

test('loads joined booking history', async (t) => {
  const bookings = [{ booking_id: 'B001', hotel_name: 'Harbor Lantern Hotel' }]
  const fetchMock = t.mock.method(globalThis, 'fetch', async () => jsonResponse(bookings))

  assert.deepEqual(await loadBookings(), bookings)
  assert.deepEqual(fetchMock.mock.calls[0].arguments, ['/api/bookings', undefined])
})

test('creates a booking with the exact JSON body', async (t) => {
  const created = { booking_id: 'B007', user_id: 'U006', trip_id: 'T001' }
  const fetchMock = t.mock.method(globalThis, 'fetch', async () => jsonResponse(created, { status: 201 }))

  assert.deepEqual(await createBooking('U006', 'T001'), created)
  assert.deepEqual(fetchMock.mock.calls[0].arguments, [
    '/api/bookings',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: 'U006', trip_id: 'T001' }),
    },
  ])
})

test('cancels a booking with PATCH and cancelled status', async (t) => {
  const cancelled = { booking_id: 'B007', status: 'cancelled' }
  const fetchMock = t.mock.method(globalThis, 'fetch', async () => jsonResponse(cancelled))

  assert.deepEqual(await cancelBooking('B007'), cancelled)
  assert.deepEqual(fetchMock.mock.calls[0].arguments, [
    '/api/bookings/B007',
    {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'cancelled' }),
    },
  ])
})

test('deletes a booking with DELETE and accepts an empty 204 response', async (t) => {
  const fetchMock = t.mock.method(globalThis, 'fetch', async () => ({ ok: true, status: 204 }))

  assert.equal(await deleteBooking('B007'), null)
  assert.deepEqual(fetchMock.mock.calls[0].arguments, [
    '/api/bookings/B007',
    { method: 'DELETE' },
  ])
})

test('surfaces HTTP error details', async (t) => {
  t.mock.method(globalThis, 'fetch', async () =>
    jsonResponse({ detail: 'Trip T999 was not found.' }, { ok: false, status: 404 }),
  )

  await assert.rejects(createBooking('U006', 'T999'), (error) => {
    assert.equal(error instanceof BookingApiError, true)
    assert.equal(error.message, 'Trip T999 was not found.')
    return true
  })
})

test('uses a clear fallback for an empty error response', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => jsonResponse({}, { ok: false, status: 500 }))

  await assert.rejects(loadBookings(), {
    name: 'BookingApiError',
    message: 'Booking history could not be loaded. Please try again.',
  })
})

test('uses a clear fallback for a malformed error response', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => ({
    ok: false,
    status: 500,
    json: async () => {
      throw new SyntaxError('invalid JSON')
    },
  }))

  await assert.rejects(loadUsers(), {
    name: 'BookingApiError',
    message: 'Travelers could not be loaded. Please try again.',
  })
})
