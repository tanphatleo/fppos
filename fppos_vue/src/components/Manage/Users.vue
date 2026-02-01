<template>
  <div class="work-area">
    <div class="top-area">
      <div class="page-name-area">Người dùng</div>
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

            <button @click="toggleSubList" class="btn btn-outline create-new-btn-group">
              Nhóm Users
            </button>
              <div class="list-product-groups btn-group" style="position:relative;" >
                <Teleport to="body">
                  <div v-if="showSubList" ref="subListRef" class="product-group-teleport" @click.self="showSubList = false" :style="{ position: 'fixed', maxHeight:'50vh' , 
                      overflow : 'auto', top: subListPosition.top, left: subListPosition.left, zIndex: 9999, background: 'white', border: '1px solid #ccc', borderRadius: '6px', boxShadow: '0 2px 8px rgba(0,0,0,0.15)', padding: '1rem', minWidth: subListPosition.width }">
                    <ul style="margin:0; padding:0; list-style:none;">
                      <li v-for="item in subList" :key="item.id" style="padding:0.5rem 0; border-bottom:1px solid #eee;">
                        <span>{{ item.name }}</span>
                        <!-- <button @click.stop.prevent="openAddEditSub(item)" class="c-button"> 
                          <i class="fa-solid fa-pen-to-square"></i>
                        </button> -->
                      </li>
                      <!-- li for create new
                      <li style="padding:0.5rem 0; border-bottom:none;">
                        <button @click="openAddEditSub(null)" style="padding:0.3rem 1rem;">+ Tạo mới</button>
                      </li> -->
                    </ul>
                    <div style="text-align:right; margin-top:0.5rem;">
                      <button @click="showSubList = false" style="padding:0.3rem 1rem;">Đóng</button>
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
    <AddEditUsers
      v-if="showAddEditItem"
      :item="selectedItem"
      :user-groups="subList"
      @close="showAddEditItem = false"
      @saved="onItemSaved"
    />



  </div>
</template>

<script>
import { ref, computed, onMounted, watch, nextTick , onBeforeUnmount } from 'vue';
import axios from 'axios';
import AddEditUsers from './AddEditUsers.vue';


export default {
  name: 'Trans',
  components: {
    AddEditUsers,
  },
  setup() {

    const showSubList = ref(false);
    const subListRef = ref(null);
    const selectedSubItem = ref(null);
    const showAddEditSub = ref(false);
    const subList = ref([]);
    const subListPosition = ref({ top: '0px', left: '0px', width: '0px' });
    const fetchSubList = async () => {
      try {
        const response = await axios.get('/usergroups/');
        // filter active only and not cash accounts
        subList.value = response.data;
        console.log('Fetched sub list:', subList.value);
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
    };
    const onSubItemSaved = async () => {
      console.log("Sub Item saved, refreshing sub list...");
      await fetchSubList();
      showAddEditSub.value = false;
    };


    const items = ref([]);
    const filterText = ref('');
    const currentPage = ref(1);
    const pageSize = ref(50);
    const showAddEditItem = ref(false);
    const selectedItem = ref({});
    const headers = [
        { title: '', key: 'actions', sortable: false, headerProps: { class: 'my-custom-header-class' } , cellProps: { class: 'text-left' }},
        { title: 'id', key: 'id' , headerProps: { class: 'my-custom-header-class' } , cellProps: { class: 'text-left' } },  
        { title: 'userName', key: 'username' , headerProps: { class: 'my-custom-header-class' }, cellProps: { class: 'text-left' } },
        { title: 'Tên', key: 'first_name' , headerProps: { class: 'my-custom-header-class' }, cellProps: { class: 'text-left' } },
        { title: 'Họ', key: 'last_name' , headerProps: { class: 'my-custom-header-class' }, cellProps: { class: 'text-left' } },
        { title: 'Nhóm', key: 'usergroups' , headerProps: { class: 'my-custom-header-class' }, cellProps: { class: 'text-left' } },
        { title: 'Kích hoạt', key: 'is_active' , headerProps: { class: 'my-custom-header-class' }, cellProps: { class: 'text-left' } },
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
        const response = await axios.get('/users/');
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
      fetchSubList();
      document.addEventListener('mousedown', handleClickOutside);
    });

    onBeforeUnmount(() => {
      document.removeEventListener('mousedown', handleClickOutside);
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
