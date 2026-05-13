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
          <button class="navbar__group-tab navbar__group-tab--add" @click="goToGroupSetup">
            + New group
          </button>
        </div>
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
        <div class="avatar avatar--sm avatar--gold">{{ currentUserInitials }}</div>
        <span class="navbar__user-name">{{ currentUserName }}</span>
        <span v-if="isAdmin" class="badge badge--admin">Admin</span>
        <span v-else class="badge badge--member">Member</span>

        <button class="logout-btn" :disabled="isLoading" @click="handleLogout" aria-label="Logout">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <path
              d="M6 14H3.5C2.67 14 2 13.33 2 12.5V3.5C2 2.67 2.67 2 3.5 2H6"
              stroke="currentColor"
              stroke-width="1.5"
              stroke-linecap="round"
            />
            <path
              d="M11 11L14 8L11 5M14 8H6"
              stroke="currentColor"
              stroke-width="1.5"
              stroke-linecap="round"
              stroke-linejoin="round"
            />
          </svg>
        </button>
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
          <InviteMemberModal
            :is-open="isInviteModalOpen"
            @close="isInviteModalOpen = false"
            @toast="showToast($event.message, $event.type)"
          />
        </section>

        <section class="sidebar__section">
          <div class="sidebar__section-title">Connected Cards</div>

          <template v-if="isLoadingCards">
            <div class="card-widget-skeleton"></div>
          </template>

          <template v-else>
            <div v-for="card in connectedCards" :key="card.id" class="card-widget">
              <div class="card-widget__header">
                <span class="card-widget__bank">Monobank</span>
                <span
                  class="card-widget__dot"
                  :class="{ 'card-widget__dot--inactive': card.status === 'INACTIVE' }"
                ></span>
              </div>
              <div class="card-widget__pan">{{ card.masked_pan }}</div>
            </div>
            <button class="connect-card-btn" @click="isConnectCardOpen = true">
              + Connect Card
            </button>
          </template>
        </section>
      </aside>

      <!-- FEED MAIN -->
      <main class="feed-main">
        <div class="feed-main__header">
          <div class="feed-main__title-row">
            <h1 class="feed-main__title">Family Feed</h1>
            <ConnectionIndicator :is-connected="wsConnected" />
          </div>
          <div class="feed-filters" v-if="memberFilters.length > 1">
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

        <!-- Skeleton під час initial load (PROJ-52 FE-03) -->
        <FeedSkeleton v-if="isLoadingFeed" :count="5" />

        <!-- Empty state (PROJ-52 FE-02) -->
        <EmptyFeed
          v-else-if="!filteredTransactions.length"
          @connect-card="isConnectCardOpen = true"
        />

        <!-- Транзакції з infinite scroll (PROJ-52 FE-01) -->
        <template v-else>
          <TransitionGroup name="tx-list" tag="div" class="tx-list-wrap">
            <TransactionCard v-for="tx in filteredTransactions" :key="tx.id" :transaction="tx" />
          </TransitionGroup>

          <!-- Sentinel для infinite scroll через Intersection Observer -->
          <div ref="sentinelRef" class="feed-sentinel">
            <div v-if="isLoadingMore" class="feed-sentinel__loader">
              <svg class="spinner" width="20" height="20" viewBox="0 0 20 20" fill="none">
                <circle cx="10" cy="10" r="8" stroke="rgba(184,151,58,0.3)" stroke-width="2" />
                <path
                  d="M10 2A8 8 0 0 1 18 10"
                  stroke="#b8973a"
                  stroke-width="2"
                  stroke-linecap="round"
                />
              </svg>
              Loading more...
            </div>
            <div v-else-if="!hasMore && filteredTransactions.length > 0" class="feed-sentinel__end">
              You've reached the end
            </div>
          </div>
        </template>
      </main>

      <!-- RIGHT PANEL (TODO: підключити до реальних endpoints коли з'являться) -->
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

    <!-- Modals -->
    <ConnectCardModal
      :is-open="isConnectCardOpen"
      @close="isConnectCardOpen = false"
      @toast="showToast($event.message, $event.type)"
      @connected="handleCardConnected"
    />

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
  import { useFeedTransactions } from '../composables/useFeedTransactions'
  import { useInfiniteScroll } from '../composables/useInfiniteScroll'
  import { useWebSocket } from '../composables/useWebSocket'
  import { fetchGroupMembers } from '../services/authService'
  import { fetchGroupCards } from '../services/cardService'

  import InviteMemberModal from '../components/InviteMemberModal.vue'
  import ConnectCardModal from '../components/ConnectCardModal.vue'
  import TransactionCard from '../components/TransactionCard.vue'
  import FeedSkeleton from '../components/FeedSkeleton.vue'
  import EmptyFeed from '../components/EmptyFeed.vue'
  import UserAvatar from '../components/UserAvatar.vue'
  import ConnectionIndicator from '../components/ConnectionIndicator.vue'

  const router = useRouter()
  const { currentUser, isAdmin, isLoading, logout } = useAuth()

  // ─── Navbar user info ───
  const currentUserName = computed(() => currentUser.value?.fullName || '')
  const currentUserInitials = computed(() => {
    const name = currentUser.value?.fullName || '?'
    if (!name) return '?'
    return name
      .split(' ')
      .map((w) => w[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)
  })

  async function handleLogout() {
    await logout()
  }

  // ─── Groups (поки тільки активна група, перемикання — окрема таска) ───
  const groups = computed(() => [{ id: 1, name: currentUser.value?.groupName || 'Family' }])
  const activeGroupId = ref(1)

  function goToGroupSetup() {
    router.push('/group-setup')
  }

  // ─── Modals ───
  const isInviteModalOpen = ref(false)
  const isConnectCardOpen = ref(false)

  // ─── Group Members (sidebar) ───
  const groupMembers = ref([])
  const isLoadingMembers = ref(false)

  function mapMemberFromApi(apiMember, currentUserEmail) {
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
      role: apiMember.role,
      avatarVariant: variants[variantIdx],
      isCurrentUser: apiMember.email === currentUserEmail,
    }
  }

  async function loadGroupMembers() {
    if (!currentUser.value?.groupId) return
    isLoadingMembers.value = true
    try {
      const data = await fetchGroupMembers(currentUser.value.groupId)
      const members = Array.isArray(data) ? data : data.members || []
      groupMembers.value = members.map((m) => mapMemberFromApi(m, currentUser.value?.email))
    } catch (err) {
      // 404 — endpoint поки не реалізований, не показуємо toast
      if (err.response?.status !== 404) {
        showToast('Failed to load group members', 'error')
      }
    } finally {
      isLoadingMembers.value = false
    }
  }

  function openMoneyRequestModal(member) {
    showToast(`Opening request to ${member.name}`, 'info')
  }

  // ─── Cards (sidebar) ───
  const connectedCards = ref([])
  const isLoadingCards = ref(false)

  async function loadCards() {
    if (!currentUser.value?.groupId) return
    isLoadingCards.value = true
    try {
      connectedCards.value = await fetchGroupCards(currentUser.value.groupId)
    } catch (err) {
      console.warn('Failed to load cards:', err)
    } finally {
      isLoadingCards.value = false
    }
  }

  async function handleCardConnected() {
    await loadCards()
    showToast('Card connected successfully', 'success')
  }

  // ─── Transactions feed (PROJ-52) ───
  const {
    transactions,
    isLoading: isLoadingFeed,
    isLoadingMore,
    hasMore,
    loadFirstPage,
    loadMore,
    prependTransaction,
  } = useFeedTransactions(currentUser.value?.groupId)

  const activeFilter = ref('all')

  /**
   * Фільтри з авторів транзакцій + GroupMembers (якщо endpoint доступний).
   * Об'єднуємо обидва джерела щоб filter працював і коли endpoint /members 404.
   */
  const memberFilters = computed(() => {
    const uniqueAuthors = new Map()

    // 1. Автори з самих транзакцій (PROJ-53 поля)
    transactions.value.forEach((tx) => {
      if (tx.author_id && !uniqueAuthors.has(tx.author_id)) {
        uniqueAuthors.set(tx.author_id, {
          value: tx.author_id,
          label: (tx.author_full_name || tx.author_email || 'User').split(' ')[0],
        })
      }
    })

    // 2. Доповнюємо учасниками з /members endpoint (якщо вантажились)
    groupMembers.value.forEach((m) => {
      if (m.id && !uniqueAuthors.has(m.id)) {
        uniqueAuthors.set(m.id, {
          value: m.id,
          label: m.name.split(' ')[0],
        })
      }
    })

    return [{ value: 'all', label: 'All' }, ...uniqueAuthors.values()]
  })

  const filteredTransactions = computed(() => {
    if (activeFilter.value === 'all') return transactions.value
    return transactions.value.filter((tx) => tx.author_id === activeFilter.value)
  })

  // ─── Infinite scroll (PROJ-52 FE-01) ───
  const { sentinelRef } = useInfiniteScroll(() => {
    if (hasMore.value && !isLoadingMore.value) {
      loadMore()
    }
  })

  // ─── WebSocket для real-time (PROJ-50) ───
  const { isConnected: wsConnected } = useWebSocket({
    onTransaction: (tx) => {
      prependTransaction(tx)
    },
  })

  // ─── Right panel (TODO: підключити до реальних endpoints) ───
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

  // ─── Toast ───
  const toast = ref({ isVisible: false, message: '', type: 'success' })

  function showToast(message, type = 'success') {
    toast.value = { isVisible: true, message, type }
    setTimeout(() => {
      toast.value.isVisible = false
    }, 3000)
  }

  // ─── Mount ───
  onMounted(() => {
    loadGroupMembers()
    loadCards()
    loadFirstPage()
  })
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

  .logout-btn {
    width: 32px;
    height: 32px;
    border-radius: 6px;
    border: 1px solid rgba(255, 255, 255, 0.12);
    background: rgba(255, 255, 255, 0.04);
    color: rgba(255, 255, 255, 0.6);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.18s;
    margin-left: 4px;
  }
  .logout-btn:hover:not(:disabled) {
    background: rgba(196, 64, 42, 0.18);
    border-color: rgba(196, 64, 42, 0.4);
    color: #ff8a72;
  }
  .logout-btn:disabled {
    opacity: 0.4;
    cursor: not-allowed;
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
  .card-widget__dot--inactive {
    background: #b0ada7;
    box-shadow: 0 0 0 2px #eae8e4;
  }
  .card-widget__pan {
    font-size: 12px;
    color: #6b6860;
    font-family: 'DM Mono', 'Courier New', monospace;
  }

  .card-widget-skeleton {
    height: 56px;
    background: linear-gradient(90deg, #ede9de 25%, #f4f1e9 50%, #ede9de 75%);
    background-size: 200% 100%;
    animation: shimmer 1.6s ease infinite;
    border-radius: 12px;
    margin-bottom: 8px;
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
    margin-bottom: 18px;
  }

  .feed-main__title-row {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 12px;
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
    width: fit-content;
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

  .tx-list-wrap {
    display: flex;
    flex-direction: column;
  }

  .feed-sentinel {
    padding: 24px 0;
    text-align: center;
  }
  .feed-sentinel__loader {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 12px;
    color: #9b7a25;
  }
  .feed-sentinel__end {
    font-size: 12px;
    color: #b0ada7;
    font-style: italic;
  }

  .spinner {
    animation: spin 0.8s linear infinite;
  }
  @keyframes spin {
    to {
      transform: rotate(360deg);
    }
  }
  @keyframes shimmer {
    0% {
      background-position: 200% 0;
    }
    100% {
      background-position: -200% 0;
    }
  }

  /* ── Right panel (TODO: real endpoints) ── */
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

  /* ── Transitions ── */
  .tx-list-enter-active,
  .tx-list-leave-active {
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
  }
  .tx-list-enter-from {
    opacity: 0;
    transform: translateY(-20px) scale(0.98);
  }
  .tx-list-leave-to {
    opacity: 0;
    transform: translateX(-20px);
  }
  .tx-list-move {
    transition: transform 0.4s ease;
  }
</style>
