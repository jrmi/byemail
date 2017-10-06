<template>
  <div class="login">
    <md-whiteframe class="inside">
      <form novalidate @submit.stop.prevent="submit">
        <p v-if="loginFailed">Your username or password is incorrect. Please try again...</p>
        <md-input-container>
          <label>Login</label>
          <md-input v-model.trim="name" required></md-input>
        </md-input-container>
        <md-input-container>
          <label>Password</label>
          <md-input type="password" v-model="password" required></md-input>
        </md-input-container>
        <md-button class="md-raised md-primary" @click="submit()">Submit</md-button>
      </form>
    </md-whiteframe>
  </div>
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
