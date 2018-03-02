<template>
  <div class="mailedit">

    <div class="reciptients">
      <ul>
        <li v-for="(recipient, index) in recipients" :key="recipient.id">
          <md-input-container class="recipient-type">
            <md-select v-model="recipient.type">
              <md-option value="to">To</md-option>
              <md-option value="cc">Cc</md-option>
              <md-option value="bcc">Bcc</md-option>
            </md-select>
          </md-input-container>

          <md-input-container class="recipient-address" >
            <md-autocomplete v-model="recipient.address" :fetch="searchContact" :debounce="500" print-attribute="value"></md-autocomplete>
          </md-input-container>

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

          <md-input-container class="attachment-file" >
            <md-file v-model="attachment.filename" @selected="files => {attachment.files = files}"></md-file>
          </md-input-container>

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
      <label>Subject</label>
      <md-input-container>
        <md-input v-model.trim="mailSubject" required></md-input>
      </md-input-container>
    </div>

    <div class="attachement"></div>

    <div class="mail-content">
      <label>Message</label>
      <md-input-container>
        <md-textarea v-model="mailContent"></md-textarea>
      </md-input-container>
    </div>
    <div class="actions">
      <md-button class="md-raised" @click="goBack()">Cancel</md-button>
      <md-button class="md-raised md-primary" @click="send()">Send</md-button>
    </div>
  </div>
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
    searchContact (search) {
      // let query = search.q

      let result = new Promise((resolve, reject) => {
        resolve([])
      })
      return result
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

.reciptients ul{
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
  flex: 20;
}
.recipient-address{
  //width: 5em;
  padding-right: 10px;
  flex: 80;
}
.recipient-type{
  //width: 5em;
  padding-right: 10px;
  flex: 2;
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
