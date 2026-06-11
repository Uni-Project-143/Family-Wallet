import js from '@eslint/js'
import pluginVue from 'eslint-plugin-vue'
import prettier from 'eslint-plugin-prettier/recommended'
import globals from 'globals'

export default [
  js.configs.recommended,
  ...pluginVue.configs['flat/recommended'],
  prettier,
  {
    files: ['src/**/*.{js,vue}'],
    // 2. Додаємо секцію languageOptions
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      globals: {
        ...globals.browser, // Додає window, localStorage, document тощо
        ...globals.node, // Додає process, module тощо (якщо потрібно)
      },
    },
    rules: {
      'no-console': 'warn',
      'no-debugger': 'warn',
      'no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      'vue/multi-word-component-names': 'off',

      // Це дозволить писати багато атрибутів в один рядок і не сваритиметься
      'vue/max-attributes-per-line': 'off',

      // Це прибере помилку про CR/LF (червоне підкреслення всього файлу)
      'prettier/prettier': ['error', { endOfLine: 'auto' }],
    },
  },
  {
    ignores: ['dist/', 'node_modules/', '*.config.js'],
  },
]
