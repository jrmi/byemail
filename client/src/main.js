import Vue from 'vue'
import './plugins/vuetify'
import App from './App.vue'
import router from './router'
import store from './store/index'
import VueResource from 'vue-resource'
import './registerServiceWorker'

Vue.config.productionTip = false

Vue.use(VueResource)

/* let deferredPrompt
window.addEventListener('beforeinstallprompt', e => {
  // Prevent Chrome 67 and earlier from automatically showing the prompt
  e.preventDefault()
  // Stash the event so it can be triggered later.
  deferredPrompt = e

  addBtn.addEventListener('click', e => {
    // hide our user interface that shows our A2HS button
    addBtn.style.display = 'none'
    // Show the prompt
    deferredPrompt.prompt()
    // Wait for the user to respond to the prompt
    deferredPrompt.userChoice.then(choiceResult => {
      if (choiceResult.outcome === 'accepted') {
        console.log('User accepted the A2HS prompt')
      } else {
        console.log('User dismissed the A2HS prompt')
      }
      deferredPrompt = null
    })
  })
}) */

Vue.http.interceptors.push(function (request) {
  // return response callback
  return function (response) {
    /* Log network errors and show message */
    if (response.status >= 500) {
      console.log('Error while accessing backend. See error below...')
      store.dispatch('setLoading', false)
      store.dispatch('showMessage', {
        color: 'error',
        message: 'Network error...'
      })
    }
  }
})

new Vue({
  router,
  store,
  render: h => h(App)
}).$mount('#app')
