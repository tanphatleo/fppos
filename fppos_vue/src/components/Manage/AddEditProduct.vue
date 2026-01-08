<template>
  <div class="add-edit-product-modal" @click.self="$emit('close')">
    <div class="add-edit-product-content">
      
        
        <div class="standard-fields">
            <div class="header-holder">
                <h2>{{ product.id ? 'Sửa sản phẩm' : 'Tạo mới sản phẩm' }}
                    
                </h2>
                <button class="modal-close-btn" @click="$emit('close')" aria-label="Đóng">×</button>
            </div>
            
            <v-text-field v-model="product.name" label="Tên"  style="width: 30rem;"/>
            <v-text-field v-model="product.code" label="Mã" />
            <v-text-field v-model="product.price" label="Giá" type="number" />
            <v-select v-model="product.product_type" :items="['normal', 'combo']" label="Loại" :disabled="!!product.id" />
            <v-select
                v-model="product.product_group"
                :items="productGroups.filter(g => g.is_active)"
                item-title="name"
                item-value="id"
                label="Nhóm sản phẩm"
            />
            <v-switch v-model="product.is_active" label="Kích hoạt" />
            <div class="actions">
                <v-btn color="primary" @click="saveProduct">Lưu</v-btn>
                <v-btn @click="$emit('close')">Hủy</v-btn>
            </div>
        </div>

        <!-- Combo products selector -->
        <div v-if="product.product_type === 'combo'" class="combo-area">
            <label style="margin-bottom: 0.5rem; font-weight: bold;">Chọn sản phẩm thành phần và số lượng</label>
            <div v-for="(item, idx) in comboItems" :key="idx" style="display: flex; align-items: center;">
                <v-select
                v-model="item.code"
                :items="normalProducts"
                :item-title="item => `${item.name} (${item.code})`"
                item-value="code"
                label="Sản phẩm"
                style="width: 40rem; height: auto; font-size: 1rem;"
                />
                <v-text-field
                    v-model.number="item.quantity"
                    type="number"
                    min="1"
                    label="Số lượng"
                    style="width: 5rem;"
                />
                <div>
                    <v-btn icon density="compact" size="small" @click="removeComboItem(idx)" color="error" class="btn-edit btn-edit-top"><span style="font-weight:bold; display: inline-block; font-size: 1.1rem;">×</span></v-btn>
                </div>
            </div>
            <v-btn color="secondary" @click="addComboItem">Thêm sản phẩm</v-btn>
        </div>
    
      
      
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue';
import axios from 'axios';

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

const normalProducts = computed(() => props.products.filter(p => p.product_type === 'normal'));

watch(() => props.productData, (newVal) => {
  if (newVal && Object.keys(newVal).length > 0 && newVal.id) {
    product.value = { ...newVal };

    // If editing a combo, load combo items from package_details
    console.log("Loaded product package_details:", product);
    if (product.value.product_type === 'combo' && Array.isArray(product.value.package_details)) {
      comboItems.value = product.value.package_details.map(item => ({
        code: item.code,
        name: item.name,
        quantity: item.quantity
      }));
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
  comboItems.value.push({ product: null, quantity: 1 });
}
function removeComboItem(idx) {
  comboItems.value.splice(idx, 1);
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
  if (product.value.id) {
    await axios.put(`/products/${product.value.id}/`, payload);
    // close modal after save
    
    emit('saved');
    emit('close');
  } else {
    
    await axios.post('/products/', payload);
    emit('saved');
    emit('close');
  }
}
</script>

<style scoped>
.add-edit-product-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0,0,0,0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.header-holder{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
}

.add-edit-product-content {
  background: #fff;
  padding: 2rem;
  border-radius: 1rem;
  min-width: 350px;
  max-width: 90vw;
  box-shadow: 0 2px 16px rgba(0,0,0,0.2);
  display: flex;
  flex-direction: row;
  gap: 1rem;
}

.modal-close-btn {
  background: transparent;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}
.actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
}

.btn-edit {
  display: flex;
  align-items: center;
  justify-content: center;
}

.combo-area {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-left: 1rem;
}
</style>



