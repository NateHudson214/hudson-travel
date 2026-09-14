export class ApiRequestError extends Error {
  constructor(message) {
    super(message)
    this.name = 'ApiRequestError'
  }
}

export async function requestJson(url, options, ErrorType, fallbackMessage) {
  let response

  try {
    response = await fetch(url, options)
  } catch {
    throw new ErrorType(fallbackMessage)
  }

  if (response.status === 204) {
    return null
  }

  let data

  try {
    data = await response.json()
  } catch {
    throw new ErrorType(fallbackMessage)
  }

  if (!response.ok) {
    const detail = typeof data?.detail === 'string' ? data.detail : fallbackMessage
    throw new ErrorType(detail)
  }

  return data
}
