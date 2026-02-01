<template>
  <div class="p-2 max-w-7xl mx-auto">
    <!-- Date Selection -->
    <div class="flex items-center gap-4 mb-8 bg-white p-4 rounded-lg shadow-sm border " style="display: flex; flex-direction: row ; justify-content: center; align-items: center; ">
      <div class="font-medium text-gray-700 pr-3"><b> Chốt Tiền </b>từ ngày <b>{{ previousDate }}</b> đến ngày</div>
      <input 
        type="date" 
        id="date" 
        v-model="selectedDate" 
        @change="fetchData"
        @click="$event.target.showPicker()"
        :max="maxDate"
        :min="minDate"
        class="border border-gray-300 rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
        style="background-color: white; color: black; border: 1px solid gray;"
      />
      <div class="text-gray-700 pl-3">Đã chốt lúc: {{ createdAt }}</div>
      <button 
        @click="fetchData" 
        class="btn ml-2"
      >
        Refresh
      </button>
    </div>

    <div v-if="loading" class="text-center py-10 text-gray-500">Loading data...</div>

    <div v-else-if="balanceData" class="space-y-6">
      
      <!-- Summary Cards -->
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <!-- Beginning Balance -->
        <div class="bg-white p-2 rounded-lg shadow border border-gray-200">
          <h3 class="text-gray-500 text-sm font-medium uppercase">Số dư đầu kỳ</h3>
          <p class="text-2xl font-bold text-gray-800 mt-2">{{ formatCurrency(beginningBalance) }}</p>
          <p class="text-xs text-gray-400 mt-1" v-if="balanceData.previous_date">
            From {{ balanceData.previous_date.date }}
          </p>
        </div>
        
        <!-- Total In (DR) -->
        <div class="bg-white p-2 rounded-lg shadow border border-gray-200">
          <h3 class="text-gray-500 text-sm font-medium uppercase">Tổng Thu (DR)</h3>
          <p class="text-2xl font-bold text-green-600 mt-2">+{{ formatCurrency(totalIn) }}</p>
        </div>

        <!-- Total Out (CR) -->
        <div class="bg-white p-2 rounded-lg shadow border border-gray-200">
          <h3 class="text-gray-500 text-sm font-medium uppercase">Tổng Chi (CR)</h3>
          <p class="text-2xl font-bold text-red-600 mt-2">-{{ formatCurrency(totalOut) }}</p>
        </div>

        <!-- Expected Ending -->
        <div class="bg-blue-50 p-2 rounded-lg shadow border border-blue-200">
          <h3 class="text-blue-800 text-sm font-medium uppercase">Số dư cuối kỳ</h3>
          <p class="text-2xl font-bold text-blue-700 mt-2">{{ formatCurrency(expectedEnding) }}</p>
        </div>

        <!-- finalised Ending -->
        <div class="bg-white p-2 rounded-lg shadow border border-gray-200">
          <h3 class="text-blue-800 text-sm font-medium uppercase">Số dư đã chốt</h3>
          <p class="text-2xl font-bold text-blue-700 mt-2">{{ balanceData.created_at ? formatCurrency(finalisedEnding) : '...' }}</p>
        </div>

         <!-- finalised Ending -->
        <div class="bg-white p-2 rounded-lg shadow border border-gray-200">
          <h3 class="text-blue-800 text-sm font-medium uppercase">Chênh lệch</h3>
          <p class="text-2xl font-bold text-blue-700 mt-2">{{ formatCurrency(difference) }}</p>
        </div>

        <!-- Finalize Input Section -->
        <div class="bg-white p-2 rounded-lg shadow border border-gray-200">
            <div class="">
                <label class="block text-sm font-medium text-gray-700 mb-2">Tiền mặt thực tế</label>
                <input 
                style="background-color: white; color: black; border: 1px solid gray; width: 100%;"
                type="text" 
                v-model="actualCashInHandDisplay" 
                class=" rounded px-3 py-2 "
                @focus="$event.target.select()"
                />
            </div>
        </div>
        <div class=" p-2 rounded-lg shadow border border-gray-200">
            <button 
              @click="saveBalance" 
              :disabled="saving"
              class="btn btn-secondary"
            >
              {{ saving ? 'Đang lưu...' : 'Lưu số dư' }}
            </button>
          </div>
      </div>

      <!-- Transactions Table -->
      <div class="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
        <div class="" style="display: flex; flex-direction: row ; justify-content: space-between; align-items: center; padding: 0.5rem;">
          <h2 class="text-lg font-semibold text-gray-800"> <b>Giao dịch</b></h2>
          <button @click="exportToCSV" class="btn btn-secondary" style="font-size: 0.8rem;">Export CSV</button>
          
        </div>
        <v-data-table
          :headers="headers"
          :items="transactions"
          class="elevation-1"
          density="compact"
          :items-per-page="-1"
          hide-default-footer
          height="calc(100vh - 22rem)"
          style="background-color: white; color: black;"
          fixed-header
        >
          <template v-slot:item.transaction_type_name="{ item }">
            {{ item.transaction_type_name }}
            <span 
              class="ml-2 px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
              :class="item.debit_or_credit === 'DR' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
            >
              {{ item.debit_or_credit }}
            </span>
          </template>
          <template v-slot:item.amount="{ item }">
            <span :class="item.debit_or_credit === 'DR' ? 'text-green-600 font-medium' : 'text-red-600 font-medium'">
              {{ formatCurrency(item.amount) }}
            </span>
          </template>
          <template v-slot:no-data>
            <div class="px-6 py-8 text-center text-sm text-gray-500" style="background-color: white; color: black;">Không tìm thấy giao dịch cho ngày này.</div>
          </template>
        </v-data-table>
      </div>

      

    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'DateEndCashBalance',
  props: {
    d_edit_days: {
      type: Number,
      default: 3,
    },
  },
  data(props) {
    return {
      d_edit_days: props.d_edit_days,
      selectedDate: this.getLocalDateISO(new Date(Date.now())),
      loading: false,
      saving: false,
      balanceData: null,
      actualCashInHand: 0,
      headers: [
        { title: 'ID', key: 'id', align: 'start', headerProps: { class: 'my-custom-header-class' }, cellProps: { class: 'text-left back-ground-white' } },
        { title: 'Loại', key: 'transaction_type_name', align: 'start', headerProps: { class: 'my-custom-header-class' }, cellProps: { class: 'text-left back-ground-white' } },
        { title: 'Mô tả', key: 'description', align: 'start', headerProps: { class: 'my-custom-header-class' }, cellProps: { class: 'text-left back-ground-white' } },
        { title: 'Mã hóa đơn', key: 'invoice_code', align: 'start', headerProps: { class: 'my-custom-header-class' }, cellProps: { class: 'text-left back-ground-white' } },
        { title: 'Tài khoản', key: 'bank_account_name', align: 'start', headerProps: { class: 'my-custom-header-class' }, cellProps: { class: 'text-left back-ground-white' } },
        { title: 'Số tiền', key: 'amount', align: 'end', headerProps: { class: 'my-custom-header-class pr-3' }, cellProps: { class: 'text-right pr-3 back-ground-white' } },
        
      ],
    };
  },
  computed: {
    maxDate() {
      return this.getLocalDateISO(new Date());
    },
    minDate() {
      if (this.$store.getters.userAdmin || this.$store.getters.userSuperadmin) {
        return ''; // No minimum date for admins
      }
      const today = new Date();
      const minDay = new Date();
      minDay.setDate(today.getDate() - (this.d_edit_days || 3));
      return this.getLocalDateISO(minDay);
    },

    transactions() {
      return (this.balanceData?.transactions || []).filter(t => t.account === 1);
    },
    beginningBalance() {
      if (this.balanceData?.previous_date) {
        return parseFloat(this.balanceData.previous_date.cash_in_hand) || 0;
      }
      return 0;
    },
    totalIn() {
      return this.transactions
        .filter(t => t.debit_or_credit === 'DR')
        .reduce((sum, t) => sum + parseFloat(t.amount), 0);
    },
    totalOut() {
      return this.transactions
        .filter(t => t.debit_or_credit === 'CR')
        .reduce((sum, t) => sum + parseFloat(t.amount), 0);
    },
    expectedEnding() {
      return this.beginningBalance + this.totalIn - this.totalOut;
    },
    finalisedEnding() {
      return this.balanceData ? parseFloat(this.balanceData.cash_in_hand) : '';
    }
    ,
    difference() {
      return this.finalisedEnding - this.expectedEnding;
    },
    previousDate() {
      return this.balanceData?.previous_date?.date || '...';
    },
    createdAt() {
      return this.balanceData?.created_at ? this.balanceData.created_at.slice(0, 16).replace('T', ' ') : 'chưa chốt';
    },
    actualCashInHandDisplay: {
      get() {
        return this.actualCashInHand.toLocaleString('en-US');
      },
      set(value) {
        const num = parseFloat(value.replace(/,/g, ''));
        this.actualCashInHand = isNaN(num) ? 0 : num;
      }
    }
  },
  mounted() {
    this.fetchData();
  },
  methods: {
    
    getLocalDateISO(date) {
      return new Date(date.getTime() - (date.getTimezoneOffset() * 60000)).toISOString().slice(0, 10);
    },

    async fetchData() {
      if (!this.selectedDate) return;
      
      this.loading = true;
      try {
        const response = await axios.get(`/dateendcashbalances/?date=${this.selectedDate}&dateend=true`);
        
        // API returns a list, we take the first item
        if (Array.isArray(response.data) && response.data.length > 0) {
          this.balanceData = response.data[0];
          
          // If the record exists (has an ID), use its saved cash_in_hand
          // Otherwise, default to the expected ending balance
          if (this.balanceData.id) {
            this.actualCashInHand = parseFloat(this.balanceData.cash_in_hand);
          } else {
            // Use nextTick to ensure computed properties are ready if needed, 
            // though here we can just use the logic directly or wait.
            this.$nextTick(() => {
               this.actualCashInHand = this.expectedEnding;
            });
          }
        } else {
          this.balanceData = null;
        }
      } catch (error) {
        console.error('Error fetching balance data:', error);
        alert('Failed to load data.');
      } finally {
        this.loading = false;
      }
    },
    async saveBalance() {
      this.saving = true;
      try {
        const payload = {
          date: this.selectedDate,
          cash_in_hand: this.actualCashInHand
        };

        if (this.balanceData.id) {
          // Update existing record
          await axios.put(`/dateendcashbalances/${this.balanceData.id}/`, payload);
        } else {
          // Create new record
          await axios.post('/dateendcashbalances/', payload);
        }
        
        alert('Balance saved successfully!');
        await this.fetchData(); // Reload to get updated state (e.g. ID)
      } catch (error) {
        console.error('Error saving balance:', error);
        alert('Failed to save balance.');
      } finally {
        this.saving = false;
      }
    },
    formatCurrency(value) {
      return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(value);
    },
    exportToCSV() {
      if (!this.balanceData || !this.balanceData.transactions || this.balanceData.transactions.length === 0) {
        alert("Không có dữ liệu để xuất.");
        return;
      }
      
      const data = this.balanceData.transactions;
      const headers = ['ID', 'Ngày', 'Loại', 'Mô tả', 'Mã hóa đơn', 'Tài khoản', 'Số tiền', 'Thu/Chi'];
      
      const csvContent = [
        headers.join(','),
        ...data.map(t => {
          return [
            t.id,
            t.date,
            `"${t.transaction_type_name || ''}"`,
            `"${(t.description || '').replace(/"/g, '""')}"`,
            `"${t.invoice_code || ''}"`,
            `"${t.bank_account_name || ''}"`,
            t.amount,
            t.debit_or_credit
          ].join(',');
        })
      ].join('\n');
      
      const blob = new Blob(["\uFEFF" + csvContent], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      if (link.download !== undefined) {
        const url = URL.createObjectURL(blob);
        link.setAttribute('href', url);
        link.setAttribute('download', `transactions_${this.selectedDate}.csv`);
        link.style.visibility = 'hidden';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    }
  }
};
</script>

<style lang="scss" scoped>
    .max-w-7xl {
      max-width: 90rem;
      width: 75vw;
    }

::v-deep .back-ground-white {
  background-color: white;
  color: black;
}

::v-deep .text-red-600 {
  color: red;
}

::v-deep .text-green-600 {
  color: green;
}

::v-deep .table__wrapper{
    background-color: white;
    color: black
}

.btn {
  padding: 8px 16px;
  border-radius: 3px;
  cursor: pointer;
  font-weight: 500;
  border: 1px solid transparent;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 0.0892857143em;
  background-color: #7dabe7;
}


</style>