<template>
  <div style="height: 100%;">
    <div class="home-page" style="height: 100%;">
      <div class="page-header">
        <div class="header-left">
          <div class="col-left-control">
            <div class="product-search">
              <i class="fas fa-search"></i>
              <input class="product-search-input c-input" placeholder="Tìm hàng hóa" />
              <div class="product-search-results">
                <ul v-for="product in products" :key="product.id" :id="'product-' + product.id">
                  <li class="suggestions-item">
                    <div class="suggestions-item-info"> 
                      <h5><b>{{ product.name }}</b></h5>
                      <div class="number-blue"> {{ formatPrice(product.price) }}</div>
                    </div>
                    <div class="suggestions-item-info"> {{ product.code }}</div>
                  </li>
                </ul>
              </div>
            </div>
            <div class="carts-tab">
            </div>
          </div>
          <div class="header-left-info">
          </div>
        </div>
        <div class="header-right">
        </div>  
      </div>
    </div>
  </div>

</template>
<script>

  export default {
    name: "SaleView",
    methods: {
      formatPrice(value) {
        return new Intl.NumberFormat('vi-VN').format(value);
      }
    },
    data() {
      return {
        products: []
      }
    },
    created() {
      // Simulate fetching products from an API
      this.products = [
        { "id": 1, "code":"ESP001", "name": "Espresso", "price": 35000 },
        { "id": 2, "code":"LAT002", "name": "Latte", "price": 45000 },
        { "id": 3, "code":"BANHMI003", "name": "Banh Mi", "price": 25000 }
      ];
    }
  }
</script>

<style lang="scss" scoped>
$kv-primary: #0070F4;
$size-sm: 10vh;

.home-page {
  height: 100%;
  display: flex ;
  flex-direction: column;
  background-color: azure;
}
.number-blue {
  color: $kv-primary;
  // text-decoration: solid;
  font-weight: bold;
}

.c-input{
  background-color: white;
  color: black;
  padding-left: 2.5rem;
}
.carts-tab {
  flex: 1;
  width: 70vw;
}

.page-header {
  display: flex;
  flex-direction: row;
  height: $size-sm;
  background-color: $kv-primary;
}

.product-search {
  // background-color: white;
    min-width: 30rem;
    position: relative;
    height: 100%;
    padding: 0.4rem 0 0.4rem 0.4rem;
    flex-grow: 1;
    display: flex;
    max-width: 15vw;
}
.suggestions-item {
  display: flex;
  flex-direction: column;
}

.suggestions-item-info {
  display: flex;
  justify-content: space-between;
}

.product-search-results{
  position: absolute;
  margin-top: 0.7rem;
  top: 100%;
  left: 0;
  width: 100%;
  z-index: 2;
}
.product-search > i {
  position: absolute;
  top: 0.9rem;
  left: 1rem;
  color: gray;
  z-index: 1;
  height: $size-sm;
}
.product-search > input {
  height: 100%;
  border: none;
  border-radius: 0.3rem;
  font-size: 1rem;
  box-shadow: 0 0 0 0;
  outline: none;
  width: 100%;
  
}

.col-left-control {
  display: flex;
}

.header-left {
  display: flex;
  flex-direction: row;
}

.header-right {
  display: flex;
  flex-direction: row;
}

</style>
