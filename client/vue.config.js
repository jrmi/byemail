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
  }
}
