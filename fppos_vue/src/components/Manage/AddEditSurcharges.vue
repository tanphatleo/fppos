<template>
  <div class="modal-overlay" @mousedown.self="$emit('close')">
    <div class="modal-content">
      <h2>{{ surcharge ? 'Chỉnh sửa phụ phí' : 'Tạo phụ phí mới' }}</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="code">Mã phụ phí</label>
          <input
            id="code"
            v-model="code"
            type="text"
            maxlength="10"
            placeholder="Nhập mã phụ phí (tùy chọn)"
          />
        </div>
        <div class="form-group">
          <label for="description">Mô tả</label>
          <input
            id="description"
            v-model="description"
            type="text"
            maxlength="100"
            required
            placeholder="Nhập mô tả phụ phí"
          />
        </div>
        <div class="form-group">
          <label for="amount">Số tiền</label>
          <input
            id="amount"
            v-model.number="amount"
            type="number"
            min="0"
            required
            placeholder="Nhập số tiền phụ phí"
          />
        </div>
        <div class="form-group">
          <label for="is_active">Kích hoạt</label>
          <select id="is_active" v-model="isActive">
            <option :value="true">Có</option>
            <option :value="false">Không</option>
          </select>
        </div>
        <button type="submit" class="save-btn">
          {{ surcharge ? 'Lưu thay đổi' : 'Tạo mới' }}
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
  name: 'AddEditSurcharge',
  props: {
    surcharge: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'saved'],
  setup(props, { emit }) {
    const { surcharge } = toRefs(props);
    const code = ref(surcharge.value ? surcharge.value.code : '');
    const description = ref(surcharge.value ? surcharge.value.description : '');
    const amount = ref(surcharge.value ? surcharge.value.amount : 0);
    const isActive = ref(surcharge.value && surcharge.value.is_active !== undefined ? surcharge.value.is_active : true);

    watch(surcharge, (newVal) => {
      code.value = newVal ? newVal.code : '';
      description.value = newVal ? newVal.description : '';
      amount.value = newVal ? newVal.amount : 0;
      isActive.value = newVal && newVal.is_active !== undefined ? newVal.is_active : true;
    });

    async function handleSubmit() {
      const payload = {
        code: code.value,
        description: description.value,
        amount: amount.value,
        is_active: isActive.value
      };
      if (surcharge.value && surcharge.value.id) {
        // Editing existing surcharge
        payload.id = surcharge.value.id;
        await axios.put(`/surcharges/${surcharge.value.id}/`, payload)
          .then(response => {
            console.log("Surcharge updated:", response.data);
          })
          .catch(error => {
            console.error("Error updating surcharge:", error);
          });
        emit('saved', payload);
      } else {
        // Creating new surcharge
        await axios.post('/surcharges/', payload)
          .then(response => {
            console.log("Surcharge created:", response.data);
          })
          .catch(error => {
            console.error("Error creating surcharge:", error);
          });
        emit('saved', payload);
      }
    }

    return {
      code,
      description,
      amount,
      isActive,
      surcharge,
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