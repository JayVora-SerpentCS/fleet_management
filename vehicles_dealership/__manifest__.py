# See LICENSE file for full copyright and licensing details.

{
    # Module Information
    "name": "Vehicles Dealership",
    "category": "vehicles",
    "version": "19.0.1.0.0",
    "license": "LGPL-3",
    "sequence": 1,
    "summary": """Vehicles Dealership Management System""",
    # Website
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "website": "https://www.serpentcs.com",
    # Dependencies
    "depends": ["fleet", "sale_management", "stock", "purchase"],
    # Data
    "data": [
        "data/fleet_vehicle_demo.xml",
        "views/product_views.xml",
        "views/res_company_views.xml",
    ],
    "images": ["static/description/vehicles_dealership_product_banner.jpg"],
    # Technical
    "auto_install": False,
    "installable": True,
    "application": True,
}
