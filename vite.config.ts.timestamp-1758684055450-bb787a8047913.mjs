// vite.config.ts
import { defineConfig } from "file:///D:/Code/github/my-bundle-viewer/node_modules/vite/dist/node/index.js";
import vue from "file:///D:/Code/github/my-bundle-viewer/node_modules/@vitejs/plugin-vue/dist/index.mjs";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "url";
import VueI18nPlugin from "file:///D:/Code/github/my-bundle-viewer/node_modules/@intlify/unplugin-vue-i18n/lib/vite.mjs";
import { vuestic } from "file:///D:/Code/github/my-bundle-viewer/node_modules/@vuestic/compiler/dist/vite/vite-plugin.js";
var __vite_injected_original_import_meta_url = "file:///D:/Code/github/my-bundle-viewer/vite.config.ts";
var vite_config_default = defineConfig({
  build: {
    sourcemap: true
  },
  plugins: [
    vuestic(),
    vue(),
    VueI18nPlugin({
      include: resolve(dirname(fileURLToPath(__vite_injected_original_import_meta_url)), "./src/i18n/locales/**")
    })
  ]
});
export {
  vite_config_default as default
};
//# sourceMappingURL=data:application/json;base64,ewogICJ2ZXJzaW9uIjogMywKICAic291cmNlcyI6IFsidml0ZS5jb25maWcudHMiXSwKICAic291cmNlc0NvbnRlbnQiOiBbImNvbnN0IF9fdml0ZV9pbmplY3RlZF9vcmlnaW5hbF9kaXJuYW1lID0gXCJEOlxcXFxDb2RlXFxcXGdpdGh1YlxcXFxteS1idW5kbGUtdmlld2VyXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ZpbGVuYW1lID0gXCJEOlxcXFxDb2RlXFxcXGdpdGh1YlxcXFxteS1idW5kbGUtdmlld2VyXFxcXHZpdGUuY29uZmlnLnRzXCI7Y29uc3QgX192aXRlX2luamVjdGVkX29yaWdpbmFsX2ltcG9ydF9tZXRhX3VybCA9IFwiZmlsZTovLy9EOi9Db2RlL2dpdGh1Yi9teS1idW5kbGUtdmlld2VyL3ZpdGUuY29uZmlnLnRzXCI7aW1wb3J0IHsgZGVmaW5lQ29uZmlnIH0gZnJvbSAndml0ZSdcbmltcG9ydCB2dWUgZnJvbSAnQHZpdGVqcy9wbHVnaW4tdnVlJ1xuaW1wb3J0IHsgcmVzb2x2ZSwgZGlybmFtZSB9IGZyb20gJ25vZGU6cGF0aCdcbmltcG9ydCB7IGZpbGVVUkxUb1BhdGggfSBmcm9tICd1cmwnXG5pbXBvcnQgVnVlSTE4blBsdWdpbiBmcm9tICdAaW50bGlmeS91bnBsdWdpbi12dWUtaTE4bi92aXRlJ1xuaW1wb3J0IHsgdnVlc3RpYyB9IGZyb20gJ0B2dWVzdGljL2NvbXBpbGVyL3ZpdGUnXG5cbi8vIGh0dHBzOi8vdml0ZWpzLmRldi9jb25maWcvXG5leHBvcnQgZGVmYXVsdCBkZWZpbmVDb25maWcoe1xuICBidWlsZDoge1xuICAgIHNvdXJjZW1hcDogdHJ1ZSxcbiAgfSxcbiAgcGx1Z2luczogW1xuICAgIHZ1ZXN0aWMoKSxcbiAgICB2dWUoKSxcbiAgICBWdWVJMThuUGx1Z2luKHtcbiAgICAgIGluY2x1ZGU6IHJlc29sdmUoZGlybmFtZShmaWxlVVJMVG9QYXRoKGltcG9ydC5tZXRhLnVybCkpLCAnLi9zcmMvaTE4bi9sb2NhbGVzLyoqJyksXG4gICAgfSksXG4gIF0sXG59KVxuIl0sCiAgIm1hcHBpbmdzIjogIjtBQUF1UixTQUFTLG9CQUFvQjtBQUNwVCxPQUFPLFNBQVM7QUFDaEIsU0FBUyxTQUFTLGVBQWU7QUFDakMsU0FBUyxxQkFBcUI7QUFDOUIsT0FBTyxtQkFBbUI7QUFDMUIsU0FBUyxlQUFlO0FBTHFKLElBQU0sMkNBQTJDO0FBUTlOLElBQU8sc0JBQVEsYUFBYTtBQUFBLEVBQzFCLE9BQU87QUFBQSxJQUNMLFdBQVc7QUFBQSxFQUNiO0FBQUEsRUFDQSxTQUFTO0FBQUEsSUFDUCxRQUFRO0FBQUEsSUFDUixJQUFJO0FBQUEsSUFDSixjQUFjO0FBQUEsTUFDWixTQUFTLFFBQVEsUUFBUSxjQUFjLHdDQUFlLENBQUMsR0FBRyx1QkFBdUI7QUFBQSxJQUNuRixDQUFDO0FBQUEsRUFDSDtBQUNGLENBQUM7IiwKICAibmFtZXMiOiBbXQp9Cg==
