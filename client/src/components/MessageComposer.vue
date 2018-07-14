<template>
<v-container grid-list-md text-xs-left>
  <v-form>
      <v-layout row wrap>
        <v-flex xs7>
          <v-layout class="recipients" row wrap v-for="(recipient, index) in currentDraft().recipients" :key="recipient.id" >
            <v-flex xs2>
              <v-select
                v-model="recipient.type"
                :items="recipientTypes"
              ></v-select>
            </v-flex>
            <v-flex xs9>
              <v-combobox
                v-model="address"
                :items="entries"
                :loading="isLoading"
                :search-input.sync="search"
                item-text="name"
                item-value="name"
                @change="test(recipient)"
              >
                Recipient
              </v-combobox>
            </v-flex>
            <v-flex xs1>
              <v-btn color="error" icon @click="removeDraft({recipient: index})" v-if="index >= 1">
                <v-icon>clear</v-icon>
              </v-btn>
            </v-flex>
          </v-layout>
          <v-btn @click="addRecipient()">
            Add recipient
          </v-btn>
        </v-flex>

        <v-flex xs5 class="attachments">
          <v-layout row wrap v-for="(attachment, index) in currentDraft().attachments" :key="attachment.id" >

            <v-flex xs11>
              <v-text-field
                v-model="attachment.filename"
                type="file"
                @click="attachment.files = $event.target.files"
                prepend-icon='attach_file'
              >
              </v-text-field>
            </v-flex>

            <v-flex xs1>
              <v-btn color="error" icon @click="removeDraft({attachment: index})">
                <v-icon>clear</v-icon>
              </v-btn>
            </v-flex>

          </v-layout>
          <v-btn @click="addAttachment()">Add attachment</v-btn>
        </v-flex>
      </v-layout>

      <hr />

      <div class="mail-subject">
        <v-text-field
          v-model.trim="currentDraft().mailSubject"
          label="Subject"
        >
        </v-text-field>
      </div>

      <div class="mail-content">
          <v-textarea
              box
              v-model="currentDraft().mailContent"
              label="Content"
          ></v-textarea>
      </div>

      <div class="actions">
        <v-btn @click="send()">Send</v-btn>
      </div>
  </v-form>
</v-container>
</template>

<script>
import _ from 'lodash'
import { mapGetters, mapActions, mapMutations } from 'vuex'

export default {
  name: 'message-composer',
  data () {
    return {
      recipientTypes: [
        {text: 'To', value: 'to'},
        {text: 'Cc', value: 'cc'},
        {text: 'Bcc', value: 'bcc'}
      ],
      address: '',
      entries: [],
      isLoading: false,
      search: '',
      mailContent: '',
      mailSubject: '',
      attachments: [],
      recipients: []
    }
  },
  created () {
    if (this.draft.recipients.length < 1){
      this.addRecipient()
    }
  },
  computed: {
    draft: {
      get () {
        return this.currentDraft()
      },
      set (data) {
        this.setDraft(data)
      }
    }
  },
  watch: {
  },
  methods: {
    /*currentDraft () {
      return {
        mailContent: this.mailContent,
        mailSubject: this.mailSubject,
        attachments: this.attachments,
        recipients: this.recipients
      }
    },*/
    test (arg) {
      console.log('test', arg)
    },
    querySelections (recipient, val) {
      recipient.loading = true
      this.$http.get('/api/contacts/search', { responseType: 'json', params: {text: val} }).then(function (response) {
        recipient.entries = response.body.map((item) => { return {name: item} })
        recipient.loading = false
      })
    },
    addRecipient () {
      this.addDraftRecipient({recipient_info:''}).then(() => {

        //console.log(this.currentDraft())
        // TODO unwatch when necessary
        /*this.$watch(function () {
          return this.currentDraft().recipient.search
        },
        function (val) {
          val && this.querySelections(recipient, val)
        })*/
      })
      /*const recipient = {
        id: _.uniqueId(),
        address: '',
        type: 'to',
        search: null,
        result: [],
        loading: false
      }

      this.recipients.push(recipient)*/

    },
    addAttachment () {
      let attachment = {
        id: _.uniqueId(),
        files: null,
        filename: '',
        files_b64: []
      }
      this.attachments.push(attachment)
    },
    send () {
      this.prepareAttachment().then((attachments) => {
        let data = {
          recipients: this.recipients,
          attachments: attachments,
          subject: this.mailSubject,
          content: this.mailContent
        }
        this.$emit('sendMessage', data)
      })
    },
    prepareAttachment () {
      // Compute all base64 for attachment
      return new Promise((resolve, reject) => {
        let promises = []
        let attachments = []
        for (let att of this.attachments) {
          for (let f of att.files) {
            let promise = new Promise((resolve, reject) => {
              let reader = new FileReader()
              reader.onload = () => {
                attachments.push({filename: f.name, b64: btoa(reader.result)})
                resolve()
              }
              reader.readAsBinaryString(f)
            })
            promises.push(promise)
          }
        }
        Promise.all(promises).then(() => {
          resolve(attachments)
        })
      })
    },
    ...mapActions([
      'sendMail',
      'setLoading',
      'addDraftRecipient'
    ]),
    ...mapGetters([
      'currentDraft'
    ]),
    ...mapMutations([
      'setDraft',
      'resetDraft',
      'addDraft',
      'removeDraft'
    ])
  }

}
</script>

<style scoped lang="less">

</style>
