import Vue from 'vue'
import Moment from 'moment'
import _ from 'lodash'
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
  all: null,
  current: null,
  mail: null,
  draft: {
    mailContent: '',
    mailSubject: '',
    recipients: [
      {
        id: _.uniqueId(),
        address: '',
        type: 'to'
      }
    ]
  }
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
      mailbox.messages = _.orderBy(mailbox.messages, 'date', 'desc')
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
  markAllMailRead ({commit}) {
    let promises = []
    for (let msg of state.current.messages) {
      if (msg.unread) {
        promises.push(Vue.http.post('/api/mail/' + msg.uid + '/mark_read'))
      }
    }
    return Promise.all(promises).then(() => {
      commit({ type: types.SET_ALL_MAIL_READ })
    })
  },
  markMailRead ({commit}) {
    return Vue.http.post('/api/mail/' + state.mail.uid + '/mark_read').then((response) => {
      commit({ type: types.SET_CURRENT_MAIL_READ })
    })
  },
  sendMail ({dispatch, commit}, {recipients, subject, content, replyTo}) {
    return Vue.http.post('/api/sendmail/', {recipients, subject, content, replyTo}).then(function (response) {
      let promise = dispatch('getAllMailboxes')
      if (state.current) {
        promise = dispatch('getMailbox', {mailboxId: state.current.uid})
      }
      return promise
    })
  },
  resetDraft ({commit}) {
    let draft = {
      mailContent: '',
      mailSubject: '',
      recipients: [
        {
          id: _.uniqueId(),
          address: '',
          type: 'to'
        }
      ]
    }
    commit({ type: types.SET_DRAFT }, draft)
  },
  addDraftReciptient ({commit}) {
    let reciptient = {
      id: _.uniqueId(),
      address: '',
      type: 'to'
    }
    let reciptients = state.draft.reciptients
    recipients.push(reciptient)


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
  [types.SET_ALL_MAIL_READ] (state) {
    for (let msg of state.current.messages) {
      if (msg.unread) {
        msg.unread = false
      }
    }
    if (state.mail) {
      state.mail.unread = false
    }
    state.current.unreads = 0
    state.all.find(mb => mb.uid === state.current.uid).unreads = 0
  },
  [types.SET_CURRENT_MAIL_READ] (state) {
    state.all.find(m => m.uid === state.current.uid).unreads--
    state.current.unreads--
    state.current.messages.find(m => m.uid === state.mail.uid).unread = false
    state.mail.unread = false
  },
  [types.SET_DRAFT] (state, { mailContent, mailSubject, recipients }) {
    if (_.isDefined(mailContent)) {
      state.draft.mailContent = mailContent
    }
    if (_.isDefined(mailSubject)) {
      state.draft.mailSubject = mailSubject
    }
    if (_.isDefined(recipients)) {
      state.draft.recipients = recipients
    }
  }
}

export default {
  state,
  getters,
  actions,
  mutations
}
