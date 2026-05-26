<template>
  <div class="page">
    <!-- Той самий navbar що на Feed/Settings -->
    <header class="navbar">
      <div class="navbar__left">
        <span class="navbar__logo">Family <span class="navbar__logo--accent">Wallet</span></span>
      </div>
      <nav class="navbar__center">
        <router-link to="/feed" class="navbar__tab" active-class="navbar__tab--active"
          >Feed</router-link
        >
        <router-link to="/gift-events" class="navbar__tab" active-class="navbar__tab--active"
          >Gift Events</router-link
        >
        <router-link to="/settings" class="navbar__tab" active-class="navbar__tab--active"
          >Settings</router-link
        >
      </nav>
      <div class="navbar__right">
        <div class="avatar avatar--sm avatar--gold">{{ initials }}</div>
        <span class="navbar__user-name">{{ fullName }}</span>
        <span class="badge" :class="isAdmin ? 'badge--admin' : 'badge--member'">
          {{ isAdmin ? 'Admin' : 'Member' }}
        </span>
      </div>
    </header>

    <main class="main">
      <div class="header-row">
        <h1 class="title">Create Secret Gift Event</h1>
        <p class="subtitle">
          A surprise gift collection. The recipient won't see this event until the unlock date.
        </p>
      </div>

      <!-- ── Stepper ── -->
      <div class="stepper">
        <div class="step" :class="stepClass(1)">
          <div class="step__circle">1</div>
          <div class="step__label">Setup</div>
        </div>
        <div class="step__line" :class="{ 'step__line--done': currentStep > 1 }"></div>
        <div class="step" :class="stepClass(2)">
          <div class="step__circle">2</div>
          <div class="step__label">Review</div>
        </div>
        <div class="step__line" :class="{ 'step__line--done': currentStep > 2 }"></div>
        <div class="step" :class="stepClass(3)">
          <div class="step__circle">3</div>
          <div class="step__label">Done</div>
        </div>
      </div>

      <!-- Loading members -->
      <section v-if="isLoadingMembers" class="stage-card">
        <p class="loading-text">Loading group members...</p>
      </section>

      <!-- Error loading members -->
      <section v-else-if="membersError" class="stage-card">
        <p class="error-text">{{ membersError }}</p>
        <button class="btn-secondary" @click="loadMembers">Retry</button>
      </section>

      <!-- ══ STAGE 1 — Setup ══ -->
      <section v-else-if="currentStep === 1" class="stage-card">
        <h2 class="stage-card__title">Who is the gift for?</h2>

        <div v-if="availableMembers.length === 0" class="empty-members">
          You need at least one other group member to create a gift event.
        </div>

        <div v-else class="member-carousel">
          <button
            v-for="member in availableMembers"
            :key="member.id"
            type="button"
            class="member-pick"
            :class="{ 'member-pick--active': form.targetUserId === member.id }"
            @click="form.targetUserId = member.id"
          >
            <div class="avatar avatar--md" :class="`avatar--${member.avatarVariant}`">
              {{ member.initials }}
            </div>
            <div class="member-pick__name">{{ member.name }}</div>
          </button>
        </div>
        <p v-if="errors.targetUserId" class="error-text">{{ errors.targetUserId }}</p>

        <div class="divider"></div>

        <div class="field">
          <label class="field__label" for="event-name">EVENT NAME</label>
          <div class="i-field-wrap" :class="{ 'i-field-wrap--error': errors.name }">
            <input
              id="event-name"
              v-model="form.name"
              type="text"
              class="i-field"
              placeholder="e.g. Birthday gift for Sofia"
              maxlength="80"
              @blur="validate('name')"
            />
          </div>
          <p v-if="errors.name" class="error-text">{{ errors.name }}</p>
        </div>

        <div class="field-row">
          <div class="field">
            <label class="field__label" for="unlock-date">UNLOCK DATE & TIME</label>
            <div class="i-field-wrap" :class="{ 'i-field-wrap--error': errors.unlockDate }">
              <input
                id="unlock-date"
                v-model="form.unlockDate"
                type="datetime-local"
                class="i-field"
                :min="minDateTime"
                @blur="validate('unlockDate')"
              />
            </div>
            <p v-if="errors.unlockDate" class="error-text">{{ errors.unlockDate }}</p>
            <p v-if="form.unlockDate && !errors.unlockDate" class="hint-text">
              {{ formatUnlockDateWithTz }}
            </p>
          </div>

          <div class="field">
            <label class="field__label" for="goal-amount">GOAL AMOUNT (UAH)</label>
            <div class="i-field-wrap" :class="{ 'i-field-wrap--error': errors.goalAmount }">
              <input
                id="goal-amount"
                v-model.number="form.goalAmount"
                type="number"
                class="i-field"
                placeholder="2000"
                min="100"
                step="100"
                @blur="validate('goalAmount')"
              />
            </div>
            <p v-if="errors.goalAmount" class="error-text">{{ errors.goalAmount }}</p>
          </div>
        </div>

        <div class="actions">
          <button type="button" class="btn-secondary" @click="$router.push('/feed')">Cancel</button>
          <button
            type="button"
            class="btn-gold"
            :disabled="!canProceedToReview"
            @click="goToReview"
          >
            Continue
          </button>
        </div>
      </section>

      <!-- ══ STAGE 2 — Review ══ -->
      <section v-else-if="currentStep === 2" class="stage-card">
        <h2 class="stage-card__title">Confirm your gift event</h2>
        <p class="stage-card__sub">
          Review all details. After confirmation, the recipient will be hidden from this event.
        </p>

        <div class="review-list">
          <div class="review-row">
            <span class="review-row__label">Recipient</span>
            <div class="review-row__value review-row__value--member">
              <div class="avatar avatar--sm" :class="`avatar--${selectedMember?.avatarVariant}`">
                {{ selectedMember?.initials }}
              </div>
              {{ selectedMember?.name }}
            </div>
          </div>
          <div class="review-row">
            <span class="review-row__label">Event Name</span>
            <span class="review-row__value">{{ form.name }}</span>
          </div>
          <div class="review-row">
            <span class="review-row__label">Unlock Date</span>
            <span class="review-row__value">{{ formatUnlockDateWithTz }}</span>
          </div>
          <div class="review-row">
            <span class="review-row__label">Goal</span>
            <span class="review-row__value">{{ form.goalAmount.toLocaleString('uk-UA') }} UAH</span>
          </div>
        </div>

        <div class="privacy-note">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path
              d="M8 1L2 3.5V8C2 11.5 4.7 14.5 8 15.5C11.3 14.5 14 11.5 14 8V3.5L8 1Z"
              stroke="currentColor"
              stroke-width="1.4"
            />
          </svg>
          <div>
            <strong>{{ selectedMember?.name }}</strong> won't see this event in their feed until
            <strong>{{ formatUnlockDateWithTz }}</strong
            >. All transactions linked to this event will be hidden in their view.
          </div>
        </div>

        <Transition name="fade-down">
          <div v-if="serverError" class="server-error" role="alert">{{ serverError }}</div>
        </Transition>

        <div class="actions">
          <button
            type="button"
            class="btn-secondary"
            :disabled="isSubmitting"
            @click="currentStep = 1"
          >
            Back
          </button>
          <button type="button" class="btn-gold" :disabled="isSubmitting" @click="handleConfirm">
            <span v-if="!isSubmitting">Create Gift Event</span>
            <svg v-else class="spinner" width="18" height="18" viewBox="0 0 18 18" fill="none">
              <circle cx="9" cy="9" r="7" stroke="rgba(255,255,255,.3)" stroke-width="2" />
              <path
                d="M9 2A7 7 0 0 1 16 9"
                stroke="white"
                stroke-width="2"
                stroke-linecap="round"
              />
            </svg>
          </button>
        </div>
      </section>

      <!-- ══ STAGE 3 — blurred preview ══ -->
      <section v-else-if="currentStep === 3" class="stage-card stage-card--blurred">
        <div class="review-list" aria-hidden="true">
          <div class="review-row">
            <span class="review-row__label">Recipient</span>
            <span class="review-row__value">{{ selectedMember?.name }}</span>
          </div>
        </div>
      </section>
    </main>

    <!-- Success Modal — Stage 3 -->
    <Teleport to="body">
      <Transition name="overlay">
        <div v-if="currentStep === 3" class="success-overlay" role="dialog" aria-modal="true">
          <Transition name="modal">
            <div v-if="currentStep === 3" class="success-card">
              <div class="success-icon">
                <svg width="56" height="56" viewBox="0 0 56 56" fill="none">
                  <circle cx="28" cy="28" r="26" stroke="#b8973a" stroke-width="2" />
                  <path
                    d="M16 28L24 36L40 20"
                    stroke="#b8973a"
                    stroke-width="3"
                    stroke-linecap="round"
                    stroke-linejoin="round"
                  />
                </svg>
              </div>

              <h2 class="success-title">Gift event created!</h2>
              <p class="success-text">
                <strong>{{ form.name }}</strong> is now active. Family members can contribute until
                <strong>{{ formatUnlockDateWithTz }}</strong
                >.
              </p>

              <div class="success-summary">
                <div class="success-summary__row">
                  <span>Recipient</span>
                  <strong>{{ selectedMember?.name }}</strong>
                </div>
                <div class="success-summary__row">
                  <span>Goal</span>
                  <strong>{{ form.goalAmount.toLocaleString('uk-UA') }} UAH</strong>
                </div>
              </div>

              <!-- Invite link (PROJ-57) -->
              <div v-if="inviteUrl" class="invite-section">
                <div class="invite-section__label">SHARE WITH FAMILY</div>
                <div class="invite-link-box">
                  <div class="invite-link-box__url">{{ inviteUrl }}</div>
                  <button
                    class="btn-copy"
                    :class="{ 'btn-copy--copied': isLinkCopied }"
                    @click="copyInviteLink"
                  >
                    <svg
                      v-if="!isLinkCopied"
                      width="14"
                      height="14"
                      viewBox="0 0 14 14"
                      fill="none"
                    >
                      <rect
                        x="4"
                        y="4"
                        width="8"
                        height="8"
                        rx="1.5"
                        stroke="currentColor"
                        stroke-width="1.5"
                      />
                      <path
                        d="M2 10V3C2 2.44772 2.44772 2 3 2H10"
                        stroke="currentColor"
                        stroke-width="1.5"
                        stroke-linecap="round"
                      />
                    </svg>
                    <svg v-else width="14" height="14" viewBox="0 0 14 14" fill="none">
                      <path
                        d="M2.5 7L5.5 10L11.5 4"
                        stroke="currentColor"
                        stroke-width="1.5"
                        stroke-linecap="round"
                        stroke-linejoin="round"
                      />
                    </svg>
                    {{ isLinkCopied ? 'Copied!' : 'Copy' }}
                  </button>
                </div>
              </div>

              <div v-else-if="inviteError" class="invite-section">
                <p class="error-text">Couldn't generate invite link. {{ inviteError }}</p>
                <button class="btn-secondary" style="margin-top: 8px" @click="retryInvite">
                  Retry
                </button>
              </div>

              <div class="success-actions">
                <button type="button" class="btn-secondary" @click="resetWizard">
                  Create Another
                </button>
                <button
                  type="button"
                  class="btn-gold"
                  @click="$router.push(`/gift-events/${createdGiftId}`)"
                >
                  Open Event
                </button>
              </div>
            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>

    <!-- Toast -->
    <Transition name="toast">
      <div v-if="toast.isVisible" class="toast" :class="`toast--${toast.type}`" role="alert">
        {{ toast.message }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
  import { ref, computed, onMounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { useAuth } from '../composables/useAuth'
  import { fetchGroupMembers } from '../services/authService'
  import { createGiftEvent, generateGiftInviteLink } from '../services/giftEventService'

  const router = useRouter()
  const { currentUser, isAdmin } = useAuth()

  const fullName = computed(() => currentUser.value?.fullName || '')
  const initials = computed(() => {
    const name = fullName.value
    if (!name) return '?'
    return name
      .split(' ')
      .map((w) => w[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  })

  // ─── Group members з API ───
  const groupMembers = ref([])
  const isLoadingMembers = ref(false)
  const membersError = ref('')

  function mapMemberFromApi(apiMember) {
    const fullName = apiMember.full_name || apiMember.email || 'User'
    const initials = fullName
      .split(' ')
      .map((w) => w[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)

    const variants = ['gold', 'dark', 'light']
    const variantIdx = (initials.charCodeAt(0) || 0) % variants.length

    return {
      id: apiMember.user_id || apiMember.id,
      name: fullName,
      initials,
      avatarVariant: variants[variantIdx],
    }
  }

  async function loadMembers() {
    if (!currentUser.value?.groupId) {
      membersError.value = 'Active group not found. Please sign in again.'
      return
    }

    isLoadingMembers.value = true
    membersError.value = ''

    try {
      const data = await fetchGroupMembers(currentUser.value.groupId)
      const members = Array.isArray(data) ? data : data.members || []
      groupMembers.value = members.map(mapMemberFromApi)
    } catch (err) {
      const status = err.response?.status
      if (status === 404) {
        // Endpoint ще не реалізований на беку — показуємо порожній список і дозволяємо рухатись
        groupMembers.value = []
        membersError.value = 'Group members endpoint not available yet. Backend WIP.'
      } else {
        membersError.value = 'Failed to load group members. Try again.'
      }
    } finally {
      isLoadingMembers.value = false
    }
  }

  // Виключаємо себе зі списку
  const availableMembers = computed(() =>
    groupMembers.value.filter((m) => m.id !== currentUser.value?.id),
  )

  // ─── Stepper ───
  const currentStep = ref(1)
  function stepClass(num) {
    return {
      'step--active': currentStep.value === num,
      'step--done': currentStep.value > num,
    }
  }

  // ─── Form ───
  const form = ref({
    targetUserId: null,
    name: '',
    unlockDate: '',
    goalAmount: 2000,
  })

  const errors = ref({
    targetUserId: '',
    name: '',
    unlockDate: '',
    goalAmount: '',
  })

  /**
   * Мінімум для datetime-local — завтра 00:00 у локальній timezone.
   * datetime-local не приймає UTC ISO — потрібен local string "YYYY-MM-DDTHH:mm".
   */
  const minDateTime = computed(() => {
    const d = new Date()
    d.setDate(d.getDate() + 1)
    d.setHours(0, 0, 0, 0)
    return formatLocalDateTime(d)
  })

  function formatLocalDateTime(date) {
    const pad = (n) => String(n).padStart(2, '0')
    return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}T${pad(date.getHours())}:${pad(date.getMinutes())}`
  }

  const selectedMember = computed(() =>
    groupMembers.value.find((m) => m.id === form.value.targetUserId),
  )

  /**
   * Виводить unlockDate з timezone — напр. "April 15, 2025 at 6:00 PM GMT+3".
   * Required by PROJ-56 Interface AC.
   */
  const formatUnlockDateWithTz = computed(() => {
    if (!form.value.unlockDate) return ''
    const date = new Date(form.value.unlockDate)
    if (isNaN(date.getTime())) return ''
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      timeZoneName: 'short',
    }).format(date)
  })

  function validate(field) {
    errors.value[field] = ''

    if (field === 'name') {
      if (!form.value.name.trim()) {
        errors.value.name = 'Event name is required'
        return false
      }
      if (form.value.name.trim().length < 3) {
        errors.value.name = 'Event name must be at least 3 characters'
        return false
      }
    }

    if (field === 'unlockDate') {
      if (!form.value.unlockDate) {
        errors.value.unlockDate = 'Unlock date is required'
        return false
      }
      const selected = new Date(form.value.unlockDate)
      if (isNaN(selected.getTime())) {
        errors.value.unlockDate = 'Invalid date format'
        return false
      }
      if (selected.getTime() <= Date.now()) {
        errors.value.unlockDate = 'Date must be in the future'
        return false
      }
    }

    if (field === 'goalAmount') {
      if (!form.value.goalAmount || form.value.goalAmount < 100) {
        errors.value.goalAmount = 'Goal must be at least 100 UAH'
        return false
      }
    }

    return true
  }

  const canProceedToReview = computed(() => {
    return (
      form.value.targetUserId !== null &&
      form.value.name.trim().length >= 3 &&
      form.value.unlockDate &&
      new Date(form.value.unlockDate).getTime() > Date.now() &&
      form.value.goalAmount >= 100
    )
  })

  function goToReview() {
    errors.value.targetUserId = ''
    if (!form.value.targetUserId) {
      errors.value.targetUserId = 'Please pick a recipient'
      return
    }

    const ok = ['name', 'unlockDate', 'goalAmount'].map(validate).every(Boolean)
    if (!ok) return

    currentStep.value = 2
  }

  // ─── Submit ───
  const isSubmitting = ref(false)
  const serverError = ref('')
  const createdGiftId = ref(null)
  const inviteUrl = ref('')
  const inviteError = ref('')
  const isLinkCopied = ref(false)

  async function handleConfirm() {
    isSubmitting.value = true
    serverError.value = ''
    inviteUrl.value = ''
    inviteError.value = ''

    try {
      const created = await createGiftEvent({
        name: form.value.name.trim(),
        target_user_id: form.value.targetUserId,
        unlock_date: new Date(form.value.unlockDate).toISOString(), // → UTC ISO 8601
        goal_amount: form.value.goalAmount,
        group_id: currentUser.value.groupId,
      })

      createdGiftId.value = created.gift_id || created.id

      // Автоматично генеруємо invite link (PROJ-57)
      try {
        const linkData = await generateGiftInviteLink(createdGiftId.value)
        inviteUrl.value = linkData.invite_url
      } catch (linkErr) {
        inviteError.value =
          linkErr.response?.data?.message || 'You can generate it later from the event page.'
      }

      currentStep.value = 3
    } catch (err) {
      const status = err.response?.status
      const message = err.response?.data?.message

      if (status === 400) {
        serverError.value = message || 'Invalid event data. Please check the fields.'
      } else if (status === 422) {
        serverError.value = message || 'Validation error. Date must be in the future.'
      } else if (status === 403) {
        serverError.value = "You don't have permission to create events in this group."
      } else {
        serverError.value = message || 'Something went wrong. Please try again.'
      }
    } finally {
      isSubmitting.value = false
    }
  }

  async function retryInvite() {
    if (!createdGiftId.value) return
    inviteError.value = ''
    try {
      const linkData = await generateGiftInviteLink(createdGiftId.value)
      inviteUrl.value = linkData.invite_url
    } catch (err) {
      inviteError.value = err.response?.data?.message || 'Failed to generate link.'
    }
  }

  async function copyInviteLink() {
    if (!inviteUrl.value) return
    try {
      await navigator.clipboard.writeText(inviteUrl.value)
      isLinkCopied.value = true
      showToast('Link copied!', 'success')
      setTimeout(() => {
        isLinkCopied.value = false
      }, 2500)
    } catch {
      showToast('Failed to copy. Please copy manually.', 'error')
    }
  }

  function resetWizard() {
    form.value = { targetUserId: null, name: '', unlockDate: '', goalAmount: 2000 }
    errors.value = { targetUserId: '', name: '', unlockDate: '', goalAmount: '' }
    serverError.value = ''
    inviteUrl.value = ''
    inviteError.value = ''
    createdGiftId.value = null
    currentStep.value = 1
  }

  // ─── Toast ───
  const toast = ref({ isVisible: false, message: '', type: 'success' })

  function showToast(message, type = 'success') {
    toast.value = { isVisible: true, message, type }
    setTimeout(() => {
      toast.value.isVisible = false
    }, 3000)
  }

  onMounted(loadMembers)
</script>

<style scoped>
  .page {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    background: #faf8f3;
  }

  /* ── Navbar (повторюється з FeedView) ── */
  .navbar {
    height: 60px;
    background: #0d0c0a;
    display: grid;
    grid-template-columns: 1fr auto 1fr;
    align-items: center;
    padding: 0 28px;
    flex-shrink: 0;
    border-bottom: 1px solid rgba(184, 151, 58, 0.18);
    position: sticky;
    top: 0;
    z-index: 100;
  }
  .navbar__left {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  .navbar__logo {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 18px;
    font-weight: 600;
    color: #fff;
  }
  .navbar__logo--accent {
    color: #b8973a;
  }
  .navbar__center {
    display: flex;
    gap: 2px;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 8px;
    padding: 4px;
    justify-self: center;
  }
  .navbar__tab {
    padding: 7px 20px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.5);
    text-decoration: none;
    transition: all 0.18s;
    white-space: nowrap;
    border: 1px solid transparent;
  }
  .navbar__tab:hover {
    color: rgba(255, 255, 255, 0.85);
  }
  .navbar__tab--active {
    background: rgba(184, 151, 58, 0.18);
    color: #ead9a0;
    font-weight: 600;
    border-color: rgba(184, 151, 58, 0.25);
  }
  .navbar__right {
    display: flex;
    align-items: center;
    gap: 10px;
    justify-self: end;
  }
  .navbar__user-name {
    font-size: 13px;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.85);
  }

  .avatar {
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-weight: 700;
    flex-shrink: 0;
  }
  .avatar--sm {
    width: 32px;
    height: 32px;
    font-size: 11px;
  }
  .avatar--md {
    width: 48px;
    height: 48px;
    font-size: 16px;
  }
  .avatar--gold {
    background: linear-gradient(135deg, #f2e9c8, #dfc876);
    color: #7a5e1a;
  }
  .avatar--dark {
    background: linear-gradient(135deg, #3f3d38, #2d2b27);
    color: #ead9a0;
  }
  .avatar--light {
    background: linear-gradient(135deg, #f8f2e0, #f2e9c8);
    color: #9b7a25;
  }

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

  /* ── Main ── */
  .main {
    flex: 1;
    padding: 36px 48px 48px;
    max-width: 720px;
    margin: 0 auto;
    width: 100%;
  }

  @media (max-width: 720px) {
    .main {
      padding: 28px 20px 32px;
    }
  }

  .header-row {
    margin-bottom: 28px;
    text-align: center;
  }
  .title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 32px;
    font-weight: 600;
    letter-spacing: -0.4px;
    color: #0d0c0a;
    margin: 0 0 6px;
  }
  .subtitle {
    font-size: 14px;
    color: #6b6860;
    margin: 0;
    line-height: 1.6;
  }

  /* ── Stepper ── */
  .stepper {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0;
    margin-bottom: 32px;
  }
  .step {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
  }
  .step__circle {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: 2px solid #d6d3ce;
    background: #ffffff;
    color: #b0ada7;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-weight: 700;
    font-size: 14px;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.25s;
  }
  .step--active .step__circle {
    border-color: #b8973a;
    background: linear-gradient(135deg, #b8973a, #c9a84c);
    color: #ffffff;
    box-shadow: 0 0 0 4px rgba(184, 151, 58, 0.18);
  }
  .step--done .step__circle {
    border-color: #b8973a;
    background: #b8973a;
    color: #ffffff;
  }
  .step__label {
    font-size: 11px;
    font-weight: 600;
    color: #b0ada7;
    letter-spacing: 0.5px;
    text-transform: uppercase;
  }
  .step--active .step__label,
  .step--done .step__label {
    color: #9b7a25;
  }
  .step__line {
    width: 80px;
    height: 2px;
    background: #eae8e4;
    margin: 0 8px;
    margin-bottom: 24px;
    transition: background 0.25s;
  }
  .step__line--done {
    background: #b8973a;
  }

  /* ── Stage card ── */
  .stage-card {
    background: #ffffff;
    border-radius: 16px;
    padding: 36px 36px 28px;
    box-shadow:
      0 8px 32px rgba(13, 12, 10, 0.06),
      0 0 0 1px rgba(184, 151, 58, 0.08);
    border-top: 3px solid #b8973a;
  }
  @media (max-width: 560px) {
    .stage-card {
      padding: 24px 20px;
    }
  }
  .stage-card--blurred {
    filter: blur(3px);
    pointer-events: none;
    user-select: none;
  }
  .stage-card__title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 22px;
    font-weight: 600;
    color: #0d0c0a;
    margin: 0 0 6px;
  }
  .stage-card__sub {
    font-size: 13px;
    color: #6b6860;
    margin: 0 0 24px;
    line-height: 1.6;
  }

  .loading-text {
    text-align: center;
    color: #b0ada7;
    font-size: 14px;
    padding: 32px 0;
  }

  .empty-members {
    text-align: center;
    padding: 32px 20px;
    background: #faf8f3;
    border: 1px dashed #d6d3ce;
    border-radius: 10px;
    color: #b0ada7;
    font-size: 13px;
  }

  /* ── Member carousel ── */
  .member-carousel {
    display: flex;
    gap: 12px;
    overflow-x: auto;
    padding: 8px 4px 16px;
    margin-bottom: 8px;
    scroll-snap-type: x mandatory;
  }
  .member-pick {
    flex-shrink: 0;
    width: 112px;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 8px;
    padding: 16px 12px;
    border: 1.5px solid #eae8e4;
    border-radius: 12px;
    background: #faf8f3;
    cursor: pointer;
    transition: all 0.18s;
    font-family: 'DM Sans', system-ui, sans-serif;
    scroll-snap-align: start;
  }
  .member-pick:hover {
    border-color: #dfc876;
    background: #fbf7ec;
  }
  .member-pick--active {
    border-color: #b8973a;
    background: linear-gradient(135deg, #fbf7ec, #faf8f3);
    box-shadow: 0 4px 16px rgba(184, 151, 58, 0.18);
  }
  .member-pick__name {
    font-size: 13px;
    font-weight: 600;
    color: #0d0c0a;
    text-align: center;
  }
  .member-pick--active .member-pick__name {
    color: #9b7a25;
  }

  .divider {
    height: 1px;
    background: #eae8e4;
    margin: 24px 0;
  }

  /* ── Field ── */
  .field {
    margin-bottom: 18px;
  }
  .field__label {
    font-size: 11px;
    font-weight: 600;
    color: #6b6860;
    letter-spacing: 0.7px;
    text-transform: uppercase;
    margin-bottom: 6px;
    display: block;
  }
  .field-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
  }
  @media (max-width: 520px) {
    .field-row {
      grid-template-columns: 1fr;
    }
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
  }
  .i-field:focus {
    background: #ffffff;
  }
  .error-text {
    font-size: 12px;
    color: #c4402a;
    margin: 5px 0 0;
  }
  .hint-text {
    font-size: 12px;
    color: #9b7a25;
    margin: 5px 0 0;
    font-style: italic;
  }

  /* ── Review list ── */
  .review-list {
    background: #faf8f3;
    border: 1px solid #eae8e4;
    border-radius: 10px;
    padding: 18px 20px;
    margin-bottom: 20px;
  }
  .review-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px 0;
    border-bottom: 1px solid #eae8e4;
  }
  .review-row:last-child {
    border-bottom: none;
  }
  .review-row__label {
    font-size: 11px;
    font-weight: 600;
    color: #6b6860;
    letter-spacing: 0.5px;
    text-transform: uppercase;
  }
  .review-row__value {
    font-size: 14px;
    color: #0d0c0a;
    font-weight: 500;
  }
  .review-row__value--member {
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .privacy-note {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 14px 16px;
    background: linear-gradient(135deg, #fbf7ec, #f4f1e9);
    border: 1px solid #f2e9c8;
    border-radius: 8px;
    font-size: 13px;
    color: #7a5e1a;
    line-height: 1.6;
    margin-bottom: 24px;
  }

  .server-error {
    padding: 12px 14px;
    background: #fef0ed;
    border: 1px solid #e8897a;
    border-radius: 8px;
    font-size: 13px;
    color: #c4402a;
    margin-bottom: 16px;
  }

  /* ── Actions ── */
  .actions {
    display: flex;
    gap: 12px;
    margin-top: 8px;
  }
  .btn-secondary {
    flex: 1;
    height: 48px;
    background: #ffffff;
    color: #6b6860;
    border: 1.5px solid #d6d3ce;
    border-radius: 8px;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.18s;
  }
  .btn-secondary:hover:not(:disabled) {
    background: #f4f1e9;
    border-color: #b0ada7;
  }
  .btn-gold {
    flex: 1.5;
    height: 48px;
    background: linear-gradient(135deg, #b8973a, #c9a84c);
    color: #fff;
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
    box-shadow: 0 4px 16px rgba(184, 151, 58, 0.18);
  }
  .btn-gold:hover:not(:disabled) {
    background: linear-gradient(135deg, #9b7a25, #b8973a);
    transform: translateY(-1px);
  }
  .btn-gold:disabled,
  .btn-secondary:disabled {
    opacity: 0.4;
    cursor: not-allowed;
    transform: none;
  }

  /* ── Success modal ── */
  .success-overlay {
    position: fixed;
    inset: 0;
    background: rgba(13, 12, 10, 0.4);
    backdrop-filter: blur(8px);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 200;
    padding: 20px;
  }
  .success-card {
    background: #ffffff;
    border-radius: 20px;
    padding: 40px 36px 32px;
    width: 100%;
    max-width: 480px;
    text-align: center;
    box-shadow:
      0 24px 64px rgba(13, 12, 10, 0.2),
      0 0 0 1px rgba(184, 151, 58, 0.12);
    border-top: 3px solid #b8973a;
  }
  .success-icon {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background: linear-gradient(135deg, #fbf7ec, #faf8f3);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 18px;
    border: 2px solid #f2e9c8;
  }
  .success-title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 26px;
    font-weight: 600;
    color: #0d0c0a;
    margin: 0 0 10px;
  }
  .success-text {
    font-size: 14px;
    color: #6b6860;
    margin: 0 0 22px;
    line-height: 1.6;
  }
  .success-summary {
    background: #faf8f3;
    border: 1px solid #eae8e4;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 18px;
    text-align: left;
  }
  .success-summary__row {
    display: flex;
    justify-content: space-between;
    padding: 6px 0;
    font-size: 13px;
    color: #6b6860;
  }
  .success-summary__row strong {
    color: #0d0c0a;
    font-weight: 600;
  }

  /* ── Invite section у Success modal ── */
  .invite-section {
    text-align: left;
    margin-bottom: 22px;
  }
  .invite-section__label {
    font-size: 10px;
    font-weight: 700;
    color: #6b6860;
    letter-spacing: 0.7px;
    text-transform: uppercase;
    margin-bottom: 8px;
  }
  .invite-link-box {
    display: flex;
    align-items: stretch;
    border: 1.5px solid #dfc876;
    border-radius: 8px;
    overflow: hidden;
    background: #fff;
    box-shadow: 0 2px 8px rgba(184, 151, 58, 0.1);
  }
  .invite-link-box__url {
    flex: 1;
    padding: 0 14px;
    font-size: 12px;
    color: #6b6860;
    font-family: 'DM Mono', 'Courier New', monospace;
    display: flex;
    align-items: center;
    background: #fbf7ec;
    border-right: 1px solid #f2e9c8;
    min-height: 44px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .btn-copy {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 0 16px;
    background: #fff;
    border: none;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 12px;
    font-weight: 600;
    color: #9b7a25;
    cursor: pointer;
    transition: all 0.18s;
    flex-shrink: 0;
  }
  .btn-copy:hover {
    background: #fbf7ec;
  }
  .btn-copy--copied {
    color: #2a6b2a;
  }

  .success-actions {
    display: flex;
    gap: 12px;
  }

  .spinner {
    animation: spin 0.8s linear infinite;
  }
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }

  /* ── Toast ── */
  .toast {
    position: fixed;
    bottom: 28px;
    right: 28px;
    padding: 14px 20px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 500;
    z-index: 999;
    box-shadow: 0 8px 24px rgba(13, 12, 10, 0.14);
    font-family: 'DM Sans', system-ui, sans-serif;
  }
  .toast--success {
    background: #0d0c0a;
    color: #fff;
  }
  .toast--error {
    background: #fef0ed;
    color: #c4402a;
    border: 1px solid #e8897a;
  }
  .toast-enter-active,
  .toast-leave-active {
    transition: all 0.25s ease;
  }
  .toast-enter-from,
  .toast-leave-to {
    opacity: 0;
    transform: translateY(12px);
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
  .overlay-enter-active,
  .overlay-leave-active {
    transition: opacity 0.25s ease;
  }
  .overlay-enter-from,
  .overlay-leave-to {
    opacity: 0;
  }
  .modal-enter-active,
  .modal-leave-active {
    transition:
      opacity 0.25s ease,
      transform 0.25s ease;
  }
  .modal-enter-from,
  .modal-leave-to {
    opacity: 0;
    transform: scale(0.94) translateY(12px);
  }
</style>
