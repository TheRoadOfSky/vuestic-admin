<template>
  <div class="bundle-viewer">
    <h1 class="page-title">Asset-Packer 依赖查看器</h1>

    <div class="mb-4">
      <VaInput
        v-model="searchQuery"
        placeholder="搜索 Asset 路径、Bundle Hash 或 GUID..."
        class="mr-2"
        style="width: 300px"
      />
    </div>

    <VaCard>
      <VaCardContent>
        <VaDataTable :items="filteredAssets" :columns="assetColumns" :loading="loading" @rowClicked="showBundles">
          <template #cell(actions)="{ rowData }">
            <VaButton size="small" @click.stop="showBundles(rowData)"> 查看依赖 </VaButton>
          </template>
        </VaDataTable>
      </VaCardContent>
    </VaCard>

    <!-- Bundle Detail Modal -->
    <VaModal v-model="showBundleDetail" hide-default-actions size="large">
      <template #header>
        <h3>{{ selectedAsset }} 依赖详情</h3>
      </template>
      <div class="bundle-details-container">
        <div class="modal-search-box">
          <VaInput
            v-model="detailSearchQuery"
            placeholder="搜索 Bundle Hash, GUID 或 Asset Path..."
            style="width: 100%; margin-bottom: 15px"
          />
        </div>
        <div class="bundle-details-header">
          <div class="bundle-hash-column">Bundle Hash</div>
          <div class="guids-column">GUIDs</div>
          <div class="asset-path-column">Asset Paths</div>
        </div>
        <div v-for="item in filteredBundleDetailItems" :key="item.bundle" class="bundle-item">
          <div class="bundle-hash-column">{{ item.bundle }}</div>
          <div class="guids-column">
            <div v-for="guidDetail in item.guids" :key="guidDetail.guid" class="guid-item">
              {{ guidDetail.guid }}
            </div>
          </div>
          <div class="asset-path-column">
            <div v-for="guidDetail in item.guids" :key="guidDetail.guid" class="asset-path-item">
              {{ guidDetail.assetPath }}
            </div>
          </div>
        </div>
      </div>
    </VaModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { VaCard, VaCardContent, VaDataTable, VaInput, VaButton, VaModal } from 'vuestic-ui'

// 数据状态
const loading = ref(true)
const jsonData = ref<any>(null)

// 搜索和过滤
const searchQuery = ref('')
const detailSearchQuery = ref('')

// 显示控制
const showBundleDetail = ref(false)
const selectedAsset = ref('')

// Bundle 详情数据
const bundleDetailItems = ref<any[]>([])

// 表格列定义
const assetColumns = [
  { key: 'asset', label: 'Asset 路径', sortable: true },
  { key: 'bundleCount', label: '依赖 Bundle 数', sortable: true },
  { key: 'actions', label: '操作' },
]

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

// 过滤后的资产列表
const filteredAssets = computed(() => {
  if (!jsonData.value || !jsonData.value.assets) return []

  const assets = Object.keys(jsonData.value.assets)
  const query = searchQuery.value.toLowerCase()

  if (!query) {
    return assets.map((asset) => ({
      asset,
      bundleCount: Object.keys(jsonData.value!.assets[asset]).length,
    }))
  }

  return assets
    .filter((asset) => {
      // 检查 asset 路径
      if (asset.toLowerCase().includes(query)) {
        return true
      }

      // 检查该 asset 依赖的 bundles 和 guids
      const bundles = jsonData.value.assets[asset]
      for (const bundleHash in bundles) {
        // 检查 bundle hash
        if (bundleHash.toLowerCase().includes(query)) {
          return true
        }

        // 检查 guids
        const guids = bundles[bundleHash]
        if (guids.some((guid: string) => guid.toLowerCase().includes(query))) {
          return true
        }

        // 检查每个 guid 对应的 asset path
        for (const guid of guids) {
          const bundleData = jsonData.value.bundles[bundleHash]
          if (bundleData && bundleData.files) {
            const file = bundleData.files.find((f: any) => f.guid === guid)
            if (file && file.assetPath && file.assetPath.toLowerCase().includes(query)) {
              return true
            }
          }
        }
      }

      return false
    })
    .map((asset) => ({
      asset,
      bundleCount: Object.keys(jsonData.value!.assets[asset]).length,
    }))
})

// 过滤后的 Bundle 详情项
const filteredBundleDetailItems = computed(() => {
  if (!bundleDetailItems.value) return []

  const query = detailSearchQuery.value.toLowerCase()

  if (!query) {
    return bundleDetailItems.value
  }

  return bundleDetailItems.value
    .map((item) => {
      // 过滤 GUID 和 Asset Path
      const filteredGuids = item.guids.filter(
        (guidDetail: any) =>
          item.bundle.toLowerCase().includes(query) ||
          guidDetail.guid.toLowerCase().includes(query) ||
          guidDetail.assetPath.toLowerCase().includes(query),
      )

      return {
        ...item,
        guids: filteredGuids,
      }
    })
    .filter((item: any) => item.bundle.toLowerCase().includes(query) || item.guids.length > 0)
})

// 显示资产的 bundles
const showBundles = (rowData: any) => {
  const asset = typeof rowData === 'string' ? rowData : rowData.asset
  selectedAsset.value = asset

  // 准备表格数据
  const bundles = jsonData.value.assets[asset]
  const items: any[] = []

  Object.keys(bundles).forEach((bundle) => {
    const guids = bundles[bundle]
    // 获取每个 GUID 对应的 asset path
    const guidDetails = guids.map((guid: string) => {
      // 在 bundle 中查找对应的 asset path
      const bundleData = jsonData.value.bundles[bundle]
      if (bundleData && bundleData.files) {
        const file = bundleData.files.find((f: any) => f.guid === guid)
        return {
          guid,
          assetPath: file ? file.assetPath : 'Unknown',
        }
      }
      return {
        guid,
        assetPath: 'Unknown',
      }
    })

    items.push({
      bundle,
      guids: guidDetails,
    })
  })

  bundleDetailItems.value = items
  showBundleDetail.value = true
}

// 组件挂载时获取数据
onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.bundle-viewer {
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

.guid-item {
  margin-bottom: 2px;
  padding: 2px 0;
  min-height: 20px;
  line-height: 20px;
  word-break: break-all;
}

.asset-path-item {
  margin-bottom: 2px;
  padding: 2px 0;
  min-height: 20px;
  line-height: 20px;
  word-break: break-all;
}

.bundle-details-container {
  display: flex;
  flex-direction: column;
  width: 100%;
}

.modal-search-box {
  padding: 10px;
  border-bottom: 1px solid #eee;
}

.bundle-details-header {
  display: flex;
  font-weight: bold;
  padding: 10px 0;
  border-bottom: 2px solid #ddd;
  background-color: #f8f9fa;
}

.bundle-item {
  display: flex;
  padding: 10px 0;
  border-bottom: 1px solid #eee;
  min-height: 40px;
}

.bundle-item:last-child {
  border-bottom: none;
}

.bundle-hash-column {
  flex: 0 0 25%;
  padding-right: 10px;
  word-break: break-all;
  align-self: flex-start;
}

.guids-column {
  flex: 0 0 25%;
  padding: 0 10px;
  border-left: 1px solid #eee;
  word-break: break-all;
}

.asset-path-column {
  flex: 0 0 50%;
  padding-left: 10px;
  border-left: 1px solid #eee;
  word-break: break-all;
}

.bundle-header {
  font-weight: bold;
  margin-bottom: 5px;
  color: #333;
}

.guids-container {
  padding-left: 10px;
}
</style>
