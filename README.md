# OwlDoor Geocoder

A simple, standalone geocoding tool that converts addresses to coordinates using OpenStreetMap's Nominatim service.

## Features

- Single address geocoding
- Batch geocoding (multiple addresses at once)
- Copy results as CSV
- No API key required (uses free Nominatim service)
- Clean, modern UI

## Usage

1. Enter a single address in the address field, or
2. Enter multiple addresses (one per line) in the batch field
3. Click "Geocode Address" or "Batch Geocode"
4. Copy results as CSV if needed

## Deploy to GitHub Pages

This repository is set up for GitHub Pages deployment:

1. Push to GitHub:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/owldoor-geocoder
   git push -u origin main
   ```

2. Enable GitHub Pages:
   - Go to repository Settings → Pages
   - Select "main" branch as source
   - Your geocoder will be live at: `https://YOUR_USERNAME.github.io/owldoor-geocoder`

## Rate Limits

Nominatim (OpenStreetMap) has a rate limit of 1 request per second. Batch geocoding automatically handles this delay.

## License

MIT

