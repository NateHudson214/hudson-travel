export class TripSearchError extends Error {}

export async function searchTrips(hotelName) {
  const query = new URLSearchParams({ hotel_name: hotelName })
  const response = await fetch(`/api/trips?${query}`)
  let data

  try {
    data = await response.json()
  } catch {
    throw new TripSearchError('Trips could not be loaded. Please try again.')
  }

  if (!response.ok) {
    throw new TripSearchError(data.detail || 'Trips could not be loaded. Please try again.')
  }

  return data
}
