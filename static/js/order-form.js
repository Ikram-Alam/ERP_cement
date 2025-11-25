/**
 * Order Form JavaScript - Dynamic Interactions
 * Component-based approach with proper OOP
 */

// ========================================
// OrderFormManager Class
// ========================================
class OrderFormManager {
    constructor() {
        this.form = document.getElementById('orderForm');
        this.itemsContainer = document.getElementById('itemsBody');
        this.addItemBtn = document.getElementById('addItemBtn');
        this.vendorSelect = document.getElementById('vendor');
        this.itemCounter = 0;
        this.products = [];
        
        this.init();
    }
    
    init() {
        // Load products data
        this.loadProducts();
        
        // Add first item row
        this.addItemRow();
        
        // Event listeners
        this.addItemBtn.addEventListener('click', () => this.addItemRow());
        this.vendorSelect.addEventListener('change', () => this.handleVendorChange());
        
        // Form submission
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));
        
        // Auto-fill delivery address when vendor selected
        this.vendorSelect.addEventListener('change', () => this.autoFillAddress());
        
        console.log('✅ Order Form initialized');
    }
    
    loadProducts() {
        // Load products from window data or use sample data
        if (window.PRODUCTS_DATA && window.PRODUCTS_DATA.length > 0) {
            this.products = window.PRODUCTS_DATA;
        } else {
            // Sample product data as fallback
            this.products = [
                { id: 1, name: 'Premium Cement - Grade 43', price: 350, stock: 5000, grade: '43' },
                { id: 2, name: 'Premium Cement - Grade 53', price: 400, stock: 3500, grade: '53' },
                { id: 3, name: 'PPC Cement', price: 320, stock: 4200, grade: 'PPC' },
                { id: 4, name: 'PSC Cement', price: 330, stock: 2800, grade: 'PSC' },
                { id: 5, name: 'OPC Cement - Grade 33', price: 310, stock: 1500, grade: '33' }
            ];
        }
    }
    
    addItemRow() {
        this.itemCounter++;
        
        const row = document.createElement('div');
        row.className = 'item-row';
        row.dataset.itemId = this.itemCounter;
        
        row.innerHTML = `
            <div class="item-col">
                <select name="product[]" class="form-control product-select" required data-row="${this.itemCounter}">
                    <option value="">Select Product</option>
                    ${this.products.map(p => `
                        <option value="${p.id}" data-price="${p.price}" data-stock="${p.stock}">
                            ${p.name} - ${p.grade}
                        </option>
                    `).join('')}
                </select>
                <small class="stock-info" id="stock-${this.itemCounter}"></small>
            </div>
            
            <div class="item-col">
                <input type="number" name="quantity[]" class="form-control quantity-input" 
                       min="1" value="1" required data-row="${this.itemCounter}">
            </div>
            
            <div class="item-col">
                <input type="number" name="unit_price[]" class="form-control price-input" 
                       min="0" step="0.01" readonly required data-row="${this.itemCounter}">
            </div>
            
            <div class="item-col">
                <span class="item-total" id="item-total-${this.itemCounter}">₹0.00</span>
            </div>
            
            <div class="item-col">
                <button type="button" class="btn-remove-item" data-row="${this.itemCounter}">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;
        
        this.itemsContainer.appendChild(row);
        
        // Add event listeners for this row
        this.attachRowListeners(this.itemCounter);
    }
    
    attachRowListeners(rowId) {
        const productSelect = document.querySelector(`.product-select[data-row="${rowId}"]`);
        const quantityInput = document.querySelector(`.quantity-input[data-row="${rowId}"]`);
        const priceInput = document.querySelector(`.price-input[data-row="${rowId}"]`);
        const removeBtn = document.querySelector(`.btn-remove-item[data-row="${rowId}"]`);
        
        // Product selection
        productSelect.addEventListener('change', (e) => {
            const selectedOption = e.target.selectedOptions[0];
            const price = selectedOption.dataset.price || 0;
            const stock = selectedOption.dataset.stock || 0;
            
            priceInput.value = price;
            
            // Show stock info
            const stockInfo = document.getElementById(`stock-${rowId}`);
            if (stock) {
                stockInfo.textContent = `Available: ${stock} bags`;
                stockInfo.className = stock < 100 ? 'stock-info stock-low' : 'stock-info';
            }
            
            this.calculateRowTotal(rowId);
        });
        
        // Quantity change
        quantityInput.addEventListener('input', () => this.calculateRowTotal(rowId));
        priceInput.addEventListener('input', () => this.calculateRowTotal(rowId));
        
        // Remove button
        removeBtn.addEventListener('click', () => this.removeItemRow(rowId));
        
        // Discount and tax changes
        document.getElementById('discount_percent').addEventListener('input', () => this.calculateOrderTotal());
        document.getElementById('tax_percent').addEventListener('input', () => this.calculateOrderTotal());
    }
    
    calculateRowTotal(rowId) {
        const quantityInput = document.querySelector(`.quantity-input[data-row="${rowId}"]`);
        const priceInput = document.querySelector(`.price-input[data-row="${rowId}"]`);
        const totalSpan = document.getElementById(`item-total-${rowId}`);
        
        const quantity = parseFloat(quantityInput.value) || 0;
        const price = parseFloat(priceInput.value) || 0;
        const total = quantity * price;
        
        totalSpan.textContent = `₹${total.toFixed(2)}`;
        
        // Recalculate order total
        this.calculateOrderTotal();
    }
    
    calculateOrderTotal() {
        let subtotal = 0;
        let totalBags = 0;
        
        // Calculate subtotal from all rows
        const rows = this.itemsContainer.querySelectorAll('.item-row');
        rows.forEach(row => {
            const rowId = row.dataset.itemId;
            const quantityInput = document.querySelector(`.quantity-input[data-row="${rowId}"]`);
            const priceInput = document.querySelector(`.price-input[data-row="${rowId}"]`);
            
            const quantity = parseFloat(quantityInput.value) || 0;
            const price = parseFloat(priceInput.value) || 0;
            
            subtotal += quantity * price;
            totalBags += quantity;
        });
        
        // Get discount and tax percentages
        const discountPercent = parseFloat(document.getElementById('discount_percent').value) || 0;
        const taxPercent = parseFloat(document.getElementById('tax_percent').value) || 0;
        
        // Calculate amounts
        const discountAmount = (subtotal * discountPercent) / 100;
        const taxableAmount = subtotal - discountAmount;
        const taxAmount = (taxableAmount * taxPercent) / 100;
        const totalAmount = taxableAmount + taxAmount;
        
        // Update UI
        document.getElementById('subtotal').textContent = `₹${subtotal.toFixed(2)}`;
        document.getElementById('discountAmount').textContent = `₹${discountAmount.toFixed(2)}`;
        document.getElementById('taxableAmount').textContent = `₹${taxableAmount.toFixed(2)}`;
        document.getElementById('taxAmount').textContent = `₹${taxAmount.toFixed(2)}`;
        document.getElementById('totalAmount').textContent = `₹${totalAmount.toFixed(2)}`;
        document.getElementById('totalBags').textContent = totalBags;
    }
    
    removeItemRow(rowId) {
        const row = document.querySelector(`.item-row[data-item-id="${rowId}"]`);
        const remainingRows = this.itemsContainer.querySelectorAll('.item-row').length;
        
        if (remainingRows > 1) {
            row.remove();
            this.calculateOrderTotal();
        } else {
            alert('At least one item is required');
        }
    }
    
    handleVendorChange() {
        const selectedOption = this.vendorSelect.selectedOptions[0];
        const vendorCard = document.getElementById('vendorInfoCard');
        
        if (selectedOption.value) {
            const phone = selectedOption.dataset.phone || '-';
            const credit = selectedOption.dataset.credit || '0';
            
            document.getElementById('vendorPhone').textContent = phone;
            document.getElementById('vendorCredit').textContent = `₹${parseFloat(credit).toFixed(2)}`;
            
            vendorCard.style.display = 'block';
        } else {
            vendorCard.style.display = 'none';
        }
    }
    
    autoFillAddress() {
        const selectedOption = this.vendorSelect.selectedOptions[0];
        const addressField = document.getElementById('delivery_address');
        
        if (selectedOption.value && !addressField.value) {
            const address = selectedOption.dataset.address || '';
            addressField.value = address;
        }
    }
    
    handleSubmit(e) {
        // Validate form
        const rows = this.itemsContainer.querySelectorAll('.item-row');
        let hasItems = false;
        
        rows.forEach(row => {
            const productSelect = row.querySelector('.product-select');
            if (productSelect.value) {
                hasItems = true;
            }
        });
        
        if (!hasItems) {
            e.preventDefault();
            alert('Please add at least one item to the order');
            return false;
        }
        
        // Show loading state
        const submitBtn = this.form.querySelector('button[type="submit"]');
        submitBtn.classList.add('loading');
        submitBtn.disabled = true;
        
        // Form will submit normally
        return true;
    }
}

// ========================================
// Initialize when DOM is ready
// ========================================
document.addEventListener('DOMContentLoaded', () => {
    const orderForm = new OrderFormManager();
    
    // Set minimum delivery date to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('delivery_date').setAttribute('min', today);
});
