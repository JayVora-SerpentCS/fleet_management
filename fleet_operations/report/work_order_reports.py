# See LICENSE file for full copyright and licensing details.
"""Work Order report."""

from odoo import api, fields, models


class WorkOrderReports(models.TransientModel):
    """Work Order Reports."""

    _name = 'work.order.reports'
    _description = "Work Order Reports"

    select_report = fields.Selection([
        ('wo_month_sum_rep', 'Vehicle Services Monthly Summary Report')], default='wo_month_sum_rep')
    name = fields.Char("Name", default='Genric Report.xls')
    vehicle_ids = fields.Many2many('fleet.vehicle', 'fleet_wo_report_rel',
                                   'wor_id', 'vehicle_id',
                                   string="Vehicle")
    file = fields.Binary("Click On Download Link To Download Xls File",
                         readonly=True)

    def print_wo_xlsx_report(self):
        """Print Wo xlsx report."""
        for vehicle in self:
            wo_obj = self.env['fleet.vehicle.log.services']
            records = wo_obj.search([])
            if vehicle.vehicle_ids:
                records = wo_obj.search(
                    [('vehicle_id', 'in', vehicle.vehicle_ids.ids)])
            if vehicle.select_report == 'wo_month_sum_rep':
                wo_obj = self.env[
                    'report.fleet_operations.workorder.monthly.summary.xls']
                file = wo_obj.generate_xlsx_report(records)
                vehicle.write({
                    'name': 'WorkOrder Monthly Summary Report.xls',
                    'file': file
                })
            return {
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'work.order.reports',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'res_id': vehicle.id
            }
