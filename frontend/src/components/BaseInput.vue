<template>
  <div class="base-input">
    <label v-if="label" :for="inputId" class="base-input__label">
      {{ label }}
    </label>

    <div
      class="base-input__wrapper"
      :class="{
        'base-input__wrapper--error': hasError,
        'base-input__wrapper--focused': isFocused,
        'base-input__wrapper--filled': modelValue,
      }"
    >
      <input
        :id="inputId"
        class="base-input__field"
        :type="currentInputType"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :autocomplete="autocomplete"
        @input="$emit('update:modelValue', $event.target.value)"
        @focus="isFocused = true"
        @blur="handleBlur"
      />

      <span v-if="hasError && !isPasswordType" class="base-input__icon base-input__icon--error">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <circle cx="8" cy="8" r="7" stroke="currentColor" stroke-width="1.5" />
          <path d="M8 4.5V8.5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" />
          <circle cx="8" cy="11" r="0.75" fill="currentColor" />
        </svg>
      </span>

      <button
        v-if="isPasswordType"
        type="button"
        class="base-input__eye"
        :aria-label="isPasswordVisible ? 'Hide password' : 'Show password'"
        @click="togglePasswordVisibility"
      >
        <svg v-if="!isPasswordVisible" width="18" height="18" viewBox="0 0 18 18" fill="none">
          <path
            d="M1 9C1 9 4 3 9 3C14 3 17 9 17 9C17 9 14 15 9 15C4 15 1 9 1 9Z"
            stroke="#B0ADA7"
            stroke-width="1.5"
          />
        </svg>

        <svg v-else width="18" height="18" viewBox="0 0 18 18" fill="none">
          <path d="M2 2L16 16" stroke="#B0ADA7" stroke-width="1.5" stroke-linecap="round" />
          <path
            d="M7.5 4C8 3.7 8.5 3.5 9 3.5C14 3.5 17 9 17 9C17 9 15.9 11.1 14 12.8"
            stroke="#B0ADA7"
            stroke-width="1.5"
            stroke-linecap="round"
          />
          <path
            d="M10.5 14C10 14.2 9.5 14.5 9 14.5C4 14.5 1 9 1 9C1 9 2.1 6.9 4 5.2"
            stroke="#B0ADA7"
            stroke-width="1.5"
            stroke-linecap="round"
          />
        </svg>
      </button>
    </div>

    <Transition name="fade-down">
      <p v-if="hasError" class="base-input__error" role="alert">
        {{ errorMessage }}
      </p>
    </Transition>

    <p v-if="hint && !hasError" class="base-input__hint">{{ hint }}</p>
  </div>
</template>

<script setup>
  import { ref, computed } from 'vue'

  const props = defineProps({
    modelValue: {
      type: String,
      default: '',
    },
    label: {
      type: String,
      default: '',
    },
    placeholder: {
      type: String,
      default: '',
    },
    type: {
      type: String,
      default: 'text',
    },
    errorMessage: {
      type: String,
      default: '',
    },
    hint: {
      type: String,
      default: '',
    },
    disabled: {
      type: Boolean,
      default: false,
    },
    autocomplete: {
      type: String,
      default: 'off',
    },
  })

  const emit = defineEmits(['update:modelValue', 'blur'])

  const inputId = computed(
    () => `input-${props.label?.toLowerCase().replace(/\s/g, '-') || Math.random()}`,
  )
  const hasError = computed(() => !!props.errorMessage)
  const isPasswordType = computed(() => props.type === 'password')

  const isFocused = ref(false)
  const isPasswordVisible = ref(false)

  function handleBlur() {
    isFocused.value = false
    emit('blur')
  }

  const currentInputType = computed(() => {
    if (isPasswordType.value) {
      return isPasswordVisible.value ? 'text' : 'password'
    }
    return props.type
  })

  function togglePasswordVisibility() {
    isPasswordVisible.value = !isPasswordVisible.value
  }
</script>

<style scoped>
  .base-input {
    display: flex;
    flex-direction: column;
    gap: 5px;
  }

  .base-input__label {
    font-size: 11px;
    font-weight: 600;
    color: #6b6860;
    letter-spacing: 0.7px;
    text-transform: uppercase;
  }

  .base-input__wrapper {
    position: relative;
    display: flex;
    align-items: center;
    border: 1.5px solid #eae8e4;
    border-radius: 8px;
    background: #f4f1e9;
    transition:
      border-color 0.18s,
      box-shadow 0.18s,
      background 0.18s;
  }

  .base-input__wrapper--focused {
    border-color: #b8973a;
    background: #ffffff;
    box-shadow: 0 0 0 3px rgba(184, 151, 58, 0.15);
  }

  .base-input__wrapper--filled {
    background: #ffffff;
    border-color: #d6d3ce;
  }

  .base-input__wrapper--error {
    border-color: #c4402a;
    background: #fef0ed;
    box-shadow: none;
  }

  .base-input__field {
    flex: 1;
    height: 46px;
    border: none;
    background: transparent;
    padding: 0 16px;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 14px;
    color: #0d0c0a;
    outline: none;
    width: 100%;
  }

  .base-input__field::placeholder {
    color: #b0ada7;
  }

  .base-input__field:disabled {
    cursor: not-allowed;
    opacity: 0.45;
  }

  .base-input__icon {
    padding: 0 12px;
    display: flex;
    align-items: center;
    flex-shrink: 0;
  }

  .base-input__icon--error {
    color: #c4402a;
  }

  .base-input__eye {
    padding: 0 12px;
    background: none;
    border: none;
    cursor: pointer;
    display: flex;
    align-items: center;
    flex-shrink: 0;
    color: #b0ada7;
    transition: color 0.15s;
  }

  .base-input__eye:hover {
    color: #6b6860;
  }

  .base-input__error {
    font-size: 12px;
    color: #c4402a;
    display: flex;
    align-items: center;
    gap: 4px;
    margin: 0;
  }

  .base-input__hint {
    font-size: 11px;
    color: #b0ada7;
    margin: 0;
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
