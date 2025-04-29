# Install needed libraries first
# pip install streamlit pandas mlxtend

import streamlit as st
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules
import time

# --- Dataset ---
dataset = [
    ['Bread', 'Milk', 'Butter'],
    ['Bread', 'Diaper', 'Beer', 'Eggs'],
    ['Milk', 'Diaper', 'Beer', 'Cola', 'Chips'],
    ['Bread', 'Milk', 'Diaper', 'Beer', 'Eggs'],
    ['Bread', 'Milk', 'Diaper', 'Cola'],
    ['Fruits', 'Vegetables', 'Milk'],
    ['Bread', 'Butter', 'Jam', 'Eggs'],
    ['Cola', 'Chips', 'Chocolate'],
    ['Beer', 'Chips', 'Nuts'],
    ['Fruits', 'Chocolate', 'Ice Cream']
]

# --- Preprocess ---
te = TransactionEncoder()
te_data = te.fit(dataset).transform(dataset)
df = pd.DataFrame(te_data, columns=te.columns_)

# --- Apply Apriori ---
frequent_itemsets = apriori(df, min_support=0.2, use_colnames=True)
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)

# --- Build Top Popular Items List ---
item_counts = df.sum().sort_values(ascending=False)
top_items = item_counts.index.tolist()

# --- Recommendation Function ---
def recommend(selected_items, top_n=3):
    selected_items = set(selected_items)
    recommendations = []

    # Find based on rules
    for idx, row in rules.iterrows():
        if selected_items.issubset(row['antecedents']):
            for consequent in row['consequents']:
                recommendations.append((consequent, row['confidence']))

    if recommendations:
        rec_df = pd.DataFrame(recommendations, columns=['Item', 'Confidence'])
        rec_df = rec_df.groupby('Item').max().sort_values(by='Confidence', ascending=False).reset_index()
        return rec_df.head(top_n)
    else:
        # No rule found → Suggest most popular item NOT already selected
        fallback_recs = []
        for item in top_items:
            if item not in selected_items:
                fallback_recs.append({'Item': item, 'Confidence': 0.5})  # Dummy confidence
            if len(fallback_recs) >= top_n:
                break
        return pd.DataFrame(fallback_recs)

# --- Streamlit App ---
st.title('🛒 Grocery Product Recommender')

# Show available grocery items (no images now)
st.subheader("Available Grocery Items:")
st.write(", ".join(sorted(df.columns.tolist())))

# User Selection
selected_items = st.multiselect(
    "🛍️ Select the items you already have:",
    options=sorted(df.columns.tolist())
)

# Get Recommendations
if st.button("🎯 Get Recommendations"):
    if selected_items:
        with st.spinner('🔎 Finding the best products...'):
            time.sleep(1)
            recommendations = recommend(selected_items, top_n=3)

        if not recommendations.empty:
            st.success("✨ Recommended Products:")
            for idx, row in recommendations.iterrows():
                item = row['Item']
                confidence = row['Confidence']

                # Show product with highlighted style
                st.markdown(f"<div style='background-color: #E2F7D9; padding: 10px; border-radius: 5px;'>"
                            f"<strong style='font-size: 18px; color: #388E3C;'>{item}</strong> - "
                            f"<span style='font-size: 16px; color: #388E3C;'>Confidence: {confidence:.2f}</span></div>", 
                            unsafe_allow_html=True)

        else:
            st.info("✅ You already have good items!")
    else:
        st.error("⚠️ Please select at least one item!")

# Show sample data
with st.expander("🔍 See Sample Grocery Transactions"):
    st.dataframe(df)
