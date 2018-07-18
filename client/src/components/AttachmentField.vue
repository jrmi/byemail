<template>
    <v-text-field
      v-model="filename"
      type="file"
      prepend-icon='attach_file'
      ref="fileInput"
      @blur="change($event)"
    >
    </v-text-field>
</template>

<script>

export default {
  name: 'message-composer',
  data () {
    return {
      filename: '',
    }
  },
  methods: {
    change (event) {
      for (let f of event.target.files) {
        const reader = new FileReader()
        reader.onload = () => {
          this.$emit('change', {filename: f.name, b64: btoa(reader.result)})
        }
        reader.readAsBinaryString(f)
      }
    }
  }

}
</script>

<style scoped lang="less">

</style>
