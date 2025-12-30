

import os
import csv
import yaml
from pathlib import Path

def extract_product_name(yaml_data):
    """
    Extract product name from YAML data.
    Tries multiple possible fields in order of preference.
    """
    # Try different possible name fields
    if 'name' in yaml_data:
        return yaml_data['name']
    elif 'product_specific' in yaml_data and 'product_name' in yaml_data['product_specific']:
        return yaml_data['product_specific']['product_name']
    elif 'product_name' in yaml_data:
        return yaml_data['product_name']
    else:
        return "Unknown Product"

def generate_category_csv(region_path, category_name):
    """
    Generate CSV for a specific category with UUID to name mapping.
    
    Args:
        region_path: Path to the region folder (e.g., 'IN/', 'US/')
        category_name: Name of the category folder
    """
    category_path = os.path.join(region_path, category_name)
    
    if not os.path.isdir(category_path):
        print(f"Warning: {category_path} is not a directory")
        return
    
    # Collect product data
    products = []
    
    # Scan all YAML files in the category
    for filename in os.listdir(category_path):
        if filename.endswith('.yaml') or filename.endswith('.yml'):
            uuid = filename.replace('.yaml', '').replace('.yml', '')
            yaml_path = os.path.join(category_path, filename)
            
            try:
                with open(yaml_path, 'r', encoding='utf-8') as f:
                    yaml_data = yaml.safe_load(f)
                    
                if yaml_data:
                    product_name = extract_product_name(yaml_data)
                    
                    # Extract additional useful fields
                    gwp = yaml_data.get('gwp', '')
                    declared_unit = yaml_data.get('declared_unit', '')
                    
                    products.append({
                        'uuid': uuid,
                        'name': product_name,
                        'gwp': gwp,
                        'declared_unit': declared_unit,
                        'category': category_name
                    })
            except Exception as e:
                print(f"Error processing {yaml_path}: {e}")
                continue
    
    # Write CSV file
    if products:
        # Determine region code from path
        region_code = os.path.basename(region_path.rstrip('/'))
        csv_filename = f"{region_code}-{category_name}.csv"
        csv_path = os.path.join(region_path, csv_filename)
        
        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['uuid', 'name', 'gwp', 'declared_unit', 'category']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for product in sorted(products, key=lambda x: x['name']):
                writer.writerow(product)
        
        print(f"Generated: {csv_path} ({len(products)} products)")
    else:
        print(f"No products found in {category_path}")

def generate_all_category_csvs(base_path='.'):
    """
    Generate CSV files for all categories in all regions.
    
    Args:
        base_path: Base directory containing region folders (default: current directory)
    """
    # Common region codes
    regions = ['US', 'IN', 'CN', 'EU']  # Add more as needed
    
    for region in regions:
        region_path = os.path.join(base_path, region)
        
        if not os.path.isdir(region_path):
            print(f"Skipping {region} - directory not found")
            continue
        
        print(f"\nProcessing region: {region}")
        
        # Get all subdirectories (categories)
        for item in os.listdir(region_path):
            item_path = os.path.join(region_path, item)
            
            # Skip files and CSV files
            if os.path.isfile(item_path):
                continue
            
            # Process category directory
            print(f"  Category: {item}")
            generate_category_csv(region_path, item)

def generate_master_csv(base_path='.', output_file='all_products.csv'):
    """
    Generate a master CSV containing all products from all regions and categories.
    
    Args:
        base_path: Base directory containing region folders
        output_file: Output CSV filename
    """
    all_products = []
    regions = ['US', 'IN', 'CN', 'EU']
    
    for region in regions:
        region_path = os.path.join(base_path, region)
        
        if not os.path.isdir(region_path):
            continue
        
        for category in os.listdir(region_path):
            category_path = os.path.join(region_path, category)
            
            if not os.path.isdir(category_path):
                continue
            
            for filename in os.listdir(category_path):
                if filename.endswith('.yaml') or filename.endswith('.yml'):
                    uuid = filename.replace('.yaml', '').replace('.yml', '')
                    yaml_path = os.path.join(category_path, filename)
                    
                    try:
                        with open(yaml_path, 'r', encoding='utf-8') as f:
                            yaml_data = yaml.safe_load(f)
                            
                        if yaml_data:
                            product_name = extract_product_name(yaml_data)
                            
                            all_products.append({
                                'region': region,
                                'category': category,
                                'uuid': uuid,
                                'name': product_name,
                                'gwp': yaml_data.get('gwp', ''),
                                'declared_unit': yaml_data.get('declared_unit', '')
                            })
                    except Exception as e:
                        print(f"Error processing {yaml_path}: {e}")
                        continue
    
    # Write master CSV
    if all_products:
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['region', 'category', 'uuid', 'name', 'gwp', 'declared_unit']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for product in sorted(all_products, key=lambda x: (x['region'], x['category'], x['name'])):
                writer.writerow(product)
        
        print(f"\nGenerated master CSV: {output_file} ({len(all_products)} total products)")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate CSV overview files for product categories')
    parser.add_argument('--path', default='.', help='Base path to scan (default: current directory)')
    parser.add_argument('--master', action='store_true', help='Also generate a master CSV with all products')
    
    args = parser.parse_args()
    
    print("Generating category CSV files...")
    generate_all_category_csvs(args.path)
    
    if args.master:
        print("\nGenerating master CSV...")
        generate_master_csv(args.path)
    
    print("\nDone!")