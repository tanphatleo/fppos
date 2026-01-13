<template>

</template>

<script>
import { ref, computed, onMounted, nextTick, onBeforeUnmount, watch} from 'vue';
import axios from 'axios';
import { useStore } from 'vuex';

export default {
  name: 'DateEndInventory',
  components: {
  },
  setup() {
    const DateEndInventorys = ref([]);
    const store = useStore();
    const getLocalDateISO = (date) => {
      return new Date(date.getTime() - (date.getTimezoneOffset() * 60000)).toISOString().substr(0, 10);
    };
    const fetchDateEndInventorys = async () => {
      store.commit('setLoading', true);
      try {
        const response = await axios.get('/DateEndInventory/', {
          params: {
            dateEnd: true,
            // date default to to-day's date
            date: ref(getLocalDateISO(new Date(Date.now() - 30 * 24 * 60 * 60 * 1000)))
          }
        });
        DateEndInventorys.value = response.data;
      } catch (error) {
        console.error('Error fetching invoices:', error);
      }
      store.commit('setLoading', false);
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
    });

    return {
      
      // surcharges,
      formatPrice,
      formatDateTime,
      
    };
  },
};
</script>