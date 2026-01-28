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

def extract_short_id(yaml_data, filename):
    """
    Extract the short open_xpd_uuid from YAML data.
    Falls back to filename if not found in YAML.
    """
    # Try to get open_xpd_uuid from YAML
    if 'open_xpd_uuid' in yaml_data:
        return yaml_data['open_xpd_uuid']
    
    # Fallback: use filename without extension as the ID
    return filename.replace('.yaml', '').replace('.yml', '')

def generate_category_csv(region_path, category_name):
    """
    Generate CSV for a specific category with ID to name mapping.
    
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
            yaml_path = os.path.join(category_path, filename)
            
            try:
                with open(yaml_path, 'r', encoding='utf-8') as f:
                    yaml_data = yaml.safe_load(f)
                    
                if yaml_data:
                    product_id = extract_short_id(yaml_data, filename)
                    product_name = extract_product_name(yaml_data)
                    
                    # Extract additional useful fields
                    gwp = yaml_data.get('gwp', '')
                    declared_unit = yaml_data.get('declared_unit', '')
                    
                    products.append({
                        'ID': product_id,
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
            fieldnames = ['ID', 'name', 'gwp', 'declared_unit', 'category']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for product in sorted(products, key=lambda x: x['name']):
                writer.writerow(product)
        
        print(f"Generated: {csv_path} ({len(products)} products)")
    else:
        print(f"No products found in {category_path}")

def move_state_csvs_to_subfolder(region_path):
    """
    Move state CSV files (like US-AK.csv) to a 'states' subfolder.
    
    Args:
        region_path: Path to the region folder (e.g., 'US/')
    """
    region_code = os.path.basename(region_path.rstrip('/'))
    states_folder = os.path.join(region_path, 'states')
    
    # Create states folder if it doesn't exist
    os.makedirs(states_folder, exist_ok=True)
    
    # Pattern for state CSVs: US-XX.csv (2-letter state codes)
    moved_count = 0
    for filename in os.listdir(region_path):
        if filename.endswith('.csv') and filename.startswith(f"{region_code}-"):
            # Check if it's a state file (e.g., US-AK.csv, US-CA.csv)
            parts = filename.replace('.csv', '').split('-')
            if len(parts) == 2 and len(parts[1]) == 2:  # 2-letter state code
                old_path = os.path.join(region_path, filename)
                new_path = os.path.join(states_folder, filename)
                
                # Move the file
                os.rename(old_path, new_path)
                print(f"Moved: {filename} → states/{filename}")
                moved_count += 1
    
    if moved_count > 0:
        print(f"Moved {moved_count} state CSV files to {states_folder}")

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
            
            # Skip files and the new 'states' folder
            if os.path.isfile(item_path) or item == 'states':
                continue
            
            # Process category directory
            print(f"  Category: {item}")
            generate_category_csv(region_path, item)
        
        # Move state CSV files to states subfolder
        print(f"\nMoving state CSV files for {region}...")
        move_state_csvs_to_subfolder(region_path)

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
            
            # Skip files and states folder
            if not os.path.isdir(category_path) or category == 'states':
                continue
            
            for filename in os.listdir(category_path):
                if filename.endswith('.yaml') or filename.endswith('.yml'):
                    yaml_path = os.path.join(category_path, filename)
                    
                    try:
                        with open(yaml_path, 'r', encoding='utf-8') as f:
                            yaml_data = yaml.safe_load(f)
                            
                        if yaml_data:
                            product_id = extract_short_id(yaml_data, filename)
                            product_name = extract_product_name(yaml_data)
                            
                            all_products.append({
                                'region': region,
                                'category': category,
                                'ID': product_id,
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
            fieldnames = ['region', 'category', 'ID', 'name', 'gwp', 'declared_unit']
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