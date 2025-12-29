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
          <div class="user-name"> {{ this.branch }}</div>
          <div class="user-name"> {{ this.user }}</div>
          <div class="menu-toggle"> 
            <menu_toggle/>
          </div>
        </div>  
      </div>
      <div class="body-page">
        <div class="detail-box">
          <Carts :focus_invoice="focus_invoice"
          @remove-item="handleRemoveItem"
          @update-item="handleUpdateItem"
          @update-total="handleUpdateTotal"/>
        </div>
        <div class="shortcut-box">
          <div class="shortcut-box-header">
            <div class="search_filter-control">
              <div class="customer-search">
                <i class="fas fa-search"></i>
                <input class="customer-search-input c-input" placeholder="Tìm khách hàng" @focus="search_input_focus" @blur="search_input_blur" @input="search_input_change"/>
                <i class="fas fa-plus add-cust"></i>
                <div class="place-holder"> </div>
                <div class="customer-search-results is-hidden">
                  <ul v-for="product in filteredProducts" :key="product.id" :id="'product-' + product.id">
                    <li class="suggestions-item">
                      <div class="suggestions-item-info"> 
                        <h5><b>{{ }}</b></h5>
                        <div class="number-blue"> {{  }}</div>
                      </div>
                      <div class="suggestions-item-info"> {{ }}</div>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
            <div class="product-header-right">
              <i class="fas fa-list-ul"></i>
            </div>
          </div>
          <div class="product-short-list">
            <div class="product-grid-container">
              <div class="product-list">
                <div
                  v-for="product in products" 
                  :key="product.id" 
                  class="product-item"
                  @click="add_product"
                >
                  <div class="product-card-top">  
                    <i class="fas fa-image placeholder-icon"></i>
                  </div>

                  <div class="product-card-bottom">
                    <h4 class="product-name">{{ product.name }}</h4>
                    <h4 class="product-price">{{ formatPrice(product.price) }}</h4>
                  </div>

                </div>
              </div>

            </div>
          </div>
          <div class="payment-action">
            <button class="payment-button">
              Thanh toán
            </button>
          </div>

        </div>
      </div>
      <div class="page-footer">
        aaaaaaaaaaaaaa
      </div>
    </div>
  </div>
  <AddCust 
    v-if="isCustomerModalOpen" 
    :current-branch="this.branch"
    @close="isCustomerModalOpen = false" 
    @save="handleCustomerSave"
  />
</template>
<script>
// import { search } from 'core-js/fn/symbol';
import menu_toggle from '@/components/menu_toogle.vue'
import AddCust from '@/components/AddCust.vue';
import Carts from '@/components/Carts.vue';

  export default {
    name: "SaleView",
    components: {
      menu_toggle,
      AddCust,
      Carts
    },
    data() {
      return {
        products: [],
        filteredProducts: [], 
        localPendingSales: [], 
        user: 'Nguyen Van A', 
        branch: 'Chi nhánh Hà Nội',
        isCustomerModalOpen: false, 
        focus_invoice: [],
      }
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
        this.focus_invoice = this.localPendingSales[Array.from(event.currentTarget.parentNode.children).indexOf(event.currentTarget)];
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
      }, 

      handleUpdateItem() {
        console.log("Item updated in cart");
        // Additional logic can be added here if needed\
        console.log(this.localPendingSales);
      },

      update_total_and_quantity() {
        if (!this.focus_invoice || !Array.isArray(this.focus_invoice.items)) return;
        let total = 0;
        let totalItems = 0;
        this.focus_invoice.items.forEach(item => {
          total += (item.price || 0) * (item.quantity || 0);
          totalItems += (item.quantity || 0);
        });
        this.focus_invoice.total = total;
        this.focus_invoice.totalItems = totalItems;
      },

      add_product(event) {
        console.log("Add product to cart");
        console.log(event);
        const productId = Array.from(event.currentTarget.parentNode.children).indexOf(event.currentTarget) + 1;
        const product = this.products.find(p => p.id === productId);
        if (product) {
          // Check if product already exists in cart
          const existingItem = this.focus_invoice.items.find(item => item.code === product.code);
          if (existingItem) {
            existingItem.quantity += 1; // Increment quantity
          } else {
            this.focus_invoice.items.push({
              uuid: Date.now().toString(),
              code: product.code,
              name: product.name,
              price: product.price,
              quantity: 1,
              onHand: product.stock,
              ordered: product.orderCount,
              hasNote: false,
              units: [{id: 1, name: 'Gói'}],
              productType: product.productType,
              actualProducts: [
                {
                  code: product.code,
                  quantity: 1
                }
              ],
              isSerial: false,
              note: '',
              isOpenPopover: false
            });
          }

          this.update_total_and_quantity();
        }
      },
    },
    
    created() {
      // Simulate fetching products from an API
      this.products = [
        { id: 1, code: 'ABC01', name: "100g Ức gà Xông Khói", productGroup: "Gà", price: 30000, stock: 121, orderCount: 39, productType: 2, image: null },
        { id: 2, code: 'ABC02', name: "Ức gà Xông Khói 150g", productGroup: "Gà", price: 40000, stock: 81, orderCount: 33, productType: 2, image: null },
        { id: 3, code: 'ABC03', name: "Sốt Teriyaki 10ml - Hàng Tặng", productGroup: "Gà", price: 0, stock: -2159, orderCount: 45, productType: 2, image: null },
        { id: 4, code: 'ABC04', name: "Hủ Sốt Teriyaki 200ml", productGroup: "Sốt", price: 50000, stock: 0, orderCount: 1, productType: 2, image: null },
        { id: 5, code: 'ABC05', name: "100g Ức gà Cà ri Ấn", productGroup:"Gà", price: 30000, stock: 60, orderCount: 45, productType: 2, image: null },
        { id: 6, code:'ABC06', name:"Ức gà Tỏi Á 150g", productGroup:"Gà", price :40000 , stock : -205 , orderCount :28 , productType :2 , image :null },
        { id: 7, code: 'ABC07', name: "100g Ức gà Tiêu xanh", productGroup: "Gà", price: 30000, stock: 28, orderCount: 41, productType: 2, image: null },
        { id: 8, code: 'ABC08', name: "100g Ức gà Ngũ vị", productGroup: "Gà", price: 30000, stock: 23, orderCount: 53, productType: 2, image: null },
        { id: 9, code: 'ABC09', name: "100g Ức gà Tỏi Á", productGroup:"Gà", price: 30000, stock: -69, orderCount: 34, productType: 2, image: null },
        { id: 10, code:'ABC10', name:"100g Ức gà Teriyaki", productGroup:"Gà", price :30000 , stock :31 , orderCount :48 , productType :2 , image :null },
        { id: 11, code:'ABC11', name:"Ức gà Ngũ vị 150g", productGroup:"Gà", price :40000 , stock :35 , orderCount :59 , productType :2 , image :null },
        { id: 12, code: 'ABC12', name: "Ức gà Cà ri ấn 150g", productGroup:"Gà", price: 40000, stock: 100, orderCount: 47, productType: 2, image: null },
        { id: 13, code: 'ABC13', name: "Ức gà Teriyaki 150g", productGroup:"Gà", price: 40000, stock: 6, orderCount: 45, productType: 2, image: null },
        { id: 14, code: 'ABC14', name: "Ức gà Tiêu xanh 150g", productGroup:"Gà", price: 40000, stock: 22, orderCount: 48, productType: 2, image: null },
        { id: 15, code:'ABC15', name:"COMBO 6 GÓI ỨC GÀ (Mix 6 vị)", productGroup:"Gà", price :230000 , stock :-205 , orderCount :5 , productType :2 , image :null },
        { id: 16, code:'ABC16', name:"Sốt Tiêu Đen 20ml", productGroup:"Sốt", price :5000 , stock :20 , orderCount :0 , productType :2 , image :null },
        { id: 17, code:'ABC17', name: "Sốt Tứ Xuyên 20ml", productGroup:"Sốt", price: 5000, stock: 75, orderCount: 0, productType: 2, image: null },
      ];

      // read pending sales from local storage
      // const pendingSales = localStorage.getItem('pendingSales');
      // if (pendingSales) {
      //   this.localPendingSales = JSON.parse(pendingSales);
      //   this.focus_invoice = this.localPendingSales[0];
      // } else {
        this.localPendingSales = [{
          id: 1,
          total: 40000,
          totalItems: 1,
          discount: 0,
          finalTotal: 40000,
          note: '',
          items: [
            {
              uuid: '1',
              code: 'FP0011',
              name: 'Ức gà Teriyaki 150g',
              price: 40000,
              quantity: 1,
              onHand: 6,
              ordered: 45,
              hasNote: false,
              units: [{id: 1, name: 'Gói'}],
              productType: 2,
              actualProducts: [
                {
                  code: 'FP0011',
                  quantity: 1
                }
              ],
              isSerial: false,
              note: '',
              isOpenPopover: false
            }
          ]
        },
        {
          id: 2,
          items: []
        }
        ];

        this.focus_invoice = this.localPendingSales[0];
      // }

      console.log("Pending Sales Loaded:", this.localPendingSales);
      console.log("Focus Invoice:", this.focus_invoice);

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

  .page-header {
    display: flex;
    flex-direction: row;
    height: max($size-sm, 3rem);
    background-color: $kv-primary;

    .header-left {
      display: flex;
      flex-direction: row;
      flex-grow: 4;
      
      .col-left-control {
        display: flex;

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

        .carts-tab {
          flex: 1;
          max-width: 70vw;

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

          .pending-sales-item {
            border-left: rgba(0, 0, 0, 0.256) 0.7px solid;
            border-radius: 0.3rem 0.3rem 0rem 0rem;
            // margin-right: 0.5rem ;
            padding-left: 0.75rem ;
            padding-right: 0.55rem ;
            display: flex;
            height: 100%;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
            // box-shadow: 1em 1em 2em rgba(0, 0, 0, 0.1);
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

        }

      }

    }

    .header-right {
      display: flex;
      flex-direction: row;
      flex-grow: 1;
      min-width: 15vw;
      justify-content: flex-end;

      .menu-toggle{
        // menu-toggle
          padding: 0.4rem 1.2rem 0.4rem 0.4rem;
          display: flex;
          align-items: center;
      }

    }

  }

  .body-page{
    flex: 1;
    // background-color: red;
    display: flex ;
    flex-direction: row;
    min-height: 0;
    overflow: hidden;

    .detail-box {
      flex: 3;
      // background-color: rgba(128, 128, 128, 1);
      
      margin: 0.3rem;
      border-radius: 0.3rem;
      height: calc(100% - 0.6rem); // Account for margin (0.3 top + 0.3 bottom)
    }

    .shortcut-box {
      min-width: 30rem;
      flex: 1;
      background-color: $main-bg-color;
      margin: 0.3rem;
      border-radius: 0.3rem;
      height: calc(100% - 0.6rem); // Account for margin
      // Flex column to stack Header -> List -> Footer
      display: flex;
      flex-direction: column;
      
      // Stop this specific box from pushing boundaries
      overflow: hidden; 
      // height: 100%;

      .shortcut-box-header {
        flex-shrink: 0; // 1. Never shrink the header
        
        display: flex;
        flex-direction: row;
        justify-content: space-between;
        margin-top: 0.3rem;
        padding: 0rem 0.4rem 0 0.4rem;
        // border-bottom: 1px solid lightgray;
        
        .search_filter-control{
          // margin-left: 1rem;
          display: flex;
          flex-direction: row;
          height: 2.5rem;
          
          width: 70%;

          .customer-search {
            // background-color: white;
              // min-width: 20rem;
              // width: 70%;
              position: relative;
              height: 100%;
              padding: 0.2rem 0 0.2rem 0.2rem;
              flex-grow: 1;
              display: flex;
              // max-width: 15vw;

              input {
                width: 100%;
                height: 100%;
                border: 1px solid gray;
                border-radius: 0.3rem;
                font-size: 1rem;
                box-shadow: 0 0 0 0;
                outline: none;
                width: 100%;
                
              }

              i.fa-search {
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

              i.fa-plus {
                position: absolute;
                right: 1rem;
                z-index: 1;
                color: $kv-primary;
                
                // Vertical Centering Logic
                top: 50%;
                transform: translateY(-50%); 
                
                // Ensure the icon has a consistent width for horizontal centering
                width: 1.5rem; 
                display: flex;
                align-items: center;
                justify-content: center;
                cursor: pointer;
              }
          }
          

        }

        .product-header-right {
          display: flex;       // 2. Make this a flex container
          align-items: center; // 3. Vertically center items inside this container
          height: 100%;
          i {
            // Removed absolute positioning logic
            z-index: 1;
            color: $kv-primary;
            width: 1.5rem;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            
            // Optional: Add margin if you want spacing from the edge
            margin-right: 1rem;
          }
        }
      }

      .product-short-list {
        // 2. Grow to fill space between Header and Payment
        flex: 1; 
        
        // 3. Create a boundary context for the absolute child
        position: relative; 
        
        // 4. Ensure it doesn't bleed out
        overflow: hidden; 

        // background-color: rgb(168, 94, 94);
        margin: 0.3rem;
        border-radius: 0.3rem;

        .product-grid-container {

          // 5. THE FIX: Detach from flow and force-fit to parent edges
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          
          // 6. Scroll happens here
          overflow-y: auto; 
          
          padding: 10px;

          .product-list {
            display: grid;
            /* Auto-fill columns, min 140px wide */
            grid-template-columns: repeat(auto-fill, minmax(10rem, 1fr));
            gap: 10px;
            padding-bottom: 10px;
            min-height: 0;

            // Add padding at bottom so last items aren't cut off by scrollbar
            padding-bottom: 10px;

            /* Alternate placeholder colors for product cards */
            .product-item:nth-child(7n+1) .placeholder-icon { color: rgba(255,44,82,0.6); }
            .product-item:nth-child(7n+2) .placeholder-icon { color: rgba(255,186,7,0.6); }
            .product-item:nth-child(7n+3) .placeholder-icon { color: rgba(76,176,80,0.6); }
            .product-item:nth-child(7n+4) .placeholder-icon { color: rgba(33,183,192,0.6); }
            .product-item:nth-child(7n+5) .placeholder-icon { color: rgba(136,97,214,0.6); }
            .product-item:nth-child(7n+6) .placeholder-icon { color: rgba(255,107,0,0.6); }
            .product-item:nth-child(7n)   .placeholder-icon { color: rgba(35,127,205,0.6); }

            .product-item {
              background: white;
              border: 1px solid #ddd;
              border-radius: 4px;
              cursor: pointer;
              overflow: hidden;
              transition: all 0.2s ease;
              display: flex;
              flex-direction: row;
              height: 5rem;

              .product-card-top {
                // height: 3rem;
                position: relative;
                display: flex;
                align-items: center;
                justify-content: center;
                background-color: #eee;
              }

              .product-card-bottom {
                padding: 8px;
                text-align: center;
                flex-grow: 1;
                display: flex;
                flex-direction: column;
                align-items: start;
                justify-content: space-around;

                .product-name {
                  margin: 0;
                  font-size: 13px;
                  color: #333;
                  line-height: 1.3;
                  /* Limit to 2 lines */
                  // display: -webkit-box;
                  -webkit-line-clamp: 2;
                  -webkit-box-orient: vertical;
                  overflow: hidden;
                  display: flex;
                  align-items: start;
                  justify-content: flex-end; /* Align text to the right */
                  text-align: left;
                }
              }

              .placeholder-icon {
                font-size: 2rem;
                user-select: none;
                -webkit-user-select: none;
                -moz-user-select: none;
                -ms-user-select: none;
                /* Default color, will be overridden below */
              }

              
            }

            .product-item:hover {
              box-shadow: 0 4px 10px rgba(0,0,0,0.15);
              border-color: #0090da;
            }

          }
        }

        
      }

      .payment-action {
        background-color: white;
        margin: 0.3rem;
        border-radius: 0.3rem;
        flex-shrink: 0; // Prevent footer from shrinking
        z-index: 2; // Ensure it stays on top visually

        .payment-button {
          width: 100%;
          background-color: $kv-primary;
          color: white;
          border: none;
          border-radius: 0.3rem;
          padding: 0.8rem 0;
          font-size: 1.2rem;
          font-weight: bold;
          cursor: pointer;
        }
      }
      


    }

  }

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


.suggestions-item {
  display: flex;
  flex-direction: column;
  padding: 0.5rem 1rem 0.5rem 1rem;
  border-radius: 0.5rem;
  margin: 0rem 0.2rem 0.3rem 0.2rem;
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
  background-color: rgba($main-bg-color, 1);
  z-index: 2;
  border-radius: 0 0 0.3rem 0.3rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.514);
  margin-left: 0.3rem;
  max-height: 60vh;
  overflow-y: auto;
}


.user-name{
  margin-right: 2rem;
  padding-right: 1rem;
  color: white;
  // font-weight: bold;
  margin-right: 1rem;
  display: flex;
  align-items: center;
}

::-webkit-scrollbar {
    width: 0.4em;
}

/* Track */
::-webkit-scrollbar-track {
    -webkit-border-radius: 5px;
    border-radius: 5px;
}

/* Handle */
::-webkit-scrollbar-thumb {
    -webkit-border-radius: 5px;
    border-radius: 5px;
    background: rgba(160, 160, 160, 0.463); 
    -webkit-box-shadow: inset 0 0 6px rgba(0, 0, 0, 0.352); 
}
</style>
