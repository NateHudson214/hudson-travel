import { ApiRequestError, requestJson } from './http.js'

export class TripSearchError extends ApiRequestError {
  constructor(message) {
    super(message)
    this.name = 'TripSearchError'
  }
}

export async function searchTrips(hotelName) {
  const query = new URLSearchParams({ hotel_name: hotelName })
  return requestJson(
    `/api/trips?${query}`,
    undefined,
    TripSearchError,
    'Trips could not be loaded. Please try again.',
  )
}
