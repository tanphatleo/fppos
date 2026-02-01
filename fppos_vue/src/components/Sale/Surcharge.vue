

<template>
  <div v-if="visible" class="modal-overlay-a" @mousedown.self="onOverlayClick" ref="overlayRef">
    <div class="modal-container" ref="modalRef">
      <div class="modal-header">
        <h3 class="title">Các khoản thu khác</h3>
        <button @click="close" class="close-btn">×</button>
      </div>
      <div class="modal-body">
        <div class="table-container">
          <table class="grid-blue">
            <thead>
              <tr>
                <th class="cell-checkbox"></th>
                <th class="cell-code">Mã thu khác</th>
                <th class="cell-name">Loại thu</th>
                <th class="cell-price text-right">Mức thu</th>
                <th class="cell-price text-right">Thu trên hóa đơn</th>
              </tr>
            </thead>
            <tbody>
              <tr class="tr-summary">
                <td colspan="4" class="text-right font-bold">Tổng thu:</td>
                <td class="text-right font-bold text-primary">{{ formatCurrency(totalAmount) }}</td>
              </tr>
              <tr v-for="item in surchargeList" :key="item.id" :class="{ selected: item.selected }">
                <td class="cell-checkbox text-center">
                  <input 
                    type="checkbox" 
                    v-model="item.selected" 
                    class="form-check-input"
                  />
                </td>
                <td class="cell-code">{{ item.code }}</td>
                <td class="cell-name">{{ item.description }}</td>
                <td class="cell-price text-right">
                  <span v-if="item.value > 0">{{ formatCurrency(item.amount) }}</span>
                  <span v-else class="text-muted">-</span>
                </td>
                <td class="cell-price">
                  <input 
                    type="number" 
                    @focus="selectAll"
                    v-model="item.amount"
                    :disabled="!item.selected"
                    class="form-control-sm text-right no-arrow"
                  />
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
// --- Refs for outside click ---
const overlayRef = ref(null);
const modalRef = ref(null);

const onOverlayClick = (e) => {
  // Only emit close if click is outside modal-container
  if (modalRef.value && !modalRef.value.contains(e.target)) {
    close();
  }
};

// --- Props & Emits ---
const props = defineProps({
  visible: { type: Boolean, default: false },
  // Allow passing existing surcharges from parent
  items: { type: Array, default: () => [] },
  defaultSurcharges: { type: Array, default: () => [] },
  chosenSurcharges: { type: Array, default: () => [] }
});

const emit = defineEmits(['close', 'update-surcharges']);

// --- State ---
// Default mock data based on your HTML snapshot
const defaultSurcharges = props.defaultSurcharges

const selectAll = (event) => {
  event.target.select();
};

// deep copy to avoid mutating props directly
const surchargeList = ref(JSON.parse(JSON.stringify(defaultSurcharges)));

// console.log("Updating surchargeList based on chosenSurcharges:", props.chosenSurcharges);
// check each surcharge in chosenSurcharges and update surchargeList accordingly
if (props.chosenSurcharges && props.chosenSurcharges.length > 0) {
    
  props.chosenSurcharges.forEach(chosen => {
    const match = surchargeList.value.find(s => s.id === chosen.id);
    if (match) {
      match.selected = chosen.selected;
      match.amount = chosen.amount;
    }
  });
}


// If props.items is provided (e.g., editing previously saved state), use it
watch(() => props.items, (newItems) => {
  if (newItems && newItems.length > 0) {
    surchargeList.value = JSON.parse(JSON.stringify(newItems));
  }
}, { immediate: true });

// --- Computed ---
const totalAmount = computed(() => {
  console.log("Calculating totalAmount from surchargeList:", surchargeList.value);
  return surchargeList.value.reduce((sum, item) => {
    // if item.amount undefined or NaN, treat as 0
    const amount = isNaN(Number(item.amount)) ? 0 : Number(item.amount);

    return sum + (item.selected ? amount : 0);

    // return item.selected ? sum + Number(item.amount) : sum;
  }, 0);
});

// --- Formatting ---
const formatCurrency = (value) => {
  return new Intl.NumberFormat('vi-VN').format(value);
};

// --- Actions ---
const toggleSelection = (item) => {
  // Logic if needed when toggling
};



const close = () => {
    // console.log("Closing Surcharge Modal. Selected Surcharges:", surchargeList.value.filter(s => s.selected));
  emit('close', surchargeList.value.filter(s => s.selected));
};
</script>

<style scoped>

.no-arrow::-webkit-outer-spin-button,
.no-arrow::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}    
/* Modal Overlay */
.modal-overlay-a {
    position: fixed; top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0,0,0,0.5); 
    z-index: 20000;
  /* display: flex;  */
}

.modal-container {
  position: absolute;
  top: 20%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  width: 60rem;
  max-width: 95vw;
  border-radius: 1rem; box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  display: flex; flex-direction: column;
  overflow: hidden;
}

/* Header */
.modal-header {
  padding: 10px 15px; background: #007bff; color: white;
  display: flex; justify-content: space-between; align-items: center;
}
.title { margin: 0; font-size: 1.1rem; font-weight: 500; }
.close-btn { background: none; border: none; color: white; font-size: 1.5rem; cursor: pointer; }

/* Table Styling (Mimicking .grid-blue) */
.table-container { padding: 0; max-height: 60vh; overflow-y: auto; }

.grid-blue { width: 100%; border-collapse: collapse; font-size: 14px; }

.grid-blue thead th {
  background-color: #f0f3f5; color: #333; font-weight: 600;
  padding: 8px 10px; border-bottom: 1px solid #ccc; border-right: 1px solid #e0e0e0;
  text-align: left;
}

.grid-blue tbody td {
  padding: 8px 10px; border-bottom: 1px solid #eee; border-right: 1px solid #eee;
  vertical-align: middle;
}

/* Column Widths */
.cell-checkbox { width: 40px; }
.cell-code { width: 150px; color: #0056b3; } /* Code often blue link color */
.cell-price { width: 140px; }

/* Interactive Elements */
.tr-summary { background-color: #fffae6; } /* Highlight summary row slightly */
.text-right { text-align: right; }
.text-center { text-align: center; }
.font-bold { font-weight: bold; }
.text-primary { color: #007bff; }
.text-muted { color: #999; }

/* Input Styling */
.form-control-sm {
  width: 100%; padding: 4px 8px;
  border: 1px solid #ccc; border-radius: 3px;
  font-size: 14px;
}
.form-control-sm:focus { border-color: #007bff; outline: none; }
.form-control-sm:disabled { background-color: #f9f9f9; color: #aaa; }

.form-check-input {
  width: 16px; height: 16px; cursor: pointer;
}

/* Footer */
.modal-footer {
  padding: 10px 15px; border-top: 1px solid #eee; background: #f9f9f9;
  display: flex; justify-content: flex-end; gap: 10px;
}
.btn-primary { background: #007bff; color: white; border: none; padding: 6px 15px; border-radius: 3px; cursor: pointer; }
.btn-secondary { background: #6c757d; color: white; border: none; padding: 6px 15px; border-radius: 3px; cursor: pointer; }
</style>