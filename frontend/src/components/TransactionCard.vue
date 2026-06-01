<template>
  <div class="tx-card">
    <UserAvatar :avatar-url="transaction.avatar" :full-name="transaction.display_name" size="md" />

    <div class="tx-card__body">
      <div class="tx-card__header">
        <div>
          <div class="tx-card__name">
            {{ authorDisplayName }}
            <span v-if="transaction.is_secret_gift" class="tx-card__gift-badge">Gift</span>
          </div>

          <div class="tx-card__category">
            <span v-if="transaction.category_emoji">{{ transaction.category_emoji }}</span>
            {{ transaction.category_name || 'Other' }}
          </div>

          <span
            v-if="transaction.is_virtual"
            class="tx-card__virtual-badge"
            title="Внутрішній переказ"
          >
            ↔ Переказ
          </span>

          <div v-if="transaction.description" class="tx-card__desc">
            {{ transaction.description }}
          </div>

          <div class="tx-card__date">{{ relativeTime }}</div>
        </div>

        <div class="tx-card__amount" :class="{ 'tx-card__amount--income': isIncome }">
          {{ formattedAmount }}
          <span class="tx-card__currency">{{ transaction.currency }}</span>
        </div>
      </div>

      <div class="tx-card__reactions">
        <button
          v-for="r in displayReactions"
          :key="r.emoji"
          class="reaction-pill"
          :class="{ 'reaction-pill--mine': r.mine }"
          @click="onToggle(r.emoji)"
        >
          {{ r.emoji }} {{ r.count }}
        </button>

        <!-- Кнопка-пікер реакцій (Telegram-style) -->
        <div class="reaction-picker">
          <button
            class="reaction-add"
            :class="{ 'reaction-add--open': isPickerOpen }"
            aria-label="Додати реакцію"
            @click="togglePicker"
          >
            <svg width="14" height="14" viewBox="0 0 16 16" fill="none">
              <circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.3" />
              <path
                d="M5.8 9.4C6.2 10.2 7 10.8 8 10.8C9 10.8 9.8 10.2 10.2 9.4"
                stroke="currentColor"
                stroke-width="1.3"
                stroke-linecap="round"
              />
              <circle cx="6" cy="6.4" r="0.9" fill="currentColor" />
              <circle cx="10" cy="6.4" r="0.9" fill="currentColor" />
            </svg>
          </button>

          <Transition name="picker">
            <div v-if="isPickerOpen" class="reaction-menu" role="menu">
              <button
                v-for="emoji in REACTION_EMOJIS"
                :key="emoji"
                class="reaction-menu__item"
                :class="{ 'reaction-menu__item--active': myReaction === emoji }"
                :aria-label="`Реакція ${emoji}`"
                @click="onPick(emoji)"
              >
                {{ emoji }}
              </button>
            </div>
          </Transition>
        </div>
      </div>
    </div>

    <!-- Прозорий бекдроп: клік поза пікером закриває його -->
    <div v-if="isPickerOpen" class="reaction-backdrop" @click="closePicker" />
  </div>
</template>

<script setup>
  import { computed, ref } from 'vue'
  import UserAvatar from './UserAvatar.vue'
  import { useReactions, useDisplayReactions, REACTION_EMOJIS } from '../composables/useReactions'

  const props = defineProps({
    transaction: { type: Object, required: true },
  })

  // ─── Емодзі-реакції (Telegram-style) ───
  const { getMyReaction, toggleReaction } = useReactions()
  const displayReactions = useDisplayReactions(() => props.transaction)
  const myReaction = computed(() => getMyReaction(props.transaction.id))

  const isPickerOpen = ref(false)

  function togglePicker() {
    isPickerOpen.value = !isPickerOpen.value
  }
  function closePicker() {
    isPickerOpen.value = false
  }
  function onPick(emoji) {
    toggleReaction(props.transaction.id, emoji)
    closePicker()
  }
  function onToggle(emoji) {
    // Клік по наявній реакції-пілюлі також ставить/знімає її
    toggleReaction(props.transaction.id, emoji)
  }

  const authorDisplayName = computed(() => {
    return props.transaction.display_name || 'Невідомий учасник'
  })

  const isIncome = computed(() => Number(props.transaction.amount) > 0)

  const formattedAmount = computed(() => {
    const num = Number(props.transaction.amount)
    if (Number.isNaN(num)) return '—'
    const sign = num > 0 ? '+' : num < 0 ? '−' : ''
    return `${sign}${Math.abs(num).toLocaleString('uk-UA')}`
  })

  /**
   * Відносний час: "2 хв тому", "3 год тому", "вчора", "12 кві".
   */
  const relativeTime = computed(() => {
    if (!props.transaction.timestamp) return ''
    const txDate = new Date(props.transaction.timestamp)
    const diffMs = Date.now() - txDate.getTime()
    const minutes = Math.floor(diffMs / 60000)

    if (minutes < 1) return 'щойно'
    if (minutes < 60) return `${minutes} хв тому`

    const hours = Math.floor(minutes / 60)
    if (hours < 24) return `${hours} год тому`

    const days = Math.floor(hours / 24)
    if (days === 1) return 'вчора'
    if (days < 7) return `${days} дн тому`

    return txDate.toLocaleDateString('uk-UA', { day: 'numeric', month: 'short' })
  })
</script>

<style scoped>
  .tx-card {
    position: relative;
    display: flex;
    gap: 14px;
    padding: 16px 18px;
    background: #fff;
    border: 1px solid #eae8e4;
    border-radius: 12px;
    margin-bottom: 10px;
    box-shadow: 0 1px 2px rgba(13, 12, 10, 0.06);
    transition:
      box-shadow 0.18s,
      transform 0.18s;
  }

  .tx-card:hover {
    box-shadow: 0 2px 8px rgba(13, 12, 10, 0.08);
    transform: translateY(-1px);
  }

  .tx-card__body {
    flex: 1;
  }

  .tx-card__header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }

  .tx-card__name {
    font-size: 13px;
    font-weight: 600;
    color: #0d0c0a;
    margin-bottom: 4px;
  }

  .tx-card__category {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 2px 10px;
    border-radius: 9999px;
    background: #fbf7ec;
    border: 1px solid #f2e9c8;
    font-size: 11px;
    font-weight: 500;
    color: #9b7a25;
    margin-bottom: 4px;
  }

  .tx-card__desc {
    font-size: 12px;
    color: #6b6860;
    margin-bottom: 2px;
  }

  .tx-card__date {
    font-size: 11px;
    color: #b0ada7;
    font-family: 'DM Mono', 'Courier New', monospace;
  }

  .tx-card__amount {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 18px;
    font-weight: 600;
    color: #c4402a;
    text-align: right;
    white-space: nowrap;
  }

  .tx-card__amount--income {
    color: #2a6b2a;
  }

  .tx-card__currency {
    font-size: 12px;
    font-weight: 400;
    color: #b0ada7;
    margin-left: 2px;
  }

  .tx-card__reactions {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 10px;
    flex-wrap: wrap;
  }

  .reaction-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 9999px;
    background: #f4f1e9;
    border: 1px solid #eae8e4;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.18s;
    font-family: 'DM Sans', system-ui, sans-serif;
  }

  .reaction-pill:hover {
    background: #fbf7ec;
    border-color: #f2e9c8;
  }

  /* Реакція, яку поставив поточний користувач */
  .reaction-pill--mine {
    background: #fbf7ec;
    border-color: #dfc876;
    color: #9b7a25;
    font-weight: 600;
  }

  /* ── Пікер реакцій ── */
  .reaction-picker {
    position: relative;
    display: inline-flex;
  }

  .reaction-add {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 26px;
    border-radius: 9999px;
    border: 1px dashed #d6d3ce;
    color: #b0ada7;
    background: none;
    cursor: pointer;
    transition: all 0.18s;
  }
  .reaction-add:hover,
  .reaction-add--open {
    color: #9b7a25;
    border-color: #dfc876;
    background: #fbf7ec;
  }

  .reaction-menu {
    position: absolute;
    bottom: calc(100% + 8px);
    left: 0;
    z-index: 30;
    display: flex;
    gap: 2px;
    padding: 6px;
    background: #fff;
    border: 1px solid #eae8e4;
    border-radius: 9999px;
    box-shadow: 0 8px 24px rgba(13, 12, 10, 0.16);
  }

  .reaction-menu__item {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    border: none;
    background: none;
    font-size: 18px;
    line-height: 1;
    cursor: pointer;
    transition:
      transform 0.12s ease,
      background 0.12s ease;
  }
  .reaction-menu__item:hover {
    background: #f4f1e9;
    transform: scale(1.25);
  }
  .reaction-menu__item--active {
    background: #fbf7ec;
    box-shadow: inset 0 0 0 1.5px #dfc876;
  }

  /* Прозорий бекдроп для закриття по кліку поза пікером */
  .reaction-backdrop {
    position: fixed;
    inset: 0;
    z-index: 20;
  }

  .picker-enter-active,
  .picker-leave-active {
    transition:
      opacity 0.15s ease,
      transform 0.15s ease;
    transform-origin: bottom left;
  }
  .picker-enter-from,
  .picker-leave-to {
    opacity: 0;
    transform: translateY(6px) scale(0.92);
  }
  .tx-card__gift-badge {
    display: inline-block;
    margin-left: 6px;
    padding: 1px 8px;
    border-radius: 9999px;
    background: linear-gradient(135deg, #b8973a, #c9a84c);
    color: #fff;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    vertical-align: middle;
  }

  .tx-card__virtual-badge {
    display: inline-block;
    margin-left: 6px;
    font-size: 0.75rem;
    padding: 2px 6px;
    border-radius: 4px;
    background-color: rgba(99, 102, 241, 0.1);
    color: #4f46e5;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-weight: 500;
    vertical-align: middle;
  }
</style>
