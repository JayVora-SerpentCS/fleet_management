"""Fleet History Report."""

import base64
import io
from odoo.tools import format_date
from odoo import _, api, fields, models

import xlwt


class FleetHistorySummary(models.TransientModel):
    """Fleet History Summary."""

    _name = "excel.fleet.report"
    _description = "Fleet Excel Report"

    file = fields.Binary("Click On Download Link To Download Xls File",
                         readonly=True)
    name = fields.Char("Name", default='generic summary.xls')


class PrintFleetHistory(models.TransientModel):
    """Print Fleet History."""

    _name = "print.fleet.history"
    _description = "Print fleet History"

    sel_report = fields.Selection([
        ('history', 'Fleet History'),
        ('listing', 'Fleet Listing'),
        ('pending_repairs', 'Fleet Pending Repairs'),
        ('pending_repair_summary', 'Fleet Pending Repair Summary'),
        ('complete_stage', 'Fleet Complete Stage'),
        ('nex_ser_odometer', 'Next Service by Odometer'),
        ('nex_ser_date', 'Next Service by Date')],
        string="Select Report")

    def print_xlsx_report(self):
        for rep in self:
            res = False
            ret_dict = {'view_type': 'form',
                        "view_mode": 'form',
                        'res_model': 'excel.fleet.report',
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                        }
            docids = self.env.context.get('active_ids')
            obj = self.env[self.env.context.get(
                'active_model')].browse(docids) or False
            if rep.sel_report == 'history':
                res = self.print_fleet_history_xlsx_report(res, obj)
                vals = {'name': 'Fleet History.xls', 'file': res}
                module_rec = self.env['excel.fleet.report'].create(vals)
                ret_dict.update({'name': _('Fleet History Report'),
                                 'res_id': module_rec.id})
            elif rep.sel_report == 'listing':
                listing_obj = \
                    self.env['report.fleet_operations.fleet.summary.xls']
                res = listing_obj.generate_listing_xlsx_report(res, obj)
                vals = {'name': 'Fleet Listing.xls', 'file': res}
                module_rec = self.env['excel.fleet.report'].create(vals)
                ret_dict.update({'name': _('Fleet Listing Report'),
                                 'res_id': module_rec.id})
            elif rep.sel_report == 'pending_repairs':
                pending_repair_obj =\
                    self.env['report.fleet_operations.fleet.pending.repairs.xls']
                res = pending_repair_obj.generate_pending_repairs_xlsx_report(
                    res, obj)
                vals = {'name': 'Fleet Pending Repairs.xls', 'file': res}
                module_rec = self.env['excel.fleet.report'].create(vals)
                ret_dict.update({'name': _('Fleet Pending Repairs Report'),
                                 'res_id': module_rec.id})
            elif rep.sel_report == 'pending_repair_summary':
                pending_repair_summary_obj =\
                    self.env['report.fleet_operations.fleet.pending.xls']
                res =\
                    pending_repair_summary_obj.generate_pending_summary_xlsx_report(
                        res, obj)
                vals =\
                    {'name': 'Fleet Pending Repair Summary.xls', 'file': res}
                module_rec = self.env['excel.fleet.report'].create(vals)
                ret_dict.update({'name': _('Fleet Pending Repair Summary Report'),
                                 'res_id': module_rec.id})
            elif rep.sel_report == 'complete_stage':
                complete_stage_obj =\
                    self.env['report.fleet_operations.fleet.wait.collection.xls']
                res = complete_stage_obj.generate_complete_stage_xlsx_report(
                    res, obj)
                vals = {'name': 'Fleet Complete Stage.xls', 'file': res}
                module_rec = self.env['excel.fleet.report'].create(vals)
                ret_dict.update({'name': _('Fleet Complete Stage Report'),
                                 'res_id': module_rec.id})
            elif rep.sel_report == 'nex_ser_odometer':
                ser_odometer_obj =\
                    self.env['report.fleet_operations.next.services.by.odometer.xls']
                res = ser_odometer_obj.generate_service_odometer_xlsx_report(
                    res, obj)
                vals =\
                    {'name': 'Next Service Odometer Repairs.xls', 'file': res}
                module_rec = self.env['excel.fleet.report'].create(vals)
                ret_dict.update({'name': _('Next Service Odometer Repairs Report'),
                                 'res_id': module_rec.id})
            elif rep.sel_report == 'nex_ser_date':
                ser_date_obj =\
                    self.env['report.fleet_operations.next.services.by.date.xls']
                res = ser_date_obj.generate_service_date_xlsx_report(res, obj)
                vals = {'name': 'Next Service Date.xls', 'file': res}
                module_rec = self.env['excel.fleet.report'].create(vals)
                ret_dict.update({'name': _('Next Service Date Report'),
                                 'res_id': module_rec.id})
            return ret_dict

    def print_fleet_history_xlsx_report(self, res=False, fleet_history=False):
        workbook = xlwt.Workbook()
        worksheet = workbook.add_sheet('fleet_history')
        worksheet.col(0).width = 7000
        worksheet.col(1).width = 7000
        worksheet.col(2).width = 7000
        worksheet.col(3).width = 7000
        worksheet.col(4).width = 7000
        worksheet.col(5).width = 7000
        worksheet.col(6).width = 7000
        worksheet.col(7).width = 7000

        font = xlwt.Font()
        font.bold = True
        font.name = 'Arial'
        font.height = 200
        style1 = xlwt.easyxf('font: bold 1; font: name 1; font: height 200')
        # pattern = xlwt.Pattern()
        # tot = xlwt.easyxf('font: bold 1; font: name 1; font: height 200')
        border = xlwt.easyxf('font: bold 1; font: name 1; font: height 200')
        format1 = xlwt.easyxf('font: bold 1; font: name 1; font: height 200;\
            pattern: pattern solid, fore_colour yellow;')

        row = 0
        row += 1
        worksheet.write(row, 1, 'Fleet History Report', format1)
        row = 2
        for obj in fleet_history:
            row += 3
            worksheet.write(row, 0, 'Identification :', format1)
            worksheet.write(row, 1, obj.name or '', border)
            worksheet.write(row, 2, 'Driver Name :', format1)
            worksheet.write(row, 3, obj.driver_id and
                            obj.driver_id.name or '', border)
            row += 1
            worksheet.write(row, 0, 'Vehicle Type :', format1)
            worksheet.write(row, 1, obj.vechical_type_id and
                            obj.vechical_type_id.name or '', border)
            worksheet.write(row, 2, 'Driver Contact No :', format1)
            worksheet.write(row, 3, obj.driver_contact_no or '', border)
            row += 1
            worksheet.write(row, 0, 'VIN No :', format1)
            worksheet.write(row, 1, obj.vin_sn or '', border)
            worksheet.write(row, 2, 'Engine No :', format1)
            worksheet.write(row, 3, obj.engine_no or '', border)
            row += 1
            worksheet.write(row, 0, 'Vehicle Color :', format1)
            worksheet.write(row, 1, obj.vehical_color_id and
                            obj.vehical_color_id.name or '', border)
            worksheet.write(row, 2, 'Last Meter :', format1)
            worksheet.write(row, 3, obj.odometer or '', border)
            row += 1
            worksheet.write(row, 0, 'Plate No :', format1)
            worksheet.write(row, 1, obj.license_plate or '', border)
            # worksheet.write(row, 2, 'Registration State :', format1)
            # worksheet.write(row, 3, obj.vechical_location_id and
            #                 obj.vechical_location_id.name or '', border)
            row += 2
            for order in obj.work_order_ids:
                row += 1
                worksheet.write(row, 0, 'WO No :', format1)
                worksheet.write(row, 1, order.name or '', border)
                worksheet.write(row, 2, 'Kilometer :', format1)
                worksheet.write(row, 3, order.odometer or '', border)
                row += 1
                date=''
                if order.date:
                    date = format_date(self.env, order.date, self._context.get('lang'), date_format=False)
                worksheet.write(row, 0, 'Actual Date Issued :', format1)
                worksheet.write(row, 1, date or '', style1)
                # worksheet.write(row, 2, 'Location :', format1)
                # worksheet.write(row, 3, order.vechical_location_id and
                #                 order.vechical_location_id.name or '', border)
                worksheet.write(row, 2, 'Notes :', format1)
                worksheet.write(row, 3, order.note or '', border)
                row += 2
                worksheet.write(row, 1, 'REPAIRS PERFORMED', format1)
                row += 2
                worksheet.write(row, 0, 'No', format1)
                worksheet.write(row, 1, 'Repair Type', format1)
                worksheet.write(row, 2, 'Category', format1)
                line_row = row + 1
                line_col = 0
                counter = 1
                for repair_line in order.repair_line_ids:
                    if repair_line.complete is True:
                        worksheet.write(line_row, line_col, counter, border)
                        line_col += 1
                        worksheet.write(line_row, line_col,
                                        repair_line.repair_type_id and
                                        repair_line.repair_type_id.name or '',
                                        border)
                        line_col += 1
                        worksheet.write(line_row, line_col,
                                        repair_line.categ_id and
                                        repair_line.categ_id.name or '',
                                        border)
                        line_col = 0
                        line_row += 1
                        counter += 1
                row += 3
                worksheet.write(row, 0, '**************************')
                worksheet.write(row, 1, '**************************')
                worksheet.write(row, 2, '**************************')
                row += 1
                worksheet.write(row, 0, '**************************')
                worksheet.write(row, 1, '**************************')
                worksheet.write(row, 2, '**************************')
        fp = io.BytesIO()
        workbook.save(fp)
        fp.seek(0)
        data = fp.read()
        fp.close()
        res = base64.encodebytes(data)
        return res
