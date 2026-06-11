<template>
  <Teleport to="body">
    <Transition name="overlay">
      <div v-if="isOpen" class="modal-overlay" @click.self="close">
        <Transition name="modal">
          <div v-if="isOpen" class="modal-card" role="dialog" aria-modal="true">
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

            <h2 class="modal-title">Choose a card to pay from</h2>
            <p class="modal-sub">
              You have several cards in this group. Select which one to debit.
            </p>

            <div class="card-list">
              <button
                v-for="card in cards"
                :key="card.id"
                class="card-option"
                :class="{ 'card-option--active': chosen === card.id }"
                @click="chosen = card.id"
              >
                <span
                  class="card-option__radio"
                  :class="{ 'card-option__radio--on': chosen === card.id }"
                ></span>
                <span class="card-option__info">
                  <span class="card-option__pan">{{ card.masked_pan }}</span>
                  <span class="card-option__bal">{{ formatBalance(cardBalance(card)) }} UAH</span>
                </span>
              </button>
            </div>

            <div class="actions">
              <button type="button" class="btn-outline" @click="close">Cancel</button>
              <button type="button" class="btn-gold" :disabled="!chosen" @click="confirm">
                Confirm
              </button>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
  import { ref, watch } from 'vue'

  const props = defineProps({
    isOpen: { type: Boolean, required: true },
    cards: { type: Array, default: () => [] },
  })

  const emit = defineEmits(['close', 'select'])

  const chosen = ref('')

  watch(
    () => props.isOpen,
    (open) => {
      if (open) chosen.value = props.cards[0]?.id || ''
    },
  )

  function cardBalance(card) {
    return card.virtual_balance ?? card.effective_balance ?? card.balance
  }
  function formatBalance(value) {
    if (value == null) return '0.00'
    const num = typeof value === 'number' ? value : parseFloat(value)
    return Number.isNaN(num) ? String(value) : num.toFixed(2)
  }

  function confirm() {
    if (!chosen.value) return
    emit('select', chosen.value)
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
    z-index: 205;
    backdrop-filter: blur(4px);
    padding: 20px;
  }
  .modal-card {
    background: #fff;
    border-radius: 20px;
    box-shadow:
      0 20px 56px rgba(13, 12, 10, 0.16),
      0 0 0 1px rgba(184, 151, 58, 0.1);
    padding: 32px 32px 28px;
    width: 100%;
    max-width: 420px;
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
  }
  .modal-close:hover {
    background: #0d0c0a;
    color: #fff;
  }
  .modal-title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 22px;
    font-weight: 600;
    color: #0d0c0a;
    margin: 0 0 4px;
  }
  .modal-sub {
    font-size: 13px;
    color: #6b6860;
    margin: 0 0 20px;
    line-height: 1.6;
  }
  .card-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
    margin-bottom: 22px;
  }
  .card-option {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 14px;
    background: #faf8f3;
    border: 1.5px solid #eae8e4;
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.15s;
    text-align: left;
    width: 100%;
    font-family: 'DM Sans', system-ui, sans-serif;
  }
  .card-option:hover {
    border-color: #dfc876;
  }
  .card-option--active {
    border-color: #b8973a;
    background: #fbf7ec;
  }
  .card-option__radio {
    width: 18px;
    height: 18px;
    border-radius: 50%;
    border: 2px solid #d6d3ce;
    flex-shrink: 0;
    position: relative;
  }
  .card-option__radio--on {
    border-color: #b8973a;
  }
  .card-option__radio--on::after {
    content: '';
    position: absolute;
    inset: 3px;
    border-radius: 50%;
    background: #b8973a;
  }
  .card-option__info {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  .card-option__pan {
    font-size: 13px;
    font-weight: 600;
    color: #0d0c0a;
    font-family: 'DM Mono', 'Courier New', monospace;
  }
  .card-option__bal {
    font-size: 12px;
    color: #9b7a25;
  }
  .actions {
    display: flex;
    gap: 10px;
  }
  .btn-outline {
    flex: 1;
    height: 44px;
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
  .btn-outline:hover {
    background: #f4f1e9;
  }
  .btn-gold {
    flex: 1;
    height: 44px;
    background: linear-gradient(135deg, #b8973a, #c9a84c);
    color: #fff;
    border: none;
    border-radius: 8px;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.18s;
    box-shadow: 0 4px 16px rgba(184, 151, 58, 0.18);
  }
  .btn-gold:hover:not(:disabled) {
    background: linear-gradient(135deg, #9b7a25, #b8973a);
  }
  .btn-gold:disabled {
    opacity: 0.5;
    cursor: not-allowed;
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
