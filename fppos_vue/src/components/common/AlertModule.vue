<template>
  <div v-if="visible" class="alert-module">
    <span class="alert-message">{{ message }}</span>
    <span class="alert-close" @click="close">&times;</span>
  </div>
</template>

<script setup>
import { ref, onUnmounted } from 'vue';

const props = defineProps({
  message: { type: String, required: true },
  duration: { type: Number, default: 30000 }, // 30 seconds
});

const visible = ref(true);
let timer = setTimeout(() => {
  visible.value = false;
}, props.duration);

function close() {
  visible.value = false;
  clearTimeout(timer);
}

onUnmounted(() => {
  clearTimeout(timer);
});
</script>

<style scoped>
.alert-module {
  position: fixed;
  right: 2rem;
  bottom: 2rem;
  min-width: 250px;
  background: #222;
  color: #fff;
  padding: 1rem 2.5rem 1rem 1.2rem;
  border-radius: 0.5rem;
  box-shadow: 0 2px 12px rgba(0,0,0,0.2);
  z-index: 9999;
  display: flex;
  align-items: center;
  font-size: 1rem;
}
.alert-message {
  flex: 1;
}
.alert-close {
  margin-left: 1rem;
  cursor: pointer;
  font-size: 1.3rem;
  font-weight: bold;
  color: #fff;
  opacity: 0.7;
  transition: opacity 0.2s;
}
.alert-close:hover {
  opacity: 1;
}
</style>
