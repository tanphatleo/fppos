<template>
  <div class="work-area">
    <div class="top-area">
      <div class="page-name-area">Hàng Hóa</div>
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
            <button @click="createNewProduct" class="btn btn-primary" style="margin-right: 0.5rem;">
              Tạo mới
            </button>

            <button @click="toggleGroupList" class="btn btn-outline create-new-btn-group" style="margin-right: 0.5rem;">
              Nhóm SP
            </button>
              <div class="list-product-groups btn-group" style="position:relative;">
                <Teleport to="body" >
                  <div v-if="showGroupList" ref="groupListRef" class="product-group-teleport" @click.self="showGroupList = false" :style="{ position: 'fixed', maxHeight:'50vh' , overflow : 'auto', top: groupListPosition.top, left: groupListPosition.left, zIndex: 9999, background: 'white', border: '1px solid #ccc', borderRadius: '6px', boxShadow: '0 2px 8px rgba(0,0,0,0.15)', padding: '1rem', minWidth: groupListPosition.width }">
                    <ul style="margin:0; padding:0; list-style:none;">
                      <li v-for="group in productGroups" :key="group.id" style="padding:0.5rem 0; border-bottom:1px solid #eee;">
                        <span>{{ group.name }}</span>
                        <button @click.stop.prevent="openAddEditProductGroup(group)" class="c-button">
                          <i class="fa-solid fa-pen-to-square"></i>
                        </button>
                      </li>
                      <!-- li for create new -->
                      <li style="padding:0.5rem 0; border-bottom:none;">
                        <button @click="openAddEditProductGroup(null)" style="padding:0.3rem 1rem;">+ Tạo nhóm mới</button>
                      </li>
                    </ul>
                    <div style="text-align:right; margin-top:0.5rem;">
                      <button @click="showGroupList = false" style="padding:0.3rem 1rem;">Đóng</button>
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
            <label>Nhóm sản phẩm</label>
            <div class="multiselect-dropdown" ref="productGroupFilterDropdownRef">
              <button @click="toggleProductGroupFilterDropdown" class="multiselect-toggle">
                {{ selectedGroupNames }}
              </button>
              <div v-if="showProductGroupFilterDropdown" class="multiselect-menu">
                <div class="multiselect-item">
                  <label>
                    <input type="checkbox" v-model="allGroupsSelected"  style="margin-right: 0.5rem;"/>
                    Tất cả
                  </label>
                </div>
                <div v-for="group in productGroups" :key="group.id" class="multiselect-item">
                  <label>
                    <input type="checkbox" v-model="productGroupFilter" :value="group.id" style="margin-right: 0.5rem;"/>
                    {{ group.name }}
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
          :items="filteredProducts"
          :items-per-page="pageSize"
          :page.sync="currentPage"
          class="elevation-1 "
          fixed-header
          :search="filterText"
        >
          <template v-slot:item.actions="{ item }">
            <button class="c-button" @click="openEditProduct($event, { item })">
              <i class="fa-solid fa-pen-to-square"></i>
            </button>
          </template>
          <template v-slot:item.price="{ item }">
            {{ formatPrice(item.price) }}
          </template>
          <template v-slot:item.productGroup="{ item }">
            <div style="display: flex; align-items: center; width: 100%;">
              <span>{{ item.productGroup }}</span>

            </div>
          </template>
        </v-data-table>
      </div>
    </div>
    <AddEditProduct
      v-if="showAddEdit"
      :productData="selectedProduct"
      :products="products"
      :productGroups="productGroups"
      @close="showAddEdit = false"
      @saved="onProductSaved"
    />
    <AddEditProductGroup
      v-if="showAddEditProductGroupModal"
      :item="editingProductGroup"
      @close="showAddEditProductGroupModal = false"
        @saved="onProductGroupSaved"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, watch, nextTick, onBeforeUnmount } from 'vue';
import axios from 'axios';
import AddEditProduct from './AddEditProduct.vue';
import AddEditProductGroup from './AddEditProductGroup.vue';

export default {
  name: 'Products',
  components: {
    AddEditProduct,
    AddEditProductGroup
  },
  setup() {
    const showGroupList = ref(false);
    const groupListPosition = ref({ top: '0px', left: '0px', width: '200px' }); 
    const groupListRef = ref(null);

    const showProductGroupFilterDropdown = ref(false);
    const productGroupFilterDropdownRef = ref(null);

    const handleClickOutside = (event) => {
      if (showGroupList.value) {
        const groupListEl = groupListRef.value;
        if (groupListEl && !groupListEl.contains(event.target)) {
          showGroupList.value = false;
        }
      }
      if (showProductGroupFilterDropdown.value) {
        if (productGroupFilterDropdownRef.value && !productGroupFilterDropdownRef.value.contains(event.target)) {
          showProductGroupFilterDropdown.value = false;
        }
      }
    };

    const products = ref([]);
    const filterText = ref('');
    const currentPage = ref(1);
    const pageSize = ref(50);
    const showAddEdit = ref(false);
    const selectedProduct = ref({});
    const productGroups = ref([]);
    const showAddEditProductGroupModal = ref(false);
    const editingProductGroup = ref(null);
    const headers = [
        { title: '', key: 'actions', sortable: false, headerProps: { class: 'my-custom-header-class' }, cellProps: { class: 'text-left' } },
        { title: 'Mã', key: 'code' , headerProps: { class: 'my-custom-header-class' } , cellProps:  { class: 'text-left'}},  
        { title: 'Tên', key: 'name' , headerProps: { class: 'my-custom-header-class' } , cellProps:  { class: 'text-left'}},
        { title: 'Giá', key: 'price' ,headerProps: { class: 'my-custom-header-class pr-3' } , align: 'end', cellProps:  { class: 'text-right pr-3'}},
        { title: 'Nhóm', key: 'productGroup' ,headerProps: { class: 'my-custom-header-class' }, cellProps:  { class: 'text-left'}},
        { title: 'Loại', key: 'product_type' ,headerProps: { class: 'my-custom-header-class' }, cellProps:  { class: 'text-left'}},
        { title: 'Trạng thái', key: 'is_active' ,headerProps: { class: 'my-custom-header-class' }, cellProps:  { class: 'text-left'}},
    ];

    const isActiveFilter = ref([true]);
    const productGroupFilter = ref([]);

    const selectedGroupNames = computed(() => {
      if (!productGroupFilter.value || productGroupFilter.value.length === 0) return 'Tất cả';
      if (productGroupFilter.value.length === productGroups.value.length) return 'Tất cả';
      if (productGroupFilter.value.length > 1) return `${productGroupFilter.value.length} nhóm đã chọn`;
      return productGroups.value.find(g => g.id === productGroupFilter.value[0])?.name || 'Chọn nhóm';
    });

    const allGroupsSelected = computed({
      get: () => productGroups.value.length > 0 && productGroupFilter.value.length === productGroups.value.length,
      set: (value) => {
        if (value) {
          productGroupFilter.value = productGroups.value.map(g => g.id);
        } else {
          productGroupFilter.value = [];
        }
      }
    });
    const filteredProducts = computed(() => {
      let result = products.value;

      if (isActiveFilter.value && isActiveFilter.value.length > 0) {
        result = result.filter(product => isActiveFilter.value.includes(product.is_active));
      }

      if (productGroupFilter.value && productGroupFilter.value.length > 0) {
        result = result.filter(product => {
          // Support both id and object for product_group
          if (product.product_group !== undefined && product.product_group !== null) {
            return productGroupFilter.value.includes(product.product_group);
          }
          // fallback: try productGroup string (if present)
          if (product.productGroup !== undefined && product.productGroup !== null) {
            return productGroupFilter.value.some(groupId => {
              return product.productGroup === productGroups.find(g => g.id === groupId)?.name;
            });
          }
          return false;
        });
      }

      if (!filterText.value.trim()) return result;

      const search = filterText.value.toLowerCase();
      return result.filter(product =>
        (product.name && product.name.toLowerCase().includes(search)) ||
        (product.productGroup && product.productGroup.toLowerCase().includes(search)) ||
        (product.code && product.code.toLowerCase().includes(search)) ||
        (product.product_type && product.product_type.toLowerCase().includes(search))
      );
    });

    const fetchProducts = async () => {
      try {
        const response = await axios.get('/products/');
        products.value = response.data.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
      } catch (error) {
        console.error('Error fetching products:', error);
      }
    };

    const fetchProductGroups = async () => {
      try {
        const response = await axios.get('/productgroups/');
        productGroups.value = response.data;
      } catch (error) {
        console.error('Error fetching product groups:', error);
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
      filteredProducts.value.forEach(row => {
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
      a.download = 'products.csv';
      a.click();
      window.URL.revokeObjectURL(url);
    }

    function openAddProduct() {
      selectedProduct.value = {};
      showAddEdit.value = true;
    }

    function openEditProduct(event, { item }) {
      // 'item' is the actual data object from the row
      console.log("Clicked item:", item); 
      
      // Create a copy to avoid mutating the table data directly while editing
      selectedProduct.value = { ...item }; 
      showAddEdit.value = true;
    }

    function createNewProduct() {
      selectedProduct.value = {};
      showAddEdit.value = true;
    }

    async function onProductSaved() {

        console.log("Product saved, refreshing list...");
        await fetchProducts();
        // await fetchProducts();
        // send post to /products/ to create new product
        // await axios.post('/products/', selectedProduct.value)


        showAddEdit.value = false;
      
    }

    async function onProductGroupSaved() {

        console.log("Product saved, refreshing list...");
        await fetchProducts();
        await fetchProductGroups();
        // await fetchProducts();
        // send post to /products/ to create new product
        // await axios.post('/products/', selectedProduct.value)


        showAddEdit.value = false;
        showAddEditProductGroupModal.value = false;
      
    }

    const openAddEditProductGroup = (item) => {
        
        let productGroupTrue = productGroups.value.find(pg => {
          if (typeof item === 'object' && item !== null) {
            return pg.id === item.id;
          } else {
            return pg.id === item;
          }
        });
        console.log("Editing product group:", productGroupTrue);

      showGroupList.value = false;
      editingProductGroup.value = productGroupTrue;
      showAddEditProductGroupModal.value = true;
    };

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

    function toggleGroupList() {
      showGroupList.value = !showGroupList.value;
      if (showGroupList.value) updateGroupListPosition();
    }

    const toggleProductGroupFilterDropdown = () => {
      showProductGroupFilterDropdown.value = !showProductGroupFilterDropdown.value;
    };

    onMounted(() => {
      fetchProducts();
      fetchProductGroups();
      document.addEventListener('mousedown', handleClickOutside);
    });

    onBeforeUnmount(() => {
      document.removeEventListener('mousedown', handleClickOutside);
    });

    return {
      products,
      filterText,
      currentPage,
      pageSize,
      showAddEdit,
      selectedProduct,
      productGroups,
      headers,
      filteredProducts,
      productGroupFilter,
      isActiveFilter,
      formatPrice,
      exportToCSV,
      openAddProduct,
      openEditProduct,
      createNewProduct,
      onProductSaved,
      onProductGroupSaved,
      openAddEditProductGroup,
      editingProductGroup,
      showAddEditProductGroupModal,
      showGroupList,
      groupListPosition,
      toggleGroupList,
      groupListRef,
      showProductGroupFilterDropdown,
      productGroupFilterDropdownRef,
      toggleProductGroupFilterDropdown,
      selectedGroupNames,
      allGroupsSelected,
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
