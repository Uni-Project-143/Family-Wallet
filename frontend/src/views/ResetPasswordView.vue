<template>
  <div class="login-page">
    <div class="auth-card">
      <template v-if="!token">
        <div class="auth-card__header">
          <h1 class="auth-card__title">Invalid Link</h1>
          <p class="auth-card__subtitle">
            This password reset link is invalid or incomplete. Please request a new one.
          </p>
        </div>
        <router-link to="/forgot-password" class="btn-gold btn-gold--link">
          Request New Link
        </router-link>
      </template>

      <template v-else-if="!isDone">
        <div class="auth-card__header">
          <h1 class="auth-card__title">Set New Password</h1>
          <p class="auth-card__subtitle">Enter a new password for your account.</p>
        </div>

        <form class="auth-form" novalidate @submit.prevent="handleSubmit">
          <BaseInput
            v-model="password"
            label="New password"
            type="password"
            placeholder="At least 8 characters"
            autocomplete="new-password"
            :error-message="passwordError"
            @blur="validatePassword"
          />
          <BaseInput
            v-model="confirmPassword"
            label="Confirm password"
            type="password"
            placeholder="Repeat the password"
            autocomplete="new-password"
            :error-message="confirmError"
            @blur="validateConfirm"
          />

          <Transition name="fade-down">
            <div v-if="serverError" class="auth-form__server-error" role="alert">
              {{ serverError }}
            </div>
          </Transition>

          <button
            type="submit"
            class="btn-gold"
            :disabled="isLoading || !password || !confirmPassword"
          >
            <span v-if="!isLoading">Reset Password</span>
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

      <template v-else>
        <div class="success-state">
          <div class="success-state__icon" aria-hidden="true">✅</div>
          <h2 class="success-state__title">Password Changed</h2>
          <p class="success-state__text">
            Your password has been updated successfully.<br />
            You can now log in with your new password.
          </p>
          <router-link to="/login" class="btn-gold btn-gold--link">Go to Login</router-link>
        </div>
      </template>

      <div v-if="token && !isDone" class="auth-card__back">
        <router-link to="/login" class="auth-link">← Back to Login</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { ref } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import BaseInput from '../components/BaseInput.vue'
  import { resetPassword } from '../services/authService'

  const route = useRoute()
  const router = useRouter()

  const token = ref(route.query.token || '')

  const password = ref('')
  const confirmPassword = ref('')
  const passwordError = ref('')
  const confirmError = ref('')
  const serverError = ref('')
  const isLoading = ref(false)
  const isDone = ref(false)

  const MIN_LENGTH = 8

  function validatePassword() {
    passwordError.value = ''
    if (!password.value) {
      passwordError.value = 'Password is required'
      return false
    }
    if (password.value.length < MIN_LENGTH) {
      passwordError.value = `Password must be at least ${MIN_LENGTH} characters`
      return false
    }
    return true
  }

  function validateConfirm() {
    confirmError.value = ''
    if (!confirmPassword.value) {
      confirmError.value = 'Please confirm your password'
      return false
    }
    if (confirmPassword.value !== password.value) {
      confirmError.value = 'Passwords do not match'
      return false
    }
    return true
  }

  async function handleSubmit() {
    const okPass = validatePassword()
    const okConfirm = validateConfirm()
    if (!okPass || !okConfirm) return

    isLoading.value = true
    serverError.value = ''

    try {
      await resetPassword({ token: token.value, new_password: password.value })
      isDone.value = true
      setTimeout(() => router.push('/login'), 2500)
    } catch (err) {
      const status = err.response?.status
      if (status === 400) {
        serverError.value = 'This reset link is invalid or has expired. Please request a new one.'
      } else {
        serverError.value = err.userMessage || 'Something went wrong. Please try again'
      }
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

  .btn-gold--link {
    text-decoration: none;
    margin-top: 8px;
  }

  .spinner-icon {
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

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
