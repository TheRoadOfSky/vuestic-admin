<template>
  <div class="bundle-viewer">
    <h1 class="page-title">Asset-Packer 依赖查看器</h1>

    <div class="mb-4">
      <VaInput v-model="searchQuery" placeholder="搜索 Asset/Bundle/GUID..." class="mr-2" style="width: 300px" />
      <VaButton @click="loadOldJson">加载旧日志对比</VaButton>
      <input ref="fileInput" type="file" accept=".json" style="display: none" @change="handleFileSelect" />
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
      <div v-html="bundleDetailContent"></div>
    </VaModal>

    <!-- Compare Result Modal -->
    <VaModal v-model="showCompareResult" hide-default-actions size="large">
      <template #header>
        <h3>对比结果</h3>
      </template>
      <pre>{{ compareResult }}</pre>
    </VaModal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { VaCard, VaCardContent, VaDataTable, VaInput, VaButton, VaModal } from 'vuestic-ui'

// 数据状态
const loading = ref(true)
const jsonData = ref<any>(null)
const oldJsonData = ref<any>(null)

// 搜索和过滤
const searchQuery = ref('')

// 显示控制
const showBundleDetail = ref(false)
const bundleDetailContent = ref('')
const selectedAsset = ref('')

const showCompareResult = ref(false)
const compareResult = ref('')

// 文件输入引用
const fileInput = ref<HTMLInputElement | null>(null)

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
  const normalized: any = { assets: {}, bundles: raw.bundles || {} }

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

  return normalized
}

// 过滤后的资产列表
const filteredAssets = computed(() => {
  if (!jsonData.value || !jsonData.value.assets) return []

  const assets = Object.keys(jsonData.value.assets)
  const query = searchQuery.value.toLowerCase()

  return assets
    .filter((asset) => asset.toLowerCase().includes(query))
    .map((asset) => ({
      asset,
      bundleCount: Object.keys(jsonData.value!.assets[asset]).length,
    }))
})

// 显示资产的 bundles
const showBundles = (rowData: any) => {
  const asset = typeof rowData === 'string' ? rowData : rowData.asset
  selectedAsset.value = asset

  const bundles = jsonData.value.assets[asset]
  let html = '<ul>'

  Object.keys(bundles).forEach((bundle) => {
    const guids = bundles[bundle]
    html += `<li>Bundle: ${bundle} (GUIDs: ${guids.length}) <button onclick="window.showBundleContent('${bundle}')" style="margin-left: 10px;" class="va-button va-button--small va-button--primary">查看内容</button><ul>`
    guids.forEach((g: string) => (html += `<li>GUID: ${g}</li>`))
    html += '</ul></li>'
  })

  html += '</ul>'
  bundleDetailContent.value = html
  showBundleDetail.value = true
}

// 显示 bundle 内容
const showBundleContent = (bundleHash: string) => {
  const bundle = jsonData.value.bundles[bundleHash]
  if (!bundle) {
    alert('Bundle 未找到')
    return
  }

  let html = bundleDetailContent.value
  html += `<h4>Bundle ${bundleHash} (CRC: ${bundle.crc})</h4><ul>`
  bundle.files.forEach((f: any) => {
    html += `<li>${f.asset_path} (GUID: ${f.guid}, 大小: ${f.size || '未知'})</li>`
  })
  html += `</ul><p>总文件: ${bundle.files.length}</p>`

  bundleDetailContent.value = html
}

// 加载旧 JSON 文件
const loadOldJson = () => {
  if (fileInput.value) {
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
      performCompare()
    } catch (error) {
      console.error('Failed to parse old JSON:', error)
    }
  }
  reader.readAsText(file)
}

// 执行对比
const performCompare = () => {
  if (!jsonData.value || !oldJsonData.value) return

  const changes: any = { addedAssets: [], removedAssets: [], bundleChanges: {} }

  // 对比 Assets
  Object.keys(jsonData.value.assets).forEach((asset) => {
    if (!oldJsonData.value.assets[asset]) changes.addedAssets.push(asset)
  })

  Object.keys(oldJsonData.value.assets).forEach((asset) => {
    if (!jsonData.value.assets[asset]) changes.removedAssets.push(asset)
  })

  // 对比 Bundles
  Object.keys(jsonData.value.bundles).forEach((bundle) => {
    if (!oldJsonData.value.bundles[bundle]) {
      changes.bundleChanges[bundle] = { status: 'added', files: jsonData.value.bundles[bundle].files }
    } else if (
      JSON.stringify(jsonData.value.bundles[bundle].files) !== JSON.stringify(oldJsonData.value.bundles[bundle].files)
    ) {
      changes.bundleChanges[bundle] = { status: 'modified', files: jsonData.value.bundles[bundle].files }
    }
  })

  Object.keys(oldJsonData.value.bundles).forEach((bundle) => {
    if (!jsonData.value.bundles[bundle]) {
      changes.bundleChanges[bundle] = { status: 'removed' }
    }
  })

  compareResult.value = JSON.stringify(changes, null, 2)
  showCompareResult.value = true
}

// 组件挂载时获取数据
onMounted(() => {
  fetchData()

  // 将 showBundleContent 方法暴露到全局作用域，以便在 HTML 中调用
  ;(window as any).showBundleContent = showBundleContent
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
</style>
