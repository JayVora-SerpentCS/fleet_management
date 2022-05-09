# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    'name': 'Vehicles Dealership',
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'version': '11.0.1.0.0',
    'license': 'AGPL-3',
    'website': 'http://www.serpentcs.com',
    'category': 'vehicles',
    'description': """
        Vehicles Dealership Management System
     """,
    'depends': ['fleet', 'sale_management', 'purchase'],
    'data': [
        "views/product_views.xml",
        "views/res_company_views.xml",
    ],
    'images': ['static/description/vehicles_dealership_banner.png'],
    'auto_install': False,
    'installable': True,
    'application': True,
}
