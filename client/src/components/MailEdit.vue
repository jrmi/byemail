<template>
  <form class="md-layout mailedit">
    <md-card class="md-layout-item">
      <md-card-content>
        <div class="recipients">
          <ul>
            <li v-for="(recipient, index) in recipients" :key="recipient.id" class="md-layout">
              <md-field class="recipient-type md-layout-item">
                <label>Type</label>
                <md-select v-model="recipient.type">
                  <md-option value="to">To</md-option>
                  <md-option value="cc">Cc</md-option>
                  <md-option value="bcc">Bcc</md-option>
                </md-select>
              </md-field>

              <!-- md-autocomplete class="recipient-address md-layout-item" 
                  v-model="recipient.address" 
                  :md-options="contacts"
                  @md-changed="searchContacts" 
                  @md-opened="searchContacts" 
                  :debounce="500" 
                  print-attribute="value"
              >
                <label>Recipient</label>
                <template slot="md-autocomplete-item" slot-scope="{ item, term }">
                  <md-highlight-text :md-term="term">{{ item.name }}</md-highlight-text>
                </template>

                <template slot="md-autocomplete-empty" slot-scope="{ term }">
                  No address matching "{{ term }}" were found.
                </template>
              </md-autocomplete -->

              <md-field class="recipient-address md-layout-item">
                <label>Recipient</label>
                <md-input v-model.trim="recipient.address" required>
                </md-input>
              </md-field>

              <md-button class="md-icon-button md-raised md-accent recipient-remover" @click="recipients.splice(index, 1)">
                <md-icon>remove</md-icon>
              </md-button>

            </li>
          </ul>
          <div class="actions">
            <md-button class="md-raised" @click="addReciptient()">Add recipient</md-button>
          </div>
        </div>

        <div class="attachments">
          <ul>
            <li v-for="(attachment, index) in attachments" :key="attachment.id">

              <md-field class="attachment-file" >
                <md-file v-model="attachment.filename" @md-change="files => {attachment.files = files}">
                </md-file>
              </md-field>

              <md-button class="md-icon-button md-raised md-accent attachment-remover" @click="attachments.splice(index, 1)">
                <md-icon>remove</md-icon>
              </md-button>

            </li>
          </ul>
          <div class="actions">
            <md-button class="md-raised" @click="addAttachment()">Add attachment</md-button>
          </div>
        </div>

        <div class="mail-subject">
          <md-field>
            <label>Subject</label>
            <md-input v-model.trim="mailSubject" required>
              <label>Subject</label>
            </md-input>
          </md-field>
        </div>

        <div class="attachement"></div>

        <div class="mail-content">
          <md-field>
            <label>Message</label>
            <md-textarea v-model="mailContent"></md-textarea>
          </md-field>
        </div>
        <div class="actions">
          <md-button class="md-raised" @click="goBack()">Cancel</md-button>
          <md-button class="md-raised md-primary" @click="send()">Send</md-button>
        </div>

      </md-card-content>
    </md-card>
  </form>
</template>

<script>
import _ from 'lodash'
import { mapActions } from 'vuex'

export default {
  name: 'mailedit',
  data () {
    return {
      mailContent: '',
      mailSubject: '',
      attachments: [],
      contacts: [],
      recipients: [
        {
          id: _.uniqueId(),
          address: '',
          type: 'to'
        }
      ]
    }
  },
  methods: {
    searchContacts (search) {
      return new Promise((resolve, reject) => {
        this.contacts = [{id: 1, name: 'toto@localhost'}]
        resolve(this.contacts)
      })
    },
    addReciptient () {
      let reciptient = {
        id: _.uniqueId(),
        address: '',
        type: 'to'
      }
      this.recipients.push(reciptient)
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

.mailedit{
  padding: 10px 10%;
}

.recipients ul{
  list-style-type: none;
  li{
    display:flex;
    margin: 0;
  }
  .md-input-container{
    //margin-bottom: 0px;
    //margin-top: 0px;
    padding-top: 0px;
  }
  .md-button{
    float: right;
  }
}

.attachments ul{
  list-style-type: none;
  li{
    display:flex;
    margin: 0;
  }
  .md-input-container{
    //margin-bottom: 0px;
    //margin-top: 0px;
    padding-top: 0px;
  }
  .md-button{
    float: right;
  }
}

.recipient-type{
  //width: 5em;
  margin-right: 10px;
  //flex: 20;
}
.recipient-address{
  //width: 5em;
  padding-right: 10px;
  //flex: 80;
}
.recipient-type{
  //width: 5em;
  padding-right: 10px;
  //flex: 2;
}

.mail-subject{
  padding-top: 20px;
}

.mail-content{
  padding-top: 20px;
  padding-bottom: 20px;
}

.actions{
  display: flex;
  justify-content: flex-end;
}

</style>
