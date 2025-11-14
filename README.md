# 🗺️ OwlDoor Geocoder

A powerful geocoding tool for converting addresses to coordinates. Perfect for processing large CSV files with millions of rows.

## 🌟 Features

### Web App
- ✅ Drag & drop CSV upload
- ✅ Multiple geocoding providers (OSM, Google, Mapbox)
- ✅ Progress tracking with real-time stats
- ✅ Real-time logging
- ✅ Download geocoded results as CSV
- ✅ No installation required
- ✅ Works on any device

### Python Script
- ✅ Process millions of rows
- ✅ Checkpoint/resume support
- ✅ Multiple providers
- ✅ Rate limiting built-in
- ✅ Error handling
- ✅ Progress statistics

## 🚀 Quick Start

### Web App

1. Visit: https://darren-owldoor.github.io/owldoor-geocoder/
2. Upload your CSV file
3. Select geocoding provider
4. Enter API key (if using Google/Mapbox)
5. Click "Process CSV"
6. Download results!

### Python Script

```bash
# Install dependencies
pip install pandas requests

# Geocode with free OSM (1 req/sec)
python geocode_bulk.py agents.csv geocoded_agents.csv --address "full_address"

# Or build from components
python geocode_bulk.py agents.csv geocoded_agents.csv \
  --street "street" \
  --city "city" \
  --state "state" \
  --zip "zip_code"

# Resume if interrupted
python geocode_bulk.py agents.csv geocoded_agents.csv \
  --address "full_address" \
  --resume
```

## 🌍 Geocoding Providers

### 1. OpenStreetMap (Nominatim) - FREE ✨
- **Cost:** FREE
- **Rate Limit:** 1 request/second
- **API Key:** Not required
- **Best For:** Testing, small batches (<10K rows)
- **Time:** ~3 hours per 10K rows

### 2. Google Maps
- **Cost:** $5 per 1,000 requests
- **Rate Limit:** 50 requests/second
- **API Key:** Required
- **Best For:** High accuracy, US addresses
- **Time:** ~50 seconds per 10K rows

### 3. Mapbox
- **Cost:** $0.50 per 1,000 requests (first 100K free)
- **Rate Limit:** 600 requests/minute
- **API Key:** Required
- **Best For:** Best value, global coverage
- **Time:** ~10 minutes per 10K rows

## 💰 Cost Comparison (2M Agents)

| Provider | Cost | Time | Quality |
|----------|------|------|---------|
| OSM (Free) | $0 | ~55 hours | Good |
| Google Maps | $10,000 | ~11 hours | Excellent |
| Mapbox | $1,000 | ~5.5 hours | Excellent |

**Recommendation:** Use Mapbox for best value ($1K for 2M)

## 📝 Input CSV Format

### Option A: Single Address Column
```csv
name,email,phone,address
John Smith,john@example.com,555-1234,"123 Main St, San Antonio, TX 78201"
Jane Doe,jane@example.com,555-5678,"456 Oak Ave, Austin, TX 78701"
```

### Option B: Component Columns
```csv
name,street,city,state,zip_code
John Smith,123 Main St,San Antonio,TX,78201
Jane Doe,456 Oak Ave,Austin,TX,78701
```

## 📤 Output CSV Format

Your CSV with added columns:

```csv
name,address,latitude,longitude,geocode_status,geocode_address
John Smith,"123 Main St, San Antonio, TX",29.4241,-98.4936,success,"123 Main St, San Antonio, TX 78201, USA"
Jane Doe,"456 Oak Ave, Austin, TX",30.2672,-97.7431,success,"456 Oak Ave, Austin, TX 78701, USA"
```

**New columns:**
- `latitude` - Latitude coordinate
- `longitude` - Longitude coordinate
- `geocode_status` - success/failed/no_address
- `geocode_address` - Formatted address from provider

## 🛠️ Python Script Usage

### Basic Usage

```bash
# Single address column
python geocode_bulk.py input.csv output.csv --address "full_address"

# Component columns
python geocode_bulk.py input.csv output.csv \
  --street "street" \
  --city "city" \
  --state "state" \
  --zip "zip"
```

### Advanced Options

```bash
# Use Google Maps
python geocode_bulk.py agents.csv geocoded.csv \
  --provider google \
  --api-key "YOUR_API_KEY" \
  --address "address"

# Use Mapbox
python geocode_bulk.py agents.csv geocoded.csv \
  --provider mapbox \
  --api-key "YOUR_API_KEY" \
  --address "address"

# Resume interrupted processing
python geocode_bulk.py agents.csv geocoded.csv \
  --address "address" \
  --resume

# Custom checkpoint interval (default: 1000)
python geocode_bulk.py agents.csv geocoded.csv \
  --address "address" \
  --chunk-size 5000
```

### Full Options

```
usage: geocode_bulk.py [-h] [-p {nominatim,google,mapbox}] [-k API_KEY]
                       [-a ADDRESS] [--street STREET] [--city CITY]
                       [--state STATE] [--zip ZIP] [-r] [-c CHUNK_SIZE]
                       input output

positional arguments:
  input                 Input CSV file
  output                Output CSV file

optional arguments:
  -p, --provider        Geocoding provider (default: nominatim)
  -k, --api-key         API key (required for google/mapbox)
  -a, --address         Single address column name
  --street              Street column name
  --city                City column name
  --state               State column name
  --zip                 Zip code column name
  -r, --resume          Resume from last checkpoint
  -c, --chunk-size      Checkpoint interval (default: 1000)
```

## 📊 Processing Large Files (2M Rows)

### Strategy for 2M Agents

**Best Approach:**
```bash
# Use Mapbox (best value)
python geocode_bulk.py \
  your_2m_agents.csv \
  geocoded_agents.csv \
  --provider mapbox \
  --api-key "YOUR_MAPBOX_KEY" \
  --address "full_address" \
  --chunk-size 10000

# Time: ~5-6 hours
# Cost: ~$1,000
# Success rate: ~95%
```

**Cost-Effective Approach:**
```bash
# Use free OSM (slower but free)
python geocode_bulk.py \
  your_2m_agents.csv \
  geocoded_agents.csv \
  --provider nominatim \
  --address "full_address" \
  --chunk-size 5000

# Time: ~55 hours (~2.5 days)
# Cost: $0
# Success rate: ~90%

# Pro tip: Run overnight, use --resume if interrupted
```

**Split Strategy:**
```bash
# Split into smaller files (100K each)
split -l 100000 agents.csv agents_part_

# Geocode each part separately
for file in agents_part_*; do
  python geocode_bulk.py $file "geocoded_$file" \
    --provider mapbox \
    --api-key "YOUR_KEY" \
    --address "address"
done

# Combine results
cat geocoded_agents_part_* > all_geocoded.csv
```

## 🔑 Getting API Keys

### Google Maps API
1. Go to: https://console.cloud.google.com/
2. Create project
3. Enable "Geocoding API"
4. Create credentials → API Key
5. Copy key

**Pricing:** $5 per 1,000 requests  
**Free tier:** $200/month credit

### Mapbox API
1. Go to: https://account.mapbox.com/
2. Sign up / Sign in
3. Create access token
4. Copy token

**Pricing:** $0.50 per 1,000 requests  
**Free tier:** 100,000 requests/month

## 🚨 Troubleshooting

### Web App Issues

**"Provider not responding"**
- Check internet connection
- Verify API key if using Google/Mapbox
- Try switching providers

**"Browser freezing on large files"**
- Use Python script for files >10K rows
- Close other browser tabs
- Try smaller batches

### Python Script Issues

**"Rate limit exceeded"**
- Script has built-in rate limiting
- For OSM: Already at max (1/sec)
- For paid APIs: Increase delay in code

**"Connection timeout"**
- Network issue - will retry
- Check internet connection
- Verify API key

**"Module not found"**
```bash
pip install pandas requests
```

**Resume not working**
- Make sure output file exists
- Use exact same output filename
- Add --resume flag

## 🔒 Security & Privacy

**API Keys:**
- Never commit API keys to GitHub
- Use environment variables
- Rotate keys periodically

**Data Privacy:**
- Web app: All processing is client-side
- Python script: All processing is local
- No data sent to OwlDoor servers
- Only sent to chosen geocoding provider

## 📞 Example Workflows

### Workflow 1: New Agent Database
```bash
# 1. Export agents from your system
# → agents_raw.csv (2M rows, no coordinates)

# 2. Geocode addresses
python geocode_bulk.py \
  agents_raw.csv \
  agents_geocoded.csv \
  --provider mapbox \
  --api-key "$MAPBOX_KEY" \
  --street "street" \
  --city "city" \
  --state "state" \
  --zip "zip_code" \
  --chunk-size 10000

# 3. Import to Supabase
node import-agents.js agents_geocoded.csv

# 4. Deploy OwlDoor with map features
vercel --prod
```

### Workflow 2: Update Existing Agents
```bash
# 1. Export agents missing coordinates
# → missing_coords.csv (50K rows)

# 2. Geocode quickly with Mapbox
python geocode_bulk.py \
  missing_coords.csv \
  newly_geocoded.csv \
  --provider mapbox \
  --api-key "$MAPBOX_KEY" \
  --address "full_address"

# 3. Update Supabase
# (Use SQL UPDATE or re-import)
```

## 🎉 Success! What's Next?

After geocoding your agents:

✅ Import to Supabase  
✅ Add map view to agent directory  
✅ Enable radius search  
✅ Add "Near Me" feature  
✅ Show service area coverage  
✅ Match agents to zip codes  
✅ Build heat maps of agent density

You now have the most powerful agent directory in real estate! 🦉🗺️

## 📄 License

MIT

## 🔗 Links

- **Live App:** https://darren-owldoor.github.io/owldoor-geocoder/
- **GitHub:** https://github.com/darren-owldoor/owldoor-geocoder

---

Built for OwlDoor 🦉
