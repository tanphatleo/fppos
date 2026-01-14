<template>
  <div class="work-area">
    <div class="top-area">
      <div class="page-name-area">Chốt Kho</div>
      <div class="action-area">
        <div class="page-actions">
          <input type="date" v-model="chosenDate" class="date-picker" />
          <button @click="copyClosingToActual" class="btn btn-primary" style="margin-left: 1rem;">
            Copy Tồn cuối -> Thực tế
          </button>
        </div>
      </div>
    </div>
    <div class="bottom-area">
      <div class="data-area">
        

          <v-data-table
            :headers="headers"
            :items="tableRows"
            class="elevation-1"
            fixed-header
            :items-per-page="-1"
            height="calc(100vh - 8rem)"
            style="background-color: white;"
            density="compact"
            hide-default-footer
          >
            <template v-slot:item.diff="{ item }">
              <span :class="{'text-red': item.diff !== 0}">{{ item.diff }}</span>
            </template>
            <template v-slot:item.closing="{ item }">
              <span class="font-bold">{{ item.closing }}</span>
            </template>
            <template v-slot:item.actual="{ item }">
              <input type="number" v-model.number="item.actual" class="qty-input" @input="onDiffChange(item)" @focus="$event.target.select()">
            </template>
          </v-data-table>

        
      </div>
      <div class="info-area pl-3">
        <div class="filters">
          <input type="text" v-model="searchQuery" placeholder="Tìm kiếm mã hàng, tên hàng" />
          <input type="text" v-model="searchQueryInvoice" placeholder="Tìm kiếm hóa đơn" />
          <button @click="exportToExcel" class="btn btn-secondary">Export Excel</button>
        </div>
        <div style="padding: 0.5rem; text-align: left;">
          Lưu ý: Hiển thị tối đa 10 hóa đơn gần nhất theo ngày chọn, xuất excel sẽ xuất toàn bộ hóa đơn.
        </div>
        <div class="data-table-holder">
          <v-data-table
            :headers="infoHeaders"
            :items="infoTableRows"
            class="elevation-1 bordered-table"
            fixed-header
            :items-per-page="-1"
            style="background-color: white; width: max-content; min-width: 100%;"
            density="compact"
            height="65vh"
            hide-default-footer
          >
          </v-data-table>
        </div>
        
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick, onBeforeUnmount, watch} from 'vue';
import axios from 'axios';
import * as XLSX from 'xlsx';
import { useStore } from 'vuex';

export default {
  name: 'DateEndInventory',
  components: {
  },
  setup() {
    const store = useStore();

    const getLocalDateISO = (date) => {
      return new Date(date.getTime() - (date.getTimezoneOffset() * 60000)).toISOString().slice(0, 10);
    };

    const DateEndInventorys = ref([]);
    // default to today -1 day
    
    const chosenDate = ref(getLocalDateISO(new Date(Date.now() - 86400000)));
    const searchQuery = ref('');
    const searchQueryInvoice = ref('');

    const products = ref([]);

    const fetchProducts = async () => {
      try {
        const response = await axios.get('/products/');
        products.value = response.data;
      } catch (error) {
        console.error('Error fetching products:', error);
      }
    };

    const fetchDateEndInventorys = async () => {
      store.commit('setLoading', true);
      try {
        const response = await axios.get('/dateendinventories/', {
          params: {
            dayend: true,
            date: chosenDate.value
          }
        });
        DateEndInventorys.value = response.data;
      } catch (error) {
        console.error('Error fetching date end inventories:', error);
      }
      store.commit('setLoading', false);
    };

    const headers = [
      { title: 'Nhóm hàng', key: 'group', headerProps: { class: 'my-custom-header-class' } , align: 'start' , cellProps: { class: 'text-left back-ground-white' } },
      { title: 'Mã hàng', key: 'code', headerProps: { class: 'my-custom-header-class' } , align: 'start' , cellProps: { class: 'text-left back-ground-white' } },
      { title: 'Tên hàng', key: 'name', headerProps: { class: 'my-custom-header-class' } , align: 'start' , cellProps: { class: 'text-left back-ground-white' } },
      { title: 'Tồn đầu', key: 'prev', align: 'end', headerProps: { class: 'my-custom-header-class ', style: 'text-align: right;' } , align: 'end', cellProps: { class: 'text-right back-ground-white' }},
      { title: 'Nhập', key: 'purchaseSum', align: 'end', headerProps: { class: 'my-custom-header-class ', style: 'text-align: right;' } , align: 'end', cellProps: { class: 'text-right back-ground-white ' } },
      { title: 'Xuất', key: 'invoiceSum', align: 'end', headerProps: { class: 'my-custom-header-class ', style: 'text-align: right;' } , align: 'end', cellProps: { class: 'text-right  back-ground-white' } },
      { title: 'Đổi hàng', key: 'changeSum', align: 'end', headerProps: { class: 'my-custom-header-class ', style: 'text-align: right;' } , align: 'end', cellProps: { class: 'text-right  back-ground-white' } },
      { title: 'Tồn cuối (LT)', key: 'closing', align: 'end', headerProps: { class: 'my-custom-header-class ' , style: 'text-align: right;' } , align: 'end', cellProps: { class: 'text-right  back-ground-white' } },
      { title: 'Thực tế', key: 'actual', align: 'end', headerProps: { class: 'my-custom-header-class ' , style: 'text-align: right;'} , align: 'end', cellProps: { class: 'text-right back-ground-white ' } },
      { title: 'Chênh lệch', key: 'diff', align: 'end', headerProps: { class: 'my-custom-header-class  pr-3' , style: 'text-align: right;' } , align: 'end', cellProps: { class: 'text-right  back-ground-white pr-3' } },
    ];

    const tableRows = ref([]);
    const updateTableRows = () => {
      if (!DateEndInventorys.value || DateEndInventorys.value.length === 0) {
        tableRows.value = [];
        return;
      }
      const data = DateEndInventorys.value[0];
      
      const prevItems = data.previous_date?.items || [];
      const currentItems = data.items || [];
      const purchases = data.purchases || [];
      const invoices = data.invoices || [];

      const allCodes = new Set();

      const collectCodes = (items) => {
        if (Array.isArray(items)) {
          items.forEach(i => {
            if (i.code) {
              allCodes.add(i.code);
            }
          });
        }
      };

      collectCodes(prevItems);
      collectCodes(currentItems);
      purchases.forEach(p => collectCodes(p.items));
      invoices.forEach(i => {
        collectCodes(i.expanded_items);
        collectCodes(i.changes_items);
      });

      const productInfoMap = {};
      products.value.forEach(p => {
        productInfoMap[p.code] = { name: p.name, group: p.productGroup };
      });

      const rows = [];
      allCodes.forEach(code => {
        const info = productInfoMap[code] || {};
        const row = {
          code: code,
          name: info.name || '',
          group: info.group || '',
          prev: 0,
          purchaseSum: 0,
          invoiceSum: 0,
          changeSum: 0,
          closing: 0,
          actual: 0,
          diff: 0
        };

        // Previous Quantity
        const prevItem = prevItems.find(i => i.code === code);
        row.prev = prevItem ? (Number(prevItem.quantity) || 0) : 0;

        // Purchases
        let purchaseSum = 0;
        purchases.forEach(p => {
          const pItem = p.items ? p.items.find(i => i.code === code) : null;
          const qty = pItem ? (Number(pItem.quantity) || 0) : 0;
          purchaseSum += qty;
        });
        row.purchaseSum = purchaseSum === 0 ? '' : purchaseSum;

        // Invoices
        let invoiceSum = 0;
        let changeSum = 0;
        invoices.forEach(inv => {
          const invItem = inv.expanded_items ? inv.expanded_items.find(i => i.code === code) : null;
          const qty = invItem ? (Number(invItem.quantity) || 0) : 0;
          invoiceSum += qty;

          if (inv.changes_items && inv.changes_items.length > 0) {
            const changeItem = inv.changes_items.find(i => i.code === code);
            const cQty = changeItem ? (Number(changeItem.quantity) || 0) : 0;
            // Assuming changes also count towards outflow/adjustment in the same direction for simplicity of "sum"
            invoiceSum += cQty; 
            changeSum += cQty; 
          }
        });
        row.invoiceSum = invoiceSum === 0 ? '' : invoiceSum;
        row.changeSum = changeSum === 0 ? '' : changeSum;

        // Closing (Calculated)
        row.closing = row.prev + purchaseSum - invoiceSum;
        row.closing = row.prev + purchaseSum - invoiceSum - changeSum;

        // Actual (Checked)
        const currItem = currentItems.find(i => i.code === code);
        row.actual = currItem ? (Number(currItem.quantity) || 0) : 0;

        // Diff
        row.diff = row.closing - row.actual;

        rows.push(row);
      });

      tableRows.value = rows.sort((a, b) => a.code.localeCompare(b.code));
    };

    const filteredInvoices = computed(() => {
      if (!DateEndInventorys.value || DateEndInventorys.value.length === 0) return [];
      let invoices = DateEndInventorys.value[0].invoices || [];
      if (searchQueryInvoice.value) {
        const lower = searchQueryInvoice.value.toLowerCase();
        invoices = invoices.filter(inv => 
          (inv.code && inv.code.toLowerCase().includes(lower)) ||
          (inv.channel && inv.channel.toLowerCase().includes(lower))
        );
      }
      // return invoices;
      return invoices.slice(0, 10);
    });

    const infoTableRows = computed(() => {
      if (!DateEndInventorys.value || DateEndInventorys.value.length === 0) return [];
      const invoices = filteredInvoices.value;
      
      const productMap = {};

      invoices.forEach(inv => {
        const items = inv.expanded_items || [];
        items.forEach(item => {
          if (item.type === 'combo_item' || item.type === 'normal') {
             if (!productMap[item.code]) {
               const p = products.value.find(prod => prod.code === item.code);
               productMap[item.code] = {
                 code: item.code,
                 name: p ? p.name : '',
               };
             }
             
             const key = `invoice_${inv.id}`;
             productMap[item.code][key] = (productMap[item.code][key] || 0) + (Number(item.quantity) || 0);
          }
        });

        if (inv.changes_items && inv.changes_items.length > 0) {
          inv.changes_items.forEach(item => {
             if (!productMap[item.code]) {
               const p = products.value.find(prod => prod.code === item.code);
               productMap[item.code] = {
                 code: item.code,
                 name: p ? p.name : '',
               };
             }
             const key = `invoice_change_${inv.id}`;
             productMap[item.code][key] = (productMap[item.code][key] || 0) + (Number(item.quantity) || 0);
          });
        }
      });

      let result = Object.values(productMap);
      if (searchQuery.value) {
        const lower = searchQuery.value.toLowerCase();
        result = result.filter(item => 
          (item.code && item.code.toLowerCase().includes(lower)) ||
          (item.name && item.name.toLowerCase().includes(lower))
        );
      }
      return result.sort((a, b) => a.code.localeCompare(b.code));
    });

    const infoHeaders = computed(() => {
      if (!DateEndInventorys.value || DateEndInventorys.value.length === 0) return [];
      const invoices = filteredInvoices.value;
      const visibleRows = infoTableRows.value;
      
      const headers = [
        { title: 'Mã hàng', key: 'code', fixed: true, align: 'start', headerProps: { class: 'my-custom-header-class' }, cellProps: { class: 'text-left back-ground-white' } },
        { title: 'Tên hàng', key: 'name',fixed: true, align: 'start', headerProps: { class: 'my-custom-header-class' , style: 'min-width: 10rem;' }, cellProps: { class: 'text-left back-ground-white' } },
      ];

      invoices.forEach(inv => {
        const invKey = `invoice_${inv.id}`;
        const changeKey = `invoice_change_${inv.id}`;
        
        const hasMainData = searchQuery.value ? visibleRows.some(r => r[invKey]) : true;

        if (hasMainData) {
          headers.push({
            title: inv.code,
            key: invKey,
            align: 'end',
            headerProps: { class: 'my-custom-header-class vertical-header' },
            cellProps: { class: 'text-right back-ground-white pr-2' }
          });
        }

        if (inv.changes_items && inv.changes_items.length > 0) {
          const hasChangeData = searchQuery.value ? visibleRows.some(r => r[changeKey]) : true;
          if (hasChangeData) {
            headers.push({
              title: inv.code + ' (Thay đổi)',
              key: changeKey,
              align: 'end',
              headerProps: { class: 'my-custom-header-class vertical-header' },
              cellProps: { class: 'text-right back-ground-white pr-2' }
            });
          }
        }
      });
      
      return headers;
    });

    const exportToExcel = () => {
      if (!DateEndInventorys.value || DateEndInventorys.value.length === 0) return;
      const invoices = DateEndInventorys.value[0].invoices || [];
      
      const productMap = {};

      invoices.forEach(inv => {
        const items = inv.expanded_items || [];
        items.forEach(item => {
          if (item.type === 'combo_item' || item.type === 'normal') {
             if (!productMap[item.code]) {
               const p = products.value.find(prod => prod.code === item.code);
               productMap[item.code] = {
                 code: item.code,
                 name: p ? p.name : '',
               };
             }
             
             const key = `invoice_${inv.id}`;
             productMap[item.code][key] = (productMap[item.code][key] || 0) + (Number(item.quantity) || 0);
          }
        });

        if (inv.changes_items && inv.changes_items.length > 0) {
          inv.changes_items.forEach(item => {
             if (!productMap[item.code]) {
               const p = products.value.find(prod => prod.code === item.code);
               productMap[item.code] = {
                 code: item.code,
                 name: p ? p.name : '',
               };
             }
             const key = `invoice_change_${inv.id}`;
             productMap[item.code][key] = (productMap[item.code][key] || 0) + (Number(item.quantity) || 0);
          });
        }
      });

      const rows = Object.values(productMap).sort((a, b) => a.code.localeCompare(b.code));

      const headerRow = ['Mã hàng', 'Tên hàng'];
      const keys = ['code', 'name'];

      invoices.forEach(inv => {
        headerRow.push(inv.code);
        keys.push(`invoice_${inv.id}`);

        if (inv.changes_items && inv.changes_items.length > 0) {
           headerRow.push(inv.code + ' (Thay đổi)');
           keys.push(`invoice_change_${inv.id}`);
        }
      });

      const wsData = [headerRow];
      rows.forEach(row => {
        const rowData = keys.map(k => row[k] || '');
        wsData.push(rowData);
      });

      const ws = XLSX.utils.aoa_to_sheet(wsData);
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, "InfoData");
      XLSX.writeFile(wb, `InfoData_${chosenDate.value}.xlsx`);
    };

    watch([DateEndInventorys, products], updateTableRows);

    const onDiffChange = (item) => {
      item.diff = item.closing - item.actual;
    };

    const copyClosingToActual = () => {
      tableRows.value.forEach(row => {
        let val = row.closing;
        if (val < 0) val = 0;
        row.actual = val;
        row.diff = row.closing - row.actual;
      });
    };

    const formatPrice = (value) => {
      const numericValue = Number(value);
      if (isNaN(numericValue)) return '0 ₫';
      return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(numericValue);
    };


    const formatDateTime = (dateString) => { // format YYYY-MM-DD HH:mm:ss
      if (!dateString) return '';
      const date = new Date(dateString);
      
      const year = date.getFullYear();
      const month = String(date.getMonth() + 1).padStart(2, '0');
      const day = String(date.getDate()).padStart(2, '0');
      const hours = String(date.getHours()).padStart(2, '0');
      const minutes = String(date.getMinutes()).padStart(2, '0');
      const seconds = String(date.getSeconds()).padStart(2, '0');

      return `${year}/${month}/${day} ${hours}:${minutes}:${seconds}`;
    };

    onMounted(() => {
      fetchDateEndInventorys();
      fetchProducts();
    });

    watch(chosenDate, fetchDateEndInventorys);

    return {
      getLocalDateISO,
      DateEndInventorys,
      fetchDateEndInventorys,
      chosenDate,
      searchQuery,
      searchQueryInvoice,
      // surcharges,
      formatPrice,
      formatDateTime,
      tableRows,
      headers,
      onDiffChange,
      copyClosingToActual,
      infoHeaders,
      infoTableRows,
      exportToExcel,
    };
  },
};
</script>

<style lang="scss" scoped>
$kv-primary-color: #0070F4;
$border-color: #aaaaaa;
.work-area {
  padding: 1rem;
  width: 100%;
  display: flex;
  flex-direction: column;
  height: 100%;
  box-sizing: border-box;

  .top-area {
    display: flex;
    padding: 0.5rem;
    align-items: center;

    .page-name-area {
      font-size: 1.2rem;
      font-weight: bold;
      margin-right: 1rem;
    }
    .date-picker {
      padding: 5px;
      border: 1px solid $border-color;
      border-radius: 4px;
    }
  }

  .bottom-area {
    display: flex;
    flex: 1;
    overflow: hidden;
  }

  .data-area {
      height: 100%;
      width: 60%;
      overflow: auto;
      background: white;
  }
}

.info-area {
    height: 100%;
    width: 40%;
    overflow: auto;
    background: white;
    border-left: 1px solid #aaaaaa;
}

.page-actions {
  display: flex;
  align-items: center;
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
}

.btn-primary {
  background: $kv-primary-color;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.font-bold {
    font-weight: bold;
}

.text-red {
    color: red;
    font-weight: bold;
}
::v-deep .back-ground-white {
    background-color: white;
    color: black;
}

::v-deep .qty-input {
    width: 100%;
    text-align: right;
    border: 1px solid #ccc;
    border-radius: 4px;
    padding: 4px;
    background-color: white;
    color: black;
    -moz-appearance: textfield;
}

::v-deep .qty-input::-webkit-outer-spin-button,
::v-deep .qty-input::-webkit-inner-spin-button {
    -webkit-appearance: none;
    margin: 0;
}

::v-deep .qty-input:focus {
    outline: 2px solid #0070F4;
    border-color: transparent;
}

::v-deep .vertical-header {
  writing-mode: vertical-lr;
  transform: rotate(180deg);
  max-height: 12rem;
  min-height: 12rem;
  text-align: left;
}

.data-table-holder {
    margin-top: 1rem;
    height: 70vh;
    max-width: 47vw;
    overflow: auto;
}

::v-deep .bordered-table .v-table__wrapper > table {
  border-collapse: collapse;
}
::v-deep .bordered-table th,
::v-deep .bordered-table td {
  border: 1px solid #000000 !important;
}

.filters {
  display: flex;
  flex-direction: row;
  gap: 0.5rem;
  padding: 0.5rem;

  input {
    background-color: white;
    color: black;
    border-radius: 0.3rem;
    width: 100%;
    border: 1px solid #ccc;
    padding: 6px 10px;
    font-size: 1rem;
    transition: border-color 0.2s;
  }

  input:focus {
    border-color: #0070F4;
    outline: none;
  }
}
</style>