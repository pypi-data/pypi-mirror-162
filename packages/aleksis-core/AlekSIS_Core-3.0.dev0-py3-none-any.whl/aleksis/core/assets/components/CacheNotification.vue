<template>
  <message-box :value="cache" type="warning">
    {{ this.$root.django.gettext('This page may contain outdated information since there is no internet connection.') }}
  </message-box>
</template>

<script>
  export default {
    name: "cache-notification",
    data () {
        return {
            cache: false,
        }
    },
    created() {
        this.channel = new BroadcastChannel("cache-or-not");
        this.channel.onmessage = (event) => {
            this.cache = event.data === true;
        }
    },
      destroyed(){
        this.channel.close()
      },
  }
</script>
