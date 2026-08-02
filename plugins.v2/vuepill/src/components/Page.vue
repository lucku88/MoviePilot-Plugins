<template>
  <div class="siqi-page">
    <div class="siqi-topbar">
      <div class="siqi-topbar__left">
        <div class="siqi-topbar__icon">
          <v-icon icon="mdi-flask-round-bottom" size="24" />
        </div>
        <div class="siqi-topbar__copy">
          <div class="siqi-topbar__title">Vue-魔丸</div>
          <div class="siqi-topbar__sub">搬砖、清理沙滩、兑换、赠送与炼造</div>
        </div>
      </div>
      <div class="siqi-topbar__right">
        <v-btn-group variant="tonal" density="compact" class="elevation-0">
          <v-btn
            color="success"
            size="small"
            class="px-0 px-sm-3"
            min-width="40"
            aria-label="刷新 Vue-魔丸状态"
            :loading="actionLoading === 'refresh'"
            :disabled="writeActionsDisabled"
            @click="refreshData"
          >
            <v-icon icon="mdi-refresh" size="18" class="mr-sm-1" />
            <span class="d-none d-sm-inline">刷新</span>
          </v-btn>
          <v-btn
            color="success"
            size="small"
            class="px-0 px-sm-3"
            min-width="40"
            aria-label="打开 Vue-魔丸配置"
            :disabled="isBusy"
            @click="emit('switch', 'config')"
          >
            <v-icon icon="mdi-cog" size="18" class="mr-sm-1" />
            <span class="d-none d-sm-inline">配置</span>
          </v-btn>
          <v-btn
            color="success"
            size="small"
            class="px-0 px-sm-3"
            min-width="40"
            aria-label="关闭 Vue-魔丸"
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

      <div v-if="initialLoading" class="page-skeleton">
        <v-row dense class="mb-3">
          <v-col v-for="index in 4" :key="`overview-skeleton-${index}`" cols="6" md="3">
            <div class="stat-card skeleton-card"><div class="sk sk-icon" /><div class="sk-lines"><div class="sk sk-line short" /><div class="sk sk-line" /></div></div>
          </v-col>
        </v-row>
        <v-card flat class="siqi-card schedule-board mb-3 skeleton-shell">
          <v-card-title class="siqi-card-title"><div class="sk sk-title" /></v-card-title>
          <v-card-text class="schedule-board-body">
            <div v-for="index in 2" :key="`schedule-skeleton-${index}`" class="sk sk-action" />
          </v-card-text>
        </v-card>
        <div v-for="index in 4" :key="`panel-skeleton-${index}`" class="siqi-card skeleton-panel mb-3"><div class="sk sk-title" /><div class="sk sk-row" /><div class="sk sk-row" /></div>
      </div>

      <template v-else>
        <v-row dense class="mb-3 overview-grid">
          <v-col v-for="item in overview" :key="item.label" cols="6" md="3">
            <div class="stat-card" :class="`stat-${overviewTone(item)}`">
              <div class="stat-icon">
                <v-icon :icon="overviewIcon(item)" size="22" />
              </div>
              <div class="stat-content">
                <div class="stat-title">{{ item.label }}</div>
                <div class="stat-value">{{ item.value }}</div>
              </div>
            </div>
          </v-col>
        </v-row>

        <div class="primary-grid mb-3">
          <v-card flat class="siqi-card schedule-board mb-3">
            <v-card-title class="siqi-card-title d-flex align-center">
              <v-icon icon="mdi-calendar-clock" class="mr-2" color="green" />动态任务
              <span class="card-subtitle">搬砖与沙滩</span>
            </v-card-title>
            <v-card-text class="schedule-board-body">
              <div class="schedule-action-list">
                <div class="neu-action-card neu-action-card--brick">
                  <div class="neu-action-icon"><v-icon icon="mdi-wall" size="19" /></div>
                  <div class="neu-action-content">
                    <div class="neu-action-heading">
                      <div class="neu-action-label">搬砖</div>
                      <span
                        class="schedule-status"
                        :class="{
                          'schedule-status--ready': brick.ready === true,
                          'schedule-status--done': brickStatusLabel === '今日已完成',
                        }"
                      >{{ brickStatusLabel }}</span>
                    </div>
                    <div class="neu-action-desc">{{ brick.status_text || '等待刷新搬砖状态' }}</div>
                    <div class="schedule-meta">
                      <span>今日 {{ brick.daily_bricks ?? 0 }}/{{ brick.daily_limit ?? 50 }}</span>
                      <span>可搬 {{ brick.available_count ?? 0 }}</span>
                      <span>重置 {{ brick.next_reset_time || '等待刷新' }}</span>
                    </div>
                  </div>
                  <v-btn
                    color="deep-orange"
                    size="small"
                    class="neu-btn schedule-action"
                    :loading="actionLoading === 'brick'"
                    :disabled="writeActionsDisabled || brick.ready !== true"
                    @click="moveBricks"
                  >立即搬砖</v-btn>
                </div>

                <div class="neu-action-card neu-action-card--beach">
                  <div class="neu-action-icon"><v-icon icon="mdi-beach" size="19" /></div>
                  <div class="neu-action-content">
                    <div class="neu-action-heading">
                      <div class="neu-action-label">沙滩</div>
                      <span
                        class="schedule-status"
                        :class="{
                          'schedule-status--ready': beachActionable,
                          'schedule-status--cooldown': beachStatusLabel === '冷却中',
                        }"
                      >{{ beachStatusLabel }}</span>
                    </div>
                    <div class="neu-action-desc">{{ beach.status_text || '等待刷新沙滩状态' }}</div>
                    <div class="schedule-meta">
                      <span>{{ beach.level_text || '等级待刷新' }}</span>
                      <span>{{ beach.hnr_text || 'HNR 待刷新' }}</span>
                      <span>可用 {{ beach.next_ready_time || '等待刷新' }}</span>
                    </div>
                  </div>
                  <v-btn
                    color="teal"
                    size="small"
                    class="neu-btn schedule-action"
                    :loading="actionLoading === 'beach'"
                    :disabled="writeActionsDisabled || !beachActionable"
                    @click="cleanBeach"
                  >清理沙滩</v-btn>
                </div>
              </div>
            </v-card-text>
          </v-card>

          <v-card flat class="siqi-card exchange-card mb-3">
          <v-card-title class="siqi-card-title siqi-card-title--exchange d-flex align-center">
            <v-icon icon="mdi-swap-horizontal-circle" class="mr-2" color="amber-darken-2" />兑换魔力
          </v-card-title>
          <v-card-text class="exchange-body">
            <div class="exchange-summary">
              <div class="exchange-stat"><span>当前魔丸</span><strong>{{ exchange.magic_pills ?? 0 }}</strong></div>
              <div class="exchange-stat"><span>单颗价值</span><strong>{{ exchange.pill_price ?? 0 }}</strong><small>魔力</small></div>
              <div class="exchange-stat"><span>后端上限</span><strong>{{ exchange.max_count ?? 0 }}</strong><small>颗</small></div>
            </div>
            <div class="exchange-action-panel">
              <v-text-field
                v-model="exchangeQuantity"
                type="number"
                min="1"
                :max="exchange.max_count"
                label="兑换数量"
                variant="outlined"
                density="compact"
                :error-messages="exchangeQuantityError ? [exchangeQuantityError] : []"
              />
              <v-btn
                color="amber-darken-2"
                variant="tonal"
                :loading="actionLoading === 'exchange'"
                :disabled="writeActionsDisabled || exchange.enabled !== true || exchange.action_ready !== true || !!exchangeQuantityError"
                @click="exchangePoints"
              >兑换魔力</v-btn>
            </div>
          </v-card-text>
          </v-card>
        </div>

        <div class="resource-grid mb-3">
          <v-card flat class="siqi-card inventory-card">
          <v-card-title class="siqi-card-title siqi-card-title--inventory d-flex align-center">
            <v-icon icon="mdi-package-variant-closed" class="mr-2" color="orange" />物品栏
            <v-spacer />
            <div class="inventory-title-actions">
              <v-btn
                color="orange-darken-1"
                variant="tonal"
                prepend-icon="mdi-gift-open-outline"
                aria-label="打开批量赠送"
                :disabled="writeActionsDisabled || !batchGiftableItems.length"
                @click="openBatchGiftDialog"
              >批量赠送</v-btn>
              <v-btn
                color="blue"
                variant="tonal"
                prepend-icon="mdi-chart-box-outline"
                aria-label="查看赠送统计"
                :loading="giftStatsLoading"
                :disabled="initialLoading || giftStatsLoading"
                @click="openGiftStats"
              >赠送统计</v-btn>
            </div>
          </v-card-title>
          <v-card-text class="inventory-body">
            <div v-if="!inventoryItems.length" class="empty-state">
              <v-icon icon="mdi-package-variant" size="34" />
              <strong>物品栏暂无内容</strong>
              <small>刷新后仍为空时，请以后端页面数据为准。</small>
            </div>
            <div v-else class="inventory-grid">
              <button
                v-for="item in inventoryItems"
                :key="item.name"
                type="button"
                class="gift-item"
                :class="{ 'gift-item--available': canGiftItem(item) }"
                :disabled="!canGiftItem(item)"
                :aria-label="canGiftItem(item) ? `赠送 ${item.name}` : `${item.name} 当前不可赠送`"
                @click="openGiftDialog(item)"
              >
                <span class="gift-item__icon">{{ item.icon || '📦' }}</span>
                <span class="gift-item__main">
                  <strong>{{ item.name }}</strong>
                  <small>数量 {{ item.count ?? 0 }}</small>
                </span>
                <span class="gift-item__state">{{ canGiftItem(item) ? '点击赠送' : '不可赠送' }}</span>
              </button>
            </div>
          </v-card-text>
          </v-card>

          <v-card flat class="siqi-card workshop-card">
          <v-card-title class="siqi-card-title siqi-card-title--workshop d-flex align-center">
            <v-icon icon="mdi-anvil" class="mr-2" color="cyan-darken-1" />炼造工坊
            <v-spacer />
            <v-btn
              color="cyan-darken-1"
              variant="tonal"
              prepend-icon="mdi-flask-round-bottom"
              :loading="actionLoading === 'craft-max'"
              :disabled="writeActionsDisabled"
              @click="craftMaxPill"
            >一键炼造魔丸</v-btn>
          </v-card-title>
          <v-card-text class="workshop-body">
            <div v-if="!recipes.length" class="empty-state">
              <v-icon icon="mdi-flask-empty-outline" size="34" />
              <strong>后端暂未返回配方</strong>
              <small>页面不会自行补造配方或推测可炼造状态。</small>
            </div>
            <div v-else class="recipe-grid">
              <article v-for="recipe in recipes" :key="recipe.craft_id" class="recipe-card" :class="{ 'recipe-card--disabled': recipe.enabled !== true }">
                <div class="recipe-head">
                  <span class="recipe-icon">{{ recipe.icon || '⚒️' }}</span>
                  <div class="recipe-title">
                    <strong>{{ recipe.output_item || recipe.name || recipe.title }}</strong>
                    <small>
                      配方 ID {{ recipe.craft_id }}
                      <template v-if="Number(recipe.max_count || 0) > 0"> · 最多 {{ recipe.max_count }}</template>
                    </small>
                  </div>
                </div>
                <div class="recipe-ingredients">
                  <span v-for="(required, name) in recipe.ingredients || {}" :key="`${recipe.craft_id}-${name}`">{{ name }} ×{{ required }}</span>
                </div>
                <div class="recipe-controls">
                  <v-text-field
                    v-model="recipeQuantities[recipe.craft_id]"
                    type="number"
                    min="1"
                    :max="recipe.max_count"
                    label="数量"
                    variant="outlined"
                    density="compact"
                    hide-details="auto"
                    :error-messages="recipeQuantityError(recipe) ? [recipeQuantityError(recipe)] : []"
                    :disabled="writeActionsDisabled || recipe.enabled !== true || Number(recipe.max_count || 0) <= 0"
                  />
                  <v-btn
                    color="cyan-darken-1"
                    variant="tonal"
                    :loading="actionLoading === `craft-${recipe.craft_id}`"
                    :disabled="writeActionsDisabled || recipe.enabled !== true || Number(recipe.max_count || 0) <= 0 || !!recipeQuantityError(recipe)"
                    @click="craftRecipe(recipe)"
                  >炼造</v-btn>
                </div>
                <div v-if="recipeUnavailableReason(recipe)" class="unavailable-reason">
                  {{ recipeUnavailableReason(recipe) }}
                </div>
              </article>
            </div>
          </v-card-text>
          </v-card>
        </div>

        <v-card flat class="siqi-card history-card">
          <v-card-title class="siqi-card-title siqi-card-title--logs d-flex align-center">
            <v-icon icon="mdi-history" class="mr-2" color="blue" />执行历史
          </v-card-title>
          <v-card-text class="history-body">
            <div v-if="!historyItems.length" class="empty-state compact-empty">暂无执行记录</div>
            <div v-else class="history-list">
              <div v-for="item in historyItems" :key="historyKey(item)" class="history-item">
                <span class="history-detail">{{ historyText(item) }}</span>
                <time class="history-time">{{ item.time || '' }}</time>
              </div>
            </div>
          </v-card-text>
        </v-card>
      </template>
    </div>

    <v-dialog v-model="showGiftDialog" max-width="560" :persistent="giftLoading">
      <v-card flat class="siqi-dialog gift-dialog">
        <v-card-title class="dialog-header">
          <div class="dialog-avatar">{{ selectedGiftItem?.icon || '🎁' }}</div>
          <div class="dialog-copy">
            <strong>赠送 {{ selectedGiftItem?.name || '物品' }}</strong>
            <small>当前库存 {{ selectedGiftItem?.count ?? 0 }}，网站单次最多接受 500 个。</small>
          </div>
          <v-btn icon variant="text" aria-label="取消赠送并关闭对话框" :disabled="giftLoading" @click="closeGiftDialog">
            <v-icon icon="mdi-close" />
          </v-btn>
        </v-card-title>
        <v-card-text class="dialog-body">
          <v-text-field
            v-model="giftForm.target_uid"
            label="接收方 UID"
            variant="outlined"
            autocomplete="off"
            :disabled="giftLoading"
          />
          <v-text-field
            v-model="giftForm.quantity"
            type="number"
            min="1"
            :max="giftMaxQuantity"
            label="赠送数量"
            variant="outlined"
            :hint="giftQuantityHint"
            persistent-hint
            :error-messages="giftFormError ? [giftFormError] : []"
            :disabled="giftLoading"
          />
          <v-alert v-if="giftConfirming" type="warning" variant="tonal" density="compact" class="confirm-alert">
            再次确认：向 UID {{ giftForm.target_uid.trim() }} 赠送 {{ selectedGiftItem?.name }} ×{{ normalizedGiftQuantity }}。提交后由后端进行最终校验。
          </v-alert>
        </v-card-text>
        <v-card-actions class="dialog-actions">
          <v-btn variant="tonal" :disabled="giftLoading" @click="closeGiftDialog">取消</v-btn>
          <v-spacer />
          <v-btn v-if="giftConfirming" variant="text" :disabled="giftLoading" @click="giftConfirming = false">返回修改</v-btn>
          <v-btn
            v-if="!giftConfirming"
            color="orange-darken-1"
            variant="tonal"
            :disabled="giftLoading || !!giftFormError"
            @click="requestGiftConfirmation"
          >确认赠送</v-btn>
          <v-btn
            v-else
            color="error"
            variant="tonal"
            :loading="giftLoading"
            :disabled="giftLoading || !!giftFormError"
            @click="submitGift"
          >再次确认并赠送</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="showBatchGiftDialog" max-width="720" scrollable :persistent="batchGiftLoading">
      <v-card flat class="siqi-dialog batch-gift-dialog">
        <v-card-title class="dialog-header">
          <div class="dialog-avatar batch-gift-avatar"><v-icon icon="mdi-gift-open-outline" /></div>
          <div class="dialog-copy">
            <strong>批量赠送</strong>
            <small>勾选多种物品，共用一个接收方 UID；每种物品单次最多赠送 500 个。</small>
          </div>
          <v-btn icon variant="text" aria-label="取消批量赠送并关闭对话框" :disabled="batchGiftLoading" @click="closeBatchGiftDialog">
            <v-icon icon="mdi-close" />
          </v-btn>
        </v-card-title>
        <v-card-text class="dialog-body batch-gift-body">
          <v-text-field
            v-model="batchGiftForm.target_uid"
            label="接收方 UID"
            variant="outlined"
            autocomplete="off"
            :disabled="batchGiftLoading"
          />
          <div class="batch-gift-list">
            <div
              v-for="item in batchGiftRows"
              :key="item.name"
              class="batch-gift-row"
              :class="{ 'batch-gift-row--selected': item.selected }"
            >
              <v-checkbox-btn
                v-model="item.selected"
                color="orange-darken-1"
                :aria-label="`${item.name} 加入批量赠送`"
                :disabled="batchGiftLoading"
              />
              <div class="batch-gift-item">
                <span class="batch-gift-item__icon">{{ item.icon || '📦' }}</span>
                <span class="batch-gift-item__copy">
                  <strong>{{ item.name }}</strong>
                  <small>库存 {{ item.count }} · 最多 {{ item.maxQuantity }}</small>
                </span>
              </div>
              <v-text-field
                v-model="item.quantity"
                type="number"
                min="1"
                :max="item.maxQuantity"
                label="数量"
                variant="outlined"
                density="compact"
                hide-details="auto"
                :error-messages="item.selected && batchGiftRowError(item) ? [batchGiftRowError(item)] : []"
                :disabled="batchGiftLoading || !item.selected"
              />
            </div>
          </div>
          <v-alert v-if="batchGiftConfirming" type="warning" variant="tonal" density="compact" class="confirm-alert">
            再次确认：向 UID {{ batchGiftForm.target_uid.trim() }} 批量赠送 {{ batchGiftSummary }}。提交后将按顺序处理，遇到失败会立即停止。
          </v-alert>
          <v-alert v-else-if="batchGiftFormError" type="info" variant="tonal" density="compact" class="confirm-alert">
            {{ batchGiftFormError }}
          </v-alert>
        </v-card-text>
        <v-card-actions class="dialog-actions">
          <v-btn variant="tonal" :disabled="batchGiftLoading" @click="closeBatchGiftDialog">取消</v-btn>
          <v-spacer />
          <v-btn v-if="batchGiftConfirming" variant="text" :disabled="batchGiftLoading" @click="batchGiftConfirming = false">返回修改</v-btn>
          <v-btn
            v-if="!batchGiftConfirming"
            color="orange-darken-1"
            variant="tonal"
            :disabled="batchGiftLoading || !!batchGiftFormError"
            @click="requestBatchGiftConfirmation"
          >确认批量赠送</v-btn>
          <v-btn
            v-else
            color="error"
            variant="tonal"
            :loading="batchGiftLoading"
            :disabled="batchGiftLoading || !!batchGiftFormError"
            @click="submitBatchGift"
          >再次确认并批量赠送</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-dialog v-model="showGiftStatsDialog" max-width="820" scrollable>
      <v-card flat class="siqi-dialog stats-dialog">
        <v-card-title class="dialog-header">
          <div class="dialog-avatar stats-avatar"><v-icon icon="mdi-chart-box-outline" /></div>
          <div class="dialog-copy">
            <strong>赠送统计</strong>
            <small>按后端记录查看赠出或收到的物品汇总。</small>
          </div>
          <v-btn icon variant="text" aria-label="关闭赠送统计" :disabled="giftStatsLoading" @click="showGiftStatsDialog = false">
            <v-icon icon="mdi-close" />
          </v-btn>
        </v-card-title>
        <v-card-text class="stats-dialog-body">
          <div class="stats-filters">
            <v-btn-toggle v-model="giftStatsDraftDirection" mandatory :disabled="giftStatsLoading" color="blue" variant="tonal" divided>
              <v-btn value="out">赠出</v-btn>
              <v-btn value="in">收到</v-btn>
            </v-btn-toggle>
            <v-btn-toggle v-model="giftStatsDraftRange" mandatory :disabled="giftStatsLoading" color="blue" variant="tonal" divided>
              <v-btn value="30">最近30天</v-btn>
              <v-btn value="all">全部</v-btn>
            </v-btn-toggle>
            <v-btn color="blue" variant="tonal" :loading="giftStatsLoading" :disabled="initialLoading || giftStatsLoading" @click="loadGiftStats">查询统计</v-btn>
          </div>

          <v-alert v-if="giftStatsError" type="error" variant="tonal" density="compact" class="mb-3">{{ giftStatsError }}</v-alert>
          <div v-else-if="giftStatsLoading && !giftStats" class="empty-state">正在加载赠送统计...</div>
          <template v-else-if="giftStats">
            <div class="stats-applied-filter">当前数据：{{ giftStatsAppliedDirectionLabel }} · {{ giftStatsAppliedRangeLabel }}</div>
            <div class="gift-stats summary-grid">
              <div class="summary-stat"><span>总事件数</span><strong>{{ giftStats.total_events ?? 0 }}</strong></div>
              <div class="summary-stat"><span>总数量</span><strong>{{ giftStats.total_quantity ?? 0 }}</strong></div>
            </div>
            <div v-if="giftStatsEmpty" class="empty-state compact-empty">当前筛选范围暂无赠送记录</div>
            <div v-else class="stats-columns">
              <section class="stats-section">
                <h3>用户汇总</h3>
                <div v-if="!giftStatsUsers.length" class="stats-empty">暂无用户数据</div>
                <div v-else class="stats-list">
                  <div v-for="row in giftStatsUsers" :key="row.uid || row.name || row.display_name" class="stats-row">
                    <span>{{ row.display_name || row.name || row.uid || '未知用户' }}</span>
                    <small>{{ rowEvents(row) }} 次 · {{ rowQuantity(row) }} 个</small>
                  </div>
                </div>
              </section>
              <section class="stats-section">
                <h3>物品汇总</h3>
                <div v-if="!giftStatsItems.length" class="stats-empty">暂无物品数据</div>
                <div v-else class="stats-list">
                  <div v-for="row in giftStatsItems" :key="row.item_name || row.name" class="stats-row">
                    <span>{{ row.item_name || row.name || '未知物品' }}</span>
                    <small>{{ rowEvents(row) }} 次 · {{ rowQuantity(row) }} 个</small>
                  </div>
                </div>
              </section>
            </div>
          </template>
        </v-card-text>
        <v-card-actions class="dialog-actions">
          <v-spacer />
          <v-btn variant="tonal" :disabled="giftStatsLoading" @click="showGiftStatsDialog = false">关闭</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'
import {
  createLatestRequestGuard,
  extractStatusPayload,
  isStrictSuccess,
  resolveGiftStatsFilters,
  safeResponseMessage,
} from '../utils/asyncGuards'

const props = defineProps({ api: { type: Object, required: true }, initialConfig: { type: Object, default: () => ({}) } })
const emit = defineEmits(['switch', 'close'])

const PLUGIN_ID = 'VuePill'
const apiGet = (path) => props.api.get(`/plugin/${PLUGIN_ID}${path}`)
const apiPost = (path, data = {}) => props.api.post(`/plugin/${PLUGIN_ID}${path}`, data)

const status = reactive({ pill_status: {}, history: [] })
const message = reactive({ text: '', type: 'success' })
const initialLoading = ref(true)
const actionLoading = ref('')
const exchangeQuantity = ref('1')
const recipeQuantities = reactive({})
const showGiftDialog = ref(false)
const selectedGiftItem = ref(null)
const giftForm = reactive({ target_uid: '', quantity: '1' })
const giftConfirming = ref(false)
const giftConfirmationSnapshot = ref(null)
const giftLoading = ref(false)
const showBatchGiftDialog = ref(false)
const batchGiftForm = reactive({ target_uid: '' })
const batchGiftRows = ref([])
const batchGiftConfirming = ref(false)
const batchGiftConfirmationSnapshot = ref(null)
const batchGiftLoading = ref(false)
const showGiftStatsDialog = ref(false)
const giftStatsDraftDirection = ref('out')
const giftStatsDraftRange = ref('30')
const giftStatsAppliedDirection = ref('')
const giftStatsAppliedRange = ref('')
const giftStats = ref(null)
const giftStatsLoading = ref(false)
const giftStatsError = ref('')
const statusRequestGuard = createLatestRequestGuard()
const actionRequestGuard = createLatestRequestGuard()
const giftRequestGuard = createLatestRequestGuard()
const batchGiftRequestGuard = createLatestRequestGuard()
const giftStatsRequestGuard = createLatestRequestGuard()
let giftDialogToken = 0
let batchGiftDialogToken = 0
let messageTimer = null

const pill = computed(() => status.pill_status || {})
const overview = computed(() => Array.isArray(pill.value.overview) ? pill.value.overview.slice(0, 4) : [])
const brick = computed(() => pill.value.brick || {})
const beach = computed(() => pill.value.beach || {})
const beachActionable = computed(() => (
  beach.value.ready === true
  || beach.value.can_collect === true
  || beach.value.has_trash === true
  || beach.value.collect_enabled === true
))
const brickStatusLabel = computed(() => {
  if (brick.value.ready === true) return '可以搬砖'
  const daily = Number(brick.value.daily_bricks || 0)
  const limit = Number(brick.value.daily_limit || 0)
  if (limit > 0 && daily >= limit) return '今日已完成'
  if (
    Object.prototype.hasOwnProperty.call(brick.value, 'available_count')
    && Number(brick.value.available_count || 0) <= 0
  ) return '暂无砖块'
  return '等待刷新'
})
const beachStatusLabel = computed(() => {
  if (beachActionable.value) return '可以清理'
  const statusText = String(beach.value.status_text || '')
  if (beach.value.next_ready_time || statusText.includes('冷却')) return '冷却中'
  return '等待刷新'
})
const exchange = computed(() => pill.value.exchange || {})
const inventoryItems = computed(() => {
  const inventory = pill.value.inventory || {}
  return Array.isArray(inventory.items) ? inventory.items : []
})
const recipes = computed(() => Array.isArray(pill.value.recipes) ? pill.value.recipes : [])
const historyItems = computed(() => Array.isArray(status.history) ? status.history : [])
const isBusy = computed(() => !!actionLoading.value)
const writeActionsDisabled = computed(() => (
  initialLoading.value
  || isBusy.value
  || giftLoading.value
  || batchGiftLoading.value
  || showGiftDialog.value
  || showBatchGiftDialog.value
))

const exchangeQuantityError = computed(() => quantityError(exchangeQuantity.value, Number(exchange.value.max_count || 0), '兑换'))

const giftMaxQuantity = computed(() => Math.min(Math.max(Number(selectedGiftItem.value?.count || 0), 0), 500))
const normalizedGiftQuantity = computed(() => Number.parseInt(giftForm.quantity, 10) || 0)
const giftFormError = computed(() => {
  if (!selectedGiftItem.value) return '请选择要赠送的物品'
  if (!giftForm.target_uid.trim()) return '请填写接收方 UID'
  return quantityError(giftForm.quantity, giftMaxQuantity.value, '赠送')
})
const giftQuantityHint = computed(() => `前端提示范围 1-${giftMaxQuantity.value || 0}，最终以后端校验为准。`)

const batchGiftableItems = computed(() => inventoryItems.value.filter((item) => (
  item?.giftable === true && Number(item?.count || 0) > 0
)))
const batchGiftSelectedRows = computed(() => batchGiftRows.value.filter((item) => item.selected))
const batchGiftSummary = computed(() => batchGiftSelectedRows.value
  .map((item) => `${item.name}×${Number.parseInt(item.quantity, 10) || 0}`)
  .join('、'))
const batchGiftFormError = computed(() => {
  if (!batchGiftForm.target_uid.trim()) return '请填写接收方 UID'
  if (!batchGiftSelectedRows.value.length) return '请至少选择一种物品'
  for (const item of batchGiftSelectedRows.value) {
    const error = batchGiftRowError(item)
    if (error) return `${item.name}：${error}`
  }
  return ''
})

const giftStatsUsers = computed(() => Array.isArray(giftStats.value?.users) ? giftStats.value.users : [])
const giftStatsItems = computed(() => Array.isArray(giftStats.value?.items) ? giftStats.value.items : [])
const giftStatsEmpty = computed(() => Number(giftStats.value?.total_events || 0) <= 0 && !giftStatsUsers.value.length && !giftStatsItems.value.length)
const giftStatsAppliedDirectionLabel = computed(() => giftStatsAppliedDirection.value === 'in' ? '收到' : '赠出')
const giftStatsAppliedRangeLabel = computed(() => giftStatsAppliedRange.value === 'all' ? '全部' : '最近30天')

watch(() => exchange.value.max_count, (maxCount) => {
  const maximum = Number(maxCount || 0)
  if (maximum > 0 && Number(exchangeQuantity.value) > maximum) exchangeQuantity.value = String(maximum)
}, { immediate: true })

watch(recipes, (rows) => {
  rows.forEach((recipe) => {
    const key = recipe.craft_id
    const maximum = Number(recipe.max_count || 0)
    const current = Number(recipeQuantities[key])
    if (!Number.isInteger(current) || current < 1) recipeQuantities[key] = '1'
    else if (maximum > 0 && current > maximum) recipeQuantities[key] = String(maximum)
  })
}, { immediate: true })

watch(() => [giftForm.target_uid, giftForm.quantity], () => {
  giftConfirming.value = false
  giftConfirmationSnapshot.value = null
})

watch(
  () => [
    batchGiftForm.target_uid,
    ...batchGiftRows.value.flatMap((item) => [item.selected, item.quantity]),
  ],
  () => {
    batchGiftConfirming.value = false
    batchGiftConfirmationSnapshot.value = null
  },
)

watch(() => [giftStatsDraftDirection.value, giftStatsDraftRange.value], ([direction, range]) => {
  if (direction === giftStatsAppliedDirection.value && range === giftStatsAppliedRange.value) return
  giftStatsRequestGuard.invalidate()
  giftStatsLoading.value = false
  giftStats.value = null
  giftStatsError.value = ''
})

function flash(text, type = 'success') {
  message.text = String(text || '')
  message.type = type
  if (messageTimer) window.clearTimeout(messageTimer)
  messageTimer = window.setTimeout(() => {
    message.text = ''
    messageTimer = null
  }, 3600)
}

function applyStatusPayload(payload = {}) {
  const update = extractStatusPayload(payload)
  if (!update) return false

  status.pill_status = update.pillStatus
  if (update.history) status.history = update.history
  return true
}

async function loadStatus({ silent = false } = {}) {
  const requestId = statusRequestGuard.begin()
  try {
    const result = await apiGet('/status')
    if (!statusRequestGuard.isCurrent(requestId)) return false
    if (!result || typeof result !== 'object') throw new Error('状态响应无效')
    if (result.success === false) throw new Error(safeResponseMessage(result, '状态加载失败'))
    if (!applyStatusPayload(result)) throw new Error('状态响应无效')
    return true
  } catch (error) {
    if (!statusRequestGuard.isCurrent(requestId)) return false
    if (!silent) flash(safeResponseMessage(error, '状态加载失败'), 'error')
    return false
  } finally {
    if (statusRequestGuard.isCurrent(requestId)) initialLoading.value = false
  }
}

async function runAction(key, request, fallbackMessage) {
  if (initialLoading.value || actionLoading.value) return null
  const requestId = actionRequestGuard.begin()
  actionLoading.value = key
  try {
    const result = await request()
    if (!actionRequestGuard.isCurrent(requestId)) return null
    statusRequestGuard.invalidate()
    const statusApplied = applyStatusPayload(result)
    if (!isStrictSuccess(result)) {
      flash(safeResponseMessage(result, `${fallbackMessage}失败`), 'error')
      if (!statusApplied) await loadStatus({ silent: true })
      return null
    }
    flash(safeResponseMessage(result, fallbackMessage))
    await loadStatus({ silent: true })
    return result
  } catch (error) {
    if (!actionRequestGuard.isCurrent(requestId)) return null
    flash(safeResponseMessage(error, `${fallbackMessage}失败`), 'error')
    statusRequestGuard.invalidate()
    await loadStatus({ silent: true })
    return null
  } finally {
    if (actionRequestGuard.isCurrent(requestId)) actionLoading.value = ''
  }
}

function quantityError(value, maximum, actionName) {
  const quantity = Number(value)
  if (!Number.isInteger(quantity) || quantity < 1) return `${actionName}数量必须是正整数`
  if (maximum <= 0) return `后端返回的${actionName}上限为 0`
  if (quantity > maximum) return `${actionName}数量不能超过后端上限 ${maximum}`
  return ''
}

function overviewTone(item) {
  const label = String(item?.label || '')
  if (label.includes('兑换')) return 'green'
  if (label.includes('魔丸')) return 'blue'
  if (label.includes('搬砖')) return 'orange'
  return 'red'
}

function overviewIcon(item) {
  const label = String(item?.label || '')
  if (label.includes('兑换')) return 'mdi-cash-multiple'
  if (label.includes('魔丸')) return 'mdi-flask-round-bottom'
  if (label.includes('搬砖')) return 'mdi-wall'
  return 'mdi-star-four-points'
}

function canGiftItem(item) {
  return !writeActionsDisabled.value && item?.giftable === true && Number(item?.count || 0) > 0
}

function openGiftDialog(item) {
  if (initialLoading.value || isBusy.value || giftLoading.value || showGiftDialog.value) return
  if (!canGiftItem(item)) return
  giftRequestGuard.invalidate()
  giftDialogToken += 1
  selectedGiftItem.value = item
  giftForm.target_uid = ''
  giftForm.quantity = '1'
  giftConfirming.value = false
  giftConfirmationSnapshot.value = null
  showGiftDialog.value = true
}

function closeGiftDialog() {
  if (giftLoading.value) return
  giftRequestGuard.invalidate()
  giftDialogToken += 1
  showGiftDialog.value = false
  giftConfirming.value = false
  giftConfirmationSnapshot.value = null
  selectedGiftItem.value = null
}

function currentGiftSnapshot() {
  return {
    dialogToken: giftDialogToken,
    itemName: String(selectedGiftItem.value?.name || '').trim(),
    targetUid: String(giftForm.target_uid || '').trim(),
    quantity: normalizedGiftQuantity.value,
  }
}

function sameGiftSnapshot(left, right) {
  return !!left && !!right
    && left.dialogToken === right.dialogToken
    && left.itemName === right.itemName
    && left.targetUid === right.targetUid
    && left.quantity === right.quantity
}

function requestGiftConfirmation() {
  if (initialLoading.value || !showGiftDialog.value) return
  if (giftFormError.value) return flash(giftFormError.value, 'warning')
  giftConfirmationSnapshot.value = currentGiftSnapshot()
  giftConfirming.value = true
}

async function submitGift() {
  if (giftLoading.value) return
  if (initialLoading.value || !showGiftDialog.value) return
  if (giftFormError.value) return flash(giftFormError.value, 'warning')
  const snapshot = currentGiftSnapshot()
  if (!giftConfirming.value || !sameGiftSnapshot(snapshot, giftConfirmationSnapshot.value)) {
    giftConfirming.value = false
    giftConfirmationSnapshot.value = null
    flash('赠送信息已变化，请重新确认', 'warning')
    return
  }

  const requestId = giftRequestGuard.begin()
  const requestDialogToken = snapshot.dialogToken
  giftLoading.value = true
  try {
    const result = await apiPost('/gift-item', {
      item_name: snapshot.itemName,
      target_uid: snapshot.targetUid,
      quantity: snapshot.quantity,
    })
    if (!giftRequestGuard.isCurrent(requestId)) return
    statusRequestGuard.invalidate()
    const statusApplied = applyStatusPayload(result)
    if (!isStrictSuccess(result)) {
      flash(safeResponseMessage(result, '赠送失败'), 'error')
      if (!statusApplied) await loadStatus({ silent: true })
      return
    }

    flash(safeResponseMessage(result, '赠送成功'))
    if (
      showGiftDialog.value
      && giftDialogToken === requestDialogToken
      && sameGiftSnapshot(currentGiftSnapshot(), snapshot)
    ) {
      showGiftDialog.value = false
      giftConfirming.value = false
      giftConfirmationSnapshot.value = null
      selectedGiftItem.value = null
      giftDialogToken += 1
    }
    await loadStatus({ silent: true })
  } catch (error) {
    if (giftRequestGuard.isCurrent(requestId)) {
      flash(safeResponseMessage(error, '赠送失败'), 'error')
      statusRequestGuard.invalidate()
      await loadStatus({ silent: true })
    }
  } finally {
    if (giftRequestGuard.isCurrent(requestId)) giftLoading.value = false
  }
}

function batchGiftRowError(item) {
  const maximum = Math.min(Math.max(Number(item?.maxQuantity || item?.count || 0), 0), 500)
  return quantityError(item?.quantity, maximum, '赠送')
}

function openBatchGiftDialog() {
  if (
    initialLoading.value
    || isBusy.value
    || giftLoading.value
    || batchGiftLoading.value
    || showGiftDialog.value
    || showBatchGiftDialog.value
  ) return
  if (!batchGiftableItems.value.length) {
    flash('当前没有可批量赠送的物品', 'warning')
    return
  }

  batchGiftRequestGuard.invalidate()
  batchGiftDialogToken += 1
  batchGiftForm.target_uid = ''
  batchGiftRows.value = batchGiftableItems.value.map((item) => ({
    name: String(item.name || '').trim(),
    icon: item.icon || '📦',
    count: Math.max(Number(item.count || 0), 0),
    maxQuantity: Math.min(Math.max(Number(item.count || 0), 0), 500),
    selected: false,
    quantity: '1',
  }))
  batchGiftConfirming.value = false
  batchGiftConfirmationSnapshot.value = null
  showBatchGiftDialog.value = true
}

function resetBatchGiftDialog() {
  showBatchGiftDialog.value = false
  batchGiftConfirming.value = false
  batchGiftConfirmationSnapshot.value = null
  batchGiftRows.value = []
  batchGiftForm.target_uid = ''
  batchGiftDialogToken += 1
}

function closeBatchGiftDialog() {
  if (batchGiftLoading.value) return
  batchGiftRequestGuard.invalidate()
  resetBatchGiftDialog()
}

function currentBatchGiftSnapshot() {
  return {
    dialogToken: batchGiftDialogToken,
    targetUid: String(batchGiftForm.target_uid || '').trim(),
    items: batchGiftSelectedRows.value.map((item) => ({
      item_name: item.name,
      quantity: Number.parseInt(item.quantity, 10) || 0,
    })),
  }
}

function sameBatchGiftSnapshot(left, right) {
  if (!left || !right) return false
  if (left.dialogToken !== right.dialogToken || left.targetUid !== right.targetUid) return false
  if (!Array.isArray(left.items) || !Array.isArray(right.items) || left.items.length !== right.items.length) return false
  return left.items.every((item, index) => (
    item.item_name === right.items[index]?.item_name
    && item.quantity === right.items[index]?.quantity
  ))
}

function requestBatchGiftConfirmation() {
  if (initialLoading.value || !showBatchGiftDialog.value) return
  if (batchGiftFormError.value) return flash(batchGiftFormError.value, 'warning')
  batchGiftConfirmationSnapshot.value = currentBatchGiftSnapshot()
  batchGiftConfirming.value = true
}

function dismissBatchGiftDialog(snapshot) {
  if (
    showBatchGiftDialog.value
    && batchGiftDialogToken === snapshot.dialogToken
    && sameBatchGiftSnapshot(currentBatchGiftSnapshot(), snapshot)
  ) resetBatchGiftDialog()
}

async function submitBatchGift() {
  if (batchGiftLoading.value) return
  if (initialLoading.value || !showBatchGiftDialog.value) return
  if (batchGiftFormError.value) return flash(batchGiftFormError.value, 'warning')
  const snapshot = currentBatchGiftSnapshot()
  if (
    !batchGiftConfirming.value
    || !sameBatchGiftSnapshot(snapshot, batchGiftConfirmationSnapshot.value)
  ) {
    batchGiftConfirming.value = false
    batchGiftConfirmationSnapshot.value = null
    flash('批量赠送信息已变化，请重新确认', 'warning')
    return
  }

  const requestId = batchGiftRequestGuard.begin()
  batchGiftLoading.value = true
  try {
    const result = await apiPost('/gift-items', {
      target_uid: snapshot.targetUid,
      items: snapshot.items,
    })
    if (!batchGiftRequestGuard.isCurrent(requestId)) return
    statusRequestGuard.invalidate()
    const statusApplied = applyStatusPayload(result)
    const gifted = Array.isArray(result?.gifted) ? result.gifted : []

    if (isStrictSuccess(result)) {
      flash(safeResponseMessage(result, '批量赠送成功'))
      dismissBatchGiftDialog(snapshot)
      await loadStatus({ silent: true })
      return
    }

    if (result?.partial === true && gifted.length) {
      flash(safeResponseMessage(result, '批量赠送部分完成'), 'warning')
      dismissBatchGiftDialog(snapshot)
      await loadStatus({ silent: true })
      return
    }

    flash(safeResponseMessage(result, '批量赠送失败'), 'error')
    if (!statusApplied) await loadStatus({ silent: true })
  } catch (error) {
    if (batchGiftRequestGuard.isCurrent(requestId)) {
      flash(safeResponseMessage(error, '批量赠送失败'), 'error')
      statusRequestGuard.invalidate()
      await loadStatus({ silent: true })
    }
  } finally {
    if (batchGiftRequestGuard.isCurrent(requestId)) batchGiftLoading.value = false
  }
}

async function openGiftStats() {
  if (initialLoading.value) return
  showGiftStatsDialog.value = true
  await loadGiftStats()
}

async function loadGiftStats() {
  if (initialLoading.value) return
  const requestedFilters = resolveGiftStatsFilters(null, {
    direction: giftStatsDraftDirection.value,
    range: giftStatsDraftRange.value,
  })
  const requestId = giftStatsRequestGuard.begin()
  giftStatsLoading.value = true
  giftStatsError.value = ''
  giftStats.value = null
  giftStatsAppliedDirection.value = ''
  giftStatsAppliedRange.value = ''
  try {
    const result = await apiPost('/gift-stats', {
      direction: requestedFilters.direction,
      range: requestedFilters.range,
    })
    if (!giftStatsRequestGuard.isCurrent(requestId)) return
    if (!isStrictSuccess(result)) {
      giftStatsError.value = safeResponseMessage(result, '赠送统计加载失败')
      return
    }

    const appliedFilters = resolveGiftStatsFilters(result, requestedFilters)
    giftStatsAppliedDirection.value = appliedFilters.direction
    giftStatsAppliedRange.value = appliedFilters.range
    giftStatsDraftDirection.value = appliedFilters.direction
    giftStatsDraftRange.value = appliedFilters.range
    giftStats.value = {
      total_events: Number(result?.total_events || 0),
      total_quantity: Number(result?.total_quantity || 0),
      users: Array.isArray(result?.users) ? result.users : [],
      items: Array.isArray(result?.items) ? result.items : [],
    }
  } catch (error) {
    if (giftStatsRequestGuard.isCurrent(requestId)) {
      giftStatsError.value = safeResponseMessage(error, '赠送统计加载失败')
    }
  } finally {
    if (giftStatsRequestGuard.isCurrent(requestId)) giftStatsLoading.value = false
  }
}

function rowEvents(row) {
  return Number(row?.total_events ?? row?.events ?? row?.count ?? 0)
}

function rowQuantity(row) {
  return Number(row?.total_quantity ?? row?.quantity ?? row?.count ?? 0)
}

function recipeQuantityError(recipe) {
  const maximum = Number(recipe.max_count || 0)
  if (maximum <= 0) return ''
  return quantityError(recipeQuantities[recipe.craft_id], maximum, '炼造')
}

function recipeUnavailableReason(recipe) {
  if (recipe.supported === false) return '后端标记该配方暂不支持。'
  if (Number(recipe.max_count || 0) <= 0) return ''
  if (recipe.status && !/材料不足|炼造上限为\s*0|最大可炼造数量为\s*0/.test(recipe.status)) return recipe.status
  return recipe.enabled !== true ? '后端标记该配方当前不可炼造。' : ''
}

function historyText(item) {
  return [item?.title, ...(Array.isArray(item?.lines) ? item.lines : [])].filter(Boolean).join(' / ') || '未提供执行内容'
}

function historyKey(item) {
  return `${item?.time || ''}-${item?.title || ''}-${historyText(item)}`
}

async function refreshData() { await runAction('refresh', () => apiPost('/refresh'), '状态已刷新') }
async function moveBricks() { await runAction('brick', () => apiPost('/move-bricks'), '搬砖完成') }
async function cleanBeach() { await runAction('beach', () => apiPost('/clean-beach'), '沙滩清理完成') }

async function exchangePoints() {
  if (exchangeQuantityError.value) return flash(exchangeQuantityError.value, 'warning')
  await runAction('exchange', () => apiPost('/exchange-points', { quantity: Number(exchangeQuantity.value) }), '兑换完成')
}

async function craftRecipe(recipe) {
  const error = recipeQuantityError(recipe)
  if (error) return flash(error, 'warning')
  await runAction(
    `craft-${recipe.craft_id}`,
    () => apiPost('/craft-item', { recipe_id: Number(recipe.craft_id), quantity: Number(recipeQuantities[recipe.craft_id]) }),
    '炼造完成',
  )
}

async function craftMaxPill() {
  await runAction('craft-max', () => apiPost('/craft-max-pill'), '一键炼造完成')
}

onMounted(loadStatus)

onBeforeUnmount(() => {
  statusRequestGuard.invalidate()
  actionRequestGuard.invalidate()
  giftRequestGuard.invalidate()
  batchGiftRequestGuard.invalidate()
  giftStatsRequestGuard.invalidate()
  if (messageTimer) window.clearTimeout(messageTimer)
})
</script>

<style scoped>
.siqi-page{padding:16px 20px;display:flex;flex-direction:column;gap:16px;min-height:400px;overflow-x:hidden;font-family:-apple-system,BlinkMacSystemFont,'SF Pro Text','Inter',sans-serif;color:rgba(var(--v-theme-on-surface),.85);border:1px solid rgba(var(--v-theme-on-surface),.12);border-radius:8px;background:linear-gradient(180deg,rgba(255,255,255,.02),rgba(76,175,80,.025))}
.siqi-page,.siqi-page *{box-sizing:border-box}
.siqi-page :deep(.v-btn){min-height:44px;transition:transform .16s ease,box-shadow .16s ease,filter .16s ease,opacity .16s ease}
.siqi-page :deep(.v-btn:not(.v-btn--disabled):hover){transform:translateY(-1px);box-shadow:0 6px 16px rgba(15,23,42,.12);filter:saturate(1.05)}
.siqi-page :deep(.v-btn:not(.v-btn--disabled):active){transform:translateY(0) scale(.98)}
.siqi-page :deep(.v-btn.v-btn--disabled){cursor:not-allowed;opacity:.55}
.siqi-topbar{display:flex;align-items:center;justify-content:space-between;gap:16px;padding-bottom:8px}
.siqi-topbar__left{display:flex;align-items:center;gap:12px;min-width:0;flex:1}
.siqi-topbar__copy{min-width:0}
.siqi-topbar__right{display:flex;align-items:center;flex-shrink:0}
.siqi-topbar__right :deep(.v-btn-group){flex-wrap:nowrap}
.siqi-topbar__icon{width:42px;height:42px;border-radius:11px;background:rgba(76,175,80,.14);display:flex;align-items:center;justify-content:center;color:#2e7d32;flex-shrink:0}
.siqi-topbar__title{font-size:16px;font-weight:700;letter-spacing:-.3px;color:rgba(var(--v-theme-on-surface),.88)}
.siqi-topbar__sub{font-size:11px;color:rgba(var(--v-theme-on-surface),.55);margin-top:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.siqi-content{display:flex;flex-direction:column;gap:0}
.siqi-toast{position:fixed!important;top:18px!important;left:50%!important;transform:translateX(-50%)!important;z-index:99999!important;width:min(520px,calc(100vw - 32px))!important;margin:0!important;box-shadow:0 12px 36px rgba(15,23,42,.18)!important;border-radius:12px!important}
.siqi-card{background:rgba(var(--v-theme-on-surface),.03)!important;backdrop-filter:blur(20px) saturate(150%);border-radius:14px!important;border:.5px solid rgba(var(--v-theme-on-surface),.08)!important;box-shadow:0 2px 10px rgba(0,0,0,.05)!important;overflow:hidden}
.siqi-card-title{min-height:44px;padding:10px 16px!important;font-size:13px!important;font-weight:700!important;background:rgba(76,175,80,.08);border-bottom:.5px solid rgba(var(--v-theme-on-surface),.07);color:rgba(var(--v-theme-on-surface),.84)}
.siqi-card-title :deep(.v-spacer){flex:1 1 auto!important}
.siqi-card-title--exchange{background:rgba(245,158,11,.09)}.siqi-card-title--inventory{background:rgba(251,146,60,.10)}.siqi-card-title--workshop{background:rgba(6,182,212,.09)}.siqi-card-title--logs{background:rgba(59,130,246,.09)}
.stat-card{--stat-rgb:76,175,80;--stat-color:#2e7d32;min-height:78px;border-radius:14px;padding:12px 14px;border:.5px solid rgba(var(--v-theme-on-surface),.08);background:rgba(var(--v-theme-on-surface),.03);box-shadow:inset 0 1px 0 rgba(var(--v-theme-surface),.2),0 2px 12px rgba(var(--v-theme-on-surface),.08);display:flex;align-items:center;gap:12px}
.stat-icon{width:38px;height:38px;border-radius:12px;display:flex;align-items:center;justify-content:center;background:rgba(var(--stat-rgb),.14);color:var(--stat-color);flex:0 0 38px}
.stat-content{min-width:0}.stat-title{font-size:11px;font-weight:600;color:rgba(var(--v-theme-on-surface),.55);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.stat-value{margin-top:2px;font-size:20px;font-weight:800;letter-spacing:-.5px;color:rgba(var(--v-theme-on-surface),.88);overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.stat-orange{--stat-rgb:245,158,11;--stat-color:#f59e0b;background:rgba(245,158,11,.12);border-color:rgba(245,158,11,.24)}.stat-green{--stat-rgb:16,185,129;--stat-color:#10b981;background:rgba(16,185,129,.12);border-color:rgba(16,185,129,.24)}.stat-blue{--stat-rgb:59,130,246;--stat-color:#3b82f6;background:rgba(59,130,246,.12);border-color:rgba(59,130,246,.24)}.stat-red{--stat-rgb:239,68,68;--stat-color:#ef4444;background:rgba(239,68,68,.12);border-color:rgba(239,68,68,.24)}
.stat-orange .stat-icon,.stat-orange .stat-title,.stat-orange .stat-value{color:#f59e0b}.stat-green .stat-icon,.stat-green .stat-title,.stat-green .stat-value{color:#10b981}.stat-blue .stat-icon,.stat-blue .stat-title,.stat-blue .stat-value{color:#3b82f6}.stat-red .stat-icon,.stat-red .stat-title,.stat-red .stat-value{color:#ef4444}
.overview-grid{display:grid!important;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px;margin:0 0 12px!important}
.overview-grid>*{width:auto!important;max-width:none!important;padding:0!important}
.primary-grid{display:grid;grid-template-columns:minmax(520px,1fr) minmax(360px,.78fr);gap:12px;align-items:stretch}.primary-grid>.siqi-card{height:100%;margin-bottom:0!important}.resource-grid{display:grid;grid-template-columns:1fr;gap:12px;align-items:stretch}.resource-grid>.siqi-card{min-width:0}.card-subtitle{margin-left:10px;color:rgba(var(--v-theme-on-surface),.48);font-size:12px;font-weight:500}
.schedule-board-body{padding:16px!important}.schedule-action-list{display:flex;flex-direction:column;gap:8px}.neu-action-card{display:grid;grid-template-columns:32px minmax(0,1fr) auto;align-items:center;gap:10px;min-height:76px;padding:10px 12px;border-radius:12px;background:rgba(var(--v-theme-surface),.86);border:1px solid rgba(76,175,80,.16);transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease}.neu-action-card:hover{transform:translateY(-1px);box-shadow:0 6px 14px rgba(15,23,42,.07)}.neu-action-card--beach{border-color:rgba(14,165,233,.18)}.neu-action-icon{width:32px;height:32px;display:grid;place-items:center;border-radius:9px;background:rgba(76,175,80,.10);color:#22c55e}.neu-action-card--beach .neu-action-icon{background:rgba(14,165,233,.11);color:#0ea5e9}.neu-action-content{min-width:0}.neu-action-heading{display:flex;align-items:center;gap:8px;min-width:0}.neu-action-label{font-size:13px;font-weight:800;color:rgba(var(--v-theme-on-surface),.84);line-height:1.2}.neu-action-desc{margin-top:3px;color:rgba(var(--v-theme-on-surface),.52);font-size:11px;line-height:1.3;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.schedule-status{display:inline-flex;align-items:center;min-height:20px;padding:2px 7px;border-radius:999px;background:rgba(var(--v-theme-on-surface),.07);color:rgba(var(--v-theme-on-surface),.55);font-size:10px;font-weight:800;white-space:nowrap}.schedule-status--ready{background:rgba(34,197,94,.12);color:#22c55e}.schedule-status--done{background:rgba(245,158,11,.12);color:#f59e0b}.schedule-status--cooldown{background:rgba(14,165,233,.11);color:#0ea5e9}.schedule-meta{display:flex;align-items:center;gap:6px;flex-wrap:wrap;margin-top:7px}.schedule-meta span{padding:3px 7px;border-radius:999px;background:rgba(var(--v-theme-on-surface),.045);border:1px solid rgba(var(--v-theme-on-surface),.065);font-size:10px;color:rgba(var(--v-theme-on-surface),.58);font-variant-numeric:tabular-nums}.neu-btn{height:32px!important;min-height:32px!important;border-radius:999px!important;font-weight:800;letter-spacing:0;font-size:11px!important;min-width:82px!important;box-shadow:none!important}.schedule-action{flex:0 0 auto}
.exchange-body{padding:16px!important}.exchange-summary{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}.exchange-stat{padding:12px;border-radius:12px;background:rgba(var(--v-theme-surface),.68);border:1px solid rgba(var(--v-theme-on-surface),.07);text-align:center}.exchange-stat span{display:block;font-size:11px;color:rgba(var(--v-theme-on-surface),.52)}.exchange-stat strong{display:inline-block;margin-top:3px;font-size:21px;color:#f59e0b}.exchange-stat small{margin-left:3px;color:rgba(var(--v-theme-on-surface),.52)}.exchange-action-panel{display:grid;grid-template-columns:minmax(220px,1fr) auto;gap:12px;align-items:start;margin-top:14px}
.inventory-title-actions{display:flex;align-items:center;justify-content:flex-end;gap:8px;flex-wrap:wrap}.inventory-body,.workshop-body{padding:14px!important}.inventory-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:9px}.gift-item{width:100%;min-height:76px;display:grid;grid-template-columns:42px minmax(0,1fr) auto;align-items:center;gap:10px;padding:10px;border-radius:12px;text-align:left;background:rgba(var(--v-theme-surface),.68);border:1px solid rgba(var(--v-theme-on-surface),.07);color:rgba(var(--v-theme-on-surface),.82);transition:transform .16s ease,box-shadow .16s ease,border-color .16s ease;cursor:pointer}.gift-item--available:hover{transform:translateY(-1px);border-color:rgba(251,146,60,.3);box-shadow:0 6px 16px rgba(15,23,42,.08)}.gift-item:disabled{cursor:not-allowed;opacity:.58}.gift-item__icon{width:42px;height:42px;border-radius:11px;display:grid;place-items:center;background:rgba(251,146,60,.12);font-size:24px}.gift-item__main{min-width:0}.gift-item__main strong,.gift-item__main small{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.gift-item__main strong{font-size:13px}.gift-item__main small{margin-top:4px;font-size:11px;color:rgba(var(--v-theme-on-surface),.52)}.gift-item__state{font-size:10px;font-weight:800;color:#f59e0b;white-space:nowrap}
.recipe-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}.recipe-card{padding:12px;border-radius:13px;background:rgba(var(--v-theme-surface),.68);border:1px solid rgba(6,182,212,.16)}.recipe-card--disabled{border-color:rgba(var(--v-theme-on-surface),.08)}.recipe-head{display:flex;align-items:center;gap:10px}.recipe-icon{width:38px;height:38px;border-radius:11px;display:grid;place-items:center;background:rgba(6,182,212,.12);font-size:22px;flex:0 0 38px}.recipe-title{min-width:0}.recipe-title strong,.recipe-title small{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.recipe-title strong{font-size:13px;color:rgba(var(--v-theme-on-surface),.84)}.recipe-title small{margin-top:3px;font-size:10px;color:rgba(var(--v-theme-on-surface),.5)}.recipe-ingredients{display:flex;gap:6px;flex-wrap:wrap;margin:10px 0}.recipe-ingredients span{padding:4px 7px;border-radius:999px;background:rgba(var(--v-theme-on-surface),.055);font-size:10px;color:rgba(var(--v-theme-on-surface),.65)}.recipe-controls{display:grid;grid-template-columns:minmax(120px,1fr) auto;gap:8px;align-items:start}.unavailable-reason{margin-top:8px;padding:7px 9px;border-radius:9px;background:rgba(239,68,68,.08);color:#ef5350;font-size:11px;line-height:1.5}
.history-body{max-height:360px;overflow-y:auto;padding:12px!important}.history-list{display:flex;flex-direction:column;border-radius:12px;background:rgba(var(--v-theme-surface),.68);border:1px solid rgba(var(--v-theme-on-surface),.06);overflow:hidden}.history-item{display:grid;grid-template-columns:minmax(0,1fr) auto;align-items:center;gap:12px;padding:10px 12px;border-bottom:1px solid rgba(var(--v-theme-on-surface),.07);font-size:12px}.history-item:last-child{border-bottom:none}.history-detail{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:rgba(var(--v-theme-on-surface),.68)}.history-time{text-align:right;white-space:nowrap;color:rgba(var(--v-theme-on-surface),.48);font-size:11px;font-variant-numeric:tabular-nums}
.empty-state{min-height:150px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:5px;text-align:center;color:rgba(var(--v-theme-on-surface),.54)}.empty-state strong{font-size:13px}.empty-state small{font-size:11px;color:rgba(var(--v-theme-on-surface),.42)}.compact-empty{min-height:96px}
.siqi-dialog{background:rgba(var(--v-theme-surface),.98)!important;border-radius:16px!important;border:1px solid rgba(var(--v-theme-on-surface),.10)!important;box-shadow:0 18px 48px rgba(15,23,42,.18)!important;overflow:hidden}.dialog-header{display:flex;align-items:center;gap:12px;padding:14px 16px!important;background:rgba(var(--v-theme-on-surface),.025);border-bottom:1px solid rgba(var(--v-theme-on-surface),.08)!important}.dialog-avatar{width:48px;height:48px;border-radius:14px;background:rgba(245,158,11,.12);display:grid;place-items:center;font-size:25px;flex:0 0 48px}.batch-gift-avatar{color:#f59e0b}.stats-avatar{color:#3b82f6;background:rgba(59,130,246,.12)}.dialog-copy{flex:1;min-width:0}.dialog-copy strong,.dialog-copy small{display:block}.dialog-copy strong{font-size:15px;color:rgba(var(--v-theme-on-surface),.84)}.dialog-copy small{margin-top:3px;font-size:11px;color:rgba(var(--v-theme-on-surface),.5)}.dialog-body{display:grid;gap:4px;padding:18px 18px 4px!important}.dialog-actions{padding:10px 16px 16px!important}.dialog-actions :deep(.v-spacer){flex:1 1 auto!important}.confirm-alert{margin-top:4px}.batch-gift-body{gap:12px!important}.batch-gift-list{display:flex;flex-direction:column;gap:8px;max-height:430px;overflow-y:auto;padding:2px}.batch-gift-row{display:grid;grid-template-columns:auto minmax(0,1fr) minmax(120px,150px);align-items:center;gap:10px;padding:10px 12px;border-radius:12px;background:rgba(var(--v-theme-on-surface),.025);border:1px solid rgba(var(--v-theme-on-surface),.08);transition:border-color .16s ease,background .16s ease}.batch-gift-row--selected{background:rgba(245,158,11,.08);border-color:rgba(245,158,11,.24)}.batch-gift-item{display:flex;align-items:center;gap:10px;min-width:0}.batch-gift-item__icon{width:38px;height:38px;border-radius:10px;display:grid;place-items:center;background:rgba(245,158,11,.12);font-size:22px;flex:0 0 38px}.batch-gift-item__copy{min-width:0}.batch-gift-item__copy strong,.batch-gift-item__copy small{display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.batch-gift-item__copy strong{font-size:13px;color:rgba(var(--v-theme-on-surface),.82)}.batch-gift-item__copy small{margin-top:3px;font-size:10px;color:rgba(var(--v-theme-on-surface),.5)}.stats-dialog-body{padding:16px!important}.stats-filters{display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:14px}.stats-applied-filter{margin:-2px 0 10px;font-size:11px;color:rgba(var(--v-theme-on-surface),.52)}.summary-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-bottom:14px}.summary-stat{padding:13px;border-radius:12px;background:rgba(59,130,246,.09);border:1px solid rgba(59,130,246,.16);text-align:center}.summary-stat span,.summary-stat strong{display:block}.summary-stat span{font-size:11px;color:rgba(var(--v-theme-on-surface),.52)}.summary-stat strong{margin-top:4px;font-size:22px;color:#3b82f6}.stats-columns{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.stats-section{min-width:0;padding:12px;border-radius:12px;background:rgba(var(--v-theme-surface),.66);border:1px solid rgba(var(--v-theme-on-surface),.07)}.stats-section h3{margin:0 0 8px;font-size:13px;color:rgba(var(--v-theme-on-surface),.8)}.stats-list{display:flex;flex-direction:column}.stats-row{display:flex;align-items:center;justify-content:space-between;gap:10px;padding:8px 2px;border-bottom:1px solid rgba(var(--v-theme-on-surface),.06)}.stats-row:last-child{border-bottom:none}.stats-row span{min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:12px;font-weight:700}.stats-row small{white-space:nowrap;color:rgba(var(--v-theme-on-surface),.5)}.stats-empty{padding:20px 8px;text-align:center;font-size:12px;color:rgba(var(--v-theme-on-surface),.48)}
.page-skeleton{display:flex;flex-direction:column}.skeleton-shell,.skeleton-card{pointer-events:none}.skeleton-panel{padding:16px;pointer-events:none}.sk{position:relative;overflow:hidden;border-radius:10px;background:rgba(var(--v-theme-on-surface),.075);border:1px solid rgba(var(--v-theme-on-surface),.035)}.sk::after{content:"";position:absolute;inset:0;transform:translateX(-100%);background:linear-gradient(90deg,transparent,rgba(var(--v-theme-surface),.46),transparent);animation:skeleton-shimmer 1.25s infinite}.sk-icon{width:38px;height:38px;flex:0 0 38px}.sk-lines{flex:1}.sk-line{height:16px;margin-top:7px}.sk-line.short{width:58%;height:11px;margin-top:0}.sk-title{width:132px;height:18px}.sk-action{height:76px;margin-top:8px}.sk-row{height:38px;margin-top:12px}@keyframes skeleton-shimmer{100%{transform:translateX(100%)}}
@media(max-width:1100px){.primary-grid{grid-template-columns:1fr}}
@media(max-width:900px){.overview-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.resource-grid,.recipe-grid,.stats-columns{grid-template-columns:1fr}.exchange-action-panel{grid-template-columns:1fr}.exchange-action-panel :deep(.v-btn){width:100%}}
@media(max-width:600px){.siqi-page{padding:14px}.siqi-topbar{align-items:flex-start;gap:10px}.siqi-topbar__right :deep(.v-btn){min-width:44px!important;padding-inline:0!important}.overview-grid>.v-col{padding:4px!important}.stat-card{padding:10px;gap:8px}.stat-icon{width:34px;height:34px;flex-basis:34px}.stat-value{font-size:17px}.card-subtitle{display:none}.schedule-board-body{padding:14px!important}.neu-action-card{grid-template-columns:32px minmax(0,1fr);row-gap:10px;padding:12px}.schedule-action{grid-column:1/-1;width:100%}.schedule-meta span{flex:1 1 100%}.exchange-summary{grid-template-columns:1fr}.siqi-card-title--inventory{flex-wrap:wrap;gap:8px}.siqi-card-title--inventory :deep(.v-spacer){display:none}.inventory-title-actions{width:100%;justify-content:stretch}.inventory-title-actions :deep(.v-btn){flex:1 1 0}.inventory-grid{grid-template-columns:1fr}.recipe-controls{grid-template-columns:1fr}.recipe-controls :deep(.v-btn){width:100%}.batch-gift-row{grid-template-columns:auto minmax(0,1fr)}.batch-gift-row :deep(.v-input){grid-column:2}.history-item{grid-template-columns:minmax(0,1fr) auto;gap:6px;padding-inline:10px}.history-detail{font-size:11px}.history-time{text-align:right;white-space:nowrap}.dialog-header{align-items:flex-start}.dialog-avatar{width:42px;height:42px;flex-basis:42px}.stats-filters{align-items:stretch;flex-direction:column}.stats-filters :deep(.v-btn-toggle),.stats-filters :deep(.v-btn){width:100%}.stats-filters :deep(.v-btn-toggle .v-btn){flex:1}.summary-grid{grid-template-columns:1fr}}
</style>
