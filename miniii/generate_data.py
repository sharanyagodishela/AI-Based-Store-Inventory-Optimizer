import pandas as pd
import numpy as np

np.random.seed(1)

rows = 1000

data = {
    "Store_ID": range(1, rows + 1),
    "Store_Area": np.random.randint(1000, 2000, rows),
    "Items_Available": np.random.randint(1200, 2500, rows),
    "Daily_Customer_Count": np.random.randint(200, 1500, rows),
}

df = pd.DataFrame(data)

df["Store_Sales"] = (
    df["Store_Area"] * 25 +
    df["Items_Available"] * 12 +
    df["Daily_Customer_Count"] * 35 +
    np.random.randint(-5000, 5000, rows)
)

df.to_csv("stores.csv", index=False)

print("✅ 1000 rows dataset created successfully!")