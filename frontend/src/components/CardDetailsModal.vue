<template>
  <Teleport to="body">
    <Transition name="overlay">
      <div v-if="isOpen" class="modal-overlay" @click.self="close">
        <Transition name="modal">
          <div v-if="isOpen" ref="modalRootRef" class="modal-card" role="dialog" aria-modal="true">
            <h2 class="modal-title">Card Details</h2>
            <p class="modal-sub">Full information about this connected card.</p>

            <div v-if="card" class="details-list">
              <div class="details-row">
                <span class="details-row__label">Bank</span>
                <span class="details-row__value">Monobank</span>
              </div>

              <div class="details-row">
                <span class="details-row__label">Owner</span>
                <span class="details-row__value">
                  {{ card.owner_full_name || 'Unknown' }}
                </span>
              </div>

              <div class="details-row">
                <span class="details-row__label">Card number</span>
                <span class="details-row__value details-row__value--mono">
                  {{ card.masked_pan }}
                </span>
              </div>

              <div v-if="isOwnCard" class="details-row">
                <span class="details-row__label">Balance</span>
                <span class="details-row__value details-row__value--accent">
                  {{
                    formatBalance(card.virtual_balance ?? card.effective_balance ?? card.balance)
                  }}
                  <span class="details-row__currency">UAH</span>
                </span>
              </div>

              <div class="details-row">
                <span class="details-row__label">Status</span>
                <span
                  class="status-badge"
                  :class="`status-badge--${(card.status || '').toLowerCase()}`"
                >
                  {{ card.status }}
                </span>
              </div>

              <div v-if="!isOwnCard" class="privacy-note">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                  <path
                    d="M7 1L2 3V6.5C2 9.5 4.3 12.1 7 13C9.7 12.1 12 9.5 12 6.5V3L7 1Z"
                    stroke="currentColor"
                    stroke-width="1.3"
                  />
                </svg>
                Balance is visible only to the card owner.
              </div>
            </div>

            <div class="actions">
              <button type="button" class="btn-secondary" @click="close">Close</button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
  import { ref, computed } from 'vue'
  import { useAuth } from '../composables/useAuth'
  import { useFocusTrap } from '../composables/useFocusTrap'

  const props = defineProps({
    isOpen: { type: Boolean, default: false },
    card: { type: Object, default: null },
  })

  const emit = defineEmits(['close'])

  const modalRootRef = ref(null)
  useFocusTrap(modalRootRef, () => props.isOpen)

  const { currentUser } = useAuth()

  const isOwnCard = computed(() => {
    return props.card?.user_id === currentUser.value?.id
  })

  function formatBalance(balance) {
    const num = Number(balance)
    if (isNaN(num)) return balance
    return new Intl.NumberFormat('uk-UA', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(num)
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
    padding: 36px 36px 28px;
    width: 100%;
    max-width: 440px;
    position: relative;
    border-top: 3px solid #b8973a;
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

  .details-list {
    display: flex;
    flex-direction: column;
    gap: 14px;
    margin-bottom: 24px;
  }

  .details-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 12px 14px;
    background: #faf8f3;
    border-radius: 8px;
    border: 1px solid #eae8e4;
  }

  .details-row__label {
    font-size: 11px;
    font-weight: 600;
    color: #6b6860;
    letter-spacing: 0.7px;
    text-transform: uppercase;
  }

  .details-row__value {
    font-size: 14px;
    font-weight: 500;
    color: #0d0c0a;
  }
  .details-row__value--mono {
    font-family: 'DM Mono', 'Courier New', monospace;
    font-size: 13px;
  }
  .details-row__value--accent {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 20px;
    font-weight: 600;
  }
  .details-row__currency {
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 11px;
    font-weight: 500;
    color: #b0ada7;
    margin-left: 4px;
  }

  .status-badge {
    display: inline-flex;
    align-items: center;
    height: 22px;
    padding: 0 10px;
    border-radius: 9999px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.7px;
    text-transform: uppercase;
  }
  .status-badge--active {
    background: #eef7ee;
    color: #2a6b2a;
    border: 1px solid #8bc88b;
  }
  .status-badge--inactive {
    background: #f4f1e9;
    color: #6b6860;
    border: 1px solid #d6d3ce;
  }

  .privacy-note {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 14px;
    background: #fbf7ec;
    border: 1px solid #f2e9c8;
    border-radius: 8px;
    font-size: 12px;
    color: #9b7a25;
    font-style: italic;
  }

  .actions {
    display: flex;
    justify-content: flex-end;
  }

  .btn-secondary {
    padding: 0 32px;
    height: 44px;
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
  .btn-secondary:hover {
    background: #f4f1e9;
    border-color: #b0ada7;
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
  }

  @media (max-width: 560px) {
    .details-row {
      padding: 10px 12px;
    }
    .details-row__value--accent {
      font-size: 18px;
    }
  }
</style>
