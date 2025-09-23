<template>
  <div class="dashboard">
    <h1 class="page-title font-bold">Tuanjie AssetPacker Build Log</h1>
    <div class="content">
      <p>欢迎使用 Tuanjie AssetPacker Build Log 查看器。</p>
      <p>请使用左侧导航栏选择要查看的工具：</p>
      <ul>
        <li>Bundle Viewer - 查看 Asset 依赖的 Bundle 信息</li>
        <li>Bundle 详情 - 查看 Bundle 的详细内容</li>
        <li>Asset 查找 - 根据 Asset 路径查找对应的 Bundle 信息</li>
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
</style>
