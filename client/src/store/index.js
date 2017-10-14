import Vue from 'vue'
import Vuex from 'vuex'
import mailboxes from './modules/mailboxes'
import createLogger from 'vuex/dist/logger'

const debug = process.env.NODE_ENV !== 'production'

Vue.use(Vuex)

export default new Vuex.Store({
  // state,
  // mutations,
  // actions,
  modules: {
    mailboxes
  },
  strict: debug,
  plugins: debug ? [createLogger()] : []
})
