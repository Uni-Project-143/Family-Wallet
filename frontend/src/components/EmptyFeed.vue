<template>
  <div class="empty-feed">
    <svg width="56" height="56" viewBox="0 0 56 56" fill="none">
      <rect x="6" y="14" width="44" height="32" rx="3" stroke="#d6d3ce" stroke-width="1.5" />
      <path d="M6 22H50" stroke="#d6d3ce" stroke-width="1.5" />
      <circle cx="14" cy="30" r="1.5" fill="#d6d3ce" />
      <circle cx="20" cy="30" r="1.5" fill="#d6d3ce" />
    </svg>
    <h3 class="empty-feed__title">No transactions yet</h3>
    <p class="empty-feed__text">
      Connect your Monobank card to start tracking family expenses automatically.
    </p>
    <button class="btn-gold" @click="$emit('connect-card')">+ Connect Monobank Card</button>
  </div>
</template>

<script setup>
  defineEmits(['connect-card'])
</script>

<style scoped>
  .empty-feed {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    padding: 64px 24px;
    background: #fff;
    border: 1px dashed #d6d3ce;
    border-radius: 16px;
    text-align: center;
  }

  .empty-feed__title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 22px;
    font-weight: 600;
    color: #0d0c0a;
    margin: 4px 0 0;
  }

  .empty-feed__text {
    font-size: 14px;
    color: #6b6860;
    max-width: 320px;
    margin: 0 0 16px;
    line-height: 1.6;
  }

  .btn-gold {
    height: 44px;
    padding: 0 24px;
    background: linear-gradient(135deg, #b8973a, #c9a84c);
    color: #fff;
    border: none;
    border-radius: 8px;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.18s;
  }

  .btn-gold:hover {
    background: linear-gradient(135deg, #9b7a25, #b8973a);
    transform: translateY(-1px);
  }
</style>
