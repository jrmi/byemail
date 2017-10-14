import Vue from 'vue'
import Moment from 'moment'
import * as types from '../mutation-types'

var tagsToReplace = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;'
}

function sanitizeText (str) {
  return str.replace(/[&<>]/g, (tag) => { return tagsToReplace[tag] || tag })
}

// initial state
const state = {
  all: [],
  current: null,
  mail: null
}

// getters
const getters = {
  allMailboxes: state => state.all,
  currentMailbox: state => state.current,
  currentMail: state => state.mail
}

// actions
const actions = {
  getAllMailboxes ({ commit }) {
    return Vue.http.get('/api/mailboxes', {responseType: 'json'}).then((response) => {
      let mailboxes = response.body
      for (let mb of mailboxes) {
        mb.last_message = Moment(mb.last_message)
      }
      commit({ type: types.SET_MAILBOXES, mailboxes })
    })
  },
  getMailbox ({commit}, { mailboxId }) {
    return Vue.http.get('/api/mailbox/' + mailboxId, {responseType: 'json'}).then(function (response) {
      let mailbox = response.body
      for (let msg of mailbox.messages) {
        msg.date = Moment(msg.date)
      }
      commit({ type: types.SET_CURRENT_MAILBOX, mailbox })
    })
  },
  getMail ({commit}, {mailId}) {
    return Vue.http.get('/api/mail/' + mailId, { responseType: 'json' }).then(function (response) {
      let mail = response.body
      mail.date = Moment(mail.date)
      if (mail['body-type'] === 'text/html') {
        mail.iframeSrc = 'data:text/html;charset=' + mail['body-charset'] + ',' + escape(mail.body)
      } else {
        mail.body = sanitizeText(mail.body).replace(/\n/g, '<br />')
      }
      commit({ type: types.SET_CURRENT_MAIL, mail })
    })
  },
  markMailRead ({commit}) {
    return Vue.http.post('/api/mail/' + state.mail.uid + '/mark_read').then(function (response) {
      commit({ type: types.SET_CURRENT_MAIL_READ })
    })
  }

}

// mutations
const mutations = {
  [types.SET_MAILBOXES] (state, { mailboxes }) {
    state.all = mailboxes
  },
  [types.SET_CURRENT_MAILBOX] (state, { mailbox }) {
    state.current = mailbox
  },
  [types.SET_CURRENT_MAIL] (state, { mail }) {
    state.mail = mail
  },
  [types.SET_CURRENT_MAIL_READ] (state, { mailbox }) {
    state.current.messages.find(m => m.uid === state.mail.uid).unread = false
    state.mail.unread = false
  }
}

export default {
  state,
  getters,
  actions,
  mutations
}
