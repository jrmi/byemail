<template>

  <v-form>      
    
    <div class="recipients">
      <ul>
        <li v-for="(recipient, index) in recipients" :key="recipient.id" class="md-layout">
          <v-select
            v-model="recipient.type"
            :items="recipientTypes"
          ></v-select>
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
          <v-btn icon @click="recipients.splice(index, 1)">
            <v-icon>remove</v-icon>
          </v-btn>
        </li>

      </ul>
      <v-btn icon @click="addRecipient()">
        <v-icon>add</v-icon>
      </v-btn>
    </div>

    <div class="attachments">
      <ul>
        <li v-for="(attachment, index) in attachments" :key="attachment.id">

          <v-text-field 
            v-model="attachment.filename" 
            type="file"
            @md-change="files => {attachment.files = files}">
          </v-text-field>

          <v-btn icon @click="attachments.splice(index, 1)">
            <v-icon>remove</v-icon>
          </v-btn>

        </li>
      </ul>

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
      <v-btn @click="goBack()">Cancel</v-btn>
      <v-btn @click="send()">Send</v-btn>
    </div>

  </v-form>
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
      address: [
        {id: 1, name: 'Toto <toto@localhost>'},
        {id: 2, name: 'titi@localhost'},
        {id: 3, name: 'tata@localhost'}
      ],
      recipients: []
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
          recipient.entries = this.address.filter(e => {
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
    goBack () {
      // TODO verify dirtyness
      this.$router.go(-1)
    },
    send () {
      this.setLoading(true)
      this.prepareAttachment().then((attachments) => {
        let data = {
          recipients: this.recipients,
          attachments: attachments,
          subject: this.mailSubject,
          content: this.mailContent
        }
        this.sendMail(data).then(response => {
          this.setLoading(false)
          this.$router.go(-1)
        })
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
