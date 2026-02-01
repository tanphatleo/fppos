<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="product-window" @click.stop :style="{ width: product.product_type === 'combo' ? '60rem' : '30rem' }">
      <div class="window-header">
        <span class="window-title">
          <span class="no-select">{{ product.id ? 'Sửa sản phẩm' : 'Tạo mới sản phẩm' }}</span>
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
            <div class="form-layout">
              <div class="col-left">
                <div class="form-group">
                  <label>Tên</label>
                  <input type="text" v-model="product.name" />
                </div>
                <div class="form-group">
                  <label>Mã</label>
                  <input type="text" v-model="product.code" />
                </div>
                <div class="form-group">
                  <label>Giá</label>
                  <input type="text" v-model="priceDisplay" style="text-align: right;" @focus="selectAll" @beforeinput="onlyNumbers" />
                </div>
                <div class="form-group">
                  <label>Loại</label>
                  <select v-model="product.product_type" :disabled="!!product.id && !store.getters.userSuperadmin">
                    <option value="normal">Thường</option>
                    <option value="combo">Combo</option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Nhóm sản phẩm</label>
                  <select v-model="product.product_group">
                    <option v-for="group in productGroups.filter(g => g.is_active)" :key="group.id" :value="group.id">
                      {{ group.name }}
                    </option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Kích hoạt</label>
                  <input type="checkbox" v-model="product.is_active" />
                </div>
              </div>
              <div class="col-right" v-if="product.product_type === 'combo'">
                <div class="combo-area">
                  <label style="font-weight: bold; margin-bottom: 1rem; display: block;">Sản phẩm thành phần</label>
                  <div v-for="(item, idx) in comboItems" :key="idx" class="combo-item-row">
                    <div class="combo-item-input-wrapper" style="position: relative; flex: 1;">
                      <input 
                          type="text" 
                          v-model="item.searchText" 
                          @focus="handleComboFocus($event, item)"
                          @blur="handleComboBlur"
                          placeholder="Tìm sản phẩm..."
                          class="combo-product-input" 
                          style="width: 100%;"
                      />
                    </div>
                    <input type="number" v-model.number="item.quantity" min="1" class="combo-quantity-input" />
                    <button @click="removeComboItem(idx)" class="btn-remove-combo">×</button>
                  </div>
                  <button @click="addComboItem" class="btn btn-secondary" style="margin-top: 1rem;">Thêm sản phẩm</button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="window-footer">
          <button type="button" class="btn btn-outline" @click="$emit('close')">Đóng</button>
          <button type="button" class="btn btn-primary new-button" @click="saveProduct" :disabled="!product.name.trim() || (product.product_type === 'combo' && (comboItems.length === 0 || comboItems.some(item => !item.code)))">Lưu</button>
        </div>
      </div>
    </div>
  </div>
  <Teleport to="body">
    <div v-if="activeComboDropdown" class="combo-dropdown-teleport" :style="dropdownStyle">
        <div 
            v-for="p in filterProducts(activeComboDropdown.searchText)" 
            :key="p.code" 
            class="combo-dropdown-item"
            @mousedown.prevent="selectComboProduct(activeComboDropdown, p)"
        >
            {{ p.name }} ({{ p.code }})
        </div>
        <div v-if="filterProducts(activeComboDropdown.searchText).length === 0" class="combo-dropdown-item" style="color: #999; cursor: default;">
            Không tìm thấy
        </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import axios from 'axios';
import store from '@/store';

const props = defineProps({
  productData: {
    type: Object,
    default: () => ({})
  },
  productGroups: {
    type: Array,
    default: () => []
  },
  products: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['close', 'saved']);

const product = ref({
  id: null,
  productGroup: '',
  name: '',
  product_type: 'normal',
  price: 0,
  package_details: null,
  is_active: true,
  code: '',
  product_group: null,
});

// Combo items: [{ product: <id>, quantity: <number> }]
const comboItems = ref([]);

const activeComboDropdown = ref(null);
const dropdownStyle = ref({});

const priceDisplay = computed({
  get: () => {
    if (!product.value.price || product.value.price === 0) return '0';
    return new Intl.NumberFormat('vi-VN').format(product.value.price);
  },
  set: (newValue) => {
    const sanitized = newValue.replace(/\D/g, '');
    product.value.price = sanitized ? parseInt(sanitized, 10) : 0;
  }
});

const normalProducts = computed(() => props.products.filter(p => p.product_type === 'normal'));

watch(() => props.productData, (newVal) => {
  if (newVal && Object.keys(newVal).length > 0 && newVal.id) {
    product.value = { ...newVal };

    // If editing a combo, load combo items from package_details
    console.log("Loaded product package_details:", product);
    if (product.value.product_type === 'combo' && Array.isArray(product.value.package_details)) {
      comboItems.value = product.value.package_details.map(item => {
        const found = props.products.find(p => p.code === item.code);
        const name = found ? found.name : (item.name || item.code);
        return {
          code: item.code,
          name: name,
          quantity: item.quantity,
          searchText: name ? `${name} (${item.code})` : item.code
        };
      });
    } else {
      comboItems.value = [];
    }
  } else {
    product.value = {
      id: null,
      productGroup: '',
      name: '',
      product_type: 'normal',
      price: 0,
      package_details: null,
      is_active: true,
      code: '',
      product_group: null,
    };
    comboItems.value = [];
  }
}, { immediate: true, deep: true });

watch(() => product.value.product_type, (type) => {
  if (type !== 'combo') {
    comboItems.value = [];
  }
});

function addComboItem() {
  comboItems.value.push({ code: '', name: '', quantity: 1, searchText: '' });
}
function removeComboItem(idx) {
  comboItems.value.splice(idx, 1);
}

function selectAll(event) {
  event.target.select();
}

function onlyNumbers(event) {
  if (event.data && !/^\d+$/.test(event.data)) {
    event.preventDefault();
  }
}

function filterProducts(text) {
  let filtered = normalProducts.value;
  console.log("Filtering products with text:", filtered);
  const lower = text.toLowerCase();
  filtered = filtered.filter(p => p.is_active);
  // Filter by search term
  filtered = filtered.filter(p => 
    (p.name && p.name.toLowerCase().includes(lower)) || 
    (p.code && p.code.toLowerCase().includes(lower))
  );
  // Filter out products already in comboItems
  return filtered.filter(p => !comboItems.value.some(comboItem => comboItem.code === p.code));
}

function selectComboProduct(item, p) {
  item.code = p.code;
  item.name = p.name;
  item.searchText = `${p.name} (${p.code})`;
  activeComboDropdown.value = null;
}

function handleComboFocus(event, item) {
  const rect = event.target.getBoundingClientRect();
  dropdownStyle.value = {
    top: `${rect.bottom}px`,
    left: `${rect.left}px`,
    width: `${rect.width}px`
  };
  activeComboDropdown.value = item;
}

function handleComboBlur() {
  setTimeout(() => {
    activeComboDropdown.value = null;
  }, 200);
}

async function saveProduct() {
  let package_details = null;
  if (product.value.product_type === 'combo') {
    // Only keep valid combo items
    package_details = comboItems.value
      .filter(item => item.code && item.quantity > 0)
      .map(item => ({ code: item.code, quantity: item.quantity }));
  }
  const payload = {
    name: product.value.name,
    product_type: product.value.product_type,
    price: product.value.price,
    package_details,
    is_active: product.value.is_active,
    code: product.value.code,
    product_group: product.value.product_group,
  };
  try {
    if (product.value.id) {
      await axios.put(`/products/${product.value.id}/`, payload);
    } else {
      await axios.post('/products/', payload);
    }
    emit('saved');
    emit('close');
  } catch (error) {
    console.error("Error saving product:", error);
    window.alert("Lỗi khi lưu sản phẩm: " + (error.response && error.response.data ? JSON.stringify(error.response.data) : error.message));
  }
}
</script>

<style lang="scss" scoped>
$kv-primary: #0070F4;
.new-button {
  &:disabled {
    background-color: #a0c4ff !important;
    border-color: #a0c4ff !important;
    cursor: not-allowed !important;
  }
}

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

.modal-overlay {
  position: fixed;
  top: 0; left: 0;
  width: 100vw; height: 100vh;
  background: rgba(0,0,0,0.3);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.product-window {
  background: #fff;
  max-width: 95vw;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
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

.tabs-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
}

.tabs-nav li.active a {
  background: #fff;
  border-color: #ddd;
  border-bottom-color: #fff;
  color: #000;
  font-weight: 600;
  margin-bottom: -1px;
}

.tabs-nav a {
  display: block;
  padding: 10px 15px;
  text-decoration: none;
  color: #333;
  border: 1px solid transparent;
  border-bottom: none;
  border-radius: 4px 4px 0 0;
}

.window-content {
  display: flex;
  flex-direction: column;
}

.form-body {
  padding: 20px;
  background: #fff;
  max-height: 70vh;
  overflow-y: auto;
}

.form-layout {
  display: flex;
  gap: 20px;
}

.col-left, .col-right {
  flex: 1;
}

.form-group {
  display: flex;
  flex-direction: row;
  align-items: baseline;
  margin-bottom: 12px;
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

.btn {
  padding: 8px 16px;
  border-radius: 3px;
  cursor: pointer;
  font-weight: 500;
  border: 1px solid transparent;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.btn-outline {
  background: white;
  border-color: $kv-primary;
  color: $kv-primary;
}

.btn-primary {
  background: $kv-primary;
  color: white;
}

.btn-primary:hover {
  background: #0056b3;
}

.btn-secondary {
  background: #6c757d;
  color: white;
  align-self: flex-start;
}

.no-select {
  user-select: none;
}

.combo-area {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.combo-item-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.combo-product-select {
  flex: 1;
}

.combo-quantity-input {
  width: 80px;
}

.btn-remove-combo {
  background: #e74c3c;
  color: white;
  border: none;
  border-radius: 50%;
  width: 24px;
  height: 24px;
  cursor: pointer;
  font-weight: bold;
  line-height: 24px;
  text-align: center;
}

.combo-dropdown-teleport {
  position: fixed;
  background: white;
  border: 1px solid #ccc;
  max-height: 200px;
  overflow-y: auto;
  z-index: 9999;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.combo-dropdown-item {
  padding: 8px 10px;
  cursor: pointer;
  &:hover {
    background-color: #f0f0f0;
  }
}
</style>
