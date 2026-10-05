import streamlit as st
import pandas as pd
from datetime import date, timedelta

# --------------------------------------------------
# PAGE SETTINGS
# --------------------------------------------------

st.set_page_config(
    page_title="MandateMap",
    page_icon="💳",
    layout="wide"
)

st.title("💳 MandateMap")
st.subheader("AI-Powered Financial Commitment Intelligence")

st.write(
    "MandateMap helps you understand when your recurring financial "
    "commitments collide and create payment pressure."
)

# --------------------------------------------------
# SAMPLE DATA
# --------------------------------------------------

today = date.today()

sample_data = [
    {
        "Service": "Netflix",
        "Category": "Entertainment",
        "Amount": 649,
        "Frequency": "Monthly",
        "Next Payment": today + timedelta(days=3)
    },
    {
        "Service": "Spotify",
        "Category": "Entertainment",
        "Amount": 119,
        "Frequency": "Monthly",
        "Next Payment": today + timedelta(days=4)
    },
    {
        "Service": "Cloud Storage",
        "Category": "Utilities",
        "Amount": 199,
        "Frequency": "Monthly",
        "Next Payment": today + timedelta(days=5)
    },
    {
        "Service": "Gym Membership",
        "Category": "Health",
        "Amount": 1000,
        "Frequency": "Monthly",
        "Next Payment": today + timedelta(days=6)
    },
    {
        "Service": "Insurance",
        "Category": "Insurance",
        "Amount": 2500,
        "Frequency": "Monthly",
        "Next Payment": today + timedelta(days=20)
    },
    {
        "Service": "Education EMI",
        "Category": "EMI",
        "Amount": 5000,
        "Frequency": "Monthly",
        "Next Payment": today + timedelta(days=25)
    }
]

# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "mandates" not in st.session_state:
    st.session_state.mandates = pd.DataFrame(sample_data)

df = st.session_state.mandates.copy()

# --------------------------------------------------
# SIDEBAR - ADD PAYMENT
# --------------------------------------------------

st.sidebar.header("➕ Add Commitment")

service = st.sidebar.text_input("Payment / Service Name")

category = st.sidebar.selectbox(
    "Category",
    [
        "Entertainment",
        "Utilities",
        "Health",
        "Insurance",
        "Education",
        "EMI",
        "Shopping",
        "Bills",
        "Other"
    ]
)

amount = st.sidebar.number_input(
    "Amount (₹)",
    min_value=1.0,
    value=500.0
)

frequency = st.sidebar.selectbox(
    "Frequency",
    ["Monthly", "Quarterly", "Yearly"]
)

next_payment = st.sidebar.date_input(
    "Next Payment Date",
    today + timedelta(days=7)
)

if st.sidebar.button("Add Payment"):

    new_payment = {
        "Service": service,
        "Category": category,
        "Amount": amount,
        "Frequency": frequency,
        "Next Payment": next_payment
    }

    st.session_state.mandates = pd.concat(
        [
            st.session_state.mandates,
            pd.DataFrame([new_payment])
        ],
        ignore_index=True
    )

    st.success("Payment added successfully!")
    st.rerun()

# --------------------------------------------------
# RESET
# --------------------------------------------------

if st.sidebar.button("🔄 Reset Demo Data"):

    st.session_state.mandates = pd.DataFrame(sample_data)

    st.success("Demo data restored!")
    st.rerun()

# --------------------------------------------------
# MONTHLY VALUE CALCULATION
# --------------------------------------------------

def monthly_value(row):

    if row["Frequency"] == "Monthly":
        return row["Amount"]

    elif row["Frequency"] == "Quarterly":
        return row["Amount"] / 3

    elif row["Frequency"] == "Yearly":
        return row["Amount"] / 12

    return 0


df["Monthly Value"] = df.apply(monthly_value, axis=1)

# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

st.header("📊 Financial Commitment Dashboard")

monthly_commitment = df["Monthly Value"].sum()

upcoming_7 = df[
    (pd.to_datetime(df["Next Payment"]).dt.date >= today) &
    (pd.to_datetime(df["Next Payment"]).dt.date <= today + timedelta(days=7))
]

upcoming_30 = df[
    (pd.to_datetime(df["Next Payment"]).dt.date >= today) &
    (pd.to_datetime(df["Next Payment"]).dt.date <= today + timedelta(days=30))
]

amount_7 = upcoming_7["Amount"].sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Monthly Commitment",
    f"₹{monthly_commitment:,.0f}"
)

col2.metric(
    "Active Commitments",
    len(df)
)

col3.metric(
    "Due in 7 Days",
    len(upcoming_7)
)

col4.metric(
    "Amount Due Soon",
    f"₹{amount_7:,.0f}"
)

# --------------------------------------------------
# COMMITMENT COLLISION DETECTION
# --------------------------------------------------

st.header("💥 Commitment Collision Map")

st.write(
    "MandateMap identifies periods where several financial commitments "
    "occur close together."
)

collision_days = []

for i, row in df.iterrows():

    payment_date = pd.to_datetime(
        row["Next Payment"]
    ).date()

    if today <= payment_date <= today + timedelta(days=30):

        collision_days.append({
            "Date": payment_date,
            "Service": row["Service"],
            "Amount": row["Amount"]
        })

collision_df = pd.DataFrame(collision_days)

if not collision_df.empty:

    collision_df = collision_df.sort_values("Date")

    # Find days with multiple payments within 3 days
    collision_groups = []

    for i in range(len(collision_df)):

        start_date = collision_df.iloc[i]["Date"]

        group = collision_df[
            (
                collision_df["Date"] >= start_date
            )
            &
            (
                collision_df["Date"]
                <= start_date + timedelta(days=3)
            )
        ]

        if len(group) >= 2:

            total = group["Amount"].sum()

            collision_groups.append(
                {
                    "Start": start_date,
                    "End": start_date + timedelta(days=3),
                    "Payments": len(group),
                    "Total": total
                }
            )

    if collision_groups:

        collision_table = pd.DataFrame(
            collision_groups
        ).drop_duplicates()

        st.warning(
            "⚠️ Financial commitment collision detected!"
        )

        st.dataframe(
            collision_table,
            use_container_width=True,
            hide_index=True
        )

        biggest = collision_table.loc[
            collision_table["Total"].idxmax()
        ]

        st.error(
            f"🔴 Highest pressure period: "
            f"{biggest['Start']} to {biggest['End']} — "
            f"{biggest['Payments']} payments totaling "
            f"₹{biggest['Total']:,.0f}"
        )

    else:

        st.success(
            "🟢 No major payment collision detected "
            "in the next 30 days."
        )

# --------------------------------------------------
# COMMITMENT STRESS SCORE
# --------------------------------------------------

st.header("🧠 Commitment Stress Score")

next_7_ratio = 0

if monthly_commitment > 0:
    next_7_ratio = amount_7 / monthly_commitment

payment_count_score = min(len(upcoming_7) * 10, 40)

amount_score = min(next_7_ratio * 60, 60)

stress_score = int(
    min(
        payment_count_score + amount_score,
        100
    )
)

if stress_score >= 70:

    level = "HIGH 🔴"

elif stress_score >= 40:

    level = "MODERATE 🟠"

else:

    level = "LOW 🟢"

col1, col2 = st.columns([1, 2])

with col1:

    st.metric(
        "Pressure Score",
        f"{stress_score}/100"
    )

    st.write(f"### {level}")

with col2:

    st.progress(stress_score / 100)

    st.info(
        "This score measures the concentration of upcoming "
        "recurring payments. It is NOT a measure of your "
        "overall financial health or affordability."
    )

# --------------------------------------------------
# FINANCIAL HEATMAP
# --------------------------------------------------

st.header("🔥 30-Day Commitment Heatmap")

heatmap_data = []

for i in range(31):

    current_day = today + timedelta(days=i)

    payments = df[
        pd.to_datetime(
            df["Next Payment"]
        ).dt.date == current_day
    ]

    total = payments["Amount"].sum()

    heatmap_data.append(
        {
            "Date": current_day,
            "Payments": len(payments),
            "Amount": total
        }
    )

heatmap_df = pd.DataFrame(heatmap_data)

st.dataframe(
    heatmap_df,
    use_container_width=True,
    hide_index=True
)

# --------------------------------------------------
# WHAT-IF SIMULATOR
# --------------------------------------------------

st.header("🔮 What-If Financial Simulator")

st.write(
    "Test how removing a recurring commitment could change "
    "your future monthly commitment."
)

if len(df) > 0:

    selected_payment = st.selectbox(
        "Select a commitment to simulate",
        df["Service"].tolist()
    )

    selected_row = df[
        df["Service"] == selected_payment
    ].iloc[0]

    reduction = selected_row["Monthly Value"]

    new_monthly = monthly_commitment - reduction

    annual_saving = reduction * 12

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Current Monthly",
        f"₹{monthly_commitment:,.0f}"
    )

    col2.metric(
        "After Removing",
        f"₹{new_monthly:,.0f}",
        f"-₹{reduction:,.0f}"
    )

    col3.metric(
        "Potential Yearly Difference",
        f"₹{annual_saving:,.0f}"
    )

    st.success(
        f"💡 Removing/reviewing **{selected_payment}** "
        f"would reduce the estimated monthly recurring "
        f"commitment by ₹{reduction:,.0f}."
    )

# --------------------------------------------------
# SMART INSIGHT ENGINE
# --------------------------------------------------

st.header("🤖 Smart Financial Insights")

if len(df) > 0:

    largest_payment = df.loc[
        df["Monthly Value"].idxmax()
    ]

    largest_category = (
        df.groupby("Category")["Monthly Value"]
        .sum()
        .sort_values(ascending=False)
        .index[0]
    )

    largest_category_amount = (
        df.groupby("Category")["Monthly Value"]
        .sum()
        .max()
    )

    st.info(
        f"💡 Your largest recurring commitment is "
        f"**{largest_payment['Service']}** at "
        f"₹{largest_payment['Monthly Value']:,.0f} per month."
    )

    st.info(
        f"📌 **{largest_category}** is currently your "
        f"largest recurring-payment category, contributing "
        f"approximately ₹{largest_category_amount:,.0f} per month."
    )

    if len(upcoming_7) >= 3:

        st.warning(
            "⚠️ You have several commitments arriving within "
            "the next 7 days. Review the payment timeline "
            "before the deduction period."
        )

    elif len(upcoming_7) == 0:

        st.success(
            "🟢 No recurring payments are scheduled "
            "within the next 7 days."
        )

# --------------------------------------------------
# CATEGORY ANALYSIS
# --------------------------------------------------

st.header("📈 Commitment by Category")

category_data = (
    df.groupby("Category")["Monthly Value"]
    .sum()
    .sort_values(ascending=False)
)

st.bar_chart(category_data)

# --------------------------------------------------
# EDIT PAYMENT
# --------------------------------------------------

st.header("✏️ Edit Commitment")

if len(df) > 0:

    edit_service = st.selectbox(
        "Select commitment to edit",
        df["Service"].tolist(),
        key="edit_select"
    )

    edit_index = df[
        df["Service"] == edit_service
    ].index[0]

    selected = df.loc[edit_index]

    new_service = st.text_input(
        "Service Name",
        selected["Service"],
        key="edit_service"
    )

    new_amount = st.number_input(
        "Amount",
        min_value=1.0,
        value=float(selected["Amount"]),
        key="edit_amount"
    )

    new_frequency = st.selectbox(
        "Frequency",
        ["Monthly", "Quarterly", "Yearly"],
        index=[
            "Monthly",
            "Quarterly",
            "Yearly"
        ].index(selected["Frequency"]),
        key="edit_frequency"
    )

    new_date = st.date_input(
        "Next Payment",
        pd.to_datetime(
            selected["Next Payment"]
        ).date(),
        key="edit_date"
    )

    if st.button("Save Changes"):

        st.session_state.mandates.loc[
            edit_index,
            "Service"
        ] = new_service

        st.session_state.mandates.loc[
            edit_index,
            "Amount"
        ] = new_amount

        st.session_state.mandates.loc[
            edit_index,
            "Frequency"
        ] = new_frequency

        st.session_state.mandates.loc[
            edit_index,
            "Next Payment"
        ] = new_date

        st.success("Changes saved!")
        st.rerun()

# --------------------------------------------------
# DELETE PAYMENT
# --------------------------------------------------

st.header("🗑️ Delete Commitment")

if len(df) > 0:

    delete_service = st.selectbox(
        "Select commitment to delete",
        df["Service"].tolist(),
        key="delete_select"
    )

    if st.button("Delete Selected Payment"):

        delete_index = df[
            df["Service"] == delete_service
        ].index[0]

        st.session_state.mandates = (
            st.session_state.mandates
            .drop(delete_index)
            .reset_index(drop=True)
        )

        st.success(
            f"{delete_service} deleted successfully!"
        )

        st.rerun()

# --------------------------------------------------
# ALL COMMITMENTS
# --------------------------------------------------

st.header("📋 All Financial Commitments")

display_df = st.session_state.mandates.copy()

display_df["Next Payment"] = pd.to_datetime(
    display_df["Next Payment"]
).dt.date

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True
)

# --------------------------------------------------
# DOWNLOAD REPORT
# --------------------------------------------------

csv = display_df.to_csv(index=False)

st.download_button(
    "📥 Download Financial Commitment Report",
    csv,
    "mandatemap_report.csv",
    "text/csv"
)

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "💳 MandateMap — Map your commitments. "
    "Understand your pressure. Plan ahead."
)

st.caption(
    "Prototype: Uses user-entered/demo data. "
    "It does not access bank accounts or initiate payments."
)