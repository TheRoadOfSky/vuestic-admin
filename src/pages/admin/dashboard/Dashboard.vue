<template>
  <div class="dashboard">
    <h1 class="page-title font-bold">Tuanjie AssetPacker Build Log</h1>
    <div class="content">
      <p>欢迎使用 Tuanjie AssetPacker Build Log 查看器。</p>
      <p>请使用左侧导航栏选择要查看的工具：</p>
      <ul>
        <li>Bundle Viewer：查看本次构建中每个直接打包的 Asset 依赖的 Bundle 详细信息</li>
        <li>Bundle 详情：查看特定 Bundle 中包含的所有内容详情</li>
        <li>Asset 查找：通过 Asset 路径、GUID 或 Bundle Hash 查找相关信息</li>
        <li>日志对比：加载旧版本的构建日志文件，与当前版本进行对比，对比变化</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
// Tuanjie AssetPacker Build Log Dashboard
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.page-title {
  margin-bottom: 20px;
}

.content {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.content ul {
  margin-top: 10px;
  padding-left: 20px;
}

.content li {
  margin-bottom: 8px;
}

.instructions {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #dee2e6;
}

.instructions h3 {
  margin-bottom: 10px;
}

.instructions ol {
  padding-left: 20px;
}

.instructions li {
  margin-bottom: 8px;
}
</style>
