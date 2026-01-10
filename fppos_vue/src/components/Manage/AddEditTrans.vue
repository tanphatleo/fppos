<template>
  <div class="modal-overlay" @mousedown.self="$emit('close')">
    <div class="modal-content">
      <h2>{{ item ? 'Chỉnh sửa cấu hình' : 'Tạo cấu hình mới' }}</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="key">Key</label>
          <input
            id="key"
            v-model="key"
            type="text"
            required
            placeholder="Nhập key (ví dụ: branch_name)"
          />
        </div>
        <div class="form-group">
          <label for="value">Value</label>
          <input
            id="value"
            v-model="value"
            type="text"
            required
            placeholder='Nhập value (ví dụ: "Chi nhánh SG")'
          />
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
  name: 'AddEditSettings',
  props: {
    item: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'saved'],
  setup(props, { emit }) {
    const { item } = toRefs(props);
    const key = ref(item.value ? item.value.key : '');
    const value = ref(item.value ? item.value.value : '');
    const isActive = ref(item.value && item.value.is_active !== undefined ? item.value.is_active : true);

    watch(item, (newVal) => {
      key.value = newVal ? newVal.key : '';
      value.value = newVal ? newVal.value : '';
      isActive.value = newVal && newVal.is_active !== undefined ? newVal.is_active : true;
    });

    async function handleSubmit() {

        // check if editing or creating
        if (item.value && item.value.id) {
          // Editing existing product group
          const payload = {
            id: item.value.id,
            key: key.value,
            value: value.value,
            is_active: isActive.value
          };

          // send api request to update
          await axios.put(`/logicconfigs/${item.value.id}/`, payload)
            .then(response => {
              console.log("Product group updated:", response.data);
            })
            .catch(error => {
              console.error("Error updating product group:", error);
            });

          emit('saved', payload);
          return;
        } else {
          // Creating new product group
            const payload = {
              key: key.value,
              value: value.value,
              is_active: isActive.value
            };

            // send api request to create
            await axios.post('/logicconfigs/', payload)
              .then(response => {
                console.log("Product group created:", response.data);
              })
              .catch(error => {
                console.error("Error creating product group:", error);
              });
        emit('saved', payload);
      }
    };

    return {
      key,
      value,
      isActive,
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