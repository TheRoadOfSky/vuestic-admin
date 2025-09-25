<template>
  <div class="log-comparison">
    <h1 class="page-title">日志对比</h1>

    <div class="comparison-controls mb-4">
      <VaButton @click="loadOldJson">加载旧日志对比</VaButton>
      <input ref="fileInput" type="file" accept=".json" style="display: none" @change="handleFileSelect" />
    </div>

    <!-- Comparison Tables Container -->
    <div v-if="oldJsonData" class="comparison-container">
      <!-- Asset Comparison Table -->
      <div class="comparison-table">
        <h2 class="section-title">Asset 对比结果</h2>
        <VaCard>
          <VaCardContent>
            <VaDataTable :items="assetComparisonData" :columns="assetComparisonColumns" :loading="loading">
              <template #cell(status)="{ rowData }">
                <span :class="getCellClass(rowData.status)">{{ rowData.status }}</span>
              </template>
            </VaDataTable>
          </VaCardContent>
        </VaCard>
      </div>

      <!-- Bundle Comparison Table -->
      <div class="comparison-table">
        <h2 class="section-title">Bundle 对比结果</h2>
        <VaCard>
          <VaCardContent>
            <VaDataTable :items="bundleComparisonData" :columns="bundleComparisonColumns" :loading="loading">
              <template #cell(status)="{ rowData }">
                <span :class="getCellClass(rowData.status)">{{ rowData.status }}</span>
              </template>
            </VaDataTable>
          </VaCardContent>
        </VaCard>
      </div>
    </div>

    <!-- No Data Message -->
    <div v-if="!oldJsonData && !loading" class="no-data-message">
      <p>请加载旧日志文件以进行对比。</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { VaCard, VaCardContent, VaDataTable, VaButton } from 'vuestic-ui'

// 数据状态
const loading = ref(true)
const currentJsonData = ref<any>(null)
const oldJsonData = ref<any>(null)

// 文件输入引用
const fileInput = ref<HTMLInputElement | null>(null)

// 表格列定义
const assetComparisonColumns = [
  { key: 'asset', label: 'Asset 路径' },
  { key: 'status', label: '状态' },
]

const bundleComparisonColumns = [
  { key: 'bundle', label: 'Bundle Hash' },
  { key: 'status', label: '状态' },
]

// 获取当前数据
const fetchData = async () => {
  try {
    loading.value = true
    const response = await fetch('/build_log.json')
    const rawData = await response.json()
    currentJsonData.value = normalizeData(rawData)
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

// 加载旧 JSON 文件
const loadOldJson = () => {
  if (fileInput.value) {
    // 重置文件输入，确保每次都能触发 change 事件
    fileInput.value.value = ''
    fileInput.value.click()
  }
}

// 处理文件选择
const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]

  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const rawData = JSON.parse(e.target?.result as string)
      oldJsonData.value = normalizeData(rawData)
    } catch (error) {
      console.error('Failed to parse old JSON:', error)
    }
  }
  reader.readAsText(file)
}

// Asset 对比数据
const assetComparisonData = computed(() => {
  if (!currentJsonData.value || !oldJsonData.value) return []

  const changes: any[] = []

  // 新增的 Assets
  Object.keys(currentJsonData.value.assets).forEach((asset) => {
    if (!oldJsonData.value.assets[asset]) {
      changes.push({ asset, status: '新增' })
    }
  })

  // 删除的 Assets
  Object.keys(oldJsonData.value.assets).forEach((asset) => {
    if (!currentJsonData.value.assets[asset]) {
      changes.push({ asset, status: '删除' })
    }
  })

  // 修改的 Assets (对比 bundle 和 GUID)
  Object.keys(currentJsonData.value.assets).forEach((asset) => {
    if (oldJsonData.value.assets[asset]) {
      const currentAssetData = currentJsonData.value.assets[asset]
      const oldAssetData = oldJsonData.value.assets[asset]

      // 对比 bundle 和对应的 GUID
      let isModified = false

      // 检查是否有新增或删除的 bundles
      const currentBundles = Object.keys(currentAssetData)
      const oldBundles = Object.keys(oldAssetData)

      if (currentBundles.length !== oldBundles.length) {
        isModified = true
      } else {
        // 检查每个 bundle 及其 GUID
        for (const bundle of currentBundles) {
          if (!oldAssetData[bundle]) {
            isModified = true
            break
          }

          // 对比 GUID 数组
          const currentGuids = currentAssetData[bundle]
          const oldGuids = oldAssetData[bundle]

          if (JSON.stringify(currentGuids.sort()) !== JSON.stringify(oldGuids.sort())) {
            isModified = true
            break
          }
        }
      }

      if (isModified && !changes.some((item) => item.asset === asset)) {
        changes.push({ asset, status: '修改' })
      }
    }
  })

  return changes
})

// Bundle 对比数据
const bundleComparisonData = computed(() => {
  if (!currentJsonData.value || !oldJsonData.value) return []

  const changes: any[] = []

  // 新增的 Bundles
  Object.keys(currentJsonData.value.bundles).forEach((bundle) => {
    if (!oldJsonData.value.bundles[bundle]) {
      changes.push({ bundle, status: '新增' })
    }
  })

  // 删除的 Bundles
  Object.keys(oldJsonData.value.bundles).forEach((bundle) => {
    if (!currentJsonData.value.bundles[bundle]) {
      changes.push({ bundle, status: '删除' })
    }
  })

  // 修改的 Bundles
  Object.keys(currentJsonData.value.bundles).forEach((bundle) => {
    if (oldJsonData.value.bundles[bundle]) {
      if (
        JSON.stringify(currentJsonData.value.bundles[bundle].files) !==
        JSON.stringify(oldJsonData.value.bundles[bundle].files)
      ) {
        changes.push({ bundle, status: '修改' })
      }
    }
  })

  return changes
})

// 获取行的 CSS 类
const getCellClass = (status: string) => {
  switch (status) {
    case '新增':
      return 'cell-added'
    case '删除':
      return 'cell-removed'
    case '修改':
      return 'cell-modified'
    default:
      return ''
  }
}

// 组件挂载时获取数据
onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.log-comparison {
  padding: 20px;
}

.page-title {
  margin-bottom: 20px;
}

.section-title {
  margin-bottom: 15px;
  font-size: 1.5rem;
  font-weight: bold;
}

.mb-4 {
  margin-bottom: 1rem;
}

.comparison-controls {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 20px;
}

.comparison-container {
  display: flex;
  gap: 20px;
  flex-wrap: wrap;
}

.comparison-table {
  flex: 1;
  min-width: 300px;
}

.no-data-message {
  text-align: center;
  padding: 40px;
  color: #666;
}

.cell-added {
  background-color: #e8f5e9; /* 浅绿色 */
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: bold;
  color: #2e7d32;
}

.cell-removed {
  background-color: #ffebee; /* 浅红色 */
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: bold;
  color: #c62828;
}

.cell-modified {
  background-color: #e3f2fd; /* 浅蓝色 */
  padding: 4px 8px;
  border-radius: 4px;
  font-weight: bold;
  color: #1565c0;
}

@media (max-width: 768px) {
  .comparison-container {
    flex-direction: column;
  }
}
</style>
