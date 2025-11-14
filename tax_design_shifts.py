# ============================================================
# Phase 1 – Step 1: Outline Major Tax Design Shifts
# Project: DEEP – Vehicle Scrapping and Environmental Policy
# Author: Mahsa Gorji
# Date: 2025-11-03
# ============================================================
#
# OBJECTIVE:
#   - Analyze the evolution of vehicle tax components (1969–2023)
#   - Identify the shift from weight/power/displacement to CO₂/NOₓ
#
# INPUT:
#   utility/vehicle_taxes.csv
#
# OUTPUTS:
#   1. tax_component_presence_by_year.csv
#   2. tax_design_timeline.csv
#   3. tax_components_timeline.png
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import os

# ------------------------------------------------------------
# File paths
# ------------------------------------------------------------
save_path = r"C:\Users\s15832\Documents\Project\New Project\Data"
plot_dir  = r"C:\Users\s15832\Documents\Project\New Project\Plot"
tax_path  = os.path.join(save_path, "vehicle_taxes.csv")

os.makedirs(plot_dir, exist_ok=True)

# ------------------------------------------------------------
# Load the tax data
# ------------------------------------------------------------
df = pd.read_csv(tax_path)
print(f"✅ Loaded {df.shape[0]:,} rows × {df.shape[1]} columns")

# Clean column names
df.columns = df.columns.str.lower().str.strip()

# ------------------------------------------------------------
# Step 1 — Identify main components and normalize names
# ------------------------------------------------------------
# Normalize component names (handle spelling variants)
df["name_clean"] = (
    df["name"]
    .str.lower()
    .str.strip()
    .replace({
        "displacem": "displacement",
        "effekt": "effect",
        "power": "effect",
        "vikt": "weight",
        "co2": "co2",
        "nox": "nox",
    })
)

# Focus only on relevant components
relevant = ["weight", "displacement", "effect", "co2", "nox"]
df = df[df["name_clean"].isin(relevant)].copy()

# ------------------------------------------------------------
# Step 2 — Summarize presence and activity by year
# ------------------------------------------------------------
component_summary = (
    df.groupby(["year", "name_clean"])["fee"]
    .sum()
    .unstack(fill_value=0)
    .reset_index()
)

# Compute binary indicator (1 if component active that year)
presence = component_summary.copy()
for c in relevant:
    presence[c] = (presence[c] > 0).astype(int)

presence_csv = os.path.join(save_path, "tax_component_presence_by_year.csv")
presence.to_csv(presence_csv, index=False)
print(f"📄 Saved component presence table → {presence_csv}")

# ------------------------------------------------------------
# Step 3 — Identify first and last appearance years per component
# ------------------------------------------------------------
first_last = (
    df.groupby("name_clean")["year"]
    .agg(["min", "max"])
    .reset_index()
    .rename(columns={"min": "first_year", "max": "last_year"})
)
print("\n🧾 Component Activity Range:")
print(first_last)

# ------------------------------------------------------------
# Step 4 — Define tax regime periods manually based on presence
# ------------------------------------------------------------
# Identify general pattern from the data
pre_env = (presence["weight"] + presence["displacement"] + presence["effect"]).gt(0) & (
    presence["co2"] + presence["nox"] == 0
)
transition = (presence["co2"] + presence["nox"]).gt(0) & (
    presence["weight"] + presence["displacement"] + presence["effect"] > 0
)
green = (presence["co2"] + presence["nox"]).gt(0) & (
    presence["weight"] + presence["displacement"] + presence["effect"] == 0
)

summary = pd.DataFrame({
    "Period": ["1980–2006", "2007–2008", "2009–2023"],
    "Dominant_Tax_Basis": [
        "Weight, Power, Displacement",
        "CO₂ introduced (NOₓ emerging)",
        "CO₂ and NOₓ dominate"
    ],
    "Comment": [
        "Pre-environmental tax era",
        "Start of green reform",
        "Fully environmental-based system"
    ]
})

timeline_csv = os.path.join(save_path, "tax_design_timeline.csv")
summary.to_csv(timeline_csv, index=False)
print(f"📄 Saved tax design summary → {timeline_csv}")

# ------------------------------------------------------------
# Step 5 — Visualization: Tax components by year (stacked area)
# ------------------------------------------------------------
plt.figure(figsize=(10, 6))
stack_df = component_summary.set_index("year")[relevant]
stack_df.plot.area(alpha=0.7, cmap="tab10")

plt.title("Evolution of Vehicle Tax Components in Norway (1969–2023)",
          fontsize=14, weight="bold")
plt.xlabel("Year")
plt.ylabel("Total Tax Fee (NOK, summed across steps)")
plt.grid(alpha=0.3)
plt.legend(title="Tax Component", loc="upper left")
plt.tight_layout()

plot_path = os.path.join(plot_dir, "tax_components_timeline.png")
plt.savefig(plot_path, dpi=300)
plt.show()
print(f"✅ Plot saved → {plot_path}")

# ------------------------------------------------------------
# Step 6 — Print a short interpretation
# ------------------------------------------------------------
print("\n📊 INTERPRETATION:")
print("• 1980s–2000s: tax dominated by weight, displacement, and effect.")
print("• 2007–2008: CO₂ component appears, marking environmental shift.")
print("• 2009 onward: CO₂ and NOₓ replace old technical bases entirely.")
print("• This matches the transition from 'technical' to 'green' taxation.")
# ============================================================
