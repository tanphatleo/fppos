<template>
  <div class="modal-overlay" @click="closeForm">
    <div class="customer-window" @click.stop>
      <div class="window-header ">
        <span class="window-title">
          <span class="no-select">{{ props.customer ? 'Cập nhật khách hàng' : 'Thêm khách hàng' }}</span>
          <span class="branch-info"> Chi nhánh tạo: <span> {{ props.currentBranch }} </span></span>
        </span>
        <div class="window-actions no-select">
          <button @click="closeForm" class="close-btn">
            <span>×</span>
          </button>
        </div>
      </div>

      <div class="window-content">
        <div class="tabs-nav no-select">
          <ul>
            <li :class="{ active: activeTab === 'general' }">
              <a href="#" @click.prevent="activeTab = 'general'">Thông tin chung</a>
            </li>
          </ul>
        </div>

        <div class="form-body">
          <div v-if="activeTab === 'general'" class="tab-pane">
            <div class="form-layout">
              <div class="col-left">
                <div class="form-group">
                  <label class="no-select">Mã khách hàng</label>
                  <input type="text" v-model="form.code" placeholder="Mã mặc định" :disabled="type!=='new'" />
                </div>
                <div class="form-group">
                  <label class="required no-select">Tên khách hàng</label>
                  <input type="text" v-model="form.name" placeholder="Bắt buộc" />
                </div>
                <div class="form-group">
                  <label class="no-select">Điện thoại</label>
                  <input type="text" v-model="form.phone_number" placeholder="Bắt buộc" @input="handlePhoneNumberInput"/>
                </div>
                <div class="form-group">
                  <label class="no-select">Địa chỉ</label>
                  <textarea v-model="form.address" rows="2" placeholder="Số nhà, tòa nhà, ngõ, đường"></textarea>
                </div>
                
                <div class="form-group">
                  <label class="no-select">Khu vực</label>
                  <div class="autocomplete-wrapper">
                    <input 
                      ref="locationInputRef"
                      type="text" 
                      v-model="form.province_name" 
                      placeholder="Chọn Tỉnh/TP"
                      @focus="openDropdown('location')"
                      @input="openDropdown('location')"
                      @blur="handleBlur('location')"
                      @change="handleChangeLocation"
                    />
                    
                    <Teleport to="body">
                      <ul 
                        v-if="showLocationList && filteredRegions.length" 
                        class="autocomplete-list"
                        :style="dropdownStyle"
                      >
                        <li 
                          v-for="region in filteredRegions" 
                          :key="region.id"
                          @mousedown.prevent="selectLocation(region)"
                        >
                          {{ region.name }}
                        </li>
                      </ul>
                    </Teleport>
                  </div>
                </div>

                <div class="form-group">
                  <label class="no-select">Phường xã</label>
                  <div class="autocomplete-wrapper">
                    <input 
                      ref="wardInputRef"
                      type="text" 
                      v-model="form.ward_name" 
                      placeholder="Chọn Phường/Xã"
                      :disabled="!form.province"
                      @focus="openDropdown('ward')"
                      @input="openDropdown('ward')"
                      @blur="handleBlur('ward')"
                    />

                    <Teleport to="body">
                      <ul 
                        v-if="showWardList && filteredWards.length" 
                        class="autocomplete-list"
                        :style="dropdownStyle"
                      >
                        <li 
                          v-for="ward in filteredWards" 
                          :key="ward.id"
                          @mousedown.prevent="selectWard(ward)"
                        >
                          {{ ward.name }}
                        </li>
                      </ul>
                    </Teleport>
                  </div>
                </div>

              </div>

              <div class="col-right">

                <div class="form-group">
                  <label class="no-select">Ngày sinh</label>
                  <div class="row-inputs">
                    <input type="date" v-model="form.birthdate" class="input-date" />
                    <div class="gender-radios">
                      <label><input type="radio" :value="true" v-model="form.gender" /> Nam</label>
                      <label><input type="radio" :value="false" v-model="form.gender" /> Nữ</label>
                    </div>
                  </div>
                </div>

                <div class="form-group">
                  <label class="no-select">Email</label>
                  <input type="email" v-model="form.email" />
                </div>
                <div class="form-group">
                  <label class="no-select">Facebook</label>
                  <input type="text" v-model="form.facebook" />
                </div>
                <div class="form-group">
                  <label class="no-select">Ghi chú</label>
                  <textarea v-model="form.comments" rows="3"></textarea>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="window-footer">
          <button class="btn btn-outline" @click="closeForm">
            <i class="icon-ban"></i> Bỏ qua
          </button>
          <button class="btn btn-primary new-button" @click="saveCustomer" :disabled="!form.name.trim() || !form.phone_number.trim() || !form.address.trim() || !form.province_name.trim()">
            <i class="icon-save"></i> Lưu
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, defineProps, computed, nextTick, watch } from 'vue';
import axios from 'axios';

const activeTab = ref('general');
const emit = defineEmits(['close', 'saved']);

const props = defineProps({
  currentBranch: {
    type: String,
    default: 'Chi nhánh Gia'
  },
  customer: {
    type: Object,
    default: null
  }, 
  regionList: {
    type: Array,
    default: () => []
  },
  wardList: {
    type: Array,
    default: () => []
  }, 
  type: {
    type: String,
    default: 'new' // or 'edit'
  }
});



const defaultForm = () => ({
  code: '',
  name: '',
  phone_number: '',
  address: '',
  location: '', // region id
  locationName: '', // region name for display
  ward: null, // ward id
  ward_name: '', // ward name for display
  province: null,
  province_name: '',
  // group: '',
  birthdate: '',
  gender: true,
  email: '',
  facebook: '',
  comments: ''
});

function handlePhoneNumberInput(event) {
  let value = event.target.value;
  // Allow numbers, +, -, (, )
  form.phone_number = value.replace(/[^0-9+\-()]/g, '');
}


const form = reactive(defaultForm());

// --- Autocomplete Logic ---
const showLocationList = ref(false);
const showWardList = ref(false);

// Refs for the inputs so we can calculate position
const locationInputRef = ref(null);
const wardInputRef = ref(null);

// Reactive style object for the dropdown
const dropdownStyle = reactive({
  top: '0px',
  left: '0px',
  width: '0px',
  display: 'block' // Required for teleport
});

// Calculate position based on the input element
const updateDropdownPosition = (inputElement) => {
  if (!inputElement) return;
  
  const rect = inputElement.getBoundingClientRect();
  dropdownStyle.top = `${rect.bottom + window.scrollY}px`; // Add scrollY for safety
  dropdownStyle.left = `${rect.left + window.scrollX}px`;
  dropdownStyle.width = `${rect.width}px`;
};

const openDropdown = (type) => {
  // Close others first
  showLocationList.value = false;
  showWardList.value = false;

  nextTick(() => {
    if (type === 'location') {
      console.log('Opening location dropdown');
      updateDropdownPosition(locationInputRef.value);
      showLocationList.value = true;
    } else if (type === 'ward') {
      updateDropdownPosition(wardInputRef.value);
      showWardList.value = true;
    }
  });
};

// --- Regions ---
const filteredRegions = computed(() => {
  // console.log('Filtering regions with query:', form.province_name);
  const query = form.province_name ? form.province_name.toLowerCase() : '';
  // console.log('Filtering regions with query:', query);
  // console.log('Total regions available:', props.regionList);
  if (!query) return props.regionList || [];
  return (props.regionList || []).filter(r => r.name.toLowerCase().includes(query));
});

function selectLocation(region) {
  form.province = region.id;
  form.province_name = region.name;
  form.ward = null;
  form.ward_name = '';
  showLocationList.value = false;
}

function handleChangeLocation() {
  // form.province_id = null;
  form.ward_id = null;
  form.ward = '';
}

const filteredWards = computed(() => {
  const queryWard = form.ward_name ? form.ward_name.toLowerCase() : '';
  // console.log('Filtering wards with query:', queryWard);
  // console.log('Total wards available:', props.wardList);
  // console.log('Current selected province:', form.province);

  let wardsToFilter = props.wardList || [];
  
  // If a province is selected, filter by province first
  if (form.province) {
    wardsToFilter = wardsToFilter.filter(w => w.province === form.province);
  }
  // console.log('Wards to filter count:', form.province, wardsToFilter.length);

  // Always filter by the ward name query
  return wardsToFilter.filter(w => w.name.toLowerCase().includes(queryWard));
});

function selectWard(ward) {
  form.ward = ward.id;
  form.ward_name = ward.name;
  showWardList.value = false;
}

// --- UI Helpers ---
function handleBlur(type) {
  setTimeout(() => {
    if (type === 'location') showLocationList.value = false;
    if (type === 'ward') showWardList.value = false;
  }, 200);
}

// --- Standard Actions ---

const saveCustomer = async () => {
  //  check if old customer or new]
  // send request to backend /customers/ 

  const customerData = { ...form };

  // remove province_name and ward_name before sending
  // customerData.address =  customerData.address + ', ' + customerData.ward_name + ', ' + customerData.province_name;
  // delete customerData.province_name;
  // delete customerData.ward_name;
  
  if (props.type === 'edit') {
    // update 
    delete customerData.province_name;
    delete customerData.ward_name;
    await axios.put(`/customers/${props.customer.id}/`, customerData)
      .then(response => {
        console.log("Customer updated:", response.data);
        emit('saved', response.data);
        emit('close');
      })
      .catch(error => {
        console.error("Error updating customer:", error);
        window.alert("Lỗi cập nhật khách hàng: " + (error.response && error.response.data ? JSON.stringify(error.response.data) : error.message));
      });
  } else {
    // create new
    // customerData.address =  customerData.address + ', ' + customerData.ward_name + ', ' + customerData.province_name;
    delete customerData.province_name;
    delete customerData.ward_name;
    await axios.post('/customers/', customerData)
      .then(response => {
        console.log("Customer created:", response.data);
        emit('saved', response.data);
        emit('close');
      })
      .catch(error => {
        console.error("Error creating customer:", error);
        window.alert("Lỗi tạo khách hàng: " + (error.response && error.response.data ? JSON.stringify(error.response.data) : error.message));
      });
  }
   

};

const closeForm = () => {
  emit('close');
};

// Ensure locationName is synced when editing
onMounted(() => {
  if (props.customer) {
    Object.assign(form, defaultForm(), props.customer);
    if (props.customer.province) {
      const region = props.regionList.find(r => r.id === props.customer.province);
      if (region) form.province_name = region.name;
    }
    if (props.customer.ward) {
      const ward = props.wardList.find(w => w.id === props.customer.ward);
      if (ward) form.ward_name = ward.name;
    }
  } else {
    Object.assign(form, defaultForm());
  }
});



</script>

<style lang="scss" scoped>
  $kv-primary: #0070F4;
/* Reset & Layout */

.new-button {
  &:disabled {
    background-color: #a0c4ff !important;
    border-color: #a0c4ff !important;
    cursor: not-allowed !important;
  }
}

.no-select {
  user-select: none;
  -webkit-user-select: none;
  -moz-user-select: none;
  -ms-user-select: none;

}

input, textarea, select {
  background-color: white;
  color: black;
}


$calendar-icon-url: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="16" height="15" viewBox="0 0 24 24"><path fill="%23000" d="M20 3h-1V1h-2v2H7V1H5v2H4c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm0 18H4V8h16v13z"/></svg>');

input[type="date"] {
  position: relative;
  
  &::-webkit-calendar-picker-indicator {
    cursor: pointer;
    
    // 1. Hide the default native icon
    background-image: none; 
    
    // 2. Define the mask shape using the icon
    -webkit-mask-image: $calendar-icon-url;
    mask-image: $calendar-icon-url;
    
    -webkit-mask-repeat: no-repeat;
    mask-repeat: no-repeat;
    
    -webkit-mask-position: center;
    mask-position: center;
    
    -webkit-mask-size: 1rem;
    mask-size: 1rem;

    // 3. Set your specific color here!
    background-color: black; 
    // font-size: 0.5rem;
    
    // Adjust size if needed
    width: 20px;
    height: 20px;
  }
}

* {
  box-sizing: border-box;
  font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  text-align: left;
}

.modal-overlay {
  position: fixed;
  top: 0; left: 0;
  width: 100vw; height: 100vh;
  background: rgba(0,0,0,0.3);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.customer-window {
  background: #fff;
  width: 900px;
  max-width: 95vw;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  overflow: hidden; /* This no longer cuts off the dropdown */
}

/* Header */
.window-header {
  background-color: $kv-primary;
  color: white;
  padding: 10px 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.window-title {
  font-weight: bold;
  font-size: 15px;
}

.branch-info {
  font-weight: normal;
  font-size: 12px;
  opacity: 0.9;
  margin-left: 10px;
}

.close-btn {
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  line-height: 1;
}

/* Tabs */
.tabs-nav {
  background: #f0f0f0;
  border-bottom: 1px solid #ddd;
  padding: 0 10px;
}

.tabs-nav ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
}

.tabs-nav li {
  margin-right: 2px;
}

.tabs-nav a {
  display: block;
  padding: 10px 15px;
  text-decoration: none;
  color: #333;
  border: 1px solid transparent;
  border-bottom: none;
  border-radius: 4px 4px 0 0;
}

.tabs-nav li.active a {
  background: #fff;
  border-color: #ddd;
  border-bottom-color: #fff;
  color: #000;
  font-weight: 600;
  margin-bottom: -1px;
}

/* Form Body */
.form-body {
  padding: 20px;
  background: #fff;
  max-height: 70vh;
  overflow-y: auto;
}

.form-layout {
  display: flex;
  gap: 20px;
}

.col-left, .col-right {
  flex: 1;
}

.form-group {
  display: flex;
  flex-direction: row;
  align-items: baseline;
  margin-bottom: 12px;
  -webkit-user-select: none; /* Safari */
  -moz-user-select: none;    /* Firefox */
  -ms-user-select: none;     /* IE10+/Edge */
  user-select: none;   
}

.form-group label {
  width: 9rem;
  color: #333;
  font-weight: 500;
  flex-shrink: 0;
  padding-right: 1em;
}

.form-group input, 
.form-group select, 
.form-group textarea {
  width: 100%;
  padding: 6px 10px;
  border: 1px solid #ccc;
  border-radius: 3px;
  transition: border-color 0.2s;
}

.form-group input:focus, 
.form-group select:focus, 
.form-group textarea:focus {
  border-color: $kv-primary;
  outline: none;
}

/* AUTOCOMPLETE STYLES (UPDATED) */
.autocomplete-wrapper {
  position: relative;
  width: 100%;
}

/* This is now a GLOBAL class because of Teleport */
.autocomplete-list {
  position: fixed; /* Fixed to viewport */
  max-height: 200px;
  overflow-y: auto;
  background: white;
  border: 1px solid #ccc;
  list-style: none;
  padding: 0;
  margin: 0;
  z-index: 99999; /* Sit on top of everything */
  box-shadow: 0 4px 10px rgba(0,0,0,0.2);
  border-radius: 0 0 4px 4px;
}

.autocomplete-list li {
  padding: 8px 10px;
  cursor: pointer;
  border-bottom: 1px solid #eee;
  font-size: 13px; /* Ensure font size matches */
  color: #333;
}

.autocomplete-list li:hover {
  background-color: #f0f8ff;
  color: $kv-primary;
}

/* Specific Field Styles */
.row-inputs {
  display: flex;
  align-items: center;
  width: 100%;
  gap: 15px;
}

.input-date {
  width: 140px !important;
}

.gender-radios {
  display: flex;
}

.gender-radios label {
  width: auto;
  margin-right: 15px;
  font-weight: normal;
  cursor: pointer;
  display: flex;
  flex-direction: row;
}

.gender-radios label input {
  margin-right: 5px;
}

/* Footer */
.window-footer {
  padding: 15px 20px;
  border-top: 1px solid #ddd;
  background: #f5f5f5;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
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
}

.btn-outline {
  background: white;
  border-color:   $kv-primary;
  color: $kv-primary;
}

.btn-primary {
  background: $kv-primary;
  color: white;
}

.btn-primary:hover {
  background: #0077b5;
}
</style>