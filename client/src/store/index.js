import Vue from 'vue'
import Vuex from 'vuex'
import mailboxes from './modules/mailboxes'
import createLogger from 'vuex/dist/logger'
import * as types from './mutation-types'

const debug = process.env.NODE_ENV !== 'production'

Vue.use(Vuex)

const state = {
  isLoading: false
}

const mutations = {
  [types.SET_LOADING] (state, status) {
    state.isLoading = status
  }
}

const actions = {
  setLoading: ({commit}, status) => {
    commit(types.SET_LOADING, status)
  }
}

const getters = {
  isLoading: state => {
    return state.isLoading
  }
}

export default new Vuex.Store({
  state,
  mutations,
  actions,
  getters,
  modules: {
    mailboxes
  },
  strict: debug,
  plugins: debug ? [createLogger()] : []
})
