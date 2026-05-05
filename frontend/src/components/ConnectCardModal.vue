<template>
  <Teleport to="body">
    <Transition name="overlay">
      <div v-if="isOpen" class="modal-overlay" @click.self="close">
        <Transition name="modal">
          <div v-if="isOpen" class="modal-card" role="dialog" aria-modal="true">
            <button class="modal-close" @click="close" aria-label="Закрити">
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
              Connect your Monobank account to automatically sync transactions with your family.
            </p>

            <form class="form" novalidate @submit.prevent="handleConnect">
              <!-- ── FE-03: Token field with tooltip ── -->
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
                      aria-label="Як знайти токен"
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
                    @input="serverError = ''"
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

              <!-- ── FE-01: Privacy + GDPR ── -->
              <label class="checkbox-row">
                <input v-model="agreedToPrivacy" type="checkbox" class="checkbox" />
                <span class="checkbox-text">
                  I agree to with the
                  <a href="/privacy" target="_blank" rel="noopener noreferrer" class="link">
                    Privacy Policy
                  </a>
                  and conditions of
                  <a href="/gdpr" target="_blank" rel="noopener noreferrer" class="link">
                    GDPR-processing data </a
                  >. My token will be encrypted (AES-256) before being saved.
                </span>
              </label>

              <!-- ── Server error ── -->
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

              <!-- ── Actions ── -->
              <div class="actions">
                <button type="button" class="btn-secondary" :disabled="isConnecting" @click="close">
                  Cancel
                </button>
                <button type="submit" class="btn-gold" :disabled="!canSubmit">
                  <template v-if="!isConnecting">Connect Card</template>
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
                    Checking token...
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
  import { connectMonobankCard } from '../services/cardService'

  const props = defineProps({
    isOpen: { type: Boolean, default: false },
  })

  const emit = defineEmits(['close', 'toast', 'connected'])

  const personalToken = ref('')
  const agreedToPrivacy = ref(false)
  const showToken = ref(false)
  const isTooltipOpen = ref(false)
  const isConnecting = ref(false)
  const serverError = ref('')
  const fieldErrors = ref({ token: '' })

  const inputType = computed(() => (showToken.value ? 'text' : 'password'))

  // FE-01: кнопка disabled до підтвердження чекбоксу і непорожнього токена
  const canSubmit = computed(
    () => personalToken.value.trim().length > 0 && agreedToPrivacy.value && !isConnecting.value,
  )

  watch(
    () => props.isOpen,
    (open) => {
      if (!open) resetForm()
    },
  )

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

  async function handleConnect() {
    if (!validateToken()) return
    if (!agreedToPrivacy.value) return

    const storedUser = JSON.parse(localStorage.getItem('currentUser') || '{}')
    if (!storedUser.groupId) {
      serverError.value = 'Active group not found. Please log in again.'
      return
    }

    isConnecting.value = true
    serverError.value = ''

    try {
      const data = await connectMonobankCard({
        groupId: storedUser.groupId,
        personalToken: personalToken.value.trim(),
      })

      // FE-02: бекенд повертає { masked_pan, status: "Активна", message }
      emit('connected', {
        masked_pan: data.masked_pan,
        status: data.status || 'Active',
      })

      emit('toast', {
        message: `Card connected: ${data.masked_pan}`,
        type: 'success',
      })

      close()
    } catch (err) {
      handleServerError(err)
    } finally {
      isConnecting.value = false
    }
  }

  /**
   * Mapping помилок з бекенду monobank_service.py.
   * Бекенд кладе текст у `detail`, FastAPI HTTPException формат.
   */
  function handleServerError(err) {
    const status = err.response?.status
    const detail = err.response?.data?.detail || err.response?.data?.message

    if (status === 400) {
      serverError.value = detail || 'Invalid Monobank token'
    } else if (status === 403) {
      serverError.value = detail || 'You are not a member of this family group'
    } else if (status === 409) {
      serverError.value = detail || 'This account is already connected to the system'
    } else if (status === 503) {
      serverError.value = 'Monobank API is currently unavailable. Please try again later.'
    } else if (status === 422) {
      serverError.value = 'Please check the correctness of the field values'
    } else {
      serverError.value = 'Failed to connect the card. Please try again.'
    }
  }

  function resetForm() {
    personalToken.value = ''
    agreedToPrivacy.value = false
    showToken.value = false
    isTooltipOpen.value = false
    fieldErrors.value.token = ''
    serverError.value = ''
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
    margin: 0 0 24px;
    line-height: 1.6;
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
</style>
