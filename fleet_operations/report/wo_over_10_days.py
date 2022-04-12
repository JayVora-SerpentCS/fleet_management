# See LICENSE file for full copyright and licensing details.
"""Wo Over 10 Days."""

import base64
import io
from datetime import datetime

from odoo import models
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


import xlwt


class WoOver10DaysXlsx(models.AbstractModel):
    """Wo over 10 days xlsx."""

    _name = 'report.fleet_operations.wo.over.daysxls'
    _description = 'Work Order Over 10 Days Report'

    def get_wo_over_10days(self, work_orders):
        """Method to get wo over 10days."""
        over_orders = []
        for wk_order in work_orders:
            if wk_order.state == 'done':
                diff = (datetime.strptime(str(wk_order.date_close),
                                          DEFAULT_SERVER_DATE_FORMAT) -
                        datetime.strptime(str(wk_order.date_open),
                                          DEFAULT_SERVER_DATE_FORMAT)).days
                if diff > 10:
                    over_orders.append(wk_order)
            elif wk_order.state == 'confirm':
                diff = (datetime.today() - datetime.strptime(
                    str(wk_order.date_open), DEFAULT_SERVER_DATE_FORMAT)).days
                if diff > 10:
                    over_orders.append(wk_order)
        return over_orders

    def get_identification(self, vehicles_id):
        """Get Identification."""
        ident = ""
        if vehicles_id:
            if vehicles_id.name:
                ident += vehicles_id.name or ''
            if vehicles_id.f_brand_id:
                ident += ' ' + vehicles_id.f_brand_id.name or ''
            if vehicles_id.model_id:
                ident += ' ' + vehicles_id.model_id.name or ''
        return ident

    def get_wo_status(self, status):
        """Get Wo Status."""
        if status == 'done':
            wo_status = "Closed"
        elif status == 'confirm':
            wo_status = "Open"
        else:
            wo_status = "New"
        return wo_status

    def get_over_wo_repair_perform(self, work_order, state):
        """Get Over Wo Repair Perform."""
        repair_perform = ""
        status = state
        if status == "done":
            repair_perform = self.get_workperform(work_order)
        elif status == "confirm":
            repair_perform = self.get_all_selected_repair(work_order)
        return repair_perform

    def get_workperform(self, workorder_id):
        """Get Workperform."""
        repair_type = ""
        if workorder_id:
            for repair_line in workorder_id.repair_line_ids:
                if repair_line.complete:
                    repair_type += repair_line.repair_type_id.name + ","
        return repair_type[:-1]

    def get_all_selected_repair(self, workorder_id):
        """Get All Selected Repair."""
        repair_type = ""
        if workorder_id:
            for repair_line in workorder_id.repair_line_ids:
                repair_type += repair_line.repair_type_id.name + ","
        return repair_type[:-1]

    def generate_xlsx_report(self, services):
        """Generate xlsx report."""
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('wo_over_10days')
        worksheet.col(0).width = 5000
        worksheet.col(1).width = 7500
        worksheet.col(2).width = 25000
        worksheet.col(3).width = 5000
        worksheet.col(4).width = 5000
        worksheet.col(5).width = 22000
        worksheet.col(6).width = 7500
        worksheet.col(7).width = 7500

        font = xlwt.Font()
        font.bold = True
        font.name = 'Arial'
        font.height = 200
        # pattern = xlwt.Pattern()
        # tot = xlwt.easyxf('font: bold 1; font: name 1; font: height 200')
        border = xlwt.easyxf('font: bold 1; font: name 1; font: height 200')
        format1 = xlwt.easyxf('font: bold 1; font: name 1; font: height 200; \
            pattern: pattern solid')

        row = 0
        row += 1
        row += 1
        worksheet.write(row, 2, 'Work Order Over 10 Days', border)
        row += 3
        res1 = self.get_wo_over_10days(services)

        worksheet.write(row, 0, 'No.', format1)
        worksheet.write(row, 1, 'WO No:', format1)
        worksheet.write(row, 2, 'Identification.', format1)
        worksheet.write(row, 3, 'Status', format1)
        worksheet.write(row, 4, 'Meter', format1)
        worksheet.write(row, 5, 'Work Performed', format1)
        worksheet.write(row, 6, 'ETIC', format1)
        row += 1
        counter = 1
        for line in res1:
            worksheet.write(row, 0, counter)
            worksheet.write(row, 1, line.name or '')
            worksheet.write(row, 2, self.get_identification(line.vehicle_id))
            worksheet.write(row, 3, line.state)
            worksheet.write(row, 3, self.get_wo_status(line.state))
            worksheet.write(row, 4, line.odometer or 0)
            worksheet.write(row, 5,
                            self.get_over_wo_repair_perform(line, line.state))
            worksheet.write(row, 6,
                            line.etic and line.date_complete or '')
            row += 1
            counter += 1
        row += 5
        fp = io.BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        res = base64.encodestring(data)
        return res
