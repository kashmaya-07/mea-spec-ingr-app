import streamlit as st
import pandas as pd
import plotly.express as px

# =========================================
# PAGE CONFIG
# =========================================

st.set_page_config(
    page_title="Ingredient Intelligence System",
    layout="wide"
)

# =========================================
# TITLE
# =========================================

st.title("Ingredient Intelligence System")

st.markdown("""
Analyze ingredient usage, company overlaps, product intersections, and ingredient intelligence.
""")

st.markdown("---")

# =========================================
# LOAD EXCEL
# =========================================

FILE_PATH = "meaf.xlsx"

xls = pd.ExcelFile(FILE_PATH)

sheet_name = xls.sheet_names[0]

df = pd.read_excel(FILE_PATH, sheet_name=sheet_name)

# =========================================
# CLEAN COLUMNS
# =========================================

df.columns = df.columns.str.strip()

# =========================================
# COLUMN CHECK
# =========================================

st.sidebar.header("Ingredient Filters")

required_cols = [
    "Ingredient",
    "Company",
    "Product",
    "Brand"
]

missing = [c for c in required_cols if c not in df.columns]

if len(missing) > 0:
    st.error(f"Missing columns: {missing}")
    st.stop()

# =========================================
# FILTERS
# =========================================

ingredients = sorted(df["Ingredient"].dropna().unique())

selected_ingredients = st.sidebar.multiselect(
    "Select Ingredients",
    ingredients
)

filtered_df = df.copy()

if selected_ingredients:
    filtered_df = filtered_df[
        filtered_df["Ingredient"].isin(selected_ingredients)
    ]

# =========================================
# INGREDIENT SUMMARY
# =========================================

st.header("Ingredient Summary")

summary = (
    df.groupby("Ingredient")
    .agg(
        Unique_Companies=("Company", "nunique"),
        Unique_Products=("Product", "nunique"),
        Unique_Brands=("Brand", "nunique")
    )
    .reset_index()
)

st.dataframe(summary, use_container_width=True)

st.markdown("---")

# =========================================
# COMPANY → INGREDIENTS USED
# =========================================

st.header("Company → Ingredients Used")

company_ing = (
    filtered_df.groupby("Company")
    .agg({
        "Ingredient": lambda x: ", ".join(sorted(set(x)))
    })
    .reset_index()
)

company_ing["Ingredient Count"] = (
    company_ing["Ingredient"]
    .apply(lambda x: len(x.split(",")))
)

company_ing = company_ing.rename(
    columns={
        "Ingredient": "Ingredients Used"
    }
)

st.dataframe(
    company_ing,
    use_container_width=True
)

st.markdown("---")

# =========================================
# MULTI INGREDIENT INTERSECTION
# =========================================

st.header("Multi Ingredient Intersection")

if len(selected_ingredients) >= 2:

    grouped = (
        df.groupby("Company")["Ingredient"]
        .apply(set)
        .reset_index()
    )

    common_companies = grouped[
        grouped["Ingredient"].apply(
            lambda x: all(
                ingr in x for ingr in selected_ingredients
            )
        )
    ]

    st.metric(
        "Common Companies",
        len(common_companies)
    )

    st.subheader("Common Companies")

    display_df = common_companies.copy()

    display_df["Ingredient"] = len(selected_ingredients)

    st.dataframe(
        display_df,
        use_container_width=True
    )

    # =====================================
    # COMMON PRODUCTS
    # =====================================

    temp = df[
        df["Ingredient"].isin(selected_ingredients)
    ]

    product_counts = (
        temp.groupby("Product")["Ingredient"]
        .nunique()
        .reset_index()
    )

    common_products = product_counts[
        product_counts["Ingredient"] == len(selected_ingredients)
    ]

    final_products = temp[
        temp["Product"].isin(common_products["Product"])
    ]

    st.metric(
        "Common Products",
        common_products.shape[0]
    )

    st.subheader("Common Products")

    cols_to_show = [
        "Product",
        "Brand",
        "Company",
        "Ingredient"
    ]

    existing_cols = [
        c for c in cols_to_show
        if c in final_products.columns
    ]

    st.dataframe(
        final_products[existing_cols],
        use_container_width=True
    )

else:

    st.info("Select at least 2 ingredients")

st.markdown("---")

# =========================================
# TOP COMPANIES
# =========================================

st.header("Top Companies")

top_companies = (
    filtered_df.groupby("Company")["Product"]
    .nunique()
    .reset_index()
)

top_companies.columns = [
    "Company",
    "Products"
]

top_companies = top_companies.sort_values(
    by="Products",
    ascending=False
).head(15)

fig = px.bar(
    top_companies,
    x="Products",
    y="Company",
    orientation="h",
    title="Top Companies by Products"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =========================================
# INGREDIENT DISTRIBUTION
# =========================================

st.header("Ingredient Distribution")

ingredient_dist = (
    filtered_df["Ingredient"]
    .value_counts()
    .reset_index()
)

ingredient_dist.columns = [
    "Ingredient",
    "Count"
]

fig2 = px.pie(
    ingredient_dist,
    names="Ingredient",
    values="Count",
    hole=0.5
)

st.plotly_chart(
    fig2,
    use_container_width=True
)

# =========================================
# DOWNLOAD
# =========================================

csv = filtered_df.to_csv(index=False)

st.download_button(
    label="Download Filtered Data",
    data=csv,
    file_name="ingredient_intelligence.csv",
    mime="text/csv"
)