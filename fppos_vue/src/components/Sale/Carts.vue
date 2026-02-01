<template>
  <div class="cart-products-component">
    <div class="welcome-page no-select" v-if="!cartItems.length && !isRefund">
      <p>Chưa có sản phẩm nào trong giỏ hàng</p>
    </div>

    <div class="carts-list no-select" :class="{ 'show-duplicate-item': displayOptions.duplicateCartItem }">
      
      <div 
        v-for="(item, index) in cartItems" 
        :key="item.uuid" 
        class="carts active" 
        :class="{ 'carts-item-sortable': displayOptions.usingSortProduct }"
      >
        <div class="carts-item">
          <div class="carts-left">
            <div class="cell-order" v-if="displayOptions.numberOrder">{{ index + 1 }}</div>
            <div class="cell-actions carts-actions">
              <button class="btn-icon btn-icon-default" @click="removeProduct(item)" title="Xóa hàng hóa">
                <i class="far fa-trash-alt"></i>
              </button>
            </div>
          </div>

          <div class="carts-content">
            <div class="carts-container">
              <div class="carts-content-info">
                <div class="carts-content-top">
                  <div class="cell-code" v-if="displayOptions.code">{{ item.code }}</div>
                  <div class="cell-info">
                    <div class="info-content">
                      <span >{{ item.name }}</span>
                    </div>
                  </div>
                  <div class="cell-units" v-if="item.units && item.units.length > 1">
                    <select v-model="item.selectedUnit" @change="unitChanged(item)" class="form-control">
                      <option v-for="u in item.units" :key="u.id" :value="u.id">{{ u.name }}</option>
                    </select>
                  </div>
                </div>

                <div class="carts-content-bottom">
                  <div class="cell-quantity">
                    <div class="quantity quantity-sm">
                      <button type="button" class="btn-icon btn-icon-bg-default down" @click="updateQuantity(item, -1)">
                        <i class="fas fa-minus"></i>
                      </button>
                      <input 
                        type="number" 
                        v-model.number="item.quantity" 
                        class="form-control form-control-sm input-white"
                        @change="onQuantityChange(item)"
                      />
                      <button type="button" class="btn-icon btn-icon-bg-default up" @click="updateQuantity(item, 1)">
                        <i class="fas fa-plus"></i>
                      </button>
                    </div>
                  </div>

                  <div class="cell-change-price" v-if="displayOptions.price">
                    <button class="form-control form-control-sm text-right no-select" >
                      {{ formatPrice(item.price) }}
                    </button>
                    <span class="sub-label label-discount" v-if="item.discount > 0">
                      - {{ formatPrice(item.discount) }}
                    </span>
                  </div>

                  <div class="cell-change-price" v-if="displayOptions.total">
                    <div class="cell-total text-right">
                      <span class="cart-price-new">{{ formatPrice(item.quantity * item.price) }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="carts-secondary cell-secondary" v-if="item.hasNote || item.note">
              <div class="carts-note">
                <textarea 
                  class="form-control form-control-custom" 
                  v-model="item.note" 
                  placeholder="Ghi chú..." 
                  rows="1"
                  @change="emit('update-invoice', props.focus_invoice)"
                ></textarea>
              </div>
            </div>
          </div>

          <div class="cell-actions carts-actions">
            <!-- <button class="btn-icon btn-icon-default" @click="duplicateCartItem(item)" v-if="displayOptions.duplicateCartItem">
              <i class="fas fa-plus"></i>
            </button> -->
            <button class="btn-icon btn-icon-default btn-more" @click="togglePopover(item)">
              <i class="fas fa-ellipsis-v"></i>
            </button>
            
            <div 
              class="popover-menu" 
              v-if="item.isOpenPopover" 
              v-click-outside="() => closePopover(item)"
              >
              <a @click="removeProduct(item)"><i class="far fa-trash-alt"></i> Xóa hàng hóa</a>
              <a @click="toggleNote(item)"><i class="fa-regular fa-note-sticky"></i> Ghi chú</a>
              <!-- <a @click="viewDetail(item)"><i class="far fa-info-circle"></i> Xem chi tiết</a> -->
            </div>
          </div>
        </div>

        <div class="carts-item row-serial-child" v-if="item.isSerial">
          <div class="carts-left"></div> <div class="carts-content">
             <div class="carts-container">
                <div class="cell-name">
                   <div class="tags-input-wrapper">
                      <span v-for="(serial, idx) in item.serials" :key="idx" class="tag">
                        {{ serial }} <span @click="removeSerial(item, idx)">×</span>
                      </span>
                      <input 
                        type="text" 
                        placeholder="Nhập Serial/Imei" 
                        @keydown.enter="addSerial(item, $event)"
                      />
                   </div>
                </div>
             </div>
          </div>
        </div>

      </div>
    </div>

    <div class="carts-footer no-select">
      <div class="carts-footer-left" v-if="!displayOptions.isOnlineMode">
        <textarea
          class="form-control form-control-custom note-cart"
          v-model="props.focus_invoice.note"
          placeholder="Ghi chú đơn hàng"
          maxlength="4000"
          tabindex="1500"
          style="height: 43px;"
        ></textarea>
      </div>
      <div class="cart-footer-right" v-if="displayOptions.saleScreenMode === 2 && !isRefund && !displayOptions.isWarrantyCart && !displayOptions.isOnlineMode">
        <div class="form-group-inline form-group-row form-group-row-sm">
          <label class="col-form-label no-select">Tổng tiền hàng</label>
          <div class="col-form-wrap d-flex">
            <span class="text-bg-default" v-if="displayOptions.useTotalQuantity">{{ props.focus_invoice.totalItems }}</span>
          </div>
        </div>
        <div class="form-group-inline form-group-row-sm form-group-price">
          <div class="form-control-plaintext text-right font-size-medium has-currency font-bold ">
            {{ formatPrice(props.focus_invoice.total) }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue';
// --- Cart Note ---
const cartNote = ref("");

// --- Cart Total and Quantity ---


// --- Display Options Extension (for demo) ---
const displayOptions = reactive({
  numberOrder: true,
  code: true,
  price: true,
  total: true,
  duplicateCartItem: true,
  // showCartItemNote: false,
  usingSortProduct: false
});
// Add these to displayOptions or replace with real logic as needed
if (!('isOnlineMode' in displayOptions)) displayOptions.isOnlineMode = false;
if (!('saleScreenMode' in displayOptions)) displayOptions.saleScreenMode = 2;
if (!('isWarrantyCart' in displayOptions)) displayOptions.isWarrantyCart = false;
if (!('useTotalQuantity' in displayOptions)) displayOptions.useTotalQuantity = true;

// --- Props & Emits ---
const emit = defineEmits(['update-invoice']);

const props = defineProps({
  focus_invoice: {
    type: Object,
    required: true,
    // In a real app, default data usually comes from the parent, 
    // but we keep the mock here for standalone visualization.
    default: () => ({
          id: 1,
          total: 40000,
          totalItems: 1,
          discount: 0,
          finalTotal: 40000,
          items: [
            {
              uuid: '1',
              code: 'FP0011',
              name: 'Ức gà Teriyaki 150g',
              price: 40000,
              quantity: 1,
              onHand: 6,
              ordered: 45,
              hasNote: false,
              units: [{id: 1, name: 'Gói'}],
              productType: 2,
              actualProducts: [
                {
                  code: 'FP0011',
                  quantity: 1
                }
              ],
              isSerial: false,
              note: '',
              isOpenPopover: false
            }
          ]
        })
  }

});

// --- Mock Data (Replace with your Store/Props) ---

const cartItems = computed(() => props.focus_invoice.items || []);



const isRefund = ref(false);

// --- Methods ---

const update_total_and_quantity = () => {
  let total = 0;
  let totalItems = 0;
  cartItems.value.forEach(item => {
    total += item.price * item.quantity;
    totalItems += item.quantity;
  });
  props.focus_invoice.total = total;
  props.focus_invoice.finalTotal = total - props.focus_invoice.discount;
  props.focus_invoice.totalItems = totalItems;
  emit('update-invoice', props.focus_invoice); // Notify parent of total/quantity change
};

const vClickOutside = {
  mounted(el, binding) {
    el.clickOutsideEvent = (event) => {
      // Check if the click was outside the el and its children
      if (!(el === event.target || el.contains(event.target))) {
        binding.value(event);
      }
    };
    
    // CRITICAL FIX: Wait 0ms to let the current click event finish 
    // before starting to listen for outside clicks.
    setTimeout(() => {
      document.addEventListener('click', el.clickOutsideEvent);
    }, 0);
  },
  unmounted(el) {
    document.removeEventListener('click', el.clickOutsideEvent);
  },
};

const removeProduct = (item) => {
  const index = props.focus_invoice.items.indexOf(item);
  if (index > -1) {
    props.focus_invoice.items.splice(index, 1);
    update_total_and_quantity();
  }
};

const formatPrice = (val) => {
  return new Intl.NumberFormat('vi-VN').format(val);
};

const updateQuantity = (item, delta) => {
  // 1. Ensure we are working with a Number, not a String
  console.log('Button clicked', delta); // Check browser console
  const currentQty = Number(item.quantity) || 0;
  const newVal = currentQty + delta;

  // 2. Only update if valid
  if (newVal > 0) {
    item.quantity = newVal;
    
    // update the item quantity in the cart

    // 3. Trigger the emit you defined in defineEmits
    // This tells the parent component that data changed
    update_total_and_quantity();
  }

  // 
};

const onQuantityChange = (item) => {
  // 1. Force conversion to number to prevent future string issues
  let val = Number(item.quantity);
  
  // 2. Validation logic
  if (isNaN(val) || val < 1) {
    val = 1;
  }
  
  item.quantity = val;
  
  update_total_and_quantity();
};


const unitChanged = (item) => {
  console.log('Unit changed', item.selectedUnit);
};

// Updated togglePopover
const togglePopover = (item) => {
  // 1. Close ALL other popovers first
  props.focus_invoice.items.forEach(i => {
    if (i !== item) i.isOpenPopover = false;
  });

  // 2. Toggle the current one
  item.isOpenPopover = !item.isOpenPopover;
};

const closePopover = (item) => {
  if (item.isOpenPopover) {
    item.isOpenPopover = false;
  }
};

const toggleNote = (item) => {
  // displayOptions.showCartItemNote = !displayOptions.showCartItemNote;
  if (item.hasNote) {
    item.note = '';
  }

  item.hasNote = !item.hasNote;
  // item.note = item.note || '';
  // item.isOpenPopover = false;
  closePopover(item);
  emit('update-invoice', props.focus_invoice); // Notify parent of change
};

// Serial Logic
const addSerial = (item, event) => {
  const val = event.target.value.trim();
  if (val) {
    if (!item.serials) item.serials = [];
    item.serials.push(val);
    event.target.value = '';
  }
};

const removeSerial = (item, index) => {
  item.serials.splice(index, 1);
};

</script>

<style scoped lang="scss">
$border-color: #e1e1e1;
$primary-color: #0090da;
.no-select {
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;
}

.cart-products-component {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.welcome-page {
  padding: 20px;
  text-align: center;
  color: #999;
}

.carts-list {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;

  /* Hide scrollbar for Chrome, Safari and Opera */
  &::-webkit-scrollbar {
    display: none;
  }

  /* Hide scrollbar for IE, Edge and Firefox */
  -ms-overflow-style: none;  /* IE and Edge */
  scrollbar-width: none;  /* Firefox */
}

.font-bold {
  font-weight: bold;
}

.input-white {
  background-color: white !important;
  color: black !important;
}

.carts {
  border-bottom: 1px solid $border-color;
  // background: #fff;
  
  &.active {
    // background-color: #f0f9ff; // Active highlight
  }
}

.carts-item {
  display: flex;
  padding: 0.5rem 0rem 0.5rem 0rem;
  border-radius: 4px;
  margin-bottom: 0.3rem;
}

.carts-item:hover {
  // border-color: rgba(0, 145, 218, 0.304);
  border: #0090da 1px solid;
  // $primary-color with 5% opacity
}

/* Left Column (Order & Delete) */
.carts-left {
  width: 40px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  border-right: 1px solid #eee;
  margin-right: 10px;
  padding-right: 5px;
}

.cell-order {
  // font-size: 12px;
  // color: #888;
  margin-bottom: 5px;
}

/* Middle Content */
.carts-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.carts-content-top {
  display: flex;
  // justify-content: space-between;
  margin-bottom: 10px;
  
  .cell-code {
    width: 7vw;
    // font-weight: bold;
    // color: #555;
    margin-right: 10px;
    font-size: 1rem;
    display: flex;
    align-items: start;
  }
  
  .info-content {
    // font-weight: 500;
    color: #333;
    
    .btn-inventory {
      color: $primary-color;
      margin-left: 5px;
      cursor: pointer;
      border: none;
      background: none;
    }
  }

  .cell-info {
    flex-grow: 6;
    display: flex;
    align-items: start;
  }
}

.carts-content-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 5px;
}

/* Quantity Stepper */
.quantity-sm {
  display: flex;
  align-items: center;
  border: 1px solid #ddd;
  border-radius: 4px;
  overflow: hidden;
  
  .btn-icon {
    width: 24px;
    height: 24px;
    border: none;
    background: #f5f5f5;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 10px;
    
    &:hover { background: #e0e0e0; }
  }
  
  input {
    width: 40px;
    text-align: center;
    border: none;
    outline: none;
    font-size: 13px;
    padding: 2px;
    /* Hide spin buttons */
    -moz-appearance: textfield;
    &::-webkit-inner-spin-button, &::-webkit-outer-spin-button { 
      -webkit-appearance: none; 
      margin: 0; 
    }
  }
}

.cell-change-price button {
  background: none;
  border: none;
  color: $primary-color;
  font-weight: bold;
  cursor: auto;
}

.cart-price-new {
  font-weight: bold;
  color: #333;
}

/* Notes Area */
.carts-note textarea {
  width: 100%;
  border: none;
  border-bottom: 1px solid #eee;
  resize: none;
  // font-size: 12px;
  padding: 1rem 0 0 0;
  outline: none;
  
  &:focus { border-bottom-color: $primary-color; }
}

/* Right Actions */
.carts-actions {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  margin-left: 10px;
  position: relative; // For popover positioning
}

.btn-icon-default {
  background: none;
  border: 1px solid transparent;
  color: #666;
  width: 28px; 
  height: 28px;
  border-radius: 4px;
  cursor: pointer;
  display: flex; 
  align-items: center; 
  justify-content: center;
  
  &:hover {
    background: #f0f0f0;
    color: #333;
  }
}

/* Popover Menu */
.popover-menu {
  position: absolute;
  right: 0;
  top: calc(100% - 2rem); // Move the menu up by 10px
  background: white;
  border: 1px solid #ddd;
  box-shadow: 0 4px 10px rgba(0,0,0,0.1);
  border-radius: 4px;
  z-index: 100;
  width: 150px;
  
  a {
    display: block;
    padding: 8px 10px;
    font-size: 13px;
    color: #333;
    cursor: pointer;
    
    &:hover { background: #f5f5f5; color: $primary-color; }
    i { margin-right: 5px; width: 15px; }
  }
}

/* Tags Input (Serial) */
.tags-input-wrapper {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  border: 1px solid #ddd;
  padding: 5px;
  border-radius: 4px;
  background: #f9f9f9;
  
  .tag {
    background: #e0e0e0;
    padding: 2px 6px;
    border-radius: 3px;
    font-size: 12px;
    display: flex;
    align-items: center;
    
    span {
      margin-left: 5px;
      cursor: pointer;
      color: #999;
      &:hover { color: red; }
    }
  }
  
  input {
    border: none;
    outline: none;
    background: transparent;
    flex: 1;
    min-width: 100px;
    font-size: 12px;
  }

  
}

.carts-footer {
    display: flex;
    flex-direction: row;
    // justify-content: space-between;
    padding: 0.5rem 1rem 0.5rem 2rem;
    border-top: 1px solid $border-color;
    // background: #fafafa;

      .carts-footer-left {
        // flex: 4;
        width: 70%;
        padding-right: 2rem;
        display: flex;
        .note-cart {
        width:100%;
        height: 100%;
        min-height: 40px;
        border: 1px solid #e1e1e1;
        border-radius: 6px;
        padding: 10px 12px;
        font-size: 15px;
        background: #fafbfc;
        resize: none;
        box-sizing: border-box;
        // flex: 1 1 auto;
      }
    }

    .cart-footer-right {
      flex: 1;
      display: flex;
      align-items: center;
      justify-content: space-between;

      .form-group-row {
        margin-right: 15px;
        display: flex;
        flex-direction: row;
        flex: 1;
        justify-content: space-between;
        padding-right: 2em;
      }

      .form-group-price {
        .form-control-plaintext {
          font-size: 18px;
        }
      }
    }
  }
</style>