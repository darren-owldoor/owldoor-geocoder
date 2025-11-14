#!/usr/bin/env python3
"""
OwlDoor Bulk Geocoder
Process CSV files with millions of rows using multiple geocoding providers.

Usage:
    python geocode_bulk.py input.csv output.csv --address "full_address"
    python geocode_bulk.py input.csv output.csv --street "street" --city "city" --state "state" --zip "zip_code"
    python geocode_bulk.py input.csv output.csv --address "address" --provider mapbox --api-key "YOUR_KEY" --resume
"""

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import requests
from urllib.parse import quote

try:
    import pandas as pd
except ImportError:
    print("Error: pandas is required. Install with: pip install pandas")
    sys.exit(1)


class Geocoder:
    """Base geocoding provider class"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.last_request_time = 0
        self.rate_limit_delay = 1.0  # seconds
    
    def geocode(self, address: str) -> Tuple[float, float, str]:
        """Geocode an address. Returns (latitude, longitude, formatted_address)"""
        raise NotImplementedError
    
    def _rate_limit(self):
        """Enforce rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()


class NominatimGeocoder(Geocoder):
    """OpenStreetMap Nominatim geocoder - FREE, no API key required"""
    
    def __init__(self):
        super().__init__()
        self.rate_limit_delay = 1.0  # 1 request per second
        self.base_url = "https://nominatim.openstreetmap.org/search"
    
    def geocode(self, address: str) -> Tuple[float, float, str]:
        self._rate_limit()
        
        params = {
            'q': address,
            'format': 'json',
            'limit': 1
        }
        
        headers = {
            'User-Agent': 'OwlDoorGeocoder/1.0'
        }
        
        try:
            response = requests.get(self.base_url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data or len(data) == 0:
                raise ValueError(f"Address not found: {address}")
            
            result = data[0]
            return (
                float(result['lat']),
                float(result['lon']),
                result['display_name']
            )
        except requests.RequestException as e:
            raise ValueError(f"Geocoding error: {str(e)}")


class GoogleGeocoder(Geocoder):
    """Google Maps Geocoding API"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        if not api_key:
            raise ValueError("Google Maps API key is required")
        self.rate_limit_delay = 0.02  # 50 requests per second
        self.base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    
    def geocode(self, address: str) -> Tuple[float, float, str]:
        self._rate_limit()
        
        params = {
            'address': address,
            'key': self.api_key
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data['status'] != 'OK':
                raise ValueError(f"Google API error: {data['status']}")
            
            result = data['results'][0]
            location = result['geometry']['location']
            return (
                location['lat'],
                location['lng'],
                result['formatted_address']
            )
        except requests.RequestException as e:
            raise ValueError(f"Geocoding error: {str(e)}")


class MapboxGeocoder(Geocoder):
    """Mapbox Geocoding API"""
    
    def __init__(self, api_key: str):
        super().__init__(api_key)
        if not api_key:
            raise ValueError("Mapbox API key is required")
        self.rate_limit_delay = 0.1  # 600 requests per minute
        self.base_url = "https://api.mapbox.com/geocoding/v5/mapbox.places"
    
    def geocode(self, address: str) -> Tuple[float, float, str]:
        self._rate_limit()
        
        encoded_address = quote(address)
        url = f"{self.base_url}/{encoded_address}.json"
        
        params = {
            'access_token': self.api_key,
            'limit': 1
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('features') or len(data['features']) == 0:
                raise ValueError(f"Address not found: {address}")
            
            feature = data['features'][0]
            center = feature['center']
            return (
                center[1],  # latitude
                center[0],  # longitude
                feature['place_name']
            )
        except requests.RequestException as e:
            raise ValueError(f"Geocoding error: {str(e)}")


class BulkGeocoder:
    """Bulk geocoding processor with checkpoint/resume support"""
    
    def __init__(self, geocoder: Geocoder, chunk_size: int = 1000):
        self.geocoder = geocoder
        self.chunk_size = chunk_size
        self.checkpoint_file = None
    
    def process_csv(
        self,
        input_file: str,
        output_file: str,
        address_column: Optional[str] = None,
        street_column: Optional[str] = None,
        city_column: Optional[str] = None,
        state_column: Optional[str] = None,
        zip_column: Optional[str] = None,
        resume: bool = False
    ):
        """Process CSV file with geocoding"""
        
        # Load CSV
        print(f"Loading CSV: {input_file}")
        try:
            df = pd.read_csv(input_file)
        except Exception as e:
            print(f"Error reading CSV: {e}")
            sys.exit(1)
        
        print(f"Loaded {len(df)} rows")
        
        # Build addresses
        addresses = []
        for idx, row in df.iterrows():
            if address_column and pd.notna(row.get(address_column)):
                addresses.append(str(row[address_column]))
            elif street_column or city_column or state_column or zip_column:
                parts = []
                if street_column and pd.notna(row.get(street_column)):
                    parts.append(str(row[street_column]))
                if city_column and pd.notna(row.get(city_column)):
                    parts.append(str(row[city_column]))
                if state_column and pd.notna(row.get(state_column)):
                    parts.append(str(row[state_column]))
                if zip_column and pd.notna(row.get(zip_column)):
                    parts.append(str(row[zip_column]))
                addresses.append(', '.join(parts) if parts else None)
            else:
                addresses.append(None)
        
        # Filter out None addresses
        valid_indices = [i for i, addr in enumerate(addresses) if addr]
        print(f"Found {len(valid_indices)} valid addresses")
        
        # Setup checkpoint
        self.checkpoint_file = output_file + '.checkpoint'
        start_idx = 0
        
        if resume and os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, 'r') as f:
                checkpoint = json.load(f)
                start_idx = checkpoint.get('last_processed', 0)
                print(f"Resuming from row {start_idx}")
        
        # Initialize output columns
        if 'latitude' not in df.columns:
            df['latitude'] = None
        if 'longitude' not in df.columns:
            df['longitude'] = None
        if 'geocode_status' not in df.columns:
            df['geocode_status'] = None
        if 'geocode_address' not in df.columns:
            df['geocode_address'] = None
        
        # Process addresses
        stats = {
            'total': len(valid_indices),
            'processed': start_idx,
            'success': 0,
            'failed': 0
        }
        
        if start_idx > 0:
            # Count existing successes
            stats['success'] = df['geocode_status'].eq('success').sum()
            stats['failed'] = df['geocode_status'].eq('failed').sum()
        
        print(f"\nStarting geocoding...")
        print(f"Provider: {type(self.geocoder).__name__}")
        print(f"Total addresses: {stats['total']}")
        print(f"Starting from: {start_idx}")
        print("-" * 60)
        
        start_time = time.time()
        
        for i in range(start_idx, len(valid_indices)):
            idx = valid_indices[i]
            address = addresses[idx]
            
            try:
                lat, lng, formatted = self.geocoder.geocode(address)
                df.at[idx, 'latitude'] = lat
                df.at[idx, 'longitude'] = lng
                df.at[idx, 'geocode_status'] = 'success'
                df.at[idx, 'geocode_address'] = formatted
                stats['success'] += 1
                
                if (i + 1) % 100 == 0:
                    elapsed = time.time() - start_time
                    rate = (i + 1) / elapsed if elapsed > 0 else 0
                    eta = (stats['total'] - i - 1) / rate if rate > 0 else 0
                    print(f"Progress: {i + 1}/{stats['total']} | "
                          f"Success: {stats['success']} | "
                          f"Failed: {stats['failed']} | "
                          f"Rate: {rate:.2f}/sec | "
                          f"ETA: {eta/60:.1f} min")
                
            except Exception as e:
                df.at[idx, 'geocode_status'] = 'failed'
                df.at[idx, 'geocode_address'] = None
                stats['failed'] += 1
                if (i + 1) % 100 == 0:
                    print(f"Error on row {idx}: {str(e)[:50]}")
            
            stats['processed'] = i + 1
            
            # Checkpoint save
            if (i + 1) % self.chunk_size == 0:
                self._save_checkpoint(df, output_file, i + 1)
        
        # Final save
        print("\nSaving final results...")
        df.to_csv(output_file, index=False)
        
        # Remove checkpoint
        if os.path.exists(self.checkpoint_file):
            os.remove(self.checkpoint_file)
        
        # Print final stats
        elapsed = time.time() - start_time
        print("\n" + "=" * 60)
        print("Geocoding Complete!")
        print(f"Total processed: {stats['processed']}")
        print(f"Successful: {stats['success']} ({stats['success']/stats['total']*100:.1f}%)")
        print(f"Failed: {stats['failed']} ({stats['failed']/stats['total']*100:.1f}%)")
        print(f"Time elapsed: {elapsed/60:.1f} minutes")
        print(f"Average rate: {stats['processed']/elapsed:.2f} addresses/second")
        print(f"Output saved to: {output_file}")
        print("=" * 60)
    
    def _save_checkpoint(self, df: pd.DataFrame, output_file: str, last_processed: int):
        """Save checkpoint file"""
        df.to_csv(output_file, index=False)
        checkpoint = {
            'last_processed': last_processed,
            'timestamp': datetime.now().isoformat()
        }
        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint, f)


def main():
    parser = argparse.ArgumentParser(
        description='Bulk geocode CSV files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Single address column (free OSM)
  python geocode_bulk.py agents.csv output.csv --address "full_address"
  
  # Component columns
  python geocode_bulk.py agents.csv output.csv --street "street" --city "city" --state "state" --zip "zip_code"
  
  # Use Google Maps
  python geocode_bulk.py agents.csv output.csv --provider google --api-key "YOUR_KEY" --address "address"
  
  # Use Mapbox with resume
  python geocode_bulk.py agents.csv output.csv --provider mapbox --api-key "YOUR_KEY" --address "address" --resume
        """
    )
    
    parser.add_argument('input', help='Input CSV file')
    parser.add_argument('output', help='Output CSV file')
    
    parser.add_argument('-p', '--provider', 
                       choices=['nominatim', 'google', 'mapbox'],
                       default='nominatim',
                       help='Geocoding provider (default: nominatim)')
    
    parser.add_argument('-k', '--api-key',
                       help='API key (required for google/mapbox)')
    
    parser.add_argument('-a', '--address',
                       help='Single address column name')
    
    parser.add_argument('--street', help='Street column name')
    parser.add_argument('--city', help='City column name')
    parser.add_argument('--state', help='State column name')
    parser.add_argument('--zip', help='Zip code column name')
    
    parser.add_argument('-r', '--resume', action='store_true',
                       help='Resume from last checkpoint')
    
    parser.add_argument('-c', '--chunk-size', type=int, default=1000,
                       help='Checkpoint interval (default: 1000)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.address and not (args.street or args.city or args.state or args.zip):
        print("Error: Must specify either --address or component columns (--street, --city, etc.)")
        sys.exit(1)
    
    # Create geocoder
    try:
        if args.provider == 'nominatim':
            geocoder = NominatimGeocoder()
        elif args.provider == 'google':
            if not args.api_key:
                print("Error: --api-key is required for Google Maps")
                sys.exit(1)
            geocoder = GoogleGeocoder(args.api_key)
        elif args.provider == 'mapbox':
            if not args.api_key:
                print("Error: --api-key is required for Mapbox")
                sys.exit(1)
            geocoder = MapboxGeocoder(args.api_key)
    except Exception as e:
        print(f"Error initializing geocoder: {e}")
        sys.exit(1)
    
    # Process CSV
    bulk_geocoder = BulkGeocoder(geocoder, chunk_size=args.chunk_size)
    
    try:
        bulk_geocoder.process_csv(
            input_file=args.input,
            output_file=args.output,
            address_column=args.address,
            street_column=args.street,
            city_column=args.city,
            state_column=args.state,
            zip_column=args.zip,
            resume=args.resume
        )
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Progress saved. Use --resume to continue.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

