const API_URL = "http://127.0.0.1:8000";
let currentUser = localStorage.getItem("username") || "";
let isSignUpMode = false;
let cart = [];

// App Init
window.onload = () => {
    updateAuthUI();
    loadProducts();
    if (currentUser) {
        switchTab('products');
    } else {
        showAuthOnly();
    }
};

function showAuthOnly() {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.getElementById('auth-section').style.display = 'block';
}

function updateAuthUI() {
    const div = document.getElementById('auth-status-div');
    if (currentUser) {
        div.innerHTML = `<span>👤 <b>${currentUser}</b></span> <button class="btn btn-outline" onclick="logout()">Logout</button>`;
        document.getElementById('auth-section').style.display = 'none';
    } else {
        div.innerHTML = `<button class="btn btn-outline" onclick="showAuthModal('login')">Login</button>
                         <button class="btn" onclick="showAuthModal('signup')">Sign Up</button>`;
    }
}

function showAuthModal(mode) {
    isSignUpMode = (mode === 'signup');
    toggleAuthModeDisplay();
    showAuthOnly();
}

function toggleAuthMode() {
    isSignUpMode = !isSignUpMode;
    toggleAuthModeDisplay();
}

function toggleAuthModeDisplay() {
    document.getElementById('auth-title').innerText = isSignUpMode ? "Sign Up" : "Login";
    document.getElementById('email-group').style.display = isSignUpMode ? "block" : "none";
    document.getElementById('auth-submit-btn').innerText = isSignUpMode ? "Register" : "Login";
    document.getElementById('auth-toggle-link').innerText = isSignUpMode ? "Already have an account? Login" : "Don't have an account? Sign Up";
}

async function handleAuthSubmit() {
    const username = document.getElementById('auth-user').value;
    const password = document.getElementById('auth-pass').value;
    const email = document.getElementById('auth-email').value;

    const endpoint = isSignUpMode ? "/auth/signup" : "/auth/login";
    const payload = isSignUpMode ? { username, email, password } : { username, password };

    try {
        const res = await fetch(API_URL + endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await res.json();

        if (res.ok) {
            if (isSignUpMode) {
                alert("Account Created! Please Login.");
                toggleAuthMode();
            } else {
                currentUser = data.username;
                localStorage.setItem("username", currentUser);
                updateAuthUI();
                switchTab('products');
            }
        } else {
            alert(data.detail || "Authentication Failed");
        }
    } catch (err) {
        alert("Error connecting to server: " + err);
    }
}

function logout() {
    currentUser = "";
    localStorage.removeItem("username");
    cart = [];
    updateCartCount();
    updateAuthUI();
    showAuthOnly();
}

function switchTab(tabName) {
    if (!currentUser) {
        alert("Please login first!");
        return;
    }
    document.getElementById('auth-section').style.display = 'none';
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('nav button').forEach(el => el.classList.remove('active'));

    document.getElementById(`tab-${tabName}`).classList.add('active');
    
    // Highlight active nav button
    const buttons = document.querySelectorAll('nav button');
    buttons.forEach(btn => {
        if(btn.getAttribute('onclick').includes(tabName)) {
            btn.classList.add('active');
        }
    });

    if (tabName === 'cart') renderCart();
    if (tabName === 'orders') loadOrders();
}

async function loadProducts() {
    try {
        const res = await fetch(API_URL + "/products");
        const data = await res.json();
        const grid = document.getElementById('products-grid');
        grid.innerHTML = data.products.map(p => `
            <div class="product-card">
                <img src="${p.image}">
                <div class="product-card-body">
                    <h3>${p.name}</h3>
                    <p>${p.description}</p>
                    <div class="price">₹${p.price}</div>
                    <button class="btn" onclick="addToCart(${p.id}, '${p.name}', ${p.price})">Add to Cart</button>
                </div>
            </div>
        `).join('');
    } catch (err) {
        console.error(err);
    }
}

function addToCart(id, name, price) {
    const existing = cart.find(item => item.product_id === id);
    if (existing) {
        existing.quantity++;
    } else {
        cart.push({ product_id: id, name, price, quantity: 1 });
    }
    updateCartCount();
    alert(`${name} added to cart!`);
}

function updateCartCount() {
    document.getElementById('cart-count').innerText = cart.reduce((acc, item) => acc + item.quantity, 0);
}

function renderCart() {
    const container = document.getElementById('cart-container');
    if (cart.length === 0) {
        container.innerHTML = "Your cart is empty.";
        return;
    }

    let total = 0;
    let rows = cart.map(i => {
        let subtotal = i.price * i.quantity;
        total += subtotal;
        return `<tr><td>${i.name}</td><td>₹${i.price}</td><td>${i.quantity}</td><td>₹${subtotal}</td></tr>`;
    }).join('');

    container.innerHTML = `
        <table>
            <thead><tr><th>Item</th><th>Price</th><th>Qty</th><th>Subtotal</th></tr></thead>
            <tbody>${rows}</tbody>
        </table>
        <br>
        <h3>Total Amount: ₹${total}</h3>
        <br>
        <button class="btn" onclick="placeOrder(${total})">Checkout & Place Order</button>
    `;
}

async function placeOrder(total) {
    try {
        const res = await fetch(API_URL + "/orders/create", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: currentUser, items: cart, total_amount: total })
        });
        const data = await res.json();
        if (res.ok) {
            alert("Order Placed Successfully! Order ID: " + data.order.order_id);
            cart = [];
            updateCartCount();
            switchTab('orders');
        }
    } catch (err) {
        alert("Order failed: " + err);
    }
}

async function loadOrders() {
    try {
        const res = await fetch(API_URL + `/orders/${currentUser}`);
        const data = await res.json();
        const container = document.getElementById('orders-container');
        if (data.orders.length === 0) {
            container.innerHTML = "No past orders found.";
            return;
        }
        container.innerHTML = data.orders.map(o => `
            <div style="background:white; padding:15px; border-radius:8px; border:1px solid #e2e8f0; margin-bottom:10px;">
                <h4>Order ID: ${o.order_id} — Total: ₹${o.total_amount} (${o.status})</h4>
                <p>Items: ${o.items.map(i => `${i.name} (x${i.quantity})`).join(', ')}</p>
            </div>
        `).join('');
    } catch (err) {
        console.error(err);
    }
}

async function uploadAndDetectVoids() {
    const input = document.getElementById('void-image-input');
    if (!input.files[0]) return alert("Please select an image");

    const formData = new FormData();
    formData.append('file', input.files[0]);

    try {
        const res = await fetch(API_URL + "/predict/voids", { method: 'POST', body: formData });
        const data = await res.json();

        if (data.status === "success") {
            const img = document.getElementById('void-annotated-img');
            img.src = data.annotated_image;
            img.style.display = 'block';
            document.getElementById('void-json-output').innerText = JSON.stringify(data.detections, null, 2);
        }
    } catch (err) {
        alert("Detection failed: " + err);
    }
}

async function analyzeSentiment() {
    const text = document.getElementById('sentiment-text').value;
    try {
        const res = await fetch(API_URL + "/predict/sentiment", {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        const data = await res.json();
        document.getElementById('sentiment-result').innerHTML = `
            <h3>Sentiment: ${data.sentiment}</h3>
            <p>Confidence: ${(data.confidence * 100).toFixed(2)}%</p>
        `;
    } catch (err) {
        alert("Sentiment failed: " + err);
    }
}