<template>
  <div class="conn-indicator" :class="{ 'conn-indicator--offline': !isConnected }">
    <span class="conn-indicator__dot"></span>
    <span class="conn-indicator__label">
      {{ isConnected ? 'Live' : 'Reconnecting...' }}
    </span>
  </div>
</template>

<script setup>
  defineProps({
    isConnected: { type: Boolean, default: false },
  })
</script>

<style scoped>
  .conn-indicator {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 10px;
    border-radius: 9999px;
    background: #eef7ee;
    border: 1px solid #8bc88b;
    font-size: 10px;
    font-weight: 600;
    color: #2a6b2a;
    letter-spacing: 0.5px;
  }

  .conn-indicator__dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #2a6b2a;
    animation: pulse 2s ease infinite;
  }

  .conn-indicator--offline {
    background: #fef5e8;
    border-color: #e8b87a;
    color: #9b6a25;
  }

  .conn-indicator--offline .conn-indicator__dot {
    background: #c48a2a;
  }

  @keyframes pulse {
    0%,
    100% {
      box-shadow: 0 0 0 2px rgba(42, 107, 42, 0.15);
    }
    50% {
      box-shadow: 0 0 0 5px rgba(42, 107, 42, 0.05);
    }
  }
</style>
