<template>
  <Teleport to="body">
    <Transition name="overlay">
      <div v-if="isOpen" class="reminder-overlay" @click.self="$emit('later')">
        <Transition name="modal">
          <div
            v-if="isOpen"
            ref="modalRootRef"
            class="reminder-card"
            role="dialog"
            aria-modal="true"
          >
            <div class="reminder-icon" aria-hidden="true">
              <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                <rect
                  x="4"
                  y="9"
                  width="24"
                  height="16"
                  rx="2"
                  stroke="#b8973a"
                  stroke-width="1.6"
                />
                <path d="M4 14H28" stroke="#b8973a" stroke-width="1.6" />
                <circle cx="9" cy="20" r="1.2" fill="#b8973a" />
                <circle cx="13" cy="20" r="1.2" fill="#b8973a" />
              </svg>
            </div>
            <h2 class="reminder-title">Don't forget your card</h2>
            <p class="reminder-text">
              Connect a Monobank card to start tracking your family's expenses automatically.
            </p>
            <div class="reminder-actions">
              <button class="btn-secondary" @click="$emit('later')">Later</button>
              <button class="btn-gold" @click="$emit('connect-now')">Connect now</button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
  import { ref } from 'vue'
  import { useFocusTrap } from '../composables/useFocusTrap'

  const props = defineProps({
    isOpen: { type: Boolean, default: false },
  })

  const emit = defineEmits(['connect-now', 'later'])

  const modalRootRef = ref(null)
  useFocusTrap(modalRootRef, () => props.isOpen)
</script>

<style scoped>
  .reminder-overlay {
    position: fixed;
    inset: 0;
    background: rgba(13, 12, 10, 0.55);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
    padding: 16px;
  }

  .reminder-card {
    background: #fff;
    border-radius: 14px;
    padding: 32px 28px 24px;
    width: 100%;
    max-width: 380px;
    text-align: center;
    box-shadow: 0 16px 48px rgba(13, 12, 10, 0.24);
    font-family: 'DM Sans', system-ui, sans-serif;
  }

  .reminder-icon {
    width: 56px;
    height: 56px;
    margin: 0 auto 14px;
    background: #fbf7ec;
    border: 1px solid #f2e9c8;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .reminder-title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 22px;
    font-weight: 600;
    color: #0d0c0a;
    margin: 0 0 10px;
  }

  .reminder-text {
    font-size: 14px;
    color: #6b6860;
    line-height: 1.55;
    margin: 0 0 22px;
  }

  .reminder-actions {
    display: flex;
    gap: 10px;
  }

  .btn-secondary,
  .btn-gold {
    flex: 1;
    height: 42px;
    border-radius: 8px;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.18s;
  }

  .btn-secondary {
    background: #fff;
    border: 1px solid #d6d3ce;
    color: #6b6860;
  }

  .btn-secondary:hover {
    background: #f4f1e9;
    border-color: #b0ada7;
  }

  .btn-gold {
    background: linear-gradient(135deg, #b8973a, #c9a84c);
    border: none;
    color: #fff;
  }

  .btn-gold:hover {
    background: linear-gradient(135deg, #9b7a25, #b8973a);
    transform: translateY(-1px);
  }

  .overlay-enter-active,
  .overlay-leave-active {
    transition: opacity 0.2s ease;
  }

  .overlay-enter-from,
  .overlay-leave-to {
    opacity: 0;
  }

  .modal-enter-active,
  .modal-leave-active {
    transition: all 0.22s ease;
  }

  .modal-enter-from,
  .modal-leave-to {
    opacity: 0;
    transform: translateY(8px) scale(0.98);
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
</style>
