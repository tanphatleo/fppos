<template>
  <div style="height: 100%;">
    <div class="home-page" style="height: 100%;">
      <div class="page-header">
        <div class="header-left">
          <div class="col-left-control">
            <div class="product-search">
              <i class="fas fa-search"></i>
              <input class="product-search-input c-input" placeholder="Tìm hàng hóa" @focus="search_input_focus" @blur="search_input_blur" @input="search_input_change"/>
              <div class="place-holder"> </div>
              <div class="product-search-results">
                <ul v-for="product in filteredProducts" :key="product.id" :id="'product-' + product.id">
                  <li class="suggestions-item">
                    <div class="suggestions-item-info"> 
                      <h5><b>{{ product.name }}</b></h5>
                      <div class="number-blue"> {{ formatPrice(product.price) }}</div>
                    </div>
                    <div class="suggestions-item-info"> {{ product.code }}</div>
                  </li>
                </ul>
              </div>
            </div>
            <div class="carts-tab">
              <ul class="pending-sales-list">
                <li 
                  v-for="(sale, index) in localPendingSales" 
                  :key="sale.id" 
                  class="pending-sales-item"
                  :class="{ 'selected': index === 0 }"
                  @click="select_pending_invoice"
                >
                    <h5> Hóa đơn {{ sale.id }} </h5>
                    <i class="fa fa-times" @click="remove_pending_sale"></i>
                </li>
                <li class="new_pending_sale pending-sales-item" @click="add_new_pending_sale">
                  <h5> Đơn mới </h5>
                </li>
                
              </ul>
            </div>
          </div>
          <div class="header-left-info">
          </div>
        </div>
        <div class="header-right">
          <div class="user-name"> </div>
          <div class="menu-toggle"> 
            <menu_toggle/>
          </div>
        </div>  
      </div>
    </div>
  </div>

</template>
<script>
// import { search } from 'core-js/fn/symbol';
import menu_toggle from '@/components/menu_toogle.vue'

  export default {
    name: "SaleView",
    components: {
      menu_toggle
    },
    methods: {
      formatPrice(value) {
        return new Intl.NumberFormat('vi-VN').format(value);
      },

      search_input_focus(event) {
        console.log("Input focused");
        console.log(event);
        event.target.select();
      },

      search_input_blur(event) {
        console.log("Input blurred");
        // get element with class product-search-results and hide it
        document.querySelector('.product-search-results').classList.add('is-hidden');
        console.log(event);
      }, 

      search_input_change(event) {
        console.log("Input changed");
        console.log(event);
        document.querySelector('.product-search-results').classList.remove('is-hidden');
        const query = event.target.value.toLowerCase();
        this.filteredProducts = this.products.filter(product => 
          product.name.toLowerCase().includes(query) || 
          product.code.toLowerCase().includes(query)
        );
      }, 

      select_pending_invoice(event) {
        // add selected to this li and remove from others
        const items = document.querySelectorAll('.pending-sales-item');
        items.forEach(item => {
          item.classList.remove('selected');
        });
        event.currentTarget.classList.add('selected');
      }, 

      remove_pending_sale(event) {
        event.stopPropagation(); // prevent triggering parent click event
        console.log("Remove pending sale");
        console.log(event);
        const index = Array.from(event.currentTarget.parentNode.parentNode.children).indexOf(event.currentTarget.parentNode);
        this.localPendingSales.splice(index, 1);
        // update local storage
        localStorage.setItem('pendingSales', JSON.stringify(this.localPendingSales));
      },

      add_new_pending_sale() {
        console.log("Add new pending sale");
        const newId = this.localPendingSales.length > 0 ? Math.max(...this.localPendingSales.map(sale => sale.id)) + 1 : 1;
        this.localPendingSales.push({
          id: newId,
          items: []
        });
        // update local storage
        localStorage.setItem('pendingSales', JSON.stringify(this.localPendingSales));
      }
      
    },
    data() {
      return {
        products: [],
        filteredProducts: [], 
        localPendingSales: []
      }
    },
    created() {
      // Simulate fetching products from an API
      this.products = [
        { "id": 1, "code":"ESP001", "name": "Espresso", "price": 35000 },
        { "id": 2, "code":"LAT002", "name": "Latte", "price": 45000 },
        { "id": 3, "code":"BANHMI003", "name": "Banh Mi", "price": 25000 }
      ];

      // read pending sales from local storage
      const pendingSales = localStorage.getItem('pendingSales');
      if (pendingSales) {
        this.localPendingSales = JSON.parse(pendingSales);
      } else {
        this.localPendingSales = [{
          id: 1,
          items: []
        }
        ,{
            id: 2,
            items: []
          }
        ];
      }

    }
  }
</script>

<style lang="scss" scoped>
$kv-primary: #0070F4;
$size-sm: 4vh;
$main-bg-color: azure;

.home-page {
  height: 100%;
  display: flex ;
  flex-direction: column;
  background-color: $main-bg-color;
}
.number-blue {
  color: $kv-primary;
  // text-decoration: solid;
  font-weight: bold;
}

.c-input{
  background-color: white;
  color: black;
  padding-left: 2.5rem;
}
.carts-tab {
  flex: 1;
  max-width: 70vw;
}

.page-header {
  display: flex;
  flex-direction: row;
  height: $size-sm;
  background-color: $kv-primary;
}

.product-search {
  // background-color: white;
    min-width: 30rem;
    position: relative;
    height: 100%;
    padding: 0.4rem 0 0.4rem 0.4rem;
    flex-grow: 1;
    display: flex;
    max-width: 15vw;
}
.product-search > .place-holder {
  
  min-width: 3rem;
}
.suggestions-item {
  display: flex;
  flex-direction: column;
  padding: 0.5rem 1rem 0.5rem 1rem;
}
.suggestions-item:hover {
  background-color: lightgray;
  cursor: pointer;
}

.suggestions-item-info {
  display: flex;
  justify-content: space-between;
}

.product-search-results{
  position: absolute;
  top: 100%;
  left: 0;
  width: 100%;
  // max-height: 90vh;
  z-index: 2;
}
.product-search > i {
  position: absolute;
  left: 1rem;
  z-index: 1;
  color: gray;
  
  // Vertical Centering Logic
  top: 50%;
  transform: translateY(-50%); 
  
  // Ensure the icon has a consistent width for horizontal centering
  width: 1.5rem; 
  display: flex;
  align-items: center;
  justify-content: center;
}

.product-search > input {
  width: 100%;
  height: 100%;
  border: none;
  border-radius: 0.3rem;
  font-size: 1rem;
  box-shadow: 0 0 0 0;
  outline: none;
  width: 100%;
  
}

.pending-sales-list {
  display: flex ;
  flex-direction: row;
  padding: 0.3rem 0 0 0 ;
  height: 100%;
  user-select: none;           /* Modern browsers */
  -webkit-user-select: none;   /* Safari */
  -moz-user-select: none;      /* Firefox */
  -ms-user-select: none;       /* Legacy IE */
}
.pending-sales-item:hover {
  background-color: rgba(0, 0, 0, 0.285);
  cursor: pointer;
}

.new_pending_sale > h5 {
  padding-right: 0.4rem ;
}

.menu-toggle{
  // menu-toggle
    padding: 0.4rem 1rem 0.4rem 0.4rem;
    display: flex;
    align-items: center;
}
.pending-sales-item {
  border-left: rgba(0, 0, 0, 0.256) 0.7px solid;
  border-radius: 0.3rem 0.3rem 0rem 0rem;
  // margin-right: 0.5rem ;
  padding-left: 0.75rem ;
  padding-right: 0.55rem ;
  display: flex;
  height: 100%;
  // max-width: 10rem;

  h5 {
    margin: 0;              /* Remove default browser margin that pushes text down */
    line-height: 1;         /* Ensures the text box is only as tall as the font */
    font-size: 1rem;
    display: flex;          /* Sometimes helps icons center better */
    align-items: center;
    color: white;
  }

  i {
    cursor: pointer;
    display: flex;          /* Sometimes helps icons center better */
    align-items: center;
    text-align: center;
    color: white;
    margin-left: 0.8rem;
    // margin-left: 1rem;
  }

  i:hover {
    color: red!important;
    // background-color: red!important;
  }
}

.pending-sales-item.selected {
  background-color: $main-bg-color;
  

  h5 {
    font-weight: bold;
    color: black;
  };

  i {
    color: black;
  }
} 




.col-left-control {
  display: flex;
}

.header-left {
  display: flex;
  flex-direction: row;
  flex-grow: 4;
}

.header-right {
  display: flex;
  flex-direction: row;
  flex-grow: 1;
  min-width: 15vw;
  justify-content: flex-end
}

</style>
