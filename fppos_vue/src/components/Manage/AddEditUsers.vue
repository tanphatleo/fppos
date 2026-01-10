<template>
  <div class="modal-overlay" @mousedown.self="$emit('close')">
    <div class="modal-content">
      <h2>{{ !!item.username ? 'Cập nhật người dùng' : 'Thêm người dùng mới' }}</h2>
      <form @submit.prevent="handleSubmit">
        
        <div class="form-group">
          <label for="username">Tên đăng nhập <span class="required">*</span></label>
          <input
            id="username"
            v-model="form.username"
            type="text"
            required
            :disabled="!!item.username" 
            placeholder="Ví dụ: admin"
          />
          </div>

        <div class="form-group">
          <label for="password">Mật khẩu <span v-if="!item" class="required">*</span></label>
          <input
            id="password"
            v-model="form.password"
            type="password"
            :required="!item"
            placeholder="Nhập mật khẩu"
            autocomplete="new-password"
          />
          <small v-if="!!item.username" style="color: #666; font-size: 0.8rem;">Để trống nếu không muốn đổi mật khẩu</small>
        </div>

        <div class="name-row">
            <div class="form-group half">
            <label for="firstName">Họ</label>
            <input
                id="firstName"
                v-model="form.last_name"
                type="text"
                placeholder="Họ"
            />
            </div>
            <div class="form-group half">
            <label for="lastName">Tên</label>
            <input
                id="lastName"
                v-model="form.first_name"
                type="text"
                placeholder="Tên"
            />
            </div>
        </div>

        <div class="form-group">
          <label>Nhóm quyền</label>
          <div class="checkbox-container">
            <div v-for="group in userGroups" :key="group.id" class="checkbox-item">
              <label :for="'group-' + group.id" class="checkbox-label">
                <input 
                  type="checkbox" 
                  :id="'group-' + group.id" 
                  :value="group.id" 
                  v-model="form.groups"
                >
                {{ group.name }}
              </label>
            </div>
          </div>
          <div v-if="userGroups.length === 0" class="empty-text">Chưa có nhóm nào.</div>
        </div>

        <div class="form-group checkbox-item">
             <label class="checkbox-label">
                <input type="checkbox" v-model="form.is_active">
                Kích hoạt (Active)
             </label>
        </div>

        <div class="actions">
            <button type="submit" class="save-btn">
            {{ item ? 'Lưu thay đổi' : 'Tạo mới' }}
            </button>
            <button type="button" class="cancel-btn" @click="$emit('close')">Hủy</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { reactive, watch, toRefs, onMounted } from 'vue';
import axios from 'axios';

export default {
  name: 'AddEditUser',
  props: {
    item: {
      type: Object,
      default: null
    }, 
    userGroups: {
      type: Array,
      default: () => [] // Expects: [{"id":1,"name":"admin"}, ...]
    } 
  },
  emits: ['close', 'saved'],
  setup(props, { emit }) {
    const { item } = toRefs(props);

    // Reactive form state
    const form = reactive({
        username: '',
        first_name: '',
        last_name: '',
        email: '',
        password: '',
        groups: [], // Array of IDs [1, 2]
        is_active: true
    });

    // Helper to reset or fill form
    const initForm = (data) => {
        if (data) {
            form.username = data.username || '';
            form.first_name = data.first_name || '';
            form.last_name = data.last_name || '';
            form.email = data.email || '';
            form.groups = data.groups || []; // Takes the array of IDs from props
            form.is_active = data.is_active !== undefined ? data.is_active : true;
            form.password = ''; // Don't pre-fill password hash
        } else {
            // Reset for create mode
            form.username = '';
            form.first_name = '';
            form.last_name = '';
            form.email = '';
            form.groups = [];
            form.is_active = true;
            form.password = '';
        }
    };

    // Watch for changes in prop 'item' to update form
    watch(item, (newVal) => {
        initForm(newVal);
    });

    // Initialize on mount
    onMounted(() => {
        initForm(item.value);
    });

    async function handleSubmit() {
        const payload = {
            username: form.username,
            first_name: form.first_name,
            last_name: form.last_name,
            email: form.email,
            groups: form.groups,
            is_active: form.is_active
        };

        // Only include password if it was typed
        if (form.password) {
            payload.password = form.password;
        }

        try {
            if (item.value && item.value.id) {
                // --- UPDATE ---
                // Depending on backend, might need to remove password if empty
                const response = await axios.put(`/users/${item.value.id}/`, payload);
                console.log("User updated:", response.data);
                emit('saved', response.data);
            } else {
                // --- CREATE ---
                const response = await axios.post('/users/', payload);
                console.log("User created:", response.data);
                emit('saved', response.data);
            }
        } catch (error) {
            console.error("Error saving user:", error.response ? error.response.data : error);
            alert("Có lỗi xảy ra: " + (error.response?.data?.detail || "Vui lòng kiểm tra lại thông tin"));
        }
    }

    return {
      form,
      item, // return item to check if editing in template
      handleSubmit
    };
  }
};
</script>

<style scoped>
/* Base Reset */
* {
    box-sizing: border-box;
}

textarea, input, select {
  background-color: #f9f9f9;
  color: black;
} 

.required {
    color: red;
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
  padding: 1.5rem;
  width: 500px; /* Wider for user form */
  max-width: 95vw;
  max-height: 90vh;
  overflow-y: auto; /* Handle scrolling on small screens */
  display: flex;
  flex-direction: column;
}

h2 {
    margin-top: 0;
    text-align: center;
    color: #333;
}

/* Form Layout */
.form-group {
  margin-bottom: 1rem;
  width: 100%;
}

.name-row {
    display: flex;
    gap: 10px;
}

.half {
    flex: 1;
}

label {
  display: block;
  margin-bottom: 0.3rem;
  font-weight: bold;
  font-size: 0.9rem;
  color: #333;
}

input[type="text"],
input[type="password"],
input[type="email"],
textarea,
select {
  width: 100%;
  padding: 0.6rem;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 1rem;
}

input:disabled {
    background-color: #e9ecef;
    cursor: not-allowed;
}

/* Checkbox Styling */
.checkbox-container {
    border: 1px solid #ccc;
    padding: 10px;
    border-radius: 4px;
    background: #f9f9f9;
    max-height: 150px;
    overflow-y: auto;
}

.checkbox-item {
    margin-bottom: 5px;
}

/* Make checkbox label inline and clickable */
.checkbox-label {
    font-weight: normal;
    display: flex;
    align-items: center;
    cursor: pointer;
    margin-bottom: 0;
}

.checkbox-label input {
    width: auto;
    margin-right: 8px;
}

.empty-text {
    font-size: 0.85rem;
    color: #777;
    font-style: italic;
}

/* Buttons */
.actions {
    display: flex;
    justify-content: flex-end;
    margin-top: 1.5rem;
    gap: 10px;
}

.save-btn {
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
  padding: 0.5rem 1.5rem;
  background: #e74c3c;
  color: #fff;
  border: none;
  border-radius: 5px;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}
.cancel-btn:hover {
  background: #c0392b;
}
</style>