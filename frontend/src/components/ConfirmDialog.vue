<template>
  <Teleport to="body">
    <Transition name="overlay">
      <div v-if="isOpen" class="confirm-overlay" @click.self="onCancel">
        <Transition name="modal">
          <div v-if="isOpen" class="confirm-card" role="alertdialog" aria-modal="true">
            <div class="confirm-icon" :class="`confirm-icon--${variant}`">
              <svg
                v-if="variant === 'danger'"
                width="24"
                height="24"
                viewBox="0 0 24 24"
                fill="none"
              >
                <path
                  d="M12 8V13M12 16V16.01M3 17.5L11 4.5C11.4 3.83 12.6 3.83 13 4.5L21 17.5C21.4 18.17 20.92 19 20 19H4C3.08 19 2.6 18.17 3 17.5Z"
                  stroke="currentColor"
                  stroke-width="1.8"
                  stroke-linecap="round"
                />
              </svg>
              <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="1.8" />
                <path
                  d="M12 8V12M12 16V16.01"
                  stroke="currentColor"
                  stroke-width="1.8"
                  stroke-linecap="round"
                />
              </svg>
            </div>

            <h3 class="confirm-title">{{ title }}</h3>
            <p class="confirm-message">{{ message }}</p>

            <div class="confirm-actions">
              <button type="button" class="btn-secondary" :disabled="isLoading" @click="onCancel">
                {{ cancelText }}
              </button>
              <button
                type="button"
                :class="variant === 'danger' ? 'btn-danger' : 'btn-gold'"
                :disabled="isLoading"
                @click="onConfirm"
              >
                <template v-if="!isLoading">{{ confirmText }}</template>
                <template v-else>
                  <svg class="spinner" width="16" height="16" viewBox="0 0 16 16" fill="none">
                    <circle cx="8" cy="8" r="6" stroke="rgba(255,255,255,.3)" stroke-width="2" />
                    <path
                      d="M8 2A6 6 0 0 1 14 8"
                      stroke="white"
                      stroke-width="2"
                      stroke-linecap="round"
                    />
                  </svg>
                </template>
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
  defineProps({
    isOpen: { type: Boolean, default: false },
    title: { type: String, default: 'Are you sure?' },
    message: { type: String, default: '' },
    confirmText: { type: String, default: 'Yes' },
    cancelText: { type: String, default: 'Cancel' },
    variant: { type: String, default: 'warning' },
    isLoading: { type: Boolean, default: false },
  })

  const emit = defineEmits(['confirm', 'cancel'])

  function onConfirm() {
    emit('confirm')
  }
  function onCancel() {
    emit('cancel')
  }
</script>

<style scoped>
  .confirm-overlay {
    position: fixed;
    inset: 0;
    background: rgba(13, 12, 10, 0.52);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 250;
    backdrop-filter: blur(4px);
    padding: 20px;
  }

  .confirm-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 32px 28px 24px;
    width: 100%;
    max-width: 400px;
    box-shadow: 0 20px 56px rgba(13, 12, 10, 0.2);
    text-align: center;
  }

  .confirm-icon {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 16px;
  }

  .confirm-icon--danger {
    background: #fef0ed;
    color: #c4402a;
  }

  .confirm-icon--warning {
    background: #fbf7ec;
    color: #b8973a;
  }

  .confirm-title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 20px;
    font-weight: 600;
    color: #0d0c0a;
    margin: 0 0 8px;
  }

  .confirm-message {
    font-size: 14px;
    color: #6b6860;
    margin: 0 0 24px;
    line-height: 1.6;
  }

  .confirm-actions {
    display: flex;
    gap: 10px;
  }

  .btn-secondary,
  .btn-gold,
  .btn-danger {
    flex: 1;
    height: 44px;
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
  }

  .btn-secondary {
    background: #ffffff;
    color: #6b6860;
    border: 1.5px solid #d6d3ce;
  }

  .btn-secondary:hover:not(:disabled) {
    background: #f4f1e9;
  }

  .btn-gold {
    background: linear-gradient(135deg, #b8973a, #c9a84c);
    color: #ffffff;
  }

  .btn-danger {
    background: #c4402a;
    color: #ffffff;
  }

  .btn-danger:hover:not(:disabled) {
    background: #a83423;
  }

  .btn-secondary:disabled,
  .btn-gold:disabled,
  .btn-danger:disabled {
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
    transition: opacity 0.25s;
  }
  .overlay-enter-from,
  .overlay-leave-to {
    opacity: 0;
  }

  .modal-enter-active,
  .modal-leave-active {
    transition:
      opacity 0.25s,
      transform 0.25s;
  }
  .modal-enter-from,
  .modal-leave-to {
    opacity: 0;
    transform: scale(0.94) translateY(8px);
  }
</style>
