module.exports = {
  devServer: {
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        ws: true,
        changeOrigin: false
      },
      '/login': {
        target: 'http://localhost:8000'
      },
      '/logout': {
        target: 'http://localhost:8000'
      }
    }
  },
  pwa: {
    name: 'byemail-client',
    workboxPluginMode: 'InjectManifest',
    workboxOptions: {
      swSrc: 'src/service-worker.js'
    }
  }
}
