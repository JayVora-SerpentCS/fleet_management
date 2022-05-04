# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    # Module Information
    'name': 'Fleet Operations',
    'category': 'Managing vehicles and contracts',
    'version': '15.0.1.0.0',
    'license': 'LGPL-3',
    'summary': """This module extends the fleet functionality and
     provides extra features and manage fleet operations.
    """,
    'description': """This module extends the fleet functionality and
    provides extra features and manage fleet operations.
    """,
    # Website
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'https://www.serpentcs.com',
    # Dependencies
    'depends': ['fleet', 'stock', 'account'],
    # Data
    'data': [
        'security/fleet_security.xml',
        'security/ir.model.access.csv',
        'data/fleet_extended_data.xml',
        'data/vechical_sequence.xml',
        'wizard/pending_repair_confirm_view.xml',
        'wizard/continue_pending_repair_view.xml',
        'wizard/update_history_view.xml',
        'wizard/writoff_cancel_reason_view.xml',
        'wizard/update_next_service.xml',
        'report/report_xlsx.xml',
        'report/report_write_off_qweb.xml',
        'report/vehicle_change_history_qweb.xml',
        'report/repair_line_summary_qweb.xml',
        'views/fleet_operation_account.xml',
        'views/fleet_service_view.xml',
        'views/fleet_driver_views.xml',
        'views/fleet_extended_view.xml',
        'views/update_pending_history_view.xml',
        'views/mail_template.xml',
        'wizard/work_order_reports_view.xml',
        'wizard/xlsx_report_view.xml',
        'wizard/vehicle_change_history_view.xml',
        'wizard/repair_line_summary_view.xml',
    ],
    'images': ['static/description/fleet_operations_banner.png'],
    'assets': {
        'web.assets_backend': [
                "fleet_operations/static/src/js/web_disable_drag_drop_kanban.js",
            ],
    },
    # Technical
    'demo': ['data/fleet_extended_demo.xml'],
    'installable': True,
    'application': True,
}
