<template>
  <v-card @keyup.enter="submit()" class="login">
      <v-form novalidate @submit.stop.prevent="submit">
        <p v-if="loginFailed">Your username or password is incorrect. Please try again...</p>
        <v-text-field v-model.trim="name" required label="Login"></v-text-field>
        <v-text-field v-model="password" required label="Password"></v-text-field>
        <v-btn class="success" @click="submit()">Submit</v-btn>
      </v-form>
  </v-card>
</template>

<script>
export default {
  name: 'hello',
  data () {
    return {
      password: '',
      name: '',
      loginFailed: false
    }
  },
  methods: {
    submit () {
      let credentials = {
        name: this.name,
        password: this.password
      }
      this.$http.post('/login/', credentials).then(response => {
        this.$router.push({ name: 'mailboxes' })
      },
      response => {
        this.loginFailed = true
      })
    }
  }

}
</script>

<style scoped lang="less">
.login{
  display: flex;
  flex-direction: column;
  align-items: center;
  .inside {
    display: block;
    flex: 1;
    width: 33%;
    min-width: 300px;
    padding: 10px;
    margin-top: 10px;
  }
}

</style>
