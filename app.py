import streamlit as st
import google.generativeai as genai
from supabase_client import supabase
from datetime import date

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")
st.title("💰 Finance App")

# --- ADD EXPENSE FORM ---
st.subheader("Add Expense")

amount = st.number_input("Amount (R)", min_value=0.0, format="%.2f")
category = st.selectbox("Category", ["Food", "Transport", "Entertainment", "Shopping", "Bills", "Other"])
description = st.text_input("Description")
expense_date = st.date_input("Date", value=date.today())

if st.button("Add Expense"):
    if amount == 0:
        st.warning("Please enter an amount.")
    elif description == "":
        st.warning("Please enter a description.")
    else:
        data = {
            "amount": amount,
            "category": category,
            "description": description,
            "date": str(expense_date),
            "user_id": "00000000-0000-0000-0000-000000000001"
        }
        supabase.table("expenses").insert(data).execute()
        st.success("Expense added! ✅")
        st.rerun()

# --- FETCH EXPENSES ---
response = supabase.table("expenses").select("*").order("date", desc=True).execute()
expenses = response.data

# --- SPENDING SUMMARY ---
st.subheader("Spending Summary")

if len(expenses) == 0:
    st.info("No expenses yet. Add one above!")
else:
    # Calculate total per category
    summary = {}
    for expense in expenses:
        cat = expense["category"]
        amt = expense["amount"]
        summary[cat] = summary.get(cat, 0) + amt

    # Display summary boxes
    cols = st.columns(len(summary))
    for i, (cat, total) in enumerate(summary.items()):
        with cols[i]:
            st.metric(label=cat, value=f"R {total:.2f}")

    # Total spent
    total_spent = sum(summary.values())
    st.markdown(f"### Total Spent: R {total_spent:.2f}")

# --- VIEW EXPENSES TABLE ---
st.subheader("Your Expenses")

if len(expenses) == 0:
    st.info("No expenses yet.")
else:
    # Clean up columns for display
    clean = []
    for e in expenses:
        clean.append({
            "Date": e["date"],
            "Category": e["category"],
            "Description": e["description"],
            "Amount (R)": f"R {e['amount']:.2f}"
        })
    st.table(clean)
    # --- AI INSIGHTS ---
st.subheader("🤖 AI Spending Insights")

if st.button("Analyse My Spending"):
    if len(expenses) == 0:
        st.warning("Add some expenses first!")
    else:
        summary_text = "\n".join([f"{cat}: R{total:.2f}" for cat, total in summary.items()])
        prompt = f"""
        Here is my spending this month:
        {summary_text}
        Total spent: R{total_spent:.2f}

        Please give me:
        1. A brief analysis of my spending
        2. Which category I should cut back on
        3. One practical money saving tip for a student in South Africa
        Keep it short and friendly.
        """

    

        with st.spinner("Analysing your spending..."):
            response = model.generate_content(prompt)
            st.info(response.text)