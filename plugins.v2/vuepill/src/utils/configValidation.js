export const BOOLEAN_CONFIG_FIELDS = Object.freeze([
  'enabled',
  'notify',
  'onlyonce',
  'use_proxy',
  'enable_brick',
  'enable_beach',
  'auto_craft',
  'auto_exchange',
])

export const INTEGER_CONFIG_RULES = Object.freeze({
  schedule_buffer_seconds: Object.freeze({ label: '冷却缓冲', min: 0, max: 3600 }),
  reserve_magic_pill_count: Object.freeze({ label: '保留魔丸', min: 0, max: Number.MAX_SAFE_INTEGER }),
  random_delay_max_seconds: Object.freeze({ label: '随机延迟', min: 0, max: 300 }),
  http_timeout: Object.freeze({ label: '请求超时', min: 5, max: 120 }),
  http_retry_times: Object.freeze({ label: '网络重试次数', min: 1, max: 5 }),
  http_retry_delay: Object.freeze({ label: '重试间隔', min: 200, max: 60000 }),
})

export const DEFAULT_CONFIG = Object.freeze({
  enabled: false,
  notify: true,
  onlyonce: false,
  use_proxy: false,
  enable_brick: true,
  enable_beach: true,
  auto_craft: false,
  auto_exchange: false,
  cookie: '',
  brick_cron: '5 0 * * *',
  schedule_buffer_seconds: 5,
  reserve_magic_pill_count: 10,
  random_delay_max_seconds: 3,
  http_timeout: 12,
  http_retry_times: 5,
  http_retry_delay: 1500,
})

const CANONICAL_UNSIGNED_INTEGER = /^(?:0|[1-9]\d*)$/
const MAX_MANUAL_COOKIE_LENGTH = 16384
const CRON_NUMBER = /^\d+$/
const MONTH_NAMES = Object.freeze({
  jan: 1,
  feb: 2,
  mar: 3,
  apr: 4,
  may: 5,
  jun: 6,
  jul: 7,
  aug: 8,
  sep: 9,
  oct: 10,
  nov: 11,
  dec: 12,
})
const DAY_OF_WEEK_NAMES = Object.freeze({
  mon: 0,
  tue: 1,
  wed: 2,
  thu: 3,
  fri: 4,
  sat: 5,
  sun: 6,
})
const CRON_FIELD_RULES = Object.freeze([
  Object.freeze({ label: '分钟', min: 0, max: 59 }),
  Object.freeze({ label: '小时', min: 0, max: 23 }),
  Object.freeze({ label: '日期', min: 1, max: 31 }),
  Object.freeze({ label: '月份', min: 1, max: 12, names: MONTH_NAMES }),
  Object.freeze({ label: '星期', min: 0, max: 7, names: DAY_OF_WEEK_NAMES }),
])

export function parseStrictInteger(value, rule) {
  let parsed
  if (typeof value === 'number') {
    if (!Number.isSafeInteger(value)) {
      return { valid: false, value: null, error: `${rule.label}必须填写规范整数` }
    }
    parsed = value
  } else if (typeof value === 'string' && CANONICAL_UNSIGNED_INTEGER.test(value)) {
    parsed = Number(value)
    if (!Number.isSafeInteger(parsed)) {
      return { valid: false, value: null, error: `${rule.label}必须填写安全整数` }
    }
  } else {
    return { valid: false, value: null, error: `${rule.label}必须填写规范整数` }
  }

  if (parsed < rule.min || parsed > rule.max) {
    return {
      valid: false,
      value: null,
      error: `${rule.label}必须在 ${rule.min} 到 ${rule.max} 之间`,
    }
  }
  return { valid: true, value: parsed, error: '' }
}

function parseCronValue(value, rule) {
  if (CRON_NUMBER.test(value)) {
    const parsed = Number(value)
    return Number.isSafeInteger(parsed) && parsed >= rule.min && parsed <= rule.max
      ? parsed
      : null
  }
  return rule.names && Object.hasOwn(rule.names, value)
    ? rule.names[value]
    : null
}

function validateCronItem(item, rule) {
  const stepParts = item.split('/')
  if (stepParts.length > 2 || stepParts.some(part => !part)) return false

  const base = stepParts[0]
  let step = null
  if (stepParts.length === 2) {
    if (!CRON_NUMBER.test(stepParts[1])) return false
    step = Number(stepParts[1])
    if (!Number.isSafeInteger(step) || step <= 0) return false
  }

  let start
  let end
  if (base === '*') {
    start = rule.min
    end = rule.max
  } else if (base.includes('-')) {
    const rangeParts = base.split('-')
    if (rangeParts.length !== 2 || rangeParts.some(part => !part)) return false
    start = parseCronValue(rangeParts[0], rule)
    end = parseCronValue(rangeParts[1], rule)
    if (start === null || end === null || start > end) return false
  } else {
    if (step !== null) return false
    return parseCronValue(base, rule) !== null
  }

  return step === null || step <= end - start
}

function validateCronField(field, rule) {
  const items = field.split(',')
  if (!items.length || items.some(item => !item)) return false
  if (items.length > 1 && items.some(item => item.startsWith('*'))) return false
  return items.every(item => validateCronItem(item, rule))
}

export function validateCronExpression(value) {
  if (typeof value !== 'string' || !value.trim()) {
    return { valid: false, value: '', error: '搬砖 Cron 不能为空' }
  }
  if (/\r|\n/.test(value)) {
    return { valid: false, value: '', error: '搬砖 Cron 不能包含换行' }
  }

  const fields = value.trim().split(/[ \t]+/)
  if (fields.length !== 5) {
    return { valid: false, value: '', error: '搬砖 Cron 必须是 5 段表达式' }
  }
  const normalizedFields = fields.map(field => field.toLowerCase())
  const invalidIndex = normalizedFields.findIndex(
    (field, index) => !validateCronField(field, CRON_FIELD_RULES[index]),
  )
  if (invalidIndex >= 0) {
    return {
      valid: false,
      value: '',
      error: `搬砖 Cron 的${CRON_FIELD_RULES[invalidIndex].label}段不合法`,
    }
  }
  return { valid: true, value: normalizedFields.join(' '), error: '' }
}

export function validateManualCookie(value) {
  if (typeof value !== 'string') {
    return { valid: false, value: '', error: '站点 Cookie 必须是文本' }
  }
  if (/\r|\n/.test(value)) {
    return { valid: false, value: '', error: '站点 Cookie 不能包含换行' }
  }
  const cookie = value.trim()
  if (cookie.length > MAX_MANUAL_COOKIE_LENGTH) {
    return { valid: false, value: '', error: '站点 Cookie 内容过长' }
  }
  if (cookie.toLowerCase() === 'cookie') {
    return { valid: false, value: '', error: '站点 Cookie 不是有效内容' }
  }
  if ([...cookie].some(character => character.charCodeAt(0) < 32 || character.charCodeAt(0) === 127)) {
    return { valid: false, value: '', error: '站点 Cookie 包含不允许的控制字符' }
  }
  return { valid: true, value: cookie, error: '' }
}

export function validateVuePillConfig(source) {
  const safeSource = source && typeof source === 'object' ? source : {}
  const payload = {}
  const errors = {}

  for (const field of BOOLEAN_CONFIG_FIELDS) {
    payload[field] = safeSource[field] === true
  }

  const cron = validateCronExpression(safeSource.brick_cron)
  if (cron.valid) payload.brick_cron = cron.value
  else errors.brick_cron = cron.error

  const cookie = validateManualCookie(safeSource.cookie)
  if (cookie.valid) payload.cookie = cookie.value
  else errors.cookie = cookie.error

  for (const [field, rule] of Object.entries(INTEGER_CONFIG_RULES)) {
    const parsed = parseStrictInteger(safeSource[field], rule)
    if (parsed.valid) payload[field] = parsed.value
    else errors[field] = parsed.error
  }

  const errorFields = Object.keys(errors)
  return {
    valid: errorFields.length === 0,
    payload,
    errors,
    firstErrorField: errorFields[0] || '',
  }
}
