<template>
  <div class="work-area">
    <div class="top-area">
      <div class="page-name-area">Hàng Hóa</div>
      <div class="action-area">
        <div class="other-actions">
          <div class="buttons-area">

            <v-btn color="primary" @click="createNewProduct" class="create-new-btn">
              Tạo mới
            </v-btn>

            <v-btn color="primary" @click="openAddEditProductGroup()" class="create-new-btn">
              Tạo Nhóm mới
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
          <v-select
            v-model="productGroupFilter"
            :items="[ ...productGroups]"
            item-title="name"
            item-value="id"
            label="Nhóm sản phẩm"
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
          :items="filteredProducts"
          :items-per-page="pageSize"
          :page.sync="currentPage"
          class="elevation-1 "
          fixed-header
          :search="filterText"
          @click:row="openEditProduct"
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
          <template v-slot:item.productGroup="{ item }">
            <div style="display: flex; align-items: center; width: 100%;">
              <span>{{ item.productGroup }}</span>
              <button @click.stop.prevent="openAddEditProductGroup(item.product_group)" class="c-button"> 
                <i class="fa-solid fa-pen-to-square"></i>
              </button>
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
      :productGroup="editingProductGroup"
      @close="showAddEditProductGroupModal = false"
        @saved="onProductGroupSaved"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue';
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
        { title: 'Mã', key: 'code' , headerProps: { class: 'my-custom-header-class' }},  
        { title: 'Tên', key: 'name' , headerProps: { class: 'my-custom-header-class' }},
        { title: 'Giá', key: 'price' ,headerProps: { class: 'my-custom-header-class' }},
        { title: 'Nhóm', key: 'productGroup' ,headerProps: { class: 'my-custom-header-class' }},
        { title: 'Loại', key: 'product_type' ,headerProps: { class: 'my-custom-header-class' }},
        { title: 'Trạng thái', key: 'is_active' ,headerProps: { class: 'my-custom-header-class' }},
    ];

    const isActiveFilter = ref(null);
    const productGroupFilter = ref(null);
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
      return value.toLocaleString('en-US', { style: 'currency', currency: 'VND', minimumFractionDigits: 0 });
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


      editingProductGroup.value = productGroupTrue;
      showAddEditProductGroupModal.value = true;
    };

    onMounted(() => {
      fetchProducts();
      fetchProductGroups();
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
      showAddEditProductGroupModal
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