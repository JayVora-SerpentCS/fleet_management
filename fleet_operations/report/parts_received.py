# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models


class ReceivedPartsXlsx(models.AbstractModel):
    _name = 'report.fleet_operations.receved.parts.xls'
    _inherit = 'report.report_xlsx.abstract'


    def get_purchase_id(self, picking):
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

    def generate_xlsx_report(self, workbook, data, stock_picking_ids):
        # add the worksheet
        worksheet = workbook.add_worksheet('invoice')
        worksheet.set_column(0, 0, 10)
        worksheet.set_column(1, 1, 15)
        worksheet.set_column(2, 2, 10)
        worksheet.set_column(3, 3, 10)
        worksheet.set_column(4, 4, 9)
        worksheet.set_column(5, 5, 12)
        worksheet.set_column(6, 6, 10)
        worksheet.set_column(7, 7, 15)
        worksheet.set_column(8, 8, 10)
        worksheet.set_column(9, 9, 9)
        worksheet.set_column(10, 10, 9)
        worksheet.set_column(11, 11, 18)
        worksheet.set_column(12, 12, 15)
        worksheet.set_column(13, 13, 12)
        worksheet.set_column(14, 14, 12)
        worksheet.set_column(15, 15, 12)
        bold = workbook.add_format({'bold': True,
                                    'font_name': 'Arial',
                                    'font_size': '10'})
        tot = workbook.add_format({'border': 2,
                                   'bold': True,
                                   'font_name': 'Arial',
                                   'font_size': '10'})
        tot.set_bg_color('gray')
        row = 0
        for picking in stock_picking_ids:
            row += 1
            row += 1
            worksheet.write(row, 3, 'Parts Received ', bold)
            row += 3
            worksheet.write(row, 0, 'No.', tot)
            worksheet.write(row, 1, 'PO No:', tot)
            worksheet.write(row, 2, 'Part No.', tot)
            worksheet.write(row, 3, 'Part Name', tot)
            worksheet.write(row, 4, 'Vehicle Type', tot)
            worksheet.write(row, 5, 'Vendor', tot)
            worksheet.write(row, 6, 'Qty Received', tot)
            worksheet.write(row, 7, 'Unit Cost', tot)
            worksheet.write(row, 8, 'Total Cost', tot)
            worksheet.write(row, 9, 'Received By', tot)
            worksheet.write(row, 10, 'Received For', tot)
            worksheet.write(row, 11, 'Location', tot)
            row += 2
            purchase_id = self.get_purchase_id(picking)
            counter = 1
            worksheet.write(row, 0, 'DATE RECEIVED:', bold)
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
        