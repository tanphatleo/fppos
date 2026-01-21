<template>
  <div class="work-area">
    <div class="top-area">
      <div class="page-name-area">Sổ Quỹ</div>
      <div class="action-area">
        <div class="page-actions">
          <div class="datatable-toolbar">
              <input
                v-model="filterText"
                placeholder="Tìm kiếm..."
                class="search-input"
                style="margin-right: 1rem;"
              />
              <select
                v-model="pageSize"
                class="page-size-select"
              >
                <option v-for="size in [5, 10, 20, 50, 100, 200]" :key="size" :value="size">{{ size }} rows</option>
              </select>
            </div>
        </div>
        <div class="other-actions">
          <div class="buttons-area">
            <button @click="createNewItem('DR')" class="btn btn-primary" style="margin-right: 0.5rem;">
              Phiếu Thu
            </button>
            <button @click="createNewItem('CR')" class="btn btn-primary" style="margin-right: 0.5rem;">
              Phiếu Chi
            </button>
              

            <button @click="toggleSubList" class="btn btn-outline create-new-btn-group" style="margin-right: 0.5rem;" v-if="store.getters.userAdmin || store.getters.userSuperadmin">
              Bank Accounts
            </button>
              <div class="list-product-groups btn-group" style="position:relative;">
                <Teleport to="body">
                  <div v-if="showSubList" ref="subListRef" class="product-group-teleport" @click.self="showSubList = false" :style="{ position: 'fixed', maxHeight:'50vh' , 
                      overflow : 'auto', top: subListPosition.top, left: subListPosition.left, zIndex: 9999, background: 'white', border: '1px solid #ccc', borderRadius: '6px', boxShadow: '0 2px 8px rgba(0,0,0,0.15)', padding: '1rem', minWidth: subListPosition.width }">
                    <ul style="margin:0; padding:0; list-style:none;">
                      <li v-for="item in subList" :key="item.id" style="padding:0.5rem 0; border-bottom:1px solid #eee;">
                        <span>{{ item.bank_name + ' - ' + item.account_number }}</span>
                        <button @click.stop.prevent="openAddEditSub(item)" class="c-button"> 
                          <i class="fa-solid fa-pen-to-square"></i>
                        </button>
                      </li>
                      <!-- li for create new -->
                      <li style="padding:0.5rem 0; border-bottom:none;">
                        <button @click="openAddEditSub(null)" style="padding:0.3rem 1rem;">+ Tạo mới</button>
                      </li>
                    </ul>
                    <div style="text-align:right; margin-top:0.5rem;">
                      <button @click="showSubList = false" style="padding:0.3rem 1rem;">Đóng</button>
                    </div>
                  </div>
                </Teleport>
              </div>

            <template v-if="store.getters.userAdmin || store.getters.userSuperadmin">
              <button @click="toggleSubList2" class="btn btn-outline create-new-btn-group-2" style="margin-right: 0.5rem;">
                Loại Giao Dịch
              </button>
            </template>
              <div class="list-product-groups btn-group" style="position:relative;" >
                <Teleport to="body">
                  <div v-if="showSubList2" ref="subListRef2" class="product-group-teleport" @click.self="showSubList2 = false" :style="{ position: 'fixed', maxHeight:'50vh' , 
                      overflow : 'auto', top: subListPosition2.top, left: subListPosition2.left, zIndex: 9999, background: 'white', border: '1px solid #ccc', borderRadius: '6px', boxShadow: '0 2px 8px rgba(0,0,0,0.15)', padding: '1rem', minWidth: subListPosition2.width }">
                    <ul style="margin:0; padding:0; list-style:none;">
                      <li v-for="item in subList2" :key="item.id" style="padding:0.5rem 0; border-bottom:1px solid #eee;">
                        <span>{{ item.name }}</span>
                        <button v-if="item.id > 4" @click.stop.prevent="openAddEditSub2  (item)" class="c-button"> 
                          <i class="fa-solid fa-pen-to-square"></i>
                        </button>
                      </li>
                      <!-- li for create new -->
                      <li style="padding:0.5rem 0; border-bottom:none;">
                        <button @click="openAddEditSub2(null)" style="padding:0.3rem 1rem;">+ Tạo mới</button>
                      </li>
                    </ul>
                    <div style="text-align:right; margin-top:0.5rem;">
                      <button @click="showSubList2 = false" style="padding:0.3rem 1rem;">Đóng</button>
                    </div>
                  </div>
                </Teleport>
              </div>

            <button @click="exportToExcel" class="btn btn-secondary">
              <i class="fa-solid fa-file-excel" style="margin-right: 0.5rem;"></i>
              Export Excel
            </button>
            
          </div>
        </div>
      </div>
    </div>
    <div class="bottom-area">
      <div class="filter-area">
        <div class="filters">
          <div class="form-group">
            <label>Từ ngày</label>
            <input type="date" v-model="dateFrom" @click="$event.target.showPicker()" />
          </div>
          <div class="form-group">
            <label>Đến ngày</label>
            <input type="date" v-model="dateTo" @click="$event.target.showPicker()" />
          </div>
          <div class="form-group">
            <label>Trạng thái</label>
            <div class="checkbox-group">
              <label><input type="checkbox" v-model="isActiveFilter" :value="true" /> Kích hoạt</label>
              <label><input type="checkbox" v-model="isActiveFilter" :value="false" /> Không kích hoạt</label>
            </div>
          </div>
          <div class="form-group">
            <label>Loại phiếu</label>
            <div class="checkbox-group">
              <label><input type="checkbox" v-model="debitCreditFilter" value="DR" /> Phiếu thu</label>
              <label><input type="checkbox" v-model="debitCreditFilter" value="CR" /> Phiếu chi</label>
            </div>
          </div>
          <div class="form-group">
            <label>Chi tiết loại thu/chi</label>
            <div class="multiselect-dropdown" ref="transactionTypeFilterDropdownRef">
              <button @click="toggleTransactionTypeFilterDropdown" class="multiselect-toggle">
                {{ selectedTransactionTypeNames }}
              </button>
              <div v-if="showTransactionTypeFilterDropdown" class="multiselect-menu">
                <div class="multiselect-item">
                  <label>
                    <input type="checkbox" v-model="allTransactionTypesSelected" style="margin-right: 0.5rem;"/>
                    Tất cả
                  </label>
                </div>
                <div v-for="tt in filteredTransactionTypesForFilter" :key="tt.id" class="multiselect-item">
                  <label>
                    <input type="checkbox" v-model="transactionTypeFilter" :value="tt.id" style="margin-right: 0.5rem;"/>
                    {{ tt.name }}
                  </label>
                </div>
              </div>
            </div>
          </div>
          
          <div class="form-group">
            <label>Tài khoản</label>
            <div class="multiselect-dropdown" ref="bankAccountFilterDropdownRef">
              <button @click="toggleBankAccountFilterDropdown" class="multiselect-toggle">
                {{ selectedBankAccountNames }}
              </button>
              <div v-if="showBankAccountFilterDropdown" class="multiselect-menu">
                <div class="multiselect-item">
                  <label>
                    <input type="checkbox" v-model="allBankAccountsSelected" style="margin-right: 0.5rem;"/>
                    Tất cả
                  </label>
                </div>
                <div v-for="acc in allAccounts" :key="acc.id" class="multiselect-item">
                  <label>
                    <input type="checkbox" v-model="bankAccountFilter" :value="acc.id" style="margin-right: 0.5rem;"/>
                    {{ acc.bank_name }} - {{ acc.account_number }}
                  </label>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <div class="data-area">
        <v-data-table
          :headers="headers"
          :items="filteredItems"
          :items-per-page="pageSize"
          :page.sync="currentPage"
          class="elevation-1 "
          fixed-header
          :search="filterText"
        >
          <template v-slot:item.actions="{ item }">
            <button v-if="isEditable(item.date)" class="c-button" @click="openEditItem($event, { item })">
              <i class="fa-solid fa-pen-to-square"></i>
            </button>
          </template>
          <template v-slot:item.amount="{ item }">
            {{ formatPrice( parseInt(item.amount)  ) }}
          </template>
          <template v-slot:item.debit_or_credit="{item}">
            {{ item.debit_or_credit == 'DR' ? 'Phiếu Thu' : 'Phiếu Chi' }}
          </template>
          <template v-slot:item.created_at="{ item }">
            {{ formatDateTime(item.created_at) }}
          </template>
        </v-data-table>
      </div>
    </div>
    <AddEditTrans
      v-if="showAddEditItem"
      :item="selectedItem"
      :accounts="allAccounts"
      :transaction-types="subList2"
      @close="showAddEditItem = false"
      @saved="onItemSaved"
    />
    <AddEditAccounts
      v-if="showAddEditSub"
      :item="selectedSubItem"
      @close="showAddEditSub = false"
      @saved="onSubItemSaved"
    />

    <AddEditTransactionType
      v-if="showAddEditSub2"
      :item="selectedSubItem2"
      @close="showAddEditSub2 = false"
      @saved="onSubItemSaved2"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, watch, nextTick , onBeforeUnmount } from 'vue';
import axios from 'axios';
import { useStore } from 'vuex';
import AddEditTrans from './AddEditTrans.vue';
import AddEditAccounts from './AddEditAccounts.vue';
import AddEditTransactionType from './AddEditTransactionType.vue';

export default {
  name: 'Trans',
  components: {
    AddEditTrans,
    AddEditAccounts,
    AddEditTransactionType
  },
  props: {
    d_edit_days: {
      type: Number,
      default: 3
    }
  },
  setup(props) {
    const store = useStore();
    const isEditable = (itemDate) => {
      // console.log("Checking if editable for date:", itemDate);
      // console.log("User admin:", store.getters.userAdmin);


      if (store.getters.userAdmin || store.getters.userSuperadmin) {
        return true;
      }

      if (!itemDate) return false;
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      const date = new Date(itemDate);
      // console.log("Item date object:", date);
      date.setHours(0, 0, 0, 0);

      const diffDays = (today.getTime() - date.getTime()) / (1000 * 60 * 60 * 24);
      // console.log("Difference in days:", diffDays, "Allowed edit days:", props.d_edit_days);
      return diffDays < props.d_edit_days;
    };
    const showSubList = ref(false);
    const subListRef = ref(null);
    const selectedSubItem = ref(null);
    const showAddEditSub = ref(false);
    const subList = ref([]);
    const allAccounts = ref([]);
    const bankAccountFilter = ref([]);
    const showBankAccountFilterDropdown = ref(false);
    const bankAccountFilterDropdownRef = ref(null);
    const transactionTypeFilter = ref([]);
    const showTransactionTypeFilterDropdown = ref(false);
    const transactionTypeFilterDropdownRef = ref(null);

    const toggleTransactionTypeFilterDropdown = () => {
      showTransactionTypeFilterDropdown.value = !showTransactionTypeFilterDropdown.value;
    };

    const filteredTransactionTypesForFilter = computed(() => {
      if (!debitCreditFilter.value || debitCreditFilter.value.length === 0) {
        return subList2.value;
      }
      return subList2.value.filter(tt => debitCreditFilter.value.includes(tt.debit_or_credit));
    });

    const formatDateTime = (dateString) => { // format YYYY-MM-DD HH:mm:ss
      if (!dateString) return '';
      const date = new Date(dateString);
      
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      const seconds = String(date.getSeconds()).padStart(2, '0');

      return `${year}/${month}/${day} ${hours}:${minutes}:${seconds}`;
    };

    const selectedTransactionTypeNames = computed(() => {
      if (!transactionTypeFilter.value || transactionTypeFilter.value.length === 0) return 'Tất cả';
      if (transactionTypeFilter.value.length > 1) return `${transactionTypeFilter.value.length} loại đã chọn`;
      const tt = subList2.value.find(t => t.id === transactionTypeFilter.value[0]);
      return tt ? tt.name : 'Chọn loại';
    });

    const allTransactionTypesSelected = computed({
      get: () => {
        const visibleIDs = filteredTransactionTypesForFilter.value.map(tt => tt.id);
        return visibleIDs.length > 0 && visibleIDs.every(id => transactionTypeFilter.value.includes(id));
      },
      set: (value) => {
        const visibleIDs = filteredTransactionTypesForFilter.value.map(tt => tt.id);
        if (value) {
          const newSelection = [...transactionTypeFilter.value];
          visibleIDs.forEach(id => {
            if (!newSelection.includes(id)) newSelection.push(id);
          });
          transactionTypeFilter.value = newSelection;
        } else {
          transactionTypeFilter.value = transactionTypeFilter.value.filter(id => !visibleIDs.includes(id));
        }
      }
    });

    const toggleBankAccountFilterDropdown = () => {
      showBankAccountFilterDropdown.value = !showBankAccountFilterDropdown.value;
    };

    const selectedBankAccountNames = computed(() => {
      if (!bankAccountFilter.value || bankAccountFilter.value.length === 0) return 'Tất cả';
      if (bankAccountFilter.value.length === allAccounts.value.length) return 'Tất cả';
      if (bankAccountFilter.value.length > 1) return `${bankAccountFilter.value.length} tài khoản đã chọn`;
      const acc = allAccounts.value.find(a => a.id === bankAccountFilter.value[0]);
      return acc ? `${acc.bank_name} - ${acc.account_number}` : 'Chọn tài khoản';
    });

    const allBankAccountsSelected = computed({
      get: () => allAccounts.value.length > 0 && bankAccountFilter.value.length === allAccounts.value.length,
      set: (value) => {
        if (value) {
          bankAccountFilter.value = allAccounts.value.map(a => a.id);
        } else {
          bankAccountFilter.value = [];
        }
      }
    });

    const subListPosition = ref({ top: '0px', left: '0px', width: '0px' });
    const fetchSubList = async () => {
      try {
        const response = await axios.get('/accounts/');
        allAccounts.value = response.data.filter(item => item.is_active);
        // filter active only and not cash accounts
        subList.value = response.data.filter(item => item.is_active && !item.bank_name.toLowerCase().includes('cash'));
      } catch (error) {
        console.error('Error fetching sub list:', error);
      }
    };  
    const toggleSubList = () => {
      showSubList.value = !showSubList.value;
      if (showSubList.value) {
        setTimeout(() => {
          updateGroupListPosition();
        }, 0);
      }
    };

    const updateGroupListPosition = () => {
      nextTick(() => {
        const btn = document.querySelector('.create-new-btn-group');
        if (btn) {
          const rect = btn.getBoundingClientRect();
          subListPosition.value = {
            top: `${rect.bottom + window.scrollY}px`,
            left: `${rect.left + window.scrollX}px`,
            width: `${rect.width}px`
          };
        }
      });
    };
    const openAddEditSub = (item) => {
      console.log("Open Add/Edit Sub Item:", item);
      selectedSubItem.value = item ? { ...item } : {};
      showAddEditSub.value = true;
      showSubList.value = false;
    };

    const handleClickOutside = (event) => {
      if (showSubList.value) {
        const subListEl = subListRef.value;
        if (subListEl && !subListEl.contains(event.target)) {
          showSubList.value = false;
        }
      }
      if (showBankAccountFilterDropdown.value) {
        if (bankAccountFilterDropdownRef.value && !bankAccountFilterDropdownRef.value.contains(event.target)) {
          showBankAccountFilterDropdown.value = false;
        }
      }
      if (showTransactionTypeFilterDropdown.value) {
        if (transactionTypeFilterDropdownRef.value && !transactionTypeFilterDropdownRef.value.contains(event.target)) {
          showTransactionTypeFilterDropdown.value = false;
        }
      }
    };
    const onSubItemSaved = async () => {
      console.log("Sub Item saved, refreshing sub list...");
      await fetchSubList();
      showAddEditSub.value = false;
    };



    const showSubList2 = ref(false);
    const subListRef2 = ref(null);
    const selectedSubItem2 = ref(null);
    const showAddEditSub2 = ref(false);
    const subList2 = ref([]);
    // Datepicker filter state
    const getLocalDateISO = (date) => {
      return new Date(date.getTime() - (date.getTimezoneOffset() * 60000)).toISOString().slice(0, 10);
    };
    // date from default to last 30 days
    const dateFrom = ref(getLocalDateISO(new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)));

    // dateTo default to today
    const dateTo = ref(getLocalDateISO(new Date()));

    const subListPosition2 = ref({ top: '0px', left: '0px', width: '0px' });
    const fetchSubList2 = async () => {
      try {
        const response = await axios.get('/transactiontypes/');
        // filter active only and not cash accounts
        subList2.value = response.data
      } catch (error) {
        console.error('Error fetching sub list:', error);
      }
    };  
    const toggleSubList2 = () => {
      showSubList2.value = !showSubList2.value;
      if (showSubList2.value) {
        setTimeout(() => {
          updateGroupListPosition2();
        }, 0);
      }
    };
    const updateGroupListPosition2 = () => {
      nextTick(() => {
        const btn = document.querySelector('.create-new-btn-group-2');
        if (btn) {
          const rect = btn.getBoundingClientRect();
          subListPosition2.value = {
            top: `${rect.bottom + window.scrollY}px`,
            left: `${rect.left + window.scrollX}px`,
            width: `${rect.width}px`
          };
        }
      });
    };
    const openAddEditSub2 = (item) => {
      console.log("Open Add/Edit Sub Item:", item);
      selectedSubItem2.value = item ? { ...item } : {};
      showAddEditSub2.value = true;
      showSubList2.value = false;
    };
    const handleClickOutside2 = (event) => {
      if (showSubList2.value) {
        const subListEl = subListRef2.value;
        if (subListEl && !subListEl.contains(event.target)) {
          showSubList2.value = false;
        }
      }
    };
    const onSubItemSaved2 = async () => {
      console.log("Sub Item saved, refreshing sub list...");
      await fetchSubList2();
      showAddEditSub2.value = false;
    };

    const items = ref([]);
    const filterText = ref('');
    const currentPage = ref(1);
    const pageSize = ref(50);
    const showAddEditItem = ref(false);
    const selectedItem = ref({});
    const headers = [
        { title: '', key: 'actions', sortable: false, headerProps: { class: 'my-custom-header-class' },cellProps: { class: 'text-left' }},
        { title: 'Thu/Chi', key: 'debit_or_credit' , headerProps: { class: 'my-custom-header-class' } , cellProps:  { class: 'text-left'}},  
        { title: 'Mã', key: 'id' , headerProps: { class: 'my-custom-header-class' } , cellProps: { class: 'text-left' }},
        { title: 'Nội Dung', key: 'description' , headerProps: { class: 'my-custom-header-class' }  , cellProps: { class: 'text-left' }},
        { title: 'Loại', key: 'transaction_type_name' , headerProps: { class: 'my-custom-header-class' }, cellProps: { class: 'text-left' }},
        { title: 'Số Tiền', key: 'amount' , align: 'end', headerProps: { class: 'my-custom-header-class' }   , cellProps: { class: 'text-right' }},
        { title: 'Ngày Hiệu Lực', key: 'date' , align: 'end', headerProps: { class: 'my-custom-header-class' } ,  cellProps: { class: 'text-right' }},
        { title: 'Trạng Thái', key: 'is_active' , align: 'end', headerProps: { class: 'my-custom-header-class pr-3' } , cellProps: { class: 'text-right pr-3' }},
        { title: 'Tài Khoản', key: 'bank_account_name' , headerProps: { class: 'my-custom-header-class' }, cellProps: { class: 'text-left' }},
        { title: 'Ngày Tạo', key: 'created_at' , headerProps: { class: 'my-custom-header-class pr-3' }, align: 'end', cellProps: { class: 'text-right pr-3' }},

    ];

    const isActiveFilter = ref([true]);
    const debitCreditFilter = ref([]);
    const filteredItems = computed(() => {
      let result = items.value;

      if (isActiveFilter.value && isActiveFilter.value.length > 0) {
        result = result.filter(item => isActiveFilter.value.includes(item.is_active));
      }

      if (debitCreditFilter.value && debitCreditFilter.value.length > 0) {
        result = result.filter(item => debitCreditFilter.value.includes(item.debit_or_credit));
      }

      if (transactionTypeFilter.value && transactionTypeFilter.value.length > 0) {
        result = result.filter(item => transactionTypeFilter.value.includes(item.transaction_type));
      }

      if (bankAccountFilter.value && bankAccountFilter.value.length > 0) {
        result = result.filter(item => bankAccountFilter.value.includes(item.account));
      }

      if (!filterText.value.trim()) return result;

      const search = filterText.value.toLowerCase();
      return result.filter(item =>
        (item.description && item.description.toLowerCase().includes(search))
      );
    });

    const fetchItems = async () => {
      try {
        const params = {};
        if (dateFrom.value) {
          params.dateFrom = dateFrom.value;
        }
        if (dateTo.value) {
          params.dateTo = dateTo.value;
        }
        const response = await axios.get('/transactions/', { params });
        items.value = response.data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      } catch (error) {
        console.error('Error fetching items:', error);
      }
    };

    const formatPrice = (value) => {
      if (typeof value !== 'number') return value;
      return value.toLocaleString('en-US');
    };

    async function exportToExcel() {
      try {
        const params = {
          export: 'true',
          dateFrom: dateFrom.value,
          dateTo: dateTo.value,
        };
        const response = await axios.get('/transactions/', { params, responseType: 'blob' });
        
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const link = document.createElement('a');
        link.href = url;
        const filename = `transactions_${dateFrom.value}_to_${dateTo.value}.xlsx`;
        link.setAttribute('download', filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
      } catch (error) {
        console.error('Error exporting to Excel:', error);
      }
    }

    function openAddItem() {
      selectedItem.value = {};
      showAddEditItem.value = true;
    }

    function openEditItem(event, { item }) {
      // 'item' is the actual data object from the row
      console.log("Clicked item:", item); 
      
      // Create a copy to avoid mutating the table data directly while editing
      selectedItem.value = { ...item }; 
      showAddEditItem.value = true;
    }

    function createNewItem(type) {
      selectedItem.value = { debit_or_credit: type };
      showAddEditItem.value = true;
    }

    async function onItemSaved() {

        console.log("Item saved, refreshing list...");
        await fetchItems();


        showAddEditItem.value = false;
      
    }

    watch([dateFrom, dateTo], fetchItems);

    onMounted(() => {
      fetchItems();
      fetchSubList();
      fetchSubList2();
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('mousedown', handleClickOutside2);
    });

    onBeforeUnmount(() => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('mousedown', handleClickOutside2);
    });

    return {
      items,
      filterText,
      currentPage,
      pageSize,
      showAddEditItem,
      selectedItem,
      headers,
      filteredItems,
      isActiveFilter,
      debitCreditFilter,
      formatPrice,
      exportToExcel,
      openAddItem,
      openEditItem,
      createNewItem,
      onItemSaved,
      formatDateTime,

      showSubList,
      subList,
      subListPosition,
      toggleSubList,
      fetchSubList,
      showAddEditSub,
      selectedSubItem,
      openAddEditSub, 
      subListRef,
      onSubItemSaved,
      allAccounts,


      showSubList2,
      subList2,
      subListPosition2,
      toggleSubList2,
      fetchSubList2,
      showAddEditSub2,
      selectedSubItem2,
      openAddEditSub2,
      subListRef2,
      onSubItemSaved2,


      dateFrom,
      dateTo,

      bankAccountFilter,
      showBankAccountFilterDropdown,
      bankAccountFilterDropdownRef,
      toggleBankAccountFilterDropdown,
      selectedBankAccountNames,
      allBankAccountsSelected,

      transactionTypeFilter,
      showTransactionTypeFilterDropdown,
      transactionTypeFilterDropdownRef,
      toggleTransactionTypeFilterDropdown,
      filteredTransactionTypesForFilter,
      selectedTransactionTypeNames,
      allTransactionTypesSelected,
      store, // Make store available in the template
      isEditable,
    };
  },
};
</script>

<style lang="scss" scoped>
$back-ground-color: rgb(165, 165, 165);
$kv-primary-color: #0070F4;

.btn {
  padding: 8px 16px;
  border-radius: 3px;
  cursor: pointer;
  font-weight: 500;
  border: 1px solid transparent;
  display: inline-flex;
  align-items: center;
  // gap: 5px;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.0892857143em;
}

.btn-outline {
  background: white;
  border-color: $kv-primary-color;
  color: $kv-primary-color;
}

.btn-primary {
  background: $kv-primary-color;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn:hover {
  opacity: 0.9;
}

input, select {
  background-color: white;
  color: black;
  border-radius: 0.3rem;
  width: 100%;
  border: 1px solid #ccc;
  padding: 6px 10px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

input:focus, select:focus {
  border-color: $kv-primary-color;
  outline: none;
}

input[type="checkbox"] {
  width: auto;
  flex-grow: 0;
}

.datatable-toolbar {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem;
  // background-color: #f9f9f9;
  // border-bottom: 1px solid #eee;

  .search-input {
    width: 300px;
  }

  .page-size-select {
    width: 120px;
  }
}


.work-area {
    width: 100rem;
    // background-color: rgb(96, 96, 96);
    display: flex;
    flex-direction: column;
    box-sizing: border-box; /* Ensure padding is included in dimensions */


    .top-area {
        width: 100%;
        display: flex;
        flex-direction: row;
        // background-color: rgb(243, 243, 243);
        padding-top: 0.5rem;

        .page-name-area {
            width: 15rem;
            margin: 0.3rem;
            font-size: 1.2rem;
            font-weight: bold;
            display: flex;
            align-items: flex-start;
            padding-left: 0.5rem;
            // background-color: rgb(200, 200, 200);
        }

        .action-area {
            flex: 1;
            margin: 0.3rem;
            display: flex;
            flex-direction: row;
            justify-content: flex-start;
            // background-color: rgb(220, 220, 220);

            
            .other-actions {
                display: flex;
                flex-direction: row;
                justify-content: flex-end;
                flex: 1;
                padding: 0.5rem;

                .buttons-area {
                  display: flex;
                  // gap: 0.5rem;
                }
            }

        }
    }

    .bottom-area {
        flex: 1;
        width: 100%;
        display: flex;
        flex-direction: row;
        // border: 2px solid green; /* Debugging border */

        .filter-area {
            width: 15rem;
            margin: 0.3rem;
            border-radius: 0.5rem;
            background-color: #f9f9f9;
            padding: 1rem;

            .filters {
                display: flex;
                flex-direction: column;
                gap: 1.5rem;
            }

            .form-group {
              display: flex;
              flex-direction: column;
              label {
                font-weight: bold;
                margin-bottom: 0.5rem;
                text-align: left;
              }
            }

            .checkbox-group label {
              display: flex;
              align-items: center;
              font-weight: normal;
              margin-bottom: 0.5rem;
              input { margin-right: 0.5rem; }
            }

            .multiselect-dropdown {
              position: relative;
              width: 100%;
            }

            .multiselect-toggle {
              width: 100%;
              background-color: white;
              color: black;
              border-radius: 0.3rem;
              border: 1px solid #ccc;
              padding: 6px 10px;
              font-size: 1rem;
              text-align: left;
              cursor: pointer;
              white-space: nowrap;
              overflow: hidden;
              text-overflow: ellipsis;
            }

            .multiselect-menu {
              position: absolute;
              top: 100%;
              left: 0;
              right: 0;
              background: white;
              border: 1px solid #ccc;
              border-top: none;
              border-radius: 0 0 0.3rem 0.3rem;
              z-index: 10;
              max-height: 200px;
              overflow-y: auto;
              box-shadow: 0 4px 6px rgba(0,0,0,0.1);

              &::-webkit-scrollbar {
                display: none;
              }
              -ms-overflow-style: none;
              scrollbar-width: none;
            }

            .multiselect-item {
              padding: 8px 12px;
              cursor: pointer;
              
              label {
                display: flex;
                align-items: center;
                font-weight: normal;
                width: 100%;
                margin-bottom: 0;
              }
            }
            .multiselect-item:hover {
              background-color: #f0f0f0;
            }
        }

        .data-area {
            flex: 1;
            margin: 0.3rem;
            // background-color: rgb(255, 255, 255);
            overflow-x: auto;

            .v-table{
                background-color: rgb(243, 243, 243) !important;
            }

            .elevation-1{
                height: calc(100vh - 7.8rem);
                background-color: white;
                color: black;

                
            }
           
        }
    }
}

.checkbox-group {
  label {
    user-select: none;
    cursor: pointer;
  }
}

.multiselect-item label {
    user-select: none;
    cursor: pointer;
}

.product-group-teleport span {
    user-select: none;
    cursor: default;
    
}

.product-group-teleport li {
      display: flex;
      justify-content: space-between;
  
}

</style>
