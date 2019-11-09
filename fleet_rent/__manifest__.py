# See LICENSE file for full copyright and licensing details.

{
    # Module Information
    'name': 'Fleet Rental Vehicle',
    'category': 'Fleet Rent',
    'sequence': 1,
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'summary': """Rental Vehicle Management System
        This module provides fleet rent features.""",
    'description': """
        Rental Vehicle Management System
        This module provides fleet rent features..
     """,
    # Website
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'http://www.serpentcs.com',

    # Dependencies
    'depends': ['analytic', 'account_voucher',
                'fleet_operations'],
    # Data
    'data': [
            'security/rent_security.xml',
            'security/ir.model.access.csv',
            'data/rent_sequence.xml',
            'data/fleet_rent_data.xml',
            'data/rent_done_scheduler.xml',

            'views/fleet_rent_invoice_view.xml',
            'views/fleet_rent_view.xml',
            'views/fleet_res_partner_view.xml',
            'views/fleet_res_users_view.xml',
            'views/res_users_view.xml',
            'views/driver_res_users_view.xml',

            'views/fleet_view.xml',
            'views/template.xml',
            'wizard/renew_tenancy_view.xml',
            'wizard/rent_close_reason_view.xml',
            'wizard/fleet_rental_vehicle_history_view.xml',
            'report/fleet_rent.xml',
    ],
    # Technical
    'auto_install': False,
    'installable': True,
    'application': True,
}
