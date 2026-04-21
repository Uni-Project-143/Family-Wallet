<template>
  <div class="register-page">
    <div class="auth-card">
      <!-- Заголовок -->
      <div class="auth-card__header">
        <h1 class="auth-card__title">Створити акаунт</h1>
        <p class="auth-card__subtitle">Приєднайтесь до Family Wallet — безкоштовно</p>
      </div>

      <!-- Форма (FE-01) -->
      <form class="auth-form" novalidate @submit.prevent="handleSubmit">
        <!-- Повне ім'я -->
        <BaseInput
          v-model="fullName"
          label="Повне ім'я"
          placeholder="напр. Олена Коваленко"
          autocomplete="name"
          :error-message="fieldErrors.fullName"
          @blur="validateField('fullName')"
          @input="onFieldInput('fullName')"
        />

        <!-- Email -->
        <BaseInput
          v-model="email"
          label="ЕЛЕКТРОННА АДРЕСА"
          type="email"
          placeholder="olena@example.com"
          autocomplete="email"
          :error-message="fieldErrors.email"
          @blur="validateField('email')"
          @input="onFieldInput('email')"
        />

        <!-- Пароль з eye icon (Interface AC) -->
        <BaseInput
          v-model="password"
          label="Пароль"
          type="password"
          placeholder="Мінімум 8 символів"
          autocomplete="new-password"
          hint="Використовуйте великі літери, цифри та спецсимволи"
          :error-message="fieldErrors.password"
          @blur="validateField('password')"
          @input="onFieldInput('password')"
        />

        <!-- Підтвердження паролю -->
        <BaseInput
          v-model="confirmPassword"
          label="Підтвердження паролю"
          type="password"
          placeholder="Повторіть пароль"
          autocomplete="new-password"
          :error-message="fieldErrors.confirmPassword"
          @blur="validateField('confirmPassword')"
          @input="onFieldInput('confirmPassword')"
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
              Я погоджуюся з
              <a href="/terms" target="_blank" class="auth-link">Умовами використання</a>
              та
              <a href="/privacy" target="_blank" class="auth-link">Політикою конфіденційності</a>.
              Надаю згоду на збір та обробку фінансових даних.
              <span class="gdpr-note">(GDPR)</span>
            </span>
          </label>
          <p v-if="fieldErrors.gdpr" class="field-error">{{ fieldErrors.gdpr }}</p>
        </div>

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
          <span v-if="!isLoading">Створити акаунт</span>
          <span v-else class="btn-spinner" aria-label="Завантаження...">
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
        Вже є акаунт?
        <router-link to="/login" class="auth-link auth-link--bold">Увійти →</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
  import { ref, computed } from 'vue'
  import BaseInput from '../components/BaseInput.vue'
  import { useAuth } from '../composables/useAuth'

  const { register, isLoading, authError } = useAuth()

  // Поля форми — зберігаються навіть при навігації (FE збереження стану через composable)
  const fullName = ref('')
  const email = ref('')
  const password = ref('')
  const confirmPassword = ref('')
  const hasGdprConsent = ref(false)

  const touchedFields = ref({
    fullName: false,
    email: false,
    password: false,
    confirmPassword: false,
  })

  function onFieldInput(fieldName) {
    if (touchedFields.value[fieldName]) validateField(fieldName)
  }

  // Об'єкт помилок для кожного поля (FE-03 inline errors)
  const fieldErrors = ref({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
    gdpr: '',
  })

  // EMAIL_REGEX — валідація формату email (FE-02)
  const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

  // PASSWORD_MIN_LENGTH — мінімальна довжина паролю (FE-02)
  const PASSWORD_MIN_LENGTH = 8

  /**
   * Валідація одного поля при blur або перед відправкою.
   * @param {'fullName'|'email'|'password'|'confirmPassword'} fieldName
   * @returns {boolean} true якщо поле валідне
   */
  function validateField(fieldName) {
    touchedFields.value[fieldName] = true // ← !!!!!!!!!!
    fieldErrors.value[fieldName] = ''

    if (fieldName === 'fullName') {
      if (!fullName.value.trim()) {
        fieldErrors.value.fullName = "Ім'я є обов'язковим"
        return false
      }
      if (fullName.value.trim().length < 2) {
        fieldErrors.value.fullName = "Ім'я має містити щонайменше 2 символи"
        return false
      }
    }

    if (fieldName === 'email') {
      if (!email.value.trim()) {
        fieldErrors.value.email = "Email є обов'язковим"
        return false
      }
      if (!EMAIL_REGEX.test(email.value)) {
        fieldErrors.value.email = 'Введіть коректний email'
        return false
      }
    }

    if (fieldName === 'password') {
      if (!password.value) {
        fieldErrors.value.password = "Пароль є обов'язковим"
        return false
      }
      if (password.value.length < PASSWORD_MIN_LENGTH) {
        fieldErrors.value.password = `Пароль має містити мінімум ${PASSWORD_MIN_LENGTH} символів`
        return false
      }
      if (!/[A-Z]/.test(password.value)) {
        fieldErrors.value.password = 'Пароль має містити хоча б одну велику літеру'
        return false
      }
      if (!/[0-9]/.test(password.value)) {
        fieldErrors.value.password = 'Пароль має містити хоча б одну цифру'
        return false
      }
    }

    if (fieldName === 'confirmPassword') {
      if (!confirmPassword.value) {
        fieldErrors.value.confirmPassword = "Підтвердження паролю є обов'язковим"
        return false
      }
      if (confirmPassword.value !== password.value) {
        fieldErrors.value.confirmPassword = 'Паролі не збігаються'
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
      fullName.value.trim().length >= 2 &&
      EMAIL_REGEX.test(email.value) &&
      password.value.length >= PASSWORD_MIN_LENGTH &&
      confirmPassword.value === password.value &&
      hasGdprConsent.value
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
    })
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
</style>
