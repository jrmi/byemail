<template>
  <v-app>
    <router-view/>
    <v-snackbar
      v-model="snackbar"
      :multi-line="true"
      :timeout="5000"
      :top="true"
      :color="getMessage().color"
    >
      {{ getMessage().message }}
      <v-btn flat @click="snackbar = !snackbar">Close</v-btn>
    </v-snackbar>
  </v-app>
</template>

<script>
import { mapGetters, mapMutations } from 'vuex'

export default {
  name: 'App',
  computed: {
    snackbar: {
      get() {
        return this.getMessage().message
      },
      set(val) {
        if (!val) {
          this.setMessage({ message: '', color: 'primary' })
        }
      }
    }
  },
  methods: {
    ...mapGetters(['getMessage']),
    ...mapMutations(['setMessage'])
  }
}
</script>
