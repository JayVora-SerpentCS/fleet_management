# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Fleet Rental Vehicle',
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'website': 'http://www.serpentcs.com',
    'category': 'Fleet Rent',
    'description': """
    Rental Vehicle Management System
    This module provides fleet rent features..
     """,
     'depends': ['analytic', 'account_voucher', 'ow_account_asset',
                'ow_account_budget', 'fleet_operations'],
    'data': [
            'security/rent_security.xml',
            'security/ir.model.access.csv',
            'data/rent_sequence.xml',
            'data/fleet_rent_data.xml',
            'data/rent_done_scheduler.xml',
            'views/account_analytic_view.xml',
            'views/fleet_rent_view.xml',
            'views/asset_view.xml',
            'views/fleet_view.xml',
            'views/template.xml',
            'wizard/renew_tenancy_view.xml',
            'wizard/rent_close_reason_view.xml',
            'wizard/fleet_rental_vehicle_history_view.xml',
             ],
    'auto_install': False,
    'installable': True,
    'application': True,
}
