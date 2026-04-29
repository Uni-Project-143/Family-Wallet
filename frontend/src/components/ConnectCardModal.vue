<template>
  <Teleport to="body">
    <Transition name="overlay">
      <div v-if="isOpen" class="modal-overlay" @click.self="close">
        <Transition name="modal">
          <div v-if="isOpen" class="modal-card" role="dialog" aria-modal="true">
            <button class="modal-close" @click="close" aria-label="Close">
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
              Enter your personal Monobank API token. Get one at
              <a href="https://api.monobank.ua/" target="_blank" class="link">api.monobank.ua</a>.
            </p>

            <form class="form" novalidate @submit.prevent="handleConnect">
              <BaseInput
                v-model="apiToken"
                label="MONOBANK API TOKEN"
                type="password"
                placeholder="uXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
                autocomplete="off"
                hint="Stored encrypted on our server. Never shared."
                :error-message="fieldErrors.token"
                @blur="validateToken"
              />

              <div class="form-field">
                <div class="form-field__label">SYNC TRANSACTIONS FROM</div>
                <div class="i-field-wrap">
                  <input v-model="syncFromDate" class="i-field" type="date" :max="todayIso" />
                </div>
                <p class="form-field__hint">Older transactions won't appear in feed.</p>
              </div>

              <div class="security-note">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path
                    d="M7 1L1.5 3.5V7C1.5 10 4 12.5 7 13C10 12.5 12.5 10 12.5 7V3.5L7 1Z"
                    stroke="currentColor"
                    stroke-width="1.3"
                  />
                  <path
                    d="M5 7L6.5 8.5L9 5.5"
                    stroke="currentColor"
                    stroke-width="1.3"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
                Token is encrypted and stored server-side only. It is never exposed to other users
                or third parties. Only Admin can connect cards.
              </div>

              <Transition name="fade-down">
                <div v-if="serverError" class="server-error" role="alert">
                  {{ serverError }}
                </div>
              </Transition>

              <div class="actions">
                <button type="button" class="btn-secondary" :disabled="isConnecting" @click="close">
                  Cancel
                </button>
                <button type="submit" class="btn-gold" :disabled="!apiToken.trim() || isConnecting">
                  <span v-if="!isConnecting">Connect Card</span>
                  <svg
                    v-else
                    class="spinner"
                    width="18"
                    height="18"
                    viewBox="0 0 18 18"
                    fill="none"
                  >
                    <circle cx="9" cy="9" r="7" stroke="rgba(255,255,255,.3)" stroke-width="2" />
                    <path
                      d="M9 2A7 7 0 0 1 16 9"
                      stroke="white"
                      stroke-width="2"
                      stroke-linecap="round"
                    />
                  </svg>
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
  import { ref, computed } from 'vue'
  import BaseInput from './BaseInput.vue'

  defineProps({
    isOpen: { type: Boolean, default: false },
  })

  const emit = defineEmits(['close', 'toast', 'connected'])

  const apiToken = ref('')
  const cardAlias = ref('')
  const syncFromDate = ref(new Date(Date.now() - 30 * 86400000).toISOString().slice(0, 10))
  const isConnecting = ref(false)
  const serverError = ref('')

  const fieldErrors = ref({ token: '' })

  const todayIso = computed(() => new Date().toISOString().slice(0, 10))

  /**
   * Перевіряє формат Monobank API токена.
   * Токен має префікс 'u' і ~32+ символи.
   */
  function validateToken() {
    fieldErrors.value.token = ''
    const token = apiToken.value.trim()
    if (!token) {
      fieldErrors.value.token = 'API token is required'
      return false
    }
    if (token.length < 20) {
      fieldErrors.value.token = 'Token looks too short. Check api.monobank.ua'
      return false
    }
    return true
  }

  /**
   * Підключення картки.
   * TODO: підключити POST /api/v1/cards/connect коли з'явиться endpoint
   */
  async function handleConnect() {
    if (!validateToken()) return

    isConnecting.value = true
    serverError.value = ''

    try {
      const storedUser = JSON.parse(localStorage.getItem('currentUser') || '{}')
      if (!storedUser.groupId) {
        serverError.value = 'No active group found. Please re-login.'
        return
      }

      // TODO: реальний запит коли бекенд буде готовий
      // const data = await connectMonobankCard({
      //   groupId: storedUser.groupId,
      //   apiToken: apiToken.value.trim(),
      //   alias: cardAlias.value.trim(),
      //   syncFrom: syncFromDate.value,
      // })

      emit('connected', {
        alias: cardAlias.value.trim() || 'Monobank',
        syncFrom: syncFromDate.value,
      })
      emit('toast', { message: 'Card connected successfully', type: 'success' })
      resetForm()
      close()
    } catch (err) {
      const status = err.response?.status
      if (status === 401) {
        serverError.value = 'Invalid Monobank token. Please check and try again.'
      } else if (status === 409) {
        serverError.value = 'This card is already connected.'
      } else {
        serverError.value = 'Failed to connect card. Please try again.'
      }
    } finally {
      isConnecting.value = false
    }
  }

  function resetForm() {
    apiToken.value = ''
    cardAlias.value = ''
    fieldErrors.value.token = ''
    serverError.value = ''
  }

  function close() {
    resetForm()
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
    max-width: 520px;
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

  .link {
    color: #b8973a;
    text-decoration: underline;
  }

  .form {
    display: flex;
    flex-direction: column;
    gap: 18px;
  }

  .form-field__label {
    font-size: 11px;
    font-weight: 600;
    color: #6b6860;
    letter-spacing: 0.7px;
    text-transform: uppercase;
    margin-bottom: 6px;
  }

  .form-field__hint {
    font-size: 11px;
    color: #b0ada7;
    margin: 5px 0 0;
  }

  .i-field-wrap {
    border: 1.5px solid #eae8e4;
    border-radius: 8px;
    overflow: hidden;
    transition:
      border-color 0.18s,
      box-shadow 0.18s;
  }

  .i-field-wrap:focus-within {
    border-color: #b8973a;
    box-shadow: 0 0 0 3px rgba(184, 151, 58, 0.15);
  }

  .i-field {
    width: 100%;
    height: 46px;
    border: none;
    background: #f4f1e9;
    padding: 0 16px;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 14px;
    color: #0d0c0a;
    outline: none;
  }

  .i-field:focus {
    background: #ffffff;
  }

  .security-note {
    display: flex;
    align-items: flex-start;
    gap: 8px;
    font-size: 12px;
    color: #6b6860;
    line-height: 1.6;
    padding: 12px 14px;
    background: #f4f1e9;
    border-radius: 6px;
    border-left: 3px solid #b8973a;
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
    margin-top: 8px;
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
    flex: 1;
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
