<template>
  <div class="feed-page">
    <NavBar :show-logout="true">
      <template #left>
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
      </template>
    </NavBar>

    <div class="feed-layout">
      <aside class="sidebar">
        <section class="sidebar__section">
          <div class="sidebar__section-title">Group Members</div>

          <div v-if="isLoadingMembers && !groupMembers.length" class="sidebar__loading">
            <div v-for="n in 3" :key="n" class="sidebar__skeleton-row"></div>
          </div>

          <div v-else-if="!groupMembers.length" class="sidebar__empty">
            {{ strings.empty.members }}
          </div>

          <div v-else class="sidebar__scroll sidebar__scroll--members">
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
            <div v-if="!connectedCards.length" class="sidebar__empty">
              {{ strings.empty.cards }}
            </div>
            <div v-else class="sidebar__scroll sidebar__scroll--cards">
              <div v-for="card in connectedCards" :key="card.id" class="card-widget">
                <div class="card-widget__header">
                  <span class="card-widget__bank">Monobank</span>
                  <span
                    class="card-widget__dot"
                    :class="{ 'card-widget__dot--inactive': card.status === 'INACTIVE' }"
                  ></span>
                </div>
                <div class="card-widget__pan">{{ card.masked_pan }}</div>
                <div v-if="cardOwnerName(card)" class="card-widget__owner">
                  {{ cardOwnerName(card) }}
                </div>
                <button class="card-widget__details" @click="openCardDetails(card)">Details</button>
              </div>
            </div>
            <button class="connect-card-btn" @click="isConnectCardOpen = true">
              + Connect Card
            </button>
          </template>
        </section>

        <ConnectCardModal
          :is-open="isConnectCardOpen"
          @close="isConnectCardOpen = false"
          @toast="showToast($event.message, $event.type)"
          @connected="handleCardConnected"
        />
      </aside>

      <main class="feed-main">
        <div class="feed-main__header">
          <h1 class="feed-main__title">Family Feed</h1>
          <ConnectionIndicator :is-connected="wsConnected" />
          <div v-if="hasOwnCard && transactions.length > 0" class="feed-filters">
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
        <FeedSkeleton
          v-if="isLoadingCards || (isLoadingFeed && transactions.length === 0)"
          :count="5"
        />

        <EmptyFeed v-else-if="!hasOwnCard" @connect-card="isConnectCardOpen = true" />

        <div v-else-if="transactions.length === 0" class="feed-empty">
          <p>{{ strings.empty.transactions }}</p>
        </div>

        <template v-else>
          <TransitionGroup name="tx-list" tag="div" class="tx-list">
            <TransactionCard v-for="tx in filteredTransactions" :key="tx.id" :transaction="tx" />
          </TransitionGroup>

          <button v-if="hasMore" class="tx-load-more" :disabled="isLoadingMore" @click="loadMore">
            {{ isLoadingMore ? strings.loading.more : strings.common.loadMore }}
          </button>
        </template>
      </main>

      <aside class="right-panel">
        <section v-if="incomingRequests.length" class="right-panel__section">
          <div class="right-panel__title">Money Requests</div>
          <div v-for="req in incomingRequests" :key="req.id" class="req-card">
            <div class="req-card__head">
              <span class="req-card__from">{{ requesterName(req) }}</span>
              <span class="req-card__amount">{{ formatAmount(req.amount) }} UAH</span>
            </div>
            <div v-if="req.description" class="req-card__desc">{{ req.description }}</div>
            <div class="req-card__actions">
              <button
                class="req-btn req-btn--accept"
                :disabled="respondingId === req.id"
                @click="respondRequest(req, 'ACCEPTED')"
              >
                Accept
              </button>
              <button
                class="req-btn req-btn--decline"
                :disabled="respondingId === req.id"
                @click="respondRequest(req, 'DECLINED')"
              >
                Decline
              </button>
            </div>
          </div>
        </section>

        <section class="right-panel__section">
          <div class="right-panel__title">Spending by Category</div>

          <div v-if="hasOwnCard && categoryBreakdown.length" class="donut-wrap">
            <svg width="152" height="152" viewBox="0 0 160 160">
              <circle cx="80" cy="80" r="56" fill="none" stroke="#F0EFED" stroke-width="26" />
              <circle
                v-for="seg in categoryBreakdown"
                :key="seg.name"
                cx="80"
                cy="80"
                r="56"
                fill="none"
                :stroke="seg.color"
                stroke-width="26"
                :stroke-dasharray="seg.dasharray"
                :stroke-dashoffset="seg.offset"
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
                {{ formatAmount(categoryTotal) }}
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

          <div v-else class="right-panel__empty">{{ strings.empty.spending }}</div>
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
          <div class="right-panel__title notif-head">
            <span>Notifications</span>
            <button v-if="unreadNotifCount" class="notif-markread" @click="markNotifsRead">
              Mark all read
            </button>
          </div>
          <div v-if="visibleNotifications.length" class="notif-list">
            <div
              v-for="n in visibleNotifications"
              :key="n.id"
              class="notif-item"
              :class="{ 'notif-item--unread': !n.is_read }"
            >
              <div class="notif-item__title">{{ notifIcon(n) }} {{ notifText(n) }}</div>
              <div class="notif-item__sub">{{ notifTime(n.created_at) }}</div>
            </div>
          </div>
          <div v-else class="right-panel__empty">{{ strings.empty.notifications }}</div>
        </section>
      </aside>
    </div>

    <Transition name="toast">
      <div v-if="toast.isVisible" class="toast" :class="`toast--${toast.type}`" role="alert">
        {{ toast.message }}
      </div>
    </Transition>
  </div>
  <ConnectCardModal
    :is-open="isConnectCardOpen"
    @close="isConnectCardOpen = false"
    @toast="showToast($event.message, $event.type)"
    @connected="handleCardConnected"
  />
  <ConnectCardReminderModal
    :is-open="isReminderOpen"
    @connect-now="handleReminderConnect"
    @later="handleReminderLater"
  />
  <CardDetailsModal
    :is-open="isCardDetailsOpen"
    :card="selectedCardForDetails"
    @close="closeCardDetails"
  />
  <TransferModal
    :is-open="isTransferModalOpen"
    :user-cards="userOwnedActiveCards"
    :group-cards="connectedCards"
    :categories="[]"
    @close="isTransferModalOpen = false"
    @success="handleTransferSuccess"
    @toast="showToast($event.message, $event.type)"
  />
  <MoneyRequestModal
    :is-open="isMoneyRequestOpen"
    :sender-name="currentUser?.fullName || 'You'"
    :recipient="moneyRequestRecipient"
    @close="isMoneyRequestOpen = false"
    @success="onMoneyRequestSent"
    @toast="showToast($event.message, $event.type)"
  />
  <RequestResponseModal
    :is-open="!!responseModal"
    :status="responseModal?.status || 'ACCEPTED'"
    :responder-name="responseModal?.responderName || ''"
    :amount="responseModal?.amount || 0"
    @close="closeResponseModal"
  />
  <SelectCardModal
    :is-open="isSelectCardOpen"
    :cards="userOwnedActiveCards"
    @close="isSelectCardOpen = false"
    @select="onSelectPayCard"
  />
</template>

<script setup>
  import { ref, computed, onMounted, watch, onUnmounted } from 'vue'
  import { useRouter } from 'vue-router'
  import { useAuth } from '../composables/useAuth'
  import { useFeedTransactions } from '../composables/useFeedTransactions'
  import { useWebSocket } from '../composables/useWebSocket'
  import { applyServerReactions, seedReactions } from '../composables/useReactions'
  import { fetchGroupMembers } from '../services/authService'
  import { fetchGroupCards } from '../services/cardService'
  import InviteMemberModal from '../components/InviteMemberModal.vue'
  import ConnectCardModal from '../components/ConnectCardModal.vue'
  import TransactionCard from '../components/TransactionCard.vue'
  import FeedSkeleton from '../components/FeedSkeleton.vue'
  import EmptyFeed from '../components/EmptyFeed.vue'
  import ConnectionIndicator from '../components/ConnectionIndicator.vue'
  import NavBar from '../components/NavBar.vue'

  import ConnectCardReminderModal from '../components/ConnectCardReminderModal.vue'
  import { scheduleLater, dismissForever, getScheduledTime } from '../utils/cardReminder'
  import CardDetailsModal from '../components/CardDetailsModal.vue'
  import TransferModal from '../components/TransferModal.vue'
  import MoneyRequestModal from '../components/MoneyRequestModal.vue'
  import RequestResponseModal from '../components/RequestResponseModal.vue'
  import SelectCardModal from '../components/SelectCardModal.vue'
  import { usePersistentState } from '../composables/usePersistentState'
  import { fetchGroupGiftEvents } from '../services/giftEventService'
  import {
    fetchIncomingRequests,
    fetchOutgoingRequests,
    respondToMoneyRequest,
  } from '../services/moneyRequestService'
  import { fetchNotifications, markNotificationsRead } from '../services/notificationService'
  import { parseServerDate } from '../utils/datetime'
  import { resolveCategory } from '../utils/categoryColors'
  import strings from '../locales/en'

  const router = useRouter()
  const storedUser = JSON.parse(localStorage.getItem('currentUser') || '{}')

  const { currentUser, isAdmin } = useAuth()
  const connectedCards = ref([])
  const isLoadingCards = ref(false)

  async function loadCards() {
    if (!currentUser.value?.groupId) return
    isLoadingCards.value = true
    try {
      connectedCards.value = await fetchGroupCards(currentUser.value.groupId)
    } catch {
      // Не вдалося завантажити картки — залишаємо попередній список
    } finally {
      isLoadingCards.value = false
    }
  }

  async function handleCardConnected() {
    await loadCards()
  }

  const {
    transactions,
    isLoading: isLoadingFeed,
    isLoadingMore,
    hasMore,
    loadFirstPage,
    loadMore,
  } = useFeedTransactions(() => currentUser.value?.groupId)

  const { isConnected: wsConnected } = useWebSocket({
    groupId: () => currentUser.value?.groupId,
    onTransaction: handleWsTransaction,
    onReaction: (data) => {
      if (data?.transaction_id) applyServerReactions(data.transaction_id, data.grouped_reactions)
    },
    onRequest: (data, event) => {
      loadIncomingRequests()

      if (event === 'request_updated' && data?.request_id) {
        handleRequestResolved(data.request_id, data.status)
      }
    },
  })

  watch(
    () => transactions.value.length,
    () => transactions.value.forEach(seedReactions),
    { immediate: true },
  )

  function handleWsTransaction() {
    loadFirstPage()
    showToast('New transaction', 'info')
  }

  const isInviteModalOpen = ref(false)

  const hasOwnCard = computed(() =>
    connectedCards.value.some((c) => String(c.user_id) === String(currentUser.value?.id)),
  )

  const isTransferModalOpen = ref(false)

  const userOwnedActiveCards = computed(() =>
    connectedCards.value.filter(
      (c) => String(c.user_id) === String(currentUser.value?.id) && c.status === 'ACTIVE',
    ),
  )

  async function handleTransferSuccess(_result) {
    isTransferModalOpen.value = false

    await loadCards()
    await loadFirstPage()
  }

  const groups = ref([{ id: 1, name: storedUser.groupName || 'Family' }])

  const activeGroupId = ref(1)

  const groupMembers = ref([])
  const isLoadingMembers = ref(false)

  function mapMemberFromApi(apiMember, currentUserId) {
    const fullName = apiMember.name || 'User'
    const initials = fullName
      .split(' ')
      .map((w) => w[0])
      .join('')
      .toUpperCase()
      .slice(0, 2)

    const variants = ['gold', 'dark', 'light']
    const variantIdx = (initials.charCodeAt(0) || 0) % variants.length

    return {
      id: apiMember.id,
      name: fullName,
      initials,
      role: apiMember.role || 'MEMBER',
      avatarVariant: variants[variantIdx],
      isCurrentUser: apiMember.id === currentUserId,
    }
  }

  async function loadGroupMembers() {
    if (!storedUser.groupId) return

    isLoadingMembers.value = true
    try {
      const data = await fetchGroupMembers(storedUser.groupId)
      const members = Array.isArray(data) ? data : data.members || []
      groupMembers.value = members.map((m) => mapMemberFromApi(m, currentUser.value?.id))
    } catch (err) {
      showToast(err.userMessage || 'Failed to load group members', 'error')
    } finally {
      isLoadingMembers.value = false
    }
  }

  const realGiftEvents = ref([])

  async function loadGiftEvents() {
    if (!currentUser.value?.groupId) return
    try {
      realGiftEvents.value = await fetchGroupGiftEvents(currentUser.value.groupId)
    } catch {
      realGiftEvents.value = []
    }
  }

  const GIFT_FEED_TTL_MS = 24 * 60 * 60 * 1000

  const now = ref(Date.now())
  let nowTimer = null

  function isGiftWithinFeedWindow(g) {
    const unlock = parseServerDate(g.unlock_date)
    if (!unlock) return true // немає дати — не ховаємо
    return now.value < unlock.getTime() + GIFT_FEED_TTL_MS
  }

  const visibleGiftEvents = computed(() => realGiftEvents.value.filter(isGiftWithinFeedWindow))

  function formatPinnedDate(iso) {
    const d = parseServerDate(iso)
    if (!d) return ''
    return d.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
    })
  }

  function formatAmount(amount) {
    return new Intl.NumberFormat('uk-UA').format(Number(amount) || 0)
  }

  onMounted(async () => {
    await loadCards()
    await loadGroupMembers()
    loadFirstPage()
    initCardReminder()
    loadGiftEvents()
    loadIncomingRequests()
    loadOutgoingResolved()
    loadNotifications()

    nowTimer = setInterval(() => {
      now.value = Date.now()
      loadNotifications()
    }, 60000)
  })

  const activeFilter = ref('all')
  const memberFilters = computed(() => {
    const unique = new Map()
    for (const tx of transactions.value) {
      if (tx.author_id && !unique.has(tx.author_id)) {
        unique.set(tx.author_id, tx.display_name?.split(' ')[0] || 'Unknown')
      }
    }
    return [
      { value: 'all', label: 'All' },
      ...Array.from(unique, ([value, label]) => ({ value, label })),
    ]
  })

  const filteredTransactions = computed(() => {
    const list =
      activeFilter.value === 'all'
        ? transactions.value
        : transactions.value.filter((tx) => tx.author_id === activeFilter.value)

    return [...list].sort((a, b) => {
      const ta = parseServerDate(a.timestamp)?.getTime() ?? 0
      const tb = parseServerDate(b.timestamp)?.getTime() ?? 0
      return tb - ta
    })
  })

  const DONUT_CIRCUMFERENCE = 351.86
  const categoryBreakdown = computed(() => {
    const totals = new Map() // label → { value, color }
    for (const tx of transactions.value) {
      const amt = Number(tx.amount)
      if (!amt || amt >= 0) continue
      const { label, color } = resolveCategory(tx)
      const prev = totals.get(label) || { value: 0, color }
      prev.value += Math.abs(amt)
      totals.set(label, prev)
    }
    const grand = [...totals.values()].reduce((s, v) => s + v.value, 0)
    if (!grand) return []

    let offset = 0
    return [...totals.entries()]
      .sort((a, b) => b[1].value - a[1].value)
      .map(([name, { value, color }]) => {
        const fraction = value / grand
        const dash = fraction * DONUT_CIRCUMFERENCE
        const seg = {
          name,
          value,
          pct: Math.round(fraction * 100),
          color,
          dasharray: `${dash.toFixed(2)} ${DONUT_CIRCUMFERENCE.toFixed(2)}`,
          offset: -Number(offset.toFixed(2)),
        }
        offset += dash
        return seg
      })
  })

  const categoryTotal = computed(() => categoryBreakdown.value.reduce((s, c) => s + c.value, 0))

  const activeGiftEvents = computed(() =>
    visibleGiftEvents.value
      .filter((g) => g.status === 'ACTIVE' || g.status === 'REVEALED')
      .map((g) => {
        const collected = Number(g.collected_amount) || 0
        const goal = Number(g.goal_amount) || 0
        return {
          id: g.id,
          name: g.name,
          targetUser: g.target_user_name,
          unlockDate: formatPinnedDate(g.unlock_date),
          collected: formatAmount(collected),
          goal: formatAmount(goal),
          progressPct: goal ? Math.min(100, Math.round((collected / goal) * 100)) : 0,
        }
      }),
  )

  const toast = ref({ isVisible: false, message: '', type: 'success' })

  /**
   * @param {string} message
   * @param {'success'|'error'|'info'} type
   */
  function showToast(message, type = 'success') {
    toast.value = { isVisible: true, message, type }
    setTimeout(() => {
      toast.value.isVisible = false
    }, 4000)
  }

  const isMoneyRequestOpen = ref(false)
  const moneyRequestRecipient = ref(null)

  function openMoneyRequestModal(member) {
    moneyRequestRecipient.value = member
    isMoneyRequestOpen.value = true
  }

  const reqStorageUid = currentUser.value?.id || 'anon'

  const outgoingRequests = usePersistentState(`fw:outgoingRequests:${reqStorageUid}`, {})

  function onMoneyRequestSent(payload) {
    if (!payload?.request_id) return
    outgoingRequests.value = {
      ...outgoingRequests.value,
      [payload.request_id]: {
        recipientName: payload.recipientName,
        amount: payload.amount,
      },
    }
  }

  const acknowledgedRequests = usePersistentState(`fw:ackRequests:v2:${reqStorageUid}`, [])

  const responseQueue = ref([])
  const responseModal = computed(() => responseQueue.value[0] || null)

  function isAcked(id) {
    return acknowledgedRequests.value.includes(id)
  }

  function enqueueResponse(id, status, responderName, amount) {
    if (!id || isAcked(id)) return
    if (responseQueue.value.some((x) => x.id === id)) return
    responseQueue.value = [
      ...responseQueue.value,
      { id, status: status || 'ACCEPTED', responderName, amount },
    ]
  }

  function closeResponseModal() {
    const current = responseQueue.value[0]
    if (current && !acknowledgedRequests.value.includes(current.id)) {
      acknowledgedRequests.value = [...acknowledgedRequests.value, current.id]
    }
    responseQueue.value = responseQueue.value.slice(1)
  }

  function handleRequestResolved(requestId, status) {
    const out = outgoingRequests.value[requestId]
    if (!out) return
    enqueueResponse(requestId, status, out.recipientName || 'A group member', out.amount)
    const next = { ...outgoingRequests.value }
    delete next[requestId]
    outgoingRequests.value = next
  }

  async function loadOutgoingResolved() {
    if (!currentUser.value?.id) return
    try {
      const data = await fetchOutgoingRequests()
      for (const r of Array.isArray(data) ? data : []) {
        const id = r.id || r._id
        if ((r.status === 'ACCEPTED' || r.status === 'DECLINED') && !isAcked(id)) {
          const name =
            groupMembers.value.find((m) => String(m.id) === String(r.recipient_id))?.name ||
            'A group member'
          enqueueResponse(id, r.status, name, Number(r.amount))
        }
      }
    } catch {
      // Не вдалося завантажити вихідні запити
    }
  }

  const notifications = ref([])

  const NOTIF_FEED_TTL_MS = 48 * 60 * 60 * 1000
  const visibleNotifications = computed(() =>
    notifications.value.filter((n) => {
      const created = parseServerDate(n.created_at)
      if (!created) return true
      return now.value < created.getTime() + NOTIF_FEED_TTL_MS
    }),
  )
  const unreadNotifCount = computed(
    () => visibleNotifications.value.filter((n) => !n.is_read).length,
  )

  async function loadNotifications() {
    if (!currentUser.value?.id) return
    try {
      const data = await fetchNotifications()
      notifications.value = (Array.isArray(data) ? data : []).map((n) => ({
        ...n,
        id: n.id || n._id,
      }))
    } catch {
      // Не вдалося завантажити сповіщення
    }
  }

  async function markNotifsRead() {
    try {
      await markNotificationsRead()
      notifications.value = notifications.value.map((n) => ({ ...n, is_read: true }))
    } catch {
      showToast('Failed to mark notifications as read', 'error')
    }
  }

  const NOTIF_TEXT = {
    REVEAL: 'A secret gift was revealed!',
    REMINDER_24H: 'A gift unlocks in 24 hours',
    REMINDER_DAY_OF: 'A gift unlocks today',
    REMINDER_9AM: 'Gift unlock reminder',
  }
  const NOTIF_ICON = {
    REVEAL: '🎉',
    REMINDER_24H: '⏰',
    REMINDER_DAY_OF: '🎈',
    REMINDER_9AM: '🔔',
  }
  const notifText = (n) => NOTIF_TEXT[n.notification_type] || 'New notification'
  const notifIcon = (n) => NOTIF_ICON[n.notification_type] || '🔔'
  function notifTime(iso) {
    const d = parseServerDate(iso)
    if (!d) return ''
    return d.toLocaleString('uk-UA', {
      day: 'numeric',
      month: 'short',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  const incomingRequests = ref([])
  const respondingId = ref(null)

  async function loadIncomingRequests() {
    if (!currentUser.value?.id) return
    try {
      const data = await fetchIncomingRequests('PENDING')
      incomingRequests.value = (Array.isArray(data) ? data : []).map((r) => ({
        ...r,
        id: r.id || r._id,
      }))
    } catch {
      // Не вдалося завантажити вхідні запити
    }
  }

  function requesterName(req) {
    const m = groupMembers.value.find((x) => String(x.id) === String(req.requester_id))
    return m?.name || 'Учасник групи'
  }

  const isSelectCardOpen = ref(false)
  const pendingAcceptReq = ref(null)

  async function respondRequest(req, status) {
    if (respondingId.value) return

    if (status !== 'ACCEPTED') {
      return doRespond(req, 'DECLINED', null)
    }

    const cards = userOwnedActiveCards.value
    if (cards.length === 0) {
      showToast(
        "You haven't connected a card to this group. Connect your card first to accept money requests.",
        'error',
      )
      return
    }
    if (cards.length === 1) {
      return doRespond(req, 'ACCEPTED', cards[0].id)
    }
    pendingAcceptReq.value = req
    isSelectCardOpen.value = true
  }

  function onSelectPayCard(cardId) {
    isSelectCardOpen.value = false
    const req = pendingAcceptReq.value
    pendingAcceptReq.value = null
    if (req && cardId) doRespond(req, 'ACCEPTED', cardId)
  }

  async function doRespond(req, status, fromCardId) {
    if (respondingId.value) return
    respondingId.value = req.id
    try {
      await respondToMoneyRequest(req.id, status, fromCardId)
      incomingRequests.value = incomingRequests.value.filter((r) => r.id !== req.id)
      if (status === 'ACCEPTED') {
        showToast(`Request accepted — ${formatAmount(req.amount)} UAH sent`, 'success')
        await loadCards()
        await loadFirstPage()
      } else {
        showToast('Request declined', 'info')
      }
    } catch (err) {
      const httpStatus = err.response?.status
      const detail = err.response?.data?.detail
      let message
      if (httpStatus === 400 && typeof detail === 'string' && detail.includes('картк')) {
        message = (typeof detail === 'string' && detail) || 'Card issue: please check your cards.'
      } else if (httpStatus === 409) {
        message = 'This request has already been resolved.'
        incomingRequests.value = incomingRequests.value.filter((r) => r.id !== req.id)
      } else {
        message =
          (typeof detail === 'string' && detail) || err.userMessage || 'Failed to process request'
      }
      showToast(message, 'error')
    } finally {
      respondingId.value = null
    }
  }

  /**
   * @param {number} amount
   * @returns {string}
   */

  function goToGroupSetup() {
    router.push('/group-setup')
  }

  const isConnectCardOpen = ref(false)

  const isCardDetailsOpen = ref(false)
  const selectedCardForDetails = ref(null)

  function openCardDetails(card) {
    selectedCardForDetails.value = card
    isCardDetailsOpen.value = true
  }

  function closeCardDetails() {
    isCardDetailsOpen.value = false
    selectedCardForDetails.value = null
  }

  const isReminderOpen = ref(false)
  let reminderTimer = null

  function initCardReminder() {
    if (hasOwnCard.value) {
      dismissForever()
      return
    }

    const scheduledAt = getScheduledTime()
    if (!scheduledAt) return

    const remaining = scheduledAt - Date.now()

    if (remaining <= 0) {
      isReminderOpen.value = true
      return
    }

    reminderTimer = setTimeout(() => {
      reminderTimer = null
      if (!hasOwnCard.value) {
        isReminderOpen.value = true
      }
    }, remaining)
  }

  function handleReminderConnect() {
    isReminderOpen.value = false
    isConnectCardOpen.value = true
  }

  function handleReminderLater() {
    isReminderOpen.value = false
    scheduleLater()
    initCardReminder()
  }

  watch(hasOwnCard, (has) => {
    if (has) {
      isReminderOpen.value = false
      if (reminderTimer) {
        clearTimeout(reminderTimer)
        reminderTimer = null
      }
      dismissForever()
    }
  })

  onUnmounted(() => {
    if (reminderTimer) clearTimeout(reminderTimer)
    if (nowTimer) clearInterval(nowTimer)
  })

  function cardOwnerName(card) {
    return card.owner_full_name || null
  }
</script>

<style scoped>
  .feed-page {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    background: #faf8f3;
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

  .feed-layout {
    display: flex;
    flex: 1;
    height: calc(100vh - 60px);
    overflow: hidden;
  }

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

  .sidebar__scroll {
    overflow-y: auto;
    overscroll-behavior: contain;

    scrollbar-width: thin;
    scrollbar-color: #dfc876 transparent;

    padding-right: 4px;
  }

  .sidebar__scroll--members {
    max-height: 232px;
  }

  .sidebar__scroll--cards {
    max-height: 270px;
  }

  .sidebar__scroll::-webkit-scrollbar {
    width: 6px;
  }
  .sidebar__scroll::-webkit-scrollbar-track {
    background: transparent;
  }
  .sidebar__scroll::-webkit-scrollbar-thumb {
    background: #e7dcb4;
    border-radius: 9999px;
  }
  .sidebar__scroll:hover::-webkit-scrollbar-thumb {
    background: #dfc876;
  }

  .sidebar__empty {
    padding: 14px 10px;
    border: 1px dashed #e2ddd2;
    border-radius: 8px;
    font-size: 12px;
    line-height: 1.5;
    color: #b0ada7;
    text-align: center;
  }
  .sidebar__loading {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .sidebar__skeleton-row {
    height: 34px;
    border-radius: 8px;
    background: linear-gradient(90deg, #ede9de 25%, #f4f1e9 50%, #ede9de 75%);
    background-size: 200% 100%;
    animation: shimmer 1.6s ease infinite;
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

  .transfer-btn {
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
    margin-top: 6px;
  }
  .transfer-btn:hover:not(:disabled) {
    border-color: #b8973a;
    color: #9b7a25;
    background: #fbf7ec;
  }
  .transfer-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }

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
    border: 1px solid transparent;
    background: none;
    font-family: 'DM Sans', system-ui, sans-serif;
    cursor: pointer;
    transition: all 0.18s;
  }

  .feed-filter-chip:hover:not(.feed-filter-chip--active) {
    background: #fbf7ec;
    border-color: #f2e9c8;
    color: #9b7a25;
  }

  .feed-filter-chip--active {
    background: linear-gradient(135deg, #b8973a, #c9a84c);
    color: #fff;
    font-weight: 600;
    border-color: transparent;
    box-shadow: 0 2px 8px rgba(184, 151, 58, 0.25);
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
  .right-panel__empty {
    padding: 16px 14px;
    background: #faf8f3;
    border: 1px dashed #e2ddd2;
    border-radius: 10px;
    font-size: 12px;
    line-height: 1.5;
    color: #b0ada7;
    text-align: center;
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

  .req-card {
    background: #fff;
    border: 1px solid #f2e9c8;
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 10px;
    box-shadow: 0 1px 2px rgba(13, 12, 10, 0.05);
  }
  .req-card__head {
    display: flex;
    align-items: baseline;
    justify-content: space-between;
    gap: 8px;
  }
  .req-card__from {
    font-size: 13px;
    font-weight: 600;
    color: #0d0c0a;
  }
  .req-card__amount {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 15px;
    font-weight: 600;
    color: #9b7a25;
    white-space: nowrap;
  }
  .req-card__desc {
    font-size: 12px;
    color: #6b6860;
    margin-top: 4px;
    line-height: 1.5;
  }
  .req-card__actions {
    display: flex;
    gap: 8px;
    margin-top: 10px;
  }
  .req-btn {
    flex: 1;
    height: 32px;
    border-radius: 7px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.18s;
    font-family: 'DM Sans', system-ui, sans-serif;
  }
  .req-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  .req-btn--accept {
    background: linear-gradient(135deg, #b8973a, #c9a84c);
    color: #fff;
    border: none;
    box-shadow: 0 2px 8px rgba(184, 151, 58, 0.22);
  }
  .req-btn--accept:hover:not(:disabled) {
    background: linear-gradient(135deg, #9b7a25, #b8973a);
  }
  .req-btn--decline {
    background: #fff;
    color: #6b6860;
    border: 1.5px solid #e2ddd2;
  }
  .req-btn--decline:hover:not(:disabled) {
    background: #f4f1e9;
    border-color: #d6d3ce;
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

  .notif-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .notif-markread {
    font-size: 9px;
    font-weight: 600;
    letter-spacing: 0.2px;
    text-transform: none;
    color: #9b7a25;
    background: none;
    border: none;
    cursor: pointer;
    padding: 0;
    font-family: 'DM Sans', system-ui, sans-serif;
  }
  .notif-markread:hover {
    color: #b8973a;
    text-decoration: underline;
  }
  .notif-item {
    padding: 10px 12px;
    border-radius: 8px;
    background: #f4f1e9;
    border: 1px solid #eae8e4;
    margin-bottom: 8px;
  }
  .notif-item--unread {
    background: #fbf7ec;
    border-color: #f2e9c8;
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
  .tx-load-more {
    display: block;
    width: 100%;
    margin-top: 4px;
    padding: 12px;
    background: #fff;
    border: 1px solid #e7dcb4;
    border-radius: 10px;
    font-family: 'DM Sans', system-ui, sans-serif;
    font-size: 13px;
    font-weight: 600;
    color: #9b7a25;
    cursor: pointer;
    transition: all 0.18s;
  }
  .tx-load-more:hover:not(:disabled) {
    background: #fbf7ec;
    border-color: #dfc876;
  }
  .tx-load-more:disabled {
    opacity: 0.6;
    cursor: default;
  }
  .card-widget__owner {
    font-size: 11px;
    color: #6b6860;
    margin-top: 4px;
    letter-spacing: 0.2px;
  }

  .card-widget__details {
    width: 100%;
    margin-top: 10px;
    padding: 6px 10px;
    background: transparent;
    color: #9b7a25;
    border: 1px solid #dfc876;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.18s;
    font-family: 'DM Sans', system-ui, sans-serif;
  }
  .card-widget__details:hover {
    background: #fbf7ec;
    border-color: #b8973a;
    color: #9b7a25;
  }

  @media (max-width: 768px) {
    .feed-page {
      min-height: auto;
      height: auto;
      overflow: visible;
    }
    .feed-layout {
      flex: none;
      flex-direction: column;
      height: auto;
      overflow: visible;
    }
    .sidebar,
    .right-panel,
    .feed-main {
      width: 100%;
      flex: none;
    }

    .right-panel {
      order: 1;
      border-left: none;
      border-bottom: 1px solid #eae8e4;
      padding: 16px 16px 8px;
    }
    .feed-main {
      order: 2;
      padding: 16px;
    }
    .sidebar {
      order: 3;
      border-right: none;
      border-top: 1px solid #eae8e4;
      gap: 18px;
    }

    .sidebar__scroll--members {
      max-height: 152px;
    }
    .sidebar__scroll--cards {
      max-height: 232px;
    }

    .tx-list {
      max-height: 384px;
      overflow-y: auto;
      overscroll-behavior: contain;
      scrollbar-width: thin;
      scrollbar-color: #dfc876 transparent;
      padding-right: 4px;
    }
    .tx-list::-webkit-scrollbar {
      width: 6px;
    }
    .tx-list::-webkit-scrollbar-track {
      background: transparent;
    }
    .tx-list::-webkit-scrollbar-thumb {
      background: #e7dcb4;
      border-radius: 9999px;
    }
    .tx-list:hover::-webkit-scrollbar-thumb {
      background: #dfc876;
    }
    .right-panel__section {
      margin-bottom: 18px;
    }
    .feed-main__header {
      flex-wrap: wrap;
      gap: 10px;
    }
    .feed-filters {
      width: 100%;
      overflow-x: auto;
      -webkit-overflow-scrolling: touch;
      scrollbar-width: none;
    }
    .feed-filters::-webkit-scrollbar {
      display: none;
    }
    .navbar__groups {
      display: none;
    }
  }

  @media (max-width: 480px) {
    .feed-main {
      padding: 14px 12px;
    }
    .right-panel {
      padding: 14px 12px 6px;
    }
    .sidebar {
      padding: 16px 12px;
    }
    .feed-main__title {
      font-size: 22px;
    }
    .feed-main__header {
      align-items: flex-start;
    }
    .tx-card {
      padding: 14px;
      gap: 10px;
    }
    .tx-card__amount {
      font-size: 16px;
    }
    .tx-card__name {
      font-size: 12px;
    }
    .feed-filter-chip {
      padding: 7px 16px;
    }
  }
</style>
