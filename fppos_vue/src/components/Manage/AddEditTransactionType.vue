<template>
  <div class="modal-overlay" @mousedown.self="$emit('close')">
    <div class="modal-content">
      <h2>{{ item ? 'Chỉnh sửa loại giao dịch' : 'Tạo loại giao dịch mới' }}</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="name">Tên loại giao dịch</label>
          <input
            id="name"
            v-model="name"
            type="text"
            required
            placeholder="Nhập tên loại giao dịch"
          />
        </div>
        <div class="form-group">
          <label for="description">Mô tả</label>
          <input
            id="description"
            v-model="description"
            type="text"
            placeholder="Nhập mô tả (tùy chọn)"
          />
        </div>
        <div class="form-group">
          <label for="transaction_type">Loại giao dịch</label>
          <select id="transaction_type" v-model="transaction_type">
            <option :value="DR">Thu</option>
            <option :value="CR">Chi</option>
          </select>
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
  name: 'AddEditTransactionType',
  props: {
    item: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'saved'],
  setup(props, { emit }) {
    const { item } = toRefs(props);
    const name = ref(item.value ? item.value.name : '');
    const transaction_type = ref(item.value ? item.value.transaction_type : 'DR');
    const description = ref(item.value ? item.value.description : '');
    const is_active = ref(item.value && item.value.is_active !== undefined ? item.value.is_active : true);

    watch(item, (newVal) => {
      name.value = newVal ? newVal.name : '';
      description.value = newVal ? newVal.description : '';
      is_active.value = newVal && newVal.is_active !== undefined ? newVal.is_active : true;
    });

    async function handleSubmit() {

        // check if editing or creating
        if (item.value && item.value.id) {
          // Editing existing transaction type
          const payload = {
            id: item.value.id,
            name: name.value,
            description: description.value,
            is_active: is_active.value
          };

          // send api request to update
          await axios.put(`/transactiontypes/${item.value.id}/`, payload)
            .then(response => {
              console.log("TransactionType updated:", response.data);
            })
            .catch(error => {
              console.error("Error updating transaction type:", error);
            });

          emit('saved', payload);
          return;
        } else {
          // Creating new transaction type
          const payload = {
            name: name.value,
            description: description.value,
            transaction_type: transaction_type.value,
            is_active: is_active.value
          };

          // send api request to create
          await axios.post('/transactiontypes/', payload)
            .then(response => {
              console.log("TransactionType created:", response.data);
            })
            .catch(error => {
              console.error("Error creating transaction type:", error);
              window.alert("Error creating transaction type:", error);
            });
          emit('saved', payload);
        }
      };

      return {
        name,
        description,
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