<template>
  <div class="login-page">
    <div class="auth-card">
      <div class="auth-card__header">
        <h1 class="auth-card__title">
          Family <span class="auth-card__title--accent">Wallet</span>
        </h1>
        <p class="auth-card__subtitle">Enter the family financial space</p>
      </div>

      <form class="auth-form" novalidate @submit.prevent="handleSubmit">
        <BaseInput
          v-model="email"
          label="EMAIL ADDRESS"
          type="email"
          autocomplete="new-password"
          placeholder="olena@example.com"
          :error-message="fieldErrors.email"
          @blur="validateEmailField"
          @input="onEmailInput"
        />

        <BaseInput
          v-model="password"
          label="PASSWORD"
          type="password"
          autocomplete="new-password"
          placeholder="At least 8 characters, 1 uppercase letter"
          :error-message="fieldErrors.password"
          @blur="validatePasswordField"
          @input="onPasswordInput"
        />

        <!-- Серверна помилка: єдине повідомлення без підказки яке поле (Negative AC) -->
        <Transition name="fade-down">
          <div v-if="authError" class="auth-form__server-error" role="alert">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <circle cx="8" cy="8" r="7" stroke="currentColor" stroke-width="1.5" />
              <path
                d="M8 4.5V8.5"
                stroke="currentColor"
                stroke-width="1.5"
                stroke-linecap="round"
              />
              <circle cx="8" cy="11" r="0.75" fill="currentColor" />
            </svg>
            {{ authError }}
          </div>
        </Transition>

        <!-- Кнопка з disabled + spinner (Interface AC) -->
        <button type="submit" class="btn-primary" :disabled="isLoading || !canSubmit">
          <span v-if="!isLoading">Log in</span>
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

      <!-- Посилання -->
      <div class="auth-card__links">
        <router-link to="/forgot-password" class="auth-link">Forgot password?</router-link>
        <router-link to="/register" class="auth-link auth-link--bold">Create account →</router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { ref, computed } from 'vue'
  import BaseInput from '../components/BaseInput.vue'
  import { useAuth } from '../composables/useAuth'

  const emailTouched = ref(false)
  const passwordTouched = ref(false)

  const { login, isLoading, authError } = useAuth()

  const email = ref('')
  const password = ref('')

  const fieldErrors = ref({
    email: '',
    password: '',
  })

  const EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@gmail\.com$/

  /**
   * Валідація поля email.
   * @returns {boolean}
   */
  function validateEmailField() {
    emailTouched.value = true
    fieldErrors.value.email = ''
    if (!email.value.trim()) {
      fieldErrors.value.email = 'Email is required'
      return false
    }
    if (!EMAIL_REGEX.test(email.value)) {
      fieldErrors.value.email = 'Enter a valid Gmail address (@gmail.com)'
      return false
    }
    return true
  }

  /**
   * Валідація поля password.
   * @returns {boolean}
   */
  function validatePasswordField() {
    passwordTouched.value = true
    fieldErrors.value.password = ''
    if (!password.value) {
      fieldErrors.value.password = 'Password is required'
      return false
    }
    if (password.value.length < 8) {
      fieldErrors.value.password = 'Password must contain at least 8 characters'
      return false
    }
    if (!/[A-Z]/.test(password.value)) {
      fieldErrors.value.password = 'Password must contain at least one uppercase letter'
      return false
    }
    return true
  }
  function onEmailInput() {
    if (emailTouched.value) validateEmailField()
  }

  function onPasswordInput() {
    if (passwordTouched.value) validatePasswordField()
  }

  const canSubmit = computed(() => {
    return email.value.trim().length > 0 && password.value.length > 0
  })

  /**
   * Обробка відправки форми логіну.
   */
  async function handleSubmit() {
    const isEmailValid = validateEmailField()
    const isPasswordValid = validatePasswordField()
    if (!isEmailValid || !isPasswordValid) return

    await login({
      email: email.value.trim().toLowerCase(),
      password: password.value,
    })
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
      0 8px 16px rgba(13, 12, 10, 0.06),
      0 0 0 1px rgba(184, 151, 58, 0.08);
    padding: 52px 48px;
    width: 100%;
    max-width: 480px;
    border-top: 3px solid #b8973a;
  }

  @media (max-width: 520px) {
    .auth-card {
      padding: 32px 24px;
      border-radius: 16px;
    }
  }

  .auth-card__header {
    margin-bottom: 36px;
  }

  .auth-card__title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 28px;
    font-weight: 600;
    letter-spacing: -0.3px;
    color: #0d0c0a;
    margin: 0 0 4px;
  }

  .auth-card__title--accent {
    color: #b8973a;
  }

  .auth-card__subtitle {
    font-size: 14px;
    color: #6b6860;
    margin: 0;
  }

  .auth-form {
    display: flex;
    flex-direction: column;
    gap: 18px;
  }

  .auth-form__server-error {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 14px;
    background: #fef0ed;
    border: 1px solid #e8897a;
    border-radius: 8px;
    font-size: 13px;
    color: #c4402a;
  }

  .btn-primary {
    width: 100%;
    height: 50px;
    background: #0d0c0a;
    color: #ffffff;
    border: none;
    border-radius: 8px;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.18s;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 6px;
  }

  .btn-primary:hover:not(:disabled) {
    background: #2d2b27;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(13, 12, 10, 0.1);
  }

  .btn-primary:disabled {
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

  .auth-card__links {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-top: 18px;
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

  .auth-link--bold {
    font-weight: 600;
    color: #b8973a;
  }

  .auth-card__security-note {
    text-align: center;
    margin-top: 24px;
    font-size: 11px;
    color: #b0ada7;
    font-family: 'DM Mono', 'Courier New', monospace;
    letter-spacing: 0.5px;
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
