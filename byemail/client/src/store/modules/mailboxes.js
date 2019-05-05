import Vue from 'vue'
import Moment from 'moment'
import _ from 'lodash'
import * as types from '../mutation-types'

var tagsToReplace = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;'
}

function sanitizeText(str) {
  return str.replace(/[&<>]/g, tag => {
    return tagsToReplace[tag] || tag
  })
}

// initial state
const state = {
  all: null,
  current: null,
  mail: null,
  unreads: null
}

// getters
const getters = {
  allMailboxes: state => {
    if (state.all !== null) {
      return _.orderBy(state.all, 'last_message', 'desc')
    } else {
      return null
    }
  },
  allUnreads: state => state.unreads,
  currentMailbox: state => state.current,
  currentMail: state => state.mail
}

// mutations
const mutations = {
  [types.SET_MAILBOXES](state, { mailboxes }) {
    state.all = mailboxes
  },
  [types.SET_CURRENT_MAILBOX](state, { mailbox }) {
    state.current = mailbox
  },
  [types.SET_CURRENT_MAIL](state, { mail }) {
    state.mail = mail
  },
  [types.SET_UNREADS](state, { unreads }) {
    state.unreads = unreads
  },
  [types.SET_ALL_MAIL_READ](state) {
    const newUnread = JSON.parse(JSON.stringify(state.unreads))
    delete newUnread[state.current.uid]
    state.unreads = newUnread
  },
  [types.SET_CURRENT_MAIL_READ](state) {
    const newUnread = JSON.parse(JSON.stringify(state.unreads))
    delete newUnread[state.current.uid][state.mail.uid]
    state.unreads = newUnread
  },
  [types.RESET_MAILBOXES](state) {
    Object.assign(state, {
      all: null,
      current: null,
      mail: null
    })
  }
}

// actions
const actions = {
  getAllMailboxes({ commit }, { userId }) {
    return Vue.http
      .get(`/api/users/${userId}/mailboxes`, { responseType: 'json' })
      .then(response => {
        let mailboxes = response.body
        for (let mb of mailboxes) {
          mb.last_message = Moment(mb.last_message)
        }
        return commit({ type: types.SET_MAILBOXES, mailboxes })
      })
  },
  getAllUnreads({ commit }, { userId }) {
    return Vue.http.get(`/api/users/${userId}/unreads`, { responseType: 'json' }).then(response => {
      const unreads = {}

      for (let unr of response.body) {
        unreads[unr.mailbox] = unreads[unr.mailbox] || {}
        unreads[unr.mailbox][unr.message] = true
      }
      return commit({ type: types.SET_UNREADS, unreads })
    })
  },
  getMailbox({ commit }, { userId, mailboxId }) {
    return Vue.http
      .get(`/api/users/${userId}/mailbox/${mailboxId}`, {
        responseType: 'json'
      })
      .then(function(response) {
        let mailbox = response.body
        for (let msg of mailbox.messages) {
          msg.date = Moment(msg.date)
        }
        mailbox.messages = _.orderBy(mailbox.messages, 'date', 'desc')
        return commit({ type: types.SET_CURRENT_MAILBOX, mailbox })
      })
  },
  getMail({ commit }, { userId, mailId }) {
    return Vue.http
      .get(`/api/users/${userId}/mail/${mailId}`, { responseType: 'json' })
      .then(function(response) {
        const mail = response.body
        mail.date = Moment(mail.date)
        if (mail['body-type'] === 'text/html') {
          // mail.iframeSrc = 'data:text/html;charset=' + mail['body-charset'] + ',' + escape(mail.body)
        } else {
          mail.body = sanitizeText(mail.body).replace(/\n/g, '<br />')
        }
        return commit({ type: types.SET_CURRENT_MAIL, mail })
      })
  },
  markAllMailRead({ commit }, { userId }) {
    let promises = []
    for (let msg of state.current.messages) {
      if (msg.unread) {
        promises.push(Vue.http.post(`/api/users/${userId}/mail/${msg.uid}/mark_read`))
      }
    }
    return Promise.all(promises).then(() => {
      return commit({ type: types.SET_ALL_MAIL_READ })
    })
  },
  markMailRead({ commit }, { mailId, userId }) {
    return Vue.http.post(`/api/users/${userId}/mail/${mailId}/mark_read`).then(response => {
      return commit({ type: types.SET_CURRENT_MAIL_READ })
    })
  },
  sendMail({ dispatch, commit }, { recipients, subject, content, attachments, replyTo, userId }) {
    return Vue.http
      .post(`/api/users/${userId}/sendmail/`, {
        recipients,
        subject,
        content,
        attachments,
        replyTo
      })
      .then(function(response) {
        let promise = dispatch('getAllMailboxes', { userId })
        if (state.current) {
          promise.then(() => {
            return dispatch('getMailbox', {
              mailboxId: state.current.uid,
              userId
            })
          })
        }
        return promise
      })
  },
  resendMail({ dispatch, commit }, { to, userId }) {
    return Vue.http
      .post(`/api/users/${userId}/mail/${state.mail.uid}/resend`, { to })
      .then(function(response) {
        let promise = dispatch('getAllMailboxes', { userId })
        if (state.current) {
          promise.then(() => {
            return dispatch('getMailbox', {
              mailboxId: state.current.uid,
              userId
            })
          })
        }
        return promise
      })
  }
}

export default {
  state,
  getters,
  actions,
  mutations
}
