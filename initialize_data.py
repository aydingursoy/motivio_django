"""
Script to initialize the project with default maintenance categories and cost estimates.
Run this after migrating the database.
"""

import os
import django
import csv
from decimal import Decimal

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'motivio_project.settings')
django.setup()

from maintenance.models import MaintenanceCategory, CostEstimate

def create_maintenance_categories():
    """Create default maintenance categories"""
    categories = [
        {
            'name': 'Oil Change',
            'description': 'Change engine oil and filter',
            'suggested_interval_miles': 5000,
            'suggested_interval_months': 6
        },
        {
            'name': 'Tire Rotation',
            'description': 'Rotate tires to ensure even wear',
            'suggested_interval_miles': 7500,
            'suggested_interval_months': 6
        },
        {
            'name': 'Brake Service',
            'description': 'Inspect, clean, and adjust brakes',
            'suggested_interval_miles': 15000,
            'suggested_interval_months': 12
        },
        {
            'name': 'Air Filter Replacement',
            'description': 'Replace engine air filter',
            'suggested_interval_miles': 15000,
            'suggested_interval_months': 12
        },
        {
            'name': 'Cabin Air Filter Replacement',
            'description': 'Replace cabin air filter',
            'suggested_interval_miles': 15000,
            'suggested_interval_months': 12
        },
        {
            'name': 'Spark Plug Replacement',
            'description': 'Replace spark plugs',
            'suggested_interval_miles': 60000,
            'suggested_interval_months': 36
        },
        {
            'name': 'Transmission Fluid Service',
            'description': 'Change transmission fluid',
            'suggested_interval_miles': 60000,
            'suggested_interval_months': 36
        },
        {
            'name': 'Cooling System Flush',
            'description': 'Flush and replace coolant',
            'suggested_interval_miles': 60000,
            'suggested_interval_months': 36
        },
        {
            'name': 'Timing Belt Replacement',
            'description': 'Replace timing belt',
            'suggested_interval_miles': 90000,
            'suggested_interval_months': 60
        },
        {
            'name': 'Battery Replacement',
            'description': 'Replace vehicle battery',
            'suggested_interval_miles': 50000,
            'suggested_interval_months': 36
        },
        {
            'name': 'Wiper Blade Replacement',
            'description': 'Replace windshield wiper blades',
            'suggested_interval_miles': 15000,
            'suggested_interval_months': 6
        },
        {
            'name': 'Wheel Alignment',
            'description': 'Align wheels',
            'suggested_interval_miles': 15000,
            'suggested_interval_months': 12
        }
    ]

    # Create categories if they don't already exist
    for category_data in categories:
        MaintenanceCategory.objects.get_or_create(
            name=category_data['name'],
            defaults={
                'description': category_data['description'],
                'suggested_interval_miles': category_data['suggested_interval_miles'],
                'suggested_interval_months': category_data['suggested_interval_months']
            }
        )

    print(f"Created {len(categories)} maintenance categories")
    return MaintenanceCategory.objects.all()

def create_cost_estimates(categories):
    """Create some sample cost estimates for common vehicles"""
    common_makes = ['Toyota', 'Honda', 'Ford', 'Chevrolet', 'Nissan', 'BMW', 'Mercedes-Benz', 'Audi']

    # Dictionary of basic cost estimates for each category
    # These will be adjusted slightly for each make to create some variety
    base_costs = {
        'Oil Change': {'min': 25, 'max': 80, 'avg': 45},
        'Tire Rotation': {'min': 20, 'max': 50, 'avg': 35},
        'Brake Service': {'min': 150, 'max': 400, 'avg': 250},
        'Air Filter Replacement': {'min': 15, 'max': 50, 'avg': 30},
        'Cabin Air Filter Replacement': {'min': 15, 'max': 70, 'avg': 40},
        'Spark Plug Replacement': {'min': 50, 'max': 300, 'avg': 150},
        'Transmission Fluid Service': {'min': 100, 'max': 400, 'avg': 200},
        'Cooling System Flush': {'min': 80, 'max': 250, 'avg': 150},
        'Timing Belt Replacement': {'min': 300, 'max': 1000, 'avg': 600},
        'Battery Replacement': {'min': 100, 'max': 300, 'avg': 180},
        'Wiper Blade Replacement': {'min': 20, 'max': 80, 'avg': 40},
        'Wheel Alignment': {'min': 70, 'max': 200, 'avg': 120}
    }

    # Cost adjustment factors for different makes
    make_factors = {
        'Toyota': 1.0,
        'Honda': 1.0,
        'Ford': 0.9,
        'Chevrolet': 0.9,
        'Nissan': 1.1,
        'BMW': 1.7,
        'Mercedes-Benz': 1.8,
        'Audi': 1.6
    }

    estimates_created = 0

    for category in categories:
        if category.name in base_costs:
            base_cost = base_costs[category.name]

            for make in common_makes:
                factor = make_factors[make]

                # Create or update cost estimate
                CostEstimate.objects.update_or_create(
                    category=category,
                    make=make,
                    defaults={
                        'model': '',  # Generic for all models
                        'year_start': 2000,
                        'year_end': 2025,
                        'min_cost': Decimal(base_cost['min'] * factor),
                        'max_cost': Decimal(base_cost['max'] * factor),
                        'average_cost': Decimal(base_cost['avg'] * factor)
                    }
                )
                estimates_created += 1

    print(f"Created {estimates_created} cost estimates")

if __name__ == "__main__":
    print("Initializing Motivio with default data...")
    categories = create_maintenance_categories()
    create_cost_estimates(categories)
    print("Initialization complete!")
