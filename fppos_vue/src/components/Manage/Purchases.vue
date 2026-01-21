<template>
  <div class="work-area">
    <div class="top-area">
      <div class="page-name-area">Nhập hàng</div>
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

            <button @click="createNewItem" class="btn btn-primary">
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
          <template v-slot:item.total_quantity="{ item }">
            {{ item.total_quantity }}
          </template>
          <template v-slot:item.date="{ item }">
            {{ formatDate(item.date) }}
          </template>
        </v-data-table>
      </div>
    </div>
    <AddEditPurchase
      v-if="showAddEditItem"
      :item="selectedItem"
      :d_edit_days="d_edit_days"
      @close="showAddEditItem = false"
      @saved="onItemSaved"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, onBeforeUnmount, watch } from 'vue';
import axios from 'axios';
import AddEditPurchase from './AddEditPurchase.vue';
import { useStore } from 'vuex';


export default {
  name: 'Purchases',
  components: {
    AddEditPurchase,
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

    const items = ref([]);
    const filterText = ref('');
    const currentPage = ref(1);
    const pageSize = ref(50);
    const showAddEditItem = ref(false);
    const selectedItem = ref({});

    const getLocalDateISO = (date) => {
      return new Date(date.getTime() - (date.getTimezoneOffset() * 60000)).toISOString().slice(0, 10);
    };
    const dateFrom = ref(getLocalDateISO(new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)));
    const dateTo = ref(getLocalDateISO(new Date()));
    
    const headers = [
        { title: '', key: 'actions', sortable: false, headerProps: { class: 'my-custom-header-class' }, cellProps: { class: 'text-left' } },
        { title: 'Mã đơn', key: 'code' , headerProps: { class: 'my-custom-header-class' }, cellProps:  { class: 'text-left'}},
        { title: 'Nhà cung cấp', key: 'supplier' , headerProps: { class: 'my-custom-header-class' }, cellProps:  { class: 'text-left'}},
        { title: 'Ngày nhập', key: 'date' , headerProps: { class: 'my-custom-header-class' }, cellProps:  { class: 'text-left'}},
        { title: 'Tổng Số Lượng', key: 'total_quantity' , headerProps: { class: 'my-custom-header-class' }, align: 'end', cellProps:  { class: 'text-right'}},
        { title: 'Kích hoạt', key: 'is_active' , headerProps: { class: 'my-custom-header-class pr-2' }, align: 'end', cellProps:  { class: 'text-right pr-2'}},
    ];

    const isActiveFilter = ref([true]);
    const filteredItems = computed(() => {
      let result = items.value;

      if (isActiveFilter.value && isActiveFilter.value.length > 0) {
        result = result.filter(item => isActiveFilter.value.includes(item.is_active));
      }

      if (!filterText.value.trim()) return result;

      const search = filterText.value.toLowerCase();
      return result.filter(item =>
        (item.code && item.code.toLowerCase().includes(search)) ||
        (item.supplier && item.supplier.toLowerCase().includes(search))
      );
    });

    const fetchItems = async () => {
      try {
        const response = await axios.get('/purchases/', {
          params: {
            dateFrom: dateFrom.value,
            dateTo: dateTo.value
          }
        });
        // Sort by date descending
        items.value = response.data.sort((a, b) => new Date(b.date) - new Date(a.date));
      } catch (error) {
        console.error('Error fetching purchases:', error);
      }
    };

    const formatPrice = (value) => {
      const val = Number(value);
      if (isNaN(val)) return value;
      return val.toLocaleString('vi-VN', { style: 'currency', currency: 'VND', minimumFractionDigits: 0 });
    };

    const formatDate = (dateString) => {
        if (!dateString) return '';
        const date = new Date(dateString);
        return date.toLocaleDateString('vi-VN');
    }

    async function exportToCSV() {
      try {
        const response = await axios.get('/purchases/', {
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
        a.download = 'purchases.xlsx';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      } catch (error) {
        console.error('Error exporting purchases:', error);
      }
    }

    function openAddItem() {
      selectedItem.value = {};
      showAddEditItem.value = true;
    }

    function openEditItem(event, { item }) {
      console.log("Clicked item:", item); 
      selectedItem.value = { ...item }; 
      showAddEditItem.value = true;
    }

    function createNewItem() {
      selectedItem.value = {};
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
      formatPrice,
      formatDate,
      exportToCSV,
      openAddItem,
      openEditItem,
      createNewItem,
      onItemSaved,
      dateFrom,
      dateTo,
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
