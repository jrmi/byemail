<template>
  <div class="mail-content">
    <p class="text" v-if="message['body-type'] == 'text/plain'" v-html="message.body"></p>
    <iframe class="html" v-if="message['body-type'] == 'text/html'" :srcdoc="message.body"></iframe>
    <div class="mail-attachments" v-if="message.attachments.length">
      <h3>
        {{message.attachments.length}}
        <v-icon>attach_file</v-icon>
      </h3>
      <ul v-for="att of message.attachments" :key="att.filename">
        <li>
          <a :href="att.url" :download="att.filename">{{att.filename}}</a>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
export default {
  name: "message-content",
  props: ["message"],
  data() {
    return {};
  }
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped lang="less">
.mail-attachments {
  background-color: #ccc;
  color: #eee;
  padding-left: 10px;
  flex: 0;
  max-width: 30%;
  //overflow-x: scroll;
  ul {
    margin: 0 5px;
    padding: 0;
  }
  li {
    list-style-type: none;
    overflow: hidden;
    white-space: nowrap;
    text-overflow: ellipsis;
  }
}
.mail-content {
  border: none;
  flex: 9;
  overflow-y: hidden;
  display: flex;
  .text,
  .html {
    flex: 1;
    overflow-y: scroll;
    padding: 5px;
    border: none;
  }
}
</style>
