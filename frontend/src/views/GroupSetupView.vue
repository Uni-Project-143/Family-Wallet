<template>
  <div class="setup-page">
    <div class="setup-bg">
      <!-- Auth-style card -->
      <div class="setup-card">
        <!-- Header -->
        <div class="setup-card__header">
          <div class="setup-card__logo">
            Family <span class="setup-card__logo--accent">Wallet</span>
          </div>
          <p class="setup-card__subtitle">
            Welcome, <strong>{{ currentUserName }}</strong
            >. Set up your family space to continue.
          </p>
        </div>

        <!-- Mode selector — два варіанти -->
        <div class="mode-selector">
          <button
            class="mode-btn"
            :class="{ 'mode-btn--active': selectedMode === 'create' }"
            @click="selectMode('create')"
          >
            <span class="mode-btn__icon">🏠</span>
            <span class="mode-btn__label">Create Group</span>
            <span class="mode-btn__desc">You become Admin</span>
          </button>

          <button
            class="mode-btn"
            :class="{ 'mode-btn--active': selectedMode === 'join' }"
            @click="selectMode('join')"
          >
            <span class="mode-btn__icon">🔗</span>
            <span class="mode-btn__label">Join Group</span>
            <span class="mode-btn__desc">You become Member</span>
          </button>
        </div>

        <!-- Role hint -->
        <Transition name="fade">
          <div v-if="selectedMode" class="role-hint" :class="`role-hint--${selectedMode}`">
            <template v-if="selectedMode === 'create'">
              <span class="role-hint__badge badge badge--admin">Admin</span>
              <span class="role-hint__text">
                You will be the group administrator. You can invite members, connect Monobank cards
                and manage the group.
              </span>
            </template>
            <template v-else>
              <span class="role-hint__badge badge badge--member">Member</span>
              <span class="role-hint__text">
                You will join an existing group as a member. Paste the invite link you received from
                the group Admin.
              </span>
            </template>
          </div>
        </Transition>

        <!-- Input field — змінюється залежно від режиму -->
        <Transition name="fade">
          <div v-if="selectedMode" class="setup-field">
            <div class="i-label">
              {{ selectedMode === 'create' ? 'Group Name' : 'Invite Link' }}
              <span class="i-label__sub">
                {{
                  selectedMode === 'create'
                    ? '· Group.name — e.g. Kovalenko Family'
                    : '· paste link from Admin'
                }}
              </span>
            </div>
            <div class="i-field-wrap" :class="{ 'i-field-wrap--error': fieldError }">
              <input
                v-model="fieldValue"
                class="i-field"
                :type="'text'"
                :placeholder="
                  selectedMode === 'create'
                    ? 'e.g. Kovalenko Family'
                    : 'https://familywallet.app/join/abc123'
                "
                :disabled="isLoading"
                @blur="validateField"
                @input="onFieldInput"
              />
            </div>
            <Transition name="fade-down">
              <p v-if="fieldError" class="i-error">{{ fieldError }}</p>
            </Transition>
          </div>
        </Transition>

        <!-- Server error -->
        <Transition name="fade-down">
          <div v-if="serverError" class="server-error" role="alert">
            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
              <circle cx="8" cy="8" r="7" stroke="currentColor" stroke-width="1.5" />
              <path
                d="M8 4.5V8.5"
                stroke="currentColor"
                stroke-width="1.5"
                stroke-linecap="round"
              />
              <circle cx="8" cy="11" r=".75" fill="currentColor" />
            </svg>
            {{ serverError }}
          </div>
        </Transition>

        <!-- Submit button -->
        <button class="btn-primary" :disabled="!canSubmit || isLoading" @click="handleSubmit">
          <span v-if="!isLoading">
            {{ selectedMode === 'create' ? 'Create Group' : 'Join Group' }}
          </span>
          <svg v-else class="spinner" width="20" height="20" viewBox="0 0 20 20" fill="none">
            <circle cx="10" cy="10" r="8" stroke="rgba(255,255,255,0.3)" stroke-width="2.5" />
            <path
              d="M10 2A8 8 0 0 1 18 10"
              stroke="white"
              stroke-width="2.5"
              stroke-linecap="round"
            />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
  import { ref, computed } from 'vue'
  import { useRouter } from 'vue-router'
  import { useAuth } from '../composables/useAuth'
  import { createGroup, joinGroup, fetchMyGroups } from '../services/authService'

  const router = useRouter()
  const { currentUser, setActiveGroup } = useAuth()
  // const { currentUser } = useAuth()

  const currentUserName = computed(() => currentUser.value?.fullName || 'User')

  const selectedMode = ref(null)
  const fieldValue = ref('')
  const fieldError = ref('')
  const fieldTouched = ref(false)
  const serverError = ref('')
  const isLoading = ref(false)

  const INVITE_URL_REGEX = /^https?:\/\/.+\/join\/.+/

  /**
   * Перемикає режим create / join та скидає поле.
   * @param {'create'|'join'} mode
   */
  function selectMode(mode) {
    selectedMode.value = mode
    fieldValue.value = ''
    fieldError.value = ''
    fieldTouched.value = false
    serverError.value = ''
  }

  /**
   * Валідує поточне поле залежно від режиму.
   * @returns {boolean}
   */
  function validateField() {
    fieldTouched.value = true
    fieldError.value = ''

    if (!fieldValue.value.trim()) {
      fieldError.value =
        selectedMode.value === 'create' ? 'Group name is required' : 'Invite link is required'
      return false
    }

    if (selectedMode.value === 'create' && fieldValue.value.trim().length < 2) {
      fieldError.value = 'Group name must be at least 2 characters'
      return false
    }

    if (selectedMode.value === 'join' && !INVITE_URL_REGEX.test(fieldValue.value.trim())) {
      fieldError.value = 'Please paste a valid invite link from your Admin'
      return false
    }

    return true
  }

  function onFieldInput() {
    if (fieldTouched.value) validateField()
  }

  const canSubmit = computed(() => {
    return selectedMode.value !== null && fieldValue.value.trim().length > 0
  })

  /**
   * Обробляє створення або приєднання до групи.
   * Create → POST /api/v1/group/ → role = ADMIN
   * Join   → POST /api/v1/group/join → role = MEMBER
   */
  async function handleSubmit() {
    if (!validateField()) return

    isLoading.value = true
    serverError.value = ''

    try {
      if (selectedMode.value === 'create') {
        const result = await createGroup(fieldValue.value)

        // Використовуємо setActiveGroup замість прямого запису в localStorage —
        // він синхронно оновлює і localStorage, і currentUser.value у всіх Views
        setActiveGroup({
          id: result.group_id,
          name: fieldValue.value.trim(),
          role: 'ADMIN',
        })
      } else {
        await joinGroup(fieldValue.value)

        // Тягнемо реальну назву щойно приєднаної групи з беку
        const groups = await fetchMyGroups()
        const storedUser = JSON.parse(localStorage.getItem('currentUser') || '{}')
        const joinedGroup =
          groups.find((g) => g.id !== storedUser.groupId) || groups[groups.length - 1]

        if (joinedGroup) {
          setActiveGroup(joinedGroup) // role='MEMBER' прийде з беку у groupResponse
        }
      }

      router.push('/feed')
    } catch (err) {
      const status = err.response?.status
      const message = err.response?.data?.message

      if (status === 400 && message === 'You are already a member of this group') {
        // Якщо юзер уже учасник — теж оновлюємо стан і йдемо на feed
        const groups = await fetchMyGroups()
        const storedUser = JSON.parse(localStorage.getItem('currentUser') || '{}')
        const existingGroup = groups.find((g) => g.id !== storedUser.groupId) || groups[0]
        if (existingGroup) setActiveGroup(existingGroup)
        router.push('/feed')
        return
      }

      if (status === 409) serverError.value = 'A group with this name already exists'
      else if (status === 410)
        serverError.value = 'This invite link has expired. Ask Admin to generate a new one.'
      else if (status === 400) serverError.value = message || 'Invalid invite link'
      else if (status === 404)
        serverError.value = 'Invite link not found. Check the link and try again.'
      else serverError.value = message || 'Something went wrong. Please try again.'
    } finally {
      isLoading.value = false
    }
  }
</script>

<style scoped>
  /* ── Page ── */
  .setup-page {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #faf8f3;
  }

  .setup-bg {
    width: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 24px 16px;
    position: relative;
  }

  .setup-bg::before {
    content: '';
    position: absolute;
    width: 600px;
    height: 600px;
    background: radial-gradient(circle, rgba(184, 151, 58, 0.07) 0%, transparent 70%);
    top: -100px;
    left: calc(50% - 400px);
    pointer-events: none;
  }

  /* ── Card ── */
  .setup-card {
    background: #ffffff;
    border-radius: 20px;
    box-shadow:
      0 20px 56px rgba(13, 12, 10, 0.14),
      0 8px 16px rgba(13, 12, 10, 0.06),
      0 0 0 1px rgba(184, 151, 58, 0.08);
    padding: 52px 48px;
    width: 100%;
    max-width: 520px;
    border-top: 3px solid #b8973a;
  }

  @media (max-width: 560px) {
    .setup-card {
      padding: 32px 24px;
    }
  }

  /* ── Header ── */
  .setup-card__header {
    margin-bottom: 32px;
  }

  .setup-card__logo {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 28px;
    font-weight: 600;
    letter-spacing: -0.3px;
    color: #0d0c0a;
    margin-bottom: 6px;
  }

  .setup-card__logo--accent {
    color: #b8973a;
  }

  .setup-card__subtitle {
    font-size: 14px;
    color: #6b6860;
    margin: 0;
    line-height: 1.6;
  }

  /* ── Mode selector ── */
  .mode-selector {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin-bottom: 20px;
  }

  .mode-btn {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 22px 16px;
    border: 1.5px solid #eae8e4;
    border-radius: 12px;
    background: #faf8f3;
    cursor: pointer;
    transition: all 0.2s;
    font-family: 'DM Sans', system-ui, sans-serif;
  }

  .mode-btn:hover {
    border-color: #dfc876;
    background: #fbf7ec;
  }

  .mode-btn--active {
    border-color: #b8973a;
    background: linear-gradient(135deg, #fbf7ec, #faf8f3);
    box-shadow: 0 4px 16px rgba(184, 151, 58, 0.15);
  }

  .mode-btn__icon {
    font-size: 28px;
  }

  .mode-btn__label {
    font-size: 14px;
    font-weight: 600;
    color: #0d0c0a;
  }

  .mode-btn--active .mode-btn__label {
    color: #9b7a25;
  }

  .mode-btn__desc {
    font-size: 11px;
    color: #b0ada7;
  }

  /* ── Role hint ── */
  .role-hint {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 12px 14px;
    border-radius: 8px;
    font-size: 13px;
    line-height: 1.6;
    margin-bottom: 20px;
  }

  .role-hint--create {
    background: linear-gradient(135deg, #fbf7ec, #faf8f3);
    border: 1px solid #f2e9c8;
    color: #7a5e1a;
  }

  .role-hint--join {
    background: #f4f1e9;
    border: 1px solid #eae8e4;
    color: #6b6860;
  }

  .role-hint__badge {
    flex-shrink: 0;
    margin-top: 1px;
  }
  .role-hint__text {
    flex: 1;
  }

  /* ── Input field ── */
  .setup-field {
    margin-bottom: 20px;
  }

  .i-label {
    font-size: 11px;
    font-weight: 600;
    color: #6b6860;
    letter-spacing: 0.7px;
    text-transform: uppercase;
    margin-bottom: 6px;
    display: block;
  }

  .i-label__sub {
    font-size: 9px;
    font-weight: 400;
    color: #b0ada7;
    letter-spacing: 0;
    text-transform: none;
    margin-left: 4px;
  }

  .i-field-wrap {
    border: 1.5px solid #eae8e4;
    border-radius: 8px;
    overflow: hidden;
    transition:
      border-color 0.18s,
      box-shadow 0.18s;
  }

  .i-field-wrap:focus-within {
    border-color: #b8973a;
    box-shadow: 0 0 0 3px rgba(184, 151, 58, 0.15);
  }

  .i-field-wrap--error {
    border-color: #c4402a;
  }

  .i-field {
    width: 100%;
    height: 46px;
    border: none;
    background: #f4f1e9;
    padding: 0 16px;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 14px;
    color: #0d0c0a;
    outline: none;
    transition: background 0.18s;
  }

  .i-field:focus {
    background: #ffffff;
  }
  .i-field::placeholder {
    color: #b0ada7;
  }
  .i-field:disabled {
    opacity: 0.45;
    cursor: not-allowed;
  }
  .i-field-wrap--error .i-field {
    background: #fef0ed;
  }

  .i-error {
    font-size: 12px;
    color: #c4402a;
    margin-top: 5px;
  }

  /* ── Server error ── */
  .server-error {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 14px;
    background: #fef0ed;
    border: 1px solid #e8897a;
    border-radius: 8px;
    font-size: 13px;
    color: #c4402a;
    margin-bottom: 20px;
  }

  /* ── Buttons ── */
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
    margin-bottom: 16px;
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

  /* ── Badges ── */
  .badge {
    display: inline-flex;
    align-items: center;
    height: 20px;
    padding: 0 8px;
    border-radius: 9999px;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 0.8px;
    text-transform: uppercase;
  }

  .badge--admin {
    background: linear-gradient(135deg, #b8973a, #c9a84c);
    color: #fff;
    box-shadow: 0 2px 6px rgba(184, 151, 58, 0.25);
  }

  .badge--member {
    background: #eae8e4;
    color: #6b6860;
    border: 1px solid #d6d3ce;
  }

  /* ── Footer ── */
  .setup-card__footer {
    text-align: center;
    font-size: 13px;
    color: #b0ada7;
    margin: 0;
  }

  /* ── Spinner ── */
  .spinner {
    animation: spin 0.8s linear infinite;
  }
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  /* ── Transitions ── */
  .fade-enter-active,
  .fade-leave-active {
    transition: opacity 0.2s ease;
  }
  .fade-enter-from,
  .fade-leave-to {
    opacity: 0;
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
