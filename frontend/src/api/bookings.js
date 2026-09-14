import { ApiRequestError, requestJson } from './http.js'

export class BookingApiError extends ApiRequestError {
  constructor(message) {
    super(message)
    this.name = 'BookingApiError'
  }
}

export function loadUsers() {
  return requestJson(
    '/api/users',
    undefined,
    BookingApiError,
    'Travelers could not be loaded. Please try again.',
  )
}

export function loadBookings() {
  return requestJson(
    '/api/bookings',
    undefined,
    BookingApiError,
    'Booking history could not be loaded. Please try again.',
  )
}

export function createBooking(userId, tripId) {
  return requestJson(
    '/api/bookings',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ user_id: userId, trip_id: tripId }),
    },
    BookingApiError,
    'Booking could not be created. Please try again.',
  )
}

export function cancelBooking(bookingId) {
  return requestJson(
    `/api/bookings/${encodeURIComponent(bookingId)}`,
    {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ status: 'cancelled' }),
    },
    BookingApiError,
    'Booking could not be cancelled. Please try again.',
  )
}

export function deleteBooking(bookingId) {
  return requestJson(
    `/api/bookings/${encodeURIComponent(bookingId)}`,
    { method: 'DELETE' },
    BookingApiError,
    'Booking could not be deleted. Please try again.',
  )
}
