# See LICENSE file for full copyright and licensing details.
"""Written Off Parser."""

from odoo import api, models


class ReportQwebWriteOff (models. AbstractModel):
    """Report Qweb Write Off."""

    _name = 'report.fleet_operations.write_off_qweb'
    _description = 'Write Off Vehicle Report'

    def _get_last_work_order(self, vehicle_id):
        work_order_obj = self.env['fleet.vehicle.log.services']
        work_order_ids = \
            work_order_obj.search([('vehicle_id', '=', vehicle_id),
                                   ('state', '=', 'done')], order='id')
        work_order_name = ''
        if work_order_ids:
            work_order_id = work_order_ids[-1]
            if work_order_id:
                work_order_name = work_order_id.name or ''
        return work_order_name

    @api.model
    def _get_report_values(self, docids, data=None):
        if data is None:
            data = {}
        if not docids:
            docids = data.get('docids', [])
        docs = self.env['fleet.wittenoff'].browse(docids)
        return{
            'doc_ids': docids,
            'doc_model': 'fleet.wittenoff',
            'docs': docs,
            'get_last_work_order': self._get_last_work_order}
