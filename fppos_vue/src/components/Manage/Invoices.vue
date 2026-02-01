<template>
  <div class="work-area">
    <div class="top-area">
      <div class="page-name-area">Hóa Đơn</div>
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
            <button @click="triggerImportShopee" class="btn btn-primary" style="margin-right: 0.5rem;">
              Import SP
            </button>
            <button @click="toggleGroupList" class="btn btn-outline create-new-btn-group" style="margin-right: 0.5rem;" v-if ="store.getters.userAdmin || store.getters.userSuperadmin">
              Phụ Phí
            </button>
              <div class="list-product-groups btn-group" style="position:relative;" >
                <Teleport to="body">
                  <div v-if="showSurchargeList" ref="groupListRef" class="product-group-teleport" @click.self="showSurchargeList = false" :style="{ 
                      position: 'fixed', 
                      maxHeight:'50vh' , 
                      overflow : 'auto', top: groupListPosition.top, 
                      left: groupListPosition.left, zIndex: 9999, 
                      background: 'white', border: '1px solid #ccc', borderRadius: '6px', boxShadow: '0 2px 8px rgba(0,0,0,0.15)', padding: '1rem', minWidth: groupListPosition.width }">
                    <ul style="margin:0; padding:0; list-style:none;">
                      <li v-for="surcharge in surchargeList" :key="surcharge.id" style="padding:0.5rem 0; border-bottom:1px solid #eee;">
                        <span>{{ surcharge.code }}</span>
                        <button @click.stop.prevent="openAddEditSurcharge(surcharge)" class="c-button">
                          <i class="fas fa-edit"></i>
                        </button>
                      </li>
                      <!-- li for create new -->
                      <li style="padding:0.5rem 0; border-bottom:none;">
                        <button @click="openAddEditSurcharge(null)" style="padding:0.3rem 1rem;">+ Tạo mới</button>
                      </li>
                    </ul>
                    <div style="text-align:right; margin-top:0.5rem;">
                      <button @click="showSurchargeList = false" style="padding:0.3rem 1rem;">Đóng</button>
                    </div>
                  </div>
                </Teleport>
              </div>

            <button @click="exportToCSV" class="btn btn-secondary">
              <i class="fas fa-file-excel" style="margin-right: 0.5rem;"></i>
              Export CSV
            </button>

            
            <input type="file" ref="fileInputShopee" style="display: none" @change="handleFileUploadShopee" />
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
            <label>Người bán</label>
            <div class="multiselect-dropdown" ref="sellerFilterDropdownRef">
              <button @click="toggleSellerFilterDropdown" class="multiselect-toggle">
                {{ selectedSellerNames }}
              </button>
              <div v-if="showSellerFilterDropdown" class="multiselect-menu">
                <div class="multiselect-item">
                  <label>
                    <input type="checkbox" v-model="allSellersSelected" style="margin-right: 0.5rem;"/>
                    Tất cả
                  </label>
                </div>
                <div v-for="seller in uniqueSellers" :key="seller" class="multiselect-item">
                  <label>
                    <input type="checkbox" v-model="sellerFilter" :value="seller" style="margin-right: 0.5rem;"/>
                    {{ seller }}
                  </label>
                </div>
              </div>
            </div>
          </div>
          <div class="form-group">
            <label>Kênh bán</label>
            <div class="multiselect-dropdown" ref="channelFilterDropdownRef">
              <button @click="toggleChannelFilterDropdown" class="multiselect-toggle">
                {{ selectedChannelNames }}
              </button>
              <div v-if="showChannelFilterDropdown" class="multiselect-menu">
                <div class="multiselect-item">
                  <label>
                    <input type="checkbox" v-model="allChannelsSelected" style="margin-right: 0.5rem;"/>
                    Tất cả
                  </label>
                </div>
                <div v-for="channel in uniqueChannels" :key="channel" class="multiselect-item">
                  <label>
                    <input type="checkbox" v-model="channelFilter" :value="channel" style="margin-right: 0.5rem;"/>
                    {{ channel }}
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
          :items="filteredInvoices"
          :items-per-page="pageSize"
          :page.sync="currentPage"
          class="elevation-1 "
          fixed-header
          :search="filterText"
        >
          <template v-slot:item.actions="{ item }">
            <button v-if="isEditable(item.date)" class="c-button" @click="openEditInvoice($event, { item })">
              <i class="fas fa-edit"></i>
            </button>
          </template>
          <template v-slot:item.final_total="{ item }">
            {{ formatPrice(item.final_total) }}
          </template>
          <template v-slot:item.created_at="{ item }">
            {{ formatDateTime(item.created_at) }}
          </template>
        </v-data-table>
      </div>
    </div>
    <AddEditInvoice
      v-if="showAddEdit"
      :item="selectedInvoice"
      :channels="channels"
      @close="showAddEdit = false"
      @saved="onInvoiceSaved"
    />

    <AddEditSurcharge
      v-if="showAddEditSurchargeModal"
      :item="editingSurcharge"
      @close="showAddEditSurchargeModal = false"
      @saved="fetchSurcharges"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick, onBeforeUnmount, watch} from 'vue';
import axios from 'axios';
import AddEditInvoice from './AddEditInvoices.vue';
import AddEditSurcharge from './AddEditSurcharges.vue';
import { useStore } from 'vuex';
// import store from 'vuex';

export default {
  name: 'Invoices',
  components: {
    AddEditInvoice,
    AddEditSurcharge,
  },
  props: {
    channels: {
      type: Array,
      default: () => []
    },
    d_edit_days: {
      type: Number,
      default: 3
    }
  },
  setup(props) {
    

    const editOrNew = ref('new'); // 'new' or 'edit'
    const groupListPosition = ref({ top: '0px', left: '0px', width: '200px' }); 
    // const surcharges = ref([]);
    const store = useStore();
    const invoices = ref([]);
    const filterText = ref('');
    const currentPage = ref(1);
    const pageSize = ref(200);
    const showAddEdit = ref(false);
    const selectedInvoice = ref({});
    const showSurchargeList = ref(false);
    const surchargeList = ref([]);
    const wards = ref([]);
    const showAddEditSurchargeModal = ref(false);
    const editingSurcharge = ref(null);
    const provinces = ref([]);
    const sellerFilter = ref([]);
    const uniqueSellers = ref([]);
    const showSellerFilterDropdown = ref(false);
    const sellerFilterDropdownRef = ref(null);
    const channelFilter = ref([]);
    const uniqueChannels = ref([]);
    const showChannelFilterDropdown = ref(false);
    const channelFilterDropdownRef = ref(null);
    const fileInputShopee = ref(null);

    const triggerImportShopee = () => {
      if (fileInputShopee.value) {
        fileInputShopee.value.click();
      }
    };

    const channels = computed(() => {
      return props.channels || [];
    });

    const handleFileUploadShopee = async (event) => {
      const file = event.target.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append('file', file);

      store.commit('setLoading', true);
      try {
        await axios.post('/process_shopee/', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        await fetchInvoices();
        window.alert("Import thành công!");
      } catch (error) {
        console.error("Error importing shopee file:", error);
        window.alert("Lỗi import file: " + (error.response?.data?.message || error.message));
      } finally {
        store.commit('setLoading', false);
        event.target.value = null;
      }
    };

    const getLocalDateISO = (date) => {
      return new Date(date.getTime() - (date.getTimezoneOffset() * 60000)).toISOString().slice(0, 10);
    };

    const dateFrom = ref(getLocalDateISO(new Date(Date.now() - 7 * 24 * 60 * 60 * 1000)));
    const dateTo = ref(getLocalDateISO(new Date()));
    const headers = [
        { title: '', key: 'actions', sortable: false, headerProps: { class: 'my-custom-header-class' } , cellProps:  { class: 'text-left'}},
        { title: 'Mã HĐ', key: 'code', headerProps: { class: 'my-custom-header-class' }, cellProps:  { class: 'text-left'}},
        { title: 'Khách hàng', key: 'customer_name', headerProps: { class: 'my-custom-header-class' }, cellProps:  { class: 'text-left'}},
        { title: 'Người bán', key: 'seller', headerProps: { class: 'my-custom-header-class' }, cellProps:  { class: 'text-left'}},
        { title: 'Tổng tiền', key: 'final_total', headerProps: { class: 'my-custom-header-class' },align: 'end' ,cellProps:  { class: 'text-right'}},
        { title: 'Ngày', key: 'date', headerProps: { class: 'my-custom-header-class' }, align: 'end', cellProps:  { class: 'text-right'}},
        
        { title: 'Trạng thái', key: 'is_active', headerProps: { class: 'my-custom-header-class' },align: 'end', cellProps:  { class: 'text-right'}},
        { title: 'Thời gian tạo', key: 'created_at', headerProps: { class: 'my-custom-header-class pr-3' }, align: 'end', cellProps:  { class: 'text-right pr-3'}},
    ];

    const groupListRef = ref(null);

    const toggleGroupList = () => {
      showSurchargeList.value = !showSurchargeList.value;
      if (showSurchargeList.value) updateGroupListPosition();
    }

    const updateGroupListPosition = () => {
      nextTick(() => {
        const btn = document.querySelector('.create-new-btn-group');
        if (btn) {
          const rect = btn.getBoundingClientRect();
          groupListPosition.value = {
            top: `${rect.bottom + window.scrollY}px`,
            left: `${rect.left + window.scrollX}px`,
            width: `${rect.width}px`
          };
        }
      });
    };

    const toggleSellerFilterDropdown = () => {
      showSellerFilterDropdown.value = !showSellerFilterDropdown.value;
    };

    const toggleChannelFilterDropdown = () => {
      showChannelFilterDropdown.value = !showChannelFilterDropdown.value;
    };

    const handleClickOutside = (event) => {
      if (showSurchargeList.value) {
        const groupListEl = groupListRef.value;
        if (groupListEl && !groupListEl.contains(event.target)) {
          showSurchargeList.value = false;
        }
      }
      if (showSellerFilterDropdown.value) {
        if (sellerFilterDropdownRef.value && !sellerFilterDropdownRef.value.contains(event.target)) {
          showSellerFilterDropdown.value = false;
        }
      }
      if (showChannelFilterDropdown.value) {
        if (channelFilterDropdownRef.value && !channelFilterDropdownRef.value.contains(event.target)) {
          showChannelFilterDropdown.value = false;
        }
      }
    };

    const selectedSellerNames = computed(() => {
      if (!sellerFilter.value || sellerFilter.value.length === 0) return 'Tất cả';
      if (sellerFilter.value.length === uniqueSellers.value.length) return 'Tất cả';
      if (sellerFilter.value.length > 1) return `${sellerFilter.value.length} người bán đã chọn`;
      return sellerFilter.value[0];
    });

    const allSellersSelected = computed({
      get: () => uniqueSellers.value.length > 0 && sellerFilter.value.length === uniqueSellers.value.length,
      set: (value) => {
        if (value) {
          sellerFilter.value = uniqueSellers.value.slice();
        } else {
          sellerFilter.value = [];
        }
      }
    });

    const selectedChannelNames = computed(() => {
      if (!channelFilter.value || channelFilter.value.length === 0) return 'Tất cả';
      if (channelFilter.value.length === uniqueChannels.value.length) return 'Tất cả';
      if (channelFilter.value.length > 1) return `${channelFilter.value.length} kênh đã chọn`;
      return channelFilter.value[0];
    });

    const allChannelsSelected = computed({
      get: () => uniqueChannels.value.length > 0 && channelFilter.value.length === uniqueChannels.value.length,
      set: (value) => {
        if (value) {
          channelFilter.value = uniqueChannels.value.slice();
        } else {
          channelFilter.value = [];
        }
      }
    });

    const openAddEditSurcharge = (item) => {
        
        let surchargeTrue = surchargeList.value.find(pg => {
          if (typeof item === 'object' && item !== null) {
            return pg.id === item.id;
          } else {
            return pg.id === item;
          }
        });
        console.log("Editing surcharge:", surchargeTrue);

      showSurchargeList.value = false;
      editingSurcharge.value = surchargeTrue;
      showAddEditSurchargeModal.value = true;
    };

    const isActiveFilter = ref([true]);
    const filteredInvoices = computed(() => {
      let result = invoices.value;

      if (isActiveFilter.value && isActiveFilter.value.length > 0) {
        result = result.filter(invoice => isActiveFilter.value.includes(invoice.is_active));
      }

      if (sellerFilter.value && sellerFilter.value.length > 0) {
        result = result.filter(invoice => sellerFilter.value.includes(invoice.seller));
      }

      if (channelFilter.value && channelFilter.value.length > 0) {
        result = result.filter(invoice => channelFilter.value.includes(invoice.channel));
      }

      if (!filterText.value.trim()) return result;

      const search = filterText.value.toLowerCase();
      return result.filter(invoice =>
        (invoice.code && invoice.code.toLowerCase().includes(search)) ||
        (invoice.customer_name && invoice.customer_name.toLowerCase().includes(search))
      );
    });

    const fetchInvoices = async () => {
      store.commit('setLoading', true);
      try {
        const response = await axios.get('/invoices/', {
          params: {
            dateFrom: dateFrom.value,
            dateTo: dateTo.value,
          }
        });
        invoices.value = response.data;
      } catch (error) {
        console.error('Error fetching invoices:', error);
      }
      store.commit('setLoading', false);
    };

    const formatPrice = (value) => {
      if (typeof value !== 'number') return value;
      return value.toLocaleString('en-US');
    };


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



    const fetchProvincesWards = async () => {
      try {
        const [provincesResponse, wardsResponse] = await Promise.all([
          axios.get('/provinces/'),
          axios.get('/wards/')
        ]);
        provinces.value = provincesResponse.data;
        wards.value = wardsResponse.data;
      } catch (error) {
        console.error('Error fetching provinces or wards:', error);
      }
    };

    const fetchSurcharges = async () => {
      try {
        const response = await axios.get('/surcharges/', {
        });
        surchargeList.value = response.data;
        // console.log('Fetched surcharges:', surchargeList.value);
      } catch (error) {
        // console.error('Error fetching surcharges:', error);
      }
    };

    function createNewInvoice() {
      editOrNew.value = 'new';
      selectedInvoice.value = {};
      showAddEdit.value = true;
    };

    async function exportToCSV() {
      store.commit('setLoading', true);
      try {
        const response = await axios.get('/invoices/', {
          params: {
            dateFrom: dateFrom.value,
            dateTo: dateTo.value,
            export: 'true'
          },
          responseType: 'blob'
        });
        const url = window.URL.createObjectURL(new Blob([response.data]));
        const a = document.createElement('a');
        a.href = url;
        a.download = 'invoices.xlsx';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      } catch (error) {
        console.error('Error exporting invoices:', error);
      }
      store.commit('setLoading', false);
    }

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

    function openAddCustomer() {
      selectedCustomer.value = {};
      showAddEdit.value = true;
    }

    function openEditInvoice(event, { item }) {
      console.log('Editing invoice:', item);
      selectedInvoice.value = { ...item };
      editOrNew.value = 'edit';
      showAddEdit.value = true;
    }

    async function onInvoiceSaved() {
      console.log('Invoice saved, refreshing list...');
      await fetchInvoices();
      showAddEdit.value = false;
    }

    watch([dateFrom, dateTo], fetchInvoices);

    watch(invoices, (newInvoices) => {
      if (newInvoices && newInvoices.length > 0) {
        const sellers = newInvoices.map(inv => inv.seller).filter(Boolean);
        uniqueSellers.value = [...new Set(sellers)];
        const channelsData = newInvoices.map(inv => inv.channel).filter(Boolean);
        uniqueChannels.value = [...new Set(channelsData)];
      }
    });

    onMounted(() => {
      fetchInvoices();
      fetchProvincesWards();
      fetchSurcharges();
      document.addEventListener('mousedown', handleClickOutside);
    });

    onBeforeUnmount(() => {
      document.removeEventListener('mousedown', handleClickOutside);
    });

    

    return {
      editOrNew,
      invoices,
      filterText,
      currentPage,
      pageSize,
      showAddEdit,
      selectedInvoice,
      showSurchargeList,
      surchargeList,
      headers,
      filteredInvoices,
      isActiveFilter,
      provinces,
      wards,
      groupListPosition,
      groupListRef,
      showAddEditSurchargeModal,
      editingSurcharge,
      channels,
      sellerFilter,
      uniqueSellers,
      showSellerFilterDropdown,
      sellerFilterDropdownRef,
      toggleSellerFilterDropdown,
      selectedSellerNames,
      allSellersSelected,
      channelFilter,
      uniqueChannels,
      showChannelFilterDropdown,
      channelFilterDropdownRef,
      toggleChannelFilterDropdown,
      selectedChannelNames,
      allChannelsSelected,
      // surcharges,
      formatPrice,
      formatDateTime,
      exportToCSV,
      openAddCustomer,
      openEditInvoice,
      onInvoiceSaved,
      createNewInvoice,
      toggleGroupList,
      openAddEditSurcharge,
      fetchSurcharges,
      dateFrom,
      dateTo,
      fileInputShopee,
      isEditable,
      triggerImportShopee,
      handleFileUploadShopee,

      store
    };
  },
};
</script>

<style lang="scss" scoped>
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
  display: flex;
  flex-direction: column;
  box-sizing: border-box;

  .top-area {
    width: 100%;
    display: flex;
    flex-direction: row;
    padding-top: 0.5rem;

    .page-name-area {
      width: 15rem;
      margin: 0.3rem;
      font-size: 1.2rem;
      font-weight: bold;
      display: flex;
      align-items: flex-start;
      padding-left: 0.5rem;
    }

    .action-area {
      flex: 1;
      margin: 0.3rem;
      display: flex;
      flex-direction: row;
      justify-content: flex-start;
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
    }

    .data-area {
      flex: 1;
      margin: 0.3rem;
      overflow-x: auto;

      .v-table {
        background-color: rgb(243, 243, 243) !important;
      }

      .elevation-1 {
        height: calc(100vh - 7.8rem);
        background-color: white;
        color: black;
      }
    }
  }
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

.product-group-teleport {
  &::-webkit-scrollbar {
    display: none;
  }
  -ms-overflow-style: none;
  scrollbar-width: none;
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
