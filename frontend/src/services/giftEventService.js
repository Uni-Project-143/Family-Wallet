import apiClient from './apiClient'

//Service-шар з 4-ма API-функціями

/**
 * POST /api/v1/gift/create — створює нову gift event (PROJ-55, PROJ-56).
 * @param {object} payload - { name, target_user_id, unlock_date (ISO UTC), goal_amount, group_id }
 * @returns {Promise<{gift_id: string, status: string, ...}>}
 */
export async function createGiftEvent(payload) {
  const response = await apiClient.post('/api/v1/gift/create', payload)
  return response.data
}

/**
 * GET /api/v1/gift/{id}/details — деталі події (PROJ-58, PROJ-64).
 * Target user отримує 403 до unlock_date (бек middleware).
 */
export async function fetchGiftEventDetails(giftId) {
  const response = await apiClient.get(`/api/v1/gift/${giftId}/details`)
  return response.data
}

/**
 * Invite-лінк для запрошення родини до збору (PROJ-57).
 *
 * ⚠️ Backend НЕ має gift-специфічного ендпоінта POST /gift/{id}/invite.
 * Тому використовуємо реальний ГРУПОВИЙ invite — GET /api/v1/group/{group_id}/invite,
 * який повертає валідний токенізований лінк ({invite_link, token, expires_at}).
 * Лінк запрошує користувача до групи (де й відбувається збір).
 *
 * Якщо груповий invite недоступний (напр. організатор не ADMIN → 403),
 * повертаємо локальний fallback-URL, щоб UX копіювання не ламався.
 *
 * @param {string} giftId
 * @param {string} [groupId]
 * @returns {Promise<{invite_url: string, token: string, expires_at: string|null}>}
 */
export async function generateGiftInviteLink(giftId, groupId) {
  if (groupId) {
    try {
      const response = await apiClient.get(`/api/v1/group/${groupId}/invite`)
      const data = response.data
      return {
        invite_url: data.invite_link,
        token: data.token,
        expires_at: data.expires_at ?? null,
      }
    } catch {
      // Падаємо у fallback нижче (403 для не-ADMIN, 404, мережа тощо)
    }
  }
  return {
    invite_url: `${window.location.origin}/gift/join/${giftId}`,
    token: giftId,
    expires_at: null,
  }
}

/**
 * Завантажує деталі кількох подій за їх id (паралельно, fault-tolerant).
 *
 * ⚠️ Backend не має ендпоінта "список подій групи" (GET /gift/group/{id} відсутній).
 * Тому фронт сам тримає список id створених/відкритих подій (див. useGiftEvents)
 * і дотягує деталі через GET /gift/{id}/details.
 *
 * Події, що повертають помилку (403 ізоляція target / 404 cancelled), тихо
 * відкидаються — це зберігає таємність сюрпризу (PROJ-58).
 *
 * @param {string[]} ids
 * @returns {Promise<object[]>}
 */
export async function fetchGiftEventsByIds(ids = []) {
  if (!ids.length) return []
  const results = await Promise.allSettled(ids.map((id) => fetchGiftEventDetails(id)))
  return results.filter((r) => r.status === 'fulfilled').map((r) => r.value)
}
