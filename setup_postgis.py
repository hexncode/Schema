#!/usr/bin/env python
"""
PostGIS Setup Script for Schema GIS

This script helps you migrate from file-based GeoPackage storage
to PostgreSQL/PostGIS database.

Usage:
    1. Start Docker Desktop
    2. Run: python setup_postgis.py
"""
import os
import sys
import subprocess
import time


def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def run_command(cmd, check=True):
    print(f"  > {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.returncode != 0 and check:
        print(f"Error: {result.stderr}")
        return False
    return True


def check_docker():
    print_header("Step 1: Checking Docker")
    result = subprocess.run("docker info", shell=True, capture_output=True)
    if result.returncode != 0:
        print("ERROR: Docker is not running!")
        print("Please start Docker Desktop and try again.")
        return False
    print("Docker is running.")
    return True


def start_postgis():
    print_header("Step 2: Starting PostgreSQL/PostGIS")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    if not run_command("docker-compose up -d db pgadmin"):
        return False

    print("\nWaiting for PostgreSQL to be ready...")
    for i in range(30):
        result = subprocess.run(
            'docker exec schema_postgis pg_isready -U schema_user -d schema_gis',
            shell=True, capture_output=True
        )
        if result.returncode == 0:
            print("PostgreSQL is ready!")
            return True
        time.sleep(2)
        print(f"  Waiting... ({i+1}/30)")

    print("ERROR: PostgreSQL did not start in time.")
    return False


def run_migrations():
    print_header("Step 3: Running Django Migrations")
    os.environ['USE_POSTGIS'] = 'True'
    return run_command("python manage.py migrate")


def import_gis_data():
    print_header("Step 4: Importing GIS Data")
    print("This will import ~2.5GB of GIS data into PostgreSQL.")
    print("This may take 10-30 minutes depending on your hardware.\n")

    response = input("Continue with import? [y/N]: ").strip().lower()
    if response != 'y':
        print("Skipping import. You can run it later with:")
        print("  set USE_POSTGIS=True")
        print("  python manage.py import_gis_data")
        return True

    os.environ['USE_POSTGIS'] = 'True'
    return run_command("python manage.py import_gis_data", check=False)


def cleanup_files():
    print_header("Step 5: Cleanup Large Files")
    print("After successful import, you can delete the large GeoPackage files:")
    print("  - atlas/gis/Layers/NSW/Lots.gpkg (2.4 GB)")
    print("  - atlas/gis/Layers/NSW/Suburb.gpkg (149 MB)")
    print("\nThis will free up ~2.5 GB of disk space.")

    response = input("\nDelete GeoPackage files now? [y/N]: ").strip().lower()
    if response == 'y':
        import shutil
        files = [
            'atlas/gis/Layers/NSW/Lots.gpkg',
            'atlas/gis/Layers/NSW/Suburb.gpkg',
        ]
        for f in files:
            try:
                os.remove(f)
                print(f"  Deleted: {f}")
            except FileNotFoundError:
                print(f"  Not found: {f}")
            except Exception as e:
                print(f"  Error deleting {f}: {e}")
    else:
        print("Files kept. Delete manually when ready.")


def print_summary():
    print_header("Setup Complete!")
    print("""
ACCESS POINTS:
  - pgAdmin:      http://localhost:5050
                  Email: admin@schema.local
                  Password: admin123

  - PostgreSQL:   localhost:5432
                  Database: schema_gis
                  User: schema_user
                  Password: schema_secure_password_2024

RUNNING THE APP:
  set USE_POSTGIS=True
  python manage.py runserver

USEFUL COMMANDS:
  docker-compose up -d db pgadmin    # Start database
  docker-compose down                 # Stop database
  docker-compose logs db              # View logs
  python manage.py import_gis_data    # Re-import data
""")


def main():
    print("\n" + "="*60)
    print("  Schema PostGIS Setup")
    print("="*60)

    if not check_docker():
        sys.exit(1)

    if not start_postgis():
        sys.exit(1)

    if not run_migrations():
        print("Migration failed, but continuing...")

    import_gis_data()
    cleanup_files()
    print_summary()


if __name__ == '__main__':
    main()
