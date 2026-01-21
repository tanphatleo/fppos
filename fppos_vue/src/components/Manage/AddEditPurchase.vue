<template>
  <div class="modal-overlay" @mousedown.self="$emit('close')">
    <div class="purchase-window" @click.stop style="width: 70rem; max-width: 95vw;">
      <div class="window-header">
        <span class="window-title">
          <span class="no-select">{{ item && item.id ? 'Chỉnh sửa đơn nhập hàng: ' + item.code : 'Tạo đơn nhập hàng mới' }}</span>
        </span>
        <div class="window-actions no-select">
          <button @click="$emit('close')" class="close-btn">
            <span>×</span>
          </button>
        </div>
      </div>

      <div class="window-content">
        <div class="tabs-nav no-select">
          <ul>
            <li class="active">
              <a href="#">Thông tin chung</a>
            </li>
          </ul>
        </div>

        <div class="form-body">
          <div class="tab-pane">
            <div class="form-layout" style="display: flex; flex-direction: column; height: 100%;">
              <div class="row-general" style="display: flex; gap: 1rem; margin-bottom: 0.5rem;">
                  <div class="form-group" style="flex: 1;">
                    <label for="supplier">Nhà cung cấp</label>
                    <select id="supplier" v-model="supplier" required>
                        <option v-for="s in suppliers" :key="s.id" :value="s.name">{{ s.name }}</option>
                    </select>
                  </div>
                  <div class="form-group" style="flex: 1;">
                    <label for="date">Ngày nhập</label>
                    <input id="date" ref="dateInput" v-model="date" type="date" required @click="openDatePicker" :min="minDate" :max="maxDate" :disabled="isDateOutsideAllowedRange" />
                  </div>
                  <div class="form-group" style="flex-direction: row; align-items: center;">
                    <label for="is_active" style="width: auto; margin-right: 0.5rem;">Kích hoạt</label>
                    <input id="is_active" v-model="isActive" type="checkbox" :disabled="!isActive || (!store.getters.userAdmin && !store.getters.userSuperadmin)" />
                </div>
              </div>
              <div class="row-search" style="display: flex; gap: 1rem; align-items: flex-start; margin-bottom: 0.5rem; ">
                  <div style="position: relative; flex: 1;">
                      <input 
                        type="text" 
                        v-model="productSearchTerm" 
                        placeholder="Tìm hàng hóa theo mã hoặc tên" 
                        class="product-search-input"
                        @focus="showProductDropdown = true"
                        @blur="hideDropdown"
                      />
                      <div v-if="showProductDropdown && filteredProducts.length > 0" class="search-dropdown">
                          <div 
                            v-for="p in filteredProducts" 
                            :key="p.id" 
                            class="search-item"
                            @click="addProduct(p)"
                          >
                            <div class="item-name">{{ p.name }}</div>
                            <div class="item-code">{{ p.code }}</div>
                          </div>
                      </div>
                  </div>
                  <div class="import-excel-wrapper">
                        <button class="btn btn-outline" @click="downloadTemplate" title="Download Template" style="margin-right: 1rem;">
                          Tải template Excel
                      </button>
                      <button v-if="showImportButton && !(item && item.id)" class="btn btn-outline" @click="triggerImport" title="Import Excel">
                          Nhập từ Excel
                      </button>
                      <input type="file" ref="fileInput" style="display: none" @change="handleFileUpload" accept=".xlsx, .xls" />
                  </div>
              </div>
              <div class="row-search" style="display: flex; gap: 1rem; justify-content: space-between;">
                

   
              </div>
                          
              

              <div class="row-items">
                  <div class="div-table">
                      <div class="div-table-header">
                          <div class="div-cell col-code">Mã hàng</div>
                          <div class="div-cell col-name">Tên hàng</div>
                          <div class="div-cell col-qty">Số lượng</div>
                          <div class="div-cell col-action">{{ totalQuantity }}</div>
                      </div>
                      <div class="div-table-body">
                          <div v-for="(item, index) in items" :key="index" class="div-table-row">
                              <div class="div-cell col-code">{{ item.code }}</div>
                              <div class="div-cell col-name">{{ item.name }}</div>
                              <div class="div-cell col-qty">
                                  <input type="number" v-model.number="item.quantity" class="qty-input" min="1" @focus="selectAll" @change="handleQuantityChange(item)" />
                              </div>
                              <div class="div-cell col-action">
                                  <button @click="removeItem(index)" class="btn-remove">×</button>
                              </div>
                          </div>
                      </div>
                  </div>
              </div>

             

            </div>
          </div>
        </div>

        <div class="window-footer">
          <button type="button" class="btn btn-outline" @click="$emit('close')">Đóng</button>
          <button type="button" class="btn btn-primary" @click="handleSubmit">
            {{ item && item.id ? 'Lưu' : 'Tạo mới' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, toRefs, computed, onMounted } from 'vue';
import axios from 'axios';
import * as XLSX from 'xlsx';
// import store from '@/store';
import { useStore } from 'vuex';

export default {
  name: 'AddEditPurchase',
  props: {
    item: {
      type: Object,
      default: null
    }, 
    d_edit_days: {
      type: Number,
      default: 3
    }
  },
  emits: ['close', 'saved'],
  setup(props, { emit }) {
    const getLocalDateISO = (date) => {
      const tzOffset = date.getTimezoneOffset() * 60000; // offset in milliseconds
      const localISOTime = new Date(date - tzOffset).toISOString().slice(0, 10);
      return localISOTime;
    };

    const store = useStore();
    const maxDate = computed(() => {
      return getLocalDateISO(new Date());
    });

    const minDate = computed(() => {
      if (store.getters.userAdmin || store.getters.userSuperadmin) {
        return ''; // No minimum date for admins
      }
      const today = new Date();
      const minDay = new Date();
      minDay.setDate(today.getDate() - (props.d_edit_days || 3));
      return getLocalDateISO(minDay);
    });

    const isDateOutsideAllowedRange = computed(() => {
      // If admin, date is never disabled by range
      if (store.getters.userAdmin || store.getters.userSuperadmin) {
        return false;
      }

      const currentDate = new Date(date.value);
      const minAllowed = minDate.value ? new Date(minDate.value) : null;
      const maxAllowed = maxDate.value ? new Date(maxDate.value) : null;

      // Check if current date is before minAllowed
      if (minAllowed && currentDate < minAllowed) {
        return true;
      }
      // Check if current date is after maxAllowed
      return maxAllowed && currentDate > maxAllowed;
    });

    const { item } = toRefs(props);
    const dateInput = ref(null);
    const fileInput = ref(null);

    const code = ref(item.value ? item.value.code : '');
    const supplier = ref(item.value && item.value.supplier ? item.value.supplier : 'Sản xuất');
    const date = ref(item.value && item.value.date ? item.value.date : new Date().toISOString().slice(0, 10));
    // const total_amount = ref(item.value ? item.value.total_amount : 0);
    const isActive = ref(item.value && item.value.is_active !== undefined ? item.value.is_active : true);
    
    const items = ref(item.value && item.value.items ? JSON.parse(JSON.stringify(item.value.items)) : []);
    const suppliers = ref([]);
    const products = ref([]);
    const productSearchTerm = ref('');
    const showProductDropdown = ref(false);
    const showImportButton = ref(true);

    const totalQuantity = computed(() => {
        return items.value.reduce((sum, i) => sum + (Number(i.quantity) || 0), 0);
    });

    watch(item, (newVal) => {
      code.value = newVal ? newVal.code : '';
      supplier.value = newVal && newVal.supplier ? newVal.supplier : 'Sản xuất';
      date.value = newVal && newVal.date ? newVal.date : new Date().toISOString().slice(0, 10);
      // total_amount.value = newVal ? newVal.total_amount : 0;
      isActive.value = newVal && newVal.is_active !== undefined ? newVal.is_active : true;
      items.value = newVal && newVal.items ? JSON.parse(JSON.stringify(newVal.items)) : [];
    });

    const filteredProducts = computed(() => {
        if (!productSearchTerm.value) return [];
        const lower = productSearchTerm.value.toLowerCase();
        return products.value.filter(p => 
            p.is_active && 
            p.product_type === 'normal' &&
            ((p.name && p.name.toLowerCase().includes(lower)) || 
            (p.code && p.code.toLowerCase().includes(lower)))
        ).slice(0, 6);
    });

    const fetchSuppliers = async () => {
        try {
            const response = await axios.get('/logicconfigs/');
            const config = response.data.find(c => c.key === 'suppliers');
            if (config) {
                suppliers.value = JSON.parse(config.value);
            }
        } catch (e) { console.error(e); }
    };

    const fetchProducts = async () => {
        try {
            const response = await axios.get('/products/');
            products.value = response.data;
        } catch (e) { console.error(e); }
    };

    function addProduct(p) {
        const existing = items.value.find(i => i.code === p.code);
        if (existing) {
            existing.quantity++;
        } else {
            items.value.push({
                code: p.code,
                name: p.name,
                quantity: 1,
                price: p.price || 0 // Default to price, user can edit
            });
        }
        productSearchTerm.value = '';
        showProductDropdown.value = false;
    }

    function removeItem(index) {
        items.value.splice(index, 1);
    }

    function formatPrice(value) {
        return new Intl.NumberFormat('vi-VN').format(value);
    }

    function hideDropdown() {
        setTimeout(() => {
            showProductDropdown.value = false;
        }, 200);
    }

    async function downloadTemplate() {
        try {
            const response = await axios.get('/download_purchase_template/', { responseType: 'blob' });
            const url = window.URL.createObjectURL(new Blob([response.data]));
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', 'MauFileNhapHang.xlsx');
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
        } catch (error) {
            console.error("Error downloading template:", error);
        }
    }

    function triggerImport() {
        if (fileInput.value) {
            fileInput.value.click();
        }
    }

    async function handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = (e) => {
            const data = new Uint8Array(e.target.result);
            const workbook = XLSX.read(data, { type: 'array' });
            const firstSheetName = workbook.SheetNames[0];
            const worksheet = workbook.Sheets[firstSheetName];
            const jsonData = XLSX.utils.sheet_to_json(worksheet);
            
            const invalidQuantityRows = [];
            jsonData.forEach((row, index) => {
                const quantity = Number(row['Số lượng'] || row['Quantity']);
                if (isNaN(quantity) || quantity < 1) {
                    invalidQuantityRows.push(`Dòng ${index + 2} (Mã hàng: ${row['Mã hàng'] || row['Code'] || 'N/A'}, Số lượng: ${row['Số lượng'] || row['Quantity'] || 'N/A'})`);
                }
            });
            if (invalidQuantityRows.length > 0) {
                window.alert(`Lỗi: Các dòng sau có số lượng không hợp lệ (nhỏ hơn 1 hoặc không phải số):\n${invalidQuantityRows.join('\n')}`);
                return;
            }

            const validProductsMap = new Map();
            products.value.forEach(p => {
                if (p.product_type === 'normal' && p.is_active) {
                    validProductsMap.set(p.code, p);
                }
            });

            const newItems = [];
            const invalidCodes = [];

            jsonData.forEach(row => {
                const rawCode = row['Mã hàng'] || row['Code'];
                if (!rawCode) return;
                const code = String(rawCode).trim();

                if (validProductsMap.has(code)) {
                    const product = validProductsMap.get(code);
                    newItems.push({
                        code: code,
                        name: product.name,
                        quantity: Number(row['Số lượng'] || row['Quantity']) || 1,
                        price: Number(row['Đơn giá'] || row['Price']) || product.price || 0
                    });
                } else {
                    invalidCodes.push(code);
                }
            });

            if (invalidCodes.length > 0) {
                window.alert(`Lỗi: Các mã hàng sau không tồn tại hoặc không phải là sản phẩm thường hoặc đã bị vô hiệu hóa:\n${invalidCodes.join(', ')}`);
                event.target.value = null;
                return;
            }

            items.value = [...items.value, ...newItems];
            showImportButton.value = false;
        };
        reader.readAsArrayBuffer(file);
        event.target.value = null;
    }

    function handleQuantityChange(item) {
      const qty = Number(item.quantity);
      if (isNaN(qty) || qty < 1) {
        item.quantity = 1;
      }
    }

    onMounted(() => {
        fetchSuppliers();
        fetchProducts();
    });

    function openDatePicker() {
      if (dateInput.value) {
        if (typeof dateInput.value.showPicker === 'function') {
          try {
            dateInput.value.showPicker();
          } catch (e) {
            dateInput.value.focus();
          }
        } else {
          dateInput.value.focus();
        }
      }
    }

    function selectAll(event) {
      event.target.select();
    }

    async function handleSubmit() {
      const payload = {
        code: code.value,
        supplier: supplier.value,
        date: date.value,
        is_active: isActive.value,
        items: items.value
      };

      if (payload.items.reduce((sum, item) => sum + (Number(item.quantity) || 0), 0) === 0) {
        window.alert("Vui lòng thêm ít nhất một sản phẩm với số lượng lớn hơn 0.");
        return;
      }

      if (item.value && item.value.id) {
        // Update
        await axios.put(`/purchases/${item.value.id}/`, payload)
          .then(response => {
            emit('saved', response.data);
          })
          .catch(error => {
            console.error('Error updating purchase:', error);
            window.alert("Lỗi khi cập nhật đơn nhập hàng: " + (error.response && error.response.data ? JSON.stringify(error.response.data) : error.message));
          });
      } else {
        // Create
        await axios.post('/purchases/', payload)
          .then(response => {
            emit('saved', response.data);
          })
          .catch(error => {
            console.error('Error creating purchase:', error);
            window.alert("Lỗi khi tạo đơn nhập hàng: " + (error.response && error.response.data ? JSON.stringify(error.response.data) : error.message));
          });
      }
    }

    return {
      code,
      supplier,
      date,
      totalQuantity,
      isActive,
      item,
      items,
      suppliers,
      productSearchTerm,
      filteredProducts,
      showProductDropdown,
      dateInput,
      openDatePicker,
      selectAll,
      handleSubmit,
      addProduct,
      removeItem,
      formatPrice,
      hideDropdown,
      fileInput,
      triggerImport,
      handleFileUpload,
      downloadTemplate,
      showImportButton,
      handleQuantityChange,
      maxDate,
      minDate,
      isDateOutsideAllowedRange,
      store // Make store available in the template
    };
  }
};
</script>

<style lang="scss" scoped>
$kv-primary: #0070F4;

* {
  box-sizing: border-box;
  font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  text-align: left;
}

input, select, textarea {
  background-color: white;
  color: black;
  border-radius: 0.3rem;
  width: 100%;
  border: 1px solid #ccc;
  padding: 6px 10px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

input:focus, select:focus, textarea:focus {
  border-color: $kv-primary;
  outline: none;
}

input[type="checkbox"] {
  width: auto;
  flex-grow: 0;
}

.div-table-body {
    overflow-y: auto;
    max-height: 40vh;
    padding-bottom: 1rem;
    &::-webkit-scrollbar {
        display: none;
    }
    -ms-overflow-style: none;
    scrollbar-width: none;
}

.modal-overlay {
  position: fixed;
  top: 0; left: 0;
  width: 100vw; height: 100vh;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: flex-start;
  padding-top: 3rem;
  justify-content: center;
  z-index: 2000;
}
.purchase-window {
    margin-top: 5rem;
  background: #fff;
  width: 35rem;
  max-width: 95vw;
  box-shadow: 0 2px 16px rgba(0,0,0,0.2);
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.window-header {
  background-color: $kv-primary;
  color: white;
  padding: 10px 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.window-title {
  font-weight: bold;
  font-size: 15px;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  line-height: 1;
}

.tabs-nav {
  background: #f0f0f0;
  border-bottom: 1px solid #ddd;
  padding: 0 10px;
}

.tabs-nav ul { list-style: none; padding: 0; margin: 0; display: flex; }
.tabs-nav li.active a { background: #fff; border-color: #ddd; border-bottom-color: #fff; color: #000; font-weight: 600; margin-bottom: -1px; }
.tabs-nav a { display: block; padding: 10px 15px; text-decoration: none; color: #333; border: 1px solid transparent; border-bottom: none; border-radius: 4px 4px 0 0; }

.window-content { display: flex; flex-direction: column; }

.form-body { 
    padding: 1rem; 
    background: #fff; 
    height: 60vh; 
    overflow-y: hidden;
    display: flex; 
    flex-direction: column; 
}
.tab-pane {
    display: flex;
    flex-direction: column;
    flex: 1;
    overflow: hidden;
}
.form-layout { display: flex; flex-direction: column; }
.col-left, .col-right { flex: 1; }

.form-group {
  display: flex;
  flex-direction: row;
  align-items: baseline;
  margin-bottom: 6px;
}

.form-group label {
  width: 9rem;
  color: #333;
  font-weight: 500;
  flex-shrink: 0;
  padding-right: 1em;
}

.window-footer {
  padding: 15px 20px;
  border-top: 1px solid #ddd;
  background: #f5f5f5;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.btn { padding: 8px 16px; border-radius: 3px; cursor: pointer; font-weight: 500; border: 1px solid transparent; display: inline-flex; align-items: center; gap: 5px; }
.btn-outline { background: white; border-color: $kv-primary; color: $kv-primary; }
.btn-primary { background: $kv-primary; color: white; }
.btn-primary:hover { background: #0056b3; }
.no-select { user-select: none; }

.product-search-input {
    width: 100%;
    padding: 8px;
    border: 1px solid #ccc;
    border-radius: 4px;
}

.search-dropdown {
    position: absolute;
    top: 100%;
    left: 0;
    right: 0;
    background: white;
    border: 1px solid #ccc;
    // max-height: 200px;
    overflow-y: auto;
    z-index: 100;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.search-item {
    padding: 8px;
    cursor: pointer;
    border-bottom: 1px solid #eee;
    display: flex;
    justify-content: space-between;
}
.search-item:hover {
    background-color: #f0f0f0;
}
.item-name { font-weight: bold; }
.item-code { color: #666; font-size: 0.9em; }

.div-table {
    display: flex;
    flex-direction: column;
    width: 100%;
    // border: 1px solid #ddd;
}
.div-table-header {
    display: flex;
    background-color: #f2f2f2;
    font-weight: bold;
    position: sticky;
    top: 0;
    z-index: 1;
    border: 1px solid #ddd;
}
.div-table-row {
    display: flex;
    border: 1px solid #ddd;
    background-color: white;
}
.div-cell {
    padding: 0.4rem;
    border-right: 1px solid #ddd;
    display: flex;
    align-items: center;
}
.div-cell:last-child {
    border-right: none;
}
.col-code { flex: 0 0 120px; }
.col-name { flex: 1; }
.col-qty { flex: 0 0 100px; justify-content: flex-end; }
.col-action { flex: 0 0 80px; justify-content: center; }

.qty-input, .price-input {
    width: 80px;
    text-align: right;
    padding: 4px;
    &::-webkit-outer-spin-button,
    &::-webkit-inner-spin-button {
        -webkit-appearance: none;
        margin: 0;
    }
    -moz-appearance: textfield;
}
.btn-remove {
    background: none; border: none; color: red; font-size: 1.2rem; cursor: pointer;
}
.row-items {
    flex: 1;
    overflow-y: auto;
    margin-top: 1rem;
}
</style>
