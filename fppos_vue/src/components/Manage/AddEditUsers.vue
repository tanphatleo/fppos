<template>
  <div class="modal-overlay" @mousedown.self="$emit('close')">
    <div class="user-window" @click.stop>
      <div class="window-header">
        <span class="window-title">
          <span class="no-select">{{ item && item.id ? 'Cập nhật người dùng' : 'Thêm người dùng mới' }}</span>
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
                  <label for="username">Tên đăng nhập <span class="required">*</span></label>
                  <input id="username" v-model="form.username" type="text" required :disabled="!!item.id" placeholder="Ví dụ: admin" />
                </div>

                <div class="form-group">
                  <label for="password">Mật khẩu <span v-if="!item.id" class="required">*</span></label>
                  <input id="password" v-model="form.password" type="password" :required="!item.id" placeholder="Nhập mật khẩu" autocomplete="new-password" />
                  <small v-if="item.id" class="field-note">Để trống nếu không muốn đổi mật khẩu</small>
                </div>

                <div class="form-group">
                  <label for="lastName">Họ</label>
                  <input id="lastName" v-model="form.last_name" type="text" placeholder="Họ" />
                </div>

                <div class="form-group">
                  <label for="firstName">Tên</label>
                  <input id="firstName" v-model="form.first_name" type="text" placeholder="Tên" />
                </div>
                 <div class="form-group">
                  <label for="email">Email</label>
                  <input id="email" v-model="form.email" type="email" placeholder="Email" />
                </div>
              </div>

              <div class="col-right">
                <div class="form-group-column">
                  <label>Nhóm quyền</label>
                  <div class="checkbox-container">
                    <div v-for="group in userGroups" :key="group.id" class="checkbox-item">
                      <label :for="'group-' + group.id" class="checkbox-label">
                        <input type="checkbox" :id="'group-' + group.id" :value="group.id" v-model="form.groups" />
                        {{ group.name }}
                      </label>
                    </div>
                    <div v-if="userGroups.length === 0" class="empty-text">Chưa có nhóm nào.</div>
                  </div>
                </div>

                <div class="form-group" style="margin-top: 1rem;">
                  <label for="is_active">Kích hoạt</label>
                  <input id="is_active" type="checkbox" v-model="form.is_active" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="window-footer">
          <button type="button" class="btn btn-outline" @click="$emit('close')">Đóng</button>
          <button type="button" class="btn btn-primary" @click="handleSubmit">
            {{ item && item.id ? 'Lưu' : 'Tạo mới' }}
          </button>
        </div>
      </div>
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
            form.first_name = data.first_name || ''; // Note: Django uses first_name for "Tên"
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
            window.alert("Lỗi khi lưu người dùng: " + (error.response && error.response.data ? JSON.stringify(error.response.data) : error.message));
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

input:focus, select:focus, textarea:focus {
  border-color: $kv-primary;
  outline: none;
}

input[type="checkbox"] {
  width: auto;
  flex-grow: 0;
}

input:disabled {
  background-color: #e9ecef;
  cursor: not-allowed;
}

.required {
  color: red;
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
.user-window {
  background: #fff;
  width: 60rem;
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

.window-title { font-weight: bold; font-size: 15px; }
.close-btn { background: none; border: none; color: white; font-size: 20px; cursor: pointer; line-height: 1; }

.tabs-nav { background: #f0f0f0; border-bottom: 1px solid #ddd; padding: 0 10px; }
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

.form-group-column {
  display: flex;
  flex-direction: column;
  margin-bottom: 12px;
}

.form-group label, .form-group-column label {
  width: 9rem;
  color: #333;
  font-weight: 500;
  flex-shrink: 0;
  padding-right: 1em;
  margin-bottom: 0.5rem;
}

.form-group-column label {
  width: auto;
}

.field-note {
  color: #666;
  font-size: 0.8rem;
  margin-top: 4px;
  display: block;
  width: 100%;
  text-align: right;
}

.checkbox-container {
  border: 1px solid #ccc;
  padding: 10px;
  border-radius: 4px;
  background: #f9f9f9;
  max-height: 200px;
  overflow-y: auto;
}

.checkbox-label {
  font-weight: normal;
  display: flex;
  align-items: center;
  cursor: pointer;
  margin-bottom: 8px;
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