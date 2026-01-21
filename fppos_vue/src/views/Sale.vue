<template>
  
  <div style="height: 100%; " >
    <div class="home-page " style="height: 100%;">
      <div class="page-header">
        <div class="header-left">
          <div class="col-left-control">
            <div class="product-search">
              <i class="fas fa-search"></i>
              <input class="product-search-input c-input" placeholder="Tìm hàng hóa" @focus="search_input_focus" @blur="search_input_blur" @input="search_input_change"/>
              <div class="place-holder"> </div>
              <div class="product-search-results">
                <ul v-for="product in filteredProducts" 
                  :key="product.id" >
                  <li class="suggestions-item" 
                    :data-product-id="product.id"
                    @mousedown="add_product(product)">
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
                  :data-sale-id="sale.id"
                  class="pending-sales-item"
                  :class="{ 'selected': index === 0 }"
                  @click="select_pending_invoice(sale.id, $event)"
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
          <div style="text-align: center; margin: 1rem 0;">
        </div>
          <div class="menu-toggle"> 
            <menu_toggle @menu-action="handleMenuAction"/>
          </div>
        </div>  
      </div>
      <div class="body-page">
        <div class="detail-box">
          <Carts :focus_invoice="focus_invoice"
          @update-invoice="handleUpdateItem"
          />
        </div>
        <div class="shortcut-box">
          <div class="shortcut-box-header">
            <div class="search_filter-control">
              <div class="customer-search" v-bind:class="{ 'is-hidden': focus_invoice && focus_invoice.customer }">
                <i class="fas fa-search"></i>
                <input class="customer-search-input c-input" placeholder="Tìm khách hàng" @focus="search_input_focus" @blur="search_input_cust_blur" @input="search_input_change_cust"/>
                <i class="fas fa-plus add-cust" @click="this.editOrNew = 'new'; isCustomerModalOpen = true; "></i>
                <div class="place-holder"> </div>
                <div class="customer-search-results is-hidden">
                  <ul v-for="customer in filteredCust" 
                  :key="customer.id" 
                  :id="'customer-' + customer.id"
                  @mousedown="select_focus_customer(customer)"
                  >
                    <li class="suggestions-item">
                      <div class="suggestions-item-info"> 
                        <h5><b>{{ customer.name }}</b></h5>
                        <div class="number-blue"> {{ customer.phone_number }}</div>
                      </div>
                      <div class="suggestions-item-info"> {{ customer.code }}</div>
                    </li>
                  </ul>
                </div>
              </div>
              <div class="customer-selected" v-bind:class="{ 'is-hidden': !focus_invoice || !focus_invoice.customer }">
                <span class="customer-search-input c-input edit-cust"
                @click="this.editOrNew = 'edit'; isCustomerModalOpen = true; "  
                > {{ focus_invoice && focus_invoice.customer ? focus_invoice.customer.name : '' }} 
                </span>
                <i class="fa fa-times add-cust" @click="remove_focus_customer"></i>
                <div class="place-holder"> </div>
              </div>
            </div>
            <div class="product-header-right" @click="isFilterModalOpen = true">
              <i class="fas fa-list-ul no-select"></i>
            </div>
          </div>
          <div class="product-short-list">
            <div class="product-grid-container">
              <div class="product-list">
                <div
                  v-for="product in products" 
                  :key="product.id" 
                  :data-product-id="product.id"
                  class="product-item is-hidden"
                  :class="{ 'is-not-hidden': (product.is_active) && (productGroupFilter.length === 0 || productGroupFilter.includes(product.productGroup)) && (searchQuery === '' || product.name.toLowerCase().includes(searchQuery) || product.code.toLowerCase().includes(searchQuery)) }"
                  @click="add_product(product)"
                >
                  <div class="product-card-top">  
                    <i class="fas fa-image placeholder-icon"></i>
                  </div>

                  <div class="product-card-bottom">
                    <h4 class="product-name ">{{ limit_text(product.name, 25) }}</h4>
                    <h4 class="product-price no-select">{{ formatPrice(product.price) }}</h4>
                  </div>

                </div>
              </div>

            </div>
          </div>
          <div class="payment-action no-select">
            <button class="payment-button"
                        :disabled="!focus_invoice.totalItems"
                        @click="openPaymentModal">
                          Thanh toán
                        </button>
          </div>

        </div>
      </div>
      <div class="page-footer no-select">
      
      </div>
    </div>
  </div>
  <AddCust 
    v-if="isCustomerModalOpen" 
    :current-branch="this.branch"
    :customer="focus_invoice.customer"
    :regionList="this.provinces"
    :wardList="this.wards"
    :type="this.editOrNew"
    @close="isCustomerModalOpen = false" 
    @save="handleCustomerSave"
  />
  <ProfuctFilterCate 
    v-if="isFilterModalOpen" 
    :dataSource="this.productGroups"
    @update:visible="isFilterModalOpen = false" 
    @apply="applyProductFilter"
  />

  <Payment 
    v-if="isPaymentModalOpen"
    :visible="isPaymentModalOpen"
    :cart-data="this.focus_invoice"
    :channels="this.channels"
    :default-surcharges="this.defaultSurcharges"
    :bank-accounts="this.bankAccounts"
    :transport-companies="this.transportCompanies"
    @close="isPaymentModalOpen = false"
    @update-cart-data="handleUpdateItem"
    @complete-payment="handleCompletePayment"
  />

  <AddEditTrans 
    v-if="showAddEditTrans"
    :item="selectedTransItem"
    :accounts="allAccounts"
    :transaction-types="transactionTypes"
    @close="showAddEditTrans = false"
    @saved="onTransSaved"
  />

  <!-- Print Button -->
  

  

</template>
<script>
// import { search } from 'core-js/fn/symbol';
import menu_toggle from '@/components/Sale/menu_toogle.vue';
import AddCust from '@/components/Sale/AddCust.vue';
import Carts from '@/components/Sale/Carts.vue';
import ProfuctFilterCate from '@/components/Sale/ProfuctFilterCate.vue';
import Payment from '@/components/Sale/Payment.vue';
import AlertModule from '@/components/common/AlertModule.vue';
import AddEditTrans from '@/components/Manage/AddEditTrans.vue';

import { createApp } from 'vue';

import axios from 'axios';

  export default {
    name: "SaleView",
    components: {
      menu_toggle,
      AddCust,
      Carts, 
      ProfuctFilterCate,
      Payment,
      AlertModule,
      AddEditTrans
    },
    data() {
      return {
  
        products: [],
        filteredProducts: [], 
        localPendingSales: [], 
        branch: '',
        isCustomerModalOpen: false, 
        isPaymentModalOpen: false,
        focus_invoice: {},
        isFilterModalOpen: false,
        filteredCust: [],
        provinces: [],
        wards: [],
        productGroupFilter: [],
        editOrNew: 'new',
        bankAccounts: [],
        transportCompanies: [],
        channels: [],
        defaultSurcharges: [],
        allAccounts: [],
        transactionTypes: [],
        showAddEditTrans: false,
        selectedTransItem: {},
        searchQuery: '',
        sampleInvoice: {
          id: 1,
          total: 0,
          totalItems: 0,
          discount: 0,
          finalTotal: 0,
          note: '',
          customer: null,
          totalSurcharge: 0,
          surcharges: [],
          paymentMethod: 'cash',
          paymentAccount: 1, // default to Cash account
          chosenDiscountMethod: 'VND',
          discountMethodValue: 0,
          transportCompany: null,
          amountPaidByCustomer: 0,
          changeDue: 0,
          amountPaidTransportCompany: 0,
          chosenBankAccount: null,
          items: [
          ]
        }
      }
    },
    
    computed: {
      user() {
        return this.$store.getters.userName;
      }
    },
    methods: {

      handleMenuAction(action) {
        switch (action) {
          case 'viewReport':
            this.$router.push('/manage');
            break;
          case 'receipt':
            this.selectedTransItem = { debit_or_credit: 'DR' };
            this.showAddEditTrans = true;
            break;
          case 'payment':
            this.selectedTransItem = { debit_or_credit: 'CR' };
            this.showAddEditTrans = true;
            break;
          case 'date_end_inventory':
            this.$router.push('/manage?view=date_end_inventory');
            break;
          case 'date_end_cash_balance':
            this.$router.push('/manage?view=date_end_cash_balance');
            break;
          default:
            console.log('Unknown action:', action);
        }
      },

      onTransSaved() {
        this.showAddEditTrans = false;
        this.triggerAlert("Lưu giao dịch thành công!", 3000);
      },

      triggerAlert(message, duration=30000) {
        const alertContainer = document.createElement('div');
        document.body.appendChild(alertContainer);

        const alertApp = createApp(AlertModule, { message, duration });
        alertApp.mount(alertContainer);

        // Remove the alert from DOM after it's closed
        setTimeout(() => {
          alertApp.unmount();
          document.body.removeChild(alertContainer);
        }, duration + 1000); // Extra second to ensure it's unmounted after duration
      },
      
      async handleCompletePayment (payload) {
        if (!this.isPaymentModalOpen) return;
        console.log("Payment completed with payload:", payload);
        
        // Clear the current focus invoice
        // this.focus_invoice = null;

        // Remove the paid invoice from localPendingSales
        console.log("Pending sales before payment:", this.localPendingSales);
        console.log("Focus invoice before payment:", this.focus_invoice);
        console.log("Removing invoice with ID:", this.focus_invoice.id);
        setTimeout(() => {
          
        }, 10);
        this.localPendingSales = this.localPendingSales.filter(sale => parseInt(sale.id) !== parseInt(this.focus_invoice.id));
        console.log("Pending sales after removal:", this.localPendingSales);
        await this.$nextTick();
        localStorage.setItem('pendingSales', JSON.stringify(this.localPendingSales));
        
        // this.focus_invoice = {};

        // Update local storage
        

        // Select the first pending sale if available
        if (this.localPendingSales.length > 0) {
          this.select_pending_invoice(this.localPendingSales[0].id, null);
        } else {
          // If no pending sales left, create a new one
          this.add_new_pending_sale();
          localStorage.setItem('pendingSales', JSON.stringify(this.localPendingSales));
          this.select_pending_invoice(this.localPendingSales[0].id, null);
          this.focus_invoice = this.localPendingSales[0];
        }
        
        console.log("Pending sales after payment:", this.localPendingSales);
        // close 
        this.isPaymentModalOpen = false;
        
        const mess_ = "Tạo hóa đơn #" + payload.code + " thành công!";
        this.triggerAlert(mess_, 5000);
        
      },

      openPaymentModal() {
        this.focus_invoice = JSON.parse(JSON.stringify(this.focus_invoice));
        this.isPaymentModalOpen = true;
      },

      limit_text(text, maxLength) {
        if (text.length <= maxLength) {
          return text;
        }
        return text.slice(0, maxLength) + '...';
      },

      select_focus_customer(customer) {
        // console.log("Selected customer:", customer);
        this.focus_invoice.customer = customer;
        this.handleUpdateItem(this.focus_invoice);
        // clear search input
        document.querySelector('.customer-search-input').value = '';
      },

      applyProductFilter(filterCriteria) {
        // console.log("Applying product filter with criteria:", filterCriteria);
        // window.alert("Filter applied! (Functionality to be implemented)");
        // window.alert(JSON.stringify(filterCriteria));
        this.productGroupFilter = filterCriteria;
        // Implement filtering logic based on filterCriteria
        // For example, filter by category, price range, etc.
      },

      formatPrice(value) {
        return new Intl.NumberFormat('vi-VN').format(value);
      },

      search_input_focus(event) {
        // console.log("Input focused");
        // console.log(event);
        event.target.select();
      },

      search_input_blur(event) {
        // console.log("Input blurred");
        // get element with class product-search-results and hide it
        document.querySelector('.product-search-results').classList.add('is-hidden');
        // console.log(event);
      }, 

      async fetchSurcharges() {
        try {
          const response = await axios.get('/surcharges/');
          this.defaultSurcharges = response.data.filter(surcharge => surcharge.is_active);
          // console.log('Fetched surcharges:', this.defaultSurcharges);
        } catch (error) {
          console.error('Error fetching surcharges:', error);
        }
      },

      async search_input_change_cust(event) {

        document.querySelector('.customer-search-results').classList.remove('is-hidden');
        const query = event.target.value.toLowerCase();

        await axios.get('/search_customers/', {
          params: {
            query: query, 
            exclude: 'SP_'
          }
        }).then(response => {
          this.filteredCust = response.data;
        }).catch(error => {
          console.error('Error searching customers:', error);
        });


        // window.alert("Searching for customer: " + query);
      //   this.filteredCust = [{
      //     id: 1,
      //     code: 'CUST001',
      //     name: 'Nguyen Van A',
      //     phone: '0909123456'
      //   },
      //   {
      //     id: 2,
      //     code: 'CUST002',
      //     name: 'Tran Thi B',
      //     phone: '0909876543'
      //   },
      //   {
      //     id: 3,
      //     code: 'CUST003',
      //     name: 'Le Van C',
      //     phone: '0912345678'
      //   }
      // ];
      },

      search_input_cust_blur(event) {
        // console.log("Input blurred");
        // get element with class product-search-results and hide it
        document.querySelector('.customer-search-results').classList.add('is-hidden');
        // console.log(event);
      },

      search_input_change(event) {
        // console.log("Input changed");
        // console.log(event);
        document.querySelector('.product-search-results').classList.remove('is-hidden');
        const query = event.target.value.toLowerCase();
        this.searchQuery = query;
        this.filteredProducts = this.products.filter(product => 
          product.name.toLowerCase().includes(query) || 
          product.code.toLowerCase().includes(query) 
        );
      }, 

      async select_pending_invoice(id, event) {
        // add selected to this li and remove from others
        const items = document.querySelectorAll('.pending-sales-item');
        items.forEach(item => {
          item.classList.remove('selected');
          // window.alert("Removed selected from item " + item.getAttribute('data-sale-id'));
        });
        
        // loop through add selected to data-sale-id = id
        const targetItem = document.querySelector(`[data-sale-id="${id}"]`);
        // console.log(targetItem);
        // window.alert("Selected invoice " + id);
        if (targetItem) {
          targetItem.classList.add('selected');
        }

        // filter localPendingSales to get the one with id and assign to focus_invoice
        // window.alert("Selected invoice " + id);
        this.focus_invoice = this.localPendingSales.find(sale => sale.id === id);
        // console.log("Focus invoice set to:", this.focus_invoice);
        // window.alert("Focus invoice set to:", this.focus_invoice);

        // update local storage selected_invoice_id
        localStorage.setItem('selected_invoice_id', id);

        
      }, 

      remove_pending_sale(event) {
        event.stopPropagation(); // prevent triggering parent click event
        // console.log("Remove pending sale");
        // console.log(event);
        const index = Array.from(event.currentTarget.parentNode.parentNode.children).indexOf(event.currentTarget.parentNode);
        this.localPendingSales.splice(index, 1);
        // update local storage

        // check if localPendingSales is empty
        if (this.localPendingSales.length === 0) {
          this.focus_invoice = {};
          localStorage.removeItem('selected_invoice_id');

          // add a new pending sale
          this.localPendingSales.push(this.sampleInvoice);
          this.select_pending_invoice(this.localPendingSales[0].id, null);


        } else {
          // select first pending sale
          this.select_pending_invoice(this.localPendingSales[0].id, null);
        }

        localStorage.setItem('pendingSales', JSON.stringify(this.localPendingSales));
      },

      async  add_new_pending_sale() {
        // console.log("Add new pending sale");
        const newId = this.localPendingSales.length > 0 ? Math.max(...this.localPendingSales.map(sale => sale.id)) + 1 : 1;
        // copy sampleInvoice and set id to newId
        const newInvoice = JSON.parse(JSON.stringify(this.sampleInvoice));
        newInvoice.id = newId;
        // newInvoice.unique_code = 'INV-' + Date.now();

        this.localPendingSales.push(newInvoice);

        // update local storage
        localStorage.setItem('pendingSales', JSON.stringify(this.localPendingSales));

        // select the new pending sale
        this.$nextTick(() => {
          this.select_pending_invoice(newId, null);
        });
        // this.select_pending_invoice(newId, null);

        // select the new pending sale
        // this.focus_invoice = this.localPendingSales[this.localPendingSales.length - 1];

      },

      async handleUpdateItem(updatedInvoice) {

        // console.log("Handling update for invoice:", updatedInvoice);
        // json partse object 
        // let parsed = JSON.stringify(updatedInvoice);

        // window.alert(parsed);

        // replace the invoice in localPendingSales with the updated one
        const index = this.localPendingSales.findIndex(sale => sale.id === updatedInvoice.id);
        if (index !== -1) {
          this.localPendingSales.splice(index, 1, updatedInvoice);

          // update local storage
          localStorage.setItem('pendingSales', JSON.stringify(this.localPendingSales));
          // console.log("Pending sales updated in local storage.", this.localPendingSales);
        }

        // check if focus_invoice is the updated one, if so, update it
        await this.select_pending_invoice(updatedInvoice.id, null);

        // console.log("Updated invoice:", this.focus_invoice);
        // console.log("Item updated in cart");
        // Additional logic can be added here if needed
        // console.log(this.localPendingSales);
      },

      async update_total_and_quantity() {
        if (!this.focus_invoice || !Array.isArray(this.focus_invoice.items)) return;
        let total = 0;
        let totalItems = 0;
        this.focus_invoice.items.forEach(item => {
          total += (item.price || 0) * (item.quantity || 0);
          totalItems += (item.quantity || 0);
        });
        this.focus_invoice.total = total;
        this.focus_invoice.finalTotal = total - (this.focus_invoice.discount || 0) + (this.focus_invoice.totalSurcharge || 0);
        this.focus_invoice.totalItems = totalItems;
      },

      remove_focus_customer() {
        this.focus_invoice.customer = null;
        this.handleUpdateItem(this.focus_invoice);
      },

      async add_product(product) {
        // window.alert("Add product to cart");
        // console.log(product);
        if (!product) return;
        // Check if product already exists in cart
        const existingItem = this.focus_invoice.items.find(item => item.code === product.code);
        if (existingItem) {
          existingItem.quantity += 1; // Increment quantity
        } else {
          this.focus_invoice.items.push({
            code: product.code,
            name: product.name,
            price: product.price,
            quantity: 1,
            hasNote: false,
            product_type: product.product_type,
            package_details: product.package_details || null,
            note: '',
            isOpenPopover: false
          });
        }
        await this.update_total_and_quantity();

        await this.handleUpdateItem(this.focus_invoice);
      },


      async fetchProducts() {

        try {
          const response = await axios.get('/products/');
          this.products = response.data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
          this.products = this.products.filter(product => product.is_active);

        } catch (error) {
          console.error('Error fetching products:', error);
        }

        
      },

      async fetchProductGroups() {
        try {
          const response = await axios.get('/productgroups/');
          this.productGroups = response.data;
        } catch (error) {
          console.error('Error fetching product groups:', error);
        }
      },

      async fetchLogicConfigs() {
        // Fetch logic configurations from the backend
        axios.get('/logicconfigs/')
          .then(response => {
            // console.log('Logic configurations response:', response.data);
            
            for (const config of response.data) {
              // console.log(`Processing config - Key: ${config.key}, Value: ${JSON.parse(config.value)}`);
              if (config.key === 'branch_name') {
                this.branch = config.value;
                // console.log('Branch name set to:', this.branch);
              }

              if (config.key === 'channels') {
                this.channels = JSON.parse(config.value);
                // console.log('Channels set to:', this.channels);
              }

              if (config.key === 'transportCompanies') {
                this.transportCompanies = JSON.parse(config.value);
                // console.log('Transport companies set to:', this.transportCompanies);
              }

              // Add more configuration keys as needed
            }

            // console.log('Fetched logic configurations:', this.logicConfigs);
          })
          .catch(error => {
            console.error('Error fetching logic configurations:', error);
          });
      },

      async fetchProvincesWards() {
      try {
        const [provincesResponse, wardsResponse] = await Promise.all([
          axios.get('/provinces/'),
          axios.get('/wards/')
        ]);
        this.provinces = provincesResponse.data;
        this.wards = wardsResponse.data;
      } catch (error) {
        console.error('Error fetching provinces or wards:', error);
      }
      }, 

      async fetchBankAccounts() {
        try {
          const response = await axios.get('/accounts/');
          this.allAccounts = response.data.filter(account => account.is_active);
          this.bankAccounts = this.allAccounts.filter(account => account.bank_name !== 'Cash');
          // console.log('Fetched bank accounts:', this.bankAccounts);
        } catch (error) {
          console.error('Error fetching bank accounts:', error);
        }
      },

      async fetchTransactionTypes() {
        try {
          const response = await axios.get('/transactiontypes/');
          this.transactionTypes = response.data;
        } catch (error) {
          console.error('Error fetching transaction types:', error);
        }
      },


    },
    
    created() {
      // Simulate fetching products from an API
      this.fetchProducts();
      this.fetchProductGroups();
      this.fetchLogicConfigs();
      this.fetchProvincesWards() ;
      this.fetchSurcharges();
      this.fetchBankAccounts();
      this.fetchTransactionTypes();

      
      // read pending sales from local storage
      const pendingSales = localStorage.getItem('pendingSales');
      if (pendingSales) {
        this.localPendingSales = JSON.parse(pendingSales);
        this.focus_invoice = this.localPendingSales[0];
      } else {
        // if no pending sales, create a new one
        this.localPendingSales.push(this.sampleInvoice);
        this.focus_invoice = this.localPendingSales[0];
      }



      // console.log("Pending Sales on created:", this.localPendingSales);

      

    },

    mounted() {
      const localSelectedInvoiceId = localStorage.getItem('selected_invoice_id');
      // window.alert("Loaded selected invoice ID: " + localSelectedInvoiceId);
      if (parseInt(localSelectedInvoiceId)) {
        this.select_pending_invoice(parseInt(localSelectedInvoiceId), null);
      } else {
        this.focus_invoice = this.localPendingSales[0];
      }

      // this.focus_invoice = this.localPendingSales[0];
      // console.log("Pending Sales Loaded:", this.localPendingSales);
      // console.log("Focus Invoice:", this.focus_invoice);
    }
  }
</script>

<style lang="scss" scoped>
$kv-primary: #0070F4;
$size-sm: 4vh;
$main-bg-color: rgb(253, 253, 253);

.no-select {
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}


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
      flex: 1;
      // background-color: rgba(128, 128, 128, 1);
      
      margin: 0.3rem;
      border-radius: 0.3rem;
      height: calc(100% - 0.6rem); // Account for margin (0.3 top + 0.3 bottom)
    }

    .shortcut-box {
      min-width: 30rem;
      width: 35rem;
      // flex: 1;
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
        margin-left: 0.3rem;
        padding: 0rem 0.4rem 0 7px;
        // border-bottom: 1px solid lightgray;
        
        .search_filter-control{
          // margin-left: 1rem;
          display: flex;
          flex-direction: row;
          height: 2.5rem;
          
          width: 70%;

          .customer-search {
              // display: none !important;
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

              .customer-search-results {
                position: absolute;
                max-height: 50vh;
                height: auto;
                top: 100%;
                left: 0;
                right: 0;
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 0.3rem;
                overflow-y: auto;
                z-index: 10;
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                margin-top: 0.2rem;
                margin-left: 0.2rem;
                padding-top: 0.2rem;

                &.is-hidden {
                  display: none;
                }

                .suggestions-item {
                  padding: 0.5rem 1rem;
                  cursor: pointer;

                  &:hover {
                    background-color: #f0f0f0;
                  }

                  .suggestions-item-info {
                    display: flex;
                    justify-content: space-between;
                  }
                }
              }
          }

          .customer-selected {
            position: relative;
            height: 100%;
            padding: 0.2rem 0 0.2rem 0.2rem;
            flex-grow: 1;
            display: flex;

            span {
              text-align: left;
              border: 1px solid gray;
              // outline: none;
              background-color: rgba(gray, 0.1);
              border-radius: 0.3rem;
              width: 100%;
              height: 100%;
              font-size: 1rem;
              color: $kv-primary;
              font-weight: bold;
              display: flex;
              align-items: center;

            }

            i.fa-times {
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
            

            .product-item.is-not-hidden {
              display: flex !important;
            }

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
                  font-size: 0.9rem;
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

                .product-price {
                  margin: 0;
                  font-size: 14px;
                  font-weight: bold;
                  color: $kv-primary;
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

        .payment-button:disabled {
          background-color: gray;
          cursor: not-allowed;
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

.c-input.edit-cust{
  cursor: pointer;
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
