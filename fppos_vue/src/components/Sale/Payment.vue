<template>
  <div v-if="visible" class="modal-overlay" @mousedown.self="close">
    <div class="modal-container">

      <div class="modal-body">
        
        <div class="top-controls">
          
            <div class="label-group">
                <div class="control-group">

                    <select v-model="selectedChannel" class="form-select custom-select">
                    <option v-for="c in channels" :key="c.name" :value="c.name">{{ c.name }}</option>
                    </select>

                </div>
            
                <div class="date-group">
                    <input type="date" v-model="purchaseDate" class="form-input date-input" :disabled="!store.getters.userAdmin" @click="openDatePicker($event)" ref="dateInputRef" :max="maxDate" />
                    <input type="time" v-model="purchaseTime" class="form-input time-input" :disabled="!store.getters.userAdmin" @click="openTimePicker($event)" ref="timeInputRef" />
                </div>
            </div>

            
            

          <div class="close-btn-group">
            <button @click="close" class="close-btn">x</button>
          </div>
          
        </div>

        <div class="customer-info">
          <span class="customer-name font-bold">{{ props.cartData?.customer?.name || 'Khách lẻ' }}</span>
          <span class="customer-name"> {{ props.cartData?.customer?.address || '' }} </span>
          
          
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
                <input 
                type="text" 
                v-model="discountMethodValueDisplay" 
                @focus="selectAll"
                @keypress="onlyNumbersandPer"
                @change="checkAndUpdateDiscount"
                class="value-input font-bold text-right customer-payment-input"
                placeholder="0"
                />
            </div>
            
          </div>

          <div class="row">
            <span class="row-label">Thu khác</span>
            <span class="side-info"></span>
            <div style="position:relative;">
                <button class="value-amt" @click="surchargesOpen=true">{{ formatCurrency(totalSurcharge) }}</button>
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
                type="text" 
                v-model="amountPaidDisplay" 
                @focus="selectAll"
                @keypress="onlyNumbers"
                @change="handleUpdateAmountPaidCustomer"
                :disabled="paymentMethod=='receivable'"
                class="value-input font-bold text-right customer-payment-input"
                placeholder="0"
                />
          </div>

          <div class="row methods-row">
            <div class="radio-group">
              <label v-for="method in paymentMethods" :key="method.value" class="radio-label">
                <input 
                  type="radio" 
                  :value="method.value" 
                  v-model="paymentMethod"
                  @change="handlePaymentMethodChange" 
                />
                {{ method.label }}
              </label>

            </div>
            <div v-if="paymentMethod === 'transfer'" class="bank-holder">
              <select class="form-select custom-select" v-model="paymentAccount" @change="handleUpdatePaymentAccount">
                <option 
                  v-for="account in props.bankAccounts" 
                  :key="account.id" 
                  :value="account.id"
                  :selected="account.default"
                  :class="{ 'd-none': account.bank_name.toLowerCase().includes('cash') }"
                  >
                    {{ account.bank_name  + ' - ' + account.account_number }}
                </option>
              </select>

            </div>
          </div>

          <div class="row" v-if="changeDue > 0">
             <label>Tiền thừa trả khách</label>
             <div class="value">{{ formatCurrency(changeDue) }}</div>
          </div>
          <div class="row confirm-missing-payment" v-else-if="changeDue < 0">
            <div class="confirm-missing-payment-row">
              <label class="text-danger">Khách còn thiếu</label>
              <div class="value text-danger">{{ formatCurrency(Math.abs(changeDue)) }}</div>
            </div>
             <div class="confirm-missing-payment-row-2" v-if="paymentMethod!=='receivable'">
              <input type="checkbox" v-model="confirm_miss_payment" /> Xác nhận thanh toán thiếu
             </div>
             
          </div>

          <hr class="divider">

          <div class="row">
            <label>Đơn vị vận chuyển</label>
            <select 
            v-model="transportCompany"
            class="form-select custom-select transport-company-select">
              <option 
                v-for="company in props.transportCompanies" 
                :key="company.id" 
                :value="company">
                  {{ company.name }}
              </option>
            </select>
          </div>

          <div class="row">
            <label for=""> Phí ship mình trả tiền mặt</label>
            <input 
                v-model="amountPaidTransportCompanyDisplay" 
                @focus="selectAll"
                @keypress="onlyNumbers" 
                type="text" class="value-input font-bold text-right transport-company-amount" />
          </div>

        </div>
      </div>

      <div class="modal-footer">
        <button class="btn-primary" @click="handlePayment" :disabled="(paymentMethod !== 'receivable' && amountPaidByCustomer < finalTotal && !confirm_miss_payment)">Thanh toán</button>
      </div>

    </div>
  </div>

  <Surcharge 
    v-if="surchargesOpen" 
    :visible="surchargesOpen" 
    :default-surcharges="props.defaultSurcharges"
    :chosen-surcharges="props?.cartData?.surcharges || []"
    @close="handleUpdateSurcharges" 
    />

  <PrintInvoice 
    v-if="toPrint.id"
    :order="toPrint" 
    :key="'print-invoice-' + toPrint.id + '-' + JSON.stringify(toPrint)"
  />

</template>

<script setup>
import { ref, computed, onMounted, watch, onBeforeUnmount, nextTick } from 'vue';
import axios from 'axios';
import { useStore } from 'vuex';
import Surcharge from './Surcharge.vue';
import PrintInvoice from '@/components/Sale/PrintInvoice.vue';

const maxDate = computed(() => {
  const today = new Date();
  today.setDate(today.getDate()); // 30 days from now
  return today.toISOString().split('T')[0];
});


// --- Props & Emits ---
const props = defineProps({
  visible: { type: Boolean, default: false },
  cartData: { type: Object, required: true }, // Expects { total: number, customer: object },
  channels: { type: Array, default: () => [] },
  defaultSurcharges: { type: Array, default: () => [] },
  bankAccounts: { type: Array, default: () => [] },
  transportCompanies: { type: Array, default: () => [] },
  
  // focusCustomer: { type: Object, default: null }
});

const store = useStore();
const toPrint = ref({});

// console.log("Payment Component Props:", props);
// console.log("Payment Component Props:", props);
const emit = defineEmits(['close', 'complete-payment', 'update-cart-data']);

const onlyNumbersandPer = (event) => {
  // Allow only numbers 0-9 and a single % at the end
  const input = event.target.value;
  const char = event.data || String.fromCharCode(event.which || event.keyCode);
  // Allow navigation keys
  if ([8, 9, 13, 27, 37, 39, 46].includes(event.keyCode)) return;

  // If % is pressed
  if (char === '%') {
    // Only allow one % and only at the end
    if (input.includes('%') || event.target.selectionStart !== input.length) {
      event.preventDefault();
    }
    return;
  }
  // Allow numbers
  if (/\d/.test(char)) return;
  // Block everything else
  event.preventDefault();
};

const handleUpdateSurcharges = (surcharges) => {
    // Calculate total surcharge amount
    // console.log(" handleUpdateSurcharges Selected Surcharges:", surcharges);
    surchargesOpen.value = false;

    totalSurcharge.value = surcharges.reduce((sum, s) => 
    sum + (isNaN(Number(s.amount)) ? 0 : Number(s.amount)), 0);

    emit('update-cart-data', {
        ...props.cartData,
        surcharges: surcharges,
        totalSurcharge: totalSurcharge.value
    });
};


const onlyNumbers = (event) => {
  // Allow only numbers 0-9
  const charCode = (event.which) ? event.which : event.keyCode;
  if (charCode > 31 && (charCode < 48 || charCode > 57)) {
    event.preventDefault();
  }
};

const checkAndUpdateDiscount = (event) => {
    // If input ends with %, treat as percentage
    const input = discountMethodValueDisplay.value;
    if (input.endsWith('%')) {
        const percentStr = input.slice(0, -1).trim();
        // console.log("Percentage discount detected:", percentStr);
        const percentValue = parseFloat(percentStr);
        if (!isNaN(percentValue)) {
            discountMethodValue.value = Math.round((percentValue / 100) * totalAmount.value);
            discount.value = discountMethodValue.value;
        } else {
            discountMethodValue.value = 0;
            discount.value = 0;
        }
    } else {
        // Treat as fixed amount
        const fixedValue = parseInt(input.replace(/\D/g, ''), 10);
        if (!isNaN(fixedValue)) {
            discountMethodValue.value = fixedValue;
            discount.value = discountMethodValue.value;
        } else {
            discountMethodValue.value = 0;
            discount.value = 0;
        }
    }

    

    emit('update-cart-data', {
        ...props.cartData,
        discount: discountMethodValue.value,
        discountMethodValue: discountMethodValue.value,
        chosenDiscountMethod: 'VND'
    });
};

const handlePaymentMethodChange = () => {
//   if method is 'receivable', set amountPaidByCustomer to 0 and disable input
    if (paymentMethod.value === 'receivable') {
        amountPaidByCustomer.value = 0;
        confirm_miss_payment.value = false;

        emit('update-cart-data', {
        ...props.cartData,
        amountPaidByCustomer: 0,
        paymentMethod: paymentMethod.value,
        paymentAccount: null
        // return;
    });
    }

    if (paymentMethod.value !== 'receivable' && amountPaidByCustomer.value !== finalTotal.value) {
        amountPaidByCustomer.value = finalTotal.value;
    }

    if (paymentMethod.value === 'cash') {
        paymentAccount.value = 1; // default to Cash account
    }

    if (paymentMethod.value === 'transfer') {
        // Select first non-cash account
        const nonCashAccount = props.bankAccounts.find(acc => !acc.bank_name.toLowerCase().includes('cash'));
        if (nonCashAccount) {
            paymentAccount.value = nonCashAccount.id;
        }
    }

    emit('update-cart-data', {
        ...props.cartData,
        amountPaidByCustomer: amountPaidByCustomer.value,
        paymentMethod: paymentMethod.value,
        paymentAccount: paymentAccount.value
    });
};

const handleUpdatePaymentAccount = () => {
    emit('update-cart-data', {
        ...props.cartData,
        paymentAccount: paymentAccount.value
    });
};

const amountPaidDisplay = computed({
  get: () => {
    // Show empty string if 0 to make typing easier, or keep 0 if preferred
    if (amountPaidByCustomer.value === 0) return '0'; 
    
    // Format with dots (e.g., 100000 -> "100.000")
    return new Intl.NumberFormat('vi-VN').format(amountPaidByCustomer.value);
  },

  set: (newValue) => {
    // 1. Remove any character that is NOT a digit (remove dots, spaces)
    const sanitized = newValue.replace(/\D/g, '');
    
    // 2. Convert back to number and update the real variable
    amountPaidByCustomer.value = sanitized ? parseInt(sanitized, 10) : 0;
  }
});

const handleUpdateAmountPaidCustomer = () => {
    emit('update-cart-data', {
        ...props.cartData,
        amountPaidByCustomer: amountPaidByCustomer.value
    });
};


const amountPaidTransportCompanyDisplay = computed({
    get: () => {
        if (amountPaidTransportCompany.value === 0) return '0';
        return new Intl.NumberFormat('vi-VN').format(amountPaidTransportCompany.value);
    },
    set: (newValue) => {
        const sanitized = newValue.replace(/\D/g, '');
        amountPaidTransportCompany.value = sanitized ? parseInt(sanitized, 10) : 0;
    }
});

const discountMethodValueDisplay = computed({
    get: () => {
        if (discountMethodValue.value === 0) return '0';

        try {
          if (discountMethodValue.value.endsWith('%')) {
              return discountMethodValue.value;
          }
        } catch (e) {
          // Not a string, proceed
        }
        
        return new Intl.NumberFormat('vi-VN').format(discountMethodValue.value);
    },
    set: (newValue) => {
      // allow only numbers and % at the end
        const sanitized = newValue.replace(/[^\d%]/g, '');
        discountMethodValue.value = sanitized;
    }
});

// Optional: Helper to select all text on click (UX best practice for POS)
const selectAll = (event) => {
  event.target.select();
};

const surchargesOpen = ref(false);
// --- State ---
// Dropdown Data (Mocking the options from your HTML)

const selectedSeller = ref(36934);

const channels = props.channels || [];
const selectedChannel = ref('');


function getTodayDateStr() {
  const d = new Date();
  const month = (d.getMonth() + 1).toString().padStart(2, '0');
  const day = d.getDate().toString().padStart(2, '0');
  return `${d.getFullYear()}-${month}-${day}`;
}
function getNowTimeStr() {
  const d = new Date();
  const hours = d.getHours().toString().padStart(2, '0');
  const minutes = d.getMinutes().toString().padStart(2, '0');
  return `${hours}:${minutes}`;
}

const purchaseDate = ref(getTodayDateStr());
const purchaseTime = ref(getNowTimeStr());

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
const confirm_miss_payment = ref(false);
const totalAmount = ref(0); // Will load from props
const discount = ref(0);
// const surchargeAmount = ref(0);
const amountPaidByCustomer = ref(0); // "Khách thanh toán"
const amountPaidTransportCompany = ref(0); // "Phí ship mình trả"
const discountMethodValue = ref(0);
const chosenDiscountMethod = ref('VND');

// console.log("Initialized chosenDiscountMethod to:", chosenDiscountMethod.value);
const totalSurcharge = ref(0);
const transportCompany = ref(null);
const paymentAccount = ref(1); // default to Cash account
// const 
// Payment Methods
const paymentMethod = ref('cash'); // 'cash', 'card', 'transfer'
const paymentMethods = [
  { value: 'cash', label: 'Tiền mặt' },
  { value: 'transfer', label: 'Chuyển khoản' },
  { value: 'receivable', label: 'Công Nợ' }
];
// --- Computed Logic ---

// 1. Calculate the final amount the customer needs to pay
const finalTotal = computed(() => {
  return totalAmount.value - discount.value + totalSurcharge.value;
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
    totalAmount.value = props.cartData.total ;
     // Auto-fill full amount
    discount.value = props.cartData.discount || 0;
    // surchargeAmount.value = props.cartData.surcharge || 0;
    discountMethodValue.value = props.cartData.discountMethodValue || 0;
    chosenDiscountMethod.value = props.cartData.chosenDiscountMethod || 'VND';
    selectedChannel.value = props.cartData.channel || (channels.length > 0 ? channels[0].name : '');
    // console.log("current chosenDiscountMethod to:", chosenDiscountMethod.value);
    // console.log("current chosenDiscountValue to:", discountMethodValue.value);

    paymentMethod.value = props.cartData.paymentMethod || 'cash';
    paymentAccount.value = props.cartData.paymentAccount || 1;
    // console.log("props.cartData.transportCompany:", props.cartData.transportCompany);
    transportCompany.value = props.cartData.transportCompany || props.transportCompanies[0];
    // console.log("props.transportCompanies:", props.transportCompanies);
    // console.log("Initialized transportCompany to:", transportCompany.value);
    amountPaidTransportCompany.value = props.cartData.amountPaidTransportCompany || 0;
    totalSurcharge.value = props.cartData.surcharge || 0;
    if (paymentMethod.value === 'receivable') {
        amountPaidByCustomer.value = 0;
    } else {
    amountPaidByCustomer.value = props.cartData.amountPaidByCustomer || totalAmount.value - discount.value + totalSurcharge.value;
    }
  }
  purchaseDate.value = getTodayDateStr();
  purchaseTime.value = getNowTimeStr();
});

const printInvoice = () => {
      window.print();
    };

// --- Actions ---
const handlePayment = async () => {
  const payload = props.cartData ? { ...props.cartData } : {};

  if (paymentMethod.value === 'receivable') {
    amountPaidByCustomer.value = 0;
    paymentAccount.value = null;
  } 

  if (paymentMethod.value === 'cash') {
    paymentAccount.value = 1; // default to Cash account
  }
  
  await axios.post('/invoices/', {
    ...payload,
    amount_paid_by_customer: amountPaidByCustomer.value,
    amount_paid_transport_company: amountPaidTransportCompany.value,
    surcharges: props.cartData.surcharges || [],
    total_surcharge: totalSurcharge.value,
    final_total: finalTotal.value,
    payment_method: paymentMethod.value, 
    payment_account: paymentAccount.value,
    channel: selectedChannel.value,
    transport_company: transportCompany.value?.name || '',
    amount_paid_transport_company: amountPaidTransportCompany.value,
    date: purchaseDate.value,
    time: purchaseTime.value,
    delivery_address: props.cartData.customer ? props.cartData.customer.address : '',
    customer: props.cartData.customer ? props.cartData.customer.id : 1,
  }).then(async response => {
    payload.paymentConfirmation = response.data;

    toPrint.value = response.data;
    await nextTick();
    printInvoice();

    emit('complete-payment', response.data);

  }).catch(error => {
    console.error("Error processing payment:", error);
    // Handle error (e.g., show notification)
  });

};

const close = () => {
  emit('update-cart-data', {
    ...props.cartData,
    discount: discount.value,
    amountPaidByCustomer: amountPaidByCustomer.value,
    amountPaidTransportCompany: amountPaidTransportCompany.value,
    paymentMethod: paymentMethod.value, 
    paymentAccount: paymentAccount.value,
    selectedChannel: selectedChannel.value,
    selectedSeller: selectedSeller.value,
    transportCompany: transportCompany.value,
    amountPaidTransportCompany: amountPaidTransportCompany.value,
  });  

  emit('close');
};
</script>



<style scoped>

input, select {
  background-color: white;
  color: black;
  font-size: 1rem;
}
.bank-holder {
    margin-top: 0.5rem;
    display: flex;
    align-items: center;
    width: 100%;
    padding: 0.5rem;
    background-color: #f4f4f4;
    border-radius: 0.5rem;

    select {
        flex: 1;
        font-size: 1rem;
    }

}

.transport-company-select {
    font-size: 1rem;
}
/* Basic Styles to mimic the POS layout - Replace with Tailwind if preferred */
.modal-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  background: rgba(0,0,0,0.5); z-index: 1000;
  display: flex; justify-content: end;
}

.modal-container {
  background: white; 
  width: 30rem; 
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
.customer-info{
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    margin-bottom: 1rem;

    .customer-name {
        font-size: 1rem;
        display: flex;
        justify-content: flex-start;
        text-align: left;
    }

}

.confirm-missing-payment {
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    align-items: center;

    .confirm-missing-payment-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
    }

    .confirm-missing-payment-row-2 {
        input {
            margin-right: 5px;
        }
        display: flex;
        justify-content: flex-start;
        width: 100%;
    }
}

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
input.transport-company-amount {
    border-top: none;
    border-left: none;
    border-right: none;
    width: 8rem;
    font-size: 1rem;
}
input.transport-company-amount::-webkit-outer-spin-button,
input.transport-company-amount::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.form-select, .form-input { 
    padding: 1px; 
    border: 0px solid #ccc; 
    border-radius: 3px; 
    margin-right: 3px; }
.date-input{
    width: 8rem;
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

.divider { border: 0; border-top: 2px dashed #a9a9a9; margin: 10px 0; background-color: transparent;}
.text-primary { color: #007bff; font-size: 1.2rem; }
.text-danger { color: #dc3545; }
.font-bold { font-weight: bold; }
.text-right { text-align: right; }

/* Methods */
.methods-row { 
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    /* justify-content: space-around;  */
}
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

  button:disabled {
    background: #ccc;
    cursor: not-allowed;
  }
}
.note-input { flex: 1; border: 1px solid #ccc; padding: 5px; resize: none; }
.btn-primary {
  background: #007bff; color: white; border: none; 
  padding: 0 30px; font-size: 1.1rem; cursor: pointer; border-radius: 4px;
}
.btn-primary:hover { background: #0069d9; }


</style>