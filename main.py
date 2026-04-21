#!/usr/bin/env python3
"""
Maps GitHub URLs from shopify_data directory to woo_import.csv
Scans product folders and generates GitHub image URLs for WooCommerce import
"""

import os
import csv
from pathlib import Path
from collections import defaultdict

# Configuration
SHOPIFY_DATA_DIR = Path("product-images")
WOO_IMPORT_CSV = "woo_import.csv"
OUTPUT_CSV = "woo_import_updated.csv"
GITHUB_BASE_URL = "https://raw.githubusercontent.com/AdityaGupta832342/product-images/main"

def scan_shopify_data():
    """
    Scans shopify_data directory and creates a mapping of SKU to image files
    Returns: dict {sku: [image_file1, image_file2, ...]}
    """
    sku_images = defaultdict(list)
    
    if not SHOPIFY_DATA_DIR.exists():
        print(f"Error: {SHOPIFY_DATA_DIR} directory not found")
        return sku_images
    
    for sku_dir in SHOPIFY_DATA_DIR.iterdir():
        if not sku_dir.is_dir():
            continue
        
        sku = sku_dir.name
        images = []
        
        # Collect all image files (common image extensions)
        for image_file in sku_dir.iterdir():
            if image_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.webp']:
                images.append(image_file.name)
        
        if images:
            # Sort for consistency
            images.sort()
            sku_images[sku] = images
    
    return sku_images

def generate_github_urls(sku, image_files):
    """
    Generates GitHub URLs for image files
    Returns: comma-separated list of GitHub URLs
    """
    urls = []
    for image_file in image_files:
        url = f"{GITHUB_BASE_URL}/{sku}/{image_file}"
        urls.append(url)
    return ",".join(urls)

def read_woo_csv():
    """
    Reads the WooCommerce import CSV
    Returns: tuple (headers, rows as list of dicts)
    """
    headers = []
    rows = []
    
    if not Path(WOO_IMPORT_CSV).exists():
        print(f"Error: {WOO_IMPORT_CSV} not found")
        return headers, rows
    
    with open(WOO_IMPORT_CSV, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames
        rows = list(reader)
    
    return headers, rows

def map_urls_to_csv(sku_images):
    """
    Maps GitHub URLs to CSV entries based on SKU
    Returns: updated rows with mapped URLs
    """
    headers, rows = read_woo_csv()
    
    if not headers:
        return headers, rows
    
    updated_rows = []
    sku_column = "SKU"
    images_column = "Images"
    
    # Verify columns exist
    if sku_column not in headers or images_column not in headers:
        print(f"Error: CSV must have '{sku_column}' and '{images_column}' columns")
        return headers, rows
    
    for row in rows:
        sku = row.get(sku_column, "").strip()
        
        if sku in sku_images:
            # Update with GitHub URLs from shopify_data
            github_urls = generate_github_urls(sku, sku_images[sku])
            row[images_column] = github_urls
            print(f"✓ {sku}: {len(sku_images[sku])} image(s) mapped")
        else:
            # Keep existing URLs if SKU not found in shopify_data
            print(f"⚠ {sku}: Not found in shopify_data, keeping existing URLs")
        
        updated_rows.append(row)
    
    return headers, updated_rows

def save_to_csv(headers, rows, output_file):
    """
    Saves updated rows to CSV file
    """
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\n✓ Updated CSV saved to: {output_file}")

def print_mapping_summary(sku_images):
    """
    Prints summary of found SKUs and images
    """
    print("\n=== Shopify Data Mapping Summary ===")
    print(f"Found {len(sku_images)} products in shopify_data directory:\n")
    
    for sku in sorted(sku_images.keys()):
        images = sku_images[sku]
        print(f"  {sku}:")
        for img in images:
            print(f"    - {img}")

def main():
    """
    Main function to orchestrate the mapping process
    """
    print("Starting GitHub URL mapping...\n")
    
    # Step 1: Scan shopify_data directory
    print("Step 1: Scanning shopify_data directory...")
    sku_images = scan_shopify_data()
    
    if not sku_images:
        print("No images found in shopify_data directory")
        return
    
    print(f"Found images for {len(sku_images)} products\n")
    
    # Step 2: Print summary
    print_mapping_summary(sku_images)
    
    # Step 3: Map URLs to CSV
    print("\n\nStep 2: Mapping URLs to CSV...")
    headers, updated_rows = map_urls_to_csv(sku_images)
    
    # Step 4: Save updated CSV
    if headers and updated_rows:
        print(f"\nStep 3: Saving updated CSV...")
        save_to_csv(headers, updated_rows, OUTPUT_CSV)
        print("\n✓ Mapping complete!")
        
        # Print sample
        print(f"\n=== Sample Mapping ===")
        if updated_rows:
            sample = updated_rows[0]
            sku = sample.get("SKU", "")
            images = sample.get("Images", "")
            print(f"SKU: {sku}")
            print(f"URLs: {images}")
    else:
        print("Error: Could not process CSV file")

if __name__ == "__main__":
    main()