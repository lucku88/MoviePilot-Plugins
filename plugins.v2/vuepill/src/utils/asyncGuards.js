const GIFT_STATS_DIRECTIONS = new Set(['out', 'in'])
const GIFT_STATS_RANGES = new Set(['30', 'all'])

export function createLatestRequestGuard() {
  let latestRequestId = 0

  return {
    begin() {
      latestRequestId += 1
      return latestRequestId
    },
    invalidate() {
      latestRequestId += 1
      return latestRequestId
    },
    isCurrent(requestId) {
      return requestId === latestRequestId
    },
  }
}

export function isStrictSuccess(response) {
  return response?.success === true
}

export function resolveGiftStatsFilters(response, requested) {
  const requestedDirection = GIFT_STATS_DIRECTIONS.has(requested?.direction)
    ? requested.direction
    : 'out'
  const requestedRange = GIFT_STATS_RANGES.has(requested?.range)
    ? requested.range
    : '30'

  return {
    direction: GIFT_STATS_DIRECTIONS.has(response?.direction)
      ? response.direction
      : requestedDirection,
    range: GIFT_STATS_RANGES.has(response?.range)
      ? response.range
      : requestedRange,
  }
}

export function safeResponseMessage(response, fallback) {
  const message = typeof response?.message === 'string'
    ? response.message.trim()
    : ''
  return message || fallback
}
