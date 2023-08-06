<script>
  export default {
    name: "message-box",
    // Due to this component being a wrapper to a v-alert, all props of this can be used (and overridden).
  }
</script>

<template>
    <v-alert border="left" text v-bind="$attrs">
      <slot>
        Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
      </slot>
    </v-alert>
</template>

