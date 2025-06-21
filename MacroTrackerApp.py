import streamlit as st
import pandas as pd
import datetime

# ---------- Constants ----------
DAILY_TARGETS = {
    'Calories': 1800,
    'Protein': 150,
    'Carbs': 150,
    'Fats': 75
}

DEFAULT_MEALS_BY_DAY = {
    'Monday': ['Greek Yogurt With Mixed Berries', '2 Hard Boiled Eggs','Chicken Breast Lunch','Double Greek Yogurt','Protein Shake','Mediterranean Chicken Kabob'],
    'Tuesday': ['Greek Yogurt With Mixed Berries', '2 Hard Boiled Eggs','Chicken Thigh Lunch','Double Greek Yogurt','Protein Shake','Chicken Sweet Potato Risotto'],
    'Wednesday': ['Greek Yogurt With Mixed Berries', '2 Hard Boiled Eggs','Chicken Breast Lunch','Double Greek Yogurt','Protein Shake','French Country Dinner'],
    'Thursday': ['Greek Yogurt With Mixed Berries', '2 Hard Boiled Eggs','Chicken Thigh Lunch','Double Greek Yogurt','Protein Shake','Chicken Pesto Parm'],
    'Friday': ['Greek Yogurt With Mixed Berries', 'Friday Breakfast','Chicken Breast Lunch','Double Greek Yogurt','Protein Shake','Chicken Sweet Potato Risotto'],
    'Saturday': ['Skyr Yogurt w/ Granola', '2 Hard Boiled Eggs','French Country Dinner','Protein Shake','French Country Dinner'],
    'Sunday': ['Skyr Yogurt w/ Granola', '2 Hard Boiled Eggs','French Country Dinner','Protein Shake','Chicken Pesto Parm'],
}

# ---------- Load Data ----------
def load_meals():
    try:
        return pd.read_csv('meals.csv')
    except FileNotFoundError:
        return pd.DataFrame(columns=['Meal', 'Calories', 'Protein', 'Carbs', 'Fats'])

def load_log():
    try:
        return pd.read_csv('log.csv')
    except FileNotFoundError:
        return pd.DataFrame(columns=['Date', 'Meal', 'Calories', 'Protein', 'Carbs', 'Fats'])

# ---------- Save Data ----------
def save_meals(df):
    df.to_csv('meals.csv', index=False)

def save_log(df):
    df.to_csv('log.csv', index=False)

# ---------- UI ----------
st.title("📊 Macro Tracker")

### Log Meals ###
meals_df = load_meals()
log_df = load_log()

log_date = st.date_input("Select log date", value=datetime.date.today())
today = datetime.date.today()

st.header("🍽️ Log a Meal")
meal_selected = st.selectbox("Select a meal", meals_df['Meal'].unique())
if st.button("Log Meal"):
    meal_data = meals_df[meals_df['Meal'] == meal_selected].iloc[0]
    new_entry = pd.DataFrame([{
        'Date': log_date.isoformat(),
        'Meal': meal_selected,
        'Calories': meal_data['Calories'],
        'Protein': meal_data['Protein'],
        'Carbs': meal_data['Carbs'],
        'Fats': meal_data['Fats']
    }])
    log_df = pd.concat([log_df, new_entry], ignore_index=True)
    save_log(log_df)
    st.success(f"Logged {meal_selected}!")

weekday = log_date.strftime('%A')
default_meals = DEFAULT_MEALS_BY_DAY.get(weekday, [])

if default_meals:
    if st.button(f"Log My {weekday} Meals"):
        for meal_name in default_meals:
            if meal_name in meals_df['Meal'].values:
                meal_data = meals_df[meals_df['Meal'] == meal_name].iloc[0]
                new_entry = pd.DataFrame([{
                    'Date': log_date.isoformat(),
                    'Meal': meal_name,
                    'Calories': meal_data['Calories'],
                    'Protein': meal_data['Protein'],
                    'Carbs': meal_data['Carbs'],
                    'Fats': meal_data['Fats']
                }])
                log_df = pd.concat([log_df, new_entry], ignore_index=True)
        save_log(log_df)
        st.success(f"Logged your usual {weekday} meals!")
else:
    st.info(f"No default meals set for {weekday}.")

### Totals ###

st.subheader("Today Totals vs Goals")

log_df['Date'] = pd.to_datetime(log_df['Date']).dt.date
selected_log = log_df[log_df['Date'] == log_date]
total_today = selected_log[['Calories', 'Protein', 'Carbs', 'Fats']].sum()

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Calories", f"{total_today['Calories']:.0f}", f"{DAILY_TARGETS['Calories'] - total_today['Calories']:.0f} left")

with col2:
    st.metric("Protein", f"{total_today['Protein']:.0f}g", f"{DAILY_TARGETS['Protein'] - total_today['Protein']:.0f}g left")

with col3:
    st.metric("Carbs", f"{total_today['Carbs']:.0f}g", f"{DAILY_TARGETS['Carbs'] - total_today['Carbs']:.0f}g left")

with col4:
    st.metric("Fats", f"{total_today['Fats']:.0f}g", f"{DAILY_TARGETS['Fats'] - total_today['Fats']:.0f}g left")





### Summary ###

st.header("📅 Daily Summary")

st.dataframe(selected_log[['Meal', 'Calories', 'Protein', 'Carbs', 'Fats']])



st.header("🗑️ Delete a Logged Meal")

# Filter log by selected date
log_df['Date'] = pd.to_datetime(log_df['Date']).dt.date
selected_log = log_df[log_df['Date'] == log_date]

if not selected_log.empty:
    # Keep track of original log_df index
    selected_log_with_index = selected_log.copy()
    selected_log_with_index['log_df_index'] = selected_log_with_index.index

    # Reset for UI selection
    display_df = selected_log_with_index.reset_index(drop=True)

    selected_index = st.selectbox(
        f"Select a meal to delete (logged on {log_date.isoformat()}):",
        options=display_df.index,
        format_func=lambda i: f"{display_df.loc[i, 'Meal']} - {display_df.loc[i, 'Calories']} cal"
    )

    if st.button("Delete Selected Meal"):
        true_index = display_df.loc[selected_index, 'log_df_index']
        log_df = log_df.drop(index=true_index)
        save_log(log_df)
        st.success("Meal deleted.")
else:
    st.info(f"No meals logged on {log_date.isoformat()}.")

#st.header("📆 Weekly Summary")
last_7_days = (log_df['Date'] >= today - datetime.timedelta(days=6))
weekly_log = log_df[last_7_days]
weekly_totals = weekly_log[['Calories', 'Protein', 'Carbs', 'Fats']].sum()
#st.dataframe(weekly_log[['Date', 'Meal', 'Calories', 'Protein', 'Carbs', 'Fats']])

st.subheader("7-Day Totals vs Goals")
weekly_summary = pd.DataFrame({
    'Consumed': weekly_totals,
    'Target': pd.Series({k: v * 7 for k, v in DAILY_TARGETS.items()})
})
weekly_summary['Remaining'] = weekly_summary['Target'] - weekly_summary['Consumed']
st.dataframe(weekly_summary)

st.header("➕ Add New Meal")
with st.form("Add Meal"):
    meal_name = st.text_input("Meal Name")
    cal = st.number_input("Calories", min_value=0)
    prot = st.number_input("Protein (g)", min_value=0)
    carb = st.number_input("Carbs (g)", min_value=0)
    fat = st.number_input("Fats (g)", min_value=0)
    submitted = st.form_submit_button("Add to Saved Meals")
    if submitted:
        new_meal = pd.DataFrame([{
            'Meal': meal_name,
            'Calories': cal,
            'Protein': prot,
            'Carbs': carb,
            'Fats': fat
        }])
        meals_df = pd.concat([meals_df, new_meal], ignore_index=True)
        save_meals(meals_df)
        st.success(f"Added {meal_name} to meal list!")

st.caption("Data stored in local CSV files: 'meals.csv' and 'log.csv'")
