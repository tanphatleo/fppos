<template>
  <div class="work-area">
    <div class="top-area">
      <div class="page-name-area">Khách Hàng</div>
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
            <button @click="createNewCustomer" class="btn btn-primary">
              Tạo mới
            </button>
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
        </div>
      </div>
      <div class="data-area">
        <v-data-table
          :headers="headers"
          :items="customers"
          :items-per-page="pageSize"
          :page.sync="currentPage"
          class="elevation-1 "
          :server-items-length="totalCustomers"
          fixed-header
        >
          <template v-slot:item.actions="{ item }">
            <button class="c-button" @click="openEditCustomer($event, { item })">
              <i class="fa-solid fa-pen-to-square"></i>
            </button>
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
      @saved="onCustomerSaved"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, watch  } from 'vue';
import axios from 'axios';
import AddEditCustomer from './AddEditCustomer.vue';
import { useStore } from 'vuex';

export default {
  name: 'Customers',
  components: {
    AddEditCustomer
  },
  setup() {
    const editOrNew = ref('new'); // 'new' or 'edit'
    const store = useStore();
    const customers = ref([]);
    const filterText = ref('');
    const currentPage = ref(1);
    const pageSize = ref(50);
    const showAddEdit = ref(false);
    const selectedCustomer = ref({});
    const wards = ref([]);
    const provinces = ref([]);
    const totalCustomers = ref(0);
    const headers = [
        { title: '', key: 'actions', sortable: false, headerProps: { class: 'my-custom-header-class' } , cellProps: { class: 'text-left' }},
        { title: 'Mã', key: 'code', headerProps: { class: 'my-custom-header-class' } , cellProps:  { class: 'text-left'}},
        { title: 'Tên', key: 'name', headerProps: { class: 'my-custom-header-class' }, cellProps:  { class: 'text-left'}},
        { title: 'Số điện thoại', key: 'phone_number', headerProps: { class: 'my-custom-header-class' }, cellProps:  { class: 'text-left'}},
        { title: 'Trạng thái', key: 'is_active', headerProps: { class: 'my-custom-header-class' }, cellProps:  { class: 'text-left'}},
    ];

    const isActiveFilter = ref([true]);

    const fetchCustomers = async () => {
      // store.commit('setLoading', true);
      try {
        const params = {
          page: currentPage.value,
          page_size: pageSize.value,
        };
        if (filterText.value) {
          params.search = filterText.value;
        }
        if (isActiveFilter.value.length > 0) {
          params['is_active[]'] = isActiveFilter.value;
        }
        const response = await axios.get('/customers/', { params });
        customers.value = response.data.results;
        totalCustomers.value = response.data.count;
      } catch (error) {
        console.error('Error fetching customers:', error);
      }
      // store.commit('setLoading', false);
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

    function createNewCustomer() {
      editOrNew.value = 'new';
      selectedCustomer.value = {};
      showAddEdit.value = true;
    };

    function exportToCSV() {
      const csvRows = [];
      csvRows.push(headers.map(h => h.title).join(','));
      customers.value.forEach(row => {
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

    function openEditCustomer(event, { item }) {
      console.log('Editing customer:', item);
      selectedCustomer.value = { ...item };
      editOrNew.value = 'edit';
      showAddEdit.value = true;
    }

    async function onCustomerSaved() {
      console.log('Customer saved, refreshing list...');
      await fetchCustomers();
      showAddEdit.value = false;
    }

    watch([currentPage, pageSize, filterText, isActiveFilter], fetchCustomers, { deep: true });

    onMounted(() => {
      fetchCustomers();
      fetchProvincesWards();
    });

    return {
      editOrNew,
      customers,
      filterText,
      currentPage,
      pageSize,
      showAddEdit,
      selectedCustomer,
      headers,
      isActiveFilter,
      provinces,
      wards,
      totalCustomers,
      exportToCSV,
      openAddCustomer,
      openEditCustomer,
      onCustomerSaved,
      createNewCustomer,
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
