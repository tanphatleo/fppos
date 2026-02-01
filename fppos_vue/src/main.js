import { createApp } from 'vue';
import App from './App.vue';
import { createVuetify } from 'vuetify';
import 'vuetify/styles';
import * as components from 'vuetify/components';
import * as directives from 'vuetify/directives';
import router from './router';
import store from './store';

const vuetify = createVuetify({
  components,
  directives,
});

const app = createApp(App)
  .use(store)
  .use(router)
  .use(vuetify);

app.mount('#app');