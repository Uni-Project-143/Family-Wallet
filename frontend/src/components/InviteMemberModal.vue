<template>
  <Teleport to="body">
    <Transition name="overlay">
      <div v-if="isOpen" class="modal-overlay" @click.self="close">
        <Transition name="modal">
          <div v-if="isOpen" ref="modalRootRef" class="modal-card" role="dialog" aria-modal="true">
            <!-- Close button -->
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

            <!-- Header -->

            <h2 class="modal-title">Invite new member</h2>
            <p class="modal-sub">
              Share this link with your family member. The link is valid for
              <strong>48 hours</strong>.
            </p>

            <!-- Group Invite Code section -->
            <div class="section">
              <div class="section__label">Group Invite Code</div>

              <!-- Link box -->
              <div class="invite-box">
                <div class="invite-box__url" :class="{ 'invite-box__url--loading': isGenerating }">
                  <template v-if="isGenerating">
                    <svg class="spinner" width="14" height="14" viewBox="0 0 14 14" fill="none">
                      <circle cx="7" cy="7" r="5" stroke="rgba(184,151,58,.3)" stroke-width="1.8" />
                      <path
                        d="M7 2A5 5 0 0 1 12 7"
                        stroke="#b8973a"
                        stroke-width="1.8"
                        stroke-linecap="round"
                      />
                    </svg>
                    Generating...
                  </template>
                  <template v-else-if="inviteUrl">{{ inviteUrl }}</template>
                  <template v-else>
                    <span class="invite-box__placeholder">
                      Click "Generate" to create invite link
                    </span>
                  </template>
                </div>

                <!-- Copy button -->
                <button
                  v-if="inviteUrl && !isGenerating"
                  class="btn-copy"
                  :class="{ 'btn-copy--copied': isCopied }"
                  @click="copyLink"
                >
                  <svg v-if="!isCopied" width="13" height="13" viewBox="0 0 13 13" fill="none">
                    <rect
                      x="4"
                      y="4"
                      width="7"
                      height="7"
                      rx="1.5"
                      stroke="currentColor"
                      stroke-width="1.4"
                    />
                    <path
                      d="M2 9.5V3C2 2.44772 2.44772 2 3 2H9.5"
                      stroke="currentColor"
                      stroke-width="1.4"
                      stroke-linecap="round"
                    />
                  </svg>
                  <svg v-else width="13" height="13" viewBox="0 0 13 13" fill="none">
                    <path
                      d="M2 6.5L5 9.5L11 3.5"
                      stroke="currentColor"
                      stroke-width="1.4"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                  {{ isCopied ? 'Copied!' : 'Copy' }}
                </button>

                <!-- Regen button -->
                <button
                  v-if="inviteUrl && !isGenerating"
                  class="btn-regen"
                  :title="'Regenerate — old link becomes invalid'"
                  @click="generateLink(true)"
                >
                  <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                    <path
                      d="M11 2.5C9.9 1.4 8.3.8 6.5.8 3.5.8 1 3.1.8 6"
                      stroke="currentColor"
                      stroke-width="1.4"
                      stroke-linecap="round"
                    />
                    <path
                      d="M9 2L11.5 2.5L12 5"
                      stroke="currentColor"
                      stroke-width="1.4"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                    <path
                      d="M2 10.5C3.1 11.6 4.7 12.2 6.5 12.2c3 0 5.5-2.3 5.7-5.2"
                      stroke="currentColor"
                      stroke-width="1.4"
                      stroke-linecap="round"
                    />
                    <path
                      d="M4 11L1.5 10.5L1 8"
                      stroke="currentColor"
                      stroke-width="1.4"
                      stroke-linecap="round"
                      stroke-linejoin="round"
                    />
                  </svg>
                  Regen
                </button>
              </div>

              <!-- TTL -->
              <div v-if="inviteUrl && expiresAt" class="invite-ttl">
                <svg width="11" height="11" viewBox="0 0 11 11" fill="none">
                  <circle cx="5.5" cy="5.5" r="4.5" stroke="currentColor" stroke-width="1.2" />
                  <path
                    d="M5.5 3V5.5L7 7"
                    stroke="currentColor"
                    stroke-width="1.2"
                    stroke-linecap="round"
                  />
                </svg>
                Valid for {{ ttlLabel }}
              </div>

              <!-- Generate button (якщо посилання ще нема) -->
              <div v-if="!inviteUrl" class="generate-row">
                <button class="btn-gold" :disabled="isGenerating" @click="generateLink(false)">
                  <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                    <path
                      d="M6.5 1V2.5M6.5 10.5V12M1 6.5H2.5M10.5 6.5H12"
                      stroke="currentColor"
                      stroke-width="1.4"
                      stroke-linecap="round"
                    />
                    <circle cx="6.5" cy="6.5" r="2.5" stroke="currentColor" stroke-width="1.4" />
                  </svg>
                  Generate Link
                </button>
              </div>

              <div class="security-note">
                <svg width="11" height="11" viewBox="0 0 11 11" fill="none">
                  <path
                    d="M5.5 1L1.5 3V5.5C1.5 7.9 3.3 10 5.5 10.5C7.7 10 9.5 7.9 9.5 5.5V3L5.5 1Z"
                    stroke="currentColor"
                    stroke-width="1.2"
                  />
                </svg>
                Only Admin can generate invite links. Members receive forbidden access.
              </div>
            </div>

            <div class="section-divider"></div>

            <!-- Direct email invite section -->
            <div class="section">
              <div class="section__label">Or send invite directly by email</div>
              <div class="email-row">
                <div class="i-field-wrap" :class="{ 'i-field-wrap--error': emailError }">
                  <input
                    v-model="directEmail"
                    class="i-field"
                    type="email"
                    placeholder="member@example.com"
                    :disabled="isSending"
                    @blur="validateEmail"
                    @input="onEmailInput"
                    @keydown.enter="sendInvite"
                  />
                </div>
                <button
                  class="btn-send"
                  :disabled="!directEmail.trim() || isSending"
                  @click="sendInvite"
                >
                  <span v-if="!isSending">Send Invite</span>
                  <svg
                    v-else
                    class="spinner"
                    width="16"
                    height="16"
                    viewBox="0 0 16 16"
                    fill="none"
                  >
                    <circle cx="8" cy="8" r="6" stroke="rgba(255,255,255,.3)" stroke-width="2" />
                    <path
                      d="M8 2A6 6 0 0 1 14 8"
                      stroke="white"
                      stroke-width="2"
                      stroke-linecap="round"
                    />
                  </svg>
                </button>
              </div>
              <Transition name="fade-down">
                <p v-if="emailError" class="i-error">{{ emailError }}</p>
              </Transition>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
  import { ref, computed } from 'vue'
  import { fetchGroupInviteLink, regenerateGroupInviteLink } from '../services/authService'
  import { useFocusTrap } from '../composables/useFocusTrap'

  const props = defineProps({
    isOpen: {
      type: Boolean,
      default: false,
    },
  })

  const emit = defineEmits(['close', 'toast'])

  const modalRootRef = ref(null)
  useFocusTrap(modalRootRef, () => props.isOpen)

  const inviteUrl = ref('')
  const expiresAt = ref(null)
  const isGenerating = ref(false)
  const isCopied = ref(false)

  const ttlLabel = computed(() => {
    if (!expiresAt.value) return ''
    const hours = Math.round((new Date(expiresAt.value) - Date.now()) / 3600000)
    if (hours > 1) return `${hours} hours`
    if (hours === 1) return '1 hour'
    return 'less than 1 hour'
  })

  /**
   * Генерує або перегенеровує invite-лінк.
   * @param {boolean} isRegen - true якщо перегенерація
   */
  async function generateLink(isRegen) {
    isGenerating.value = true

    const storedUser = JSON.parse(localStorage.getItem('currentUser') || '{}')
    const groupId = storedUser.groupId

    if (!groupId) {
      emit('toast', { message: 'Group ID not found. Please re-login.', type: 'error' })
      isGenerating.value = false
      return
    }

    try {
      // isRegen → POST /api/v1/group/{groupId}/invite/regenerate
      // !isRegen → GET  /api/v1/group/{groupId}/invite
      const fn = isRegen
        ? () => regenerateGroupInviteLink(groupId)
        : () => fetchGroupInviteLink(groupId)

      const data = await fn()

      // Бекенд повертає invite_link та expires_at
      inviteUrl.value = data.invite_link
      expiresAt.value = data.expires_at

      emit('toast', {
        message: isRegen ? 'New invite link generated' : 'Invite link ready',
        type: 'success',
      })
    } catch (err) {
      const status = err.response?.status
      if (status === 403) {
        emit('toast', { message: 'Only Admin can generate invite links (Rule-02)', type: 'error' })
      } else {
        emit('toast', { message: 'Error generating invite link. Try again.', type: 'error' })
      }
    } finally {
      isGenerating.value = false
    }
  }

  /**
   * Копіює посилання через Clipboard API.
   */
  async function copyLink() {
    if (!inviteUrl.value) return
    try {
      await navigator.clipboard.writeText(inviteUrl.value)
      isCopied.value = true
      emit('toast', { message: 'Link copied ✓', type: 'success' })
      setTimeout(() => {
        isCopied.value = false
      }, 2500)
    } catch {
      emit('toast', { message: 'Failed to copy. Please copy manually.', type: 'error' })
    }
  }

  const directEmail = ref('')
  const emailError = ref('')
  const emailTouched = ref(false)
  const isSending = ref(false)

  const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

  /**
   * Валідація поля email.
   * @returns {boolean}
   */
  function validateEmail() {
    emailTouched.value = true
    emailError.value = ''
    if (!directEmail.value.trim()) return true
    if (!EMAIL_REGEX.test(directEmail.value)) {
      emailError.value = 'Enter a valid email'
      return false
    }
    return true
  }

  function onEmailInput() {
    if (emailTouched.value) validateEmail()
  }

  /**
   * Відправляє запрошення на email.
   * TODO: підключити POST /api/v1/group/{groupId}/invite/send коли з'явиться endpoint
   */
  async function sendInvite() {
    if (!validateEmail()) return
    if (!directEmail.value.trim()) return

    isSending.value = true
    try {
      // TODO: реальний запит після появи endpoint
      // const storedUser = JSON.parse(localStorage.getItem('currentUser') || '{}')
      // await apiClient.post(`/api/v1/group/${storedUser.groupId}/invite/send`, { email: directEmail.value })
      emit('toast', { message: `Invite sent to ${directEmail.value}`, type: 'success' })
      directEmail.value = ''
      emailTouched.value = false
    } catch {
      emit('toast', { message: 'Failed to send invite. Try again.', type: 'error' })
    } finally {
      isSending.value = false
    }
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
    padding: 40px 40px 36px;
    width: 100%;
    max-width: 520px;
    position: relative;
    border-top: 3px solid #b8973a;
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

  /* ── Header ── */
  .modal-ep-tag {
    font-size: 9px;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #b0ada7;
    margin-bottom: 10px;
    font-family: 'DM Mono', 'Courier New', monospace;
  }

  .modal-title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 22px;
    font-weight: 600;
    letter-spacing: -0.2px;
    color: #0d0c0a;
    margin: 0 0 4px;
  }

  .modal-sub {
    font-size: 13px;
    color: #6b6860;
    margin: 0 0 24px;
    line-height: 1.6;
  }

  .section {
    margin-bottom: 4px;
  }

  .section__label {
    font-size: 11px;
    font-weight: 600;
    color: #6b6860;
    letter-spacing: 0.7px;
    text-transform: uppercase;
    margin-bottom: 8px;
  }

  .section__label-note {
    font-size: 9px;
    font-weight: 400;
    color: #b0ada7;
    letter-spacing: 0;
    text-transform: none;
    margin-left: 4px;
  }

  .section-divider {
    height: 1px;
    background: #eae8e4;
    margin: 20px 0;
  }

  .invite-box {
    display: flex;
    align-items: stretch;
    border: 1.5px solid #dfc876;
    border-radius: 8px;
    overflow: hidden;
    background: #ffffff;
    box-shadow: 0 2px 8px rgba(184, 151, 58, 0.1);
    margin-bottom: 8px;
  }

  .invite-box__url {
    flex: 1;
    padding: 0 14px;
    font-size: 12px;
    color: #6b6860;
    font-family: 'DM Mono', 'Courier New', monospace;
    display: flex;
    align-items: center;
    gap: 8px;
    background: #fbf7ec;
    border-right: 1px solid #f2e9c8;
    min-height: 44px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .invite-box__url--loading {
    color: #b0ada7;
  }
  .invite-box__placeholder {
    color: #b0ada7;
    font-style: italic;
  }

  .btn-copy,
  .btn-regen {
    display: flex;
    align-items: center;
    gap: 5px;
    padding: 0 14px;
    background: #ffffff;
    border: none;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.18s;
    flex-shrink: 0;
  }

  .btn-copy {
    color: #9b7a25;
    border-right: 1px solid #f2e9c8;
  }
  .btn-copy:hover {
    background: #fbf7ec;
  }
  .btn-copy--copied {
    color: #2a6b2a;
  }

  .btn-regen {
    color: #6b6860;
  }
  .btn-regen:hover {
    background: #f4f1e9;
    color: #0d0c0a;
  }

  .invite-ttl {
    display: flex;
    align-items: center;
    gap: 5px;
    font-size: 11px;
    color: #9b7a25;
    margin-bottom: 14px;
  }

  .generate-row {
    margin-bottom: 12px;
  }

  .security-note {
    display: flex;
    align-items: flex-start;
    gap: 6px;
    font-size: 11px;
    color: #b0ada7;
    line-height: 1.6;
    padding: 10px 12px;
    background: #f4f1e9;
    border-radius: 6px;
  }

  .email-row {
    display: flex;
    gap: 10px;
    align-items: flex-start;
  }

  .i-field-wrap {
    flex: 1;
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

  .i-field-wrap--error {
    border-color: #c4402a;
  }

  .i-field {
    width: 100%;
    height: 44px;
    border: none;
    background: #f4f1e9;
    padding: 0 14px;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 14px;
    color: #0d0c0a;
    outline: none;
  }

  .i-field:focus {
    background: #ffffff;
  }
  .i-field::placeholder {
    color: #b0ada7;
  }
  .i-field:disabled {
    opacity: 0.45;
  }

  .i-error {
    font-size: 12px;
    color: #c4402a;
    margin-top: 5px;
  }

  .btn-gold {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    height: 44px;
    padding: 0 20px;
    background: linear-gradient(135deg, #b8973a, #c9a84c);
    color: #ffffff;
    border: none;
    border-radius: 8px;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.18s;
    box-shadow: 0 4px 16px rgba(184, 151, 58, 0.18);
  }

  .btn-gold:hover:not(:disabled) {
    background: linear-gradient(135deg, #9b7a25, #b8973a);
    transform: translateY(-1px);
  }

  .btn-gold:disabled {
    opacity: 0.4;
    cursor: not-allowed;
    transform: none;
  }

  .btn-send {
    height: 44px;
    padding: 0 20px;
    background: #0d0c0a;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.18s;
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
  }

  .btn-send:hover:not(:disabled) {
    background: #2d2b27;
  }
  .btn-send:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  .spinner {
    animation: spin 0.8s linear infinite;
  }
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
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
</style>
