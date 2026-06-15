export default {
  common: {
    retry: 'Retry',
    cancel: 'Cancel',
    back: 'Go back',
    loading: 'Loading…',
    reload: 'Reload page',
    loadMore: 'Load more',
  },

  empty: {
    members: 'No members in this group yet.',
    cards: 'No cards connected yet.',
    spending: 'No spending to analyze yet.',
    notifications: 'Reminders about gift unlocks are delivered by email and push.',
    transactions: 'No transactions yet. Awaiting the first transaction from Monobank.',
    donors: 'No contributions yet. Share the link with family!',
    giftEvents: 'No active gift events.',
  },

  loading: {
    generic: 'Loading…',
    members: 'Loading members…',
    cards: 'Loading cards…',
    event: 'Loading event…',
    more: 'Loading more…',
  },

  errors: {
    boundaryTitle: 'Something went wrong',
    boundaryHint: 'This section failed to load. You can try again or reload the page.',
    fallback: 'Something went wrong. Please try again.',
    network: 'No connection to the server. Check your internet and try again.',
    timeout: 'The request timed out. Please try again.',
    byStatus: {
      400: 'Invalid request. Please check the data you entered.',
      401: 'Your session has expired. Please sign in again.',
      403: "You don't have permission to perform this action.",
      404: 'The requested item was not found.',
      409: 'Conflict: this record already exists or was changed elsewhere.',
      422: 'Validation failed. Please check the fields.',
      429: 'Too many requests. Please try again shortly.',
      500: 'Server error. Please try again later.',
      502: 'Server is unavailable. Please try again later.',
      503: 'Service temporarily unavailable. Please try again later.',
    },
  },
}
