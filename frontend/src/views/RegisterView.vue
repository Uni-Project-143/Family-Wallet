<template>
  <div class="register-page">
    <div class="auth-card">
      <!-- Заголовок -->
      <div class="auth-card__header">
        <h1 class="auth-card__title">Create Account</h1>
        <p class="auth-card__subtitle">Join Family Wallet — it's free!</p>
      </div>

      <!-- Форма (FE-01) -->
      <form class="auth-form" novalidate @submit.prevent="handleSubmit">
        <!-- Повне ім'я -->
        <BaseInput
          v-model="fullName"
          label="FULL NAME"
          placeholder="e.g., Olena Kovalenko"
          autocomplete="name"
          :error-message="fieldErrors.fullName"
          @blur="validateField('fullName')"
        />

        <!-- Email -->
        <BaseInput
          v-model="email"
          label="EMAIL ADDRESS"
          type="email"
          placeholder="olena@example.com"
          autocomplete="email"
          :error-message="fieldErrors.email"
          @blur="validateField('email')"
        />

        <!-- Пароль з eye icon (Interface AC) -->
        <BaseInput
          v-model="password"
          label="PASSWORD"
          type="password"
          placeholder="At least 8 characters, 1 uppercase letter"
          autocomplete="new-password"
          hint="Use uppercase letters, numbers, and special characters"
          :error-message="fieldErrors.password"
          @blur="validateField('password')"
        />

        <!-- Підтвердження паролю -->
        <BaseInput
          v-model="confirmPassword"
          label="CONFIRM PASSWORD"
          type="password"
          placeholder="Repeat your password"
          autocomplete="new-password"
          :error-message="fieldErrors.confirmPassword"
          @blur="validateField('confirmPassword')"
        />

        <!-- GDPR чекбокс -->
        <div
          class="auth-form__checkbox"
          :class="{ 'auth-form__checkbox--error': fieldErrors.gdpr }"
        >
          <label class="checkbox-row">
            <span
              class="checkbox-box"
              :class="{ 'checkbox-box--checked': hasGdprConsent }"
              role="checkbox"
              tabindex="0"
              :aria-checked="hasGdprConsent"
              @click="hasGdprConsent = !hasGdprConsent"
              @keydown.space.prevent="hasGdprConsent = !hasGdprConsent"
            ></span>
            <span class="checkbox-label">
              I agree to the
              <a href="/terms" target="_blank" class="auth-link">Terms of Service</a>
              and
              <a href="/privacy" target="_blank" class="auth-link">Privacy Policy</a>. I consent to
              the collection and processing of my financial data.
              <span class="gdpr-note">(GDPR)</span>
            </span>
          </label>
          <p v-if="fieldErrors.gdpr" class="field-error">{{ fieldErrors.gdpr }}</p>
        </div>
        <Transition name="fade-down">
          <div v-if="isFormBlocked" class="auth-form__rate-limit" role="alert">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <circle cx="8" cy="8" r="6.5" stroke="currentColor" stroke-width="1.5" />
              <path
                d="M8 4.5V8L10.5 10"
                stroke="currentColor"
                stroke-width="1.5"
                stroke-linecap="round"
              />
            </svg>
            {{ blockMessage }}
          </div>
        </Transition>
        <!-- Серверна помилка (наприклад, 409 Conflict) -->
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

        <!-- Кнопка — disabled + spinner під час запиту (FE-03) -->
        <button
          type="submit"
          class="btn-primary"
          :class="{ 'btn-primary--loading': isLoading }"
          :disabled="isLoading || !canSubmit"
        >
          <span v-if="!isLoading">Create account</span>
          <span v-else class="btn-spinner" aria-label="Loading...">
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

      <!-- Посилання на логін -->
      <p class="auth-card__footer">
        Already have an account?
        <router-link to="/login" class="auth-link auth-link--bold">Log in →</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
  // import BaseInput from '../components/BaseInput.vue'
  // import { useAuth } from '../composables/useAuth'
  // import { ref, computed, watch } from 'vue'

  // const { register, isLoading, authError } = useAuth()

  import BaseInput from '../components/BaseInput.vue'
  import { useAuth } from '../composables/useAuth'
  import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
  import { recordFailedAttempt, isBlocked, getRemainingBlockMs } from '../utils/authRateLimit'

  const { register, isLoading, authError } = useAuth()

  // ─── Rate limit (global for register process) ───
  const BLOCK_KEY = 'register'
  const isFormBlocked = ref(false)
  const remainingMs = ref(0)
  let countdownInterval = null

  function refreshBlockStatus() {
    isFormBlocked.value = isBlocked(BLOCK_KEY)
    remainingMs.value = getRemainingBlockMs(BLOCK_KEY)
  }

  const blockMessage = computed(() => {
    if (!isFormBlocked.value) return ''
    const m = Math.floor(remainingMs.value / 60000)
    const s = Math.floor((remainingMs.value % 60000) / 1000)
    return `Too many failed registration attempts. Try again in ${m}:${String(s).padStart(2, '0')}.`
  })

  onMounted(refreshBlockStatus)

  watch(isFormBlocked, (blocked) => {
    if (blocked && !countdownInterval) {
      countdownInterval = setInterval(() => {
        refreshBlockStatus()
        if (!isFormBlocked.value && countdownInterval) {
          clearInterval(countdownInterval)
          countdownInterval = null
        }
      }, 1000)
    } else if (!blocked && countdownInterval) {
      clearInterval(countdownInterval)
      countdownInterval = null
    }
  })

  onUnmounted(() => {
    if (countdownInterval) clearInterval(countdownInterval)
  })

  // Поля форми — зберігаються навіть при навігації (FE збереження стану через composable)
  const fullName = ref('')
  const email = ref('')
  const password = ref('')
  const confirmPassword = ref('')
  const hasGdprConsent = ref(false)

  // Замість touchedFields + onFieldInput
  const touchedFields = ref({
    fullName: false,
    email: false,
    password: false,
    confirmPassword: false,
  })

  watch(fullName, () => {
    if (touchedFields.value.fullName) validateField('fullName')
  })

  watch(email, () => {
    if (touchedFields.value.email) validateField('email')
  })

  watch(password, () => {
    if (touchedFields.value.password) validateField('password')
  })

  watch(confirmPassword, () => {
    if (touchedFields.value.confirmPassword) validateField('confirmPassword')
  })

  // Об'єкт помилок для кожного поля (FE-03 inline errors)
  const fieldErrors = ref({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    gdpr: '',
  })

  const EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@gmail\.com$/
  const FULL_NAME_REGEX = /^[А-ЯІЇЄA-Z][а-яіїєa-z']+\s[А-ЯІЇЄA-Z][а-яіїєa-z']+$/

  /**
   * Валідація одного поля при blur або перед відправкою.
   * @param {'fullName'|'email'|'password'|'confirmPassword'} fieldName
   * @returns {boolean} true якщо поле валідне
   */
  function validateField(fieldName) {
    touchedFields.value[fieldName] = true
    fieldErrors.value[fieldName] = ''

    if (fieldName === 'fullName') {
      if (!fullName.value.trim()) {
        fieldErrors.value.fullName = 'Full name is required'
        return false
      }
      if (!FULL_NAME_REGEX.test(fullName.value.trim())) {
        fieldErrors.value.fullName =
          'Enter your first and last name with a capital letter, e.g., Olena Kovalenko'
        return false
      }
    }

    if (fieldName === 'email') {
      if (!email.value.trim()) {
        fieldErrors.value.email = 'Email is required'
        return false
      }
      if (!EMAIL_REGEX.test(email.value)) {
        fieldErrors.value.email = 'Enter a valid Gmail address (@gmail.com)'
        return false
      }
    }

    if (fieldName === 'password') {
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
    }

    if (fieldName === 'confirmPassword') {
      if (!confirmPassword.value) {
        fieldErrors.value.confirmPassword = 'Confirm password is required'
        return false
      }
      if (confirmPassword.value !== password.value) {
        fieldErrors.value.confirmPassword = 'Passwords do not match'
        return false
      }
    }

    return true
  }

  /**
   * Валідація всіх полів перед відправкою.
   * @returns {boolean}
   */
  function validateAllFields() {
    const fieldNames = ['fullName', 'email', 'password', 'confirmPassword']
    const allValid = fieldNames.map(validateField).every(Boolean)

    fieldErrors.value.gdpr = ''
    if (!hasGdprConsent.value) {
      fieldErrors.value.gdpr = 'Необхідно прийняти умови використання'
      return false
    }

    return allValid
  }

  // Кнопка активна лише якщо всі поля заповнені (UI responsiveness) (FE-03)
  const canSubmit = computed(() => {
    return (
      FULL_NAME_REGEX.test(fullName.value.trim()) &&
      EMAIL_REGEX.test(email.value) &&
      password.value.length >= 8 &&
      /[A-Z]/.test(password.value) &&
      confirmPassword.value === password.value &&
      hasGdprConsent.value &&
      !isFormBlocked.value
    )
  })
  /**
   * Відправка форми реєстрації.
   */
  async function handleSubmit() {
    if (!validateAllFields()) return

    await register({
      fullName: fullName.value.trim(),
      email: email.value.trim().toLowerCase(),
      password: password.value,
      confirmPassword: confirmPassword.value,
    })

    // Бек повернув помилку (409, 422 тощо) — фіксуємо невдалу спробу
    if (authError.value) {
      recordFailedAttempt(BLOCK_KEY)
      refreshBlockStatus()
    }
  }
</script>

<style scoped>
  .register-page {
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
    padding: 48px 44px;
    width: 100%;
    max-width: 480px;
    border-top: 3px solid #b8973a;
  }

  /* Мобільна адаптація (Interface AC: min-width 375px) */
  @media (max-width: 520px) {
    .auth-card {
      padding: 32px 24px;
      border-radius: 16px;
    }
  }

  .auth-card__header {
    margin-bottom: 32px;
  }

  .auth-card__title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 28px;
    font-weight: 600;
    letter-spacing: -0.3px;
    color: #0d0c0a;
    margin: 0 0 4px;
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

  /* GDPR чекбокс */
  .auth-form__checkbox {
    display: flex;
    flex-direction: column;
    gap: 6px;
  }

  .checkbox-row {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    cursor: pointer;
  }

  .checkbox-box {
    width: 18px;
    height: 18px;
    border: 1.5px solid #b0ada7;
    border-radius: 4px;
    background: #ffffff;
    flex-shrink: 0;
    margin-top: 1px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.18s;
    cursor: pointer;
  }

  .checkbox-box:focus {
    outline: 3px solid rgba(184, 151, 58, 0.3);
    outline-offset: 2px;
  }

  .checkbox-box--checked {
    background: #b8973a;
    border-color: #b8973a;
    box-shadow: 0 2px 8px rgba(184, 151, 58, 0.18);
  }

  .checkbox-box--checked::after {
    content: '';
    width: 10px;
    height: 6px;
    border-left: 2px solid #fff;
    border-bottom: 2px solid #fff;
    transform: rotate(-45deg) translateY(-1px);
    display: block;
  }

  .checkbox-label {
    font-size: 13px;
    color: #6b6860;
    line-height: 1.7;
  }

  .auth-link {
    color: #b8973a;
    text-decoration: underline;
  }

  .auth-link--bold {
    font-weight: 600;
  }

  .gdpr-note {
    color: #b0ada7;
    font-size: 11px;
  }

  .field-error {
    font-size: 12px;
    color: #c4402a;
    margin: 0;
  }

  /* Серверна помилка */
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

  /* Кнопка сабміту */
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
    margin-top: 4px;
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
    box-shadow: none;
  }

  /* Spinner */
  .spinner-icon {
    animation: spin 0.8s linear infinite;
  }

  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  .auth-card__footer {
    text-align: center;
    margin-top: 20px;
    font-size: 13px;
    color: #6b6860;
  }

  /* Анімація серверної помилки */
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

  .auth-form__rate-limit {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 14px;
    background: #fef5e8;
    border: 1px solid #e8b56e;
    border-radius: 8px;
    font-size: 13px;
    color: #b97f1a;
  }
</style>
