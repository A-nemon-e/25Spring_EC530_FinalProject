<template>
  <el-menu :default-active="$route.path" router>
    <el-menu-item index="/search">
      🔍 搜索
    </el-menu-item>
    <el-menu-item index="/folder/1e80e581-8016-4414-a284-be7804b65d29">
      📁 文件夹视图
    </el-menu-item>
    <el-menu-item index="/file/14f75053681">
      📄 文件详情视图
    </el-menu-item>
    <el-divider />
    <el-menu-item index="/tag-manager">
      🏷️ 标签管理
    </el-menu-item>
    <el-menu-item index="/alias-manager">
      🔁 别名设置
    </el-menu-item>
  </el-menu>
</template>
