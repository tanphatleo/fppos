<template>
  <div class="work-area">
    <div class="top-area">
      <div class="page-name-area">Khách Hàng</div>
      <div class="action-area">
        <div class="other-actions">
          <div class="buttons-area">

            <v-btn color="primary" @click="createNewCustomer" class="create-new-btn">
              Tạo mới
            </v-btn>

            <v-btn color="primary" @click="exportToCSV" class="export-btn">
              Export CSV
            </v-btn>

          </div>
        </div>
      </div>
    </div>
    <div class="bottom-area">
      <div class="filter-area">
        <div class="filters" style="display: flex; align-items: center; gap: 1rem;">
          <v-select
            v-model="isActiveFilter"
            :items="[
              { title: 'Kích hoạt', value: true },
              { title: 'Không kích hoạt', value: false }
            ]"
            item-title="title"
            item-value="value"
            label="Trạng thái"
            dense
            hide-details
            style="width: 100%;"
            multiple
          />
        </div>
      </div>
      <div class="data-area">
        <v-data-table
          :headers="headers"
          :items="filteredCustomers"
          :items-per-page="pageSize"
          :page.sync="currentPage"
          class="elevation-1 "
          fixed-header
          :search="filterText"
          @click:row="openEditCustomer"
        >
          <template v-slot:top>
            <v-toolbar flat class="tool-bar">
                <v-text-field
                    v-model="filterText"
                    label="Tìm khách hàng"
                    dense
                    hide-details
                    solo
                    class="customer-search-input c-input"
                />
                <v-select
                    v-model="pageSize"
                    :items="[5, 10, 20, 50,100, 200]"
                    label="Rows per page"
                    class="page-size-holder"
                    dense
                    hide-details
                    style="max-width: 120px"
                />
            </v-toolbar>
          </template>
        </v-data-table>
      </div>
    </div>
    <AddEditCustomer
      v-if="showAddEdit"
      :customer="selectedCustomer"
      :regionList="provinces"
      :wardList="wards"
      @close="showAddEdit = false"
      @saved="onCustomerSaved"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import axios from 'axios';
import AddEditCustomer from './AddEditCustomer.vue';
import { useStore } from 'vuex';

export default {
  name: 'Customers',
  components: {
    AddEditCustomer
  },
  setup() {
    const store = useStore();
    const customers = ref([]);
    const filterText = ref('');
    const currentPage = ref(1);
    const pageSize = ref(200);
    const showAddEdit = ref(false);
    const selectedCustomer = ref({});
    const wards = ref([]);
    const provinces = ref([]);
    const headers = [
        { title: 'Mã', key: 'code', headerProps: { class: 'my-custom-header-class' }},
        { title: 'Tên', key: 'name', headerProps: { class: 'my-custom-header-class' }},
        { title: 'Chi Nhánh', key: 'branch', headerProps: { class: 'my-custom-header-class' }},
        { title: 'Số điện thoại', key: 'phone_number', headerProps: { class: 'my-custom-header-class' }},
        { title: 'Trạng thái', key: 'is_active', headerProps: { class: 'my-custom-header-class' }},
    ];

    const isActiveFilter = ref(null);
    const filteredCustomers = computed(() => {
      let result = customers.value;

      if (isActiveFilter.value && isActiveFilter.value.length > 0) {
        result = result.filter(customer => isActiveFilter.value.includes(customer.is_active));
      }

      if (!filterText.value.trim()) return result;

      const search = filterText.value.toLowerCase();
      return result.filter(customer =>
        (customer.name && customer.name.toLowerCase().includes(search)) ||
        (customer.email && customer.email.toLowerCase().includes(search)) ||
        (customer.phone && customer.phone.toLowerCase().includes(search))
      );
    });

    const fetchCustomers = async () => {
      store.commit('setLoading', true);
      try {
        const response = await axios.get('/customers/', {
          params: {
            _limit: 500,
            _sort: 'created_at',
            _order: 'desc'
          }
        });
        customers.value = response.data;
      } catch (error) {
        console.error('Error fetching customers:', error);
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

    function createNewCustomer() {
      selectedCustomer.value = {};
      showAddEdit.value = true;
    };

    function exportToCSV() {
      const csvRows = [];
      csvRows.push(headers.map(h => h.title).join(','));
      filteredCustomers.value.forEach(row => {
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
      showAddEdit.value = true;
    }

    async function onCustomerSaved() {
      await fetchCustomers();
      showAddEdit.value = false;
    }

    onMounted(() => {
      fetchCustomers();
      fetchProvincesWards();
    });

    return {
      customers,
      filterText,
      currentPage,
      pageSize,
      showAddEdit,
      selectedCustomer,
      headers,
      filteredCustomers,
      isActiveFilter,
      provinces,
      wards,
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
                    flex-direction: row;
                    // padding: 1rem;
                    .create-new-btn {
                        margin-right: 0.5rem;
                        padding: 0.5rem;
                        // no shadow
                        border: none;
                        color: $kv-primary-color;
                        border: #0070F4 1px solid;


                    }

                    .export-btn {
                        padding: 0.5rem;
                    }
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
      background-color: rgb(214, 214, 214);

      .filters {
        padding: 0.5rem;
        display: flex;
        flex-direction: column;
      }
    }

    .data-area {
      flex: 1;
      margin: 0.3rem;
      overflow-x: auto;

      .v-table {
        background-color: rgb(243, 243, 243) !important;
      }

      .c-input {
        height: auto !important;
        width: 20rem;
        color: black;
        border-top-left-radius: 0.5rem !important;
      }

      .page-size-holder {
        color: black;
      }

      .tool-bar {
        background-color: rgba(255, 0, 0, 0) !important;
        margin-bottom: 0.3rem;
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