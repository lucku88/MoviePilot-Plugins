import assert from 'node:assert/strict'
import { logMatchesCard } from '../src/utils/logMatching.js'

const newApiCardA = {
  card_id: 'newapi-checkin-a',
  module_key: 'newapi_checkin',
  site_name: 'New API',
  site_url: 'https://api-a.example.com',
  uid: '1001',
  title: 'New API 签到',
}

const newApiCardB = {
  card_id: 'newapi-checkin-b',
  module_key: 'newapi_checkin',
  site_name: 'New API',
  site_url: 'https://api-b.example.com',
  uid: '2002',
  title: 'New API 签到',
}

assert.equal(
  logMatchesCard(
    {
      card_id: 'newapi-checkin-b',
      module_key: 'newapi_checkin',
      site_name: 'New API',
      site_url: 'https://api-b.example.com',
      uid: '2002',
      title: 'New API 签到',
    },
    newApiCardA,
  ),
  false,
  '不同 card_id 的复制卡片不能互相显示日志',
)

assert.equal(
  logMatchesCard(
    {
      module_key: 'newapi_checkin',
      site_name: 'New API',
      site_url: 'https://api-a.example.com',
      uid: '1001',
      title: 'New API 签到',
    },
    newApiCardA,
  ),
  true,
  '旧日志没有 card_id 时，New API 可按站点地址和 UID 归属到卡片',
)

assert.equal(
  logMatchesCard(
    {
      module_key: 'newapi_checkin',
      site_name: 'New API',
      site_url: 'https://api-a.example.com',
      uid: '9999',
      title: 'New API 签到',
    },
    newApiCardA,
  ),
  false,
  '旧 New API 日志 UID 不同不能只靠站点名称混入',
)

assert.equal(
  logMatchesCard(
    {
      module_key: 'newapi_checkin',
      site_name: 'New API',
      site_url: 'https://api-b.example.com',
      uid: '2002',
      title: 'New API 签到',
    },
    newApiCardA,
  ),
  false,
  '旧 New API 日志站点不同不能只靠标题混入',
)

assert.equal(
  logMatchesCard(
    {
      card_id: 'newapi-checkin-b',
      module_key: 'newapi_checkin',
      site_name: 'New API',
      site_url: 'https://api-b.example.com',
      uid: '2002',
      title: 'New API 签到',
    },
    newApiCardB,
  ),
  true,
  '相同 card_id 的日志仍然正常显示',
)
