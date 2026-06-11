<template>
  <div class="join-page">
    <div class="join-card">
      <!-- Завантаження -->
      <template v-if="state === 'loading'">
        <svg class="spinner-icon" width="32" height="32" viewBox="0 0 32 32" fill="none">
          <circle cx="16" cy="16" r="13" stroke="rgba(184,151,58,0.25)" stroke-width="3" />
          <path
            d="M16 3A13 13 0 0 1 29 16"
            stroke="#b8973a"
            stroke-width="3"
            stroke-linecap="round"
          />
        </svg>
        <h1 class="join-title">Opening the gift…</h1>
        <p class="join-sub">Validating your invitation link.</p>
      </template>

      <!-- Помилка -->
      <template v-else>
        <div class="join-icon">🎁</div>
        <h1 class="join-title">{{ errorTitle }}</h1>
        <p class="join-sub">{{ errorMessage }}</p>
        <router-link to="/feed" class="btn-gold">Go to Feed</router-link>
      </template>
    </div>
  </div>
</template>

<script setup>
  import { ref, onMounted } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { joinGiftByInvite } from '../services/giftEventService'

  const route = useRoute()
  const router = useRouter()

  const state = ref('loading') // loading | error
  const errorTitle = ref('Invitation Error')
  const errorMessage = ref('')

  onMounted(async () => {
    const token = route.params.token
    if (!token) {
      state.value = 'error'
      errorMessage.value = 'This invitation link is invalid.'
      return
    }

    // Відновлюємо повну лінку у форматі, який очікує бек (він бере останній сегмент).
    const inviteLink = `https://family-wallet.com/gift/join/${token}`

    try {
      const data = await joinGiftByInvite(inviteLink)
      // Успіх → ведемо одразу на сторінку події.
      router.replace(`/gift-events/${data.gift_id}`)
    } catch (err) {
      state.value = 'error'
      const status = err.response?.status
      if (status === 404) {
        errorTitle.value = 'Link Expired'
        errorMessage.value =
          'This invitation was not found or has expired. Ask the organizer for a new link.'
      } else if (status === 403) {
        // Ізоляція іменинника або не учасник групи
        errorTitle.value = 'Access Restricted'
        errorMessage.value =
          err.response?.data?.detail ||
          'You cannot open this gift — it may be a surprise for you, or you are not a member of this group.'
      } else {
        errorMessage.value =
          err.userMessage || 'Something went wrong while opening the gift. Please try again.'
      }
    }
  })
</script>

<style scoped>
  .join-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #faf8f3;
    padding: 24px 16px;
  }
  .join-card {
    background: #fff;
    border-radius: 20px;
    box-shadow:
      0 20px 56px rgba(13, 12, 10, 0.14),
      0 0 0 1px rgba(184, 151, 58, 0.08);
    padding: 44px 40px;
    width: 100%;
    max-width: 440px;
    border-top: 3px solid #b8973a;
    text-align: center;
  }
  .join-icon {
    font-size: 44px;
    margin-bottom: 12px;
  }
  .join-title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 24px;
    font-weight: 600;
    color: #0d0c0a;
    margin: 12px 0 8px;
  }
  .join-sub {
    font-size: 14px;
    color: #6b6860;
    line-height: 1.6;
    margin: 0 0 24px;
  }
  .btn-gold {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    height: 46px;
    padding: 0 28px;
    background: linear-gradient(135deg, #b8973a, #c9a84c);
    color: #fff;
    border: none;
    border-radius: 8px;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 14px;
    font-weight: 600;
    text-decoration: none;
    cursor: pointer;
    transition: all 0.18s;
    box-shadow: 0 4px 16px rgba(184, 151, 58, 0.18);
  }
  .btn-gold:hover {
    background: linear-gradient(135deg, #9b7a25, #b8973a);
    transform: translateY(-1px);
  }
  .spinner-icon {
    animation: spin 0.8s linear infinite;
  }
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
</style>
