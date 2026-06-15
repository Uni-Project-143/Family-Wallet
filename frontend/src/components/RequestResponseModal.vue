<template>
  <Teleport to="body">
    <Transition name="overlay">
      <div v-if="isOpen" class="modal-overlay" @click.self="close">
        <Transition name="modal">
          <div v-if="isOpen" class="modal-card" role="dialog" aria-modal="true">
            <div class="rr-icon" :class="`rr-icon--${isAccepted ? 'ok' : 'no'}`">
              <span v-if="isAccepted">✅</span>
              <span v-else>✖</span>
            </div>

            <h2 class="modal-title">
              {{ isAccepted ? 'Request Accepted' : 'Request Declined' }}
            </h2>

            <p class="modal-msg">
              <strong>{{ responderName }}</strong>
              {{ isAccepted ? 'confirmed' : 'declined' }} your request for
              <strong>{{ formattedAmount }} UAH</strong>.
            </p>

            <button class="btn-gold" @click="close">Got it</button>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
  import { computed } from 'vue'

  const props = defineProps({
    isOpen: { type: Boolean, required: true },
    status: { type: String, default: 'ACCEPTED' },
    responderName: { type: String, default: 'A group member' },
    amount: { type: [Number, String], default: 0 },
  })

  const emit = defineEmits(['close'])

  const isAccepted = computed(() => props.status === 'ACCEPTED')

  const formattedAmount = computed(() => {
    const num = Number(props.amount)
    if (Number.isNaN(num)) return String(props.amount)
    return new Intl.NumberFormat('uk-UA').format(num)
  })

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
    z-index: 210;
    backdrop-filter: blur(4px);
    padding: 20px;
  }

  .modal-card {
    background: #ffffff;
    border-radius: 20px;
    box-shadow:
      0 20px 56px rgba(13, 12, 10, 0.16),
      0 0 0 1px rgba(184, 151, 58, 0.1);
    padding: 32px 32px 28px;
    width: 100%;
    max-width: 400px;
    position: relative;
    border-top: 3px solid #b8973a;
    text-align: center;
  }

  .rr-icon {
    width: 56px;
    height: 56px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 26px;
    margin: 0 auto 16px;
  }
  .rr-icon--ok {
    background: #eef7ee;
  }
  .rr-icon--no {
    background: #fef0ed;
    color: #c4402a;
  }

  .modal-title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 22px;
    font-weight: 600;
    color: #0d0c0a;
    margin: 0 0 8px;
  }

  .modal-msg {
    font-size: 14px;
    color: #6b6860;
    line-height: 1.6;
    margin: 0 0 22px;
  }
  .modal-msg strong {
    color: #0d0c0a;
    font-weight: 600;
  }

  .btn-gold {
    width: 100%;
    height: 46px;
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
  .btn-gold:hover {
    background: linear-gradient(135deg, #9b7a25, #b8973a);
    transform: translateY(-1px);
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
