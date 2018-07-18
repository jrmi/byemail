import Vue from 'vue'
import Moment from 'moment'
import _ from 'lodash'
import * as types from '../mutation-types'


// initial state
const state = {
  draftRecipients: {},
  draftAttachments: {},
  draft: {
    content: '',
    subject: '',
    recipients: [],
    attachments: []
  }
}

// getters
const getters = {
  draft: state => {
    const draft = {...state.draft}
    draft.recipients = draft.recipients.map( recipientId => state.draftRecipients[recipientId])
    draft.attachments = draft.attachments.map( attachmentId => state.draftAttachments[attachmentId])
    return draft
  }
}

// mutations
const mutations = {
  [types.RESET_DRAFT] (state) {
    Object.assign(state, {
      draft: {
        mailContent: '',
        mailSubject: '',
        recipients: [],
        attachments: []
      }
    })
    state.draftRecipients = {}
    state.draftAttachments  = {}
  },
  // Recipients
  [types.ADD_DRAFT_RECIPIENT] (state, {recipient}) {
    const rid = recipient.id
    Vue.set(state.draftRecipients, rid, recipient)
    state.draft.recipients.push(rid)
  },
  [types.UPDATE_DRAFT_RECIPIENT] (state, {recipient}) {
    const rid = recipient.id
    Object.assign(
        state.draftRecipients[rid], 
        recipient
    )
  },
  [types.REMOVE_DRAFT_RECIPIENT] (state, {rid}) {
    state.draft.recipients.splice(state.draft.recipients.indexOf(rid), 1);
    delete state.draftRecipients[rid]
  },
  // Attachments
  [types.ADD_DRAFT_ATTACHMENT] (state, {attachment}) {
    const aid = attachment.id
    Vue.set(state.draftAttachments, aid, attachment)
    state.draft.attachments.push(aid)
  },
  [types.UPDATE_DRAFT_ATTACHMENT] (state, {attachment}) {
    const rid = attachment.id
    Object.assign(
        state.draftAttachments[rid], 
        attachment
    )
  },
  [types.REMOVE_DRAFT_ATTACHMENT] (state, {aid}) {
    state.draft.attachments.splice(state.draft.attachments.indexOf(aid), 1);
    delete state.draftAttachments[aid]
  },
  // Subject and content
  [types.SET_DRAFT_SUBJECT] (state, {subject}) {
    state.draft.subject = subject
  },
  [types.SET_DRAFT_CONTENT] (state, {content}) {
    state.draft.content = content
  }
}

// actions
const actions = {
  addDraftEmptyRecipient ({commit}) {
    const recipient = {
      id: _.uniqueId(),
      address: '',
      type: 'to'
    }
    commit({ type: types.ADD_DRAFT_RECIPIENT, recipient})
  },
  addDraftEmptyAttachment ({commit}) {
    const attachment = {
      id: _.uniqueId(),
      filename: '',
      b64: ''
    }
    commit({ type: types.ADD_DRAFT_ATTACHMENT, attachment})
  }
}


export default {
  state,
  getters,
  actions,
  mutations
}
