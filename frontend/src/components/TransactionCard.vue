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

      <div v-if="transaction.reactions?.length" class="tx-card__reactions">
        <button v-for="r in transaction.reactions" :key="r.emoji" class="reaction-pill">
          {{ r.emoji }} {{ r.count }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { computed } from 'vue'
  import UserAvatar from './UserAvatar.vue'

  const props = defineProps({
    transaction: { type: Object, required: true },
  })

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
</style>
