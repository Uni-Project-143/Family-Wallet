<template>
  <div class="login-page">
    <div class="auth-card">
      <!-- Стан 1: форма -->
      <template v-if="!isEmailSent">
        <div class="auth-card__header">
          <h1 class="auth-card__title">Password Reset</h1>
          <p class="auth-card__subtitle">
            Enter your email and we'll send you a link to reset your password
          </p>
        </div>

        <form class="auth-form" novalidate @submit.prevent="handleSubmit">
          <BaseInput
            v-model="email"
            label="Email"
            type="email"
            placeholder="olena@example.com"
            autocomplete="email"
            :error-message="emailError"
            @blur="validateEmail"
          />

          <Transition name="fade-down">
            <div v-if="serverError" class="auth-form__server-error" role="alert">
              {{ serverError }}
            </div>
          </Transition>

          <button type="submit" class="btn-gold" :disabled="isLoading || !email.trim()">
            <span v-if="!isLoading">Send Reset Link</span>
            <span v-else aria-label="Loading...">
              <svg class="spinner-icon" width="20" height="20" viewBox="0 0 20 20" fill="none">
                <circle cx="10" cy="10" r="8" stroke="rgba(255,255,255,0.35)" stroke-width="2.5" />
                <path
                  d="M10 2A8 8 0 0 1 18 10"
                  stroke="white"
                  stroke-width="2.5"
                  stroke-linecap="round"
                />
              </svg>
            </span>
          </button>
        </form>
      </template>

      <!-- Стан 2: success -->
      <template v-else>
        <div class="success-state">
          <div class="success-state__icon" aria-hidden="true">✉️</div>
          <h2 class="success-state__title">Check Your Email</h2>
          <p class="success-state__text">
            We've sent a password reset link to<br />
            <strong>{{ email }}</strong>
          </p>
          <p class="success-state__hint">
            Didn't receive it? Check your spam folder or
            <button class="btn-text" @click="isEmailSent = false">try again</button>
          </p>
        </div>
      </template>

      <!-- Посилання назад -->
      <div class="auth-card__back">
        <router-link to="/login" class="auth-link">← Back to Login</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { ref } from 'vue'
  import BaseInput from '../components/BaseInput.vue'
  import { requestPasswordReset } from '../services/authService'

  const email = ref('')
  const emailError = ref('')
  const serverError = ref('')
  const isLoading = ref(false)
  const isEmailSent = ref(false)

  const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

  /**
   * Валідація поля email.
   * @returns {boolean}
   */
  function validateEmail() {
    emailError.value = ''
    if (!email.value.trim()) {
      emailError.value = 'Email is required'
      return false
    }
    if (!EMAIL_REGEX.test(email.value)) {
      emailError.value = 'Please enter a valid email'
      return false
    }
    return true
  }

  /**
   * Відправка запиту на скидання паролю.
   */
  async function handleSubmit() {
    if (!validateEmail()) return

    isLoading.value = true
    serverError.value = ''

    try {
      await requestPasswordReset({ email: email.value.trim().toLowerCase() })
      isEmailSent.value = true
    } catch {
      serverError.value = 'Something went wrong. Please try again'
    } finally {
      isLoading.value = false
    }
  }
</script>

<style scoped>
  .login-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #faf8f3;
    padding: 24px 16px;
  }

  .auth-card {
    background: #ffffff;
    border-radius: 20px;
    box-shadow:
      0 20px 56px rgba(13, 12, 10, 0.14),
      0 0 0 1px rgba(184, 151, 58, 0.08);
    padding: 48px 44px;
    width: 100%;
    max-width: 460px;
    border-top: 3px solid #b8973a;
  }

  @media (max-width: 520px) {
    .auth-card {
      padding: 32px 24px;
    }
  }

  .auth-card__header {
    margin-bottom: 32px;
  }

  .auth-card__title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 26px;
    font-weight: 600;
    color: #0d0c0a;
    margin: 0 0 6px;
  }

  .auth-card__subtitle {
    font-size: 14px;
    color: #6b6860;
    line-height: 1.6;
    margin: 0;
  }

  .auth-form {
    display: flex;
    flex-direction: column;
    gap: 18px;
  }

  .auth-form__server-error {
    padding: 12px 14px;
    background: #fef0ed;
    border: 1px solid #e8897a;
    border-radius: 8px;
    font-size: 13px;
    color: #c4402a;
  }

  .btn-gold {
    width: 100%;
    height: 48px;
    background: linear-gradient(135deg, #b8973a 0%, #c9a84c 100%);
    color: #ffffff;
    border: none;
    border-radius: 8px;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.18s;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 4px 20px rgba(184, 151, 58, 0.18);
  }

  .btn-gold:hover:not(:disabled) {
    background: linear-gradient(135deg, #9b7a25 0%, #b8973a 100%);
    transform: translateY(-1px);
  }

  .btn-gold:disabled {
    opacity: 0.4;
    cursor: not-allowed;
    transform: none;
  }

  .spinner-icon {
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  /* Success state */
  .success-state {
    text-align: center;
    padding: 8px 0;
  }

  .success-state__icon {
    font-size: 48px;
    margin-bottom: 16px;
    display: block;
  }

  .success-state__title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 22px;
    font-weight: 600;
    color: #0d0c0a;
    margin: 0 0 12px;
  }

  .success-state__text {
    font-size: 14px;
    color: #6b6860;
    line-height: 1.7;
    margin: 0 0 16px;
  }

  .success-state__hint {
    font-size: 13px;
    color: #b0ada7;
    margin: 0;
  }

  .btn-text {
    background: none;
    border: none;
    color: #b8973a;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    text-decoration: underline;
    padding: 0;
    font-family: 'DM Sans', system-ui, sans-serif;
  }

  .auth-card__back {
    margin-top: 28px;
    text-align: center;
  }

  .auth-link {
    font-size: 13px;
    color: #6b6860;
    text-decoration: none;
    transition: color 0.15s;
  }

  .auth-link:hover {
    color: #b8973a;
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
</style>
