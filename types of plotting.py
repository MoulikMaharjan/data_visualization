import os
import folium
import pandas as pd
import matplotlib.pyplot as plt
import glob
import pgeocode
from folium.plugins import HeatMap
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from sklearn.cluster import KMeans
from sklearn.preprocessing import (LabelEncoder)
import ssl
ssl._create_default_https_context = ssl._create_unverified_context
merged_file = '/Users/moulikmaharjan/Desktop/plots/merged1.csv'

if not os.path.exists(merged_file):
    files = glob.glob('/Users/moulikmaharjan/Desktop/plots/*.csv')

    files = [f for f in files if 'merged1.csv' not in f]

    print("Merging files:", files)
    df = pd.concat(map(pd.read_csv,files), ignore_index=True)
    df.to_csv(merged_file, index=False)
    print("CSV files merged successfully!")
else:
    print("Merged file already exists. Skipping merge.")

# Load merged file
df = pd.read_csv(merged_file)
# preparing data
df['shipDate'] = pd.to_datetime(df['shipDate'])
df['date'] = df['shipDate'].dt.date
df['week'] = df['shipDate'].dt.to_period('W')
df['month'] = df['shipDate'].dt.to_period('M')
df['year'] = df['shipDate'].dt.year
df['hour'] = df['shipDate'].dt.hour

#converting the data to detail and usable format
order_per_day = df.groupby('date').size()
order_per_week = df.groupby('week').size()
order_per_month = df.groupby('month').size()
order_per_year = df.groupby('year').size()
order_by_time = df.groupby('hour').size()
country_counts = df['country'].value_counts()
state_counts = df['state'].value_counts()
zip_counts = df['zip'].value_counts()
top10_days = order_per_day.sort_values(ascending=False).head(10)
top10_months = order_per_month.sort_values(ascending=False).head(10)
top10_weeks = order_per_week.sort_values(ascending=False).head(10)
top10_city = state_counts.sort_values(ascending=False).head(10)
top10_zip = zip_counts.sort_values(ascending=False).head(10)
# Create daily order count column
df['orders_per_day'] = df.groupby('date')['date'].transform('count')

canada_map = folium.Map(location=[56.1304, -106.3468], zoom_start=4)
canada_map

# Highest number of orders in a single day
max_orders = order_per_day.max()
max_day = order_per_day.idxmax()

print("Highest number of orders in a day:", max_orders)
print("Date with highest orders:", max_day)

# Calculate growth
order_per_month = order_per_month.sort_index()
monthly_growth = order_per_month.pct_change().fillna(0) * 100
print(monthly_growth.round(2).astype(str) + '%')
monthly_growth.plot(kind='line', marker='o')

plt.figure()
order_per_day.plot(kind='line')
plt.scatter(max_day, max_orders, color='red')
plt.text(max_day, max_orders, f'{max_orders}', color='red')
plt.title("Orders per Day")
plt.xlabel("Date")
plt.ylabel("Orders")
plt.xticks(rotation=45)
plt.show()

plt.figure()
order_per_month.plot(kind='pie' ,autopct='%1.0f%%')
plt.title("Orders per month")
plt.xlabel("Months")
plt.xticks(rotation=45)
plt.show()

plt.figure()
order_per_week.plot(kind='bar')
plt.title("Orders per week")
plt.xlabel("week")
plt.ylabel("Numbers of Orders")
plt.xticks(rotation=45)
plt.show()

plt.figure()
order_per_week.plot(kind='box')
plt.title("Orders per week")
plt.xlabel("week")
plt.ylabel("Numbers of Orders")
plt.xticks(rotation=45)
plt.show()

plt.figure()
top10_days.plot(kind='bar')
plt.title("Top 10 Highest Order Days")
plt.xlabel("Date")
plt.ylabel("Number of Orders")
plt.xticks(rotation=45)
plt.show()

plt.figure()
top10_weeks.plot(kind='bar')
plt.title("Top 10 Highest Order weeks")
plt.xlabel("Week")
plt.ylabel("Number of Orders")
plt.xticks(rotation=45)
plt.show()

plt.figure()
top10_months.plot(kind='bar')
plt.title("Top 10 Highest Order MONTHS")
plt.xlabel("Month")
plt.ylabel("Number of Orders")
plt.xticks(rotation=45)
plt.show()

plt.figure()
top10_city.plot(kind='bar')
plt.title("Top 10 Highest Order STATE")
plt.xlabel("STATE")
plt.ylabel("Number of Orders")
plt.xticks(rotation=45)
plt.show()

plt.figure()
top10_zip.plot(kind='bar')
plt.title("Top 10 Highest Order zip")
plt.xlabel("zip")
plt.ylabel("Number of Orders")
plt.xticks(rotation=45)
plt.show()
plt.figure()


# Calculate growth
monthly_growth = order_per_month.pct_change().fillna(0) * 100
plt.figure()
monthly_growth.plot(marker='o')
plt.title("Monthly Growth Rate (%)")
plt.xlabel("Month")
plt.ylabel("Growth %")
plt.xticks(rotation=45)
plt.axhline(0)  # baseline
plt.show()

# Get top 10 states
top_states = df['state'].value_counts().head(10).index
filtered_df = df[df['state'].isin(top_states)]
heatmap_data = filtered_df.pivot_table(
    index='state',
    columns='month',
    values='shipDate',
    aggfunc='count')
plt.figure(figsize=(10,6))
sns.heatmap(
    heatmap_data,
    annot=True,
    fmt='g',
    cmap='coolwarm')
plt.title("Top 10 States Order Heatmap")
plt.show() 
'''
# Create pivot table
heatmap_data = df.pivot_table(
    index='hour',        # rows
    columns='date',      # columns
    values='shipDate',
    aggfunc='count'
)
# Orders per state
state_orders = df['state'].value_counts()
# Convert to DataFrame
heatmap_data = state_orders.to_frame(name='orders')
# Plot
plt.figure(figsize=(8,6))
sns.heatmap(
    heatmap_data,
    annot=True,
    fmt='g',
    cmap='YlOrRd'
)
plt.title("Heatmap of Orders by State")
plt.xlabel("Orders")
plt.ylabel("State")
plt.show()

heatmap_data = df.pivot_table(
    index='state',
    columns='month',
    values='shipDate',
    aggfunc='count'
)





# Clean ZIP
df['zip'] = df['zip'].astype(str).str.strip()

# Choose ONE country
nomi = pgeocode.Nominatim('ca')   # or 'us'

# Count orders per zip
zip_counts = df['zip'].value_counts().reset_index()
zip_counts.columns = ['zip', 'orders']

# Unique ZIP lookup (FAST)
unique_zips = zip_counts['zip'].unique()

zip_lookup = {}
for i, z in enumerate(unique_zips):
    print(f"Processing {i+1}/{len(unique_zips)}: {z}")
    res = nomi.query_postal_code(z)
    zip_lookup[z] = (res.latitude, res.longitude)

# Map back
zip_counts['latitude'] = zip_counts['zip'].map(lambda z: zip_lookup[z][0])
zip_counts['longitude'] = zip_counts['zip'].map(lambda z: zip_lookup[z][1])

# Drop missing
zip_counts = zip_counts.dropna()

# Create map
mymap = folium.Map(location=[56.1304, -106.3468], zoom_start=4)

# Create heat data
heat_data = zip_counts[['latitude', 'longitude', 'orders']].values.tolist()

# Add heatmap (FIXED LINE)
HeatMap(
    heat_data,
    radius=12,
    blur=15,
    max_zoom=10
).add_to(mymap)

# Save
mymap.save("heatmap.html")

print("✅ Heatmap saved as heatmap.html")
'''
