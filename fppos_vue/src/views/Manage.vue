<template>
    <div class="manage-view">
        <div class="manage">
            <nav class="kv-navbar kv-navbar-main">
                <section class="kv-navbar-container">
                    <ul class="kv-navbar-list">
                        <li
                            v-for="m in this.menus"
                            :key="m.Id"
                            class="kv-navbar-item kv-dropdown kv-menu-item"
                            :class="{ 'active': activeView === m.name , 'd-none': m.require_admin && !$store.getters.userAdmin }"
                     
                        >
                            <a
                                @click.prevent="setActiveView(m.name)"
                            >
                            <span>{{ m.name }}</span>
                            </a>

                        </li>
                    </ul>

                    <ul class="kv-navbar-list">
                        <li
                        class="kv-navbar-item kv-navbar-item-light"
                        >
                        <a class="kv-nav-link" href="/sale/">
                            <i class="fas fa-cart-shopping icon-item"></i>
                            <span>Bán hàng</span>
                        </a>
                        </li>
                        <li class="kv-navbar-item kv-navbar-item-light">
                          <span class="text-white"> {{ $store.getters.userName  + ($store.getters.userSuperadmin ? ' (Superadmin)' : '') }}</span>
                        </li>

                        <li
                        v-if="$store.getters.isAuthenticated" 
                        class="kv-navbar-item kv-navbar-item-light"
                        >
                        <a class="kv-nav-link" @click.prevent="handleSignOut">
                            
                            <i class="fas fa-sign-out-alt icon-item"></i>
                            
                        </a>
                        
                        </li>
                    </ul>
                </section>
            </nav>
            <div class="main-area">
                <Products v-if="activeView === 'Sản phẩm'" :isVisible="true" />
                <Customers v-if="activeView === 'Khách hàng'" :isVisible="true" />
                <Invoices v-if="activeView === 'Hóa Đơn'" :isVisible="true" />
                <Settings v-if="activeView === 'Cài đặt'" :isVisible="true" />
                <Trans v-if="activeView === 'Sổ quỹ'" :isVisible="true" />
                <Users v-if="activeView === 'Người dùng'" :isVisible="true" />
                <Purchases v-if="activeView === 'Mua hàng'" :isVisible="true" />
            </div>
            
        </div>
    </div>
    
</template>

<script>

import Products from "@/components/Manage/Products.vue";
import Customers from "@/components/Manage/Customers.vue";
import Invoices from "@/components/Manage/Invoices.vue";
import Settings from "@/components/Manage/Settings.vue";
import Trans from "@/components/Manage/Trans.vue";
import Users from "@/components/Manage/Users.vue";
import Purchases from "@/components/Manage/Purchases.vue";

export default {
  name: "Manage",
  components: {
    Products,
    Customers,
    Invoices,
    Settings,
    Trans,  
    Users,
    Purchases,
  },

  data() {
    return {
      menus: [
        { Id: 1, name: "Hóa Đơn" , require_admin : false},
        { Id: 2, name: "Mua hàng" , require_admin : false},
        { Id: 3, name: "Sản phẩm" , require_admin : true},
        { Id: 4, name: "Khách hàng" , require_admin : true},
        { Id: 5, name: "Sổ quỹ" , require_admin : false},
        { Id: 6, name: "Cài đặt" , require_admin : true},
        { Id: 7, name: "Người dùng" , require_admin : true},
      ],
      activeView: "Mua hàng", // Define your menus data here
    };
  },
  mounted() {
    // Automatically click/select "Hóa Đơn" when the page loads
    this.setActiveView("Mua hàng");
  },
  methods: {
    setActiveView(page) {
      this.activeView = page; // Assign the emitted page to activeView
    //   window.alert(`Switched to ${page} view`);
    },
    handleSignOut() {
      this.$store.dispatch('removeToken'); // Clear token from Vuex store
      this.$router.push('/signin'); // Redirect to SignIn page
    },
    showReportPopup(condition) {
      // Define your showReportPopup logic here
    },
  },
};
</script>

<style lang="scss" scoped>
$kv-primary-color: #0070F4;

.manage-view {
  display: flex;
  justify-content: center;
  width: 100%;
  height: 100%;
  box-sizing: border-box;
  //   border: 5px solid green; /* Debugging border */
//   border-bottom: 5px solid red; /* Ensure bottom border is visible */
}    

.manage {
    width: 100%;
    box-sizing: border-box;
    display: flex ;
    flex-direction: column;
    // display: flex;
    // flex-direction: row;
    .main-area {
            // height: 100%;
            flex: 1;
            width: 100%;
            background-color: rgb(243, 243, 243);
            display: flex;
            justify-content: center;
            box-sizing: border-box;
        }

}


.kv-navbar {
    display: flex;
    flex-direction: row;
    justify-content: center;
    background-color: $kv-primary-color;
    

    .kv-navbar-container {
        padding: 0.2rem 0.5rem 0.2rem 0.5rem;
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        width: 100rem;

        .kv-navbar-list {
            display: flex;
            flex-direction: row;
            list-style-type: none;
            margin: 0;
            padding: 0;

            .kv-navbar-item {
                margin-right: 20px;
                padding: 0.5rem 0.5rem 0.3rem 0.5rem;
                user-select: none;
                a {
                    text-decoration: none;
                    color: #333;
                    font-weight: 500;
                    color: white;
                    &.active {
                        color: #007bff;
                    }
                }
            }

            .kv-navbar-item.active {
                background-color: #0056b3;
                border-radius: 0.5rem;
            }

            .kv-navbar-item:hover {
                background-color: #004d9f;
                border-radius: 0.5rem;
            }
        }
    }

}
</style>

<style>
    .v-table__wrapper {
        user-select: none;
    }
    .v-table__wrapper * {
        user-select: text;
    }
</style>