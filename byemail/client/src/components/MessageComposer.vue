<template>
  <v-container grid-list-md text-xs-left>
    <v-form>
      <v-layout row wrap>
        <v-flex xs7>
          <v-layout
            class="recipients"
            row
            wrap
            v-for="(recipient, index) in draft().recipients"
            :key="recipient.id"
          >
            <v-flex xs11>
              <search-address-field
                @update="updateRecipient(recipient, $event)"
                :initValue="recipient.address"
                :userId="userId"
              ></search-address-field>
            </v-flex>
            <v-flex xs1>
              <v-btn
                color="error"
                icon
                @click="removeDraftRecipient({rid: recipient.id})"
                v-if="index >= 1"
              >
                <v-icon>clear</v-icon>
              </v-btn>
            </v-flex>
          </v-layout>
          <v-btn @click="addDraftEmptyRecipient()">Add recipient</v-btn>
        </v-flex>

        <v-flex xs5 class="attachments">
          <v-layout row wrap v-for="attachment in draft().attachments" :key="attachment.id">
            <v-flex xs11>
              <attachment-field @change="updateAttachment(attachment, $event)"/>
            </v-flex>

            <v-flex xs1>
              <v-btn color="error" icon @click="removeDraftAttachment({aid: attachment.id})">
                <v-icon>clear</v-icon>
              </v-btn>
            </v-flex>
          </v-layout>
          <v-btn @click="addDraftEmptyAttachment()">Add attachment</v-btn>
        </v-flex>
      </v-layout>

      <hr>

      <div class="mail-subject">
        <v-text-field v-model.trim="subject" label="Subject"></v-text-field>
      </div>

      <div class="mail-content">
        <v-textarea box v-model="content" label="Content"></v-textarea>
      </div>

      <div class="actions">
        <v-btn @click="sendData">Send</v-btn>
      </div>
    </v-form>
  </v-container>
</template>

<script>
import { mapGetters, mapActions, mapMutations } from 'vuex'
import SearchAddressField from '@/components/SearchAddressField'
import AttachmentField from '@/components/AttachmentField'

export default {
  name: 'message-composer',
  props: ['userId'],
  data() {
    return {
      recipientTypes: [
        { text: 'To', value: 'to' },
        { text: 'Cc', value: 'cc' },
        { text: 'Bcc', value: 'bcc' }
      ]
    }
  },
  created() {
    if (this.draft().recipients.length < 1) {
      this.addDraftEmptyRecipient()
    }
  },
  components: {
    SearchAddressField,
    AttachmentField
  },
  computed: {
    subject: {
      get() {
        return this.draft().subject
      },
      set(value) {
        this.setDraftSubject({ subject: value })
      }
    },
    content: {
      get() {
        return this.draft().content
      },
      set(value) {
        this.setDraftContent({ content: value })
      }
    }
  },
  methods: {
    updateRecipient(recipient, newfields) {
      const newRecipient = Object.assign({ ...recipient }, newfields)
      this.updateDraftRecipient({ recipient: newRecipient })
    },
    updateAttachment(attachment, newfields) {
      const newAttachment = Object.assign({ ...attachment }, newfields)
      this.updateDraftAttachment({ attachment: newAttachment })
    },

    sendData() {
      const data = {
        recipients: this.draft().recipients,
        attachments: this.draft().attachments,
        subject: this.draft().subject,
        content: this.draft().content,
        userId: this.userId
      }
      this.$emit('sendMessage', data)
    },
    ...mapActions(['addDraftEmptyRecipient', 'addDraftEmptyAttachment']),
    ...mapGetters(['draft']),
    ...mapMutations([
      'setDraftSubject',
      'setDraftContent',
      'addDraftRecipient',
      'updateDraftRecipient',
      'removeDraftRecipient',
      'addDraftAttachment',
      'updateDraftAttachment',
      'removeDraftAttachment'
    ])
  }
}
</script>

<style scoped lang="less">
</style>
