import * as types from '../mutation-types'

function urlBase64ToUint8Array (base64String) {
  const padding = '='.repeat((4 - (base64String.length % 4)) % 4)
  const base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/')
  const rawData = window.atob(base64)
  const outputArray = new Uint8Array(rawData.length)

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i)
  }
  return outputArray
}

function pushRegister () {
  console.log('Start notification subscription process')
  navigator.serviceWorker.ready.then(async function (registration) {
    registration.pushManager
      .getSubscription()
      .then(async function (subscription) {
        if (subscription) {
          console.log('Push already registered')
          return subscription
        } else {
          console.log('New push registration')

          // Get public key from server
          const response = await fetch('/api/publickey')
          const vapidPublicKey = await response.text()
          const convertedVapidKey = urlBase64ToUint8Array(vapidPublicKey)

          return registration.pushManager.subscribe({
            userVisibleOnly: true,
            applicationServerKey: convertedVapidKey
          })
        }
      })
      .then(
        subscription => {
          console.log('Send/update push subscription to server')
          fetch(`/api/subscription/`, {
            method: 'post',
            headers: {
              'Content-type': 'application/json'
            },
            body: JSON.stringify({
              subscription: subscription
            })
          })
        },
        failed => {
          console.log('Fail to push subscription to server: ', failed)
        }
      )
  })
}

// initial state
const state = {
  notification: false
}

// getters
const getters = {
  notificationEnabled: state => {
    return state.notification
  }
}

// mutations
const mutations = {
  [types.SET_NOTIFICATION] (state, status) {
    state.notification = status
  }
}

// actions
const actions = {
  checkNotificationStatus ({ commit }) {
    if ('serviceWorker' in navigator) {
      return navigator.serviceWorker.ready
        .then(registration => {
          return registration.pushManager.getSubscription()
        })
        .then(subscription => {
          if (subscription) {
            return commit(types.SET_NOTIFICATION, true)
          } else {
            return commit(types.SET_NOTIFICATION, false)
          }
        })
    } else {
      console.log('Notification subscription unaviable')
      return commit(types.SET_NOTIFICATION, false)
    }
  },

  subscribeNotification ({ commit }) {
    return Notification.requestPermission().then(result => {
      console.log('Notification result: ', result)
      if (result === 'granted') {
        pushRegister()
        commit(types.SET_NOTIFICATION, true)
      }
    })
  },

  unsubscribeNotification ({ commit }) {
    return navigator.serviceWorker.ready
      .then(registration => {
        return registration.pushManager.getSubscription()
      })
      .then(subscription => {
        if (subscription) {
          return subscription.unsubscribe().then(() => {
            commit(types.SET_NOTIFICATION, false)
            return fetch('/api/unsubscription/', {
              method: 'post',
              headers: {
                'Content-type': 'application/json'
              },
              body: JSON.stringify({
                subscription: subscription
              })
            })
          })
        } else {
          commit(types.SET_NOTIFICATION, false)
        }
      })
  }
}

export default {
  state,
  getters,
  actions,
  mutations
}
