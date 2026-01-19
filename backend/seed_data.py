"""
╔═══════════════════════════════════════════════════════════════════════════╗
║                                                                           ║
║   ██╗  ██╗    ██╗  ██╗          ██╗  ██╗ ██████╗ ██╗     ██████╗ ██╗███╗   ██╗ ██████╗ ███████╗  ║
║   ██║  ██║    ██║  ██║          ██║  ██║██╔═══██╗██║     ██╔══██╗██║████╗  ██║██╔════╝ ██╔════╝  ║
║   ███████║    ███████║          ███████║██║   ██║██║     ██║  ██║██║██╔██╗ ██║██║  ███╗███████╗  ║
║   ██╔══██║    ██╔══██║          ██╔══██║██║   ██║██║     ██║  ██║██║██║╚██╗██║██║   ██║╚════██║  ║
║   ██║  ██║    ██║  ██║          ██║  ██║╚██████╔╝███████╗██████╔╝██║██║ ╚████║╚██████╔╝███████║  ║
║   ╚═╝  ╚═╝    ╚═╝  ╚═╝          ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═════╝ ╚═╝╚═╝  ╚═══╝ ╚═════╝ ╚══════╝  ║
║                                                                           ║
║                 BOSQUE COUNTY MINERAL & COMMODITIES EXCHANGE             ║
║                         Seed Data Loading Script                         ║
║                                                                           ║
║   Operator:    HH Holdings LLC / Bevans Real Estate                      ║
║   Location:    397 Highway 22, Clifton, TX 76634                         ║
║   Broker:      Biri Bevans, Designated Broker                            ║
║   Module:      Database Seed Data Loader                                 ║
║                                                                           ║
║   Copyright:   © 2026 HH Holdings LLC. All rights reserved.              ║
║                                                                           ║
╚═══════════════════════════════════════════════════════════════════════════╝

BCMCE Platform - Seed Data Loading Script
Load reference data (materials, suppliers) and create initial admin user
"""

import json
import sys
import os
from pathlib import Path
from passlib.context import CryptContext
from sqlalchemy.orm import Session

# Add parent directory to path to import database module
sys.path.insert(0, str(Path(__file__).parent))

from database import SessionLocal, Material, Supplier, User
from config import get_settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

settings = get_settings()


def load_materials(db: Session):
    """
    Load material types from data/seed/materials.json

    Creates 12 material types commonly used in Central Texas county projects:
    - Road Base Gravel
    - Flexible Base Grade 1-2
    - Caliche
    - Lime Slurry
    - Crushed Limestone
    - Pea Gravel
    - Topping Gravel
    - Fill Clay
    - Portland Cement
    - Crusher Run
    - Quicklime
    - Hot Mix Asphalt
    """
    materials_file = Path(__file__).parent.parent / "data" / "seed" / "materials.json"

    print(f"Loading materials from {materials_file}...")

    with open(materials_file, 'r') as f:
        materials_data = json.load(f)

    loaded_count = 0
    skipped_count = 0

    for material_data in materials_data:
        # Check if material already exists by name
        existing = db.query(Material).filter(Material.name == material_data["name"]).first()

        if existing:
            print(f"  ⚠️  Material already exists: {material_data['name']}")
            skipped_count += 1
            continue

        # Create material
        material = Material(
            name=material_data["name"],
            material_type=material_data["category"],
            txdot_spec=material_data.get("txdot_spec"),
            unit=material_data["unit"],
            description=material_data.get("description")
        )

        db.add(material)
        print(f"  ✓ Created material: {material_data['name']} ({material_data['code']})")
        loaded_count += 1

    db.commit()
    print(f"\nMaterials loaded: {loaded_count} created, {skipped_count} skipped")
    return loaded_count


def load_suppliers(db: Session):
    """
    Load supplier contacts from data/seed/suppliers.json

    Creates 7 local suppliers in Central Texas:
    - Clifton Quarry (Clifton)
    - Bosque River Pit (Meridian)
    - Central Texas Stone & Aggregate (Waco)
    - Texas Lime Solutions (Temple)
    - Loftin Dirt Works (Valley Mills)
    - Morgan Quarry & Materials (Morgan)
    - Waco Concrete & Materials (Waco)
    """
    suppliers_file = Path(__file__).parent.parent / "data" / "seed" / "suppliers.json"

    print(f"\nLoading suppliers from {suppliers_file}...")

    with open(suppliers_file, 'r') as f:
        suppliers_data = json.load(f)

    loaded_count = 0
    skipped_count = 0

    for supplier_data in suppliers_data:
        # Check if supplier already exists by email
        existing = db.query(Supplier).filter(Supplier.email == supplier_data["email"]).first()

        if existing:
            print(f"  ⚠️  Supplier already exists: {supplier_data['name']}")
            skipped_count += 1
            continue

        # Create supplier
        supplier = Supplier(
            name=supplier_data["name"],
            contact_name=supplier_data["contact_name"],
            email=supplier_data["email"],
            phone=supplier_data["phone"],
            address=supplier_data["address"],
            city=supplier_data["city"],
            state=supplier_data["state"],
            zip_code=supplier_data["zip_code"],
            is_active=supplier_data["status"] == "active"
        )

        db.add(supplier)
        print(f"  ✓ Created supplier: {supplier_data['name']} ({supplier_data['city']}, TX)")
        loaded_count += 1

    db.commit()
    print(f"\nSuppliers loaded: {loaded_count} created, {skipped_count} skipped")
    return loaded_count


def create_admin_user(db: Session):
    """
    Create initial H.H. Holdings admin user

    User: Biri Bevans (Designated Broker)
    Email: biri@hhholdings.com
    Role: admin
    Default Password: HHHoldings2026! (should be changed on first login)
    """
    admin_email = os.getenv("HH_HOLDINGS_EMAIL", "biri@hhholdings.com")

    print(f"\nCreating H.H. Holdings admin user...")

    # Check if admin already exists
    existing = db.query(User).filter(User.email == admin_email).first()

    if existing:
        print(f"  ⚠️  Admin user already exists: {admin_email}")
        return 0

    # Create admin user
    default_password = "HHHoldings2026!"
    hashed_password = pwd_context.hash(default_password)

    admin_user = User(
        email=admin_email,
        hashed_password=hashed_password,
        full_name="Biri Bevans",
        role="admin",
        is_active=True,
        supplier_id=None,
        county_id=None
    )

    db.add(admin_user)
    db.commit()

    print(f"  ✓ Created admin user: {admin_email}")
    print(f"  📧 Email: {admin_email}")
    print(f"  🔒 Default Password: {default_password}")
    print(f"  ⚠️  IMPORTANT: Change password on first login!")

    return 1


def main():
    """
    Main entry point for seed data loading

    Usage:
        python seed_data.py

    Loads:
        1. Materials (12 types)
        2. Suppliers (7 local suppliers)
        3. Admin user (Biri Bevans)
    """
    print("\n" + "="*80)
    print("BCMCE Platform - Seed Data Loader")
    print("H.H. Holdings Internal Tool")
    print("="*80 + "\n")

    db = SessionLocal()

    try:
        # Load materials
        materials_count = load_materials(db)

        # Load suppliers
        suppliers_count = load_suppliers(db)

        # Create admin user
        admin_count = create_admin_user(db)

        print("\n" + "="*80)
        print("SEED DATA LOADING COMPLETE")
        print("="*80)
        print(f"Materials: {materials_count} loaded")
        print(f"Suppliers: {suppliers_count} loaded")
        print(f"Admin user: {admin_count} created")
        print("\n✅ Database seeded successfully!")
        print("\nYou can now:")
        print("  1. Start the API server: uvicorn main:app --reload")
        print("  2. Login with: biri@hhholdings.com / HHHoldings2026!")
        print("  3. Start adding options and tracking RFPs")
        print("\n")

    except Exception as e:
        print(f"\n❌ Error loading seed data: {e}")
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    main()
