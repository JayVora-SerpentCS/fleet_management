# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo.osv import osv

try:
    from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
except ImportError:
    class ReportXlsx(object):
        def __init__(self, *args, **kwargs):
            pass


class WorkorderMontltReportXlsx(ReportXlsx):

    def get_heading(self):
        head_title = {
            'name': '',
            'rev_no': '',
            'doc_no': '',
            'image': ''
        }
        head_object = self.env['report.heading']
        head_ids = head_object.search([], order='id')
        if head_ids:
            head_rec = head_ids[0]
            if head_rec:
                head_title['name'] = head_rec.name or ''
                head_title['rev_no'] = head_rec.revision_no or ''
                head_title['doc_no'] = head_rec.document_no or ''
                head_title['image'] = head_rec.image or ''
        return head_title

    def get_wo_mthly_smry(self, workorder_browse):
        wo_summary_data = []
        wo_check_dict = {}
        no = 0
        if workorder_browse:
            for work_rec in workorder_browse:
                if work_rec.state and work_rec.state == 'done':
                    no += 1
                    parts_data = {}
                    identification = ''
                    repair_line_data = ''
                    if work_rec.vehicle_id:
                        identification += work_rec.vehicle_id.name
                        if work_rec.vehicle_id.f_brand_id:
                            identification += ' ' + \
                                work_rec.vehicle_id.f_brand_id.name
                        if work_rec.vehicle_id.model_id:
                            identification += ' ' + \
                                work_rec.vehicle_id.model_id.name
                    for repaire_line in work_rec.repair_line_ids:
                        if repaire_line.complete is True:
                            if repaire_line.repair_type_id and \
                                    repaire_line.repair_type_id.name:
                                repair_line_data += \
                                    repaire_line.repair_type_id.name + ', '
                    if work_rec.parts_ids:
                        for parts_line in work_rec.parts_ids:
                            parts_data = {}
                            if wo_check_dict. has_key(work_rec.id):
                                parts_data = {
                                    'no': -1,
                                    'location': '',
                                    'type': '',
                                    'wo': '',
                                    'identification': '',
                                    'vin': '',
                                    'plate_no': '',
                                    'work_performed': '',
                                    'part': parts_line.product_id and
                                    parts_line.product_id.default_code or '',
                                    'part_name': parts_line.name or '',
                                    'vehicle_make':
                                    parts_line.vehicle_make_id and
                                    parts_line.vehicle_make_id.name or '',
                                    'qty': parts_line.qty or 0.0,
                                    'uom': parts_line.product_uom and
                                    parts_line.product_uom.name or ''
                                }
                                wo_summary_data.append(parts_data)
                            else:
                                wo_check_dict[work_rec.id] = work_rec.id
                                parts_data = {
                                    'no': no,
                                    'location': work_rec.team_id and
                                    work_rec.team_id.name or '',
                                    'type': work_rec.main_type or '',
                                    'wo': work_rec.name or '',
                                    'identification': identification or '',
                                    'vin': work_rec.vehicle_id and
                                    work_rec.vehicle_id.vin_sn or '',
                                    'plate_no': work_rec.vehicle_id and
                                    work_rec.vehicle_id.license_plate or '',
                                    'work_performed': repair_line_data and
                                    repair_line_data[:-2] or '',
                                    'part': parts_line.product_id and
                                    parts_line.product_id.default_code or '',
                                    'part_name': parts_line.name or '',
                                    'vehicle_make':
                                    parts_line.vehicle_make_id and
                                    parts_line.vehicle_make_id.name or '',
                                    'qty': parts_line.qty or 0.0,
                                    'uom': parts_line.product_uom and
                                    parts_line.product_uom.name or ''
                                }
                                wo_summary_data.append(parts_data)
                    else:
                        parts_data = {}
                        parts_data = {
                            'no': no,
                            'location': work_rec.team_id and
                            work_rec.team_id.name or '',
                            'type': work_rec.main_type or '',
                            'wo': work_rec.name or '',
                            'identification': identification or '',
                            'vin': work_rec.vehicle_id and
                            work_rec.vehicle_id.vin_sn or '',
                            'plate_no': work_rec.vehicle_id and
                            work_rec.vehicle_id.license_plate or '',
                            'work_performed': repair_line_data and
                            repair_line_data[:-2] or '',
                            'part': '',
                            'part_name': '',
                            'vehicle_make': '',
                            'qty': '',
                            'uom': ''
                        }
                        wo_summary_data.append(parts_data)
        if not wo_summary_data:
            raise osv.except_osv(
                ('Warning!'), ("No data Available for selected work order."))
        return wo_summary_data

    def generate_xlsx_report(self, workbook, data, workorder):

        worksheet = workbook.add_worksheet('invoice')
        worksheet.set_column(0, 0, 10)
        worksheet.set_column(1, 1, 15)
        worksheet.set_column(2, 2, 10)
        worksheet.set_column(3, 3, 10)
        worksheet.set_column(4, 4, 50)
        worksheet.set_column(5, 5, 15)
        worksheet.set_column(6, 6, 15)
        worksheet.set_column(7, 7, 50)
        worksheet.set_column(8, 8, 10)
        worksheet.set_column(9, 9, 10)
        worksheet.set_column(10, 10, 10)
        worksheet.set_column(11, 11, 15)
        worksheet.set_column(12, 12, 15)
        worksheet.set_column(13, 13, 15)
        worksheet.set_column(14, 14, 15)
        worksheet.set_column(15, 15, 15)

        # tot = workbook.add_format({'border': 2,
        #                            'bold': True,
        #                            'font_name': 'Arial',
        #                            'font_size': '10'})
        border = workbook.add_format({'border': 2,
                                      'font_name': 'Arial',
                                      'font_size': '10'})
        format1 = workbook.add_format({'border': 2,
                                       'bold': True,
                                       'font_name': 'Arial',
                                       'font_size': '10'})
        format1.set_bg_color('gray')
        merge_format = workbook.add_format({'border': 2, 'align': 'center'})
#        worksheet.merge_range('C2:D2', 'Merged Cells', merge_format)
        worksheet.merge_range('C3:E3', 'Merged Cells', merge_format)
#        res = self.get_heading()

#        file_name = res.get('image', False)
#        if file_name:
#            file1 = open('/tmp/' + 'logo.png', 'wb')
#            file_data = base64.decodestring(file_name)
#            file1.write(file_data)
#            file1.close()
        row = 0
        row += 1
#        if file_name:
#            worksheet.insert_image(row, 0, '/tmp/logo.png')
#        worksheet.write(row, 2, res['name'] or '', border)
#        worksheet.write(row, 4, 'Rev. No. :', tot)
#        worksheet.write(row, 5, res['rev_no'] or '', border)
#        worksheet.write(row, 6, 'Document No. :', tot)
#        worksheet.write(row, 7, res['doc_no'] or '', border)
        row += 1
        worksheet.write(row, 2,
                        'Work Order Monthly Summary Report', merge_format)
        row += 3

        worksheet.write(row, 0, 'Item No.', format1)
        worksheet.write(row, 1, 'Location', format1)
        worksheet.write(row, 2, 'Type', format1)
        worksheet.write(row, 3, 'Wo #', format1)
        worksheet.write(row, 4, 'Identification', format1)
        worksheet.write(row, 5, 'VIN', format1)
        worksheet.write(row, 6, 'Plate No.', format1)
        worksheet.write(row, 7, 'Work Performed', format1)
        row += 1
        counter = 1
        for line in self.get_wo_mthly_smry(workorder):
            if line.get('no') > 0:
                worksheet.write(row, 0, line.get('no'), border)
                worksheet.write(row, 1, line.get('location'), border)
                worksheet.write(row, 2, line.get('type'), border)
                worksheet.write(row, 3, line.get('wo'), border)
                worksheet.write(row, 4, line.get('identification'), border)
                worksheet.write(row, 5, line.get('vin'), border)
                worksheet.write(row, 6, line.get('plate_no'), border)
                worksheet.write(row, 7, line.get('work_performed'), border)
            if line.get('no') < 0:
                worksheet.write(row, 0, line.get('no'), border)
                worksheet.write(row, 1, line.get('location'), border)
                worksheet.write(row, 2, line.get('type'), border)
                worksheet.write(row, 3, line.get('wo'), border)
                worksheet.write(row, 4, line.get('identification'), border)
                worksheet.write(row, 5, line.get('vin'), border)
                worksheet.write(row, 6, line.get('plate_no'), border)
                worksheet.write(row, 7, line.get('work_performed'), border)
            row += 1
            counter += 1


WorkorderMontltReportXlsx('report.workorder.monthly.summary.xls',
                          'fleet.vehicle.log.services')
