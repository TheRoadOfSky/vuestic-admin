<template>
  <div class="asset-lookup">
    <h1 class="page-title">Asset 查找</h1>

    <div class="search-section mb-4">
      <VaInput
        v-model="searchQuery"
        placeholder="搜索 Asset 路径、GUID 或 Bundle Hash..."
        class="mr-2"
        style="width: 300px"
      />
    </div>

    <VaCard>
      <VaCardContent>
        <VaDataTable :items="filteredAssetItems" :columns="assetColumns" :loading="loading" />
      </VaCardContent>
    </VaCard>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { VaCard, VaCardContent, VaDataTable, VaInput } from 'vuestic-ui'

// 数据状态
const loading = ref(true)
const jsonData = ref<any>(null)

// 搜索查询
const searchQuery = ref('')

// 表格列定义
const assetColumns = [
  { key: 'assetPath', label: 'Asset 路径', sortable: true },
  { key: 'guid', label: 'GUID', sortable: true },
  { key: 'bundleHash', label: 'Bundle Hash', sortable: true },
  {
    key: 'fileSize',
    label: '文件大小',
    sortable: true,
    formatter: (value: number) => formatFileSize(value),
  },
]

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  if (!bytes) return 'Unknown'

  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 获取数据
const fetchData = async () => {
  try {
    loading.value = true
    const response = await fetch('/build_log.json')
    const rawData = await response.json()
    jsonData.value = normalizeData(rawData)
    loading.value = false
  } catch (error) {
    console.error('Failed to load build log:', error)
    loading.value = false
  }
}

// 标准化数据格式
const normalizeData = (raw: any) => {
  const normalized: any = { assets: {}, bundles: {} }

  // 处理 assets 数据
  if (raw.assets && Array.isArray(raw.assets)) {
    raw.assets.forEach((asset: any) => {
      normalized.assets[asset.first] = {}
      if (asset.second && Array.isArray(asset.second)) {
        asset.second.forEach((bundle: any) => {
          normalized.assets[asset.first][bundle.first] = bundle.second || []
        })
      }
    })
  } else if (raw.assets && typeof raw.assets === 'object') {
    normalized.assets = raw.assets // 兼容旧格式
  }

  // 处理 bundles 数据
  if (raw.bundles && Array.isArray(raw.bundles)) {
    raw.bundles.forEach((bundle: any) => {
      // bundle.first 是 hash，bundle.second 包含 crc 和 files
      normalized.bundles[bundle.first] = {
        crc: bundle.second?.crc || '',
        files: bundle.second?.files || [],
      }
    })
  }

  return normalized
}

// 构建 asset 到 bundle 的映射
const buildAssetToBundleMap = () => {
  const assetToBundleMap: any[] = []

  if (!jsonData.value || !jsonData.value.bundles) return assetToBundleMap

  // 遍历所有 bundles
  Object.keys(jsonData.value.bundles).forEach((bundleHash) => {
    const bundle = jsonData.value.bundles[bundleHash]

    if (bundle.files && Array.isArray(bundle.files)) {
      bundle.files.forEach((file: any) => {
        if (file.asset_path) {
          assetToBundleMap.push({
            assetPath: file.asset_path,
            bundleHash: bundleHash,
            guid: file.guid || '',
            fileSize: file.size || 0,
          })
        }
      })
    }
  })

  return assetToBundleMap
}

// 过滤后的 asset 项目
const filteredAssetItems = computed(() => {
  const assetToBundleMap = buildAssetToBundleMap()
  const query = searchQuery.value.toLowerCase()

  if (!query) {
    return assetToBundleMap
  }

  return assetToBundleMap.filter(
    (item) =>
      item.assetPath.toLowerCase().includes(query) ||
      (item.guid && item.guid.toLowerCase().includes(query)) ||
      (item.bundleHash && item.bundleHash.toLowerCase().includes(query)),
  )
})

// 组件挂载时获取数据
onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.asset-lookup {
  padding: 20px;
}

.page-title {
  margin-bottom: 20px;
}

.mb-4 {
  margin-bottom: 1rem;
}

.mr-2 {
  margin-right: 0.5rem;
}

.search-section {
  display: flex;
  align-items: center;
}
</style>
