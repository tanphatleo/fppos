<template>
  <div class="work-area">
    <div class="top-area">
      <div class="page-name-area">Sổ Quỹ</div>
      <div class="action-area">
        <div class="other-actions">
          <div class="buttons-area">

            <v-btn color="primary" @click="createNewItem" class="create-new-btn">
              Tạo mới
            </v-btn>

            <v-btn color="primary" @click="toggleSubList" class="create-new-btn create-new-btn-group" style="position:relative;">
              Bank Accounts
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
            </v-btn>

            <v-btn color="primary" @click="toggleSubList2" class="create-new-btn create-new-btn-group-2" style="position:relative;">
              Loại Giao Dịch
              <div class="list-product-groups btn-group" style="position:relative;">
                <Teleport to="body">
                  <div v-if="showSubList2" ref="subListRef2" class="product-group-teleport" @click.self="showSubList2 = false" :style="{ position: 'fixed', maxHeight:'50vh' , 
                      overflow : 'auto', top: subListPosition2.top, left: subListPosition2.left, zIndex: 9999, background: 'white', border: '1px solid #ccc', borderRadius: '6px', boxShadow: '0 2px 8px rgba(0,0,0,0.15)', padding: '1rem', minWidth: subListPosition2.width }">
                    <ul style="margin:0; padding:0; list-style:none;">
                      <li v-for="item in subList2" :key="item.id" style="padding:0.5rem 0; border-bottom:1px solid #eee;">
                        <span>{{ item.name }}</span>
                        <button v-if="item.id > 2" @click.stop.prevent="openAddEditSub2  (item)" class="c-button"> 
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
          :items="filteredItems"
          :items-per-page="pageSize"
          :page.sync="currentPage"
          class="elevation-1 "
          fixed-header
          :search="filterText"
          @click:row="openEditItem"
        >
          <template v-slot:top>
            <v-toolbar flat class="tool-bar">
              <v-text-field
                v-model="filterText"
                label="Tìm hàng hóa"
                dense
                hide-details
                solo
                class="product-search-input c-input"
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
import AddEditSettings from './AddEditSettings.vue';
import AddEditAccounts from './AddEditAccounts.vue';
import AddEditTransactionType from './AddEditTransactionType.vue';

export default {
  name: 'Trans',
  components: {
    AddEditSettings,
    AddEditAccounts,
    AddEditTransactionType
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
        const response = await axios.get('/accounts/');
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
        { title: 'id', key: 'id' , headerProps: { class: 'my-custom-header-class' }},  
        { title: 'Mã', key: 'key' , headerProps: { class: 'my-custom-header-class' }},
        { title: 'Nội Dung', key: 'value' , headerProps: { class: 'my-custom-header-class' }},
        { title: 'Kích Hoạt', key: 'is_active' , headerProps: { class: 'my-custom-header-class' }},
    ];

    const isActiveFilter = ref(null);
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
      return value.toLocaleString('en-US', { style: 'currency', currency: 'VND', minimumFractionDigits: 0 });
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


    };
  },
};
</script>

<style lang="scss" scoped>
$back-ground-color: rgb(165, 165, 165);
$kv-primary-color: #0070F4;
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
        // border: 2px solid green; /* Debugging border */

        .filter-area {
            width: 15rem;
            margin: 0.3rem;
            border-radius: 0.5rem;
            background-color: rgb(214, 214, 214);


            .filters {
                padding: 0.5rem;
                display: flex;
                flex-direction: column;
                // background-color: rgb(180, 180, 180);
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
            
            .c-input{
                // padding;
                height: auto !important;
                width: 20rem;
                // background-color: $back-ground-color !important;
                color: black;
                border-top-left-radius: 0.5rem !important;
            }

            .page-size-holder{
                // background-color: $back-ground-color !important;
                color: black;
            }

            .tool-bar{
                background-color: rgba(255, 0, 0, 0) !important;
                margin-bottom: 0.3rem;
                
               
            }

            .elevation-1{
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

.c-button{
    margin-left: 0.5rem;
}

</style>