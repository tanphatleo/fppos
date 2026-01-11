<template>
  <div class="work-area">
    <div class="top-area">
      <div class="page-name-area">Hóa Đơn</div>
      <div class="action-area">
        <div class="other-actions">
          <div class="buttons-area">

            <button @click="toggleGroupList" class="btn btn-outline create-new-btn-group">
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
                          <i class="fa-solid fa-pen-to-square"></i>
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
              <i class="fa-solid fa-file-excel" style="margin-right: 0.5rem;"></i>
              Export CSV
            </button>

          </div>
        </div>
      </div>
    </div>
    <div class="bottom-area">
      <div class="filter-area">
        <div class="filters">
          <div class="form-group">
            <label>Trạng thái</label>
            <div class="checkbox-group">
              <label><input type="checkbox" v-model="isActiveFilter" :value="true" /> Kích hoạt</label>
              <label><input type="checkbox" v-model="isActiveFilter" :value="false" /> Không kích hoạt</label>
            </div>
          </div>
          <div class="form-group">
            <label>Từ ngày</label>
            <input type="date" v-model="dateFrom" />
          </div>
          <div class="form-group">
            <label>Đến ngày</label>
            <input type="date" v-model="dateTo" />
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
          @click:row="openEditInvoice"
        >
          <template v-slot:top>
            <div class="datatable-toolbar">
              <input
                v-model="filterText"
                placeholder="Tìm kiếm..."
                class="search-input"
              />
              <select
                v-model="pageSize"
                class="page-size-select"
              >
                <option v-for="size in [5, 10, 20, 50, 100, 200]" :key="size" :value="size">{{ size }} rows</option>
              </select>
            </div>
          </template>
        </v-data-table>
      </div>
    </div>
    <AddEditCustomer
      v-if="showAddEdit"
      :customer="selectedCustomer"
      :regionList="provinces"
      :wardList="wards"
      :type="editOrNew"
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
import AddEditCustomer from './AddEditCustomer.vue';
import AddEditSurcharge from './AddEditSurcharges.vue';
import { useStore } from 'vuex';

export default {
  name: 'Invoices',
  components: {
    AddEditCustomer,
    AddEditSurcharge,
  },
  setup() {
    const editOrNew = ref('new'); // 'new' or 'edit'
    const groupListPosition = ref({ top: '0px', left: '0px', width: '200px' }); 
    // const surcharges = ref([]);
    const store = useStore();
    const invoices = ref([]);
    const filterText = ref('');
    const currentPage = ref(1);
    const pageSize = ref(200);
    const showAddEdit = ref(false);
    const selectedCustomer = ref({});
    const showSurchargeList = ref(false);
    const surchargeList = ref([]);
    const wards = ref([]);
    const showAddEditSurchargeModal = ref(false);
    const editingSurcharge = ref(null);
    const provinces = ref([]);
    const dateFrom = ref(new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString().substr(0, 10));
    const dateTo = ref(new Date().toISOString().substr(0, 10));
    const headers = [
        { title: 'Mã HĐ', key: 'code', headerProps: { class: 'my-custom-header-class' }},
        { title: 'Khách hàng', key: 'customer_name', headerProps: { class: 'my-custom-header-class' }},
        { title: 'Tổng tiền', key: 'final_total', headerProps: { class: 'my-custom-header-class' }},
        { title: 'Ngày', key: 'date', headerProps: { class: 'my-custom-header-class' }},
        { title: 'Trạng thái', key: 'is_active', headerProps: { class: 'my-custom-header-class' }},
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

    const handleClickOutside = (event) => {
      if (showSurchargeList.value) {
        const groupListEl = groupListRef.value;
        if (groupListEl && !groupListEl.contains(event.target)) {
          showSurchargeList.value = false;
        }
      }
    };

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

    const isActiveFilter = ref([]);
    const filteredInvoices = computed(() => {
      let result = invoices.value;

      if (isActiveFilter.value && isActiveFilter.value.length > 0) {
        result = result.filter(invoice => isActiveFilter.value.includes(invoice.is_active));
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
        console.log('Fetched surcharges:', surchargeList.value);
      } catch (error) {
        console.error('Error fetching surcharges:', error);
      }
    };

    function createNewInvoice() {
      editOrNew.value = 'new';
      selectedCustomer.value = {};
      showAddEdit.value = true;
    };

    function exportToCSV() {
      const csvRows = [];
      csvRows.push(headers.map(h => h.title).join(','));
      filteredInvoices.value.forEach(row => {
        csvRows.push(headers.map(h => {
          let val = row[h.key];
          return '"' + (val !== undefined ? String(val).replace(/"/g, '""') : '') + '"';
        }).join(','));
      });
      const csvString = csvRows.join('\n');
      const blob = new Blob([csvString], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'customers.csv';
      a.click();
      window.URL.revokeObjectURL(url);
    }

    function openAddCustomer() {
      selectedCustomer.value = {};
      showAddEdit.value = true;
    }

    function openEditInvoice(event, { item }) {
      console.log('Editing customer:', item);
      selectedCustomer.value = { ...item };
      editOrNew.value = 'edit';
      showAddEdit.value = true;
    }

    async function onInvoiceSaved() {
      console.log('Customer saved, refreshing list...');
      await fetchInvoices();
      showAddEdit.value = false;
    }

    watch([dateFrom, dateTo], fetchInvoices);

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
      selectedCustomer,
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
      // surcharges,
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
  gap: 5px;
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
  padding: 1rem;
  background-color: #f9f9f9;
  border-bottom: 1px solid #eee;

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

                .buttons-area {
                  display: flex;
                  gap: 0.5rem;
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
        height: calc(100vh - 7rem);
        background-color: white;
        color: black;
      }
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

table {
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

            background-color: #66a9f5 !important;
            
        }
    }

}

.my-custom-header-class {
    background-color: #00000000 !important;

    font-weight: bold;
    color: black;
    padding-left: 0.5rem;
    padding-top: 0.4rem;
    padding-bottom: 0.4rem;
}

.v-data-table td, .v-data-table th {
    text-align: left !important;
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


</style>