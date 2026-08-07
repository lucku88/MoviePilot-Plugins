<template>
  <div class="siqi-page">
    <div class="siqi-topbar">
      <div class="siqi-topbar__left">
        <div class="siqi-topbar__icon">
          <v-icon icon="mdi-teddy-bear" size="24" />
        </div>
        <div class="siqi-topbar__copy">
          <div class="siqi-topbar__title">Vue-玩偶</div>
          <div class="siqi-topbar__sub">自己展位优先，动态收回与外展</div>
        </div>
      </div>
      <div class="siqi-topbar__right">
        <v-btn-group variant="tonal" density="compact" class="elevation-0">
          <v-btn
            color="success"
            size="small"
            min-width="40"
            class="px-0 px-sm-3"
            aria-label="刷新 Vue-玩偶状态"
            :loading="actionLoading === 'refresh'"
            :disabled="isBusy"
            @click="refreshData"
          >
            <v-icon icon="mdi-refresh" size="18" class="mr-sm-1" />
            <span class="d-none d-sm-inline">刷新</span>
          </v-btn>
          <v-btn
            color="success"
            size="small"
            min-width="40"
            class="px-0 px-sm-3"
            aria-label="打开 Vue-玩偶配置"
            :disabled="isBusy"
            @click="emit('switch', 'config')"
          >
            <v-icon icon="mdi-cog-outline" size="18" class="mr-sm-1" />
            <span class="d-none d-sm-inline">配置</span>
          </v-btn>
          <v-btn
            color="success"
            size="small"
            min-width="40"
            class="px-0 px-sm-3"
            aria-label="关闭 Vue-玩偶"
            :disabled="isBusy"
            @click="emit('close')"
          >
            <v-icon icon="mdi-close" size="18" class="mr-sm-1" />
            <span class="d-none d-sm-inline">关闭</span>
          </v-btn>
        </v-btn-group>
      </div>
    </div>

    <div class="siqi-content">
      <v-alert
        v-if="message.text"
        :type="message.type"
        density="compact"
        class="siqi-toast"
        closable
        @click:close="message.text = ''"
      >
        {{ message.text }}
      </v-alert>

      <div v-if="initialLoading" class="loading-state" role="status" aria-live="polite">
        <v-progress-linear color="success" indeterminate rounded />
        <span>正在读取玩偶状态，请稍候</span>
      </div>

      <template v-else>
        <v-row dense class="mb-3 overview-grid">
          <v-col v-for="(item, index) in overviewCards" :key="item.label" cols="6" md="3">
            <div class="stat-card" :class="`stat-${statTone(index)}`">
              <div class="stat-icon">
                <v-icon :icon="statIcon(index)" size="23" />
              </div>
              <div class="stat-content">
                <div class="stat-title">{{ item.label }}</div>
                <div class="stat-value">{{ item.value }}</div>
              </div>
            </div>
          </v-col>
        </v-row>

        <v-card flat class="siqi-card next-run-card mb-3">
          <v-card-text class="next-run-body">
            <div class="next-run-icon">
              <v-icon icon="mdi-calendar-clock-outline" size="23" />
            </div>
            <div class="next-run-copy">
              <div class="next-run-title">下次运行</div>
              <div class="next-run-sub">按展位完成时间动态运行，不使用固定周期</div>
              <div v-if="placementGuardText" class="next-run-guard">{{ placementGuardText }}</div>
            </div>
            <div class="next-run-times">
              <div class="next-run-time">
                <span>计划触发</span>
                <strong>{{ toy.next_trigger_time || status.next_trigger_time || '等待刷新' }}</strong>
              </div>
              <div class="next-run-time">
                <span>执行时间</span>
                <strong>{{ toy.next_run_time || status.next_run_time || '等待刷新' }}</strong>
              </div>
              <v-chip size="small" :color="status.enabled ? 'success' : 'grey'" variant="tonal">
                {{ status.enabled ? '已启用' : '未启用' }}
              </v-chip>
              <v-btn
                color="success"
                variant="tonal"
                size="small"
                class="schedule-run-btn"
                :loading="actionLoading === 'run'"
                :disabled="isBusy"
                @click="runNow"
              >
                <v-icon icon="mdi-play-circle-outline" size="17" class="mr-1" />立即执行
              </v-btn>
            </div>
          </v-card-text>
          <v-alert v-if="summaryLines.length" type="success" variant="tonal" density="compact" class="summary-alert">
            {{ summaryLines.join(' / ') }}
          </v-alert>
        </v-card>

        <div class="two-column-grid mb-3">
          <v-card flat class="siqi-card box-card">
            <v-card-title class="siqi-card-title d-flex align-center">
              <v-icon icon="mdi-shopping-outline" size="19" color="purple" class="mr-2" />盲盒商店
            </v-card-title>
            <v-card-text>
              <div v-if="!shopBoxes.length" class="empty-state">暂未获取到盲盒商店</div>
              <div v-else class="box-list">
                <article v-for="box in shopBoxes" :key="box.box_key || box.name" class="box-row" :class="{ 'box-row--locked': box.locked }">
                  <img v-if="box.image" :src="box.image" :alt="box.name" class="box-image" loading="lazy" />
                  <div v-else class="box-image box-image--placeholder"><v-icon icon="mdi-package-variant-closed" size="26" /></div>
                  <div class="box-copy">
                    <div class="box-name">{{ box.name }}</div>
                    <div class="box-desc">{{ box.lock_text || box.desc }}</div>
                  </div>
                  <v-text-field
                    v-model="buyQuantities[box.box_key]"
                    type="number"
                    min="1"
                    density="compact"
                    variant="outlined"
                    hide-details
                    class="quantity-field"
                    aria-label="购买数量"
                  />
                  <v-btn
                    color="purple"
                    variant="tonal"
                    size="small"
                    :disabled="box.buy_enabled === false || isBusy"
                    :loading="actionLoading === `buy-${box.box_key}`"
                    @click="buyBox(box)"
                  >购买</v-btn>
                </article>
              </div>
            </v-card-text>
          </v-card>

          <v-card flat class="siqi-card box-card">
            <v-card-title class="siqi-card-title d-flex align-center">
              <v-icon icon="mdi-package-variant" size="19" color="teal" class="mr-2" />我的盲盒
            </v-card-title>
            <v-card-text>
              <div v-if="!myBoxes.length" class="empty-state">暂无盲盒</div>
              <div v-else class="box-list">
                <article v-for="box in myBoxes" :key="`owned-${box.box_key || box.name}`" class="box-row">
                  <img v-if="box.image" :src="box.image" :alt="box.name" class="box-image" loading="lazy" />
                  <div v-else class="box-image box-image--placeholder"><v-icon icon="mdi-package-variant" size="26" /></div>
                  <div class="box-copy">
                    <div class="box-name">{{ box.name }}</div>
                    <div class="box-desc">拥有 {{ box.count }} 个</div>
                  </div>
                  <v-text-field
                    v-model="openQuantities[box.box_key || box.name]"
                    type="number"
                    min="1"
                    density="compact"
                    variant="outlined"
                    hide-details
                    class="quantity-field"
                    aria-label="开启数量"
                  />
                  <v-btn
                    color="teal"
                    variant="tonal"
                    size="small"
                    :disabled="box.open_enabled === false || isBusy"
                    :loading="actionLoading === `open-${box.box_key}`"
                    @click="openBox(box)"
                  >开启</v-btn>
                </article>
              </div>
            </v-card-text>
          </v-card>
        </div>


        <v-card flat class="siqi-card cabinet-card mb-3">
          <v-card-title class="siqi-card-title d-flex align-center">
            <v-icon icon="mdi-archive-outline" size="19" color="blue" class="mr-2" />玩偶柜
            <v-spacer />
            <span class="section-count">{{ cabinetCards.length }} 类玩偶</span>
          </v-card-title>
          <v-card-text>
            <div class="selection-strip" :class="{ 'selection-strip--active': selectedDoll }">
              <v-icon :icon="selectedDoll ? 'mdi-check-circle-outline' : 'mdi-cursor-default-click-outline'" size="19" />
              <span>{{ selectedDoll ? `已选择 ${selectedDoll.name}，请点击自己或他人空展位` : '先选择可用玩偶，再点击空展位上架' }}</span>
              <v-btn v-if="selectedDoll" size="small" variant="text" @click="selectedDollKey = ''">取消选择</v-btn>
            </div>
            <div v-if="!cabinetCards.length" class="empty-state">暂无玩偶</div>
            <div v-else class="doll-grid">
              <article
                v-for="doll in cabinetCards"
                :key="doll.doll_key || doll.name"
                class="doll-card"
                :class="{ 'doll-card--selected': selectedDollKey === doll.doll_key, 'doll-card--disabled': !doll.can_place }"
              >
                <div class="doll-card__head">
                  <v-chip size="x-small" color="blue" variant="tonal">{{ doll.quality || '未识别' }}</v-chip>
                  <span>{{ doll.origin || '' }}</span>
                </div>
                <img v-if="doll.image" :src="doll.image" :alt="doll.name" class="doll-image" loading="lazy" />
                <div v-else class="doll-image doll-image--placeholder"><v-icon icon="mdi-teddy-bear" size="38" /></div>
                <div class="doll-name">{{ doll.name }}</div>
                <div class="doll-meta">{{ doll.display_text }}</div>
                <div class="doll-meta">{{ doll.reward_text }}</div>
                <div class="doll-stats">
                  <span>可用 {{ doll.available }}</span>
                  <span>展出 {{ doll.display_count }}</span>
                  <span>冷却 {{ doll.cooling_count }}</span>
                </div>
                <div v-if="cabinetCooldownText(doll)" class="doll-cooldown">{{ cabinetCooldownText(doll) }}</div>
                <div class="doll-actions">
                  <v-btn
                    color="blue"
                    variant="tonal"
                    :disabled="!doll.can_place || isBusy"
                    @click="selectDoll(doll)"
                  >
                    {{ selectedDollKey === doll.doll_key ? '已选择' : '选择玩偶' }}
                  </v-btn>
                  <v-btn
                    color="orange"
                    variant="tonal"
                    :disabled="!doll.can_recycle || Number(doll.idle || 0) <= 0 || isBusy"
                    :loading="actionLoading === `recycle-${doll.doll_key}`"
                    @click="openRecycleDialog(doll)"
                  >
                    回收
                  </v-btn>
                </div>
              </article>
            </div>
          </v-card-text>
        </v-card>

        <v-card flat class="siqi-card personal-booth-card">
          <v-card-title class="siqi-card-title d-flex align-center">
            <v-icon icon="mdi-storefront-outline" size="19" color="orange" class="mr-2" />我的展柜
            <v-spacer />
            <span class="section-count">自己的玩偶 {{ ownedPersonalCount }}/{{ personalSlots.length }}</span>
          </v-card-title>
          <v-card-text class="personal-booth-body">
            <div v-if="!personalSlots.length" class="empty-state">暂未获取到自己展位</div>
            <div v-else class="slot-grid">
              <article
                v-for="slot in personalSlots"
                :key="`personal-${slot.slot_index}`"
                class="slot-card"
                :class="{
                  'slot-card--ready': slotKind(slot) === 'ready',
                  'slot-card--blocked': slotKind(slot) === 'blocked',
                  'slot-card--empty': slot.empty,
                }"
              >
                <div class="slot-card__head">
                  <span>展位 {{ slot.slot_index }}</span>
                  <v-chip size="x-small" :color="slotTone(slot)" variant="tonal">{{ slotBadge(slot) }}</v-chip>
                </div>

                <div v-if="slot.empty" class="slot-empty-body">
                  <v-icon :icon="slot.cooldown_active ? 'mdi-timer-sand' : 'mdi-plus-circle-outline'" size="34" />
                  <strong>{{ slot.cooldown_active ? '展位冷却中' : '空展位' }}</strong>
                  <span>{{ slot.cooldown_active ? '等待冷却结束后再上架' : selectedDoll ? `准备上架 ${selectedDoll.name}` : '请先从玩偶柜选择玩偶' }}</span>
                </div>
                <div v-else class="slot-main">
                  <img v-if="slot.image" :src="slot.image" :alt="slot.doll_name" class="slot-image" loading="lazy" />
                  <div v-else class="slot-image slot-image--placeholder"><v-icon icon="mdi-teddy-bear" size="34" /></div>
                  <div class="slot-info">
                    <div class="slot-name">{{ slot.doll_name || '未知玩偶' }}</div>
                    <div class="slot-owner">{{ slot.owner_name || (slot.viewer_is_occupant ? '自己' : '其他用户') }}</div>
                    <div class="slot-meta">{{ slotRemainText(slot) }}</div>
                    <div v-if="slot.reward_text" class="slot-meta">{{ slot.reward_text }}</div>
                  </div>
                </div>

                <div v-if="!slot.empty" class="slot-progress" aria-hidden="true">
                  <div class="slot-progress__bar" :style="{ width: `${Math.max(0, Math.min(100, Number(slot.progress || 0)))}%` }" />
                </div>

                <v-btn
                  v-if="slot.empty && !slot.cooldown_active"
                  block
                  color="orange"
                  variant="tonal"
                  class="card-action"
                  :disabled="!selectedDoll || isBusy"
                  :loading="actionLoading === `place-personal-${slot.slot_index}`"
                  @click="placePersonal(slot)"
                >
                  上架所选玩偶
                </v-btn>
                <v-btn
                  v-else-if="slot.viewer_is_occupant"
                  block
                  :color="slotKind(slot) === 'ready' ? 'success' : 'warning'"
                  variant="tonal"
                  class="card-action"
                  :disabled="isBusy"
                  :loading="actionLoading === `collect-${slot.owner_id}-${slot.slot_index}`"
                  @click="collectSlot(slot)"
                >
                  {{ slotKind(slot) === 'ready' ? '收回玩偶' : '提前收回' }}
                </v-btn>
                <v-btn v-else block color="grey" variant="tonal" class="card-action" disabled>
                  已被占用
                </v-btn>
              </article>
            </div>
          </v-card-text>
        </v-card>

        <div class="interaction-grid mb-3">
        <v-card flat class="siqi-card target-card">
          <v-card-title class="siqi-card-title d-flex align-center">
            <v-icon icon="mdi-account-search-outline" size="19" color="red" class="mr-2" />抢占他人展位
            <v-spacer />
            <span v-if="targetPanel.username" class="section-count">当前目标：{{ targetPanel.username }}</span>
          </v-card-title>
          <v-card-text class="target-body">
            <div class="target-tools">
              <v-text-field
                v-model="targetKeyword"
                label="用户名或用户 ID"
                placeholder="留空可使用随机匹配"
                density="compact"
                variant="outlined"
                hide-details
                prepend-inner-icon="mdi-account-outline"
                :disabled="isBusy"
                @keyup.enter="viewTarget()"
              />
              <v-btn color="red" variant="tonal" :disabled="isBusy || !targetKeyword.trim()" :loading="actionLoading === 'view-target'" @click="viewTarget()">
                查看目标
              </v-btn>
              <v-btn color="orange" variant="tonal" :disabled="isBusy" :loading="actionLoading === 'random-target'" @click="randomTarget">
                随机匹配
              </v-btn>
            </div>

            <div v-if="!targetPanel.slots?.length" class="empty-state">尚未选择目标，自动任务会按限制随机寻找空展位</div>
            <div v-else class="slot-grid target-slot-grid">
              <article v-for="slot in targetPanel.slots" :key="`target-${slot.owner_id}-${slot.slot_index}`" class="slot-card">
                <div class="slot-card__head">
                  <span>展位 {{ slot.slot_index }}</span>
                  <v-chip size="x-small" :color="slotTone(slot)" variant="tonal">{{ slotBadge(slot) }}</v-chip>
                </div>
                <div v-if="slot.empty" class="slot-empty-body">
                  <v-icon :icon="slot.cooldown_active ? 'mdi-timer-sand' : 'mdi-plus-circle-outline'" size="34" />
                  <strong>{{ slot.cooldown_active ? '展位冷却中' : '空位可抢' }}</strong>
                  <span>{{ selectedDoll ? `准备展出 ${selectedDoll.name}` : '请先选择玩偶' }}</span>
                </div>
                <div v-else class="slot-main">
                  <img v-if="slot.image" :src="slot.image" :alt="slot.doll_name" class="slot-image" loading="lazy" />
                  <div v-else class="slot-image slot-image--placeholder"><v-icon icon="mdi-teddy-bear" size="34" /></div>
                  <div class="slot-info">
                    <div class="slot-name">{{ slot.doll_name || slot.status_text }}</div>
                    <div class="slot-owner">{{ slot.owner_name || '其他用户' }}</div>
                    <div class="slot-meta">{{ slotRemainText(slot) }}</div>
                  </div>
                </div>
                <v-btn
                  v-if="slot.empty && !slot.cooldown_active"
                  block
                  color="red"
                  variant="tonal"
                  class="card-action"
                  :disabled="!selectedDoll || isBusy"
                  :loading="actionLoading === `place-target-${slot.slot_index}`"
                  @click="placeTarget(slot)"
                >
                  展出所选玩偶
                </v-btn>
                <v-btn v-else block color="grey" variant="tonal" class="card-action" disabled>
                  {{ slot.cooldown_active ? '冷却中' : '已被占用' }}
                </v-btn>
              </article>
            </div>
          </v-card-text>
        </v-card>

        <v-card flat class="siqi-card remote-card">
          <v-card-title class="siqi-card-title d-flex align-center">
            <v-icon icon="mdi-map-marker-path" size="19" color="indigo" class="mr-2" />我的外展记录
            <v-spacer />
            <span class="section-count">{{ remoteRecords.length }} 个展位</span>
          </v-card-title>
          <v-card-text class="remote-body">
            <div v-if="!remoteRecords.length" class="empty-state">暂无外展记录</div>
            <div v-else class="remote-grid">
              <article v-for="item in remoteRecords" :key="`${item.owner_id}-${item.slot_index}`" class="remote-row">
                <img v-if="item.image" :src="item.image" :alt="item.doll_name" class="remote-image" loading="lazy" />
                <div v-else class="remote-image remote-image--placeholder"><v-icon icon="mdi-teddy-bear" size="27" /></div>
                <div class="remote-copy">
                  <div class="remote-name">{{ item.doll_name }}</div>
                  <div class="remote-meta">{{ item.owner_name }} · 展位 {{ item.slot_index }}</div>
                  <div class="remote-meta">{{ remoteRemainText(item) }}</div>
                </div>
                <v-btn size="small" color="indigo" variant="tonal" :disabled="isBusy" @click="viewTarget(item.owner_id)">查看</v-btn>
              </article>
            </div>
          </v-card-text>
        </v-card>
        </div>

        <v-card flat class="siqi-card activity-card mb-3">
          <v-card-title class="siqi-card-title d-flex align-center">
            <v-icon icon="mdi-format-list-bulleted" size="19" color="cyan" class="mr-2" />最新操作记录
          </v-card-title>
          <v-card-text>
            <div v-if="!activityLogs.length" class="empty-state">暂无操作记录</div>
            <div v-else class="activity-list">
              <div v-for="(item, index) in activityLogs" :key="`${item.time}-${index}`" class="activity-row">
                <span>{{ item.message }}</span>
                <time>{{ item.time }}</time>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </template>
      <v-dialog v-model="recycleDialog.open" max-width="420">
        <v-card class="siqi-card recycle-dialog-card">
          <v-card-title class="siqi-card-title d-flex align-center">
            <v-icon icon="mdi-recycle" size="19" color="orange" class="mr-2" />回收闲置玩偶
          </v-card-title>
          <v-card-text v-if="recycleDialog.doll">
            <div class="recycle-dialog-name">{{ recycleDialog.doll.name }}</div>
            <div class="recycle-dialog-hint">
              当前闲置 {{ recycleDialog.doll.idle || 0 }} 个，仅回收未展出、未冷却的玩偶
            </div>
            <v-text-field
              v-model.number="recycleDialog.quantity"
              type="number"
              min="1"
              step="1"
              :max="recycleMax"
              label="回收数量"
              variant="outlined"
              density="compact"
              hide-details
              class="recycle-quantity"
            />
            <div class="recycle-estimate">预计获得魔力：{{ recycleEstimate }}</div>
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn variant="text" @click="recycleDialog.open = false">取消</v-btn>
            <v-btn
              color="orange"
              variant="tonal"
              :loading="actionLoading === `recycle-confirm`"
              :disabled="!recycleDialog.doll || recycleMax <= 0 || isBusy"
              @click="recycleDoll"
            >
              确认回收
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </div>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'

const props = defineProps({
  api: { type: Object, required: true },
  initialConfig: { type: Object, default: () => ({}) },
})

const emit = defineEmits(['switch', 'close'])
const pluginBase = '/plugin/VueToy'

const status = reactive({ toy_status: {}, history: [] })
const message = reactive({ text: '', type: 'success' })
const initialLoading = ref(true)
const actionLoading = ref('')
const targetKeyword = ref('')
const selectedDollKey = ref('')
const transientTargetPanel = ref({})
const buyQuantities = reactive({})
const openQuantities = reactive({})
const recycleDialog = reactive({ open: false, doll: null, quantity: 1 })
const nowTs = ref(Math.floor(Date.now() / 1000))
const lastAutoRefreshKey = ref('')

let timer = null

const isBusy = computed(() => !!actionLoading.value)
const toy = computed(() => status.toy_status || {})
const overviewCards = computed(() => toy.value.overview || [])
const personalSlots = computed(() => toy.value.personal_slots || [])
const cabinetCards = computed(() => {
  const items = [...(toy.value.cabinet || [])]
  return items.sort((left, right) => {
    const leftAvailable = Number(left.available || 0)
    const rightAvailable = Number(right.available || 0)
    if (!!rightAvailable !== !!leftAvailable) return rightAvailable ? 1 : -1
    const leftReady = Number(left.cooldown_until_ts || Number.MAX_SAFE_INTEGER)
    const rightReady = Number(right.cooldown_until_ts || Number.MAX_SAFE_INTEGER)
    if (leftReady !== rightReady) return leftReady - rightReady
    return String(left.name || '').localeCompare(String(right.name || ''))
  })
})
const shopBoxes = computed(() => toy.value.shop_boxes || [])
const myBoxes = computed(() => toy.value.my_boxes || [])
const remoteRecords = computed(() => toy.value.remote_records || [])
const activityLogs = computed(() => toy.value.history_logs || [])
const summaryLines = computed(() => (toy.value.summary || []).filter(Boolean))
const placementGuard = computed(() => toy.value.placement_guard || {})
const placementGuardText = computed(() => {
  const hours = Number(
    placementGuard.value.threshold_hours
      ?? placementGuard.value.guard_hours
      ?? placementGuard.value.hours
      ?? status.config?.self_slot_guard_hours
      ?? 1,
  )
  return placementGuard.value.text
    || placementGuard.value.status_text
    || placementGuard.value.message
    || (placementGuard.value.active
      ? `有自己展位将在 ${hours} 小时内到期，暂缓外展`
      : `自己展位到期前 ${hours} 小时自动保留可用玩偶`)
})
const targetPanel = computed(() => {
  if (transientTargetPanel.value?.slots?.length) return transientTargetPanel.value
  return toy.value.target_panel || {}
})
const selectedDoll = computed(() => cabinetCards.value.find((item) => item.doll_key === selectedDollKey.value) || null)
const ownedPersonalCount = computed(() => personalSlots.value.filter((slot) => slot.viewer_is_occupant).length)
const recycleMax = computed(() => Math.max(0, Math.floor(Number(recycleDialog.doll?.idle ?? recycleDialog.doll?.recycle_max ?? 0))))
const recycleEstimate = computed(() => {
  const quantity = Math.min(
    recycleMax.value,
    Math.max(1, Math.floor(Number(recycleDialog.quantity || 1))),
  )
  return quantity * Math.max(0, Number(recycleDialog.doll?.recycle_value || 0))
})
const nextRunTs = computed(() => Number(toy.value.next_run_ts || 0) || parseDateTime(toy.value.next_run_time))
const nextTriggerTs = computed(() => Number(toy.value.next_trigger_ts || 0) || parseDateTime(toy.value.next_trigger_time))

watch(shopBoxes, (items) => {
  items.forEach((item) => {
    if (!buyQuantities[item.box_key]) buyQuantities[item.box_key] = String(item.default_quantity || 1)
  })
}, { immediate: true })

watch(myBoxes, (items) => {
  items.forEach((item) => {
    const key = item.box_key || item.name
    if (!openQuantities[key]) openQuantities[key] = String(item.default_quantity || 1)
  })
}, { immediate: true })

watch(cabinetCards, (items) => {
  if (selectedDollKey.value && !items.some((item) => item.doll_key === selectedDollKey.value && item.can_place)) {
    selectedDollKey.value = ''
  }
})

function statTone(index) {
  return ['orange', 'blue', 'green', 'red'][index % 4]
}

function statIcon(index) {
  return ['mdi-star-four-points-outline', 'mdi-eye-outline', 'mdi-cash-multiple', 'mdi-storefront-outline'][index % 4]
}

function flash(text, type = 'success') {
  message.text = text
  message.type = type
}

function parseDateTime(value) {
  if (!value || typeof value !== 'string') return 0
  const match = value.match(/^(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})$/)
  if (!match) return 0
  const [, year, month, day, hour, minute, second] = match
  return Math.floor(new Date(Number(year), Number(month) - 1, Number(day), Number(hour), Number(minute), Number(second)).getTime() / 1000)
}

function formatDuration(seconds) {
  const total = Math.max(0, Math.floor(Number(seconds) || 0))
  if (total <= 0) return '现在可收回'
  const days = Math.floor(total / 86400)
  const hours = Math.floor((total % 86400) / 3600)
  const minutes = Math.floor((total % 3600) / 60)
  const secs = total % 60
  if (days) return `${days}天${hours}小时`
  if (hours) return `${hours}小时${minutes}分钟`
  if (minutes) return `${minutes}分钟${secs}秒`
  return `${secs}秒`
}

function liveRemaining(item = {}) {
  const endTs = Number(item.remaining_end_ts || 0)
  if (endTs > 0) return Math.max(0, endTs - nowTs.value)
  return Math.max(0, Number(item.remaining_seconds || 0))
}

function slotRemainText(slot = {}) {
  if (!slot.viewer_is_occupant && !slot.empty) return slot.status_text || '正在展出'
  const remain = liveRemaining(slot)
  if (slot.viewer_is_occupant && (slot.can_collect || remain <= 0)) return '现在可收回'
  return `距完成 ${formatDuration(remain)}`
}

function remoteRemainText(item = {}) {
  const remain = liveRemaining(item)
  return remain <= 0 ? '现在可收回' : `距完成 ${formatDuration(remain)}`
}

function cabinetCooldownText(doll = {}) {
  const cooling = Number(doll.cooling_count || 0)
  if (!cooling) return ''
  const endTs = Number(doll.cooldown_until_ts || 0)
  if (!endTs) return doll.cooldown_text || `冷却中 ×${cooling}`
  const remain = Math.max(0, endTs - nowTs.value)
  return `冷却中 ×${cooling} · 最快 ${formatDuration(remain)}`
}

function slotKind(slot = {}) {
  if (slot.empty) return slot.cooldown_active ? 'cooldown' : 'empty'
  if (!slot.viewer_is_occupant) return 'blocked'
  if (slot.can_collect || liveRemaining(slot) <= 0) return 'ready'
  return 'early'
}

function slotBadge(slot = {}) {
  const kind = slotKind(slot)
  if (kind === 'ready') return '可收回'
  if (kind === 'early') return '展出中'
  if (kind === 'blocked') return '他人占用'
  if (kind === 'cooldown') return '冷却中'
  return '空位'
}

function slotTone(slot = {}) {
  const kind = slotKind(slot)
  if (kind === 'ready') return 'success'
  if (kind === 'early') return 'orange'
  if (kind === 'empty') return 'blue'
  return 'grey'
}

function applyPayload(payload = {}) {
  if (payload.status?.toy_status) {
    Object.assign(status, payload.status)
  } else if (payload.toy_status || payload.history || payload.config) {
    Object.assign(status, payload)
  }
  if (payload.toy_status && !payload.status) status.toy_status = payload.toy_status
  if (payload.target_panel) transientTargetPanel.value = payload.target_panel
}

async function loadStatus(showError = true) {
  try {
    const data = await props.api.get(`${pluginBase}/status`)
    Object.assign(status, data || {})
    return true
  } catch (error) {
    if (showError) flash(error?.message || '加载状态失败', 'error')
    return false
  } finally {
    initialLoading.value = false
  }
}

async function withAction(key, action, fallback) {
  actionLoading.value = key
  try {
    const result = await action()
    applyPayload(result || {})
    await loadStatus(false)
    window.setTimeout(() => void loadStatus(false), 1200)
    flash(result?.message || fallback)
    return result
  } catch (error) {
    flash(error?.message || fallback, 'error')
    return null
  } finally {
    actionLoading.value = ''
  }
}

function refreshData() {
  return withAction('refresh', () => props.api.post(`${pluginBase}/refresh`), '状态已刷新')
}

function runNow() {
  return withAction('run', () => props.api.post(`${pluginBase}/run`), '执行完成')
}

function buyBox(box) {
  return withAction(
    `buy-${box.box_key}`,
    () => props.api.post(`${pluginBase}/buy-box`, { box_key: box.box_key, quantity: Number(buyQuantities[box.box_key] || 1) }),
    '购买完成',
  )
}

function openBox(box) {
  const key = box.box_key || box.name
  return withAction(
    `open-${box.box_key}`,
    () => props.api.post(`${pluginBase}/open-box`, { box_key: box.box_key, quantity: Number(openQuantities[key] || 1) }),
    '开启完成',
  )
}

function openRecycleDialog(doll) {
  if (!doll?.can_recycle || Number(doll.idle || 0) <= 0 || isBusy.value) return
  recycleDialog.doll = doll
  recycleDialog.quantity = 1
  recycleDialog.open = true
}

function recycleDoll() {
  const doll = recycleDialog.doll
  if (!doll || recycleMax.value <= 0) return null
  const quantity = Math.min(
    recycleMax.value,
    Math.max(1, Math.floor(Number(recycleDialog.quantity || 1))),
  )
  return withAction(
    'recycle-confirm',
    () => props.api.post(pluginBase + '/recycle-doll', {
      doll_key: doll.doll_key,
      quantity,
    }),
    '回收完成',
  ).then((result) => {
    if (result) recycleDialog.open = false
    return result
  })
}

function selectDoll(doll) {
  if (!doll.can_place) return
  selectedDollKey.value = selectedDollKey.value === doll.doll_key ? '' : doll.doll_key
}

function collectSlot(slot) {
  return withAction(
    `collect-${slot.owner_id}-${slot.slot_index}`,
    () => props.api.post(`${pluginBase}/collect-slot`, { owner_id: slot.owner_id, slot_index: slot.slot_index }),
    '收回完成',
  )
}

function placePersonal(slot) {
  if (!selectedDoll.value) return null
  return withAction(
    `place-personal-${slot.slot_index}`,
    () => props.api.post(`${pluginBase}/place-personal`, {
      owner_id: slot.owner_id,
      slot_index: slot.slot_index,
      doll_key: selectedDoll.value.doll_key,
      doll_name: selectedDoll.value.name,
    }),
    '自己展位上架完成',
  )
}

function randomTarget() {
  return withAction('random-target', () => props.api.post(`${pluginBase}/random-target`), '已匹配目标')
}

function viewTarget(ownerId = null) {
  const keyword = ownerId ?? targetKeyword.value.trim()
  return withAction('view-target', () => props.api.post(`${pluginBase}/view-target`, { keyword }), '已加载目标展台')
}

function placeTarget(slot) {
  if (!selectedDoll.value) return null
  return withAction(
    `place-target-${slot.slot_index}`,
    () => props.api.post(`${pluginBase}/place-target`, {
      owner_id: slot.owner_id,
      slot_index: slot.slot_index,
      doll_key: selectedDoll.value.doll_key,
      doll_name: selectedDoll.value.name,
    }),
    '外展完成',
  )
}

async function maybeRefreshAfterSchedule() {
  const due = [nextTriggerTs.value, nextRunTs.value].filter((value) => value > 0 && nowTs.value >= value)
  if (!due.length || isBusy.value) return
  const key = due.join('-')
  if (key === lastAutoRefreshKey.value) return
  lastAutoRefreshKey.value = key
  await loadStatus(false)
}

onMounted(async () => {
  await loadStatus(true)
  timer = window.setInterval(() => {
    nowTs.value = Math.floor(Date.now() / 1000)
    void maybeRefreshAfterSchedule()
  }, 1000)
})

onBeforeUnmount(() => {
  if (timer) window.clearInterval(timer)
})
</script>

<style scoped>
.siqi-page { padding: 16px 20px; display: flex; flex-direction: column; gap: 16px; min-height: 400px; overflow-x: hidden; font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Inter', sans-serif; color: rgba(var(--v-theme-on-surface), .85); border: 1px solid rgba(var(--v-theme-on-surface), .12); border-radius: 8px; background: linear-gradient(180deg, rgba(255,255,255,.02), rgba(76,175,80,.025)); }
.siqi-page,
.siqi-page * { box-sizing: border-box; }
.siqi-page :deep(.v-btn) { min-height: 44px; transition: transform .16s ease, box-shadow .16s ease, filter .16s ease, opacity .16s ease; }
.siqi-page :deep(.v-btn:not(.v-btn--disabled):hover) { transform: translateY(-1px); box-shadow: 0 6px 16px rgba(15,23,42,.12); filter: saturate(1.05); }
.siqi-page :deep(.v-btn:not(.v-btn--disabled):active) { transform: translateY(0) scale(.98); }
.siqi-page :deep(.v-btn.v-btn--disabled) { cursor: not-allowed; opacity: .55; }

.siqi-content { display: flex; flex-direction: column; gap: 0; }
.siqi-topbar { display: flex; align-items: center; justify-content: space-between; gap: 16px; padding-bottom: 8px; }
.siqi-topbar__left { gap: 12px; min-width: 0; flex: 1; }
.siqi-topbar__left { display: flex; align-items: center; }
.siqi-topbar__right { display: flex; align-items: center; flex-shrink: 0; }
.siqi-topbar__right :deep(.v-btn-group) { flex-wrap: nowrap; }
.siqi-topbar__copy { min-width: 0; }
.siqi-topbar__icon { width: 42px; height: 42px; border-radius: 11px; background: rgba(76,175,80,.14); display: flex; align-items: center; justify-content: center; color: #2e7d32; flex-shrink: 0; }
.siqi-topbar__title { font-size: 16px; font-weight: 700; letter-spacing: -.3px; color: rgba(var(--v-theme-on-surface), .88); }
.siqi-topbar__sub { font-size: 11px; color: rgba(var(--v-theme-on-surface), .55); margin-top: 2px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.siqi-toast {
  position: fixed !important;
  top: 18px !important;
  left: 50% !important;
  z-index: 99999 !important;
  width: min(520px, calc(100vw - 32px)) !important;
  margin: 0 !important;
  border-radius: 12px !important;
  box-shadow: 0 12px 36px rgba(15,23,42,.18) !important;
  transform: translateX(-50%) !important;
}
.loading-state {
  display: grid;
  gap: 12px;
  padding: 28px 18px;
  border: .5px solid rgba(var(--v-theme-on-surface), .08);
  border-radius: 14px;
  color: rgba(var(--v-theme-on-surface), .68);
  background: rgba(var(--v-theme-on-surface), .03);
  backdrop-filter: blur(20px) saturate(150%);
  box-shadow: 0 2px 10px rgba(0,0,0,.05);
}

.stat-card { --stat-rgb: 76,175,80; --stat-color: #2e7d32; min-height: 78px; border-radius: 14px; padding: 12px 14px; border: .5px solid rgba(var(--v-theme-on-surface), .08); background: rgba(var(--v-theme-on-surface), .03); box-shadow: inset 0 1px 0 rgba(var(--v-theme-surface), .2), 0 2px 12px rgba(var(--v-theme-on-surface), .08); display: flex; align-items: center; gap: 12px; }
.stat-icon { width: 38px; height: 38px; border-radius: 12px; display: flex; align-items: center; justify-content: center; background: rgba(var(--stat-rgb), .14); color: var(--stat-color); flex: 0 0 38px; }
.stat-content { min-width: 0; }
.stat-title { font-size: 11px; font-weight: 600; color: rgba(var(--v-theme-on-surface), .55); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.stat-value { margin-top: 2px; font-size: 20px; font-weight: 800; letter-spacing: -.5px; color: rgba(var(--v-theme-on-surface), .88); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.stat-orange { --stat-rgb: 245,158,11; --stat-color: #f59e0b; background: rgba(245,158,11,.12); border-color: rgba(245,158,11,.24); }
.stat-green { --stat-rgb: 16,185,129; --stat-color: #10b981; background: rgba(16,185,129,.12); border-color: rgba(16,185,129,.24); }
.stat-blue { --stat-rgb: 59,130,246; --stat-color: #3b82f6; background: rgba(59,130,246,.12); border-color: rgba(59,130,246,.24); }
.stat-red { --stat-rgb: 239,68,68; --stat-color: #ef4444; background: rgba(239,68,68,.12); border-color: rgba(239,68,68,.24); }
.stat-orange .stat-icon, .stat-orange .stat-title, .stat-orange .stat-value { color: #f59e0b; }
.stat-green .stat-icon, .stat-green .stat-title, .stat-green .stat-value { color: #10b981; }
.stat-blue .stat-icon, .stat-blue .stat-title, .stat-blue .stat-value { color: #3b82f6; }
.stat-red .stat-icon, .stat-red .stat-title, .stat-red .stat-value { color: #ef4444; }
.overview-grid { display: grid !important; grid-template-columns: repeat(4, minmax(0, 1fr)); gap: 8px; margin: 0 0 12px !important; }
.overview-grid > * { width: auto !important; max-width: none !important; padding: 0 !important; }
.interaction-grid { display: grid; grid-template-columns: 1fr; gap: 12px; align-items: stretch; }
.interaction-grid > .siqi-card { height: 100%; margin-bottom: 0 !important; }
.personal-booth-card { display: flex !important; flex-direction: column; margin-bottom: 12px !important; }
.personal-booth-body { display: flex; flex: 1; }
.personal-booth-card .slot-grid { width: 100%; }

.siqi-card { background: rgba(var(--v-theme-on-surface), .03) !important; backdrop-filter: blur(20px) saturate(150%); border-radius: 14px !important; border: .5px solid rgba(var(--v-theme-on-surface), .08) !important; box-shadow: 0 2px 10px rgba(0,0,0,.05) !important; overflow: hidden; }
.siqi-card-title { min-height: 44px; padding: 10px 16px !important; font-size: 13px !important; font-weight: 700 !important; background: rgba(76,175,80,.08); border-bottom: .5px solid rgba(var(--v-theme-on-surface), .07); color: rgba(var(--v-theme-on-surface), .84); }
.siqi-card-title :deep(.v-spacer) { flex: 1 1 auto !important; }
.personal-booth-card .siqi-card-title { background: rgba(245,158,11,.09); }
.cabinet-card .siqi-card-title { background: rgba(59,130,246,.09); }
.box-card .siqi-card-title { background: rgba(251,146,60,.10); }
.target-card .siqi-card-title { background: rgba(239,68,68,.08); }
.remote-card .siqi-card-title { background: rgba(6,182,212,.09); }
.activity-card .siqi-card-title { background: rgba(59,130,246,.09); }
.section-count { color: rgba(var(--v-theme-on-surface), .6); font-size: .74rem; font-weight: 500; }

.next-run-card { margin-bottom: 12px !important; }
.next-run-body { display: flex; align-items: center; gap: 12px; min-height: 72px; padding: 10px 14px !important; background: rgba(76,175,80,.08); }
.next-run-icon { display: grid; place-items: center; width: 40px; height: 40px; flex: 0 0 40px; border-radius: 12px; color: #16a34a; background: rgba(34,197,94,.13); }
.next-run-copy { min-width: 0; flex: 1 1 auto; }
.next-run-title { font-size: .88rem; font-weight: 750; }
.next-run-sub, .next-run-guard { margin-top: 2px; color: rgba(var(--v-theme-on-surface), .58); font-size: .7rem; line-height: 1.35; }
.next-run-guard { color: #d97706; }
.next-run-times { display: flex; align-items: center; justify-content: flex-end; flex-wrap: wrap; gap: 7px; }
.next-run-time { display: grid; gap: 1px; min-width: 142px; text-align: right; }
.next-run-time span { color: rgba(var(--v-theme-on-surface), .52); font-size: .64rem; }
.next-run-time strong { color: rgba(var(--v-theme-on-surface), .86); font-size: .72rem; font-weight: 700; font-variant-numeric: tabular-nums; white-space: nowrap; }

.schedule-run-btn { min-height: 32px !important; height: 32px !important; border-radius: 999px !important; font-size: 11px !important; font-weight: 700; letter-spacing: 0; }
.summary-alert { margin-top: 2px; font-size: .78rem; }

.slot-grid,
.doll-grid,
.remote-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 10px;
}
.slot-card,
.doll-card,
.remote-row {
  min-width: 0;
  border: 1px solid rgba(var(--v-theme-on-surface), .07);
  border-radius: 14px;
  background: rgba(var(--v-theme-surface), .68);
}
.slot-card { display: flex; flex-direction: column; gap: 9px; padding: 11px; }
.slot-card--ready { border-color: rgba(34, 197, 94, .5); background: rgba(34, 197, 94, .055); }
.slot-card--blocked { opacity: .82; }
.slot-card__head,
.doll-card__head,
.doll-stats {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
}
.slot-card__head { font-size: .8rem; font-weight: 700; }
.slot-main { display: flex; align-items: center; gap: 10px; min-height: 70px; }
.slot-image,
.remote-image {
  flex: 0 0 auto;
  width: 58px;
  height: 58px;
  border-radius: 13px;
  object-fit: contain;
  background: rgba(var(--v-theme-on-surface), .05);
}
.slot-image--placeholder,
.remote-image--placeholder,
.doll-image--placeholder,
.box-image--placeholder { display: grid; place-items: center; color: rgba(var(--v-theme-on-surface), .42); }
.slot-info { min-width: 0; }
.slot-name { overflow-wrap: anywhere; font-size: .93rem; font-weight: 750; }
.slot-owner { margin-top: 2px; color: rgba(var(--v-theme-on-surface), .62); font-size: .72rem; }
.slot-meta { margin-top: 3px; color: rgba(var(--v-theme-on-surface), .68); font-size: .72rem; line-height: 1.35; }
.slot-empty-body { display: grid; place-items: center; gap: 4px; min-height: 112px; text-align: center; color: rgba(var(--v-theme-on-surface), .58); }
.slot-empty-body strong { color: rgb(var(--v-theme-on-surface)); font-size: .9rem; }
.slot-empty-body span { font-size: .72rem; line-height: 1.4; }
.slot-progress { height: 5px; overflow: hidden; border-radius: 999px; background: rgba(var(--v-theme-on-surface), .08); }
.slot-progress__bar { height: 100%; border-radius: inherit; background: linear-gradient(90deg, #22c55e, #16a34a); transition: width .25s ease; }
.card-action { min-height: 44px; margin-top: auto; }
.doll-actions { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 7px; margin-top: auto; }
.doll-actions :deep(.v-btn) { min-width: 0; }

.selection-strip {
  display: flex;
  align-items: center;
  gap: 8px;
  min-height: 44px;
  margin-bottom: 10px;
  padding: 7px 10px;
  border-radius: 12px;
  color: rgba(var(--v-theme-on-surface), .66);
  background: rgba(var(--v-theme-on-surface), .04);
  font-size: .77rem;
}
.selection-strip span { flex: 1 1 auto; min-width: 0; }
.selection-strip--active { color: #2563eb; background: rgba(59, 130, 246, .1); }
.doll-grid { grid-template-columns: repeat(auto-fit, minmax(175px, 1fr)); }
.doll-card { display: flex; flex-direction: column; gap: 7px; padding: 10px; transition: border-color .18s ease, transform .18s ease, background .18s ease; }
.doll-card--selected { border-color: rgba(59, 130, 246, .7); background: rgba(59, 130, 246, .07); transform: translateY(-1px); }
.doll-card--disabled { opacity: .72; }
.doll-card__head { min-height: 22px; color: rgba(var(--v-theme-on-surface), .55); font-size: .65rem; }
.doll-image { width: 100%; height: 82px; object-fit: contain; border-radius: 12px; background: rgba(var(--v-theme-on-surface), .035); }
.doll-name { overflow-wrap: anywhere; font-size: .88rem; font-weight: 750; text-align: center; }
.doll-meta { color: rgba(var(--v-theme-on-surface), .62); font-size: .68rem; line-height: 1.35; text-align: center; }
.doll-stats { color: rgba(var(--v-theme-on-surface), .7); font-size: .66rem; }
.doll-cooldown { min-height: 32px; color: #d97706; font-size: .67rem; line-height: 1.35; text-align: center; }

.two-column-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 12px; }
.box-list,
.activity-list { display: grid; gap: 8px; }
.box-row {
  display: grid;
  grid-template-columns: 48px minmax(0, 1fr) 72px auto;
  align-items: center;
  gap: 9px;
  min-height: 66px;
  padding: 8px;
  border: 1px solid rgba(var(--v-theme-on-surface), .07);
  border-radius: 12px;
  background: rgba(var(--v-theme-surface), .68);
}
.box-row--locked { opacity: .65; }
.box-image { width: 48px; height: 48px; border-radius: 11px; object-fit: contain; background: rgba(var(--v-theme-on-surface), .04); }
.box-copy { min-width: 0; }
.box-name { font-size: .82rem; font-weight: 700; }
.box-desc { margin-top: 2px; color: rgba(var(--v-theme-on-surface), .6); font-size: .67rem; line-height: 1.35; }
.quantity-field { min-width: 0; }
.quantity-field :deep(.v-field__input) { min-height: 40px; padding-inline: 8px; text-align: center; }

.target-tools { display: grid; grid-template-columns: minmax(220px, 1fr) auto auto; gap: 9px; margin-bottom: 11px; }
.remote-grid { grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); }
.remote-row { display: grid; grid-template-columns: 50px minmax(0, 1fr) auto; align-items: center; gap: 9px; padding: 9px; }
.remote-image { width: 50px; height: 50px; }
.remote-copy { min-width: 0; }
.remote-name { font-size: .82rem; font-weight: 700; }
.remote-meta { margin-top: 2px; color: rgba(var(--v-theme-on-surface), .6); font-size: .68rem; }

.activity-row {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  min-height: 44px;
  padding: 9px 10px;
  border: 1px solid rgba(var(--v-theme-on-surface), .06);
  border-radius: 11px;
  background: rgba(var(--v-theme-surface), .68);
  font-size: .73rem;
  line-height: 1.45;
}
.activity-row span { min-width: 0; overflow-wrap: anywhere; }
.activity-row time {
  flex: 0 0 auto;
  margin-left: auto;
  color: rgba(var(--v-theme-on-surface), .52);
  font-size: .67rem;
  font-variant-numeric: tabular-nums;
  text-align: right;
  white-space: nowrap;
}
.recycle-dialog-card { overflow: hidden; }
.recycle-dialog-name { font-size: 1rem; font-weight: 750; }
.recycle-dialog-hint { margin: 6px 0 14px; color: rgba(var(--v-theme-on-surface), .58); font-size: .72rem; line-height: 1.45; }
.recycle-quantity :deep(.v-field__input) { min-height: 42px; text-align: center; }
.recycle-estimate { margin-top: 10px; color: #d97706; font-size: .78rem; font-weight: 700; }
.empty-state { padding: 22px 12px; color: rgba(var(--v-theme-on-surface), .52); font-size: .78rem; text-align: center; }

@media (hover: hover) {
  .doll-card:not(.doll-card--disabled):hover { border-color: rgba(59, 130, 246, .5); transform: translateY(-1px); }
}

@media (prefers-reduced-motion: reduce) {
  .doll-card,
  .slot-progress__bar { transition: none; }
}

@media (min-width: 1101px) {
  .interaction-grid .target-body,
  .interaction-grid .remote-body { max-height: 430px; overflow-y: auto; }
}

@media (max-width: 900px) {
  .overview-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .two-column-grid { grid-template-columns: 1fr; }
  .target-tools { grid-template-columns: 1fr 1fr; }
  .target-tools :deep(.v-input) { grid-column: 1 / -1; }
}

@media (max-width: 720px) {
  .slot-grid,
  .doll-grid,
  .remote-grid { grid-template-columns: 1fr; }
  .box-row { grid-template-columns: 44px minmax(0, 1fr) 64px; }
  .box-image { width: 44px; height: 44px; }
  .box-row > .v-btn { grid-column: 2 / -1; width: 100%; min-height: 44px; }
  .target-tools { grid-template-columns: 1fr; }
  .target-tools :deep(.v-input) { grid-column: auto; }
  .target-tools .v-btn { min-height: 44px; }
  .next-run-body { align-items: flex-start; flex-wrap: wrap; }
  .next-run-copy { flex-basis: calc(100% - 52px); }
  .next-run-times { width: 100%; justify-content: flex-start; padding-left: 52px; }
  .next-run-time { min-width: 0; flex: 1 1 160px; text-align: left; }
  .next-run-time strong { white-space: normal; }
}

@media (max-width: 600px) {
  .siqi-page { padding: 14px; }
  .siqi-topbar { align-items: flex-start; gap: 10px; }
  .siqi-topbar__left { min-width: 0; }
  .siqi-topbar__right :deep(.v-btn) { min-width: 44px !important; padding-inline: 0 !important; }
  .overview-grid > .v-col { padding: 4px !important; }
  .stat-card { padding: 10px; gap: 8px; }
  .stat-icon { width: 34px; height: 34px; flex-basis: 34px; }
  .stat-value { font-size: 17px; }
  .section-count { display: none; }
  .next-run-times { padding-left: 0; }
  .next-run-times .v-chip { display: none; }
  .next-run-time { flex-basis: 100%; }
  .doll-actions { grid-template-columns: 1fr 1fr; }
}
</style>
