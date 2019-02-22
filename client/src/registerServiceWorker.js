/* eslint-disable no-console */

import { register } from 'register-service-worker'
import store from './store'

if (process.env.NODE_ENV === 'production') {
  console.log('Try to register service worker')
  register(`${process.env.BASE_URL}service-worker.js`, {
    ready (registration) {
      console.log(
        'App is being served from cache by a service worker.\n' +
          'For more details, visit https://goo.gl/AFskqB'
      )
      store.dispatch('setServiceWorker', true)
    },
    registered () {
      console.log('Service worker has been registered.')
      store.dispatch('setServiceWorker', true)
    },
    cached () {
      console.log('Content has been cached for offline use.')
    },
    updatefound () {
      console.log('New content is downloading.')
    },
    updated () {
      console.log('New content is available; please refresh.')
    },
    offline () {
      console.log(
        'No internet connection found. App is running in offline mode.'
      )
    },
    error (error) {
      console.error('Error during service worker registration:', error)
    }
  })
}

let deferredPrompt = null

window.addEventListener('beforeinstallprompt', e => {
  console.log('before install launched')
  // Prevent Chrome 67 and earlier from automatically showing the prompt
  e.preventDefault()
  // Stash the event so it can be triggered later.
  deferredPrompt = e
})

export default {
  deferredPrompt
}
