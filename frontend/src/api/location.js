import { ApiRequestError, requestJson } from './http.js'

export class LocationApiError extends ApiRequestError {
  constructor(message) {
    super(message)
    this.name = 'LocationApiError'
  }
}

export function lookupDemoZipLocation() {
  return requestJson(
    '/api/demo/zip-location',
    { method: 'GET' },
    LocationApiError,
    'ZIP 16802 could not be looked up. Please try again.',
  )
}

export function lookupZipLocation(zipCode) {
  const query = new URLSearchParams({ zip_code: zipCode })
  return requestJson(
    `/api/zip-location?${query}`,
    { method: 'GET' },
    LocationApiError,
    'The ZIP code could not be looked up. Please try again.',
  )
}
