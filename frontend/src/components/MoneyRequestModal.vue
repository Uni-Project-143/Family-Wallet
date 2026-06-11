<template>
  <Teleport to="body">
    <Transition name="overlay">
      <div v-if="isOpen" class="modal-overlay" @click.self="close">
        <Transition name="modal">
          <div v-if="isOpen" ref="modalRootRef" class="modal-card" role="dialog" aria-modal="true">
            <!-- Close -->
            <button class="modal-close" :disabled="isSubmitting" aria-label="Close" @click="close">
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
            <h2 class="modal-title">Request for Transfer of Money</h2>
            <p class="modal-sub">
              Sender: {{ senderName }} <span class="arrow">→</span> Recipient: {{ recipientName }}
            </p>

            <form class="form" @submit.prevent="handleSubmit">
              <!-- Recipient -->
              <div class="field">
                <label class="field__label">Recipient</label>
                <div class="recipient-card">
                  <div class="avatar avatar--md" :class="`avatar--${recipientVariant}`">
                    {{ recipientInitials }}
                  </div>
                  <div class="recipient-card__info">
                    <div class="recipient-card__name">{{ recipientName }}</div>
                    <div class="recipient-card__sub">Group Member</div>
                  </div>
                  <span
                    class="badge"
                    :class="recipientRole === 'ADMIN' ? 'badge--admin' : 'badge--member'"
                  >
                    {{ recipientRole }}
                  </span>
                </div>
              </div>

              <!-- Description -->
              <div class="field">
                <label class="field__label" for="mr-desc">Description</label>
                <div class="i-field-wrap">
                  <input
                    id="mr-desc"
                    v-model="description"
                    class="i-field"
                    type="text"
                    maxlength="500"
                    placeholder="My part for groceries at the supermarket"
                    :disabled="isSubmitting"
                  />
                </div>
              </div>

              <!-- Sum -->
              <div class="field">
                <label class="field__label" for="mr-amount">Sum (UAH)</label>
                <div class="i-field-wrap sum-wrap" :class="{ 'i-field-wrap--error': error }">
                  <input
                    id="mr-amount"
                    v-model="amount"
                    class="i-field"
                    type="number"
                    step="0.01"
                    min="0.01"
                    placeholder="0.00"
                    :disabled="isSubmitting"
                    @blur="validate"
                  />
                  <span class="sum-suffix">UAH</span>
                </div>
                <Transition name="fade-down">
                  <p v-if="error" class="i-error">{{ error }}</p>
                </Transition>
              </div>

              <!-- Status -->
              <div class="field">
                <label class="field__label">Status</label>
                <div class="status-row">
                  <span class="badge badge--pending">PENDING</span>
                  <span class="status-row__hint">assigned after sending</span>
                </div>
              </div>

              <!-- Group note -->
              <div class="group-note">
                Request can only be sent between members of the same Group.
              </div>

              <!-- Actions -->
              <div class="actions">
                <button type="submit" class="btn-dark" :disabled="isSubmitting">
                  <span v-if="!isSubmitting">Send a Request</span>
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
                <button type="button" class="btn-outline" :disabled="isSubmitting" @click="close">
                  Cancel
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
  import { useFocusTrap } from '../composables/useFocusTrap'
  import { createMoneyRequest } from '../services/moneyRequestService'

  const props = defineProps({
    isOpen: { type: Boolean, required: true },
    senderName: { type: String, default: 'You' },
    // Об'єкт учасника-отримувача: { name, initials, role, avatarVariant }
    recipient: { type: Object, default: null },
  })

  const emit = defineEmits(['close', 'success', 'toast'])

  const modalRootRef = ref(null)
  useFocusTrap(modalRootRef, () => props.isOpen)

  const description = ref('')
  const amount = ref('')
  const error = ref('')
  const isSubmitting = ref(false)

  const recipientName = computed(() => props.recipient?.name || 'Group member')
  const recipientInitials = computed(() => props.recipient?.initials || '?')
  const recipientRole = computed(() => props.recipient?.role || 'MEMBER')
  const recipientVariant = computed(() => props.recipient?.avatarVariant || 'gold')

  watch(
    () => props.isOpen,
    (open) => {
      if (open) {
        description.value = ''
        amount.value = ''
        error.value = ''
        isSubmitting.value = false
      }
    },
  )

  const AMOUNT_REGEX = /^\d+(\.\d{1,2})?$/

  function validate() {
    const raw = String(amount.value ?? '')
    if (raw === '') {
      error.value = 'Enter the amount'
      return false
    }
    if (!AMOUNT_REGEX.test(raw)) {
      error.value = 'Up to 2 decimal places'
      return false
    }
    if (parseFloat(raw) <= 0) {
      error.value = 'Amount must be greater than 0'
      return false
    }
    error.value = ''
    return true
  }

  async function handleSubmit() {
    if (!validate()) return
    if (!props.recipient?.id) {
      emit('toast', { message: 'Recipient is not specified', type: 'error' })
      return
    }
    isSubmitting.value = true
    try {
      // POST /api/v1/requests/ — створює запит коштів (recipient має прийняти).
      const result = await createMoneyRequest({
        recipient_id: props.recipient.id,
        amount: parseFloat(amount.value),
        description: description.value || null,
      })
      emit('success', {
        request_id: result?.request_id,
        amount: parseFloat(amount.value),
        recipientName: recipientName.value,
      })
      emit('toast', {
        message: `Request for ${parseFloat(amount.value)} UAH sent to ${recipientName.value}`,
        type: 'success',
      })
      // Закриваємо напряму (а не через close(), бо isSubmitting ще true і guard завадив би).
      isSubmitting.value = false
      emit('close')
    } catch (err) {
      const detail =
        err.response?.data?.detail || err.userMessage || 'Failed to send request. Try again.'
      emit('toast', {
        message: typeof detail === 'string' ? detail : 'Failed to send request',
        type: 'error',
      })
    } finally {
      isSubmitting.value = false
    }
  }

  function close() {
    if (isSubmitting.value) return
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
    padding: 36px 36px 32px;
    width: 100%;
    max-width: 460px;
    position: relative;
    border-top: 3px solid #b8973a;
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
  .modal-close:hover:not(:disabled) {
    background: #0d0c0a;
    color: #ffffff;
    border-color: #0d0c0a;
  }
  .modal-close:disabled {
    opacity: 0.4;
    cursor: not-allowed;
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
    margin: 0 0 22px;
    line-height: 1.6;
  }
  .modal-sub .arrow {
    color: #b8973a;
    font-weight: 600;
  }

  .form {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  .field {
    display: flex;
    flex-direction: column;
  }
  .field__label {
    font-size: 11px;
    font-weight: 600;
    color: #6b6860;
    letter-spacing: 0.7px;
    text-transform: uppercase;
    margin-bottom: 8px;
  }

  /* Recipient card */
  .recipient-card {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 14px;
    background: #faf8f3;
    border: 1px solid #eae8e4;
    border-radius: 10px;
  }
  .recipient-card__info {
    flex: 1;
    min-width: 0;
  }
  .recipient-card__name {
    font-size: 14px;
    font-weight: 600;
    color: #0d0c0a;
  }
  .recipient-card__sub {
    font-size: 12px;
    color: #b0ada7;
    margin-top: 1px;
  }

  /* Inputs */
  .i-field-wrap {
    display: flex;
    align-items: stretch;
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
    box-sizing: border-box;
  }
  .i-field:focus {
    background: #ffffff;
  }
  .i-field::placeholder {
    color: #b0ada7;
  }
  .i-field:disabled {
    opacity: 0.45;
    cursor: not-allowed;
  }

  /* Sum suffix */
  .sum-suffix {
    display: flex;
    align-items: center;
    padding: 0 16px;
    background: #fbf7ec;
    border-left: 1px solid #f2e9c8;
    font-size: 12px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: #9b7a25;
    flex-shrink: 0;
  }

  .i-error {
    font-size: 12px;
    color: #c4402a;
    margin-top: 5px;
  }

  /* Status */
  .status-row {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 11px 14px;
    background: #faf8f3;
    border: 1px solid #eae8e4;
    border-radius: 8px;
  }
  .status-row__hint {
    font-size: 12px;
    color: #b0ada7;
  }

  /* Group note */
  .group-note {
    font-size: 12px;
    color: #9b7a25;
    line-height: 1.6;
    padding: 10px 14px;
    background: #fbf7ec;
    border: 1px solid #f2e9c8;
    border-radius: 8px;
  }

  /* Badges */
  .badge {
    display: inline-flex;
    align-items: center;
    height: 20px;
    padding: 0 9px;
    border-radius: 9999px;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
    flex-shrink: 0;
  }
  .badge--admin {
    background: linear-gradient(135deg, #b8973a, #c9a84c);
    color: #fff;
  }
  .badge--member {
    background: #eae8e4;
    color: #6b6860;
    border: 1px solid #d6d3ce;
  }
  .badge--pending {
    background: #fbf7ec;
    color: #9b7a25;
    border: 1px solid #dfc876;
  }

  /* Avatar */
  .avatar {
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-weight: 700;
    flex-shrink: 0;
  }
  .avatar--md {
    width: 40px;
    height: 40px;
    font-size: 14px;
  }
  .avatar--gold {
    background: linear-gradient(135deg, #f2e9c8, #dfc876);
    color: #7a5e1a;
  }
  .avatar--dark {
    background: linear-gradient(135deg, #3f3d38, #2d2b27);
    color: #ead9a0;
  }
  .avatar--light {
    background: linear-gradient(135deg, #f8f2e0, #f2e9c8);
    color: #9b7a25;
  }

  /* Actions */
  .actions {
    display: flex;
    gap: 10px;
    margin-top: 6px;
  }
  .btn-dark {
    flex: 1;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 7px;
    height: 46px;
    background: #0d0c0a;
    color: #fff;
    border: none;
    border-radius: 8px;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.18s;
  }
  .btn-dark:hover:not(:disabled) {
    background: #2d2b27;
  }
  .btn-dark:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  .btn-outline {
    flex: 1;
    height: 46px;
    background: #fff;
    color: #0d0c0a;
    border: 1.5px solid #eae8e4;
    border-radius: 8px;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.18s;
  }
  .btn-outline:hover:not(:disabled) {
    background: #f4f1e9;
    border-color: #d6d3ce;
  }
  .btn-outline:disabled {
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

  @media (max-width: 520px) {
    .modal-overlay {
      padding: 0;
      align-items: flex-end;
    }
    .modal-card {
      max-width: 100%;
      border-radius: 20px 20px 0 0;
      padding: 26px 20px 24px;
      max-height: 94vh;
      overflow-y: auto;
    }
    .actions {
      flex-direction: column-reverse;
    }
  }
</style>
