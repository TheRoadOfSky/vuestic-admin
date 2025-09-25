export interface INavigationRoute {
  name: string
  displayName: string
  meta: { icon: string }
  children?: INavigationRoute[]
}

export default {
  root: {
    name: '/',
    displayName: 'navigationRoutes.home',
  },
  routes: [
    {
      name: 'dashboard',
      displayName: 'menu.dashboard',
      meta: {
        icon: 'vuestic-iconset-dashboard',
      },
    },
    {
      name: 'bundle-viewer',
      displayName: 'Bundle Viewer',
      meta: {
        icon: 'view_list',
      },
    },
    {
      name: 'bundle-detail-viewer',
      displayName: 'Bundle 详情',
      meta: {
        icon: 'description',
      },
    },
    {
      name: 'asset-lookup',
      displayName: 'Asset 查找',
      meta: {
        icon: 'manage_search',
      },
    },
    {
      name: 'log-comparison',
      displayName: '日志对比',
      meta: {
        icon: 'compare',
      },
    },
  ] as INavigationRoute[],
}
