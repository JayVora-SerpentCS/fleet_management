# See LICENSE file for full copyright and licensing details.

{
    # Module Information
    "name": (
        "Vehicles Dealership | Vehicle Dealership Management | Odoo Car Dealership | "
        "Odoo Vehicle Sales and Purchase | Dealership Vehicle Management"
    ),
    "category": "vehicles",
    "version": "20.0.1.0.0",
    "license": "LGPL-3",
    "sequence": 1,
    "summary": (
        "Vehicle Dealership Management | Odoo Vehicle Dealership | "
        "Odoo Car Dealership | \n"
        "        Odoo Vehicle Sales | Odoo Vehicle Purchase | "
        "Dealership Product Management | \n"
        "        Car Sales and Purchase Management | Vehicle Dealership System"
    ),
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
    "images": ["static/description/vehicles_dealership_product_banner.gif"],
    # Technical
    "auto_install": False,
    "installable": True,
    "application": True,
}
