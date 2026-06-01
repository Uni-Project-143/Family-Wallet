import { usePersistentState } from './usePersistentState'
import { fetchGiftEventsByIds } from '../services/giftEventService'

/**
 * Локальний реєстр gift-подій (PROJ-55..64).
 *
 * ⚠️ Backend не має ендпоінта "список подій групи" (GET /gift/group/{id} відсутній —
 * є лише GET /gift/{id}/details). Щоб події відображалися у стрічці (правий блок
 * "Active Gift Events" + pinned-банер замість мок-заглушки Sofia's Birthday),
 * фронт зберігає id подій, які користувач створив або відкрив, у localStorage,
 * згрупувавши за groupId, і дотягує їх деталі по одному.
 *
 * Обмеження (потребує бекенд-ендпоінта для повного покриття):
 * події, створені іншими учасниками на інших пристроях, не зʼявляться,
 * доки користувач не відкриє їх за прямим лінком.
 *
 * Ізоляція target user (PROJ-58) зберігається: деталі замкненої події
 * повертають 403 і тихо відкидаються у fetchGiftEventsByIds.
 */

const STORAGE_KEY = 'fw_tracked_gifts'

// { [groupId]: [giftId, ...] }
const tracked = usePersistentState(STORAGE_KEY, {})

export function useGiftEvents() {
  function getTrackedIds(groupId) {
    if (!groupId) return []
    return tracked.value[groupId] || []
  }

  /** Запамʼятати подію для відображення у стрічці цієї групи. */
  function trackGift(groupId, giftId) {
    if (!groupId || !giftId) return
    const ids = new Set(tracked.value[groupId] || [])
    if (ids.has(giftId)) return
    ids.add(giftId)
    tracked.value = { ...tracked.value, [groupId]: [...ids] }
  }

  /** Прибрати подію (напр. якщо вона зникла/скасована). */
  function untrackGift(groupId, giftId) {
    if (!groupId || !tracked.value[groupId]) return
    tracked.value = {
      ...tracked.value,
      [groupId]: tracked.value[groupId].filter((id) => id !== giftId),
    }
  }

  /** Завантажити деталі всіх відстежуваних подій групи. */
  async function loadTrackedGiftEvents(groupId) {
    const ids = getTrackedIds(groupId)
    return await fetchGiftEventsByIds(ids)
  }

  return { tracked, getTrackedIds, trackGift, untrackGift, loadTrackedGiftEvents }
}
