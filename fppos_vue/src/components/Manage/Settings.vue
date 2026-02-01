<template>
  <div class="work-area">
    <div class="top-area">
      <div class="page-name-area">Cài Đặt</div>
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
            <button class="c-button" @click="openEditItem($event, { item })">
              <i class="fa-solid fa-pen-to-square"></i>
            </button>
          </template>
          <template v-slot:item.price="{ item }">
            {{ formatPrice(item.price) }}
          </template>
        </v-data-table>
      </div>
    </div>
    <AddEditSettings
      v-if="showAddEditItem"
      :item="selectedItem"
      @close="showAddEditItem = false"
      @saved="onItemSaved"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
import axios from 'axios';
import AddEditSettings from './AddEditSettings.vue';

export default {
  name: 'Settings',
  components: {
    AddEditSettings,
  },
  setup() {
    const items = ref([]);
    const filterText = ref('');
    const currentPage = ref(1);
    const pageSize = ref(50);
    const showAddEditItem = ref(false);
    const selectedItem = ref({});
    const headers = [
        { title: '', key: 'actions', sortable: false, headerProps: { class: 'my-custom-header-class' }, cellProps: { class: 'text-left' } },
        { title: 'id', key: 'id' , headerProps: { class: 'my-custom-header-class' }, cellProps: { class: 'text-left' }  },  
        { title: 'Mã', key: 'key' , headerProps: { class: 'my-custom-header-class' }, cellProps: { class: 'text-left' }  },
        { title: 'Nội Dung', key: 'value' , headerProps: { class: 'my-custom-header-class' }, cellProps: { class: 'text-left' }  },
        { title: 'Kích Hoạt', key: 'is_active' , headerProps: { class: 'my-custom-header-class' }, cellProps: { class: 'text-left' }  },
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
        (item.name && item.name.toLowerCase().includes(search)) 
      );
    });

    const fetchItems = async () => {
      try {
        const response = await axios.get('/logicconfigs/');
        items.value = response.data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      } catch (error) {
        console.error('Error fetching items:', error);
      }
    };

    const formatPrice = (value) => {
      if (typeof value !== 'number') return value;
      return value.toLocaleString('en-US');
    };

    function exportToCSV() {
      const csvRows = [];
      // Headers
      csvRows.push(headers.map(h => h.title).join(','));
      // Data
      filteredItems.value.forEach(row => {
        csvRows.push(headers.map(h => {
          let val = row[h.key];
          if (h.key === 'price') val = formatPrice(val);
          return '"' + (val !== undefined ? String(val).replace(/"/g, '""') : '') + '"';
        }).join(','));
      });
      const csvString = csvRows.join('\n');
      const blob = new Blob([csvString], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'data.csv';
      a.click();
      window.URL.revokeObjectURL(url);
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

    function createNewItem() {
      selectedItem.value = {};
      showAddEditItem.value = true;
    }

    async function onItemSaved() {

        console.log("Item saved, refreshing list...");
        await fetchItems();


        showAddEditItem.value = false;
      
    }

    

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
      exportToCSV,
      openAddItem,
      openEditItem,
      createNewItem,
      onItemSaved,
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
