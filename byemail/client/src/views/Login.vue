<template>
  <v-content>
    <v-container fluid fill-height>
      <v-layout align-center justify-center>
        <v-flex xs12 sm8 md4>
          <v-card @keyup.enter="submit()" class="login">
            <v-toolbar dark color="primary">
              <v-toolbar-title>Login</v-toolbar-title>
              <v-spacer></v-spacer>
              <v-icon large>star</v-icon>
            </v-toolbar>

            <v-card-text>
              <v-form novalidate @submit.stop.prevent="submit">
                <p v-if="loginFailed">Your username or password is incorrect. Please try again...</p>
                <v-text-field v-model.trim="name" required label="Login"></v-text-field>
                <v-text-field
                  v-model="password"
                  required
                  label="Password"
                  :append-icon="show ? 'visibility_off' : 'visibility'"
                  :type="show ? 'text' : 'password'"
                  @click:append="show = !show"
                  @keyup.enter="submit"
                ></v-text-field>
              </v-form>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn class="primary" @click="submit()">Submit</v-btn>
            </v-card-actions>
          </v-card>
        </v-flex>
      </v-layout>
    </v-container>
  </v-content>
</template>

<script>
export default {
  data() {
    return {
      password: "",
      name: "",
      show: false,
      loginFailed: false
    };
  },
  methods: {
    submit() {
      let credentials = {
        name: this.name,
        password: this.password
      };
      this.$http.post("/login/", credentials).then(
        response => {
          this.$router.push({
            name: "mailboxes",
            params: { userId: this.name }
          });
        },
        response => {
          this.loginFailed = true;
        }
      );
    }
  }
};
</script>

<style scoped lang="less">
.login {
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
