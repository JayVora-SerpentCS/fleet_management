# See LICENSE file for full copyright and licensing details.
"""Parts Received Report."""


import base64
import io

from odoo import _, api, fields, models

import xlwt


class StockPickingReport(models.TransientModel):
    """Stock Picking Report."""

    _name = 'stock.picking.xls.report'
    _description = 'Stock Picking XLSX reports'

    name = fields.Char("Name", default='Genric Report.xls')
    file = fields.Binary("Click On Download Link To Download Xls File",
                         readonly=True)

    def print_recived_part_xlsx_report(self):
        """Print recived part xlsx."""
        rec_parts_obj = self.env['report.fleet_operations.receved.parts.xls']
        for part in self:
            part.write({'name': False,
                        'file': False})
            res = False
            docids = self.env.context.get('active_ids')
            obj = self.env[self.env.context.get(
                'active_model')].browse(docids) or False
            res = rec_parts_obj.generate_xlsx_report(res, obj)
            # module_rec = part.write({'name': 'Recived Parts.xls',
            #                         'file': res})
            return {'view_type': 'form',
                    "view_mode": 'form',
                    'res_model': 'stock.picking.xls.report',
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                    'name': _('Recived Parts'),
                    'res_id': part.id}


class ReceivedPartsXlsx(models.AbstractModel):
    """Print recived part xlsx."""

    _name = 'report.fleet_operations.receved.parts.xls'
    _description = 'Recived Parts Reports'

    def get_purchase_id(self, picking):
        """Method to get purchase."""
        query = """
            SELECT po.id as purchase_id FROM stock_picking p, stock_move m,\
                     purchase_order_line pol, purchase_order po
            WHERE p.id= %s and po.id = pol.order_id and \
                    pol.id = m.purchase_line_id and m.picking_id = p.id
            GROUP BY picking_id, po.id
        """
        self.env.cr.execute(query, (tuple([picking.ids[0]]), ))
        purchase_ids = self.env.cr.fetchall()
        if purchase_ids and purchase_ids[0] is not None:
            return self.env['purchase.order'].browse(purchase_ids[0])
        return False

    def generate_xlsx_report(self, res, stock_picking_ids):
        """Generate recived part xlsx report."""
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('invoice')
        worksheet.col(0).width = 5000
        worksheet.col(1).width = 7500
        worksheet.col(2).width = 5000
        worksheet.col(3).width = 5000
        worksheet.col(4).width = 4500
        worksheet.col(5).width = 6000
        worksheet.col(6).width = 5000
        worksheet.col(7).width = 7500
        worksheet.col(8).width = 5000
        worksheet.col(9).width = 5000
        worksheet.col(10).width = 4500
        worksheet.col(11).width = 9000
        worksheet.col(12).width = 7500
        worksheet.col(13).width = 6000
        worksheet.col(14).width = 6000
        worksheet.col(15).width = 6000
        font = xlwt.Font()
        font.bold = True
        font.name = 'Arial'
        font.height = 200
        # pattern = xlwt.Pattern()
        tot = xlwt.easyxf('font: bold 1; font: name 1; font: height 200')
        # border = xlwt.easyxf('font: bold 1; font: name 1; font: height 200')
        format1 = xlwt.easyxf(
            'font: bold 1; font: name 1; font: height 200;\
            pattern: pattern solid')
        row = 0
        for picking in stock_picking_ids:
            row += 1
            row += 1
            worksheet.write(row, 3, 'Parts Received ', tot)
            row += 3
            worksheet.write(row, 0, 'No.', format1)
            worksheet.write(row, 1, 'PO No:', format1)
            worksheet.write(row, 2, 'Part No.', format1)
            worksheet.write(row, 3, 'Part Name', format1)
            worksheet.write(row, 4, 'Vehicle Type', format1)
            worksheet.write(row, 5, 'Vendor', format1)
            worksheet.write(row, 6, 'Qty Received', format1)
            worksheet.write(row, 7, 'Unit Cost', format1)
            worksheet.write(row, 8, 'Total Cost', format1)
            worksheet.write(row, 9, 'Received By', format1)
            worksheet.write(row, 10, 'Received For', format1)
            worksheet.write(row, 11, 'Location', format1)
            row += 2
            purchase_id = self.get_purchase_id(picking)
            counter = 1
            worksheet.write(row, 0, 'DATE RECEIVED:', tot)
            worksheet.write(row, 2, picking.date_done)
            row += 1
            for line in picking.move_lines:
                if picking.state == 'done' and purchase_id:
                    pur_id = purchase_id.id
                    worksheet.write(row, 0, counter)
                    worksheet.write(row, 1, pur_id or pur_id and
                                    pur_id.name or '')
                    worksheet.write(row, 2, pur_id)
                    worksheet.write(row, 3, picking.product_id and
                                    picking.product_id.name or "")
                    worksheet.write(
                        row, 4, picking.product_id and
                        picking.product_id.vehicle_make_id and
                        picking.product_id.vehicle_make_id.name or "")
                    worksheet.write(row, 5, picking.partner_id and
                                    picking.partner_id.name or "")
                    worksheet.write(row, 6, line.product_qty or 0.0)
                    worksheet.write(row, 7, line.price_unit or 0.0)
                    worksheet.write(row, 8,
                                    (line.price_unit * line.product_qty))
                    worksheet.write(row, 9, picking.received_by_id and
                                    picking.received_by_id.name or '')
                    worksheet.write(row, 10, pur_id and
                                    'Stock' or 'Scrap')
                    worksheet.write(row, 11,
                                    picking.product_id.location_ids.name)
                    row += 2
                    counter += 1
        row += 5
        fp = io.BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        res = base64.encodestring(data)
        return res
