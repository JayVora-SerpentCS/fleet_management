# See LICENSE file for full copyright and licensing details.

{
    # Module Information
    'name': 'Vehicles Dealership',
    'category': 'vehicles',
    'sequence': 1,
    'version': '12.0.1.0.0',
    'license': 'AGPL-3',
    'summary': """Vehicles Dealership Management System""",
    'description': """
        Vehicles Dealership Management System
     """,

    # Website
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'http://www.serpentcs.com',

    # Dependenices
    'depends': ['fleet', 'sale_management', 'purchase'],

    # Data
    'data': [
        "views/product_views.xml",
        "views/res_company_views.xml",
    ],

    # Technical
    'auto_install': False,
    'installable': True,
    'application': True,
}
