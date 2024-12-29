import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import openpyxl

# Set wide layout for mobile/tablet compatibility
st.set_page_config(layout="wide", page_title="Coffee Shop Tracker")

# Initialize session states for orders and expenses
if "orders" not in st.session_state:
    st.session_state.orders = pd.DataFrame(columns=["Order Number", "Date", "Order Type", "Quantity", "Price Per Item", "Total", "Payment Type"])
    st.session_state.current_order = pd.DataFrame(columns=["Order Type", "Quantity", "Price Per Item", "Total"])
    st.session_state.order_id_counter = 1  # Start from 1 for order numbering
if "expenses" not in st.session_state:
    st.session_state.expenses = pd.DataFrame(columns=["Date", "Item Type", "Amount"])

# Function to generate a formatted order ID
def generate_order_id():
    return f"EU{st.session_state.order_id_counter:03d}"

# Predefined prices for items
prices = {
    "Latte": 8.0,
    "Hazelnut Latte": 10.0,
    "Vanilla Latte": 10.0,
    "Caramel Latte": 10.0,
    "Spanish Latte": 10.0,
    "Mocha Latte": 11.0,
    "Caramel Machiatto": 11.0,
    "Creme' Nutty": 12.0,
    "Strawberry Cloudy": 5.0,
    "Beri Angkasa (Blueberry)": 5.0,
    "Mentari Manis (Banana)": 5.0,
    "Sinar Senja (Manga)": 5.0,
    "Hijau Daun (Grenntea)": 5.0,
    "Dewi Melon (HoneyDew)": 5.0,
    "French Fries": 7.0,
    "Cheezy Wedges": 8.0,
    "Popia Carbonara": 8.0
}

# Sidebar navigation
st.sidebar.title("📋 Coffee Shop Tracker")
tabs = st.sidebar.radio("Select Option", ["🛒 New Order", "📊 Manage Orders", "📊 Data & Download", "📈 Accounting"])

# Tab 1: New Order
if tabs == "🛒 New Order":
    st.title("🛒 New Order")
    
    # Add Items to Current Order Section
    with st.expander("Add Items to Current Order", expanded=True):
        order_type = st.selectbox("Order Type", list(prices.keys()))
        quantity = st.number_input("Quantity", min_value=1, value=1, step=1)
        price_per_item = prices[order_type]
        total_price = quantity * price_per_item

        # Button to add items to the current order
        if st.button("Add Item to Current Order"):
            if quantity < 1:
                st.error("Quantity must be at least 1.")
            else:
                new_item = {
                    "Order Type": order_type,
                    "Quantity": quantity,
                    "Price Per Item": price_per_item,
                    "Total": total_price,
                }
                st.session_state.current_order = pd.concat([st.session_state.current_order, pd.DataFrame([new_item])], ignore_index=True)
                st.success(f"Added {quantity} x {order_type} to current order!")

    # Display current order if there are any items added
    if not st.session_state.current_order.empty:
        st.subheader("📝 Current Order")
        st.dataframe(st.session_state.current_order, use_container_width=True)

        # Finalize Order Section
        with st.expander("Finalize Order", expanded=True):
            payment_type = st.selectbox("Payment Type", ["Cash", "Card", "Other"])
            
            # Button to finalize the order
            if st.button("Finalize Order"):
                if st.session_state.current_order.empty:
                    st.error("No items in the current order!")
                else:
                    today_date = datetime.now().strftime("%Y-%m-%d %I:%M:%S %p")
                    order_number = generate_order_id()  # Generate the custom order number
                    total_order_price = st.session_state.current_order["Total"].sum()

                    # Add order to the orders DataFrame
                    for _, row in st.session_state.current_order.iterrows():
                        order_data = row.to_dict()
                        order_data["Order Number"] = order_number
                        order_data["Date"] = today_date
                        order_data["Payment Type"] = payment_type
                        st.session_state.orders = pd.concat([st.session_state.orders, pd.DataFrame([order_data])], ignore_index=True)

                    st.success(f"Order finalized! Order Number: {order_number} | Total: RM {total_order_price:.2f}")
                    
                    # Reset current order and increment the order ID counter
                    st.session_state.current_order = pd.DataFrame(columns=["Order Type", "Quantity", "Price Per Item", "Total"])
                    st.session_state.order_id_counter += 1  # Increment the order ID counter

    # Reset Order ID button (for admin functionality)
    with st.expander("Admin Options", expanded=False):
        confirmation = st.text_input("Type 'RESET' to reset Order ID:", key="reset_confirmation")
        if confirmation == "RESET":
            st.session_state.order_id_counter = 1  # Reset the order ID counter
            st.success("Order ID counter has been reset!")

# Tab 2: Manage Orders
elif tabs == "📊 Manage Orders":
    st.title("📊 Manage Orders")

    # Search Box for Filtering Orders
    search_term = st.text_input("Search by Order Number or Date")
    filtered_orders = st.session_state.orders[
        st.session_state.orders["Order Number"].str.contains(search_term, case=False) |
        st.session_state.orders["Date"].str.contains(search_term, case=False)
    ]

    if not filtered_orders.empty:
        st.dataframe(filtered_orders, use_container_width=True)

        with st.expander("Manage Orders", expanded=True):
            col1, col2 = st.columns(2)

            # Column 1: Delete Specific Order
            with col1:
                st.subheader("Delete Order")
                order_numbers = filtered_orders["Order Number"].unique().tolist()
                selected_order_number = st.selectbox("Select Order Number to Delete", order_numbers, key="delete_order_select")
                if st.button("Delete Selected Order"):
                    st.session_state.orders = st.session_state.orders[
                        st.session_state.orders["Order Number"] != selected_order_number
                    ]
                    st.success(f"Order {selected_order_number} has been deleted!")

            # Column 2: Clear All Orders
            with col2:
                st.subheader("Clear All Orders")
                if st.button("Clear All Orders"):
                    st.session_state.orders = pd.DataFrame(
                        columns=["Order Number", "Date", "Order Type", "Quantity", "Price Per Item", "Total", "Payment Type"]
                    )
                    st.success("All orders have been cleared!")
    else:
        st.warning("No orders available to display or manage.")

# Tab 3: Data & Download
elif tabs == "📊 Data & Download":
    st.title("📊 Order Data")
    st.dataframe(st.session_state.orders, use_container_width=True)

    if st.session_state.orders.empty:
        st.warning("No orders to download.")
    else:
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            # Sheet 1: Orders
            st.session_state.orders.to_excel(writer, index=False, sheet_name="Order")

            # Sheet 2: Accounting
            daily_totals = st.session_state.orders.groupby("Date")["Total"].sum().reset_index()
            accounting_df = pd.DataFrame({
                "Debit (Income)": daily_totals["Total"],
                "Credit (Expenses)": [
                    st.session_state.expenses.groupby("Date")["Amount"].sum().get(date, 0) for date in daily_totals["Date"]
                ]
            }, index=daily_totals["Date"])
            accounting_df.to_excel(writer, sheet_name="Accounting")

            # Sheet 3: Expenses
            st.session_state.expenses.to_excel(writer, index=False, sheet_name="Expenses")

        st.download_button(
            label="Download Excel",
            data=output.getvalue(),
            file_name="coffee_shop_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

# Tab 4: Accounting
elif tabs == "📈 Accounting":
    st.title("📈 Accounting")
    today_date = datetime.now().strftime("%Y-%m-%d")

    # Section 1: View Daily Totals
    if not st.session_state.orders.empty:
        daily_totals = st.session_state.orders.groupby("Date")["Total"].sum().reset_index()
        st.subheader("📅 Daily Totals")
        st.dataframe(daily_totals, use_container_width=True)

    # Section 2: Input Expenses
    st.subheader("📤 Record Expenses")
    with st.expander("Add Monthly Expense", expanded=True):
        expense_item = st.selectbox("Expense Item Type", ["Cup", "Plastic", "Straw", "Other", "Custom"])
        expense_amount = st.number_input("Expense Amount (RM)", min_value=0.0, step=0.01)

        if expense_item == "Custom":
            expense_item = st.text_input("Enter Custom Expense Type")
        
        if st.button("Add Expense"):
            if expense_amount <= 0:
                st.error("Expense amount must be greater than 0.")
            else:
                expense_data = {
                    "Date": today_date,
                    "Item Type": expense_item,
                    "Amount": expense_amount,
                }
                st.session_state.expenses = pd.concat(
                    [st.session_state.expenses, pd.DataFrame([expense_data])], ignore_index=True
                )
                st.success(f"Added expense: {expense_item} - RM {expense_amount:.2f}")

    # Display Expenses
    if not st.session_state.expenses.empty:
        st.subheader("💳 Recorded Expenses")
        st.dataframe(st.session_state.expenses, use_container_width=True)

    # Section 3: Summary Metrics
    if not st.session_state.orders.empty:
        total_income = st.session_state.orders["Total"].sum()
        total_expenses = st.session_state.expenses["Amount"].sum() if not st.session_state.expenses.empty else 0
        net_profit = total_income - total_expenses

        st.subheader("💰 Summary")
        st.metric("Total Debit (Income)", f"RM {total_income:.2f}")
        st.metric("Total Credit (Expenses)", f"RM {total_expenses:.2f}")
        st.metric("Net Profit", f"RM {net_profit:.2f}")
