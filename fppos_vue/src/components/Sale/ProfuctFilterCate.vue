<template>
  <div class="product-filter-cate-component">
    <div v-if="visible" class="float-overlay" @mousedown.self=""></div>

    <transition name="slide-fade">
      <div v-if="visible" class="float-nav">
        <div class="float-nav-content">
          
          <h3 class="float-nav-title filter no-select">
            Lọc theo nhóm hàng
            <button tabindex="-1" @click="close" class="btn-icon btn-icon-default">
              <i class="fa fa-times"></i>
            </button>
          </h3>

          <div class="filter-header">
            <h4 class="filter-header-title no-select"><span>Nhóm hàng</span></h4>
            
            <div class="filter-header-autocomplete">
              <div class="autocomplete">
                <i class="fa fa-search"></i>
                <input 
                  tabindex="-1" 
                  type="text" 
                  v-model="searchParam" 
                  placeholder="Tìm nhóm hàng" 
                  class="form-control form-control-custom"
                >
              </div>
            </div>
          </div>

          <div class="scroll-content">
            <div class="kv-treeview k-widget k-treeview" role="tree">
              <ul class="k-group k-treeview-lines">
                
                <li role="treeitem" class="k-first k-last" aria-expanded="true">
                  <div class="k-top k-bot ">
                    <span 
                      class="k-icon fixed-cate-align" 
                      :class="isExpanded ? 'k-minus' : 'k-plus'" 
                      @click="isExpanded = !isExpanded"
                      role="presentation"
                    ></span>
                    
                    <span class="k-checkbox-wrapper" role="presentation">
                      <input 
                        type="checkbox" 
                        id="node-all" 
                        class="k-checkbox"
                        :checked="isAllSelected"
                        :indeterminate="isIndeterminate"
                        @change="toggleAll"
                      >
                      <label for="node-all" class="k-checkbox-label"></label>
                    </span>
                    
                    <span class="k-in"><span @click="onToggleAllClick" class="cate-item no-select">Tất cả</span></span>
                  </div>

                  <ul class="k-group" v-show="isExpanded">
                    <li 
                      v-for="(item, index) in filteredList" 
                      :key="item.name" 
                      role="treeitem" 
                      class="k-item adjusted-k-item no-select"
                      :class="{ 'k-last': index === filteredList.length - 1 }"
                    >
                    <div class="k-top k-bot fixed-cate-align">
                        <span class="k-icon fixed-cate-align" ></span>
                    </div>
                      <div :class="index === filteredList.length - 1 ? 'k-bot' : 'k-mid'">
                        <span class="k-checkbox-wrapper" role="presentation">
                          <input 
                            type="checkbox" 
                            :id="'node-' + item.name" 
                            class="k-checkbox"
                            :value="item.name"
                            v-model="selectedIds"
                          >
                          <label :for="'node-' + item.name" class="k-checkbox-label"></label>
                        </span>
                        <span class="k-in cate-item" @click="toggleSelection(item.name)">
                          <span>{{ item.name }}</span>
                        </span>
                      </div>
                    </li>
                  </ul>
                </li>

              </ul>
            </div>

            <div v-show="filteredList.length === 0" class="not-found" style="color: #a5a6ae; padding: 20px; text-align: center;">
              <i class="far fa-file-search" style="font-size: 32px; display: block; margin-bottom: 10px;"></i> 
              Không có kết quả nào được tìm thấy
            </div>
          </div>

          <div class="group-buttons">
            <div class="group-buttons-left no-select">
              <div @click="clearFilter" class="btn-remove-filter font-medium cursor-pointer">
                <i class="far fa-trash-alt"></i> Xóa chọn tất cả
              </div>
            </div>
            <div class="group-buttons-right no-select">
              <div @click="close" class="btn btn-outline-primary">
                Bỏ qua
              </div>
              <div @click="applyFilter" class="btn btn-primary no-select">
                <button class="">Xong</button> 
              </div>
            </div>
          </div>

        </div>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue';

// Props
const props = defineProps({
  visible: {
    type: Boolean,
    default: true
  },
  // Pass your category list here
  dataSource: {
    type: Array,
    default: () => [
    ]
  },
  // Pre-selected IDs
  modelValue: {
    type: Array,
    default: () => []
  }
});

// Emits
const emit = defineEmits(['update:visible', 'update:modelValue', 'apply']);

// State
const searchParam = ref('');
const isExpanded = ref(true); // Default expand "All"
const selectedIds = ref([]);

// Sync props with local state when modal opens
watch(() => props.visible, (newVal) => {
  if (newVal) {
    selectedIds.value = [...props.modelValue];
    searchParam.value = '';
  }
});

// Computed: Filter the list based on search
const filteredList = computed(() => {
  if (!searchParam.value) return props.dataSource;
  const lowerSearch = searchParam.value.toLowerCase();
  return props.dataSource.filter(item => 
    item.name.toLowerCase().includes(lowerSearch)
  );
});

// Computed: Checkbox "All" states
const isAllSelected = computed(() => {
  return filteredList.value.length > 0 && selectedIds.value.length === filteredList.value.length;
});

const isIndeterminate = computed(() => {
  return selectedIds.value.length > 0 && selectedIds.value.length < filteredList.value.length;
});

// Actions
const toggleAll = (e) => {
  if (e.target.checked) {
    // Select all visible items
    selectedIds.value = filteredList.value.map(item => item.name);
  } else {
    selectedIds.value = [];
  }
};

const onToggleAllClick = () => {
  if (isAllSelected.value) {
    selectedIds.value = [];
  } else {
    selectedIds.value = filteredList.value.map(item => item.name);
  }
};

const toggleSelection = (itemName) => {
  const index = selectedIds.value.indexOf(itemName);
  if (index > -1) {
    selectedIds.value.splice(index, 1);
  } else {
    selectedIds.value.push(itemName);
  }
};

const clearFilter = () => {
  selectedIds.value = [];
};

const close = () => {
  emit('update:visible', false);
};

const applyFilter = () => {
  emit('update:modelValue', selectedIds.value);
  emit('apply', selectedIds.value);
  close();
};
</script>

<style lang="scss" scoped>
/* Basic structural styles mimicking Kendo/Bootstrap 
   assuming global styles exist, but adding scoped overrides here 
*/

input {
  background-color: white;
  color: black;
}
$kv-primary: #0070F4;

.no-select {
  -webkit-user-select: none; /* Safari */
  -moz-user-select: none;    /* Firefox */
  -ms-user-select: none;     /* IE10+/Edge */
  user-select: none;         /* Standard */
}

.float-nav {
  position: fixed;
  border-radius: 0.5rem;
  top: 0;
  right: 0;
  bottom: 0;
  width: 30rem;
  max-width: 100%;
  background: #fff;
  z-index: 1050;
  box-shadow: -2px 0 5px rgba(0,0,0,0.1);
  display: flex;
  flex-direction: column;
}

.float-nav-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.float-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.5);
  z-index: 1040;
}

.scroll-content {
  flex: 1;
  overflow-y: auto;
  padding: 10px;
}

/* Header Styles */
.float-nav-title {
  padding: 15px;
  margin: 0;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 18px;
}

.filter-header {
  padding: 10px 15px;
  background: #f8f9fa;
  border-bottom: 1px solid #eee;
  display: flex;
  flex-direction: row;
}

.filter-header-title {
  margin: 0 1rem 0 0.2rem;
  font-size: 1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  height: 2rem;
}

.autocomplete {
  position: relative;
  display: flex;
}

.autocomplete input {
  flex: 1 1 0%;
  height: 2rem;
  border-radius: 0.5rem;
  border: 1px solid #ccc;
  width: 100%;
  min-width: 0;
  box-sizing: border-box;
  display: block;
}

.autocomplete i {
  position: absolute;
  flex:1;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: #999;
}

.form-control-custom {
  padding-left: 30px;
  width: 100%;
  box-sizing: border-box;
}

/* Footer Buttons */
.group-buttons {
  padding: 15px;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.group-buttons-right{
    display: flex;
}

.group-buttons-right .btn {
  margin-left: 10px;
  padding: 0.5rem;
  border-radius: 0.5rem;
  min-width: 6rem;
  width: 6rem;
  /* border: 1px solid #000000; */
}

.btn-outline-primary{
    border-color: $kv-primary;
    border: 1px solid $kv-primary;
    color: $kv-primary;
    cursor: pointer;
}

.btn-primary{
    background-color: $kv-primary;
    border: 1px solid $kv-primary;
    color: #ffffff;
    cursor: pointer;
}

.cursor-pointer {
  cursor: pointer;
}

.cate-item {
  cursor: pointer;
}

/* Minimal Kendo TreeView Imitation */
ul.k-group {
  list-style: none;
  padding-left: 16px;
}

ul.k-treeview-lines {
  padding-left: 0;
}

.k-item {
  display: flex;
}

.k-top, .k-mid, .k-bot {
  display: flex;
  align-items: center;
  padding: 4px 0;
}

.k-icon {
  width: 16px;
  height: 16px;
  margin-right: 5px;
  cursor: pointer;
  display: inline-block;
}
/* You may need font-awesome or kendo icons for plus/minus */
.k-plus::before { content: '+'; font-weight: bold; }
.k-minus::before { content: '-'; font-weight: bold; }

.k-checkbox-wrapper {
  margin-right: 8px;
}

/* Transitions */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateX(100%);
  opacity: 0;
}

.fixed-cate-align {
  width: 2rem;
}

.filter-header-autocomplete {
  flex: 1;
  height: 2rem;
}


</style>