<template>
<v-container grid-list-md text-xs-left>
  <v-form>
      <div class="recipients">

        <v-layout row wrap v-for="(recipient, index) in recipients" :key="recipient.id" >
          <v-flex xs2>
            <v-select
              v-model="recipient.type"
              :items="recipientTypes"
            ></v-select>
            </v-flex>
            <v-flex xs9>
            <v-autocomplete
              v-model="recipient.address"
              :items="recipient.entries"
              :loading="recipient.isLoading"
              :search-input.sync="recipient.search"
              item-text="name"
              item-value="name"
            >
              Recipient
            </v-autocomplete>
          </v-flex>
          <v-flex xs1>
            <v-btn color="error" icon @click="recipients.splice(index, 1)" v-if="index >= 1">
              <v-icon>clear</v-icon>
            </v-btn>
          </v-flex>
        </v-layout>
        <v-btn @click="addRecipient()">
          Add recipient
        </v-btn>
      </div>
      <hr />
      <div class="attachments">
        <v-layout row wrap v-for="(attachment, index) in attachments" :key="attachment.id" >

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
            <v-btn color="error" icon @click="attachments.splice(index, 1)">
              <v-icon>clear</v-icon>
            </v-btn>
          </v-flex>

        </v-layout>

        <v-btn @click="addAttachment()">Add attachment</v-btn>
      </div>

      <div class="mail-subject">
        <v-text-field
          v-model.trim="mailSubject"
          label="Subject"
        >
        </v-text-field>
      </div>

      <div class="mail-content">
          <v-textarea
              v-model="mailContent"
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
import { mapActions } from 'vuex'

export default {
  name: 'message-composer',
  data () {
    return {
      recipientTypes: [
        {text: 'To', value: 'to'},
        {text: 'Cc', value: 'cc'},
        {text: 'Bcc', value: 'bcc'}
      ],
      mailContent: '',
      mailSubject: '',
      attachments: [],
      recipients: [],
      address: [
        {id: 1, name: 'Toto <toto@localhost>'},
        {id: 2, name: 'titi@localhost'},
        {id: 3, name: 'tata@localhost'}
      ]
    }
  },
  created () {
    this.addRecipient()
  },
  methods: {
    querySelections (recipient, val) {
      recipient.loading = true
      // Simulated ajax query
      setTimeout(() => {
        recipient.entries = this.address.filter((e) => {
          return (e.name || '').toLowerCase().indexOf((val || '').toLowerCase()) > -1
        })
        recipient.loading = false
      }, 500)
    },
    addRecipient () {
      const recipient = {
        id: _.uniqueId(),
        address: '',
        type: 'to',
        search: null,
        result: [],
        loading: false
      }

      this.recipients.push(recipient)

      // TODO unwatch when necessary
      this.$watch(function () {
        return recipient.search
      },
      function (val) {
        val && val.length > 2 && this.querySelections(recipient, val)
      })
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
      'setLoading'
    ])
  }

}
</script>

<style scoped lang="less">

</style>
