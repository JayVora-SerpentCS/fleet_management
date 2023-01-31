# See LICENSE file for full copyright and licensing details.

{
    # Module Information
    "name": "Fleet Rental Vehicle",
    "category": "Fleet Rent",
    "version": "16.0.1.0.0",
    "license": "LGPL-3",
    "summary": """Rental Vehicle Management System
        This module provides fleet rent features.""",
    # Website
    "author": "Serpent Consulting Services Pvt. Ltd.",
    "website": "https://www.serpentcs.com",
    # Dependencies
    "depends": ["fleet_operations"],
    # Data
    "data": [
        "security/rent_security.xml",
        "security/ir.model.access.csv",
        "data/rent_sequence.xml",
        "data/fleet_rent_data.xml",
        "data/rent_done_scheduler.xml",
        "views/fleet_rent_invoice_view.xml",
        "views/fleet_rent_view.xml",
        "views/fleet_res_partner_view.xml",
        "views/fleet_res_users_view.xml",
        "views/res_users_view.xml",
        "views/fleet_view.xml",
        "wizard/renew_tenancy_view.xml",
        "wizard/rent_close_reason_view.xml",
        "report/fleet_rent.xml",
    ],
    "images": ["static/description/fleet_rental_vehicle_banner.png"],
    "assets": {
        "web.assets_backend": [
            "fleet_rent/static/src/css/fleet_rent.scss",
            "fleet_rent/static/src/css/rent_order.css",
        ],
    },
    # Technical
    "installable": True,
    "application": True,
}
