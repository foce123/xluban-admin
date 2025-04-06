import request from '@/utils/request'

// 查询环境列表
export function listEnv(query) {
  return request({
    url: '/deployment/environment/list',
    method: 'get',
    params: query
  })
}

// 查询环境详细
export function getEnv(envId) {
  return request({
    url: '/deployment/environment/' + envId,
    method: 'get'
  })
}

// 新增环境
export function addEnv(data) {
  return request({
    url: '/deployment/environment',
    method: 'post',
    data: data
  })
}

// 修改环境
export function updateEnv(data) {
  return request({
    url: '/deployment/environment',
    method: 'put',
    data: data
  })
}

// 删除环境
export function delEnv(envId) {
  return request({
    url: '/deployment/environment/' + envId,
    method: 'delete'
  })
}