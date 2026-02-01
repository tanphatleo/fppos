<template>
        <div class="popover-content" v-show="openDiscount" ref="popoverRef">
        
            <div>Giảm giá</div>
            <input 
                type="decimal" 
                class="value-input font-bold text-right" 
                @change="handleChangeDiscount"
                />
            <button :class="{ active: chosenDiscountMethod === 'VND' }" @mousedown.stop="chosenDiscountMethod = 'VND'">VND</button>
            <button :class="{ active: chosenDiscountMethod === '%' }" @mousedown.stop="chosenDiscountMethod = '%'">%</button>
        </div>    
</template>
                
<script setup>

import { ref, watch, onMounted, onBeforeUnmount } from 'vue';
const props = defineProps({
    openDiscount: {
        type: Boolean,
        required: true
    },
    chosenDiscountMethod: {
        type: String,
        required: true
    },
    discountMethodValue: {
        type: Number,
        required: true
    }
});

</script>

<style lang="scss" scoped>

discount-popover {
    position: relative;
    display: inline-block;
}

.popover-content {
      position: absolute;
      top: 0;
      right: 100%;
      width: 25rem;
      margin-right: 10px;
      background: #fff;
      border: 1px solid #ddd;
      box-shadow: 0 5px 8px rgba(0,0,0,0.5);
      padding: 10px;
      min-width: 120px;
      z-index: 10000;
      border-radius: 4px;
      /* display: block; */
      display: flex;
      flex-direction: row;

      div {
        margin-right: 8px;
        display: flex;
        align-items: center;
      }

      input {
        border-top: none;
        border-left: none;
        border-right: none;
      }

      input::-webkit-outer-spin-button,
        input::-webkit-inner-spin-button {
        -webkit-appearance: none;
        margin: 0;
        }
        input[type="number"] {
        -moz-appearance: textfield;
        }

      button {
        margin-left: 5px;
        padding: 3px 8px;
        border: 1px solid #ccc;
        border-radius: 3px;
        background: #f0f0f0;
        cursor: pointer;
      }

      button.active {
        background: #007bff !important;
        color: #fff;
        border-color: #007bff;
        }


    }
</style>