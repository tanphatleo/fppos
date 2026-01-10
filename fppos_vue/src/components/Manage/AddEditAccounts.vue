<template>
  <div class="modal-overlay" @mousedown.self="$emit('close')">
    <div class="modal-content">
      <h2>{{ item ? 'Chỉnh sửa tài khoản' : 'Tạo tài khoản mới' }}</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="account_number">Số tài khoản</label>
          <input
            id="account_number"
            v-model="account_number"
            type="text"
            required
            placeholder="Nhập số tài khoản"
          />
        </div>
        <div class="form-group">
          <label for="account_holder_name">Tên chủ tài khoản</label>
          <input
            id="account_holder_name"
            v-model="account_holder_name"
            type="text"
            required
            placeholder="Nhập tên chủ tài khoản"
          />
        </div>
        <div class="form-group">
          <label for="bank_name">Ngân hàng</label>
          <input
            id="bank_name"
            v-model="bank_name"
            type="text"
            required
            placeholder="Nhập tên ngân hàng"
          />
        </div>
        <div class="form-group">
          <label for="is_active">Kích hoạt</label>
          <select id="is_active" v-model="is_active">
            <option :value="true">Đang sử dụng</option>
            <option :value="false">Ngừng sử dụng</option>
          </select>
        </div>
        <button type="submit" class="save-btn">
          {{ item ? 'Lưu thay đổi' : 'Tạo mới' }}
        </button>
        <button type="button" class="cancel-btn" @click="$emit('close')">Hủy</button>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, watch, toRefs } from 'vue';
import axios from 'axios';

export default {
  name: 'AddEditAccounts',
  props: {
    item: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'saved'],
  setup(props, { emit }) {
    const { item } = toRefs(props);
    const account_number = ref(item.value ? item.value.account_number : '');
    const account_holder_name = ref(item.value ? item.value.account_holder_name : '');
    const bank_name = ref(item.value ? item.value.bank_name : '');
    const is_active = ref(item.value && item.value.is_active !== undefined ? item.value.is_active : true);

    watch(item, (newVal) => {
      account_number.value = newVal ? newVal.account_number : '';
      account_holder_name.value = newVal ? newVal.account_holder_name : '';
      bank_name.value = newVal ? newVal.bank_name : '';
      is_active.value = newVal && newVal.is_active !== undefined ? newVal.is_active : true;
    });

    async function handleSubmit() {

        // check if editing or creating
        if (item.value && item.value.id) {
          // Editing existing account
          const payload = {
            id: item.value.id,
            account_number: account_number.value,
            account_holder_name: account_holder_name.value,
            bank_name: bank_name.value,
            is_active: is_active.value
          };

          // send api request to update
          await axios.put(`/accounts/${item.value.id}/`, payload)
            .then(response => {
              console.log("Account updated:", response.data);
            })
            .catch(error => {
              console.error("Error updating account:", error);
            });

          emit('saved', payload);
          return;
        } else {
          // Creating new account
          const payload = {
            account_number: account_number.value,
            account_holder_name: account_holder_name.value,
            bank_name: bank_name.value,
            is_active: is_active.value
          };

          // send api request to create
          await axios.post('/accounts/', payload)
            .then(response => {
              console.log("Account created:", response.data);
            })
            .catch(error => {
              console.error("Error creating account:", error);
            });
          emit('saved', payload);
        }
      };

      return {
        account_number,
        account_holder_name,
        bank_name,
        is_active,
        item,
        handleSubmit
      };
  }
};
</script>

<style scoped>


textarea , input, select {
  background-color: #f9f9f9;
  color: black;
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

.modal-content {
  background: #fff;
  border-radius: 10px;
  box-shadow: 0 2px 16px rgba(0,0,0,0.2);
  padding: 1rem;
  min-width: 350px;
  max-width: 90vw;
  min-height: 100px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.form-group {
  margin-bottom: 1rem;
  width: 100%;
  input {
    width: 30rem;
  }
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

input,
textarea,
select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
}

.save-btn {
  margin-top: 1rem;
  padding: 0.5rem 1.5rem;
  background: #0070F4;
  color: #fff;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}
.save-btn:hover {
  background: #0056b3;
}

.cancel-btn {
  margin-top: 1.5rem;
  padding: 0.5rem 1.5rem;
  background: #e74c3c;
  color: #fff;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
  margin-left: 1rem;
}
.cancel-btn:hover {
  background: #c0392b;
}
</style>