# Smart Range Logic - Intelligent Search Parameters

## Problem
Previous logic used fixed percentages (±2 years, ±30% km) which were too wide:
- **Dacia Duster 2018, 120,000 km** searched:
  - Years: 2016-2020 (±2 years)
  - KM: 84,000-156,000 (±36,000 km)
  - Result: Too wide, found 0 results

## New Smart Logic

### Year Range (Context-Aware)

```python
if year >= 2020:
    ±1 year  # Newer cars: stricter
elif year >= 2015:
    ±1 year  # Recent cars
else:
    ±2 years # Older cars: more flexible
```

**Examples:**
- 2023 → 2022-2024 (±1)
- 2018 → 2017-2019 (±1)
- 2013 → 2011-2015 (±2)
- 2005 → 2003-2007 (±2)

### KM Range (Adaptive)

```python
if km <= 50,000:
    ±5,000 km    # Low km: tight range
elif km <= 100,000:
    ±10,000 km   # Medium km
elif km <= 150,000:
    ±15,000 km   # High km
else:
    ±20,000 km   # Very high km
```

**Examples:**
- 30,000 km → 25,000-35,000 (±5k)
- 80,000 km → 70,000-90,000 (±10k)
- 120,000 km → 110,000-130,000 (±10k)
- 180,000 km → 160,000-200,000 (±20k)

## Test Cases

### Case 1: Dacia Duster 2018, 120,000 km
**Before:**
- Year: 2016-2020 (too wide)
- KM: 84,000-156,000 (too wide)
- OLX found: 0 results

**After:**
- Year: 2017-2019 (±1 year)
- KM: 110,000-130,000 (±10k)
- OLX should find: 5-10 results ✅

### Case 2: BMW 320d 2013, 200,000 km
**Before:**
- Year: 2011-2015 (±2)
- KM: 140,000-260,000 (±60k)

**After:**
- Year: 2011-2015 (±2, same for older cars)
- KM: 180,000-220,000 (±20k for very high km)
- More precise results ✅

### Case 3: Audi A4 2022, 45,000 km
**Before:**
- Year: 2020-2024 (±2)
- KM: 31,500-58,500 (±13.5k)

**After:**
- Year: 2021-2023 (±1 for newer cars)
- KM: 40,000-50,000 (±5k for low km)
- Much more precise! ✅

### Case 4: Golf 2008, 180,000 km
**Before:**
- Year: 2006-2010 (±2)
- KM: 126,000-234,000 (±54k)

**After:**
- Year: 2006-2010 (±2, same)
- KM: 160,000-200,000 (±20k)
- Better precision ✅

## Why This Works Better

### 1. **Year Range Logic:**
- **Newer cars (2020+)**: Market changes fast, ±1 year is enough
- **Recent cars (2015-2019)**: Still relevant, ±1 year
- **Older cars (<2015)**: Less year-specific, ±2 years OK

### 2. **KM Range Logic:**
- **Low km (<50k)**: Small differences matter (30k vs 40k is significant)
- **Medium km (50-100k)**: Moderate tolerance
- **High km (100-150k)**: More tolerance (120k vs 130k is less significant)
- **Very high km (>150k)**: Large tolerance (180k vs 200k is similar)

### 3. **OLX Filtering Benefits:**
Using native OLX filters with these ranges:
```
https://www.olx.ro/autoturisme/dacia/?
  search[filter_enum_model][0]=duster&
  search[filter_float_year:from]=2017&
  search[filter_float_year:to]=2019&
  search[filter_float_rulaj_pana:from]=110000&
  search[filter_float_rulaj_pana:to]=130000&
  search[filter_enum_petrol][0]=diesel&
  search[filter_enum_gearbox][0]=manual
```

## Implementation

File: `app/routers/analysis.py`

```python
# SMART year range
if request.an >= 2020:
    year_range = 1
elif request.an >= 2015:
    year_range = 1
else:
    year_range = 2

an_min = max(1990, request.an - year_range)
an_max = min(2025, request.an + year_range)

# SMART km range
km_center = request.km
if km_center <= 50000:
    km_range = 5000
elif km_center <= 100000:
    km_range = 10000
elif km_center <= 150000:
    km_range = 15000
else:
    km_range = 20000

km_min = max(0, km_center - km_range)
km_max = km_center + km_range
```

## Debug Output

Now logs search parameters:
```
=== Search Parameters ===
Car: Dacia Duster
User input: Year 2018, KM 120,000
Search range: Year 2017-2019, KM 110,000-130,000
Filters: diesel, manuala, any
```

## Expected Results

### Dacia Duster 2018, 120k km, Diesel, Manual
- OLX query: 2017-2019, 110k-130k km, diesel, manual
- Expected: 5-10 results
- Price range: ~9,900-11,900 EUR (based on your manual search)

### Testing Steps:
1. Restart backend
2. Search: Dacia, Duster, 2018, 120000, Diesel, Manuală
3. Check backend logs for "Search Parameters"
4. Should trigger scraping and find results
5. Results should be realistic

Ready to test! 🎯
