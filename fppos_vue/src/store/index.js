import { createStore } from 'vuex';

export default createStore({
  state: {
    isAuthenticated: false,
    token: null,
    isLoading: false, // Add isLoading state
  },
  getters: {
    isAuthenticated: (state) => state.isAuthenticated,
    getToken: (state) => state.token,
    isLoading: (state) => state.isLoading, // Getter for isLoading
  },
  mutations: {
    setAuthentication(state, status) {
      state.isAuthenticated = status;
    },
    setToken(state, token) {
      state.token = token;
    },
    clearToken(state) {
      state.token = null;
    },
    setLoading(state, status) {
      state.isLoading = status; // Mutation to set isLoading
    },
  },
  actions: {
    checkAuthentication({ commit }) {
      commit('setLoading', true); // Set loading to true
      const token = localStorage.getItem('token');
      if (token) {
        commit('setToken', token);
        commit('setAuthentication', true);
      } else {
        commit('clearToken');
        commit('setAuthentication', false);
      }
    },

    setToken({ commit }, token) {
      commit('setLoading', true);
      localStorage.setItem('token', token);
      commit('setToken', token);
      commit('setAuthentication', true);

    },

    removeToken({ commit }) {
      commit('setLoading', true);
      localStorage.removeItem('token');
      commit('clearToken');
      commit('setAuthentication', false);
      commit('setLoading', false);
    },
  },
  modules: {},
});
