<template>
  <div class="modal-overlay" @mousedown.self="$emit('close')">
    <div class="modal-content">
      <h2>{{ item ? 'Edit Transaction' : 'Add Transaction' }}</h2>
      <form @submit.prevent="handleSubmit">
        <div class="form-group">
          <label for="type">Transaction type</label>
          <select id="type" v-model="type" required>
            <option value="Credit">Credit</option>
            <option value="Debit">Debit</option>
          </select>
        </div>
        <div class="form-group">
          <label for="amount">Amount</label>
          <input id="amount" v-model="amount" type="number" min="0" step="0.01" required />
        </div>
        <div class="form-group">
          <label for="description">Description</label>
          <textarea id="description" v-model="description" rows="3"></textarea>
        </div>
        <div class="form-group" style="display: flex; align-items: center;">
          <label for="is_active" style="margin-bottom: 0; min-width: 6rem;">Is active</label>
          <input id="is_active" v-model="isActive" type="checkbox" style="width: auto; margin-left: 0.5rem;" />
        </div>
        <div style="display: flex; justify-content: flex-end; width: 100%;">
          <button type="submit" class="save-btn">POST</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, watch, toRefs } from 'vue';
import axios from 'axios';


export default {
  name: 'AddEditTrans',
  props: {
    item: {
      type: Object,
      default: null
    },
    transactionTypes: {
      type: Array,
      default: () => []
    }
  },
  emits: ['close', 'saved'],
  setup(props, { emit }) {
    const { item } = toRefs(props);
    const type = ref(item.value ? item.value.type : 'Credit');
    const amount = ref(item.value ? item.value.amount : '');
    const description = ref(item.value ? item.value.description : '');
    const isActive = ref(item.value && item.value.is_active !== undefined ? item.value.is_active : false);

    watch(item, (newVal) => {
      type.value = newVal ? newVal.type : 'Credit';
      amount.value = newVal ? newVal.amount : '';
      description.value = newVal ? newVal.description : '';
      isActive.value = newVal && newVal.is_active !== undefined ? newVal.is_active : false;
    });

    async function handleSubmit() {
      const payload = {
        type: type.value,
        amount: amount.value,
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
          });
      } else {
        await axios.post('/transactions/', payload)
          .then(response => {
            emit('saved', response.data);
          })
          .catch(error => {
            console.error('Error creating transaction:', error);
          });
      }
    }

    return {
      type,
      amount,
      description,
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