import { ApiRequestError, requestJson } from './http.js'

export class SavedHotelsApiError extends ApiRequestError {
  constructor(message) {
    super(message)
    this.name = 'SavedHotelsApiError'
  }
}

export function loadSavedHotelIds() {
  return requestJson(
    '/api/saved-hotels/ids',
    { method: 'GET' },
    SavedHotelsApiError,
    'Saved hotel status could not be loaded. Please try again.',
  )
}

export function searchSavedHotels(zipCode) {
  const query = new URLSearchParams({ zip_code: zipCode })
  return requestJson(
    `/api/saved-hotels?${query}`,
    { method: 'GET' },
    SavedHotelsApiError,
    'Saved hotels could not be loaded. Please try again.',
  )
}

export function saveHotelLocally(hotel, zipCode, location) {
  return requestJson(
    '/api/saved-hotels',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        zip_code: zipCode,
        location: {
          postcode: location.postcode,
          country_code: location.country_code,
          latitude: location.latitude,
          longitude: location.longitude,
          locality: location.locality ?? null,
        },
        hotel: {
          place_id: hotel.place_id,
          name: hotel.name ?? null,
          formatted_address: hotel.formatted_address ?? null,
          latitude: hotel.latitude,
          longitude: hotel.longitude,
        },
      }),
    },
    SavedHotelsApiError,
    'The hotel could not be saved locally. Please try again.',
  )
}

export function removeSavedHotel(placeId) {
  return requestJson(
    `/api/saved-hotels/${encodeURIComponent(placeId)}`,
    { method: 'DELETE' },
    SavedHotelsApiError,
    'The saved hotel could not be removed. Please try again.',
  )
}
