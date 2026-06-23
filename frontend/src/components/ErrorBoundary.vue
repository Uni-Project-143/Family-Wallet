<template>
  <slot v-if="!hasError" />

  <div v-else class="error-boundary" role="alert">
    <div class="error-boundary__card">
      <svg class="error-boundary__icon" width="40" height="40" viewBox="0 0 24 24" fill="none">
        <path
          d="M12 9v4m0 4h.01M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0Z"
          stroke="currentColor"
          stroke-width="1.6"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
      </svg>
      <h2 class="error-boundary__title">{{ strings.errors.boundaryTitle }}</h2>
      <p class="error-boundary__hint">{{ strings.errors.boundaryHint }}</p>
      <div class="error-boundary__actions">
        <button class="error-boundary__btn error-boundary__btn--primary" @click="retry">
          {{ strings.common.retry }}
        </button>
        <button class="error-boundary__btn" @click="reload">
          {{ strings.common.reload }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { ref, onErrorCaptured } from 'vue'
  import strings from '../locales/en'

  const hasError = ref(false)

  onErrorCaptured(() => {
    hasError.value = true
    return false
  })

  function retry() {
    hasError.value = false
  }

  function reload() {
    window.location.reload()
  }
</script>

<style scoped>
  .error-boundary {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 60vh;
    padding: 32px 16px;
  }

  .error-boundary__card {
    max-width: 420px;
    width: 100%;
    text-align: center;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(184, 151, 58, 0.22);
    border-radius: 14px;
    padding: 32px 28px;
  }

  .error-boundary__icon {
    color: #c4402a;
    margin-bottom: 14px;
  }

  .error-boundary__title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 24px;
    font-weight: 600;
    color: #1a1a1a;
    margin: 0 0 8px;
  }

  .error-boundary__hint {
    font-size: 14px;
    color: #6b6860;
    line-height: 1.5;
    margin: 0 0 22px;
  }

  .error-boundary__actions {
    display: flex;
    gap: 10px;
    justify-content: center;
    flex-wrap: wrap;
  }

  .error-boundary__btn {
    padding: 9px 20px;
    border-radius: 8px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    border: 1px solid #d6d3ce;
    background: #fff;
    color: #3a3833;
    transition: all 0.18s;
  }
  .error-boundary__btn:hover {
    background: #f4f2ee;
  }
  .error-boundary__btn--primary {
    background: linear-gradient(135deg, #b8973a, #c9a84c);
    border-color: transparent;
    color: #fff;
  }
  .error-boundary__btn--primary:hover {
    filter: brightness(1.05);
  }
</style>
