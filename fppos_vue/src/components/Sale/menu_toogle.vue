<template>
    <div class="menu-container" >
        <div :class="['dropdown', { 'is-active': isOpen }]" v-click-outside="closeMenu">
        <div class="dropdown-trigger">
            <button class="button" @click="isOpen = !isOpen" aria-haspopup="true">
            <span class="icon">
                <i class="fas fa-bars"></i>
            </span>
            </button>
        </div>

        <div class="dropdown-menu" id="dropdown-menu" role="menu">
            <div class="dropdown-content">
            <a v-for="item in menuItems" 
                :key="item.text" 
                href="#" 
                class="dropdown-item"
                @click.prevent="handleAction(item.action)">
                
                <span class="icon-text">
                <span class="icon has-text-info">
                    <i :class="item.icon"></i>
                </span>
                <span>{{ item.text }}</span>
                </span>
            </a>

            <hr class="dropdown-divider">

            <a class="dropdown-item has-text-danger" @click.prevent="logout">
                <span class="icon-text">
                <span class="icon">
                    <i class="fas fa-sign-out-alt"></i>
                </span>
                <span>Đăng xuất</span>
                </span>
            </a>
            </div>
        </div>
        </div>
    </div>
</template>

<script>
export default {
  name: 'menu_toggle',
  props: {
    msg: String
  },
  emits: ['menu-action'],
  data() {
    return {
      isOpen: false,
      menuItems: [
        { text: 'Quản lý', icon: 'fas fa-chart-pie', action: 'viewReport' },
        { text: 'Lập phiếu thu', icon: 'fas fa-edit', action: 'receipt' },
        { text: 'Lập phiếu chi', icon: 'fas fa-edit', action: 'payment' },
        { text: 'Chốt hàng', icon: 'fas fa-eye', action: 'date_end_inventory' },
        { text: 'Chốt tiền', icon: 'fas fa-info-circle', action: 'date_end_cash_balance' }
      ]
    };
  },
  methods: {
    closeMenu() {
      this.isOpen = false;
    },
    handleAction(action) {
      console.log("Triggered:", action);
      this.$emit('menu-action', action);
      this.isOpen = false; // Close after click
    },
    logout() {
      this.$store.dispatch('removeToken'); // Clear token from Vuex store
      this.$router.push('/signin'); // Redirect to SignIn page
    }
  }
}
</script>

<style lang="scss" scoped>

    .menu-container {
//   padding: 10px;
    .dropdown {
        padding: 0 0 0 0;
    }
    button {
        padding: 0 0 0 0;
        background-color: transparent;
        border: none;
    }

    button:hover {
        // background-color: transparent;
        color: #000000;
    }
  .dropdown-menu {
    min-width: 250px;
    right: 0; // Align to the right like dropdown-menu-right
    left: auto;
  }

  .dropdown-item {
    display: flex;
    align-items: center;
    padding: 0.6rem 1rem;
    font-size: 0.95rem;

    .icon {
      margin-right: 15px;
      width: 20px;
      text-align: center;
    }

    &:hover {
      background-color: #f5f5f5;
      color: #0070F4; // Your primary blue
    }
  }
}
</style>