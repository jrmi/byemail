import Vue from 'vue'
import * as types from '../mutation-types'

// initial state
const state = {
  account: {}
}

// getters
const getters = {
  account: state => {
    return state.account
  }
}

// mutations
const mutations = {
  [types.SET_ACCOUNT](state, account) {
    state.account = { ...account }
  }
}

// actions
const actions = {
  loadAccount({ commit }, { userId }) {
    return Vue.http.get(`/api/users/${userId}/account`, { responseType: 'json' }).then(response => {
      return commit(types.SET_ACCOUNT, { account: response })
    })
  }
}

export default {
  state,
  getters,
  actions,
  mutations
}
