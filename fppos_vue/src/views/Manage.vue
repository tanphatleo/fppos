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
                          <span class="text-white"> {{ $store.getters.userName  }}</span>
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
                <Invoices v-if="activeView === 'Hóa Đơn'" :isVisible="true"  :channels="channels" :d_edit_days="d_edit_days" />
                <Settings v-if="activeView === 'Cài đặt'" :isVisible="true" />
                <Trans v-if="activeView === 'Sổ quỹ'" :isVisible="true" :d_edit_days="d_edit_days" />
                <Users v-if="activeView === 'Người dùng'" :isVisible="true" />
                <Purchases v-if="activeView === 'Mua hàng'" :isVisible="true" :d_edit_days="d_edit_days" />
                <DateEndInventory v-if="activeView === 'Chốt Kho'" :isVisible="true" :d_edit_days="d_edit_days" />
                <DateEndCashBalance v-if="activeView === 'Chốt Quỹ'" :isVisible="true" :d_edit_days="d_edit_days"/>
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
import DateEndInventory from "@/components/Manage/DateEndInventory.vue";
import DateEndCashBalance from "@/components/Manage/DateEndCashBalance.vue";
import axios from "axios";

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
    DateEndInventory,
    DateEndCashBalance,
  },

  data() {
    return {
        d_edit_days : 3,
      menus: [
        { Id: 1, name: "Hóa Đơn" , require_admin : false, query_params : 'invoices'},
        { Id: 2, name: "Mua hàng" , require_admin : false, query_params : 'purchases'},
        { Id: 3, name: "Sản phẩm" , require_admin : true, query_params : 'products'},
        { Id: 4, name: "Khách hàng" , require_admin : true, query_params : 'customers'},
        { Id: 5, name: "Sổ quỹ" , require_admin : false, query_params : 'trans'},
        { Id: 6, name: "Cài đặt" , require_admin : true, query_params : 'settings'},
        { Id: 7, name: "Người dùng" , require_admin : true, query_params : 'users'},
        { Id: 8, name: "Chốt Kho" , require_admin : false, query_params : 'date_end_inventory'},
        { Id: 9, name: "Chốt Quỹ" , require_admin : false, query_params : 'date_end_cash_balance'},
      ],
      activeView: "Hóa Đơn", // Define your menus data here
        channels: [],
    };
  },
  watch: {
    '$route.query.view'(newVal) {
      const menu = this.menus.find(m => m.query_params === newVal);
      if (menu) {
        this.activeView = menu.name;
      }
    }
  },
  mounted() {
    const view = this.$route.query.view;
    const menu = this.menus.find(m => m.query_params === view);
    if (menu) {
      this.activeView = menu.name;
    } else {
      this.setActiveView("Hóa Đơn");
    }
    this.fetchLogicConfig();
  },
  methods: {
    
    async fetchLogicConfig() {
      try {
        const response = await axios.get('/logicconfigs/');
        const channelConfig = response.data.find(c => c.key === 'channels');
        if (channelConfig) {
          this.channels = JSON.parse(channelConfig.value);
        }

        const editDaysConfig = response.data.find(c => c.key === 'd_edit_days');
        if (editDaysConfig) {
          this.d_edit_days = parseInt(editDaysConfig.value);
        //   console.log("Fetched d_edit_days:", this.d_edit_days);
        }

      } catch (error) {
        console.error('Error fetching channels:', error);
      }
    },

    setActiveView(page) {
      this.activeView = page; // Assign the emitted page to activeView
      const menu = this.menus.find(m => m.name === page);
      if (menu && this.$route.query.view !== menu.query_params) {
        this.$router.push({ query: { ...this.$route.query, view: menu.query_params } });
      }
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


::v-deep table {
    thead {
        // background-color: #0070F4 !important;
        tr {

            th{
                padding-left: 0.5rem !important;
            }
            // first th
            th:first-child {
                border-top-left-radius: 0.5rem !important;
            }

            // last th
            th:last-child {
                border-top-right-radius: 0.5rem !important;
            }
            // change opacity of header

            background-color: #66a9f5 ;
            
        }
    }

}
</style>

<style lang="scss">
$back-ground-color: rgba(165, 165, 165, 0.235);
$kv-primary-color: #0070F4;


// hide scroll bar table
table::-webkit-scrollbar {
    height: 0;
    width: 0;
}



.my-custom-header-class {
    background-color: #00000000 !important;

    font-weight: bold;
    color: black;
    padding-left: 0.5rem;
    padding-top: 0.4rem;
    padding-bottom: 0.4rem;
}

.my-custom-header-class-right {
    background-color: #00000000 !important;
    text-align: right;
    font-weight: bold;
    color: black;
    padding-left: 0.5rem;
    padding-top: 0.4rem;
    padding-bottom: 0.4rem;
}

.v-data-table td, .v-data-table th {
    height: auto;
    padding-left: 0.5rem;
    padding-top: 0.4rem;
    padding-bottom: 0.4rem;
    
    
}

.v-data-table td {
  border-top: 1px solid #c1c1c1 !important;
  border-bottom: none !important;
}

.v-data-table-footer {
    background-color: #f0f0f0 !important;
}

.v-toolbar__content{
    // background-color: $back-ground-color !important;
    height: auto !important;
    border-radius: 0.5rem !important;
}

// hide scroll bar table
.v-table__wrapper::-webkit-scrollbar {
    height: 0;
    width: 0;
}

.c-button{
    margin-left: 0.5rem;
}

.v-table__wrapper {
    user-select: none;
}
.v-table__wrapper * {
    user-select: text;
}

.text-left {
    text-align: left !important;
    }

.text-right {
    text-align: right !important;
}

</style>