function cleanText(value) {
  return String(value || '').trim()
}

function cleanLower(value) {
  return cleanText(value).toLowerCase()
}

function normalizeUrl(value) {
  const text = cleanLower(value).replace(/\/+$/, '')
  if (!text) return ''
  try {
    const parsed = new URL(text)
    return `${parsed.protocol}//${parsed.host}${parsed.pathname.replace(/\/+$/, '')}`
  } catch {
    return text
  }
}

export function visibleLogLines(item) {
  const summary = cleanText(item?.summary)
  const statusTitle = cleanText(item?.status_title || item?.title)
  const lines = Array.isArray(item?.lines) ? item.lines : []
  const unique = []
  const seen = new Set()
  for (const line of lines) {
    const text = cleanText(line)
    if (!text || text === summary || text === statusTitle) continue
    const key = text.toLowerCase()
    if (seen.has(key)) continue
    seen.add(key)
    unique.push(text)
  }
  return unique
}

export function logEntryKey(item) {
  if (!item) return ''
  return [
    cleanText(item.card_id),
    cleanText(item.time),
    cleanText(item.status_title || item.title),
    cleanText(item.summary),
    visibleLogLines(item).join('|'),
  ].join('::')
}

function sameLegacyNewApiTarget(item, card) {
  const cardSiteUrl = normalizeUrl(card.site_url)
  const itemSiteUrl = normalizeUrl(item.site_url)
  const cardUid = cleanText(card.uid)
  const itemUid = cleanText(item.uid)

  if (!cardSiteUrl || !itemSiteUrl || cardSiteUrl !== itemSiteUrl) return false
  if (cardUid && itemUid) return cardUid === itemUid
  return true
}

export function logMatchesCard(item, card) {
  if (!item || !card) return false

  const cardId = cleanText(card.card_id || card.id)
  const itemCardId = cleanText(item.card_id)
  if (cardId && itemCardId) return cardId === itemCardId
  if (!cardId && itemCardId) return false

  const cardModule = cleanText(card.module_key)
  const itemModule = cleanText(item.module_key)
  if (!cardModule || !itemModule || cardModule !== itemModule) return false

  if (cardModule === 'newapi_checkin') {
    return sameLegacyNewApiTarget(item, card)
  }

  const cardSiteUrl = normalizeUrl(card.site_url)
  const itemSiteUrl = normalizeUrl(item.site_url)
  if (cardSiteUrl && itemSiteUrl && cardSiteUrl === itemSiteUrl) return true

  const cardSiteName = cleanLower(card.site_name)
  const itemSiteName = cleanLower(item.site_name)
  if (cardSiteName && itemSiteName && cardSiteName === itemSiteName) return true

  const cardTitle = cleanLower(card.title)
  const itemTitle = cleanLower(item.title)
  return Boolean(cardTitle && itemTitle && cardTitle === itemTitle)
}
