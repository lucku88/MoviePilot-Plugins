export const BOOLEAN_CONFIG_FIELDS = Object.freeze([
  'enabled',
  'notify',
  'onlyonce',
  'use_proxy',
  'force_ipv4',
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
  force_ipv4: true,
  enable_brick: true,
  enable_beach: true,
  auto_craft: false,
  auto_exchange: false,
  brick_cron: '5 0 * * *',
  schedule_buffer_seconds: 5,
  reserve_magic_pill_count: 10,
  random_delay_max_seconds: 3,
  http_timeout: 12,
  http_retry_times: 5,
  http_retry_delay: 1500,
})

const CANONICAL_UNSIGNED_INTEGER = /^(?:0|[1-9]\d*)$/
const SAFE_CRON_FIELD = /^[0-9A-Za-z*/,\-]+$/

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
  if (fields.some(field => !SAFE_CRON_FIELD.test(field))) {
    return { valid: false, value: '', error: '搬砖 Cron 包含不支持的字符' }
  }
  return { valid: true, value: fields.join(' '), error: '' }
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
