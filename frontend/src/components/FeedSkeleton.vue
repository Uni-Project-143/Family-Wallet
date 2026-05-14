<template>
  <div class="skeleton-wrap">
    <div v-for="i in count" :key="i" class="tx-skeleton">
      <div class="tx-skeleton__avatar"></div>
      <div class="tx-skeleton__body">
        <div class="tx-skeleton__line tx-skeleton__line--name"></div>
        <div class="tx-skeleton__line tx-skeleton__line--category"></div>
        <div class="tx-skeleton__line tx-skeleton__line--desc"></div>
        <div class="tx-skeleton__line tx-skeleton__line--date"></div>
      </div>
      <div class="tx-skeleton__amount"></div>
    </div>
  </div>
</template>

<script setup>
  defineProps({
    count: { type: Number, default: 5 },
  })
</script>

<style scoped>
  .skeleton-wrap {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }

  .tx-skeleton {
    display: flex;
    gap: 14px;
    padding: 16px 18px;
    background: #fff;
    border: 1px solid #eae8e4;
    border-radius: 12px;
  }

  .tx-skeleton__avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: linear-gradient(90deg, #ede9de 25%, #f4f1e9 50%, #ede9de 75%);
    background-size: 200% 100%;
    animation: shimmer 1.6s ease infinite;
    flex-shrink: 0;
  }

  .tx-skeleton__body {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .tx-skeleton__line {
    height: 12px;
    border-radius: 4px;
    background: linear-gradient(90deg, #ede9de 25%, #f4f1e9 50%, #ede9de 75%);
    background-size: 200% 100%;
    animation: shimmer 1.6s ease infinite;
  }

  .tx-skeleton__line--name {
    width: 35%;
  }
  .tx-skeleton__line--category {
    width: 28%;
  }
  .tx-skeleton__line--desc {
    width: 55%;
  }
  .tx-skeleton__line--date {
    width: 22%;
  }

  .tx-skeleton__amount {
    width: 70px;
    height: 18px;
    border-radius: 4px;
    background: linear-gradient(90deg, #ede9de 25%, #f4f1e9 50%, #ede9de 75%);
    background-size: 200% 100%;
    animation: shimmer 1.6s ease infinite;
    align-self: flex-start;
  }

  @keyframes shimmer {
    0% {
      background-position: 200% 0;
    }
    100% {
      background-position: -200% 0;
    }
  }
</style>
