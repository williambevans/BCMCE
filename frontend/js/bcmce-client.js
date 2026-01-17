/**
 * BCMCE API Client Library
 * JavaScript client for interacting with BCMCE API
 */

class BCMCEClient {
    /**
     * Initialize BCMCE API client
     * @param {string} baseURL - Base URL of BCMCE API
     * @param {string} accessToken - Optional JWT access token
     */
    constructor(baseURL = 'http://localhost:8000/api/v1', accessToken = null) {
        this.baseURL = baseURL;
        this.accessToken = accessToken;
        this.wsConnection = null;
    }

    /**
     * Set access token for authenticated requests
     * @param {string} token - JWT access token
     */
    setAccessToken(token) {
        this.accessToken = token;
        localStorage.setItem('bcmce_token', token);
    }

    /**
     * Get stored access token
     * @returns {string|null} - Access token or null
     */
    getAccessToken() {
        if (this.accessToken) return this.accessToken;
        return localStorage.getItem('bcmce_token');
    }

    /**
     * Clear access token
     */
    clearAccessToken() {
        this.accessToken = null;
        localStorage.removeItem('bcmce_token');
    }

    /**
     * Make HTTP request
     * @param {string} endpoint - API endpoint
     * @param {string} method - HTTP method
     * @param {object} data - Request data
     * @param {boolean} requiresAuth - Whether endpoint requires authentication
     * @returns {Promise<object>} - Response data
     */
    async request(endpoint, method = 'GET', data = null, requiresAuth = false) {
        const url = `${this.baseURL}${endpoint}`;

        const headers = {
            'Content-Type': 'application/json'
        };

        if (requiresAuth) {
            const token = this.getAccessToken();
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }
        }

        const options = {
            method,
            headers
        };

        if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
            options.body = JSON.stringify(data);
        }

        try {
            const response = await fetch(url, options);

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || `HTTP ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error(`API Error (${method} ${endpoint}):`, error);
            throw error;
        }
    }

    // ========================================================================
    // AUTHENTICATION
    // ========================================================================

    /**
     * Login user
     * @param {string} email - User email
     * @param {string} password - User password
     * @returns {Promise<object>} - Token data
     */
    async login(email, password) {
        const response = await this.request('/auth/login', 'POST', { email, password });
        this.setAccessToken(response.access_token);
        return response;
    }

    /**
     * Logout user
     */
    logout() {
        this.clearAccessToken();
        if (this.wsConnection) {
            this.wsConnection.close();
            this.wsConnection = null;
        }
    }

    /**
     * Get current user profile
     * @returns {Promise<object>} - User data
     */
    async getCurrentUser() {
        return await this.request('/auth/me', 'GET', null, true);
    }

    // ========================================================================
    // PRICING
    // ========================================================================

    /**
     * Get current pricing for all materials
     * @returns {Promise<Array>} - Array of pricing data
     */
    async getCurrentPricing() {
        return await this.request('/pricing/current');
    }

    /**
     * Get pricing for specific material
     * @param {number} materialId - Material ID
     * @returns {Promise<Array>} - Array of pricing data
     */
    async getPricingByMaterial(materialId) {
        return await this.request(`/pricing/material/${materialId}`);
    }

    /**
     * Get pricing history
     * @param {number} pricingId - Pricing ID
     * @param {number} days - Number of days of history
     * @returns {Promise<Array>} - Array of historical pricing
     */
    async getPricingHistory(pricingId, days = 30) {
        return await this.request(`/pricing/${pricingId}/history?days=${days}`);
    }

    /**
     * Update supplier pricing
     * @param {number} pricingId - Pricing ID
     * @param {object} data - Updated pricing data
     * @returns {Promise<object>} - Updated pricing
     */
    async updatePricing(pricingId, data) {
        return await this.request(`/pricing/${pricingId}`, 'PUT', data, true);
    }

    // ========================================================================
    // OPTIONS
    // ========================================================================

    /**
     * Get available option prices
     * @returns {Promise<Array>} - Array of option prices
     */
    async getOptionPrices() {
        return await this.request('/options/prices');
    }

    /**
     * Get option prices for material
     * @param {number} materialId - Material ID
     * @returns {Promise<Array>} - Array of option prices
     */
    async getOptionPricesByMaterial(materialId) {
        return await this.request(`/options/prices/material/${materialId}`);
    }

    /**
     * Purchase option contract
     * @param {object} data - Option purchase data
     * @returns {Promise<object>} - Created option contract
     */
    async purchaseOption(data) {
        return await this.request('/options/purchase', 'POST', data, true);
    }

    /**
     * Get option contracts
     * @param {number} countyId - County ID (optional)
     * @returns {Promise<Array>} - Array of option contracts
     */
    async getOptionContracts(countyId = null) {
        const endpoint = countyId ? `/options/contracts?county_id=${countyId}` : '/options/contracts';
        return await this.request(endpoint, 'GET', null, true);
    }

    /**
     * Exercise option contract
     * @param {number} contractId - Contract ID
     * @param {object} data - Exercise data
     * @returns {Promise<object>} - Exercised contract
     */
    async exerciseOption(contractId, data) {
        return await this.request(`/options/contracts/${contractId}/exercise`, 'POST', data, true);
    }

    // ========================================================================
    // SUPPLIERS
    // ========================================================================

    /**
     * Get all suppliers
     * @returns {Promise<Array>} - Array of suppliers
     */
    async getSuppliers() {
        return await this.request('/suppliers/');
    }

    /**
     * Get supplier by ID
     * @param {number} supplierId - Supplier ID
     * @returns {Promise<object>} - Supplier data
     */
    async getSupplier(supplierId) {
        return await this.request(`/suppliers/${supplierId}`);
    }

    /**
     * Create supplier
     * @param {object} data - Supplier data
     * @returns {Promise<object>} - Created supplier
     */
    async createSupplier(data) {
        return await this.request('/suppliers/', 'POST', data, true);
    }

    /**
     * Update supplier
     * @param {number} supplierId - Supplier ID
     * @param {object} data - Updated supplier data
     * @returns {Promise<object>} - Updated supplier
     */
    async updateSupplier(supplierId, data) {
        return await this.request(`/suppliers/${supplierId}`, 'PUT', data, true);
    }

    // ========================================================================
    // COUNTY
    // ========================================================================

    /**
     * Submit requirement
     * @param {object} data - Requirement data
     * @returns {Promise<object>} - Created requirement
     */
    async submitRequirement(data) {
        return await this.request('/county/requirements', 'POST', data, true);
    }

    /**
     * Get requirements
     * @param {number} countyId - County ID (optional)
     * @returns {Promise<Array>} - Array of requirements
     */
    async getRequirements(countyId = null) {
        const endpoint = countyId ? `/county/requirements?county_id=${countyId}` : '/county/requirements';
        return await this.request(endpoint, 'GET', null, true);
    }

    /**
     * Get bids for requirement
     * @param {number} requirementId - Requirement ID
     * @returns {Promise<Array>} - Array of bids
     */
    async getBidsForRequirement(requirementId) {
        return await this.request(`/county/requirements/${requirementId}/bids`);
    }

    /**
     * Submit bid
     * @param {object} data - Bid data
     * @returns {Promise<object>} - Created bid
     */
    async submitBid(data) {
        return await this.request('/county/bids', 'POST', data, true);
    }

    /**
     * Accept bid
     * @param {number} bidId - Bid ID
     * @returns {Promise<object>} - Accepted bid
     */
    async acceptBid(bidId) {
        return await this.request(`/county/bids/${bidId}/accept`, 'POST', null, true);
    }

    // ========================================================================
    // ORDERS
    // ========================================================================

    /**
     * Get orders
     * @param {object} filters - Optional filters (county_id, supplier_id, status)
     * @returns {Promise<Array>} - Array of orders
     */
    async getOrders(filters = {}) {
        const params = new URLSearchParams(filters).toString();
        const endpoint = params ? `/orders?${params}` : '/orders';
        return await this.request(endpoint, 'GET', null, true);
    }

    /**
     * Get order by ID
     * @param {number} orderId - Order ID
     * @returns {Promise<object>} - Order data
     */
    async getOrder(orderId) {
        return await this.request(`/orders/${orderId}`, 'GET', null, true);
    }

    /**
     * Update order status
     * @param {number} orderId - Order ID
     * @param {string} status - New status
     * @returns {Promise<object>} - Updated order
     */
    async updateOrderStatus(orderId, status) {
        return await this.request(`/orders/${orderId}/status`, 'PUT', { status }, true);
    }

    // ========================================================================
    // MATERIALS
    // ========================================================================

    /**
     * Get all materials
     * @returns {Promise<Array>} - Array of materials
     */
    async getMaterials() {
        return await this.request('/materials/');
    }

    /**
     * Get material by ID
     * @param {number} materialId - Material ID
     * @returns {Promise<object>} - Material data
     */
    async getMaterial(materialId) {
        return await this.request(`/materials/${materialId}`);
    }

    // ========================================================================
    // WEBSOCKET
    // ========================================================================

    /**
     * Connect to WebSocket for real-time updates
     * @param {string} channel - Channel to subscribe to (pricing, options, bids, orders, all)
     * @param {function} onMessage - Callback for incoming messages
     * @param {function} onError - Callback for errors
     */
    connectWebSocket(channel = 'all', onMessage, onError = null) {
        const wsURL = this.baseURL.replace('http', 'ws').replace('/api/v1', '');
        const ws = new WebSocket(`${wsURL}/ws/${channel}`);

        ws.onopen = () => {
            console.log(`WebSocket connected to ${channel} channel`);
            this.wsConnection = ws;

            // Send heartbeat every 30 seconds
            setInterval(() => {
                if (ws.readyState === WebSocket.OPEN) {
                    ws.send('ping');
                }
            }, 30000);
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (onMessage) {
                onMessage(data);
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            if (onError) {
                onError(error);
            }
        };

        ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.wsConnection = null;
        };

        return ws;
    }

    /**
     * Disconnect WebSocket
     */
    disconnectWebSocket() {
        if (this.wsConnection) {
            this.wsConnection.close();
            this.wsConnection = null;
        }
    }
}

// Export for use
if (typeof module !== 'undefined' && module.exports) {
    module.exports = BCMCEClient;
}
