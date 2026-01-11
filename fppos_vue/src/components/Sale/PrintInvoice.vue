<template>
  <div class="receipt-container">
    <div class="receipt-body" id="printable-area">
      
      <div class="header">
        <img :src="logoUrl" alt="Fitpack Logo" class="fitpack-logo" />
        <h2> HÓA ĐƠN
          <span> {{ order.code }}</span></h2>
        <span class="date">{{ formatDate(order.date) }}</span>
      </div>

      <div class="divider"></div>

      <div class="customer-info">
        <p><strong>Khách hàng:</strong> {{ order.customer_name + " - " + order.customer_phone_number }}</p>
        <h3>{{ order.delivery_address }}</h3>

        <p v-if="order.note"><strong>Ghi chú:</strong> {{ order.note }}</p>
      </div>

      <div class="divider"></div>

      <table class="items-table">
        <thead style="background-color: white;">
          <tr style="background-color: white;">
            <th class="text-left" style="background-color: white;">Món</th>
            <th class="text-center" style="background-color: white;">SL</th>
            <th class="text-right" style="background-color: white;">Thành tiền</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="item in order.items" :key="item.uuid">
            <tr class="item-row">
              <td class="item-name">
                {{ item.name }}
                <div class="sku">{{ formatCurrency(item.price) }}</div>
              </td>
              <td class="text-center">{{ item.quantity }}</td>
              <td class="text-right">{{ formatCurrency(item.price * item.quantity) }}</td>
            </tr>
          </template>
        </tbody>
      </table>

      <div class="divider"></div>

      <div class="totals">
        <div class="row">
          <span>Tổng tiền hàng:</span>
          <span>{{ formatCurrency(order.total) }}</span>
        </div>

        <div class="row discount" v-if="Number(order.discount) > 0">
          <span>Giảm giá:</span>
          <span>- {{ formatCurrency(order.discount) }}</span>
        </div>

        <div v-for="surcharge in order.surcharges" :key="surcharge.id" class="row">
          <span>{{ surcharge.description }}:</span>
          <span>+ {{ formatCurrency(surcharge.amount) }}</span>
        </div>

        <div class="divider-dashed"></div>

        <div class="row final-total">
          <span>THÀNH TIỀN:</span>
          <span>{{ formatCurrency(calculatedTotal) }}</span>
        </div>
        <div class="row final-total">
          <span>ĐÃ THANH TOÁN:</span>
          <span>{{ formatCurrency(order.amount_paid_by_customer) }}</span>
        </div>
        <div class="row final-total">
          <span>CÒN LẠI:</span>
          <span>{{ formatCurrency(calculatedTotal - order.amount_paid_by_customer) }}</span>
        </div>
        <div class="row final-total">
          Thank you for shopping with us!
        </div>
      </div>
      


    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';

// Import logo from assets
import logoUrl from '@/assets/logoFitpack.png';

// Define props to accept the order JSON object
const props = defineProps({
  order: {
    type: Object,
    required: true,
    default: () => ({})
  }
});

// Format Currency (VND)
const formatCurrency = (value) => {
  return new Intl.NumberFormat('vi-VN', {
    style: 'currency',
    currency: 'VND',
  }).format(value);
};

// Format Date
const formatDate = (dateString) => {
  if (!dateString) return '';
  const date = new Date(dateString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

// Calculate Grand Total (The JSON 'final_total' is 0, so we calculate manually)
const calculatedTotal = computed(() => {
  const subtotal = Number(props.order.total) || 0;
  const discount = Number(props.order.discount) || 0;
  
  // Sum active surcharges
  const surchargeTotal = props.order.surcharges 
    ? props.order.surcharges.reduce((acc, curr) => acc + (curr.is_active ? curr.amount : 0), 0)
    : 0;

  return subtotal - discount + surchargeTotal;
});
</script>

<style scoped>
  span , strong {
    color: #000;
  }
/* Base Styles */
.receipt-container {
  max-width: 100%;
  margin: 0 auto;
  padding: 20px;
  background: #fff;
  font-family: 'Courier New', Courier, monospace;
  color: #000;
  box-shadow: none;
}

.header {
  text-align: center;
}
.header h2 {
  margin: 0 0 5px 0;
  font-size: 1.2rem;
  text-transform: uppercase;
  color: #000;
}
.header p {
  margin: 2px 0;
  font-size: 0.9rem;
  color: #000;
}

.divider {
  border-bottom: 2px solid #000;
  margin: 10px 0;
}
.divider-dashed {
  border-bottom: 1px dashed #000;
  margin: 10px 0;
}

.item-row{
  /* 1st child */

}

.text-left { text-align: left; }
.text-center { text-align: center; }
.text-right { text-align: right; }

/* Table Styles */
.items-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.9rem;
  color: #000;
}
.items-table th {
  border-bottom: 1px solid #000;
  padding-bottom: 5px;
  color: #000;
}
.items-table td {
  padding: 8px 0;
  vertical-align: top;
  color: #000;
}

.item-name {
  font-weight: bold;
  color: #000;
  text-align: left;
}
.sku {
  font-weight: normal;
  font-size: 0.75rem;
  color: #000;
}

/* Package/Combo Styles */
.package-row td {
  padding-top: 0;
  padding-bottom: 10px;
}
.package-list {
  margin: 0;
  padding-left: 15px;
  list-style: none;
  font-size: 0.75rem;
  color: #000;
}
.package-list li {
  position: relative;
  padding-left: 10px;
  color: #000;
}
.package-list li::before {
  content: "↳";
  position: absolute;
  left: -5px;
  color: #000;
}
.qty-badge {
  font-weight: bold;
  color: #000;
}

/* Totals Styles */
.totals .row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 5px;
  color: #000;
}
.final-total {
  font-weight: 900;
  font-size: 1.2rem;
  margin-top: 5px;
  color: #000;
}

.footer {
  text-align: center;
  margin-top: 20px;
  font-size: 0.8rem;
  font-style: italic;
  color: #000;
}

/* Action Bar (Button) */

.action-bar {
  margin-bottom: 20px;
  text-align: center;
}
.btn-print {
  background: #fff;
  color: #000;
  border: 1px solid #000;
  padding: 10px 20px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;
}
.btn-print:hover {
  background: #eee;
  color: #000;
}

</style>

<style>
  @media print {
  body * {
    visibility: hidden;
  }
  .receipt-container, .receipt-container * {
    visibility: visible;
  }
  .receipt-container {
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    margin: 0;
    padding: 0;
    box-shadow: none;
    max-width: 100%; /* Use full paper width */
  }
  .no-print {
    display: none !important;
  }
}
/* Logo style */
.fitpack-logo {
  display: block;
  margin: 0 auto 10px auto;
  max-width: 120px;
  max-height: 60px;
}
</style>