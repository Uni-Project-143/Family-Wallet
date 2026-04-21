<template>
  <div class="feed-page">
    <!-- ═══ NAVBAR ═══ -->
    <header class="navbar">
      <div class="navbar__left">
        <span class="navbar__logo">Family <span class="navbar__logo--accent">Wallet</span></span>
        <div class="navbar__groups">
          <button
            v-for="group in groups"
            :key="group.id"
            class="navbar__group-tab"
            :class="{ 'navbar__group-tab--active': group.id === activeGroupId }"
            @click="activeGroupId = group.id"
          >
            {{ group.name }}
          </button>
          <!-- СТАЛО -->
          <button v-if="isAdmin" class="navbar__group-tab navbar__group-tab--add">
            + New group
          </button>
        </div>
      </div>

      <!-- Центр: три вкладки -->
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

      <!-- Права: аватар + ім'я + badge -->
      <div class="navbar__right">
        <div class="avatar avatar--sm avatar--gold">{{ currentUserInitials }}</div>
        <span class="navbar__user-name">{{ currentUserName }}</span>
        <span v-if="isAdmin" class="badge badge--admin">Admin</span>
        <span v-else class="badge badge--member">Member</span>
      </div>
    </header>

    <!-- ═══ BODY ═══ -->
    <div class="feed-layout">
      <!-- SIDEBAR -->
      <aside class="sidebar">
        <section class="sidebar__section">
          <div class="sidebar__section-title">Group Members</div>
          <div v-for="member in groupMembers" :key="member.id" class="member-row">
            <div class="member-row__left">
              <div class="avatar avatar--sm" :class="`avatar--${member.avatarVariant}`">
                {{ member.initials }}
              </div>
              <span class="member-row__name">{{ member.name }}</span>
              <span v-if="member.isCurrentUser" class="member-row__you">(you)</span>
              <span v-if="member.role === 'ADMIN'" class="badge badge--admin">Admin</span>
            </div>
            <button
              v-if="!member.isCurrentUser"
              class="money-btn"
              @click="openMoneyRequestModal(member)"
            >
              $
            </button>
          </div>
          <!-- + Invite member — тільки Admin (US 1.3)        !!!!!!!!!!!!!!!!!!!!!!!! -->
          <button v-if="isAdmin" class="invite-btn" @click="isInviteModalOpen = true">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
              <path
                d="M6 2V10M2 6H10"
                stroke="currentColor"
                stroke-width="1.5"
                stroke-linecap="round"
              />
            </svg>
            Invite member
          </button>
          <!-- 3б. Сам компонент модалки -->
          <InviteMemberModal
            :is-open="isInviteModalOpen"
            @close="isInviteModalOpen = false"
            @toast="showToast($event.message, $event.type)"
          />
        </section>

        <section class="sidebar__section">
          <div class="sidebar__section-title">Connected Cards</div>
          <div v-for="card in connectedCards" :key="card.id" class="card-widget">
            <div class="card-widget__header">
              <span class="card-widget__bank">{{ card.bankName }}</span>
              <span class="card-widget__dot"></span>
            </div>
            <div class="card-widget__pan">{{ card.maskedPan }}</div>
            <div class="card-widget__balance">{{ formatCurrency(card.balance) }}</div>
          </div>
          <button v-if="isAdmin" class="connect-card-btn" @click="goToConnectCard">
            + Connect Card
          </button>
        </section>
      </aside>

      <!-- FEED MAIN -->
      <main class="feed-main">
        <div class="feed-main__header">
          <h1 class="feed-main__title">Family Feed</h1>
          <div class="feed-filters">
            <button
              v-for="f in memberFilters"
              :key="f.value"
              class="feed-filter-chip"
              :class="{ 'feed-filter-chip--active': activeFilter === f.value }"
              @click="activeFilter = f.value"
            >
              {{ f.label }}
            </button>
          </div>
        </div>

        <template v-if="isLoadingFeed">
          <div v-for="i in 3" :key="i" class="tx-card">
            <div class="skeleton skeleton--circle"></div>
            <div style="flex: 1">
              <div class="skeleton skeleton--line" style="width: 35%"></div>
              <div class="skeleton skeleton--line" style="width: 55%"></div>
              <div class="skeleton skeleton--line" style="width: 28%"></div>
            </div>
          </div>
        </template>

        <template v-else>
          <TransitionGroup name="tx-list" tag="div">
            <div
              v-for="tx in filteredTransactions"
              :key="tx.id"
              class="tx-card"
              :class="{ 'tx-card--secret': tx.isSecretGift }"
            >
              <template v-if="tx.isSecretGift">
                <div class="avatar avatar--md" style="opacity: 0.4">?</div>
                <div class="tx-card__body">
                  <div class="tx-card__name tx-card__name--muted">
                    [Secret Gift Transaction — hidden]
                  </div>
                  <div class="tx-card__note"></div>
                </div>
                <div class="tx-card__amount tx-card__amount--muted">— UAH</div>
              </template>
              <template v-else>
                <div class="avatar avatar--md" :class="`avatar--${tx.authorAvatarVariant}`">
                  {{ tx.authorInitials }}
                </div>
                <div class="tx-card__body">
                  <div class="tx-card__header">
                    <div>
                      <div class="tx-card__name">{{ tx.authorName }}</div>
                      <div class="tx-card__category">{{ tx.categoryEmoji }} {{ tx.category }}</div>
                      <div class="tx-card__desc">{{ tx.description }}</div>
                      <div class="tx-card__date">{{ tx.timestamp }}</div>
                    </div>
                    <div class="tx-card__amount">
                      {{ tx.amount }} <span class="tx-card__currency">UAH</span>
                    </div>
                  </div>
                  <div class="tx-card__reactions">
                    <button v-for="r in tx.reactions" :key="r.emoji" class="reaction-pill">
                      {{ r.emoji }} {{ r.count }}
                    </button>
                    <button class="reaction-add">+ React</button>
                  </div>
                </div>
              </template>
            </div>
          </TransitionGroup>
          <div v-if="filteredTransactions.length === 0" class="feed-empty">
            <p>Підключіть картку Monobank, щоб бачити транзакції</p>
          </div>
        </template>
      </main>

      <!-- RIGHT PANEL -->
      <aside class="right-panel">
        <section class="right-panel__section">
          <div class="right-panel__title">Spending by Category</div>
          <div class="donut-wrap">
            <svg width="152" height="152" viewBox="0 0 160 160">
              <circle cx="80" cy="80" r="56" fill="none" stroke="#F0EFED" stroke-width="26" />
              <circle
                cx="80"
                cy="80"
                r="56"
                fill="none"
                stroke="#C4862A"
                stroke-width="26"
                stroke-dasharray="123.2 351.9"
                stroke-dashoffset="0"
                transform="rotate(-90 80 80)"
              />
              <circle
                cx="80"
                cy="80"
                r="56"
                fill="none"
                stroke="#4A6FA5"
                stroke-width="26"
                stroke-dasharray="88.0 351.9"
                stroke-dashoffset="-123.2"
                transform="rotate(-90 80 80)"
              />
              <circle
                cx="80"
                cy="80"
                r="56"
                fill="none"
                stroke="#5A8A6A"
                stroke-width="26"
                stroke-dasharray="52.8 351.9"
                stroke-dashoffset="-211.2"
                transform="rotate(-90 80 80)"
              />
              <circle
                cx="80"
                cy="80"
                r="56"
                fill="none"
                stroke="#C4613A"
                stroke-width="26"
                stroke-dasharray="52.8 351.9"
                stroke-dashoffset="-264.0"
                transform="rotate(-90 80 80)"
              />
              <circle
                cx="80"
                cy="80"
                r="56"
                fill="none"
                stroke="#8A7AAA"
                stroke-width="26"
                stroke-dasharray="35.2 351.9"
                stroke-dashoffset="-316.8"
                transform="rotate(-90 80 80)"
              />
              <text
                x="80"
                y="74"
                text-anchor="middle"
                font-size="10"
                fill="#B0ADA7"
                font-family="DM Sans,sans-serif"
              >
                Total
              </text>
              <text
                x="80"
                y="90"
                text-anchor="middle"
                font-size="16"
                fill="#0D0C0A"
                font-family="Cormorant Garamond,serif"
                font-weight="600"
              >
                2 412
              </text>
              <text
                x="80"
                y="104"
                text-anchor="middle"
                font-size="10"
                fill="#B0ADA7"
                font-family="DM Sans,sans-serif"
              >
                UAH
              </text>
            </svg>
            <div class="donut-legend">
              <div v-for="cat in categoryBreakdown" :key="cat.name" class="donut-legend__row">
                <span class="donut-legend__dot" :style="{ background: cat.color }"></span>
                <span class="donut-legend__label">{{ cat.name }}</span>
                <span class="donut-legend__pct">{{ cat.pct }}%</span>
              </div>
              <div class="donut-legend__note">Categories from Monobank MCC codes</div>
            </div>
          </div>
        </section>

        <section v-if="activeGiftEvents.length" class="right-panel__section">
          <div class="right-panel__title">Active Gift Events</div>
          <div v-for="event in activeGiftEvents" :key="event.id" class="gift-card">
            <div class="gift-card__title">{{ event.name }}</div>
            <div class="gift-card__meta">
              Target: {{ event.targetUser }}<br />
              Unlock: {{ event.unlockDate }}<br />
              Collected: {{ event.collected }} / {{ event.goal }} UAH
            </div>
            <div class="progress-bar">
              <div class="progress-bar__fill" :style="{ width: event.progressPct + '%' }"></div>
            </div>
            <button class="btn-view-event" @click="$router.push(`/gift-events/${event.id}`)">
              View Event →
            </button>
          </div>
        </section>

        <section class="right-panel__section">
          <div class="right-panel__title">Notifications</div>
          <div
            v-for="n in notifications"
            :key="n.id"
            class="notif-item"
            :class="{ 'notif-item--unread': n.isUnread }"
          >
            <div class="notif-item__title">{{ n.title }}</div>
            <div class="notif-item__sub">{{ n.subtitle }}</div>
          </div>
        </section>
      </aside>
    </div>

    <!-- Toast -->
    <Transition name="toast">
      <div v-if="toast.isVisible" class="toast" :class="`toast--${toast.type}`" role="alert">
        {{ toast.message }}
      </div>
    </Transition>
  </div>
</template>

<script setup>
  import { ref, computed, onMounted, onUnmounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { useAuth } from '../composables/useAuth'
  // 1. Імпорт
  import InviteMemberModal from '../components/InviteMemberModal.vue'

  // 2. Стан модалки
  const isInviteModalOpen = ref(false)
  const router = useRouter()
  //const { currentUser, isAdmin } = useAuth()

  const { currentUser } = useAuth()
  // Тимчасово: хардкодимо Admin для демо без бекенду
  // TODO: прибрати коли бекенд поверне реальний JWT з role: 'ADMIN'
  // const isAdmin = ref(true)

  const currentUserName = computed(() => currentUser.value?.fullName || 'Olena K.')
  const currentUserInitials = computed(() => {
    const name = currentUser.value?.fullName || 'OK'
    return name
      .split(' ')
      .map((w) => w[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  })

  const activeGroupId = ref(1)
  // СТАЛО
  const storedUser = JSON.parse(localStorage.getItem('currentUser') || '{}')

  const groups = ref([
    { id: 1, name: storedUser.groupName || 'Family' },
    { id: 2, name: 'Neighborhood' },
  ])

  //для ролі. Замість const isAdmin = ref(true)
  const isAdmin = computed(() => storedUser.role === 'ADMIN')

  const groupMembers = ref([
    {
      id: 1,
      name: 'Olena K.',
      initials: 'OK',
      role: 'ADMIN',
      avatarVariant: 'gold',
      isCurrentUser: true,
    },
    {
      id: 2,
      name: 'Mykola K.',
      initials: 'MK',
      role: 'MEMBER',
      avatarVariant: 'dark',
      isCurrentUser: false,
    },
    {
      id: 3,
      name: 'Sofia K.',
      initials: 'SK',
      role: 'MEMBER',
      avatarVariant: 'light',
      isCurrentUser: false,
    },
  ])

  const connectedCards = ref([
    { id: 1, bankName: 'Monobank', maskedPan: '•••• •••• •••• 4521', balance: 12340 },
    { id: 2, bankName: 'Monobank', maskedPan: '•••• •••• •••• 7732', balance: 3870 },
  ])

  const isLoadingFeed = ref(false)
  const transactions = ref([
    {
      id: 1,
      authorName: 'Olena K.',
      authorInitials: 'OK',
      authorAvatarVariant: 'gold',
      category: 'Food & Groceries',
      categoryEmoji: '🛒',
      description: 'ATB Market',
      timestamp: '2025-04-14 14:23',
      amount: '−482',
      isSecretGift: false,
      reactions: [
        { emoji: '😮', count: 2 },
        { emoji: '👍', count: 1 },
      ],
    },
    {
      id: 2,
      authorName: 'Mykola K.',
      authorInitials: 'MK',
      authorAvatarVariant: 'dark',
      category: 'Transport',
      categoryEmoji: '⛽',
      description: 'WOG Station',
      timestamp: '2025-04-14 11:05',
      amount: '−1 200',
      isSecretGift: false,
      reactions: [{ emoji: '🔥', count: 3 }],
    },
    { id: 3, isSecretGift: true },
    {
      id: 4,
      authorName: 'Sofia K.',
      authorInitials: 'SK',
      authorAvatarVariant: 'light',
      category: 'Pharmacy',
      categoryEmoji: '💊',
      description: 'Apteka Dobryy Den',
      timestamp: '2025-04-13 18:44',
      amount: '−230',
      isSecretGift: false,
      reactions: [],
    },
  ])

  const activeFilter = ref('all')
  const memberFilters = computed(() => [
    { value: 'all', label: 'All' },
    ...groupMembers.value.map((m) => ({ value: m.id, label: m.name.split(' ')[0] })),
  ])

  const filteredTransactions = computed(() => {
    if (activeFilter.value === 'all') return transactions.value
    return transactions.value.filter(
      (tx) =>
        tx.isSecretGift ||
        tx.authorName === groupMembers.value.find((m) => m.id === activeFilter.value)?.name,
    )
  })

  const categoryBreakdown = ref([
    { name: 'Food & Groceries', pct: 35, color: '#C4862A' },
    { name: 'Transport', pct: 25, color: '#4A6FA5' },
    { name: 'Pharmacy', pct: 15, color: '#5A8A6A' },
    { name: 'Cafe & Restaurant', pct: 15, color: '#C4613A' },
    { name: 'Other', pct: 10, color: '#8A7AAA' },
  ])

  const activeGiftEvents = ref([
    {
      id: 1,
      name: "Sofia's Birthday",
      targetUser: 'Sofia K.',
      unlockDate: 'Apr 15, 2025',
      collected: 1200,
      goal: 2000,
      progressPct: 60,
    },
  ])

  const notifications = ref([
    {
      id: 1,
      title: 'Gift unlock in 24h 🎁',
      subtitle: "Sofia's Birthday — Apr 15",
      isUnread: true,
    },
    {
      id: 2,
      title: 'Mykola reacted 🔥 to your expense',
      subtitle: 'Today at 11:08',
      isUnread: false,
    },
  ])

  const toast = ref({ isVisible: false, message: '', type: 'success' })

  /**
   * Показує toast-повідомлення.
   * @param {string} message
   * @param {'success'|'error'|'info'} type
   */
  function showToast(message, type = 'success') {
    toast.value = { isVisible: true, message, type }
    setTimeout(() => {
      toast.value.isVisible = false
    }, 4000)
  }

  function openMoneyRequestModal(member) {
    showToast(`Opening request to ${member.name}`, 'info')
  }

  /**
   * Форматує суму у гривнях.
   * @param {number} amount
   * @returns {string}
   */
  function formatCurrency(amount) {
    return amount.toLocaleString('uk-UA') + ' UAH'
  }

  let wsConnection = null

  function connectWebSocket() {
    // Вимикаємо WebSocket поки немає бекенду
    if (import.meta.env.VITE_WS_ENABLED !== 'true') return
    const token = localStorage.getItem('accessToken')
    if (!token) return
    try {
      wsConnection = new WebSocket(
        `${import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws'}?token=${token}`,
      )
      wsConnection.onmessage = (event) => {
        const data = JSON.parse(event.data)
        if (data.type === 'new_transaction') transactions.value.unshift(data.transaction)
      }
    } catch {
      // silent fallback
    }
  }

  onMounted(() => connectWebSocket())
  onUnmounted(() => {
    if (wsConnection) wsConnection.close()
  })

  function goToInvite() {
    router.push({ path: '/settings', query: { section: 'members' } })
    showToast('Opening invite members section', 'info')
  }

  function goToConnectCard() {
    router.push({ path: '/settings', query: { section: 'cards' } })
    showToast('Opening connect card section', 'info')
  }
</script>

<style scoped>
  .feed-page {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    background: #faf8f3;
  }

  /* ── Navbar ── */
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
    white-space: nowrap;
  }
  .navbar__logo--accent {
    color: #b8973a;
  }
  .navbar__groups {
    display: flex;
    gap: 3px;
  }
  .navbar__group-tab {
    padding: 5px 14px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.5);
    border: 1px solid transparent;
    background: none;
    cursor: pointer;
    transition: all 0.18s;
    font-family: 'DM Sans', system-ui, sans-serif;
  }
  .navbar__group-tab--active {
    background: rgba(184, 151, 58, 0.15);
    border-color: rgba(184, 151, 58, 0.3);
    color: #dfc876;
  }
  .navbar__group-tab--add {
    color: rgba(184, 151, 58, 0.6);
  }

  /* Центровані таби */
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

  /* ── Layout ── */
  .feed-layout {
    display: flex;
    flex: 1;
    height: calc(100vh - 60px);
    overflow: hidden;
  }

  /* ── Sidebar ── */
  .sidebar {
    width: 256px;
    background: #fff;
    border-right: 1px solid #eae8e4;
    padding: 20px 16px;
    overflow-y: auto;
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    gap: 24px;
  }
  /* .sidebar__section {
  } */
  .sidebar__section-title {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #b0ada7;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .sidebar__section-title::after {
    content: '';
    flex: 1;
    height: 1px;
    background: #eae8e4;
  }

  .member-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 7px 8px;
    border-radius: 8px;
    transition: background 0.15s;
  }
  .member-row:hover {
    background: #fbf7ec;
  }
  .member-row__left {
    display: flex;
    align-items: center;
    gap: 9px;
  }
  .member-row__name {
    font-size: 13px;
    font-weight: 500;
    color: #0d0c0a;
  }
  .member-row__you {
    font-size: 11px;
    color: #b0ada7;
  }

  .money-btn {
    width: 28px;
    height: 28px;
    border-radius: 6px;
    border: 1.5px solid #d6d3ce;
    background: #f4f1e9;
    color: #6b6860;
    font-size: 13px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.18s;
    flex-shrink: 0;
  }
  .money-btn:hover {
    background: #b8973a;
    color: #fff;
    border-color: #b8973a;
    box-shadow: 0 2px 8px rgba(184, 151, 58, 0.25);
  }

  .invite-btn {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 10px;
    border: 1.5px dashed #d6d3ce;
    border-radius: 8px;
    color: #b0ada7;
    font-size: 12px;
    background: none;
    font-family: 'DM Sans', system-ui, sans-serif;
    cursor: pointer;
    transition: all 0.18s;
    margin-top: 8px;
    width: 100%;
  }
  .invite-btn:hover {
    color: #9b7a25;
    border-color: #dfc876;
    background: #fbf7ec;
  }

  .card-widget {
    background: linear-gradient(135deg, #faf8f3, #fbf7ec);
    border: 1px solid #f2e9c8;
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 8px;
  }
  .card-widget__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 3px;
  }
  .card-widget__bank {
    font-size: 11px;
    font-weight: 700;
    color: #9b7a25;
    letter-spacing: 0.5px;
  }
  .card-widget__dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #2a6b2a;
    box-shadow: 0 0 0 2px #eef7ee;
  }
  .card-widget__pan {
    font-size: 12px;
    color: #6b6860;
    margin-bottom: 4px;
    font-family: 'DM Mono', 'Courier New', monospace;
  }
  .card-widget__balance {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 17px;
    font-weight: 600;
    color: #0d0c0a;
  }

  .connect-card-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 36px;
    border: 1.5px solid #d6d3ce;
    border-radius: 8px;
    background: #fff;
    color: #6b6860;
    font-size: 13px;
    font-weight: 500;
    font-family: 'DM Sans', system-ui, sans-serif;
    cursor: pointer;
    transition: all 0.18s;
    margin-top: 4px;
  }
  .connect-card-btn:hover {
    border-color: #b8973a;
    color: #9b7a25;
    background: #fbf7ec;
  }

  /* ── Feed main ── */
  .feed-main {
    flex: 1;
    padding: 24px 28px;
    overflow-y: auto;
    background: #faf8f3;
  }
  .feed-main__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 16px;
  }
  .feed-main__title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 26px;
    font-weight: 600;
    letter-spacing: -0.3px;
    color: #0d0c0a;
    margin: 0;
  }
  .feed-filters {
    display: flex;
    gap: 4px;
    background: #fff;
    border: 1px solid #eae8e4;
    border-radius: 9999px;
    padding: 4px;
  }
  .feed-filter-chip {
    padding: 5px 16px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 500;
    color: #6b6860;
    border: none;
    background: none;
    font-family: 'DM Sans', system-ui, sans-serif;
    cursor: pointer;
    transition: all 0.18s;
  }
  .feed-filter-chip:hover {
    background: #fbf7ec;
  }
  .feed-filter-chip--active {
    background: #0d0c0a;
    color: #fff;
  }

  .live-badge {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    margin-bottom: 18px;
    background: #eef7ee;
    border: 1px solid #8bc88b;
    border-radius: 9999px;
    padding: 4px 12px;
  }
  .live-badge__dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: #2a6b2a;
    animation: pulse 2s ease infinite;
  }
  @keyframes pulse {
    0%,
    100% {
      box-shadow: 0 0 0 3px rgba(42, 107, 42, 0.15);
    }
    50% {
      box-shadow: 0 0 0 6px rgba(42, 107, 42, 0.05);
    }
  }
  .live-badge__text {
    font-size: 10px;
    font-weight: 600;
    color: #2a6b2a;
    letter-spacing: 0.5px;
  }

  .tx-card {
    background: #fff;
    border: 1px solid #eae8e4;
    border-radius: 12px;
    padding: 16px 18px;
    margin-bottom: 10px;
    display: flex;
    align-items: flex-start;
    gap: 14px;
    box-shadow: 0 1px 2px rgba(13, 12, 10, 0.06);
    transition:
      box-shadow 0.18s,
      transform 0.18s;
  }
  .tx-card:hover {
    box-shadow: 0 2px 8px rgba(13, 12, 10, 0.08);
    transform: translateY(-1px);
  }
  .tx-card--secret {
    border-style: dashed;
    border-color: #d6d3ce;
    opacity: 0.55;
    background: #f4f1e9;
  }
  .tx-card--secret:hover {
    transform: none;
  }
  .tx-card__body {
    flex: 1;
  }
  .tx-card__header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
  }
  .tx-card__name {
    font-size: 13px;
    font-weight: 600;
    color: #0d0c0a;
    margin-bottom: 4px;
  }
  .tx-card__name--muted {
    color: #b0ada7;
  }
  .tx-card__note {
    font-size: 11px;
    color: #b0ada7;
    margin-top: 4px;
  }
  .tx-card__category {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 2px 10px;
    border-radius: 9999px;
    background: #fbf7ec;
    border: 1px solid #f2e9c8;
    font-size: 11px;
    font-weight: 500;
    color: #9b7a25;
    margin-bottom: 3px;
  }
  .tx-card__desc {
    font-size: 12px;
    color: #6b6860;
    margin-bottom: 2px;
  }
  .tx-card__date {
    font-size: 11px;
    color: #b0ada7;
    font-family: 'DM Mono', 'Courier New', monospace;
  }
  .tx-card__amount {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 18px;
    font-weight: 600;
    color: #0d0c0a;
    text-align: right;
    white-space: nowrap;
  }
  .tx-card__amount--muted {
    color: #b0ada7;
  }
  .tx-card__currency {
    font-size: 12px;
    font-weight: 400;
    color: #b0ada7;
    margin-left: 2px;
  }
  .tx-card__reactions {
    display: flex;
    align-items: center;
    gap: 6px;
    margin-top: 10px;
    flex-wrap: wrap;
  }
  .reaction-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 4px 10px;
    border-radius: 9999px;
    background: #f4f1e9;
    border: 1px solid #eae8e4;
    font-size: 12px;
    cursor: pointer;
    transition: all 0.18s;
    font-family: 'DM Sans', system-ui, sans-serif;
  }
  /* Hover на emoji реакціях */
  .reaction-pill:hover {
    background: #fbf7ec;
    border-color: #f2e9c8;
  }
  .reaction-add {
    padding: 4px 10px;
    border-radius: 9999px;
    border: 1px dashed #d6d3ce;
    font-size: 11px;
    color: #b0ada7;
    background: none;
    font-family: 'DM Sans', system-ui, sans-serif;
    cursor: pointer;
    transition: all 0.18s;
  }
  .reaction-add:hover {
    color: #9b7a25;
    border-color: #dfc876;
    background: #fbf7ec;
  }
  .feed-empty {
    text-align: center;
    padding: 60px 20px;
    color: #b0ada7;
    font-size: 14px;
  }

  .skeleton {
    background: linear-gradient(90deg, #ede9de 25%, #f4f1e9 50%, #ede9de 75%);
    background-size: 200% 100%;
    animation: shimmer 1.6s ease infinite;
    border-radius: 4px;
  }
  .skeleton--circle {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    flex-shrink: 0;
  }
  .skeleton--line {
    height: 12px;
    margin-bottom: 8px;
  }
  @keyframes shimmer {
    0% {
      background-position: 200% 0;
    }
    100% {
      background-position: -200% 0;
    }
  }

  /* ── Right panel ── */
  .right-panel {
    width: 280px;
    background: #fff;
    border-left: 1px solid #eae8e4;
    padding: 20px 18px;
    overflow-y: auto;
    flex-shrink: 0;
  }
  .right-panel__section {
    margin-bottom: 24px;
  }
  .right-panel__title {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #b0ada7;
    margin-bottom: 12px;
  }
  .donut-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
  }
  .donut-legend {
    width: 100%;
    margin-top: 10px;
  }
  .donut-legend__row {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 3px 0;
  }
  .donut-legend__dot {
    width: 10px;
    height: 10px;
    border-radius: 2px;
    flex-shrink: 0;
  }
  .donut-legend__label {
    font-size: 12px;
    color: #6b6860;
    flex: 1;
  }
  .donut-legend__pct {
    font-size: 12px;
    font-weight: 600;
    color: #0d0c0a;
  }
  .donut-legend__note {
    font-size: 9px;
    color: #b0ada7;
    margin-top: 6px;
    font-style: italic;
  }

  .gift-card {
    background: linear-gradient(135deg, #fbf7ec, #f4f1e9);
    border: 1px solid #f2e9c8;
    border-radius: 12px;
    padding: 14px;
    margin-bottom: 10px;
  }
  .gift-card__title {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 15px;
    font-weight: 600;
    color: #0d0c0a;
    margin-bottom: 4px;
  }
  .gift-card__meta {
    font-size: 12px;
    color: #6b6860;
    line-height: 1.8;
    margin-bottom: 8px;
  }
  .progress-bar {
    height: 4px;
    background: #eae8e4;
    border-radius: 9999px;
    overflow: hidden;
    margin-bottom: 10px;
  }
  .progress-bar__fill {
    height: 100%;
    background: linear-gradient(90deg, #b8973a, #d4b558);
    border-radius: 9999px;
  }
  .btn-view-event {
    width: 100%;
    height: 34px;
    background: #fff;
    border: 1.5px solid #dfc876;
    border-radius: 8px;
    color: #9b7a25;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.18s;
    font-family: 'DM Sans', system-ui, sans-serif;
  }
  .btn-view-event:hover {
    background: #fbf7ec;
  }

  .notif-item {
    padding: 10px 12px;
    border-radius: 8px;
    background: #f4f1e9;
    border: 1px solid #eae8e4;
    margin-bottom: 8px;
  }
  .notif-item--unread {
    border-left: 3px solid #b8973a;
  }
  .notif-item__title {
    font-size: 12px;
    font-weight: 600;
    color: #0d0c0a;
    margin-bottom: 3px;
  }
  .notif-item__sub {
    font-size: 11px;
    color: #b0ada7;
  }

  /* ── Shared ── */
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
    width: 40px;
    height: 40px;
    font-size: 14px;
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
  .toast--info {
    background: #eef3fb;
    color: #2a4e8b;
    border: 1px solid #8aaad4;
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

  .tx-list-enter-active {
    transition: all 0.3s ease;
  }
  .tx-list-enter-from {
    opacity: 0;
    transform: translateY(-12px);
  }
</style>
