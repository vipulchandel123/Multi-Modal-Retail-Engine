import streamlit as st
import requests
import pandas as pd
import base64
from PIL import Image
import io

st.set_page_config(
    page_title="Multi-Modal AI & E-Commerce Suite",
    layout="wide",
    initial_sidebar_state="expanded"
)

BACKEND_URL = "http://127.0.0.1:8000"

# Initialize Session State
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "cart" not in st.session_state:
    st.session_state.cart = []  # List of items: {id, name, price, quantity}

# Sidebar: User Auth & Backend Connection Check
st.sidebar.title("🔐 Account & System Status")

try:
    res = requests.get(f"{BACKEND_URL}/docs", timeout=2)
    if res.status_code == 200:
        st.sidebar.success("⚡ Backend Connected")
    else:
        st.sidebar.warning("⚠️ Backend status issue")
except Exception:
    st.sidebar.error("❌ Backend Disconnected")

# Authentication Interface
if not st.session_state.logged_in:
    auth_choice = st.sidebar.radio("Authentication", ["Login", "Sign Up"])
    
    if auth_choice == "Login":
        st.sidebar.subheader("Login to Account")
        login_user = st.sidebar.text_input("Username", value="admin")
        login_pass = st.sidebar.text_input("Password", type="password", value="secretrootpass")
        if st.sidebar.button("Login", type="primary"):
            try:
                resp = requests.post(f"{BACKEND_URL}/auth/login", json={"username": login_user, "password": login_pass})
                if resp.status_code == 200:
                    data = resp.json()
                    st.session_state.logged_in = True
                    st.session_state.username = data.get("username")
                    st.sidebar.success(f"Welcome, {login_user}!")
                    st.rerun()
                else:
                    st.sidebar.error(resp.json().get("detail", "Login failed"))
            except Exception as e:
                st.sidebar.error(f"Error: {e}")

    elif auth_choice == "Sign Up":
        st.sidebar.subheader("Create New Account")
        new_user = st.sidebar.text_input("Username")
        new_email = st.sidebar.text_input("Email")
        new_pass = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Register"):
            try:
                resp = requests.post(f"{BACKEND_URL}/auth/signup", json={"username": new_user, "email": new_email, "password": new_pass})
                if resp.status_code == 200:
                    st.sidebar.success("Registration Successful! Please switch to Login.")
                else:
                    st.sidebar.error(resp.json().get("detail", "Signup failed"))
            except Exception as e:
                st.sidebar.error(f"Error: {e}")

else:
    st.sidebar.write(f"👤 Logged in as: **{st.session_state.username}**")
    cart_count = sum(item["quantity"] for item in st.session_state.cart)
    st.sidebar.write(f"🛒 Cart Items: **{cart_count}**")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.session_state.cart = []
        st.rerun()

# MAIN APPLICATION INTERFACE
st.title("🛒 Multi-Modal AI & E-Commerce Suite")

if not st.session_state.logged_in:
    st.info("👈 Please **Login** or **Sign Up** from the sidebar to browse products, manage cart, and place orders.")
else:
    # 5 Major Navigation Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🛍️ Products Catalog",
        "🛒 Shopping Cart",
        "📦 My Orders",
        "🔍 Void Detection (AI)",
        "📝 Sentiment Analysis (AI)"
    ])

    # --- TAB 1: PRODUCTS CATALOG ---
    with tab1:
        st.header("Product Catalog & Store")
        try:
            p_resp = requests.get(f"{BACKEND_URL}/products")
            if p_resp.status_code == 200:
                products = p_resp.json().get("products", [])
                
                cols = st.columns(2)
                for idx, prod in enumerate(products):
                    with cols[idx % 2]:
                        with st.container(border=True):
                            st.image(prod["image"], use_container_width=True)
                            st.subheader(prod["name"])
                            st.caption(f"Category: {prod['category']}")
                            st.write(prod["description"])
                            st.markdown(f"### ₹{prod['price']:,.2f}")
                            
                            if st.button(f"Add to Cart", key=f"add_{prod['id']}"):
                                existing = next((item for item in st.session_state.cart if item["product_id"] == prod["id"]), None)
                                if existing:
                                    existing["quantity"] += 1
                                else:
                                    st.session_state.cart.append({
                                        "product_id": prod["id"],
                                        "name": prod["name"],
                                        "price": prod["price"],
                                        "quantity": 1
                                    })
                                st.success(f"Added {prod['name']} to cart!")
                                st.rerun()
            else:
                st.error("Failed to load products from API.")
        except Exception as e:
            st.error(f"Error fetching products: {e}")

    # --- TAB 2: SHOPPING CART ---
    with tab2:
        st.header("Your Shopping Cart")
        if not st.session_state.cart:
            st.info("Your cart is empty. Browse the Product Catalog to add items!")
        else:
            cart_data = []
            total_cart_val = 0.0
            
            for item in st.session_state.cart:
                subtotal = item["price"] * item["quantity"]
                total_cart_val += subtotal
                cart_data.append({
                    "Product ID": item["product_id"],
                    "Item Name": item["name"],
                    "Price": f"₹{item['price']:,.2f}",
                    "Quantity": item["quantity"],
                    "Subtotal": f"₹{subtotal:,.2f}"
                })
            
            st.dataframe(pd.DataFrame(cart_data), use_container_width=True)
            st.markdown(f"### **Total Amount: ₹{total_cart_val:,.2f}**")
            
            col_c1, col_c2 = st.columns([1, 4])
            with col_c1:
                if st.button("Clear Cart"):
                    st.session_state.cart = []
                    st.rerun()
            with col_c2:
                if st.button("🚀 Checkout & Place Order", type="primary"):
                    payload = {
                        "username": st.session_state.username,
                        "items": st.session_state.cart,
                        "total_amount": total_cart_val
                    }
                    try:
                        o_resp = requests.post(f"{BACKEND_URL}/orders/create", json=payload)
                        if o_resp.status_code == 200:
                            res_data = o_resp.json()
                            st.balloons()
                            st.success(f"Order Placed! Order ID: {res_data['order']['order_id']}")
                            st.session_state.cart = []
                        else:
                            st.error(f"Failed to create order: {o_resp.text}")
                    except Exception as e:
                        st.error(f"Error placing order: {e}")

    # --- TAB 3: MY ORDERS ---
    with tab3:
        st.header("Order History")
        try:
            ord_resp = requests.get(f"{BACKEND_URL}/orders/{st.session_state.username}")
            if ord_resp.status_code == 200:
                orders = ord_resp.json().get("orders", [])
                if not orders:
                    st.info("No past orders found.")
                else:
                    for order in orders:
                        with st.expander(f"📦 Order ID: {order['order_id']} — Total: ₹{order['total_amount']:,.2f} ({order['status']})"):
                            st.write(f"**Customer:** {order['username']}")
                            st.write("**Items:**")
                            st.json(order["items"])
            else:
                st.error("Could not retrieve orders.")
        except Exception as e:
            st.error(f"Error: {e}")

    # --- TAB 4: YOLO VOID DETECTION (AI) ---
    with tab4:
        st.header("Retail Shelf Void Detection (YOLOv8)")
        uploaded_file = st.file_uploader("Upload shelf image", type=["jpg", "jpeg", "png"])
        if uploaded_file is not None:
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Original Image")
                st.image(uploaded_file, use_container_width=True)
                
            if st.button("Analyze Voids"):
                files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                try:
                    v_resp = requests.post(f"{BACKEND_URL}/predict/voids", files=files)
                    if v_resp.status_code == 200:
                        v_data = v_resp.json()
                        if v_data.get("status") == "success":
                            with c2:
                                st.subheader("Annotated Preview")
                                img_bytes = base64.b64decode(v_data.get("annotated_image").split(",")[1])
                                st.image(Image.open(io.BytesIO(img_bytes)), use_container_width=True)
                            st.json(v_data.get("detections"))
                        else:
                            st.error(v_data.get("message"))
                except Exception as e:
                    st.error(f"Error: {e}")

    # --- TAB 5: SENTIMENT ANALYSIS (AI) ---
    with tab5:
        st.header("Feedback Sentiment Analysis")
        user_text = st.text_area("Customer review text:", "Great quality product!")
        if st.button("Analyze"):
            try:
                s_resp = requests.post(f"{BACKEND_URL}/predict/sentiment", json={"text": user_text})
                if s_resp.status_code == 200:
                    st.json(s_resp.json())
            except Exception as e:
                st.error(f"Error: {e}")