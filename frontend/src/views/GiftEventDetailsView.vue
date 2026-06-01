<template>
  <div class="page">
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
      </div>
    </header>

    <main class="main">
      <!-- Loading -->
      <div v-if="isLoading" class="state-card">
        <p class="state-card__text">Loading event...</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="state-card state-card--error">
        <h2 class="state-card__title">{{ errorTitle }}</h2>
        <p class="state-card__text">{{ error }}</p>
        <button class="btn-secondary" @click="$router.push('/feed')">Back to Feed</button>
      </div>

      <!-- WOW EXPERIENCE — target user after unlock -->
      <div v-else-if="isWowMode && gift" class="wow-card">
        <canvas ref="confettiCanvas" class="wow-canvas" aria-hidden="true"></canvas>

        <div class="wow-icon">
          <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
            <rect x="8" y="20" width="48" height="34" rx="3" fill="#b8973a" />
            <rect x="8" y="20" width="48" height="6" fill="#9b7a25" />
            <path
              d="M32 14V54M20 14C20 8 26 6 32 14C38 6 44 8 44 14"
              stroke="#dfc876"
              stroke-width="3"
              stroke-linecap="round"
            />
          </svg>
        </div>

        <h1 class="wow-title">{{ gift.name }}</h1>
        <p class="wow-subtitle">Your family collected this for you</p>

        <div class="wow-amount">
          <div class="wow-amount__value">
            {{ formatAmount(gift.collected_amount) }}
          </div>
          <div class="wow-amount__currency">UAH</div>
        </div>

        <div class="wow-meta">Unlocked on {{ formatDate(gift.unlock_date) }}</div>

        <div class="donors-section">
          <div class="donors-section__title">From your family</div>
          <div class="donors-list">
            <div v-for="donor in gift.donors" :key="donor.id" class="donor-row">
              <div class="avatar avatar--sm" :class="`avatar--${avatarVariant(donor.name)}`">
                {{ getInitials(donor.name) }}
              </div>
              <span class="donor-row__name">{{ donor.name }}</span>
              <span v-if="donor.amount" class="donor-row__amount">
                {{ formatAmount(donor.amount) }} UAH
              </span>
            </div>
          </div>
        </div>

        <div class="wow-actions">
          <button class="btn-gold" @click="$router.push('/feed')">Continue to feed</button>
        </div>
      </div>

      <!-- ORGANIZER / DONOR VIEW — before unlock or when I'm not target -->
      <div v-else-if="gift" class="detail-card">
        <div class="detail-card__header">
          <h1 class="detail-card__title">{{ gift.name }}</h1>
          <span class="status-badge" :class="`status-badge--${gift.status?.toLowerCase()}`">
            {{ gift.status }}
          </span>
        </div>

        <div class="detail-meta">
          <div class="detail-meta__row">
            <span class="detail-meta__label">Recipient</span>
            <span class="detail-meta__value">{{ gift.target_user_name }}</span>
          </div>
          <div class="detail-meta__row">
            <span class="detail-meta__label">Organizer</span>
            <span class="detail-meta__value">{{ gift.organizer_name }}</span>
          </div>
          <div class="detail-meta__row">
            <span class="detail-meta__label">Unlock date</span>
            <span class="detail-meta__value">{{ formatDate(gift.unlock_date) }}</span>
          </div>
        </div>

        <!-- Progress -->
        <div class="progress-section">
          <div class="progress-section__top">
            <span class="progress-section__label">Collected</span>
            <span class="progress-section__value">
              <strong>{{ formatAmount(gift.collected_amount) }}</strong>
              / {{ formatAmount(gift.goal_amount) }} UAH
            </span>
          </div>
          <div class="progress-bar">
            <div class="progress-bar__fill" :style="{ width: progressPercent + '%' }"></div>
          </div>
          <div class="progress-section__percent">{{ progressPercent }}%</div>
        </div>

        <!-- Invite link — для organizer -->
        <div v-if="isOrganizer" class="invite-section">
          <div class="invite-section__label">SHARE WITH FAMILY</div>
          <div v-if="inviteUrl" class="invite-link-box">
            <div class="invite-link-box__url">{{ inviteUrl }}</div>
            <button
              class="btn-copy"
              :class="{ 'btn-copy--copied': isLinkCopied }"
              @click="copyInviteLink"
            >
              {{ isLinkCopied ? 'Copied!' : 'Copy' }}
            </button>
          </div>
          <button v-else class="btn-secondary" :disabled="isGeneratingLink" @click="generateLink">
            {{ isGeneratingLink ? 'Generating...' : 'Get invite link' }}
          </button>
        </div>

        <!-- Donors list -->
        <div v-if="gift.donors?.length" class="donors-section">
          <div class="donors-section__title">Contributors</div>
          <div class="donors-list">
            <div v-for="donor in gift.donors" :key="donor.id" class="donor-row">
              <div class="avatar avatar--sm" :class="`avatar--${avatarVariant(donor.name)}`">
                {{ getInitials(donor.name) }}
              </div>
              <span class="donor-row__name">{{ donor.name }}</span>
              <span class="donor-row__amount">{{ formatAmount(donor.amount) }} UAH</span>
            </div>
          </div>
        </div>

        <div v-else class="empty-donors">No contributions yet. Share the link with family!</div>
      </div>
    </main>

    <!-- Toast -->
    <Transition name="toast">
      <div v-if="toast.isVisible" class="toast" :class="`toast--${toast.type}`" role="alert">
        {{ toast.message }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
  import { ref, computed, onMounted, nextTick } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import { useAuth } from '../composables/useAuth'
  import { fetchGiftEventDetails, generateGiftInviteLink } from '../services/giftEventService'

  const route = useRoute()
  const router = useRouter()
  const { currentUser } = useAuth()

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

  const giftId = computed(() => route.params.id)

  const gift = ref(null)
  const isLoading = ref(true)
  const error = ref('')
  const errorTitle = ref('Event not available')

  const confettiCanvas = ref(null)

  const isTarget = computed(() => currentUser.value?.id === gift.value?.target_user_id)
  const isOrganizer = computed(() => currentUser.value?.id === gift.value?.organizer_id)
  const isUnlocked = computed(() => {
    if (!gift.value?.unlock_date) return false
    return new Date(gift.value.unlock_date).getTime() <= Date.now()
  })
  const isWowMode = computed(
    () => isTarget.value && (gift.value?.status === 'REVEALED' || isUnlocked.value),
  )

  const progressPercent = computed(() => {
    if (!gift.value?.goal_amount) return 0
    const pct = (Number(gift.value.collected_amount) / Number(gift.value.goal_amount)) * 100
    return Math.min(100, Math.round(pct))
  })

  async function loadDetails() {
    isLoading.value = true
    error.value = ''

    try {
      const data = await fetchGiftEventDetails(giftId.value)
      gift.value = data

      // wow-екран → запускаємо конфеті після рендеру
      if (isWowMode.value) {
        await nextTick()
        triggerConfetti()
      }
    } catch (err) {
      const status = err.response?.status
      if (status === 403) {
        errorTitle.value = 'Surprise in progress'
        error.value =
          "This event is being prepared for you by your family. You'll see it on the unlock date."
      } else if (status === 404) {
        errorTitle.value = 'Event not found'
        error.value = "This event doesn't exist or has been cancelled."
      } else {
        errorTitle.value = 'Could not load event'
        error.value = err.response?.data?.message || 'Please try again later.'
      }
    } finally {
      isLoading.value = false
    }
  }

  async function triggerConfetti() {
    try {
      const confetti = (await import('canvas-confetti')).default
      const duration = 3000
      const end = Date.now() + duration

      const goldColors = ['#b8973a', '#dfc876', '#c4862a', '#ead9a0', '#9b7a25']

      ;(function frame() {
        confetti({
          particleCount: 4,
          angle: 60,
          spread: 55,
          origin: { x: 0, y: 0.6 },
          colors: goldColors,
        })
        confetti({
          particleCount: 4,
          angle: 120,
          spread: 55,
          origin: { x: 1, y: 0.6 },
          colors: goldColors,
        })
        if (Date.now() < end) requestAnimationFrame(frame)
      })()
    } catch (err) {
      // canvas-confetti не встановлений — wow-екран без конфеті
      console.warn('canvas-confetti not available:', err)
    }
  }

  function formatAmount(amount) {
    const num = Number(amount)
    if (isNaN(num)) return '0'
    return new Intl.NumberFormat('uk-UA').format(num)
  }

  function formatDate(isoString) {
    if (!isoString) return ''
    const d = new Date(isoString)
    return new Intl.DateTimeFormat('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
      timeZoneName: 'short',
    }).format(d)
  }

  function getInitials(name) {
    if (!name) return '?'
    return name
      .split(' ')
      .map((w) => w[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  }

  function avatarVariant(name) {
    const variants = ['gold', 'dark', 'light']
    const idx = (name?.charCodeAt(0) || 0) % variants.length
    return variants[idx]
  }

  // ─── Invite link (PROJ-57) ───
  const inviteUrl = ref('')
  const isGeneratingLink = ref(false)
  const isLinkCopied = ref(false)

  async function generateLink() {
    isGeneratingLink.value = true
    try {
      const data = await generateGiftInviteLink(giftId.value)
      inviteUrl.value = data.invite_url
      showToast('Link generated', 'success')
    } catch (err) {
      const message = err.response?.data?.message || 'Failed to generate link.'
      showToast(message, 'error')
    } finally {
      isGeneratingLink.value = false
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

  // ─── Toast ───
  const toast = ref({ isVisible: false, message: '', type: 'success' })

  function showToast(message, type = 'success') {
    toast.value = { isVisible: true, message, type }
    setTimeout(() => {
      toast.value.isVisible = false
    }, 3000)
  }

  onMounted(loadDetails)
</script>

<style scoped>
  .page {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    background: #faf8f3;
  }

  /* Navbar */
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

  /* Main */
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

  /* State cards (loading / error) */
  .state-card {
    background: #fff;
    border-radius: 16px;
    padding: 60px 36px;
    text-align: center;
    box-shadow: 0 8px 32px rgba(13, 12, 10, 0.06);
    border-top: 3px solid #b8973a;
  }
  .state-card--error {
    border-top-color: #dfc876;
  }
  .state-card__title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 24px;
    color: #0d0c0a;
    margin: 0 0 10px;
  }
  .state-card__text {
    font-size: 14px;
    color: #6b6860;
    margin: 0 0 24px;
    line-height: 1.6;
  }

  /* WOW card */
  .wow-card {
    background: linear-gradient(135deg, #fbf7ec 0%, #ffffff 50%, #f4f1e9 100%);
    border-radius: 24px;
    padding: 48px 36px 40px;
    text-align: center;
    position: relative;
    overflow: hidden;
    box-shadow:
      0 24px 64px rgba(184, 151, 58, 0.2),
      0 0 0 2px rgba(184, 151, 58, 0.2);
  }

  .wow-canvas {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    pointer-events: none;
  }

  .wow-icon {
    width: 96px;
    height: 96px;
    border-radius: 50%;
    background: linear-gradient(135deg, #fff, #fbf7ec);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 24px;
    border: 2px solid #f2e9c8;
    box-shadow: 0 8px 24px rgba(184, 151, 58, 0.18);
    position: relative;
    z-index: 1;
  }

  .wow-title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 38px;
    font-weight: 600;
    color: #0d0c0a;
    margin: 0 0 10px;
    position: relative;
    z-index: 1;
  }
  .wow-subtitle {
    font-size: 15px;
    color: #6b6860;
    margin: 0 0 32px;
    position: relative;
    z-index: 1;
  }

  .wow-amount {
    display: inline-block;
    padding: 20px 36px;
    background: #fff;
    border-radius: 16px;
    border: 2px solid #dfc876;
    box-shadow: 0 8px 24px rgba(184, 151, 58, 0.2);
    margin-bottom: 16px;
    position: relative;
    z-index: 1;
  }
  .wow-amount__value {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 56px;
    font-weight: 600;
    color: #9b7a25;
    line-height: 1;
  }
  .wow-amount__currency {
    font-size: 12px;
    font-weight: 600;
    color: #b0ada7;
    letter-spacing: 1.5px;
    margin-top: 6px;
    text-transform: uppercase;
  }

  .wow-meta {
    font-size: 13px;
    color: #6b6860;
    margin-bottom: 32px;
    position: relative;
    z-index: 1;
  }

  .wow-actions {
    margin-top: 24px;
    display: flex;
    justify-content: center;
    position: relative;
    z-index: 1;
  }

  /* Detail card (organizer/donor view) */
  .detail-card {
    background: #fff;
    border-radius: 16px;
    padding: 36px;
    box-shadow:
      0 8px 32px rgba(13, 12, 10, 0.06),
      0 0 0 1px rgba(184, 151, 58, 0.08);
    border-top: 3px solid #b8973a;
  }
  @media (max-width: 560px) {
    .detail-card {
      padding: 24px 20px;
    }
  }

  .detail-card__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
  }
  .detail-card__title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 26px;
    font-weight: 600;
    color: #0d0c0a;
    margin: 0;
  }

  .status-badge {
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 0.7px;
    text-transform: uppercase;
  }
  .status-badge--active {
    background: #eef7ee;
    color: #2a6b2a;
    border: 1px solid #8bc88b;
  }
  .status-badge--revealed {
    background: linear-gradient(135deg, #b8973a, #c9a84c);
    color: #fff;
  }
  .status-badge--cancelled {
    background: #fef0ed;
    color: #c4402a;
    border: 1px solid #e8897a;
  }

  .detail-meta {
    background: #faf8f3;
    border: 1px solid #eae8e4;
    border-radius: 10px;
    padding: 16px 20px;
    margin-bottom: 24px;
  }
  .detail-meta__row {
    display: flex;
    justify-content: space-between;
    padding: 8px 0;
    border-bottom: 1px solid #eae8e4;
  }
  .detail-meta__row:last-child {
    border-bottom: none;
  }
  .detail-meta__label {
    font-size: 11px;
    font-weight: 600;
    color: #6b6860;
    letter-spacing: 0.5px;
    text-transform: uppercase;
  }
  .detail-meta__value {
    font-size: 13px;
    color: #0d0c0a;
    font-weight: 500;
  }

  /* Progress */
  .progress-section {
    margin-bottom: 28px;
  }
  .progress-section__top {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 8px;
  }
  .progress-section__label {
    font-size: 11px;
    font-weight: 700;
    color: #6b6860;
    letter-spacing: 0.7px;
    text-transform: uppercase;
  }
  .progress-section__value {
    font-size: 14px;
    color: #6b6860;
  }
  .progress-section__value strong {
    color: #0d0c0a;
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 18px;
    font-weight: 600;
  }
  .progress-bar {
    height: 8px;
    background: #eae8e4;
    border-radius: 9999px;
    overflow: hidden;
    margin-bottom: 6px;
  }
  .progress-bar__fill {
    height: 100%;
    background: linear-gradient(90deg, #b8973a, #dfc876);
    border-radius: 9999px;
    transition: width 0.6s ease;
  }
  .progress-section__percent {
    font-size: 11px;
    color: #b0ada7;
    text-align: right;
  }

  /* Invite section */
  .invite-section {
    margin-bottom: 28px;
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
    padding: 0 16px;
    background: #fff;
    border: none;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 12px;
    font-weight: 600;
    color: #9b7a25;
    cursor: pointer;
    transition: all 0.18s;
  }
  .btn-copy:hover {
    background: #fbf7ec;
  }
  .btn-copy--copied {
    color: #2a6b2a;
  }

  /* Donors */
  .donors-section {
    margin-top: 24px;
    position: relative;
    z-index: 1;
  }
  .donors-section__title {
    font-size: 11px;
    font-weight: 700;
    color: #6b6860;
    letter-spacing: 0.7px;
    text-transform: uppercase;
    margin-bottom: 12px;
    text-align: left;
  }
  .donors-list {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .donor-row {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 12px 14px;
    background: #fff;
    border: 1px solid #eae8e4;
    border-radius: 10px;
  }
  .donor-row__name {
    flex: 1;
    font-size: 13px;
    color: #0d0c0a;
    font-weight: 500;
    text-align: left;
  }
  .donor-row__amount {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 16px;
    font-weight: 600;
    color: #9b7a25;
  }

  .empty-donors {
    padding: 24px;
    text-align: center;
    background: #faf8f3;
    border: 1px dashed #d6d3ce;
    border-radius: 10px;
    color: #b0ada7;
    font-size: 13px;
  }

  /* Buttons */
  .btn-secondary {
    padding: 0 24px;
    height: 44px;
    background: #fff;
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
  .btn-secondary:disabled {
    opacity: 0.4;
    cursor: not-allowed;
  }
  .btn-gold {
    padding: 0 32px;
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
    box-shadow: 0 4px 16px rgba(184, 151, 58, 0.18);
  }
  .btn-gold:hover {
    background: linear-gradient(135deg, #9b7a25, #b8973a);
    transform: translateY(-1px);
  }

  /* Toast */
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

  @media (max-width: 768px) {
    .navbar {
      grid-template-columns: 1fr auto;
      grid-template-rows: auto auto;
      height: auto;
      padding: 10px 14px;
      gap: 8px 10px;
    }
    .navbar__left {
      grid-row: 1;
      grid-column: 1;
    }
    .navbar__right {
      grid-row: 1;
      grid-column: 2;
      gap: 6px;
    }
    .navbar__center {
      grid-row: 2;
      grid-column: 1 / -1;
      justify-self: stretch;
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
    }
    .navbar__center::-webkit-scrollbar {
      display: none;
    }
    .navbar__logo {
      font-size: 15px;
    }
    .navbar__tab {
      padding: 6px 14px;
      font-size: 12px;
    }
    .navbar__user-name {
      display: none;
    }
  }

  @media (max-width: 480px) {
    .navbar {
      padding: 8px 12px;
    }
    .navbar__tab {
      padding: 5px 12px;
      font-size: 11px;
    }
  }

  @media (max-width: 768px) {
    .detail-card {
      padding: 24px 18px;
    }
    .detail-card__header {
      flex-direction: column;
      align-items: flex-start;
      gap: 10px;
    }
    .invite-link-box {
      flex-direction: column;
    }
    .invite-link-box__url {
      border-right: none;
      border-bottom: 1px solid #f2e9c8;
      font-size: 11px;
    }
    .btn-copy {
      width: 100%;
      padding: 12px;
    }
  }

  @media (max-width: 480px) {
    .wow-card {
      padding: 36px 20px 28px;
    }
    .wow-title {
      font-size: 28px;
    }
    .wow-amount {
      padding: 16px 24px;
    }
    .wow-amount__value {
      font-size: 42px;
    }
    .wow-subtitle {
      font-size: 13px;
    }
    .detail-card__title {
      font-size: 22px;
    }
    .progress-section__value strong {
      font-size: 16px;
    }
    .donor-row {
      padding: 10px 12px;
      gap: 10px;
    }
    .donor-row__amount {
      font-size: 14px;
    }
  }
</style>
