<template>
  <div class="modal-overlay" @mousedown.self="$emit('close')">
    <div class="surcharge-window" @click.stop>
      <div class="window-header">
        <span class="window-title">
          <span class="no-select">{{ item && item.id ? 'Chỉnh sửa phụ phí' : 'Tạo phụ phí mới' }}</span>
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
                  <label for="code">Mã</label>
                  <input id="code" v-model="code" type="text" maxlength="10" />
                </div>
                <div class="form-group">
                  <label for="description">Mô tả</label>
                  <input id="description" v-model="description" type="text" maxlength="100" required />
                </div>
                <div class="form-group">
                  <label for="amount">Số tiền</label>
                  <input id="amount" v-model="amountDisplay" type="text" required style="text-align: right;" @focus="selectAll" @beforeinput="onlyNumbers" />
                </div>
                <div class="form-group">
                  <label for="is_active">Kích hoạt</label>
                  <input id="is_active" v-model="isActive" type="checkbox" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="window-footer">
          <button type="button" class="btn btn-outline" @click="$emit('close')">Đóng</button>
          <button type="button" class="btn btn-primary new-button" @click="handleSubmit" :disabled="!code.trim() || amount === 0 || !description.trim()">
            {{ item && item.id ? 'Lưu' : 'Tạo mới' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, toRefs, computed } from 'vue';
import axios from 'axios';

export default {
  name: 'AddEditSurcharge',
  props: {
    item: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'saved'],
  setup(props, { emit }) {
    const { item } = toRefs(props);
    const code = ref(item.value ? item.value.code : '');
    const description = ref(item.value ? item.value.description : '');
    const amount = ref(item.value ? item.value.amount : 0);
    const isActive = ref(item.value && item.value.is_active !== undefined ? item.value.is_active : true);

    const amountDisplay = computed({
      get: () => {
        if (amount.value === 0) return '0';
        return new Intl.NumberFormat('vi-VN').format(amount.value);
      },
      set: (newValue) => {
        const sanitized = newValue.replace(/\D/g, '');
        amount.value = sanitized ? parseInt(sanitized, 10) : 0;
      }
    });

    watch(item, (newVal) => {
      code.value = newVal ? newVal.code : '';
      description.value = newVal ? newVal.description : '';
      amount.value = newVal ? newVal.amount : 0;
      isActive.value = newVal && newVal.is_active !== undefined ? newVal.is_active : true;
    });

    function selectAll(event) {
      event.target.select();
    }

    function onlyNumbers(event) {
      // The `beforeinput` event is more reliable than `keypress`.
      // It checks the data that is about to be inserted, handling typing and pasting.
      if (event.data && !/^\d+$/.test(event.data)) {
        event.preventDefault();
      }
    }

    async function handleSubmit() {
      const payload = {
        code: code.value,
        description: description.value,
        amount: amount.value,
        is_active: isActive.value
      };
      if (item.value && item.value.id) {
        // Editing existing surcharge
        payload.id = item.value.id;
        await axios.put(`/surcharges/${item.value.id}/`, payload)
          .then(response => {
            console.log("Surcharge updated:", response.data);
            emit('saved', response.data);
          })
          .catch(error => {
            console.error("Error updating surcharge:", error);
            window.alert("Lỗi khi cập nhật phụ phí: " + (error.response && error.response.data ? JSON.stringify(error.response.data) : error.message));
          });
      } else {
        // Creating new surcharge
        await axios.post('/surcharges/', payload)
          .then(response => {
            console.log("Surcharge created:", response.data);
            emit('saved', response.data);
          })
          .catch(error => {
            console.error("Error creating surcharge:", error);
            window.alert("Lỗi khi tạo phụ phí: " + (error.response && error.response.data ? JSON.stringify(error.response.data) : error.message));
          });
      }
    }

    return {
      code,
      description,
      amount,
      amountDisplay,
      isActive,
      item,
      handleSubmit,
      selectAll,
      onlyNumbers
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
  background: rgba(0, 0, 0, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}
.surcharge-window {
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