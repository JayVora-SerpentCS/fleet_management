# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

try:
    from odoo.addons.report_xlsx.report.report_xlsx import ReportXlsx
except ImportError:
    class ReportXlsx(object):

        def __init__(self, *args, **kwargs):
            pass


class FleetWorkOrder(ReportXlsx):

    def get_heading(self):
        head_title = {'name': '',
                      'rev_no': '',
                      'doc_no': '',
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

    def get_wo_status(self, status):
        wo_status = "New"
        if status == 'done':
            wo_status = "Closed"
        elif status == 'confirm':
            wo_status = "Open"
        return wo_status

    def get_wo_smry(self, workorder_browse):
        wo_summary_data = []
        wo_smry_dict = {}
        if workorder_browse:
            for work_rec in workorder_browse:
                if work_rec.state and work_rec.state == 'done':
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

                    if wo_smry_dict.get(work_rec.team_id.id, False):
                        wo_data = {
                            'name': work_rec.name or '',
                            'identification': identification or '',
                            'vin': work_rec.vehicle_id and
                            work_rec.vehicle_id.vin_sn or '',
                            'date_open': work_rec.date_open or '',
                            'state': self.get_wo_status(work_rec.state),
                            'etic': work_rec.etic and
                            work_rec.date_complete or '',
                            'date_close': work_rec.date_close or '',
                            'work_performed': repair_line_data and
                            repair_line_data[:-2] or '',
                        }
                        wo_smry_dict[work_rec.team_id.id]['value'] += [wo_data]
                    else:
                        wo_data = \
                            {
                                'name': work_rec.name or '',
                                'identification': identification or '',
                                'vin': work_rec.vehicle_id and
                                work_rec.vehicle_id.vin_sn or '',
                                'date_open': work_rec.date_open or '',
                                'state': self.get_wo_status(work_rec.state),
                                'etic': work_rec.etic and
                                work_rec.date_complete or '',
                                'date_close': work_rec.date_close or '',
                                'work_performed': repair_line_data and
                                repair_line_data[:-2] or '',
                            }

                        wo_smry_dict[work_rec.team_id.id] = {
                            'team_id': work_rec.team_id and
                            work_rec.team_id.name or '',
                            'value': [wo_data]
                        }
        for team_id, workorder_data in wo_smry_dict.items():
            wo_summary_data.append(workorder_data)
        return wo_summary_data

    def generate_xlsx_report(self, workbook, data, product):
        worksheet = workbook.add_worksheet('workorder_summary')
        worksheet.set_column(0, 0, 10)
        worksheet.set_column(1, 1, 15)
        worksheet.set_column(2, 2, 50)
        worksheet.set_column(3, 3, 15)
        worksheet.set_column(4, 4, 15)
        worksheet.set_column(5, 5, 12)
        worksheet.set_column(6, 6, 8)
        worksheet.set_column(7, 7, 12)
        worksheet.set_column(8, 8, 20)
        worksheet.set_column(9, 9, 50)
        worksheet.set_column(10, 10, 15)

#        result = self.get_heading()
        tot = workbook.add_format({'border': 2,
                                   'font_name': 'Arial',
                                   'font_size': '12'})
        border = workbook.add_format({'border': 2,
                                      'font_name': 'Arial',
                                      'font_size': '10'})
        format1 = workbook.add_format({'border': 2,
                                       'bold': True,
                                       'font_name': 'Arial',
                                       'font_size': '10'})
        format1.set_bg_color('gray')
#        worksheet.merge_range('C2:E2', 'Merged Cells', merge_format)

#        file_name = result.get('image', False)
#        if file_name:
#            file1 = open('/tmp/' + 'logo.png', 'wb')
#            file_data = base64.decodestring(file_name)
#            file1.write(file_data)
#            file1.close()
        row = 0
        row += 1
#        if file_name:
#            worksheet.insert_image(row, 0, '/tmp/logo.png')
#        worksheet.write(row, 2, result.get('name') or '', border)
#        worksheet.write(row, 5, 'Rev. No. :', tot)
#        worksheet.write(row, 6, result.get('rev_no') or '', border)
#        worksheet.write(row, 7, 'Document No. :', tot)
#        worksheet.write(row, 8, result.get('doc_no') or '', border)
        row += 1
        worksheet.write(row, 2, 'Work Order Summary', tot)
        row += 4
        worksheet.write(row, 0, 'NO.', format1)
        worksheet.write(row, 1, 'WO No.', format1)
        worksheet.write(row, 2, 'Identification', format1)
        worksheet.write(row, 3, 'VIN', format1)
        worksheet.write(row, 4, 'Actual Date Issued', format1)
        worksheet.write(row, 5, 'Status', format1)
        worksheet.write(row, 6, 'ETIC', format1)
        worksheet.write(row, 7, 'WO Date Closed', format1)
        worksheet.write(row, 8, 'Workshop', format1)
        worksheet.write(row, 9, 'Work Performed', format1)
        line_row = row + 1
        line_col = 0
        counter = 1
        for obj in self.get_wo_smry(product):
            for line in obj.get('value'):
                worksheet.write(line_row, line_col, counter, border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.get('name') or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.get('identification') or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.get('vin') or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.get('date_open') or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.get('state') or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.get('etic') or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.get('date_close') or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                obj.get('team_id')or '', border)
                line_col += 1
                worksheet.write(line_row, line_col,
                                line.get('work_performed') or '', border)
                line_col = 0
                line_row += 1
                counter += 1
            worksheet.write(line_row, line_col, '********', border)


FleetWorkOrder('report.workorder.summary.xls', 'fleet.vehicle.log.services')
