import Vue from 'vue'
import './plugins/vuetify'
import App from './App.vue'
import router from './router'
import store from './store/index'
import VueResource from 'vue-resource'
import './registerServiceWorker'

Vue.config.productionTip = false

Vue.use(VueResource)

Vue.http.interceptors.push(function(request) {
  // return response callback
  return function(response) {
    /* Log network errors and show message */
    if (response.status >= 500){
      console.log('Error while accessing backend. See error below...')
      store.dispatch('setLoading', false)
      store.dispatch('showMessage', {
        color: 'error',
        message: 'Network error...'
      })
    }

  };
});

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
