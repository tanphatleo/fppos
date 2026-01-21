<template>
  <div class="modal-overlay" @mousedown.self="$emit('close')">
    <div class="transaction-window" @click.stop style="border-radius: 0.5rem;">
      <div class="window-header">
        <span class="window-title">
          <span class="no-select">{{ (item && item.id ? 'Sửa ' : 'Lập ' ) + (debit_or_credit === 'DR' ? 'Phiếu Thu' : 'Phiếu Chi') }}</span>
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
                  <label for="date">Ngày</label>
                  <input id="date" ref="dateInput" v-model="date" type="date" required @click="openDatePicker" :min="minDate" :max="maxDate"/>
                </div>

                <div class="form-group">
                  <label for="amount">Số tiền</label>
                  <input id="amount" v-model="amountDisplay" type="text" required style="text-align: right;" @focus="selectAll" />
                </div>

                <div class="form-group">
                  <label for="debit_or_credit">Loại phiếu</label>
                  <select id="debit_or_credit" v-model="debit_or_credit" required disabled>
                    <option value="DR">Thu (Debit)</option>
                    <option value="CR">Chi (Credit)</option>
                  </select>
                </div>

                <div class="form-group">
                  <label for="account">Tài khoản</label>
                  <select id="account" v-model="account_id" required>
                    <option v-for="acc in accounts" :key="acc.id" :value="acc.id" >
                      {{ acc.bank_name }} - {{ acc.account_number }} ({{ acc.account_holder_name }})
                    </option>
                  </select>
                </div>
              </div>
              <div class="col-right">
                <div class="form-group">
                  <label for="transaction_type">Loại giao dịch</label>
                  <select id="transaction_type" v-model="transaction_type_id" required>
                    <option v-for="tt in filteredTransactionTypes" :key="tt.id" :value="tt.id">
                      {{ tt.name }}
                    </option>
                  </select>
                </div>
                <div class="form-group">
                  <label for="description">Mô tả</label>
                  <textarea id="description" v-model="description" rows="3"></textarea>
                </div>
                <div class="form-group">
                  <label for="is_active">Kích hoạt</label>
                  <input id="is_active" v-model="isActive" type="checkbox" :disabled="!store.getters.userAdmin || !store.getters.userSuperadmin"/>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="window-footer">
          <button type="button" class="btn btn-outline" @click="$emit('close')">Đóng</button>
          <button type="button" class="btn btn-primary new-button" @click="handleSubmit" :disabled="amountDisplay === '0' || !description.trim()">Lưu</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, toRefs, computed } from 'vue';
import axios from 'axios';
import { useStore } from 'vuex';

export default {
  name: 'AddEditTrans',
  props: {
    item: {
      type: Object,
      default: null
    },
    accounts: {
      type: Array,
      default: () => []
    },
    transactionTypes: {
      type: Array,
      default: () => []
    }, 
    d_edit_days: {
      type: Number,
      default: 0
    }
  },
  emits: ['close', 'saved'],
  setup(props, { emit }) {

    const { item, accounts, transactionTypes, d_edit_days } = toRefs(props);
    const dateInput = ref(null);
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

    const debit_or_credit = ref(item.value?.debit_or_credit || 'DR');
    
    const amount = ref(item.value && item.value.id ? item.value.amount : '');
    const account_id = ref(item.value && item.value.id ? item.value.account : 1);
    const date = ref(item.value && item.value.id ? item.value.date : new Date().toISOString().slice(0, 10));
    const ref_field = ref(item.value && item.value.id ? item.value.ref : '');
    const description = ref(item.value && item.value.id ? item.value.description : '');
    const isActive = ref(item.value && item.value.is_active !== undefined ? item.value.is_active : true);

    const filteredTransactionTypes = computed(() => {
      if (!transactionTypes.value) return [];
      // Assuming transaction type objects have a 'transaction_type' field ('DR' or 'CR')
      return transactionTypes.value.filter(tt => tt.debit_or_credit === debit_or_credit.value);
    });

    const transaction_type_id = ref(item.value && item.value.id ? item.value.transaction_type : item.value?.debit_or_credit === 'DR' ? 2 : 1);

    watch(filteredTransactionTypes, (newVal) => {
      const isEditing = item.value && item.value.id;
      if (!isEditing && newVal && newVal.length > 0 && !transaction_type_id.value) {
        transaction_type_id.value = newVal[0].id;
      }
    });

    const amountDisplay = computed({
      get: () => {
        if (amount.value === '' || amount.value === 0) return '0';
        return new Intl.NumberFormat('vi-VN').format(amount.value);
      },
      set: (newValue) => {
        const sanitized = newValue.replace(/\D/g, '');
        amount.value = sanitized ? parseInt(sanitized, 10) : 0;
      }
    });

    watch(item, (newVal) => {
      const isEditing = newVal && newVal.id;
      debit_or_credit.value = newVal?.debit_or_credit || 'DR';
      transaction_type_id.value = isEditing ? newVal.transaction_type : null;
      amount.value = isEditing ? newVal.amount : '';
      account_id.value = isEditing ? newVal.account : null;
      date.value = isEditing ? newVal.date : new Date().toISOString().slice(0, 10);
      ref_field.value = isEditing ? newVal.ref : '';
      description.value = isEditing ? newVal.description : '';
      isActive.value = newVal && newVal.is_active !== undefined ? newVal.is_active : true;
    });

    function openDatePicker() {
      if (dateInput.value) {
        // Modern browsers support showPicker()
        if (typeof dateInput.value.showPicker === 'function') {
          try {
            dateInput.value.showPicker();
          } catch (e) {
            // Fallback for browsers that might throw an error
            dateInput.value.focus();
          }
        } else {
          // Fallback for older browsers like Firefox
          dateInput.value.focus();
        }
      }
    }

    async function handleSubmit() {
      const payload = {
        transaction_type: transaction_type_id.value,
        debit_or_credit: debit_or_credit.value,
        amount: amount.value,
        account: account_id.value,
        date: date.value,
        ref: ref_field.value,
        description: description.value,
        is_active: isActive.value
      };
      // If editing, send PUT; else POST
      if (item.value && item.value.id) {
        await axios.put(`/transactions/${item.value.id}/`, payload)
          .then(response => {
            emit('saved', response.data);
          })
          .catch(error => {
            console.error('Error updating transaction:', error);
            window.alert("Lỗi khi cập nhật giao dịch: " + (error.response && error.response.data ? JSON.stringify(error.response.data) : error.message));
          });
      } else {
        await axios.post('/transactions/', payload)
          .then(response => {
            emit('saved', response.data);
          })
          .catch(error => {
            console.error('Error creating transaction:', error);
            window.alert("Lỗi khi tạo giao dịch: " + (error.response && error.response.data ? JSON.stringify(error.response.data) : error.message));
          });
      }
    }

    function selectAll(event) {
      event.target.select();
    }

    return {
      transaction_type_id,
      debit_or_credit,
      amount,
      amountDisplay,
      account_id,
      date,
      ref_field,
      description,
      isActive,
      item,
      accounts,
      transactionTypes,
      filteredTransactionTypes,
      dateInput,
      openDatePicker,
      handleSubmit,
      selectAll,
      minDate,
      maxDate,
      store
    };
  }
};
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

input , select, textarea {
  background-color: white;
  color: black;
  border-radius: 0.3rem;
  width: 100%;
  border: 1px solid #ccc;
  padding-left: 0.5rem;
  padding-right: 0.5rem;
}

* {
  box-sizing: border-box;
  font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  text-align: left;
}

.transaction-window {
  background: #fff;
  width: 60rem;
  max-width: 95vw;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* Header */
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

/* Tabs */
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

/* Form Body */
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

input[type="checkbox"] {
  width: auto;
  flex-grow: 0;
}

/* Footer */
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

.no-select {
  user-select: none;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}
</style>