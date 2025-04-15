const path = require('path')

module.exports = {
  devServer: {
    port: process.env.VUE_APP_FRONTEND_PORT,
    proxy: {
      '/api':{
        target: process.env.VUE_APP_BACKEND_URL,
        changeOrigin: true,
        secure: true,
        pathRewrite: {
          '^/api': '/api',
        }
      }
    },
  },
  configureWebpack: {
    devtool: 'source-map',
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src')
      },
      extensions: [".ts", ".tsx", ".js", ".json", ".json5"]
    },
    module: {
      rules: [
        {
          test: /\.json$/,
          loader: 'json-loader',
          type: 'javascript/auto',
        },
        {
          test: /\.json5$/,
          loader: 'json5-loader',
          type: 'javascript/auto',
        },
      ]
    }
  }
}
