<template>
  <div v-if="!showPrintView" class="modal-overlay" @mousedown.self="$emit('close')">
    <div class="invoice-window" @click.stop>
      <div class="window-header">
        <span class="window-title">
          <span class="no-select">Chi tiết Hóa Đơn: {{ item.code }}</span>
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
            <li class="active"><a href="#">Thông tin chung</a></li>
          </ul>
        </div>

        <div class="form-body">
          <div class="tab-pane">
            <div class="form-layout">
              <div class="col-left">
                <div class="form-group">
                  <label>Khách hàng</label>
                  <input type="text" :value="item.customer_name" readonly />
                </div>
                <div class="form-group">
                  <label>Điện thoại</label>
                  <input type="text" :value="item.customer_phone_number" readonly />
                </div>
                <div class="form-group">
                  <label>Địa chỉ</label>
                  <textarea :value="item.delivery_address" rows="2" readonly></textarea>
                </div>
                <div class="form-group">
                  <label>Ngày</label>
                  <input type="date" v-model="form.date" :disabled="!item.is_active" @click="$event.target.showPicker()" :max="maxDate" :min="minDate" />
                </div>
                <div class="form-group">
                  <label>Kênh bán</label>
                  <select v-model="form.channel" :disabled="!item.is_active">
                    <option v-for="channel in channels" :key="channel.name" :value="channel.name">
                      {{ channel.name }}
                    </option>
                  </select>
                </div>
                <div class="form-group">
                  <label>Ghi chú</label>
                  <textarea :value="item.note" rows="2"></textarea>
                </div>
                <div class="form-group">
                  <label>Kích hoạt</label>
                    <input type="checkbox" v-model="form.is_active" :disabled="!item.is_active || (!store.getters.userAdmin && !store.getters.userSuperadmin)" />
                </div>
              </div>

              <div class="col-right">
                <div class="items-section">
                  <strong style="color: black;">Các sản phẩm</strong>
                  <div class="items-list">
                    <div v-for="product in item.items" :key="product.uuid" class="item-row">
                      <div class="item-name">{{ product.name }}</div>
                      <div class="item-qty">x{{ product.quantity }}</div>
                      <div class="item-price">{{ formatCurrency(product.price * product.quantity) }}</div>
                    </div>
                  </div>
                </div>
                <div class="totals-section">
                  <strong style="color: black;">Tổng cộng</strong>
                  <div class="total-row">
                    <span>Tiền hàng</span>
                    <span>{{ formatCurrency(item.total) }}</span>
                  </div>
                  <div class="total-row" v-if="Number(item.discount) > 0">
                    <span>Giảm giá</span>
                    <span>-{{ formatCurrency(item.discount) }}</span>
                  </div>
                  <div class="total-row" v-if="Number(item.total_surcharge) > 0">
                    <span>Phụ phí</span>
                    <span>+{{ formatCurrency(item.total_surcharge) }}</span>
                  </div>
                  <hr v-if="!item.code.startsWith('SP_')"/>
                  <div class="total-row final" v-if="!item.code.startsWith('SP_')">
                    <span>Khách phải trả</span>
                    <span>{{ formatCurrency(item.final_total) }}</span>
                  </div>
                  <div class="total-row" v-if="!item.code.startsWith('SP_')">
                    <span>Đã thanh toán</span>
                    <span>{{ formatCurrency(item.amount_paid_by_customer) }}</span>
                  </div>
                  <hr v-if="!item.code.startsWith('SP_')"/>
                  <!-- only show if code do not start with SP_ -->
                  <div class="total-row final" v-if="!item.code.startsWith('SP_')">
                    <span>Tiền ship đã trả bằng tiền mặt</span>
                    <span>{{ formatCurrency(item.amount_paid_transport_company) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="window-footer">
          <button type="button" class="btn btn-outline" @click="handlePrint" style="margin-right: auto;"> In   </button>
          <button type="button" class="btn btn-outline" @click="$emit('close')">Đóng</button>
          <button type="button" class="btn btn-primary" @click="handleSubmit" v-if="item.is_active">Lưu</button>
        </div>
      </div>
    </div>
  </div>
  <PrintInvoice v-else :order="item" />
</template>

<script>
import { ref, reactive, watch, toRefs, computed, nextTick } from 'vue';
import axios from 'axios';
import { useStore } from 'vuex';
import PrintInvoice from '../Sale/PrintInvoice.vue';

export default {
  name: 'AddEditInvoice',
  components: {
    PrintInvoice,
  },
  props: {
    item: {
      type: Object,
      required: true,
    },
    channels: {
      type: Array,
      default: () => [],
    },
    d_edit_days: {
      type: Number,
      default: 3,
    },
  },

  emits: ['close', 'saved'],
  setup(props, { emit }) {
    const showPrintView = ref(false);

    const getLocalDateISO = (date) => {
      const tzOffset = date.getTimezoneOffset() * 60000; // offset in milliseconds
      const localISOTime = new Date(date - tzOffset).toISOString().slice(0, 10);
      return localISOTime;
    };
    const maxDate = computed(() => {
      const today = new Date();
      return today.toISOString().split('T')[0];
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
    const { item } = toRefs(props);
    const store = useStore();

    const form = reactive({
      date: '',
      is_active: true,
      channel: '',
    });

    watch(item, (newVal) => {
      if (newVal) {
        form.date = newVal.date;
        form.is_active = newVal.is_active;
        form.channel = newVal.channel;
      }
    }, { immediate: true });

    const formatCurrency = (value) => {
      const numericValue = Number(value);
      if (isNaN(numericValue)) return '0 ₫';
      return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(numericValue);
    };

    async function handleSubmit() {
      const payload = {
        date: form.date,
        is_active: form.is_active,
        channel: form.channel,
      };

      try {
        const response = await axios.patch(`/invoices/${item.value.id}/`, payload);
        emit('saved', response.data);
        emit('close');
      } catch (error) {
        console.error("Error updating invoice:", error);
        window.alert("Lỗi cập nhật hóa đơn: " + (error.response && error.response.data ? JSON.stringify(error.response.data) : error.message));
      }
    }

    const handlePrint = () => {
      showPrintView.value = true;
      nextTick(() => {
        window.print();
        showPrintView.value = false;
      });
    };

    return {
      form,
      formatCurrency,
      handleSubmit,
      store, // Make store available in the template
      maxDate,
      minDate,
      showPrintView,
      handlePrint,
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

input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

input:focus, select:focus, textarea:focus {
  border-color: $kv-primary;
  outline: none;
}

input[type="checkbox"] {
  width: auto;
  flex-grow: 0;
}

input[readonly], textarea[readonly] {
  background-color: #e9ecef;
  cursor: not-allowed;
}

.modal-overlay {
  position: fixed;
  top: 0; left: 0;
  width: 100vw; height: 100vh;
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}
.invoice-window {
  background: #fff;
  width: 70rem;
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

.form-body { padding: 20px; background: #fff; max-height: 70vh; overflow-y: auto; }
.form-layout { display: flex; gap: 20px; }
.col-left, .col-right { flex: 1; }

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

.items-section, .totals-section {
  border: 1px solid #eee;
  padding: 1rem;
  border-radius: 4px;
  background: #f9f9f9;
}
.totals-section {
  margin-top: 1rem;
}
.items-list {
  max-height: 300px;
  overflow-y: auto;
  margin-top: 0.5rem;

  &::-webkit-scrollbar {
    display: none;
  }
  -ms-overflow-style: none;  /* IE and Edge */
  scrollbar-width: none;  /* Firefox */
}
.item-row, .total-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #eee;
}
.item-name {
  flex-grow: 1;
}
.item-qty {
  width: 50px;
  text-align: center;
}
.item-price {
  width: 100px;
  text-align: right;
}
.total-row.final {
  font-weight: bold;
  font-size: 1.1rem;
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
</style>