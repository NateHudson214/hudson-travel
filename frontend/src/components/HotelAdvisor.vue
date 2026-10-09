<script setup>
import { computed, onMounted, ref } from 'vue'

import {
  askHotelAdvisor,
  loadAdvisorConversation,
  loadAdvisorConversations,
} from '../api/advisor.js'

const question = ref('')
const conversations = ref([])
const activeConversationId = ref('')
const messages = ref([])
const evidence = ref(null)
const error = ref('')
const historyError = ref('')
const isAsking = ref(false)
const isHistoryLoading = ref(false)

const isBusy = computed(() => isAsking.value || isHistoryLoading.value)
const parameterEntries = computed(() => Object.entries(evidence.value?.query_parameters || {}))
const recordColumns = computed(() => {
  const columns = new Set()
  for (const record of evidence.value?.retrieved_records || []) {
    Object.keys(record).forEach((column) => columns.add(column))
  }
  return [...columns]
})

function displayValue(value) {
  return value === null || value === undefined ? '—' : String(value)
}

function statusLabel(status) {
  return {
    answered: 'Answered from saved data',
    no_matches: 'No matching saved data',
    insufficient_data: 'Insufficient saved data',
  }[status] || status
}

function restoreConversation(conversation) {
  activeConversationId.value = conversation.conversation_id
  messages.value = conversation.messages
  const latestAssistant = [...conversation.messages]
    .reverse()
    .find((message) => message.role === 'assistant')
  evidence.value =
    conversation.latest_completed_run && latestAssistant
      ? {
          ...conversation.latest_completed_run,
          conversation_id: conversation.conversation_id,
          answer: latestAssistant.content,
        }
      : null
}

async function refreshConversationList() {
  conversations.value = await loadAdvisorConversations()
}

async function openConversation(conversationId) {
  if (!conversationId || isBusy.value) {
    return
  }
  error.value = ''
  historyError.value = ''
  evidence.value = null
  isHistoryLoading.value = true
  try {
    const conversation = await loadAdvisorConversation(conversationId)
    restoreConversation(conversation)
  } catch (requestError) {
    historyError.value =
      requestError.message || 'The advisor conversation could not be loaded. Please try again.'
  } finally {
    isHistoryLoading.value = false
  }
}

async function initializeHistory() {
  historyError.value = ''
  isHistoryLoading.value = true
  try {
    await refreshConversationList()
    if (conversations.value.length) {
      const conversation = await loadAdvisorConversation(conversations.value[0].conversation_id)
      restoreConversation(conversation)
    }
  } catch (requestError) {
    historyError.value =
      requestError.message || 'Advisor conversations could not be loaded. Please try again.'
  } finally {
    isHistoryLoading.value = false
  }
}

function startNewConversation() {
  activeConversationId.value = ''
  messages.value = []
  evidence.value = null
  error.value = ''
  historyError.value = ''
  question.value = ''
}

async function submitQuestion() {
  error.value = ''
  historyError.value = ''
  evidence.value = null
  const normalizedQuestion = question.value.trim()
  if (!normalizedQuestion || normalizedQuestion.length > 500) {
    error.value = 'Enter a hotel question of 500 characters or fewer.'
    return
  }

  isAsking.value = true
  try {
    const result = await askHotelAdvisor(
      normalizedQuestion,
      activeConversationId.value || null,
    )
    activeConversationId.value = result.conversation_id
    evidence.value = result
    question.value = ''

    try {
      const [conversation] = await Promise.all([
        loadAdvisorConversation(result.conversation_id),
        refreshConversationList(),
      ])
      restoreConversation(conversation)
    } catch {
      error.value =
        'The answer was saved, but conversation history could not be refreshed. Reload the page to recover it.'
    }
  } catch (requestError) {
    error.value = requestError.message || 'The hotel advisor could not answer. Please try again.'
  } finally {
    isAsking.value = false
  }
}

onMounted(initializeHistory)
</script>

<template>
  <section class="advisor-section" aria-labelledby="hotel-advisor-title">
    <div class="section-heading advisor-heading">
      <div>
        <p class="eyebrow section-eyebrow">Assignment 2 hotel advisor</p>
        <h2 id="hotel-advisor-title">Ask about saved hotels</h2>
      </div>
      <button
        type="button"
        class="secondary-button"
        :disabled="isBusy"
        @click="startNewConversation"
      >
        New conversation
      </button>
    </div>

    <p class="section-intro">
      Ask about locally saved hotels, dates, costs, and rooms. Nightly rates and room
      availability are simulated course data, not live inventory.
    </p>

    <div class="advisor-history-picker">
      <label for="advisor-conversation">Saved conversations</label>
      <select
        id="advisor-conversation"
        :value="activeConversationId"
        :disabled="isBusy || conversations.length === 0"
        @change="openConversation($event.target.value)"
      >
        <option value="">Start a new conversation</option>
        <option
          v-for="conversation in conversations"
          :key="conversation.conversation_id"
          :value="conversation.conversation_id"
        >
          {{ conversation.conversation_id }} — {{ conversation.latest_message || 'No message' }}
        </option>
      </select>
    </div>

    <p v-if="isHistoryLoading" class="advisor-state">Loading saved conversations…</p>
    <p v-else-if="historyError" class="error-message advisor-state">{{ historyError }}</p>

    <ol v-if="messages.length" class="advisor-messages" aria-label="Advisor conversation">
      <li
        v-for="message in messages"
        :key="message.message_id"
        class="advisor-message"
        :class="`advisor-message-${message.role}`"
      >
        <strong>{{ message.role === 'user' ? 'You' : 'Hudson Travel advisor' }}</strong>
        <p>{{ message.content }}</p>
      </li>
    </ol>
    <p v-else-if="!isHistoryLoading" class="empty-message advisor-state">
      Ask a question to begin, or reopen a saved conversation.
    </p>

    <form class="advisor-form" novalidate @submit.prevent="submitQuestion">
      <div class="input-group">
        <label for="advisor-question">Hotel question</label>
        <textarea
          id="advisor-question"
          v-model="question"
          name="advisor-question"
          rows="3"
          maxlength="500"
          :disabled="isBusy"
          placeholder="Which saved hotel has rooms from October 10 through October 12, and what is the total cost?"
        ></textarea>
      </div>
      <button type="submit" :disabled="isBusy" :aria-busy="isAsking">
        {{ isAsking ? 'Checking saved data…' : 'Ask' }}
      </button>
    </form>

    <div class="advisor-feedback" aria-live="polite" aria-atomic="true">
      <p v-if="isAsking">Generating a safe query and checking local saved-hotel data…</p>
      <p v-else-if="error" class="error-message">{{ error }}</p>
    </div>

    <section v-if="evidence" class="advisor-evidence" aria-labelledby="advisor-evidence-title">
      <div class="advisor-answer">
        <span class="status-badge" :class="`advisor-status-${evidence.status}`">
          {{ statusLabel(evidence.status) }}
        </span>
        <h3 id="advisor-evidence-title">Grounded answer</h3>
        <p>{{ evidence.answer }}</p>
      </div>

      <details open>
        <summary>Proposed and checked SQL</summary>
        <pre><code>{{ evidence.proposed_sql }}</code></pre>
      </details>

      <details open>
        <summary>Bound query parameters</summary>
        <p v-if="parameterEntries.length === 0" class="empty-message">No query parameters.</p>
        <div v-else class="table-wrap advisor-table-wrap">
          <table>
            <thead><tr><th scope="col">Parameter</th><th scope="col">Value</th></tr></thead>
            <tbody>
              <tr v-for="entry in parameterEntries" :key="entry[0]">
                <td>{{ entry[0] }}</td><td>{{ displayValue(entry[1]) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </details>

      <details open>
        <summary>Retrieved saved-hotel records</summary>
        <p v-if="evidence.retrieved_records.length === 0" class="empty-message">
          No matching local records were retrieved.
        </p>
        <div v-else class="table-wrap advisor-table-wrap">
          <table>
            <thead>
              <tr><th v-for="column in recordColumns" :key="column" scope="col">{{ column }}</th></tr>
            </thead>
            <tbody>
              <tr v-for="(record, index) in evidence.retrieved_records" :key="index">
                <td v-for="column in recordColumns" :key="column">{{ displayValue(record[column]) }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </details>

      <p class="advisor-audit-note">
        Conversation {{ evidence.conversation_id }} · Run {{ evidence.run_id }} · Prompt
        {{ evidence.prompt_version }}
      </p>
    </section>
  </section>
</template>
