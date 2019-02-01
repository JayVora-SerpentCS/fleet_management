# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from openerp import models, api


class ReportQwebWriteOff(models.AbstractModel):

    _name = 'report.fleet_operations.write_off_qweb'

    def _get_heading(self):

        head_title = {
            'name': '',
            'rev_no': '',
            'doc_no': '',
            'image': '',
        }
        head_object = self.env['report.heading']
        head_ids = head_object.search([], order='id')
        if head_ids:
            head_id = head_ids[0]
            if head_id:
                head_title['name'] = head_id.name or ''
                head_title['rev_no'] = head_id.revision_no or ''
                head_title['doc_no'] = head_id.document_no or ''
                head_title['image'] = head_id.image or ''
        return head_title

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
    def render_html(self, docids, data=None):
        report_obj = self.env['report']
        witten_report = \
            report_obj._get_report_from_name('fleet_operations.write_off_qweb')
        if data is None:
            data = {}
        if not docids:
            docids = data.get('docids')
        fleet_obj = self.env['fleet.wittenoff'].browse(docids)
        docargs = {
            'doc_ids': docids,
            'doc_model': witten_report.model,
            'docs': fleet_obj,
            'get_last_work_order': self._get_last_work_order,
        }
        return report_obj.render('fleet_operations.write_off_qweb', docargs)
