import os
import yaml

def rename_yaml_files_in_category(region_path, category_name, dry_run=False):
    """
    Rename YAML files in a category from long UUID to short open_xpd_uuid.
    
    Args:
        region_path: Path to the region folder (e.g., 'US/')
        category_name: Name of the category folder
        dry_run: If True, only show what would be done without actually renaming
    """
    category_path = os.path.join(region_path, category_name)
    
    if not os.path.isdir(category_path):
        return
    
    renamed_count = 0
    skipped_count = 0
    error_count = 0
    
    # Get all YAML files
    yaml_files = [f for f in os.listdir(category_path) 
                  if f.endswith('.yaml') or f.endswith('.yml')]
    
    if not yaml_files:
        print(f"  ℹ️  No YAML files found")
        return
    
    for filename in yaml_files:
        old_path = os.path.join(category_path, filename)
        
        try:
            # Read the YAML file
            with open(old_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            if not yaml_data:
                print(f"  ⚠️  Skipping {filename} - empty or invalid YAML")
                skipped_count += 1
                continue
            
            # Get the short ID (top-level open_xpd_uuid only)
            if 'open_xpd_uuid' not in yaml_data:
                print(f"  ⚠️  Skipping {filename} - no open_xpd_uuid field at top level")
                error_count += 1
                continue
            
            short_id = yaml_data['open_xpd_uuid']
            
            if not short_id or not isinstance(short_id, str):
                print(f"  ⚠️  Skipping {filename} - invalid open_xpd_uuid value")
                error_count += 1
                continue
            
            # Check if filename is already the short ID
            current_name_without_ext = filename.replace('.yaml', '').replace('.yml', '')
            if current_name_without_ext == short_id:
                skipped_count += 1
                continue
            
            # New filename with short ID
            new_filename = f"{short_id}.yaml"
            new_path = os.path.join(category_path, new_filename)
            
            # Check if new file already exists
            if os.path.exists(new_path):
                if dry_run:
                    print(f"  🔍 Would delete (duplicate): {filename}")
                else:
                    print(f"  ⚠️  File already exists: {new_filename}, deleting old: {filename}")
                    os.remove(old_path)
                    print(f"  🗑️  Deleted: {filename}")
                continue
            
            # Rename the file
            if dry_run:
                print(f"  🔍 Would rename: {filename} → {new_filename}")
            else:
                os.rename(old_path, new_path)
                print(f"  ✓ Renamed: {filename} → {new_filename}")
            renamed_count += 1
            
        except Exception as e:
            print(f"  ❌ Error processing {filename}: {e}")
            error_count += 1
    
    # Summary for this category
    if renamed_count > 0 or error_count > 0:
        summary = []
        if renamed_count > 0:
            summary.append(f"✓ {renamed_count} renamed")
        if skipped_count > 0:
            summary.append(f"→ {skipped_count} skipped")
        if error_count > 0:
            summary.append(f"❌ {error_count} errors")
        print(f"  📊 {', '.join(summary)}")

def rename_all_yaml_files(base_path='.', dry_run=False):
    """
    Rename all YAML files in all regions and categories.
    
    Args:
        base_path: Base directory containing region folders
        dry_run: If True, only show what would be done
    """
    regions = ['US', 'IN', 'CN', 'EU']
    
    for region in regions:
        region_path = os.path.join(base_path, region)
        
        if not os.path.isdir(region_path):
            continue
        
        print(f"\n{'='*60}")
        print(f"Processing region: {region}")
        print(f"{'='*60}")
        
        # Get all subdirectories (categories)
        categories = [item for item in os.listdir(region_path)
                     if os.path.isdir(os.path.join(region_path, item))
                     and item != 'states']
        
        if not categories:
            print("  ℹ️  No categories found")
            continue
        
        for category in sorted(categories):
            print(f"\n📁 Category: {category}")
            rename_yaml_files_in_category(region_path, category, dry_run)

def confirm_operation(dry_run=False):
    """
    Ask user to confirm before renaming files.
    """
    if dry_run:
        print("\n" + "="*60)
        print("🔍 DRY RUN MODE - No files will be modified")
        print("="*60)
        return True
    
    print("\n" + "="*60)
    print("⚠️  WARNING: This script will rename YAML files")
    print("="*60)
    print("\nThis will:")
    print("  1. Read each YAML file")
    print("  2. Extract the top-level open_xpd_uuid field")
    print("  3. Rename the file from long UUID to short ID")
    print("  4. Delete old files if new ones already exist")
    print("\n" + "="*60)
    
    response = input("\nDo you want to continue? (yes/no): ").strip().lower()
    
    if response not in ['yes', 'y']:
        print("\n❌ Operation cancelled.")
        return False
    
    return True

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Rename YAML files from long UUID to short open_xpd_uuid'
    )
    parser.add_argument(
        '--path', 
        default='.', 
        help='Base path to scan (default: current directory)'
    )
    parser.add_argument(
        '--yes', 
        action='store_true', 
        help='Skip confirmation prompt'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without actually renaming files'
    )
    
    args = parser.parse_args()
    
    # Confirm before proceeding
    if not args.yes and not args.dry_run:
        if not confirm_operation(args.dry_run):
            exit(0)
    elif args.dry_run:
        confirm_operation(args.dry_run)
    
    print("\n🚀 Starting YAML file renaming...\n")
    rename_all_yaml_files(args.path, args.dry_run)
    
    if args.dry_run:
        print("\n✅ Dry run complete!")
        print("\nTo actually rename files, run without --dry-run flag")
    else:
        print("\n✅ Done!")
        print("\nNext steps:")
        print("  1. Review the changes in GitHub Desktop")
        print("  2. Commit with: 'Rename YAML files to use short open_xpd_uuid'")
        print("  3. Push to your fork")