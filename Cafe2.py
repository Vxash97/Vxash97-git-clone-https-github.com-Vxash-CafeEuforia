import streamlit as st
import pandas as pd
from io import BytesIO
import io
from datetime import datetime
import os

# File paths for storing the data
orders_file = "orders.csv"
expenses_file = "expenses.csv"
# Add a new CSV file for inventory
inventory_file = "inventory.csv"

# Set wide layout for mobile/tablet compatibility
st.set_page_config(layout="wide", page_title="Coffee Shop Tracker")

# Function to load data from CSV files
def load_data():
    if os.path.exists(orders_file):
        st.session_state.orders = pd.read_csv(orders_file)
    else:
        st.session_state.orders = pd.DataFrame(columns=["Order Number", "Date", "Order Type", "Quantity", "Price Per Item", "Total", "Payment Type"])

    if os.path.exists(expenses_file):
        st.session_state.expenses = pd.read_csv(expenses_file)
    else:
        st.session_state.expenses = pd.DataFrame(columns=["Date", "Item Type", "Amount"])

# Function to save data to CSV files
def save_data():
    st.session_state.orders.to_csv(orders_file, index=False)
    st.session_state.expenses.to_csv(expenses_file, index=False)

# Initialize session states for orders and expenses
if "orders" not in st.session_state:
    load_data()

if "current_order" not in st.session_state:
    st.session_state.current_order = pd.DataFrame(columns=["Order Type", "Quantity", "Price Per Item", "Total"])

if "order_id_counter" not in st.session_state:
    st.session_state.order_id_counter = len(st.session_state.orders) + 1  # Set counter based on existing orders

# Function to generate a formatted order ID
def generate_order_id():
    return f"EU{st.session_state.order_id_counter:03d}"

# Function to load inventory data
def load_inventory():
    if os.path.exists(inventory_file):
        st.session_state.inventory = pd.read_csv(inventory_file)
    else:
        # Initialize with default values if the file doesn't exist
        default_inventory = {
            "Item": ["Cup", "Cup Cover", "Straw", "Plastic", "Box"], 
            "Quantity": [0, 0, 0, 0, 0]
        }
        st.session_state.inventory = pd.DataFrame(default_inventory)
        save_inventory()  # Save to file if not exists

# Function to save inventory data
def save_inventory():
    st.session_state.inventory.to_csv(inventory_file, index=False)

# Initialize inventory state
if "inventory" not in st.session_state:
    load_inventory()

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
tabs = st.sidebar.radio("Select Option", ["🛒 New Order", "📊 Manage Orders", "📈 Accounting", "📋 Data & Download", "📦 Inventory"])

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

            # Display the current order
        if not st.session_state.current_order.empty:
            st.subheader("Current Order")
            st.table(st.session_state.current_order)

        # Finalize Order Section
        if not st.session_state.current_order.empty:
            payment_type = st.selectbox("Payment Type", ["Cash", "Online Payment", "Other"])
            
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

                    # Deduct inventory based on order quantity
                    for _, row in st.session_state.current_order.iterrows():
                        order_type = row["Order Type"]
                        # Check if the order type contains the word "Latte" or other predefined types
                        if "Latte" in row["Order Type"]:  # Assuming all coffee types require these items
                            st.session_state.inventory.loc[st.session_state.inventory["Item"] == "Cup", "Quantity"] -= row["Quantity"]
                            st.session_state.inventory.loc[st.session_state.inventory["Item"] == "Cup Cover", "Quantity"] -= row["Quantity"]
                            st.session_state.inventory.loc[st.session_state.inventory["Item"] == "Straw", "Quantity"] -= row["Quantity"]

                        elif "Caramel Machiatto" in order_type:
                            st.session_state.inventory.loc[st.session_state.inventory["Item"] == "Cup", "Quantity"] -= row["Quantity"]
                            st.session_state.inventory.loc[st.session_state.inventory["Item"] == "Cup Cover", "Quantity"] -= row["Quantity"]
                            st.session_state.inventory.loc[st.session_state.inventory["Item"] == "Straw", "Quantity"] -= row["Quantity"]
                        
                        elif "Creme' Nutty" in order_type:
                            st.session_state.inventory.loc[st.session_state.inventory["Item"] == "Cup", "Quantity"] -= row["Quantity"]
                            st.session_state.inventory.loc[st.session_state.inventory["Item"] == "Cup Cover", "Quantity"] -= row["Quantity"]
                            st.session_state.inventory.loc[st.session_state.inventory["Item"] == "Straw", "Quantity"] -= row["Quantity"]

                        elif "Strawberry Cloudy" in order_type:
                            st.session_state.inventory.loc[st.session_state.inventory["Item"] == "Plastic", "Quantity"] -= row["Quantity"]

                        elif "Beri Angkasa (Blueberry)" in order_type:
                            st.session_state.inventory.loc[st.session_state.inventory["Item"] == "Plastic", "Quantity"] -= row["Quantity"]

                        elif "Mentari Manis (Banana)" in order_type:
                            st.session_state.inventory.loc[st.session_state.inventory["Item"] == "Plastic", "Quantity"] -= row["Quantity"]

                        elif "Sinar Senja (Manga)" in order_type:
                            st.session_state.inventory.loc[st.session_state.inventory["Item"] == "Plastic", "Quantity"] -= row["Quantity"]

                        elif "Hijau Daun (Grenntea)" in order_type:
                            st.session_state.inventory.loc[st.session_state.inventory["Item"] == "Plastic", "Quantity"] -= row["Quantity"]

                        elif "Dewi Melon (HoneyDew)" in order_type:
                            st.session_state.inventory.loc[st.session_state.inventory["Item"] == "Plastic", "Quantity"] -= row["Quantity"]

                        elif "French Fries" in order_type:
                            st.session_state.inventory.loc[st.session_state.inventory["Item"] == "Box", "Quantity"] -= row["Quantity"]

                        elif "Cheezy Wedges" in order_type:
                            st.session_state.inventory.loc[st.session_state.inventory["Item"] == "Box", "Quantity"] -= row["Quantity"]

                        elif "Popia Carbonara" in order_type:
                            st.session_state.inventory.loc[st.session_state.inventory["Item"] == "Box", "Quantity"] -= row["Quantity"]

                    # Save inventory to session or database
                    save_inventory()

                    # Low inventory check
                    low_inventory = st.session_state.inventory[st.session_state.inventory["Quantity"] < 10]
                    if not low_inventory.empty:
                        st.warning("Low inventory detected for the following items:")
                        st.table(low_inventory)

                    st.success(f"Order finalized! Order Number: {order_number} | Total: RM {total_order_price:.2f}")
                    
                    # Reset current order and increment the order ID counter
                    st.session_state.current_order = pd.DataFrame(columns=["Order Type", "Quantity", "Price Per Item", "Total"])
                    st.session_state.order_id_counter += 1  # Increment the order ID counter

                    # Save the updated orders to file
                    save_data()

    # # Display current order if there are any items added
    # if not st.session_state.current_order.empty:
    #     st.subheader("📝 Current Order")
    #     st.dataframe(st.session_state.current_order, use_container_width=True)


    # Admin Options - Reset Order ID Counter
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

                    # Save the updated orders to file
                    save_data()

            # Column 2: Clear All Orders
            with col2:
                st.subheader("Clear All Orders")
                if st.button("Clear All Orders"):
                    st.session_state.orders = pd.DataFrame(
                        columns=["Order Number", "Date", "Order Type", "Quantity", "Price Per Item", "Total", "Payment Type"]
                    )
                    st.success("All orders have been cleared!")

                    # Save the updated orders to file
                    save_data()
    else:
        st.warning("No orders available to display or manage.")

# Tab 4: Accounting
elif tabs == "📈 Accounting":
    st.title("📈 Accounting")
    today_date = datetime.now().strftime("%Y-%m-%d")

    # Section 1: View Daily Totals
    if not st.session_state.orders.empty:
        # Group by "Date" and aggregate "Total" and "Order Number"
        daily_totals = (st.session_state.orders.groupby("Date").agg(Total=("Total", "sum"),Order_IDs=("Order Number", lambda x: ", ".join(map(str, x.unique())))).reset_index())
        # Display the dataframe
        st.subheader("📅 Daily Totals")
        st.dataframe(daily_totals, use_container_width=True)

    # Section 2: Input Expenses
    st.subheader("📤 Record Expenses")
    with st.expander("Add Monthly Expense", expanded=True):
        col1, col2 = st.columns([3, 1])  # Two columns: one for adding expenses, one for deleting expenses

        # Column 1: Add Expense
        with col1:
            expense_item = st.text_input("Expense Item Type")
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

                    # Save the updated expenses to file
                    save_data()

        # Column 2: Delete Expense
        with col2:
            if not st.session_state.expenses.empty:
                expense_to_delete = st.selectbox("Select Expense to Delete", st.session_state.expenses["Item Type"].unique())
                if st.button("Delete Expense"):
                    # Check if the selected expense exists and delete it
                    if expense_to_delete:
                        st.session_state.expenses = st.session_state.expenses[st.session_state.expenses["Item Type"] != expense_to_delete]
                        st.success(f"Expense '{expense_to_delete}' deleted successfully!")

                        # Save the updated expenses to file
                        save_data()
                    else:
                        st.error("Please select an expense to delete.")

        # Display Expenses
        if not st.session_state.expenses.empty:
            st.subheader("💳 Recorded Expenses")
            st.dataframe(st.session_state.expenses, use_container_width=True)


    # Section 3: Summary Metrics
    if not st.session_state.orders.empty:
        total_income = st.session_state.orders["Total"].sum()
        total_expenses = st.session_state.expenses["Amount"].sum()
        net_profit = total_income - total_expenses
        st.subheader("💸 Summary")
        st.write(f"Total Income: RM {total_income:.2f}")
        st.write(f"Total Expenses: RM {total_expenses:.2f}")
        st.write(f"Net Profit: RM {net_profit:.2f}")

# Tab 3: Data & Download
elif tabs == "📋 Data & Download":
    st.title("📊 Order Data")
    st.dataframe(st.session_state.orders, use_container_width=True)
    st.title("📊 Expenses Data")
    st.dataframe(st.session_state.expenses, use_container_width=True)

    if st.session_state.orders.empty:
        st.warning("No orders to download.")
    else:
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            # Sheet 1: Orders
            st.session_state.orders.to_excel(writer, index=False, sheet_name="Order")

            # Sheet 2: Expenses
            st.session_state.expenses.to_excel(writer, index=False, sheet_name="Expenses")

            # Sheet 3: Accounting
            # Group by month without modifying the original data
            # Convert the "Date" column to datetime and extract the year-month for grouping
            monthly_income = st.session_state.orders.groupby(pd.to_datetime(st.session_state.orders['Date']).dt.to_period('M'))["Total"].sum().reset_index()
            monthly_expenses = st.session_state.expenses.groupby(pd.to_datetime(st.session_state.expenses['Date']).dt.to_period('M'))["Amount"].sum().reset_index()

            # Merge the income and expenses dataframes
            monthly_accounting_df = pd.merge(monthly_income, monthly_expenses, left_on='Date', right_on='Date', how="outer").fillna(0)
            monthly_accounting_df.columns = ["Date", "Debit (Income)", "Credit (Expenses)"]

            # Save the monthly accounting data to the Accounting sheet
            monthly_accounting_df.to_excel(writer, sheet_name="Accounting", index=False)

        st.download_button(
            label="Download Excel",
            data=output.getvalue(),
            file_name="coffee_shop_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

# New Tab: Inventory Management
elif tabs == "📦 Inventory":
    st.title("📦 Inventory Management")

    # Display current inventory
    st.subheader("Current Inventory")
    st.dataframe(st.session_state.inventory, use_container_width=True)

    # Update inventory
    st.subheader("Update Inventory")
    with st.form("inventory_form"):
        inventory_updates = {}
        for _, row in st.session_state.inventory.iterrows():
            item = row["Item"]
            current_qty = row["Quantity"]
            new_qty = st.number_input(f"{item} Quantity", min_value=0, value=int(current_qty), step=1, key=item)
            inventory_updates[item] = new_qty

        if st.form_submit_button("Update Inventory"):
            for item, qty in inventory_updates.items():
                st.session_state.inventory.loc[st.session_state.inventory["Item"] == item, "Quantity"] = qty
            save_inventory()
            st.success("Inventory updated successfully!")
