<template>
  <div class="bundle-detail-viewer">
    <h1 class="page-title">Bundle 内容查看器</h1>

    <div class="mb-4">
      <VaInput v-model="searchQuery" placeholder="搜索 Bundle Hash 或 Asset..." class="mr-2" style="width: 300px" />
    </div>

    <VaCard>
      <VaCardContent>
        <VaDataTable
          :items="filteredBundles"
          :columns="bundleColumns"
          :loading="loading"
          @rowClicked="showBundleDetail"
        >
          <template #cell(actions)="{ rowData }">
            <VaButton size="small" @click.stop="showBundleDetail(rowData)"> 查看内容 </VaButton>
          </template>
        </VaDataTable>
      </VaCardContent>
    </VaCard>

    <!-- Bundle Detail Modal -->
    <VaModal v-model="showBundleDetailModal" hide-default-actions size="large">
      <template #header>
        <h3>Bundle: {{ selectedBundleHash }}</h3>
      </template>
      <div>
        <p v-if="selectedBundle && selectedBundle.crc"><strong>CRC:</strong> {{ selectedBundle.crc }}</p>
        <p><strong>文件总数:</strong> {{ selectedBundleFiles ? selectedBundleFiles.length : 0 }}</p>

        <VaInput v-model="fileSearchQuery" placeholder="搜索文件..." class="my-2" style="width: 300px" />

        <VaDataTable :items="filteredBundleFiles" :columns="fileColumns" :loading="false" />
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
const fileSearchQuery = ref('')

// 显示控制
const showBundleDetailModal = ref(false)
const selectedBundleHash = ref('')
const selectedBundle = ref<any>(null)

// 表格列定义
const bundleColumns = [
  { key: 'hash', label: 'Bundle Hash', sortable: true },
  { key: 'crc', label: 'CRC', sortable: true },
  { key: 'fileCount', label: '文件数', sortable: true },
  { key: 'bundleSize', label: 'Bundle 大小', sortable: true },
  { key: 'actions', label: '操作' },
]

const fileColumns = [
  { key: 'asset_path', label: 'Asset 路径', sortable: true },
  { key: 'guid', label: 'GUID', sortable: true },
  {
    key: 'size',
    label: '大小',
    sortable: true,
    formatter: (value: number) => formatFileSize(value),
  },
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

// 过滤后的 bundles 列表
const filteredBundles = computed(() => {
  if (!jsonData.value || !jsonData.value.bundles) return []

  // 将 bundles 对象转换为数组
  const bundlesArray = Object.keys(jsonData.value.bundles).map((hash) => ({
    hash,
    ...jsonData.value.bundles[hash],
  }))

  const query = searchQuery.value.toLowerCase()

  return bundlesArray
    .filter((bundle) => {
      // 检查是否匹配 hash 或文件路径
      const hashMatch = bundle.hash.toLowerCase().includes(query)

      const fileMatch =
        bundle.files &&
        bundle.files.some((file: any) => file && file.asset_path && file.asset_path.toLowerCase().includes(query))

      return hashMatch || fileMatch
    })
    .map((bundle) => ({
      hash: bundle.hash,
      crc: bundle.crc,
      fileCount: bundle.files ? bundle.files.length : 0,
      bundleSize: formatFileSize(getBundleSize(bundle.files)),
    }))
})

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 Bytes'
  if (!bytes) return 'Unknown'

  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 获取 bundle 总大小
const getBundleSize = (files: any[]): number => {
  if (!files || !Array.isArray(files)) return 0
  return files.reduce((total, file) => {
    return total + (file.size || 0)
  }, 0)
}

// 选中的 bundle 文件列表
const selectedBundleFiles = computed(() => {
  if (!selectedBundle.value) return []
  return selectedBundle.value.files || []
})

// 过滤后的 bundle 文件列表
const filteredBundleFiles = computed(() => {
  const query = fileSearchQuery.value.toLowerCase()
  return selectedBundleFiles.value.filter(
    (file: any) => file.asset_path.toLowerCase().includes(query) || file.guid.toLowerCase().includes(query),
  )
})

// 显示 bundle 详情
const showBundleDetail = (rowData: any) => {
  const hash = typeof rowData === 'string' ? rowData : rowData.hash
  selectedBundleHash.value = hash
  selectedBundle.value = jsonData.value.bundles[hash]
  showBundleDetailModal.value = true
}

// 组件挂载时获取数据
onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.bundle-detail-viewer {
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

.my-2 {
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
}
</style>
