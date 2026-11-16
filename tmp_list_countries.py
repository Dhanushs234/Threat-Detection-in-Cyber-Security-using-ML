import pandas as pd
from pathlib import Path

csv_path = Path("data/cleaned_detection_input_with_ip_country.csv")
df = pd.read_csv(csv_path, usecols=["src_country", "dst_country"], dtype=str)
unique_countries = sorted(set(df["src_country"].dropna()) | set(df["dst_country"].dropna()))

print(len(unique_countries))
for country in unique_countries:
    print(country)
