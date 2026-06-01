<template>
  <Teleport to="body">
    <Transition name="overlay">
      <div v-if="isOpen" class="modal-overlay" @click.self="close">
        <Transition name="modal">
          <div v-if="isOpen" ref="modalRootRef" class="modal-card" role="dialog" aria-modal="true">
            <!-- Close button -->
            <button class="modal-close" :disabled="isSubmitting" @click="close" aria-label="Close">
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
            <h2 class="modal-title">Переказ між картками</h2>
            <p class="modal-sub">
              Виконайте миттєвий переказ між картками учасників вашої сімейної групи.
            </p>

            <form class="form" @submit.prevent="handleSubmit">
              <!-- From card -->
              <div class="field">
                <label class="field__label" for="from-card">Картка-відправник</label>
                <div class="i-field-wrap" :class="{ 'i-field-wrap--error': errors.fromCardId }">
                  <select
                    id="from-card"
                    v-model="fromCardId"
                    class="i-field"
                    :disabled="isSubmitting"
                    @blur="validateFromCard"
                    @change="onFromCardChange"
                  >
                    <option :value="''" disabled>Виберіть картку</option>
                    <option v-for="card in userCards" :key="card.id" :value="card.id">
                      {{ card.masked_pan }} — {{ formatBalance(card.effective_balance) }} UAH
                    </option>
                  </select>
                </div>
                <Transition name="fade-down">
                  <p v-if="errors.fromCardId" class="i-error">{{ errors.fromCardId }}</p>
                </Transition>
              </div>

              <!-- To card -->
              <div class="field">
                <label class="field__label" for="to-card">Картка-отримувач</label>
                <div class="i-field-wrap" :class="{ 'i-field-wrap--error': errors.toCardId }">
                  <select
                    id="to-card"
                    v-model="toCardId"
                    class="i-field"
                    :disabled="isSubmitting"
                    @blur="validateToCard"
                  >
                    <option :value="''" disabled>Виберіть картку</option>
                    <option v-for="card in availableToCards" :key="card.id" :value="card.id">
                      <template v-if="card.owner_full_name">
                        {{ card.owner_full_name }} — {{ card.masked_pan }}
                      </template>
                      <template v-else>
                        {{ card.masked_pan }}
                      </template>
                    </option>
                  </select>
                </div>
                <Transition name="fade-down">
                  <p v-if="errors.toCardId" class="i-error">{{ errors.toCardId }}</p>
                </Transition>
              </div>

              <!-- Amount -->
              <div class="field">
                <label class="field__label" for="amount">Сума</label>
                <div class="i-field-wrap" :class="{ 'i-field-wrap--error': errors.amount }">
                  <input
                    id="amount"
                    v-model="amount"
                    class="i-field"
                    type="number"
                    step="0.01"
                    min="0.01"
                    placeholder="0.00 UAH"
                    :disabled="isSubmitting"
                    @blur="validateAmount"
                  />
                </div>
                <Transition name="fade-down">
                  <p v-if="errors.amount" class="i-error">{{ errors.amount }}</p>
                </Transition>
              </div>

              <!-- Description -->
              <div class="field">
                <label class="field__label" for="description">
                  Опис <span class="field__hint">(необовʼязково)</span>
                </label>
                <div class="i-field-wrap">
                  <input
                    id="description"
                    v-model="description"
                    class="i-field"
                    type="text"
                    maxlength="500"
                    placeholder="За що переказ?"
                    :disabled="isSubmitting"
                  />
                </div>
              </div>

              <!-- Category -->
              <div class="field">
                <label class="field__label" for="category">
                  Категорія <span class="field__hint">(необовʼязково)</span>
                </label>
                <div class="i-field-wrap">
                  <select
                    id="category"
                    v-model="categoryId"
                    class="i-field"
                    :disabled="isSubmitting"
                  >
                    <option :value="null">Без категорії</option>
                    <option v-for="cat in categories" :key="cat.id" :value="cat.id">
                      {{ cat.name }}
                    </option>
                  </select>
                </div>
              </div>

              <!-- Server error -->
              <Transition name="fade-down">
                <p v-if="serverError" class="server-error">{{ serverError }}</p>
              </Transition>

              <!-- Actions -->
              <div class="actions">
                <button
                  type="button"
                  class="btn-secondary"
                  :disabled="isSubmitting"
                  @click="close"
                >
                  Скасувати
                </button>
                <button type="submit" class="btn-gold" :disabled="isSubmitting">
                  <span v-if="!isSubmitting">Виконати переказ</span>
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
            </form>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
  import { ref, computed, reactive, watch } from 'vue'
  import { createTransfer } from '../services/transactionService'
  import { useFocusTrap } from '../composables/useFocusTrap'

  const props = defineProps({
    isOpen: {
      type: Boolean,
      required: true,
    },
    userCards: {
      type: Array,
      default: () => [],
    },
    groupCards: {
      type: Array,
      default: () => [],
    },
    categories: {
      type: Array,
      default: () => [],
    },
  })

  const emit = defineEmits(['close', 'success', 'toast'])

  const modalRootRef = ref(null)
  useFocusTrap(modalRootRef, () => props.isOpen)

  const fromCardId = ref('')
  const toCardId = ref('')
  const amount = ref('')
  const description = ref('')
  const categoryId = ref(null)
  const isSubmitting = ref(false)
  const serverError = ref('')

  const errors = reactive({
    fromCardId: '',
    toCardId: '',
    amount: '',
  })

  const availableToCards = computed(() =>
    props.groupCards.filter((c) => c.id !== fromCardId.value),
  )

  const fromCard = computed(() => props.userCards.find((c) => c.id === fromCardId.value) || null)

  function formatBalance(value) {
    if (value == null) return '0.00'
    const num = typeof value === 'number' ? value : parseFloat(value)
    if (Number.isNaN(num)) return String(value)
    return num.toFixed(2)
  }

  function resetForm() {
    fromCardId.value = props.userCards[0]?.id || ''
    toCardId.value = ''
    amount.value = ''
    description.value = ''
    categoryId.value = null
    serverError.value = ''
    errors.fromCardId = ''
    errors.toCardId = ''
    errors.amount = ''
    isSubmitting.value = false
  }

  watch(
    () => props.isOpen,
    (open) => {
      if (open) resetForm()
    },
    { immediate: true },
  )

  function onFromCardChange() {
    // якщо вибрана картка-отримувач збігається з відправником — скинути
    if (toCardId.value && toCardId.value === fromCardId.value) {
      toCardId.value = ''
    }
    validateFromCard()
  }

  function validateFromCard() {
    if (!fromCardId.value) {
      errors.fromCardId = 'Виберіть картку для переказу'
      return false
    }
    errors.fromCardId = ''
    return true
  }

  function validateToCard() {
    if (!toCardId.value) {
      errors.toCardId = 'Виберіть картку-отримувач'
      return false
    }
    if (toCardId.value === fromCardId.value) {
      errors.toCardId = 'Картка-отримувач має відрізнятися від відправника'
      return false
    }
    errors.toCardId = ''
    return true
  }

  const AMOUNT_REGEX = /^\d+(\.\d{1,2})?$/

  function validateAmount() {
    const raw = amount.value
    if (raw === '' || raw === null || raw === undefined) {
      errors.amount = 'Введіть суму переказу'
      return false
    }
    const str = String(raw)
    if (!AMOUNT_REGEX.test(str)) {
      errors.amount = 'Сума може містити максимум 2 знаки після коми'
      return false
    }
    const num = parseFloat(str)
    if (Number.isNaN(num) || num <= 0) {
      errors.amount = 'Сума має бути більше 0'
      return false
    }
    if (fromCard.value && fromCard.value.effective_balance != null) {
      const balance = parseFloat(fromCard.value.effective_balance)
      if (!Number.isNaN(balance) && num > balance) {
        errors.amount = 'Недостатньо коштів на картці-відправнику'
        return false
      }
    }
    errors.amount = ''
    return true
  }

  function validateAll() {
    const ok1 = validateFromCard()
    const ok2 = validateToCard()
    const ok3 = validateAmount()
    return ok1 && ok2 && ok3
  }

  async function handleSubmit() {
    serverError.value = ''
    if (!validateAll()) return

    isSubmitting.value = true
    try {
      const result = await createTransfer({
        from_card_id: fromCardId.value,
        to_card_id: toCardId.value,
        amount: amount.value,
        description: description.value || null,
        category_id: categoryId.value || null,
      })
      emit('toast', { message: 'Переказ успішно виконано', type: 'success' })
      emit('success', result)
      close()
    } catch (err) {
      const detail =
        err.response?.data?.message || err.response?.data?.detail || 'Не вдалося виконати переказ'
      serverError.value = typeof detail === 'string' ? detail : 'Не вдалося виконати переказ'
      emit('toast', { message: serverError.value, type: 'error' })
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
    margin: 0 0 24px;
    line-height: 1.6;
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

  .field__hint {
    font-weight: 400;
    color: #b0ada7;
    letter-spacing: 0;
    text-transform: none;
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

  select.i-field {
    appearance: none;
    -webkit-appearance: none;
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='10' height='6' viewBox='0 0 10 6' fill='none'><path d='M1 1L5 5L9 1' stroke='%236b6860' stroke-width='1.4' stroke-linecap='round' stroke-linejoin='round'/></svg>");
    background-repeat: no-repeat;
    background-position: right 14px center;
    padding-right: 36px;
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

  .i-error {
    font-size: 12px;
    color: #c4402a;
    margin-top: 5px;
  }

  .server-error {
    font-size: 13px;
    color: #c4402a;
    background: #fbecea;
    border: 1px solid #f3cfc8;
    padding: 10px 12px;
    border-radius: 8px;
    margin: 0;
  }

  .actions {
    display: flex;
    justify-content: flex-end;
    gap: 10px;
    margin-top: 8px;
  }

  .btn-secondary {
    height: 44px;
    padding: 0 20px;
    background: #f4f1e9;
    color: #0d0c0a;
    border: 1px solid #eae8e4;
    border-radius: 8px;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.18s;
  }

  .btn-secondary:hover:not(:disabled) {
    background: #eae8e4;
  }

  .btn-secondary:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }

  .btn-gold {
    display: inline-flex;
    align-items: center;
    justify-content: center;
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
    min-width: 160px;
  }

  .btn-gold:hover:not(:disabled) {
    background: linear-gradient(135deg, #9b7a25, #b8973a);
    transform: translateY(-1px);
  }

  .btn-gold:disabled {
    opacity: 0.5;
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
    .actions {
      flex-direction: column-reverse;
    }
    .btn-secondary,
    .btn-gold {
      width: 100%;
    }
  }
</style>
