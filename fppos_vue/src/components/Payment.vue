<template>
  <div v-if="visible" class="modal-overlay">
    <div class="modal-container">

      <div class="modal-body">
        
        <div class="top-controls">
          
            <div class="label-group">
                <div class="control-group">
                    <select v-model="selectedSeller" class="form-select custom-select">
                    <option v-for="s in sellers" :key="s.id" :value="s.id">{{ s.name }}</option>
                    </select>

                    <select v-model="selectedChannel" class="form-select custom-select">
                    <option v-for="c in channels" :key="c.id" :value="c.id">{{ c.name }}</option>
                    </select>

                </div>
            
                <div class="date-group">
                    <input type="date" v-model="purchaseDate" class="form-input date-input " @click="openDatePicker($event)" ref="dateInputRef" />
                    <input type="time" v-model="purchaseTime" class="form-input time-input" @click="openTimePicker($event)" ref="timeInputRef" />
                </div>
            </div>
            

          <div class="close-btn-group">
            <button @click="close" class="close-btn">x</button>
          </div>
          
        </div>

        <div class="customer-info">
          <span class="customer-name font-bold">{{ props.cartData?.customer?.name || 'Khách lẻ' }}</span>
          <div v-if="props.cartData?.customer" class="customer-stats">
            <span class="tag debt" v-if="props.cartData.customer.debt">
              Nợ: {{ formatCurrency(props.cartData.customer.debt) }}
            </span>
            <span class="tag points" v-if="props.cartData.customer.points">
              Điểm: {{ props.cartData.customer.points }}
            </span>
          </div>
        </div>

        <div class="payment-details">
          
          <div class="row">
            <span class="row-label">Tổng tiền hàng</span>
            <span class="side-info"></span>
            <div class="value-amt">{{ formatCurrency(totalAmount) }}</div>
          </div>

          <div class="row" >
            <span class="row-label">Giảm giá</span>
            <span class="side-info"></span>
            <div style="position:relative;">
                <button class="value-amt" @mousedown.stop="toggleDiscountPopover">0</button>
                <div class="popover-content" v-show="openDiscount" ref="popoverRef">
                    
                    <div>Giảm giá</div>
                    <input type="number" class="value-input font-bold text-right" />
                    <button :class="{ active: chosen_discount_method === 'VND' }" @click="chosen_discount_method = 'VND'">VND</button>
                    <button :class="{ active: chosen_discount_method === '%' }" @click="chosen_discount_method = '%'">%</button>
                </div>
            </div>
            
          </div>

          <div class="row">
            <span class="row-label">Thu khác</span>
            <span class="side-info"></span>
            <div style="position:relative;">
                <button class="value-amt" @click="surchargesOpen=true">0</button>
            </div>
            
          </div>

          <hr class="divider">

          <div class="row highlight">
            <label class="font-bold">Khách cần trả</label>
            <div class="value font-bold text-primary">{{ formatCurrency(finalTotal) }}</div>
          </div>

          <div class="row payment-input-row">
            <label class="font-bold">Khách thanh toán</label>
            <input 
              type="number" 
              v-model="amountPaidByCustomer" 
              class="value-input font-bold text-right customer-payment-input"
            />
          </div>

          <div class="row methods-row">
            <div class="radio-group">
              <label v-for="method in paymentMethods" :key="method.value" class="radio-label">
                <input 
                  type="radio" 
                  :value="method.value" 
                  v-model="paymentMethod" 
                />
                {{ method.label }}
              </label>
            </div>
            <button class="btn-icon" title="Thanh toán kết hợp">...</button>
          </div>

          <div class="row" v-if="changeDue > 0">
             <label>Tiền thừa trả khách</label>
             <div class="value">{{ formatCurrency(changeDue) }}</div>
          </div>
          <div class="row" v-else-if="changeDue < 0">
             <label class="text-danger">Khách còn thiếu</label>
             <div class="value text-danger">{{ formatCurrency(Math.abs(changeDue)) }}</div>
          </div>

        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-primary" @click="handlePayment">Thanh toán</button>
      </div>

    </div>
  </div>

  <Surcharge 
    v-if="true" 
    :visible="surchargesOpen" 
    :defaultSurcharges="props.defaultSurcharges"
    @close="surchargesOpen = false" 
    @save=""
    />

</template>

<script setup>
import { ref, computed, onMounted, watch, onBeforeUnmount } from 'vue';
import Surcharge from './Surcharge.vue';

// --- Props & Emits ---
const props = defineProps({
  visible: { type: Boolean, default: false },
  cartData: { type: Object, required: true }, // Expects { total: number, customer: object },
  channels: { type: Array, default: () => [] },
  defaultSurcharges: { type: Array, default: () => [] }
});

const emit = defineEmits(['close', 'complete-payment']);


function toggleDiscountPopover() {
    openDiscount.value = !openDiscount.value;
}

const surchargesOpen = ref(false);
// --- State ---
// Dropdown Data (Mocking the options from your HTML)
const sellers = ref([
  { id: 36934, name: 'Fitpack Hà Nội' },
  { id: 39480, name: 'Bán hàng HN' }
]);
const selectedSeller = ref(36934);

const channels = props.channels || [];
const selectedChannel = ref(0);

const openDiscount = ref(false);
const popoverRef = ref(null);

function handleClickOutside(event) {
  if (popoverRef.value && !popoverRef.value.contains(event.target)) {
    openDiscount.value = false;
  }
}

watch(openDiscount, (val) => {
  if (val) {
    document.addEventListener('mousedown', handleClickOutside);
  } else {
    document.removeEventListener('mousedown', handleClickOutside);
  }
});

onBeforeUnmount(() => {
  document.removeEventListener('mousedown', handleClickOutside);
});

// Date Time
const purchaseDate = ref(new Date().toISOString().substr(0, 10));
const purchaseTime = ref("18:55");

const dateInputRef = ref(null);
const timeInputRef = ref(null);

function openTimePicker(event) {
  if (timeInputRef.value) {
    if (typeof timeInputRef.value.showPicker === 'function') {
      timeInputRef.value.showPicker();
    } else {
      timeInputRef.value.focus();
      // Optionally, trigger a click event for browsers that require it
      // timeInputRef.value.click();
    }
  }
}

function openDatePicker(event) {
  // Always focus the input
  if (dateInputRef.value) {
    // Try to use showPicker if supported (Chrome, Edge, Opera)
    if (typeof dateInputRef.value.showPicker === 'function') {
      dateInputRef.value.showPicker();
    } else {
      // Fallback: focus and trigger click (for Firefox, Safari, etc.)
      dateInputRef.value.focus();
      // Optionally, trigger a click event for browsers that require it
      // (Some browsers may ignore programmatic click for security reasons)
      // dateInputRef.value.click();
    }
  }
}

// Financials
const totalAmount = ref(0); // Will load from props
const discountAmount = ref(0);
const surchargeAmount = ref(0);
const amountPaidByCustomer = ref(0); // "Khách thanh toán"

// Payment Methods
const paymentMethod = ref('cash'); // 'cash', 'card', 'transfer'
const paymentMethods = [
  { value: 'cash', label: 'Tiền mặt' },
  { value: 'transfer', label: 'Chuyển khoản' }
];

const chosen_discount_method = ref('VND');

// --- Computed Logic ---

// 1. Calculate the final amount the customer needs to pay
const finalTotal = computed(() => {
  return totalAmount.value - discountAmount.value + surchargeAmount.value;
});

// 2. Calculate "Tiền thừa" (Change due) or "Còn thiếu" (Remaining)
const changeDue = computed(() => {
  return amountPaidByCustomer.value - finalTotal.value;
});

// 3. Helper to format currency (VND)
const formatCurrency = (value) => {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(value);
};

// --- Lifecycle ---
onMounted(() => {
  // Initialize with data passed from parent
  if (props.cartData) {
    totalAmount.value = props.cartData.total || 1458000;
    amountPaidByCustomer.value = totalAmount.value; // Auto-fill full amount
  }
});

// --- Actions ---
const handlePayment = () => {
  const payload = {
    sellerId: selectedSeller.value,
    channelId: selectedChannel.value,
    date: `${purchaseDate.value} ${purchaseTime.value}`,
    paymentMethod: paymentMethod.value,
    total: finalTotal.value,
    paid: amountPaidByCustomer.value,
    customer: props.cartData?.customer
  };
  
  emit('complete-payment', payload);
};

const close = () => {
  emit('close');
};
</script>



<style scoped>
/* Basic Styles to mimic the POS layout - Replace with Tailwind if preferred */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.5); z-index: 1000;
  display: flex; justify-content: end;
}

.modal-container {
  background: white; 
  width: 20vw; 
  border-radius: 1rem; 
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  display: flex; 
  flex-direction: column;
}

/* Header */
.modal-header {
  padding: 10px 15px; 
  
  display: flex; justify-content: space-between; align-items: center;
}
/* .close-btn { background: none; border: none; color: white; font-size: 1.5rem; cursor: pointer; } */

/* Body */
.modal-body { 
    padding: 1.5rem; flex: 1; }


/* Top Controls */
.top-controls { 
    display: flex; 
    justify-content: space-between; 
    margin-bottom: 15px; 
    flex-wrap: wrap;
    border-bottom: 2px dashed #acacac;

    .control-group { 
        display: flex; 
        flex: 2    ;
        margin-bottom: 0.5rem;
    };
    
    .custom-select {
        appearance: none;
        -webkit-appearance: none;
        -moz-appearance: none;
        
        /* 2. basic box styling */
        padding: 8px 30px 8px 10px; /* Right padding creates space for the arrow */
        border: 1px solid #ccc;
        border-radius: 4px;
        background-color: white;
        cursor: pointer;
        font-size: 14px;
        
        /* 3. Add custom arrow using an encoded SVG
        /* This creates a small grey down triangle */
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="%23333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="6 9 12 15 18 9"/></svg>');
        background-repeat: no-repeat;
        background-position: right 8px center;
        background-size: 16px;
    };

    .date-group { 
        display: flex; 
        flex: 2    ;
        margin-bottom: 0.5rem;
    };

    .close-btn-group {
      display: flex;
      justify-content: flex-end;
      align-items: flex-start;
      flex: 1;
    }
    
    button.close-btn {
        color: black;
        background-color: #f4f4f4;
        /* width: 100px; */
        /* flex: 1; */
        padding: 0.5rem 0.5rem 0.5rem 0.5rem;
        border-radius: 0.5rem;
        margin-bottom: 3px;
    }
    button.close-btn:hover {
        background-color: #b8b8b8;
    }
}
/* no arrow */
input.customer-payment-input::-webkit-outer-spin-button,
input.customer-payment-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
input.customer-payment-input {
    border-top: none;
    border-left: none;
    border-right: none;
    width: 8rem;
    font-size: 1rem;
}

.form-select, .form-input { 
    padding: 1px; 
    border: 0px solid #ccc; 
    border-radius: 3px; 
    margin-right: 3px; }
.date-input{
    width: 6.5rem;
}
/* Payment Details Grid */
.payment-details { display: flex; flex-direction: column; gap: 10px; }
.row { 
    display: flex; justify-content: space-between; align-items: center; 
    .value-amt {
        font-weight: bold;
        font-size: 1.1rem;
        width: 8rem;
        display: flex;
        justify-content: flex-end;
    }
    button.value-amt {
      border-bottom: 1px solid #ddd;
      position: relative;
    }

    .popover-content {
      position: absolute;
      top: 0;
      right: 100%;
      width: 20rem;
      margin-right: 10px;
      background: #fff;
      border: 1px solid #ddd;
      box-shadow: 0 5px 8px rgba(0,0,0,0.5);
      padding: 10px;
      min-width: 120px;
      z-index: 10000;
      border-radius: 4px;
      /* display: block; */
      display: flex;
      flex-direction: row;

      div {
        margin-right: 8px;
        display: flex;
        align-items: center;
      }

      input {
        border-top: none;
        border-left: none;
        border-right: none;
      }

      input::-webkit-outer-spin-button,
        input::-webkit-inner-spin-button {
        -webkit-appearance: none;
        margin: 0;
        }
        input[type="number"] {
        -moz-appearance: textfield;
        }

      button {
        margin-left: 5px;
        padding: 3px 8px;
        border: 1px solid #ccc;
        border-radius: 3px;
        background: #f0f0f0;
        cursor: pointer;
      }

      button.active {
        background: #007bff !important;
        color: #fff;
        border-color: #007bff;
        }


    }
}
.value-input { 
  text-align: right; border: 1px solid #ddd; padding: 5px; width: 120px;
}
.divider { border: 0; border-top: 1px dashed #ccc; margin: 10px 0; }
.text-primary { color: #007bff; font-size: 1.2rem; }
.text-danger { color: #dc3545; }
.font-bold { font-weight: bold; }
.text-right { text-align: right; }

/* Methods */
.methods-row { justify-content: space-between; }
.radio-group { display: flex; gap: 15px; }
.radio-label { display: flex; align-items: center; gap: 5px; cursor: pointer; }

/* Footer */
.modal-footer {
    border-radius: 1rem;
    border-top: 1px solid #eee; background: #f9f9f9;
    display: flex; gap: 10px;
    padding: 0.1rem;
    margin-bottom: 1rem;
    margin-right: 1rem;
    margin-left: 1rem;

  button {
    flex: 1;
    padding: 0.8rem;
    border-radius: 0.6rem;
  }
}
.note-input { flex: 1; border: 1px solid #ccc; padding: 5px; resize: none; }
.btn-primary {
  background: #007bff; color: white; border: none; 
  padding: 0 30px; font-size: 1.1rem; cursor: pointer; border-radius: 4px;
}
.btn-primary:hover { background: #0069d9; }


</style>