<template>


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



</style>
