import Vue from 'vue'
import Vuex from 'vuex'
import mailboxes from './modules/mailboxes'
import draft from './modules/draft'
import notification from './modules/push-notifications'
import createLogger from 'vuex/dist/logger'
import * as types from './mutation-types'

const debug = process.env.NODE_ENV !== 'production'

Vue.use(Vuex)

const state = {
  isLoading: false,
  message: '',
  messageColor: 'primary',
  serviceWorker: false
}

const mutations = {
  [types.SET_LOADING] (state, status) {
    state.isLoading = status
  },
  [types.SET_SERVICE_WORKER] (state, status) {
    state.serviceWorker = status
  },
  [types.SET_MESSAGE] (state, status) {
    state.message = status.message
    state.messageColor = status.color
  }
}

const actions = {
  setLoading: ({ commit }, status) => {
    commit(types.SET_LOADING, status)
  },
  setServiceWorker: ({ commit }, status) => {
    commit(types.SET_SERVICE_WORKER, status)
  },
  showMessage: ({ commit }, status) => {
    commit(types.SET_MESSAGE, status)
  }
}

const getters = {
  isLoading: state => {
    return state.isLoading
  },
  serviceWorkerRegistered: state => {
    return state.serviceWorker
  },
  getMessage: state => {
    return {
      message: state.message,
      color: state.messageColor
    }
  }
}

export default new Vuex.Store({
  state,
  mutations,
  actions,
  getters,
  modules: {
    mailboxes,
    draft,
    notification
  },
  strict: debug,
  plugins: debug ? [createLogger()] : []
})
