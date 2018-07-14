import Vue from 'vue'
import Moment from 'moment'
import _ from 'lodash'
import * as types from '../mutation-types'


// initial state
const state = {
  draftRecipients: {},
  draftAttachment: {},
  draft: {
    mailContent: '',
    mailSubject: '',
    recipients: [],
    attachments: []
  }
}

// getters
const getters = {
  currentDraft: state => {
    const draft = {...state.draft}
    draft.recipients = draft.recipients.map( recipientId => state.draftRecipients[recipientId])
    draft.attachments = draft.attachments.map( attachmentId => state.draftAttachments[attachmentId])
    return draft
  }
}

// mutations
const mutations = {
  [types.SET_DRAFT] (state, { mailContent, mailSubject, recipients, attachments }) {
    if (mailContent) {
      state.draft.mailContent = mailContent
    }
    if (mailSubject) {
      state.draft.mailSubject = mailSubject
    }
    if (recipients) {
      state.draft.recipients = recipients
    }
    if (attachments) {
      state.draft.attachments = attachments
    }
  },
  [types.ADD_DRAFT] (state, { recipient, attachment }) {
    if (recipient) {
      state.draft.recipients.push(recipient)
    }
    if (attachment) {
      state.draft.attachments.push(attachment)
    }
  },
  [types.REMOVE_DRAFT] (state, { recipient, attachment }) {
    if (recipient) {
      state.draft.recipients.splice(recipient, 1)
    }
    if (attachment) {
      state.draft.attachments.splice(attachement, 1)
    }
  },
  [types.RESET_DRAFT] (state) {
    Object.assign(state, {
      draft: {
        mailContent: '',
        mailSubject: '',
        recipients: [],
        attachments: []
      }
    })
  }
}

// actions
const actions = {
  resetDraft ({commit}) {
    const draft = {
      mailContent: '',
      mailSubject: '',
      recipients: [],
      attachments: []
    }
    commit({ type: types.SET_DRAFT }, draft)
  },
  addDraftRecipient ({commit}, {recipient_info}) {
    const recipient = {
      id: _.uniqueId(),
      address: '',
      type: 'to',
      search: null, // TODO remove this from here
      result: [],
      loading: false
    }

    if (recipient_info) {
      recipient.address = recipient_info
    }

    const recipients = state.draft.recipients
    
    //recipients.push(recipient)
    commit({ type: types.ADD_DRAFT, recipient})
  }
}


export default {
  state,
  getters,
  actions,
  mutations
}
