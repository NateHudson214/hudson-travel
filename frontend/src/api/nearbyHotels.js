import { ApiRequestError, requestJson } from './http.js'

export class NearbyHotelsApiError extends ApiRequestError {
  constructor(message) {
    super(message)
    this.name = 'NearbyHotelsApiError'
  }
}

export function searchNearbyHotels(zipCode) {
  const query = new URLSearchParams({ zip_code: zipCode })
  return requestJson(
    `/api/hotels/nearby?${query}`,
    { method: 'GET' },
    NearbyHotelsApiError,
    'Nearby hotels could not be loaded. Please try again.',
  )
}
