const GIFT_STATS_DIRECTIONS = new Set(['out', 'in']);
const GIFT_STATS_RANGES = new Set(['30', 'all']);
const MISSING = Symbol('missing');
const STATUS_META_RULES = Object.freeze({
  enabled: value => typeof value === 'boolean',
  next_run_time: value => typeof value === 'string',
  next_trigger_time: value => typeof value === 'string',
  next_trigger_action: value => typeof value === 'string',
});

function ownDataValue(record, key) {
  try {
    const descriptor = Object.getOwnPropertyDescriptor(record, key);
    return descriptor && Object.prototype.hasOwnProperty.call(descriptor, 'value')
      ? descriptor.value
      : MISSING
  } catch {
    return MISSING
  }
}

function isPlainDataObject(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) return false
  try {
    if (Object.getPrototypeOf(value) !== Object.prototype) return false
    const descriptors = Object.getOwnPropertyDescriptors(value);
    return Reflect.ownKeys(descriptors).every((key) => {
      const descriptor = descriptors[key];
      return typeof key === 'string'
        && descriptor.enumerable === true
        && Object.prototype.hasOwnProperty.call(descriptor, 'value')
    })
  } catch {
    return false
  }
}

function isPlainDataArray(value, itemValidator) {
  if (!Array.isArray(value)) return false
  try {
    if (Object.getPrototypeOf(value) !== Array.prototype) return false
    const descriptors = Object.getOwnPropertyDescriptors(value);
    const length = descriptors.length?.value;
    if (!Number.isSafeInteger(length) || length < 0) return false

    let itemCount = 0;
    for (const key of Reflect.ownKeys(descriptors)) {
      if (key === 'length') continue
      const descriptor = descriptors[key];
      if (
        typeof key !== 'string'
        || !/^(0|[1-9]\d*)$/.test(key)
        || Number(key) >= length
        || descriptor.enumerable !== true
        || !Object.prototype.hasOwnProperty.call(descriptor, 'value')
        || !itemValidator(descriptor.value)
      ) return false
      itemCount += 1;
    }
    return itemCount === length
  } catch {
    return false
  }
}

function isPlainObjectArray(value) {
  return isPlainDataArray(value, isPlainDataObject)
}

function isCompletePillStatus(value) {
  if (!isPlainDataObject(value)) return false

  const overview = ownDataValue(value, 'overview');
  const brick = ownDataValue(value, 'brick');
  const beach = ownDataValue(value, 'beach');
  const exchange = ownDataValue(value, 'exchange');
  const inventory = ownDataValue(value, 'inventory');
  const recipes = ownDataValue(value, 'recipes');
  const history = ownDataValue(value, 'history');
  const inventoryItems = isPlainDataObject(inventory)
    ? ownDataValue(inventory, 'items')
    : MISSING;

  return isPlainObjectArray(overview)
    && isPlainDataObject(brick)
    && isPlainDataObject(beach)
    && isPlainDataObject(exchange)
    && isPlainDataObject(inventory)
    && isPlainObjectArray(inventoryItems)
    && isPlainObjectArray(recipes)
    && isPlainObjectArray(history)
}

function extractStatusMeta(response, nestedStatus) {
  const meta = {};
  for (const source of [nestedStatus, response]) {
    if (!source) continue
    for (const [key, isValid] of Object.entries(STATUS_META_RULES)) {
      if (Object.prototype.hasOwnProperty.call(meta, key)) continue
      const value = ownDataValue(source, key);
      if (value !== MISSING && isValid(value)) {
        Object.defineProperty(meta, key, {
          value,
          enumerable: true,
          configurable: true,
          writable: true,
        });
      }
    }
  }
  return meta
}

function createLatestRequestGuard() {
  let latestRequestId = 0;

  return {
    begin() {
      latestRequestId += 1;
      return latestRequestId
    },
    invalidate() {
      latestRequestId += 1;
      return latestRequestId
    },
    isCurrent(requestId) {
      return requestId === latestRequestId
    },
  }
}

function isStrictSuccess(response) {
  return response?.success === true
}

function extractStatusPayload(response) {
  if (!isPlainDataObject(response)) return null

  const statusCandidate = ownDataValue(response, 'status');
  const nestedStatus = isPlainDataObject(statusCandidate) ? statusCandidate : null;
  const directPillStatus = ownDataValue(response, 'pill_status');
  const nestedPillStatus = nestedStatus
    ? ownDataValue(nestedStatus, 'pill_status')
    : MISSING;
  const pillStatus = [directPillStatus, nestedPillStatus]
    .find(isCompletePillStatus);
  if (!pillStatus) return null

  const directHistory = ownDataValue(response, 'history');
  const nestedHistory = nestedStatus
    ? ownDataValue(nestedStatus, 'history')
    : MISSING;
  const pillHistory = ownDataValue(pillStatus, 'history');
  const history = [directHistory, nestedHistory, pillHistory]
    .find(isPlainObjectArray);

  return {
    pillStatus,
    history,
    statusMeta: extractStatusMeta(response, nestedStatus),
  }
}

function resolveGiftStatsFilters(response, requested) {
  const requestedDirection = GIFT_STATS_DIRECTIONS.has(requested?.direction)
    ? requested.direction
    : 'out';
  const requestedRange = GIFT_STATS_RANGES.has(requested?.range)
    ? requested.range
    : '30';

  return {
    direction: GIFT_STATS_DIRECTIONS.has(response?.direction)
      ? response.direction
      : requestedDirection,
    range: GIFT_STATS_RANGES.has(response?.range)
      ? response.range
      : requestedRange,
  }
}

function safeResponseMessage(response, fallback) {
  const message = typeof response?.message === 'string'
    ? response.message.trim()
    : '';
  return message || fallback
}

const _export_sfc = (sfc, props) => {
  const target = sfc.__vccOpts || sfc;
  for (const [key, val] of props) {
    target[key] = val;
  }
  return target;
};

export { _export_sfc as _, createLatestRequestGuard as c, extractStatusPayload as e, isStrictSuccess as i, resolveGiftStatsFilters as r, safeResponseMessage as s };
