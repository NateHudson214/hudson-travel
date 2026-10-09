import { ApiRequestError, requestJson } from './http.js'

export class AdvisorApiError extends ApiRequestError {
  constructor(message) {
    super(message)
    this.name = 'AdvisorApiError'
  }
}

export function loadAdvisorConversations() {
  return requestJson(
    '/api/advisor/conversations',
    undefined,
    AdvisorApiError,
    'Advisor conversations could not be loaded. Please try again.',
  )
}

export function loadAdvisorConversation(conversationId) {
  return requestJson(
    `/api/advisor/conversations/${encodeURIComponent(conversationId)}`,
    undefined,
    AdvisorApiError,
    'The advisor conversation could not be loaded. Please try again.',
  )
}

export function askHotelAdvisor(question, conversationId = null) {
  return requestJson(
    '/api/hotel-advisor',
    {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        question: question.trim(),
        conversation_id: conversationId || null,
      }),
    },
    AdvisorApiError,
    'The hotel advisor could not answer. Please try again.',
  )
}
