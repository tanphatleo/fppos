<template>
  <div class="modal-overlay" @mousedown.self="$emit('close')">
    <div class="modal-content">
      <div class="modal-header">
        <h3>Chỉnh sửa đổi hàng</h3>
        <button @click="$emit('close')" class="close-btn">&times;</button>
      </div>

      <div class="modal-body">
        <div class="table-header">
          <div class="col-deduct">Hàng trả (Deduction)</div>
          <div class="col-replace">Hàng đổi (Replacement)</div>
          <div class="col-description">Mô tả</div>
          <div class="col-qty">Số lượng</div>
          <div class="col-action"></div>
        </div>

        <div v-for="(item, index) in items" :key="index" class="table-row">
          <!-- Deduction Input -->
          <div class="col-deduct search-container">
            <input
              type="text"
              v-model="item.deductSearchTerm"
              @focus="handleFocus($event, item, 'deduction')"
              @blur="onBlur(item, 'deduction')"
              @input="onInputChange(item, 'deduction')"
              placeholder="Tìm hàng trả"
              class="search-input"
            />
          </div>
          <!-- Replacement Input -->
          <div class="col-replace search-container">
            <input
              type="text"
              v-model="item.replaceSearchTerm"
              @focus="handleFocus($event, item, 'replace')"
              @blur="onBlur(item, 'replace')"
              @input="onInputChange(item, 'replace')"
              placeholder="Tìm hàng đổi"
              class="search-input"
            />
          </div>
          <!-- Description Input -->
          <div class="col-description">
            <input type="text" v-model="item.description" placeholder="Mô tả" class="description-input" />
          </div>
          <!-- Quantity Input -->
          <div class="col-qty">
            <input type="number" v-model.number="item.quantity" class="qty-input" min="1" @change="handleQuantityChange(item)" />
          </div>
          <div class="col-action">
            <button @click="removeItem(index)" class="btn-remove">&times;</button>
          </div>
        </div>
        <button @click="addItem" class="btn-add-row">+ Thêm dòng</button>
      </div>
      <div class="modal-footer">
        <button @click="$emit('close')" class="btn btn-secondary">Hủy</button>
          <button @click="saveChanges" class="btn btn-primary new-button" :disabled="items.length === 0 || items.every(item => !item.deduction_product_code || !item.replace_product_code || item.quantity <= 0)">Lưu</button>
      </div>
    </div>
  </div>
  <Teleport to="body">
    <div v-if="activeDropdown.item && currentDropdownList.length" class="dropdown-teleport" :style="dropdownStyle">
      <div
        v-for="product in currentDropdownList"
        :key="product.id"
        class="dropdown-item"
        @mousedown.prevent="selectProduct(activeDropdown.item, product, activeDropdown.type)"
      >
        {{ product.name }} ({{ product.code }})
      </div>
    </div>
  </Teleport>
</template>

<script>
import { ref, computed, watch } from 'vue';

export default {
  name: 'EditChangesItems',
  props: {
    initialItems: {
      type: Array,
      default: () => []
    },
    products: {
      type: Array,
      default: () => []
    }
  },
  emits: ['close', 'save'],
  setup(props, { emit }) {
    const getInitialSearchTerm = (code) => {
      if (!code) return '';
      const p = props.products.find(prod => prod.code === code);
      return p ? `${p.name} - ${p.code}` : code;
    };

    const items = ref(props.initialItems.map(i => ({
      ...i,
      deductSearchTerm: getInitialSearchTerm(i.deduction_product_code),
      replaceSearchTerm: getInitialSearchTerm(i.replace_product_code),
      description: i.description || '',
      showDeductDropdown: false,
      showReplaceDropdown: false,
    })));

    const activeDropdown = ref({ item: null, type: null });
    const dropdownStyle = ref({});

    const normalProducts = computed(() => 
      props.products.filter(p => p.product_type === 'normal')
    );
    
    

    const filteredProducts = (term) => {
      if (!term) return normalProducts.value.slice(0, 10);
      const lowerTerm = term.toLowerCase();
      return normalProducts.value.filter(p => {
        const name = p.name.toLowerCase();
        const code = p.code.toLowerCase();
        const combined = `${name} - ${code}`;
        return name.includes(lowerTerm) || code.includes(lowerTerm) || combined.includes(lowerTerm);
      }).slice(0, 10);
    };

    const currentDropdownList = computed(() => {
      const { item, type } = activeDropdown.value;
      if (!item) return [];
      const term = type === 'deduction' ? item.deductSearchTerm : item.replaceSearchTerm;
      return filteredProducts(term);
    });

    const handleFocus = (event, item, type) => {
      const rect = event.target.getBoundingClientRect();
      dropdownStyle.value = {
        top: `${rect.bottom}px`,
        left: `${rect.left}px`,
        width: `${rect.width}px`
      };
      activeDropdown.value = { item, type };
    };

    const onInputChange = (item, type) => {
      if (type === 'deduction') {
        item.deduction_product_code = '';
      } else {
        item.replace_product_code = '';
      }
    };

    const onBlur = (item, type) => {
      setTimeout(() => {
        if (activeDropdown.value.item === item && activeDropdown.value.type === type) {
          activeDropdown.value = { item: null, type: null };
        }
        if (type === 'deduction') item.showDeductDropdown = false;
        else item.showReplaceDropdown = false;
      }, 200);
    };

    const selectProduct = (item, product, type) => {
      if (type === 'deduction') {
        item.deduction_product_code = product.code;
        item.deductSearchTerm = `${product.name} - ${product.code}`;
        item.showDeductDropdown = false;
        activeDropdown.value = { item: null, type: null };
      } else {
        item.replace_product_code = product.code;
        item.replaceSearchTerm = `${product.name} - ${product.code}`;
        item.showReplaceDropdown = false;
        activeDropdown.value = { item: null, type: null };
      }
    };

    const addItem = () => {
      items.value.push({
        deduction_product_code: '',
        replace_product_code: '',
        quantity: 1,
        description: '',
        deductSearchTerm: '',
        replaceSearchTerm: '',
        showDeductDropdown: false,
        showReplaceDropdown: false,
      });
    };

    const removeItem = (index) => {
      items.value.splice(index, 1);
    };

    const handleQuantityChange = (item) => {
      const qty = Number(item.quantity);
      if (isNaN(qty) || qty < 1) {
        item.quantity = 1;
      }
    };

    const saveChanges = () => {
      const validItems = items.value
        .filter(item => 
          (item.deduction_product_code || item.replace_product_code) && item.quantity > 0
        )
        .map(item => ({ // clean up internal state properties
          deduction_product_code: item.deduction_product_code,
          replace_product_code: item.replace_product_code,
          quantity: item.quantity,
          description: item.description || ''
        }));
      emit('save', validItems);
    };

    return {
      items,
      filteredProducts,
      activeDropdown,
      dropdownStyle,
      currentDropdownList,
      handleFocus,
      onInputChange,
      onBlur,
      selectProduct,
      addItem,
      removeItem,
      saveChanges,
      handleQuantityChange
    };
  }
};
</script>

<style scoped lang="scss">

.new-button {
  &:disabled {
    background-color: #a0c4ff !important;
    border-color: #a0c4ff !important;
    cursor: not-allowed !important;
  }
}
/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0; left: 0;
  width: 100vw; height: 100vh;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.modal-content {
  background: white;
  padding: 1.5rem;
  border-radius: 5px;
  width: 80%;
  max-width: 900px;
  display: flex;
  flex-direction: column;
}
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
  padding-bottom: 1rem;
  margin-bottom: 1rem;
}
.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
}
.modal-body {
  max-height: 60vh;
  overflow-y: auto;
}
.modal-footer {
  border-top: 1px solid #eee;
  padding-top: 1rem;
  margin-top: 1rem;
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}

/* Table styles */
.table-header, .table-row {
  display: flex;
  gap: 1rem;
  align-items: center;
  padding: 0.5rem 0;
  position: relative; /* For dropdown positioning */
}
.table-header {
  font-weight: bold;
  border-bottom: 1px solid #ccc;
}
.col-deduct, .col-replace { flex: 3; }
.col-qty { flex: 1; }
.col-description { flex: 2; } /* Added description column */
.col-action { flex: 0.5; text-align: center; }

.search-container {
  position: relative;
  width: 100%;
}
.search-input {
  width: 100%;
  padding: 6px;
  border: 1px solid #ccc;
  border-radius: 3px;
  box-sizing: border-box;
}

.description-input {
  width: 100%;
  padding: 6px;
  border: 1px solid #ccc;
  border-radius: 3px;
  box-sizing: border-box;
}
.dropdown {
  position: absolute;
  display: flex;
  flex-direction: column;
  top: 100%;
  left: 0;
  right: 0;
  background: white;
  border: 1px solid #ccc;
  max-height: 200px;
  overflow-y: auto;
  z-index: 1001;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.dropdown-teleport {
  position: fixed;
  background: white;
  border: 1px solid #ccc;
  max-height: 200px;
  overflow-y: auto;
  z-index: 9999;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  border-radius: 0 0 4px 4px;
}
.dropdown-item {
  padding: 8px;
  cursor: pointer;
}
.dropdown-item:hover {
  background-color: #f0f0f0;
}

.qty-input {
  width: 100%;
  padding: 6px;
  border: 1px solid #ccc;
  border-radius: 3px;
}
.btn-remove {
  color: red;
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
}
.btn-add-row {
  margin-top: 1rem;
  width: 100%;
  padding: 0.5rem;
  border: 1px dashed #ccc;
  background: #f9f9f9;
  cursor: pointer;
}

/* Reusing button styles from parent */
.btn {
  padding: 8px 16px;
  border-radius: 3px;
  cursor: pointer;
  font-weight: 500;
  border: 1px solid transparent;
}
.btn-primary {
  background: #0070F4;
  color: white;
}
.btn-secondary {
  background: #6c757d;
  color: white;
}
</style>