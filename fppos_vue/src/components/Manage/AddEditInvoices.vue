<template>
  <div class="modal-overlay" @mousedown.self="$emit('close')">
    <div class="modal-content">
      <h2>{{ productGroup ? 'Chỉnh sửa nhóm sản phẩm' : 'Tạo nhóm sản phẩm mới' }}</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="name">Tên nhóm</label>
          <input
            id="name"
            v-model="name"
            type="text"
            required
            placeholder="Nhập tên nhóm sản phẩm"
          />
        </div>
        <div class="form-group">
          <label for="description">Mô tả</label>
          <textarea
            id="description"
            v-model="description"
            placeholder="Nhập mô tả (tuỳ chọn)"
          ></textarea>
        </div>
        <div class="form-group">
          <label for="is_active">Kích hoạt</label>
          <select id="is_active" v-model="isActive">
            <option :value="true">Có</option>
            <option :value="false">Không</option>
          </select>
        </div>
        <button type="submit" class="save-btn">
          {{ productGroup ? 'Lưu thay đổi' : 'Tạo mới' }}
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
  name: 'AddEditProductGroup',
  props: {
    productGroup: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'saved'],
  setup(props, { emit }) {
    const { productGroup } = toRefs(props);
    const name = ref(productGroup.value ? productGroup.value.name : '');
    const description = ref(productGroup.value ? productGroup.value.description : '');
    const isActive = ref(productGroup.value && productGroup.value.is_active !== undefined ? productGroup.value.is_active : true);

    watch(productGroup, (newVal) => {
      name.value = newVal ? newVal.name : '';
      description.value = newVal ? newVal.description : '';
      isActive.value = newVal && newVal.is_active !== undefined ? newVal.is_active : true;
    });

    async function handleSubmit() {

        // check if editing or creating
        if (productGroup.value && productGroup.value.id) {
          // Editing existing product group
          const payload = {
            id: productGroup.value.id,
            name: name.value,
            description: description.value,
            is_active: isActive.value
          };

          // send api request to update
          await axios.put(`/productgroups/${productGroup.value.id}/`, payload)
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
              name: name.value,
              description: description.value,
              is_active: isActive.value
            };

            // send api request to create
            await axios.post('/productgroups/', payload)
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
      name,
      description,
      isActive,
      productGroup,
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