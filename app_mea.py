import streamlit as st
import pandas as pd

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Middle East Ingredient Intelligence",
    layout="wide"
)

# =========================================================
# TITLE
# =========================================================

st.title("Middle East Ingredient Intelligence")

st.markdown("""
Ingredient analysis system for:
- Products
- Companies
- Brands
- Ingredient intersections
- Common products
- Common companies
""")

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_data():

    df = pd.read_excel(
        "middleeast_africa.xlsx"
    )

    # -----------------------------------------------------
    # CLEAN COLUMN NAMES
    # -----------------------------------------------------

    df.columns = (
        df.columns
        .str.strip()
    )

    # -----------------------------------------------------
    # STANDARDIZE COLUMN NAMES
    # -----------------------------------------------------

    new_cols = {}

    for col in df.columns:

        c = col.lower()

        if 'product' in c:
            new_cols[col] = 'Product'

        elif 'brand' in c:
            new_cols[col] = 'Brand'

        elif 'ultimate' in c:
            new_cols[col] = 'Ultimate Company'

        elif 'company' in c:
            new_cols[col] = 'Company'

        elif 'country' in c:
            new_cols[col] = 'Country'

        elif 'state' in c:
            new_cols[col] = 'State'

        elif 'sub-category' in c:
            new_cols[col] = 'Sub-Category'

        elif 'category' in c:
            new_cols[col] = 'Category'

        elif 'ingredient' in c or 'ingr' in c:
            new_cols[col] = 'Ingredient'

    df = df.rename(
        columns=new_cols
    )

    # -----------------------------------------------------
    # REMOVE DUPLICATE COLUMNS
    # -----------------------------------------------------

    df = df.loc[
        :,
        ~df.columns.duplicated()
    ]

    # -----------------------------------------------------
    # CLEAN VALUES
    # -----------------------------------------------------

    for col in df.columns:

        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
        )

    # -----------------------------------------------------
    # REMOVE DUPLICATES
    # -----------------------------------------------------

    df = df.drop_duplicates()

    return df

# =========================================================
# LOAD DATAFRAME
# =========================================================

master_df = load_data()

# =========================================================
# SIDEBAR FILTER
# =========================================================

st.sidebar.header("Ingredient Filters")

all_ingredients = sorted(
    master_df['Ingredient']
    .dropna()
    .unique()
)

selected_ingredients = st.sidebar.multiselect(
    "Select Ingredients",
    all_ingredients
)

# =========================================================
# INGREDIENT SUMMARY
# =========================================================

st.divider()

st.subheader("Ingredient Summary")

ingredient_summary = (

    master_df.groupby('Ingredient')
    .agg({

        'Product': 'nunique',
        'Company': 'nunique',
        'Brand': 'nunique'

    })
    .reset_index()

)

ingredient_summary.columns = [

    'Ingredient',
    'Unique Products',
    'Unique Companies',
    'Unique Brands'

]

ingredient_summary = ingredient_summary.sort_values(
    by='Unique Products',
    ascending=False
)

st.dataframe(
    ingredient_summary,
    use_container_width=True
)

# =========================================================
# SINGLE INGREDIENT ANALYSIS
# =========================================================

if len(selected_ingredients) == 1:

    selected_ingr = selected_ingredients[0]

    temp = master_df[
        master_df['Ingredient']
        == selected_ingr
    ]

    st.divider()

    st.header(f"{selected_ingr} Analysis")

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Products",
            temp['Product'].nunique()
        )

    with c2:

        st.metric(
            "Companies",
            temp['Company'].nunique()
        )

    with c3:

        st.metric(
            "Brands",
            temp['Brand'].nunique()
        )

    # -----------------------------------------------------
    # COMPANIES
    # -----------------------------------------------------

    st.subheader("Companies Using Ingredient")

    companies_df = pd.DataFrame(

        sorted(
            temp['Company']
            .dropna()
            .unique()
        ),

        columns=['Company']

    )

    st.dataframe(
        companies_df,
        use_container_width=True
    )

    # -----------------------------------------------------
    # PRODUCTS
    # -----------------------------------------------------

    st.subheader("Products Using Ingredient")

    product_cols = [

        col for col in [

            'Product',
            'Brand',
            'Company',
            'Category',
            'Sub-Category',
            'Country'

        ]

        if col in temp.columns

    ]

    st.dataframe(

        temp[product_cols]
        .drop_duplicates(),

        use_container_width=True

    )

# =========================================================
# MULTI INGREDIENT INTERSECTION
# =========================================================

if len(selected_ingredients) >= 2:

    st.divider()

    st.header("Multi Ingredient Intersection")

    temp = master_df[
        master_df['Ingredient']
        .isin(selected_ingredients)
    ]

    # -----------------------------------------------------
    # COMMON PRODUCTS
    # -----------------------------------------------------

    product_counts = (

        temp.groupby('Product')['Ingredient']
        .nunique()
        .reset_index()

    )

    common_products = product_counts[

        product_counts['Ingredient']
        == len(selected_ingredients)

    ]

    common_product_names = (
        common_products['Product']
        .unique()
    )

    # -----------------------------------------------------
    # COMMON COMPANIES
    # -----------------------------------------------------

    company_counts = (

        temp.groupby('Company')['Ingredient']
        .nunique()
        .reset_index()

    )

    common_companies = company_counts[

        company_counts['Ingredient']
        == len(selected_ingredients)

    ]

    # -----------------------------------------------------
    # METRICS
    # -----------------------------------------------------

    c1, c2 = st.columns(2)

    with c1:

        st.metric(
            "Common Products",
            len(common_product_names)
        )

    with c2:

        st.metric(
            "Common Companies",
            len(common_companies)
        )

    # -----------------------------------------------------
    # COMMON COMPANIES TABLE
    # -----------------------------------------------------

    st.subheader("Common Companies")

    st.dataframe(
        common_companies,
        use_container_width=True
    )

    # -----------------------------------------------------
    # COMMON PRODUCTS TABLE
    # -----------------------------------------------------

    st.subheader("Common Products")

    product_details = temp[
        temp['Product']
        .isin(common_product_names)
    ]

    product_cols = [

        col for col in [

            'Product',
            'Brand',
            'Company',
            'Category',
            'Sub-Category',
            'Country',
            'Ingredient'

        ]

        if col in product_details.columns

    ]

    st.dataframe(

        product_details[
            product_cols
        ].drop_duplicates(),

        use_container_width=True

    )

# =========================================================
# COMPANY → INGREDIENTS
# =========================================================

st.divider()

st.subheader("Company → Ingredients Used")

company_ingr = (

    master_df.groupby('Company')['Ingredient']
    .unique()
    .reset_index()

)

company_ingr['Ingredient Count'] = (

    company_ingr['Ingredient']
    .apply(len)

)

company_ingr['Ingredients Used'] = (

    company_ingr['Ingredient']
    .apply(lambda x: ', '.join(sorted(x)))

)

company_ingr = company_ingr.drop(
    columns='Ingredient'
)

st.dataframe(
    company_ingr,
    use_container_width=True
)