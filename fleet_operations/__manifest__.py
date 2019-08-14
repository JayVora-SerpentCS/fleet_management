# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

{
    # Module Information
    'name': 'Fleet Operations',
    'category': 'Managing vehicles and contracts',
    'sequence': 1,
    'version': '12.0.1.0.0',
    'license': 'LGPL-3',
    'summary': """This module extends the fleet functionality and
     provides extra features and manage fleet operations.
    """,
    'description': """This module extends the fleet functionality and
    provides extra features and manage fleet operations.
    """,
    # Website
    'author': 'Serpent Consulting Services Pvt. Ltd.',
    'website': 'http://www.serpentcs.com',
    # Dependencies
    'depends': ['fleet', 'stock', 'account',
                'web_widget_multi_image'],
    # Data
    'data': [
              'security/fleet_security.xml',
              'security/ir.model.access.csv',
              'data/color.color.csv',
              'data/vehicle.type.csv',
              'data/fleet_extended_data.xml',
              'data/vechical_sequence.xml',
              'wizard/pending_repair_confirm_view.xml',
              'wizard/continue_pending_repair_view.xml',
              'wizard/update_history_view.xml',
              'wizard/writoff_cancel_reason_view.xml',
              'report/report_xlsx.xml',
              'report/report_write_off_qweb.xml',
              'report/vehicle_change_history_qweb.xml',
              'report/repair_line_summary_qweb.xml',
              'views/workflow_sequence.xml',
              'views/department_location_view.xml',
              'views/fleet_extended_view.xml',
              'views/fleet_service_view.xml',
              'views/update_pending_history_view.xml',
              'views/template.xml',
              'wizard/work_order_reports_view.xml',
              'wizard/xlsx_report_view.xml',
              'wizard/vehicle_change_history_view.xml',
              'wizard/repair_line_summary_view.xml',
    ],
    # Technical
    'demo': ['data/fleet_extended_demo.xml'],
    'installable': True,
    'application': True,
}
