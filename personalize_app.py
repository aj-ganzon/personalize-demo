import streamlit as st
import pandas as pd
import requests

st.title("🎯 Article Personalize Recommendations")

# Load metadata CSV
@st.cache_data
def load_items():
    return pd.read_csv("items_dataset.csv")

items_df = load_items()

# Input for User ID
user_id = st.text_input("Enter User ID")

# Lambda API Gateway endpoint
API_URL = "https://keul94hlki.execute-api.us-east-1.amazonaws.com/dev/personalized_smg_poc_demo"

# Optional shared secret (if used in Lambda)
headers = {
    "x-api-client": "my-secret"
}

if user_id:
    try:
        # Call Lambda via API Gateway
        response = requests.post(API_URL, json={"userId": user_id}, headers=headers)

        if response.status_code == 200:
            item_links = response.json().get("itemList", [])

            if item_links:
                st.subheader("📦 Recommended Articles")

                # Convert list of links into a DataFrame to merge with items_df
                recommended_df = pd.DataFrame(item_links, columns=["item_id"])

                # Merge: item_id in CSV contains the link
                # Merge and fill NaNs with "N/A"
                enriched_df = recommended_df.merge(items_df, on="item_id", how="left").fillna("N/A")

                for _, row in enriched_df.iterrows():
                    link = row.get("item_id", "N/A")
                    st.markdown(f"**🔗 Link:** [{link}]({link})", unsafe_allow_html=True)
                    st.markdown(f"**📰 Title:** {row.get('title', 'N/A')}")
                    st.markdown(f"**✍️ Author:** {row.get('author', 'N/A')}")
                    st.markdown(f"**📂 Category:** {row.get('category', 'N/A')}")
                    st.markdown(f"**🏷️ Tags:** {row.get('article_tags', 'N/A')}")
                    st.markdown(f"**🔑 Keywords:** {row.get('article_keywords', 'N/A')}")
                    st.markdown("---")
            else:
                st.warning("No recommendations found.")
        else:
            st.error(f"❌ API Error: {response.status_code} — {response.text}")
    except requests.exceptions.RequestException as e:
        st.error(f"🔌 Network error: {e}")
