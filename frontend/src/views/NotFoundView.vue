<template>
  <div class="nf-page">
    <div class="nf-card">
      <div class="nf-code">404</div>
      <h1 class="nf-title">Page not found</h1>
      <p class="nf-text">
        The page you're looking for doesn't exist or may have been moved.
      </p>
      <div class="nf-actions">
        <button class="nf-btn nf-btn--ghost" @click="goBack">← Go back</button>
        <button class="nf-btn nf-btn--gold" @click="goHome">Go to {{ homeLabel }}</button>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { computed } from 'vue'
  import { useRouter } from 'vue-router'

  const router = useRouter()

  const isAuthenticated = computed(() => !!localStorage.getItem('accessToken'))
  const homeLabel = computed(() => (isAuthenticated.value ? 'Feed' : 'Login'))

  function goHome() {
    // '/' редіректить на /feed або /login залежно від авторизації
    router.push('/')
  }

  function goBack() {
    // History API: якщо є куди — назад, інакше на головну
    if (window.history.length > 1) router.back()
    else goHome()
  }
</script>

<style scoped>
  .nf-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #faf8f3;
    padding: 24px;
  }

  .nf-card {
    background: #fff;
    border-radius: 16px;
    padding: 48px 40px;
    max-width: 440px;
    width: 100%;
    text-align: center;
    box-shadow:
      0 8px 32px rgba(13, 12, 10, 0.06),
      0 0 0 1px rgba(184, 151, 58, 0.08);
    border-top: 3px solid #b8973a;
  }

  .nf-code {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 84px;
    font-weight: 600;
    line-height: 1;
    letter-spacing: -1px;
    background: linear-gradient(135deg, #b8973a, #dfc876);
    -webkit-background-clip: text;
    background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
  }

  .nf-title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 26px;
    font-weight: 600;
    color: #0d0c0a;
    margin: 0 0 8px;
  }

  .nf-text {
    font-size: 14px;
    color: #6b6860;
    line-height: 1.6;
    margin: 0 0 28px;
  }

  .nf-actions {
    display: flex;
    gap: 12px;
    justify-content: center;
  }

  .nf-btn {
    height: 46px;
    padding: 0 22px;
    border-radius: 8px;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.18s;
  }
  .nf-btn--ghost {
    background: #fff;
    color: #6b6860;
    border: 1.5px solid #d6d3ce;
  }
  .nf-btn--ghost:hover {
    background: #f4f1e9;
    border-color: #b0ada7;
  }
  .nf-btn--gold {
    background: linear-gradient(135deg, #b8973a, #c9a84c);
    color: #fff;
    border: none;
    box-shadow: 0 4px 16px rgba(184, 151, 58, 0.18);
  }
  .nf-btn--gold:hover {
    background: linear-gradient(135deg, #9b7a25, #b8973a);
    transform: translateY(-1px);
  }

  @media (max-width: 480px) {
    .nf-card {
      padding: 36px 24px;
    }
    .nf-code {
      font-size: 64px;
    }
    .nf-actions {
      flex-direction: column-reverse;
    }
    .nf-btn {
      width: 100%;
    }
  }
</style>
