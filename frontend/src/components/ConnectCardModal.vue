<template>
  <Teleport to="body">
    <Transition name="overlay">
      <div v-if="isOpen" class="modal-overlay" @click.self="close">
        <Transition name="modal">
          <div v-if="isOpen" ref="modalRootRef" class="modal-card" role="dialog" aria-modal="true">
            <button class="modal-close" aria-label="Close" @click="close">
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path
                  d="M1 1L13 13M13 1L1 13"
                  stroke="currentColor"
                  stroke-width="1.5"
                  stroke-linecap="round"
                />
              </svg>
            </button>

            <h2 class="modal-title">Connect Monobank Card</h2>
            <p class="modal-sub">
              {{
                currentStep === 1
                  ? 'Connect your Monobank account to automatically sync transactions with your family.'
                  : 'Choose which card you want to connect to this group.'
              }}
            </p>

            <div class="steps">
              <div class="step" :class="stepClass(1)">
                <div class="step__circle">1</div>
                <div class="step__label">Token</div>
              </div>
              <div class="step-divider" :class="{ 'step-divider--done': currentStep > 1 }"></div>
              <div class="step" :class="stepClass(2)">
                <div class="step__circle">2</div>
                <div class="step__label">Card</div>
              </div>
            </div>

            <form v-if="currentStep === 1" class="form" novalidate @submit.prevent="handleGetCards">
              <div class="field">
                <div class="field__header">
                  <label class="field__label" for="mono-token"> PERSONAL API TOKEN </label>

                  <div
                    class="tooltip-wrap"
                    @mouseenter="isTooltipOpen = true"
                    @mouseleave="isTooltipOpen = false"
                  >
                    <button
                      type="button"
                      class="tooltip-trigger"
                      aria-label="Where to find the token"
                      @click="isTooltipOpen = !isTooltipOpen"
                    >
                      <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                        <circle cx="7" cy="7" r="6" stroke="currentColor" stroke-width="1.3" />
                        <path
                          d="M7 6V10"
                          stroke="currentColor"
                          stroke-width="1.3"
                          stroke-linecap="round"
                        />
                        <circle cx="7" cy="4" r=".8" fill="currentColor" />
                      </svg>
                      Where to find the token
                    </button>

                    <Transition name="fade-down">
                      <div v-if="isTooltipOpen" class="tooltip" role="tooltip">
                        <div class="tooltip__title">Where to find the token</div>
                        <ol class="tooltip__list">
                          <li>Open the Monobank mobile app</li>
                          <li>
                            Go to
                            <a
                              href="https://api.monobank.ua/"
                              target="_blank"
                              rel="noopener noreferrer"
                              class="tooltip__link"
                              >api.monobank.ua</a
                            >
                          </li>
                          <li>Scan the QR code in the app</li>
                          <li>Copy the Personal Token (starts with <code>u</code>)</li>
                        </ol>
                        <div class="tooltip__hint">
                          The token provides only read access to transaction statements.
                        </div>
                      </div>
                    </Transition>
                  </div>
                </div>

                <div class="i-field-wrap" :class="{ 'i-field-wrap--error': fieldErrors.token }">
                  <input
                    id="mono-token"
                    v-model="personalToken"
                    :type="inputType"
                    class="i-field"
                    placeholder="uXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
                    autocomplete="off"
                    spellcheck="false"
                    @blur="validateToken"
                    @input="onTokenInput"
                  />
                  <button
                    type="button"
                    class="eye-btn"
                    :aria-label="showToken ? 'Hide token' : 'Show token'"
                    @click="showToken = !showToken"
                  >
                    <svg v-if="!showToken" width="16" height="16" viewBox="0 0 16 16" fill="none">
                      <path
                        d="M1 8C1 8 3.5 3 8 3C12.5 3 15 8 15 8C15 8 12.5 13 8 13C3.5 13 1 8 1 8Z"
                        stroke="currentColor"
                        stroke-width="1.3"
                      />
                      <circle cx="8" cy="8" r="2.5" stroke="currentColor" stroke-width="1.3" />
                    </svg>
                    <svg v-else width="16" height="16" viewBox="0 0 16 16" fill="none">
                      <path
                        d="M2 2L14 14M6.5 6.5C5.97 7.04 5.5 7.84 5.5 8C5.5 9.38 6.62 10.5 8 10.5C8.16 10.5 8.96 10.03 9.5 9.5"
                        stroke="currentColor"
                        stroke-width="1.3"
                        stroke-linecap="round"
                      />
                    </svg>
                  </button>
                </div>
                <p v-if="fieldErrors.token" class="error-text">{{ fieldErrors.token }}</p>
              </div>

              <label class="checkbox-row">
                <input v-model="agreedToPrivacy" type="checkbox" class="checkbox" />
                <span class="checkbox-text">
                  I agree to the
                  <a href="/privacy.pdf" target="_blank" rel="noopener noreferrer" class="link">
                    Privacy Policy
                  </a>
                  and conditions of GDPR data processing. My token will be encrypted (AES-256)
                  before being saved.
                </span>
              </label>

              <Transition name="fade-down">
                <div v-if="serverError" class="server-error" role="alert">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <circle cx="7" cy="7" r="6" stroke="currentColor" stroke-width="1.3" />
                    <path
                      d="M7 4V8M7 10V10.01"
                      stroke="currentColor"
                      stroke-width="1.3"
                      stroke-linecap="round"
                    />
                  </svg>
                  {{ serverError }}
                </div>
              </Transition>

              <div class="actions">
                <button type="button" class="btn-secondary" :disabled="isLoading" @click="close">
                  Cancel
                </button>
                <button type="submit" class="btn-gold" :disabled="!canSubmitStep1">
                  <template v-if="!isLoading">Show my cards</template>
                  <template v-else>
                    <svg class="spinner" width="18" height="18" viewBox="0 0 18 18" fill="none">
                      <circle cx="9" cy="9" r="7" stroke="rgba(255,255,255,.3)" stroke-width="2" />
                      <path
                        d="M9 2A7 7 0 0 1 16 9"
                        stroke="white"
                        stroke-width="2"
                        stroke-linecap="round"
                      />
                    </svg>
                    Fetching cards...
                  </template>
                </button>
              </div>
            </form>

            <form v-else class="form" novalidate @submit.prevent="handleConnect">
              <div v-if="cards.length === 0" class="empty-cards">
                No UAH cards found on this account.
              </div>

              <div v-else class="card-list">
                <label
                  v-for="card in cards"
                  :key="card.account_id"
                  class="card-row"
                  :class="{ 'card-row--selected': selectedAccountId === card.account_id }"
                >
                  <input
                    v-model="selectedAccountId"
                    type="radio"
                    :value="card.account_id"
                    class="card-row__radio"
                  />
                  <div class="card-row__radio-visual"></div>
                  <div class="card-row__main">
                    <div class="card-row__top">
                      <span class="card-row__bank">Monobank</span>
                      <span
                        class="type-badge"
                        :class="`type-badge--${(card.type || 'default').toLowerCase()}`"
                      >
                        {{ card.type || 'card' }}
                      </span>
                    </div>
                    <div class="card-row__pan">{{ card.masked_pan }}</div>
                  </div>
                </label>
              </div>

              <Transition name="fade-down">
                <div v-if="serverError" class="server-error" role="alert">
                  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <circle cx="7" cy="7" r="6" stroke="currentColor" stroke-width="1.3" />
                    <path
                      d="M7 4V8M7 10V10.01"
                      stroke="currentColor"
                      stroke-width="1.3"
                      stroke-linecap="round"
                    />
                  </svg>
                  {{ serverError }}
                </div>
              </Transition>

              <div class="actions">
                <button type="button" class="btn-secondary" :disabled="isLoading" @click="goBack">
                  Back
                </button>
                <button type="submit" class="btn-gold" :disabled="!canSubmitStep2">
                  <template v-if="!isLoading">Connect this card</template>
                  <template v-else>
                    <svg class="spinner" width="18" height="18" viewBox="0 0 18 18" fill="none">
                      <circle cx="9" cy="9" r="7" stroke="rgba(255,255,255,.3)" stroke-width="2" />
                      <path
                        d="M9 2A7 7 0 0 1 16 9"
                        stroke="white"
                        stroke-width="2"
                        stroke-linecap="round"
                      />
                    </svg>
                    Connecting...
                  </template>
                </button>
              </div>
            </form>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
  import { ref, computed, watch } from 'vue'
  import { fetchMonobankCards, connectMonobankCard } from '../services/cardService'
  import { useFocusTrap } from '../composables/useFocusTrap'

  const props = defineProps({
    isOpen: { type: Boolean, default: false },
  })

  const emit = defineEmits(['close', 'toast', 'connected'])

  const modalRootRef = ref(null)
  useFocusTrap(modalRootRef, () => props.isOpen)

  const personalToken = ref('')
  const agreedToPrivacy = ref(false)
  const showToken = ref(false)
  const isTooltipOpen = ref(false)
  const isLoading = ref(false)
  const serverError = ref('')
  const fieldErrors = ref({ token: '' })

  const currentStep = ref(1)
  const cards = ref([])
  const selectedAccountId = ref(null)
  const cachedToken = ref('')

  const inputType = computed(() => (showToken.value ? 'text' : 'password'))

  const canSubmitStep1 = computed(
    () => personalToken.value.trim().length > 0 && agreedToPrivacy.value && !isLoading.value,
  )

  const canSubmitStep2 = computed(() => selectedAccountId.value !== null && !isLoading.value)

  watch(
    () => props.isOpen,
    (open) => {
      if (!open) resetForm()
    },
  )

  function stepClass(n) {
    return {
      'step--active': currentStep.value === n,
      'step--done': currentStep.value > n,
    }
  }

  function validateToken() {
    fieldErrors.value.token = ''
    const token = personalToken.value.trim()
    if (!token) {
      fieldErrors.value.token = 'Token is required'
      return false
    }
    if (token.length < 20) {
      fieldErrors.value.token = 'Token looks too short. Get a valid one from api.monobank.ua'
      return false
    }
    return true
  }

  function onTokenInput() {
    serverError.value = ''
    if (cards.value.length > 0 && personalToken.value.trim() !== cachedToken.value) {
      cards.value = []
      cachedToken.value = ''
      selectedAccountId.value = null
    }
  }

  async function handleGetCards() {
    if (!validateToken()) return
    if (!agreedToPrivacy.value) return

    const token = personalToken.value.trim()

    if (cards.value.length > 0 && cachedToken.value === token) {
      currentStep.value = 2
      return
    }

    isLoading.value = true
    serverError.value = ''

    try {
      const result = await fetchMonobankCards(token)
      if (!Array.isArray(result) || result.length === 0) {
        serverError.value = 'No UAH cards found on this Monobank account.'
        return
      }
      cards.value = result
      cachedToken.value = token
      currentStep.value = 2
    } catch (err) {
      handleServerError(err)
    } finally {
      isLoading.value = false
    }
  }

  async function handleConnect() {
    if (!selectedAccountId.value) return

    const storedUser = JSON.parse(localStorage.getItem('currentUser') || '{}')
    if (!storedUser.groupId) {
      serverError.value = 'Active group not found. Please sign in again.'
      return
    }

    const selectedCard = cards.value.find((c) => c.account_id === selectedAccountId.value)
    if (!selectedCard) {
      serverError.value = 'Selected card not found. Please go back and try again.'
      return
    }

    isLoading.value = true
    serverError.value = ''

    let connectedCard
    try {
      connectedCard = await connectMonobankCard(
        storedUser.groupId,
        personalToken.value.trim(),
        selectedCard,
      )
    } catch (err) {
      handleServerError(err)
      isLoading.value = false
      return
    }

    emit('connected', {
      id: connectedCard.card_id,
      masked_pan: selectedCard.masked_pan,
      status: 'ACTIVE',
    })

    emit('toast', {
      message: `Card connected: ${selectedCard.masked_pan}`,
      type: 'success',
    })

    isLoading.value = false
    close()
  }

  function goBack() {
    currentStep.value = 1
    serverError.value = ''
  }

  function handleServerError(err) {
    const status = err.response?.status
    const message = err.response?.data?.message
    const detail = err.response?.data?.detail

    if (status === 400) {
      serverError.value = message || detail || 'Invalid Monobank token'
    } else if (status === 403) {
      serverError.value = message || 'You are not a member of this group'
    } else if (status === 409) {
      serverError.value = message || 'This account is already connected to the system'
    } else if (status === 429) {
      serverError.value =
        'Too many requests to Monobank. Please wait 60 seconds before trying again.'
    } else if (status === 503) {
      serverError.value = 'Monobank API is currently unavailable. Please try again later.'
    } else if (status === 422) {
      serverError.value = detail?.[0]?.msg || 'Please check the form fields'
    } else {
      serverError.value = err.userMessage || 'Something went wrong. Please try again.'
    }
  }

  function resetForm() {
    personalToken.value = ''
    agreedToPrivacy.value = false
    showToken.value = false
    isTooltipOpen.value = false
    fieldErrors.value.token = ''
    serverError.value = ''
    currentStep.value = 1
    cards.value = []
    selectedAccountId.value = null
    cachedToken.value = ''
    isLoading.value = false
  }

  function close() {
    emit('close')
  }
</script>

<style scoped>
  .modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(13, 12, 10, 0.52);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 200;
    backdrop-filter: blur(4px);
    padding: 20px;
  }

  .modal-card {
    background: #ffffff;
    border-radius: 20px;
    box-shadow:
      0 20px 56px rgba(13, 12, 10, 0.16),
      0 0 0 1px rgba(184, 151, 58, 0.1);
    padding: 40px 40px 32px;
    width: 100%;
    max-width: 540px;
    position: relative;
    border-top: 3px solid #b8973a;
    max-height: 90vh;
    overflow-y: auto;
  }

  @media (max-width: 560px) {
    .modal-card {
      padding: 28px 22px;
    }
  }

  .modal-close {
    position: absolute;
    top: 14px;
    right: 16px;
    width: 32px;
    height: 32px;
    border-radius: 6px;
    border: 1px solid #eae8e4;
    background: #f4f1e9;
    color: #6b6860;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.18s;
  }
  .modal-close:hover {
    background: #0d0c0a;
    color: #ffffff;
    border-color: #0d0c0a;
  }

  .modal-title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 22px;
    font-weight: 600;
    color: #0d0c0a;
    margin: 0 0 6px;
  }
  .modal-sub {
    font-size: 13px;
    color: #6b6860;
    margin: 0 0 20px;
    line-height: 1.6;
  }

  .steps {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 24px;
  }
  .step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
  }
  .step__circle {
    width: 28px;
    height: 28px;
    border-radius: 50%;
    background: #f4f1e9;
    border: 2px solid #d6d3ce;
    color: #b0ada7;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-weight: 700;
    font-size: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
  }
  .step__label {
    font-size: 10px;
    font-weight: 700;
    color: #b0ada7;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    transition: color 0.2s;
  }
  .step--active .step__circle {
    background: linear-gradient(135deg, #b8973a, #c9a84c);
    border-color: #b8973a;
    color: #ffffff;
    box-shadow: 0 2px 8px rgba(184, 151, 58, 0.3);
  }
  .step--active .step__label {
    color: #9b7a25;
  }
  .step--done .step__circle {
    background: #fbf7ec;
    border-color: #b8973a;
    color: #b8973a;
  }
  .step--done .step__label {
    color: #6b6860;
  }
  .step-divider {
    flex: 1;
    height: 2px;
    background: #d6d3ce;
    margin: 0 4px 18px;
    transition: background 0.2s;
  }
  .step-divider--done {
    background: #b8973a;
  }

  .form {
    display: flex;
    flex-direction: column;
    gap: 18px;
  }
  .field {
    display: flex;
    flex-direction: column;
  }
  .field__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 6px;
  }
  .field__label {
    font-size: 11px;
    font-weight: 600;
    color: #6b6860;
    letter-spacing: 0.7px;
    text-transform: uppercase;
  }

  .tooltip-wrap {
    position: relative;
  }
  .tooltip-trigger {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    border: none;
    background: none;
    color: #b8973a;
    font-size: 11px;
    font-weight: 600;
    cursor: pointer;
    padding: 2px 4px;
    font-family: 'DM Sans', system-ui, sans-serif;
  }
  .tooltip-trigger:hover {
    color: #9b7a25;
  }
  .tooltip {
    position: absolute;
    top: calc(100% + 8px);
    right: 0;
    width: 280px;
    background: #0d0c0a;
    color: #ead9a0;
    border-radius: 10px;
    padding: 14px 16px;
    font-size: 12px;
    line-height: 1.5;
    box-shadow: 0 12px 32px rgba(13, 12, 10, 0.32);
    z-index: 10;
  }
  .tooltip::before {
    content: '';
    position: absolute;
    top: -6px;
    right: 14px;
    width: 12px;
    height: 12px;
    background: #0d0c0a;
    transform: rotate(45deg);
  }

  .tooltip__title {
    font-weight: 700;
    color: #ffffff;
    margin-bottom: 8px;
    font-size: 12px;
  }

  .tooltip__list {
    margin: 0;
    padding-left: 18px;
    color: rgba(234, 217, 160, 0.85);
  }
  .tooltip__list li {
    margin-bottom: 4px;
  }
  .tooltip__list code {
    background: rgba(184, 151, 58, 0.18);
    padding: 1px 5px;
    border-radius: 3px;
    font-family: 'DM Mono', 'Courier New', monospace;
    font-size: 11px;
    color: #ead9a0;
  }
  .tooltip__link {
    color: #ead9a0;
    text-decoration: underline;
  }
  .tooltip__hint {
    margin-top: 8px;
    padding-top: 8px;
    border-top: 1px solid rgba(184, 151, 58, 0.18);
    color: rgba(234, 217, 160, 0.6);
    font-size: 11px;
  }

  .i-field-wrap {
    position: relative;
    border: 1.5px solid #eae8e4;
    border-radius: 8px;
    overflow: hidden;
    transition:
      border-color 0.18s,
      box-shadow 0.18s;
    background: #f4f1e9;
  }
  .i-field-wrap:focus-within {
    border-color: #b8973a;
    box-shadow: 0 0 0 3px rgba(184, 151, 58, 0.15);
    background: #ffffff;
  }
  .i-field-wrap--error {
    border-color: #c4402a;
  }
  .i-field {
    width: 100%;
    height: 46px;
    border: none;
    background: transparent;
    padding: 0 44px 0 16px;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 14px;
    color: #0d0c0a;
    outline: none;
  }
  .i-field::placeholder {
    color: #b0ada7;
  }
  .eye-btn {
    position: absolute;
    right: 8px;
    top: 50%;
    transform: translateY(-50%);
    width: 32px;
    height: 32px;
    border-radius: 6px;
    border: none;
    background: transparent;
    color: #6b6860;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.15s;
  }
  .eye-btn:hover {
    background: rgba(184, 151, 58, 0.1);
    color: #b8973a;
  }
  .error-text {
    font-size: 12px;
    color: #c4402a;
    margin: 5px 0 0;
  }

  .checkbox-row {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 12px 14px;
    background: #fbf7ec;
    border: 1px solid #f2e9c8;
    border-radius: 8px;
    cursor: pointer;
  }
  .checkbox {
    width: 16px;
    height: 16px;
    margin: 2px 0 0;
    accent-color: #b8973a;
    cursor: pointer;
    flex-shrink: 0;
  }
  .checkbox-text {
    font-size: 12px;
    color: #6b6860;
    line-height: 1.6;
  }
  .link {
    color: #b8973a;
    text-decoration: underline;
  }
  .link:hover {
    color: #9b7a25;
  }

  .server-error {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 14px;
    background: #fef0ed;
    border: 1px solid #e8897a;
    border-radius: 8px;
    font-size: 13px;
    color: #c4402a;
  }

  .card-list {
    display: flex;
    flex-direction: column;
    gap: 10px;
    max-height: 360px;
    overflow-y: auto;
    padding: 2px;
  }
  .card-row {
    position: relative;
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 14px 16px;
    background: #ffffff;
    border: 1.5px solid #eae8e4;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.18s;
  }
  .card-row:hover {
    border-color: #d6d3ce;
    background: #faf8f3;
  }
  .card-row--selected {
    border-color: #b8973a;
    background: #fbf7ec;
    box-shadow: 0 2px 12px rgba(184, 151, 58, 0.18);
  }
  .card-row__radio {
    position: absolute;
    opacity: 0;
    pointer-events: none;
  }
  .card-row__radio-visual {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    border: 2px solid #d6d3ce;
    background: #ffffff;
    flex-shrink: 0;
    position: relative;
    transition: all 0.18s;
  }
  .card-row--selected .card-row__radio-visual {
    border-color: #b8973a;
  }
  .card-row--selected .card-row__radio-visual::after {
    content: '';
    position: absolute;
    inset: 3px;
    border-radius: 50%;
    background: #b8973a;
  }
  .card-row__main {
    flex: 1;
    min-width: 0;
  }
  .card-row__top {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
  }
  .card-row__bank {
    font-size: 12px;
    font-weight: 700;
    color: #9b7a25;
    letter-spacing: 0.5px;
  }
  .card-row__pan {
    font-family: 'DM Mono', 'Courier New', monospace;
    font-size: 13px;
    color: #6b6860;
  }
  .card-row__balance {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 18px;
    font-weight: 600;
    color: #0d0c0a;
    white-space: nowrap;
  }
  .card-row__currency {
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 11px;
    font-weight: 500;
    color: #b0ada7;
    margin-left: 3px;
  }

  .type-badge {
    display: inline-flex;
    align-items: center;
    height: 18px;
    padding: 0 8px;
    border-radius: 9999px;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    background: #fbf7ec;
    color: #9b7a25;
    border: 1px solid #f2e9c8;
  }
  .type-badge--black {
    background: #0d0c0a;
    color: #ead9a0;
    border-color: #0d0c0a;
  }
  .type-badge--white {
    background: #ffffff;
    color: #6b6860;
    border-color: #d6d3ce;
  }
  .type-badge--platinum {
    background: linear-gradient(135deg, #b8973a, #dfc876);
    color: #ffffff;
    border: none;
  }
  .type-badge--iron {
    background: #4f5359;
    color: #ffffff;
    border: none;
  }
  .type-badge--fop {
    background: #4a6fa5;
    color: #ffffff;
    border: none;
  }
  .type-badge--yellow {
    background: linear-gradient(135deg, #dfc876, #f2e9c8);
    color: #6b5d20;
    border: none;
  }

  .empty-cards {
    padding: 32px;
    text-align: center;
    color: #b0ada7;
    font-size: 13px;
    background: #faf8f3;
    border-radius: 10px;
    border: 1px dashed #d6d3ce;
  }

  .actions {
    display: flex;
    gap: 12px;
    margin-top: 4px;
  }
  .btn-secondary {
    flex: 1;
    height: 46px;
    background: #ffffff;
    color: #6b6860;
    border: 1.5px solid #d6d3ce;
    border-radius: 8px;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.18s;
  }
  .btn-secondary:hover:not(:disabled) {
    background: #f4f1e9;
    border-color: #b0ada7;
  }
  .btn-gold {
    flex: 1.4;
    height: 46px;
    background: linear-gradient(135deg, #b8973a, #c9a84c);
    color: #ffffff;
    border: none;
    border-radius: 8px;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.18s;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    box-shadow: 0 4px 16px rgba(184, 151, 58, 0.18);
  }
  .btn-gold:hover:not(:disabled) {
    background: linear-gradient(135deg, #9b7a25, #b8973a);
    transform: translateY(-1px);
  }
  .btn-gold:disabled,
  .btn-secondary:disabled {
    opacity: 0.4;
    cursor: not-allowed;
    transform: none;
  }
  .spinner {
    animation: spin 0.8s linear infinite;
  }
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .fade-down-enter-active,
  .fade-down-leave-active {
    transition:
      opacity 0.2s ease,
      transform 0.2s ease;
  }
  .fade-down-enter-from,
  .fade-down-leave-to {
    opacity: 0;
    transform: translateY(-4px);
  }
  .overlay-enter-active,
  .overlay-leave-active {
    transition: opacity 0.25s ease;
  }
  .overlay-enter-from,
  .overlay-leave-to {
    opacity: 0;
  }
  .modal-enter-active,
  .modal-leave-active {
    transition:
      opacity 0.25s ease,
      transform 0.25s ease;
  }
  .modal-enter-from,
  .modal-leave-to {
    opacity: 0;
    transform: scale(0.96) translateY(8px);
  }

  @media (max-width: 560px) {
    .modal-overlay {
      padding: 0;
      align-items: flex-end;
    }
    .modal-card {
      max-width: 100%;
      width: 100%;
      border-radius: 20px 20px 0 0;
      padding: 24px 20px 28px;
      max-height: 92vh;
      overflow-y: auto;
      border-top: 3px solid #b8973a;
    }
    .modal-title {
      font-size: 20px;
    }
    .modal-close {
      top: 10px;
      right: 12px;
    }
  }

  @media (max-width: 560px) {
    .step-indicator {
      gap: 8px;
    }
    .card-row {
      padding: 12px;
    }
    .card-row__pan {
      font-size: 12px;
    }
  }
</style>
