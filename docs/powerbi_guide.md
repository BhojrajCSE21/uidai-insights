# 📊 Power BI Dashboard Guide

This guide walks you through creating a professional Power BI dashboard using the exported UIDAI data.

---

## Prerequisites

1. **Power BI Desktop** installed (free from Microsoft Store)
2. **Exported data files** from `data/outputs/powerbi_exports/`:
   - `fact_aadhaar_transactions.csv`
   - `dim_states.csv`
   - `dim_date.csv`
   - `anomalies.csv`

> Run `python dashboards/export_for_powerbi.py` if files don't exist.

---

## Step 1: Import Data

1. Open **Power BI Desktop**
2. Click **Get Data** → **Text/CSV**
3. Import each file:
   - `fact_aadhaar_transactions.csv` (main fact table)
   - `dim_states.csv` (state dimension)
   - `dim_date.csv` (date dimension)
   - `anomalies.csv` (anomaly data)

---

## Step 2: Create Relationships (Data Model)

1. Go to **Model View** (left sidebar)
2. Create relationships by dragging:

| From Table                | From Column | To Table   | To Column |
| ------------------------- | ----------- | ---------- | --------- |
| fact_aadhaar_transactions | state       | dim_states | state     |
| fact_aadhaar_transactions | date        | dim_date   | date      |

3. Set all relationships to **One-to-Many**

---

## Step 3: Create DAX Measures

Click **New Measure** and add these formulas:

### Total Records

```dax
Total Records = SUM(fact_aadhaar_transactions[total_count])
```

### Children Count

```dax
Children = SUM(fact_aadhaar_transactions[children_0_5])
```

### Youth Count

```dax
Youth = SUM(fact_aadhaar_transactions[youth_5_17])
```

### Adults Count

```dax
Adults = SUM(fact_aadhaar_transactions[adults_18_plus])
```

### Month-over-Month Growth

```dax
MoM Growth % =
VAR CurrentMonth = SUM(fact_aadhaar_transactions[total_count])
VAR PreviousMonth = CALCULATE(
    SUM(fact_aadhaar_transactions[total_count]),
    DATEADD(dim_date[date], -1, MONTH)
)
RETURN
DIVIDE(CurrentMonth - PreviousMonth, PreviousMonth, 0) * 100
```

### Anomaly Count

```dax
Anomaly Count = COUNTROWS(anomalies)
```

---

## Step 4: Create Visuals

### Page 1: Overview

| Visual         | Fields                               | Purpose           |
| -------------- | ------------------------------------ | ----------------- |
| **Card**       | Total Records                        | Show total count  |
| **Card**       | Distinct state count                 | States covered    |
| **Slicer**     | data_type                            | Filter by dataset |
| **Bar Chart**  | state (axis), total_count (values)   | Top states        |
| **Line Chart** | date (axis), total_count (values)    | Monthly trend     |
| **Pie Chart**  | age groups (legend), counts (values) | Age distribution  |

### Page 2: Geographic Analysis

| Visual     | Fields                                              | Purpose                 |
| ---------- | --------------------------------------------------- | ----------------------- |
| **Map**    | state, total_count                                  | Geographic distribution |
| **Matrix** | state (rows), month (columns), total_count (values) | Heatmap view            |
| **Slicer** | region (from dim_states)                            | Filter by region        |

### Page 3: Anomalies

| Visual           | Fields                                | Purpose               |
| ---------------- | ------------------------------------- | --------------------- |
| **Scatter Plot** | zscore (X), total (Y), state (legend) | Anomaly visualization |
| **Table**        | date, state, district, total, zscore  | Anomaly details       |
| **Card**         | Anomaly Count                         | Total anomalies       |

---

## Step 5: Apply Theme

1. Go to **View** → **Themes**
2. Choose a professional theme (e.g., "Innovate")
3. Or create custom colors:
   - Primary: #3498db
   - Secondary: #2ecc71
   - Accent: #e74c3c

---

## Step 6: Add Interactivity

1. **Cross-filtering**: Click a state to filter all charts
2. **Drill-through**: Right-click → Add drill-through page
3. **Bookmarks**: Save specific views for presentations

---

## Step 7: Publish (Optional)

1. **Save** your .pbix file
2. Click **Publish** → Select workspace
3. Access via Power BI Service (app.powerbi.com)

---

## Sample Layout

```
┌────────────────────────────────────────────────────────────┐
│  UIDAI Aadhaar Insights       [Dataset Filter ▼]          │
├───────────┬───────────┬───────────┬────────────────────────┤
│   4.2M    │    59     │   756     │  Monthly Trend Line    │
│  Records  │  States   │ Districts │  ─────────────────     │
├───────────┴───────────┴───────────┤────────────────────────┤
│                                   │                        │
│  Top States Bar Chart             │  Age Distribution Pie  │
│                                   │                        │
├───────────────────────────────────┴────────────────────────┤
│             State × Month Heatmap Matrix                   │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## Tips for Resume

When describing this project:

✅ "Built interactive Power BI dashboard for UIDAI data analysis"  
✅ "Created data model with fact and dimension tables"  
✅ "Implemented DAX measures for KPIs and growth metrics"  
✅ "Designed multi-page report with drill-through capabilities"

---

## Troubleshooting

| Issue               | Solution                                  |
| ------------------- | ----------------------------------------- |
| Date not recognized | Change column type to Date in Power Query |
| Slow performance    | Reduce data by filtering or aggregating   |
| Missing values      | Check for NaN in source CSV               |

---

_Guide created: January 2026_
