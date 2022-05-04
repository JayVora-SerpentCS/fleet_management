# See LICENSE file for full copyright and licensing details.
"""Vehicle Change History Report."""

import time
from odoo.tools import format_date
from odoo import _, api, models
from odoo.exceptions import UserError


class VehicalChangeHistoryReport(models.AbstractModel):
    """Vehicle change history report."""

    _name = 'report.fleet_operations.vehicle_change_history_qweb'
    _description = 'Vehicle Change History Report'

    def get_vehicle_history(self, date_range):
        """Method to get vehicle history."""
        engine_obj = self.env['engine.history']
        color_obj = self.env['color.history']
        tire_obj = self.env['tire.history']
        battery_obj = self.env['battery.history']
        vin_obj = self.env['vin.history']
        domain = []
        if date_range.get('date_from'):
            domain += [('changed_date', '>=', date_range.get('date_from'))]
        if date_range.get('date_to'):
            domain += [('changed_date', '<=', date_range.get('date_to'))]
        if date_range.get('fleet_id'):
            domain += [('vehicle_id', '=', date_range.get('fleet_id'))]

        engine_ids = engine_obj.search(domain)
        color_ids = color_obj.search(domain)
        tire_ids = tire_obj.search(domain)
        battery_ids = battery_obj.search(domain)
        vin_ids = vin_obj.search(domain)
        vehicle_change_history = []
        changed_date = False
        work_order_date = False
        if engine_ids and date_range.get('report') == 'engine_history':
            for engine_rec in engine_ids:
                seq = engine_rec.vehicle_id and \
                    engine_rec.vehicle_id.name or ''
                if engine_rec.changed_date:
                    changed_date = format_date(
                        self.env, engine_rec.changed_date,
                        self._context.get('lang'), date_format=False
                    )
                if engine_rec.workorder_id and engine_rec.workorder_id.date_close:
                    work_order_date = format_date(
                        self.env, engine_rec.workorder_id.date_close,
                        self._context.get('lang'), date_format=False
                    )

                values = {
                    'description': seq,
                    'vehicle_type': engine_rec.vehicle_id and
                    engine_rec.vehicle_id.vechical_type_id and
                    engine_rec.vehicle_id.vechical_type_id.name or '',
                    'color_id': engine_rec.vehicle_id and
                    engine_rec.vehicle_id.vehical_color_id and
                    engine_rec.vehicle_id.vehical_color_id.name or '',
                    'vin': engine_rec.vehicle_id and
                    engine_rec.vehicle_id.vin_sn or '',
                    'plate': engine_rec.vehicle_id and
                    engine_rec.vehicle_id.license_plate or '',
                    'old_engine': engine_rec.previous_engine_no or '',
                    'new_engine': engine_rec.new_engine_no or '',
                    'old_color': '',
                    'new_color': '',
                    'old_vin': '',
                    'new_vin': '',
                    'change_date':changed_date if changed_date else False,
                    'work_order': engine_rec.workorder_id and
                    engine_rec.workorder_id.name or '',
                    'wo_close_date': work_order_date if work_order_date else False,
                    'remarks': engine_rec.note or '',
                    'seq': seq + 'a'}
                vehicle_change_history.append(values)
        if color_ids and date_range.get('report') == 'color_history':
            for color_rec in color_ids:
                seq = color_rec.vehicle_id and color_rec.vehicle_id.name or ''
                if color_rec.changed_date:
                    changed_date = format_date(
                        self.env, color_rec.changed_date,
                        self._context.get('lang'), date_format=False
                    )
                if color_rec.workorder_id and color_rec.workorder_id.date_close:
                    work_order_date = format_date(
                        self.env, color_rec.workorder_id.date_close,
                        self._context.get('lang'), date_format=False
                    )
                cvalues = {
                    'description': seq,
                    'vehicle_type': color_rec.vehicle_id and
                    color_rec.vehicle_id.vechical_type_id and
                    color_rec.vehicle_id.vechical_type_id.name or '',
                    'color_id': color_rec.vehicle_id and
                    color_rec.vehicle_id.vehical_color_id and
                    color_rec.vehicle_id.vehical_color_id.name or '',
                    'vin': color_rec.vehicle_id and
                    color_rec.vehicle_id.vin_sn or '',
                    # 'plate': engine_rec.vehicle_id and
                    # engine_rec.vehicle_id.license_plate or '',
                    'old_engine': '',
                    'new_engine': '',
                    'old_color': color_rec.previous_color_id and
                    color_rec.previous_color_id.name or '',
                    'new_color': color_rec.current_color_id and
                    color_rec.current_color_id.name or '',
                    'old_vin': '',
                    'new_vin': '',
                    'change_date': changed_date if changed_date else False,
                    'work_order': color_rec.workorder_id and
                    color_rec.workorder_id.name or '',
                    'wo_close_date': work_order_date if work_order_date else False,
                    'remarks': color_rec.note or '',
                    'seq': seq + 'b'}
                vehicle_change_history.append(cvalues)
        if tire_ids and date_range.get('report') == 'tire_history':
            for tire_rec in tire_ids:
                seq = tire_rec.vehicle_id and tire_rec.vehicle_id.name or ''
                if tire_rec.changed_date:
                    changed_date = format_date(
                        self.env, tire_rec.changed_date,
                        self._context.get('lang'), date_format=False
                    )
                if tire_rec.workorder_id and tire_rec.workorder_id.date_close:
                    work_order_date = format_date(
                        self.env, tire_rec.workorder_id.date_close,
                        self._context.get('lang'), date_format=False
                    )
                tvalues = {
                    'description': seq,
                    'vehicle_type': tire_rec.vehicle_id and
                    tire_rec.vehicle_id.vechical_type_id and
                    tire_rec.vehicle_id.vechical_type_id.name or '',
                    'color_id': tire_rec.vehicle_id and
                    tire_rec.vehicle_id.vehical_color_id and
                    tire_rec.vehicle_id.vehical_color_id.name or '',
                    'vin': tire_rec.vehicle_id and
                    tire_rec.vehicle_id.vin_sn or '',
                    'old_tire': tire_rec.previous_tire_size or '',
                    'new_tire': tire_rec.new_tire_size or '',
                    'old_vin': '',
                    'new_vin': '',
                    'change_date': changed_date if changed_date else False,
                    'work_order': tire_rec.workorder_id and
                    tire_rec.workorder_id.name or '',
                    'wo_close_date': work_order_date if work_order_date else False,
                    'remarks': tire_rec.note or '',
                    'seq': seq + 'b'}
                vehicle_change_history.append(tvalues)
        if battery_ids and date_range.get('report') == 'battery_history':
            for battery_rec in battery_ids:
                seq = battery_rec.vehicle_id and battery_rec.vehicle_id.name or ''
                if battery_rec.changed_date:
                    changed_date = format_date(
                        self.env, battery_rec.changed_date,
                        self._context.get('lang'), date_format=False
                    )
                if battery_rec.workorder_id and battery_rec.workorder_id.date_close:
                    work_order_date = format_date(
                        self.env, battery_rec.workorder_id.date_close,
                        self._context.get('lang'), date_format=False
                    )
                tvalues = {
                    'description': seq,
                    'vehicle_type': battery_rec.vehicle_id and
                    battery_rec.vehicle_id.vechical_type_id and
                    battery_rec.vehicle_id.vechical_type_id.name or '',
                    'color_id': battery_rec.vehicle_id and
                    battery_rec.vehicle_id.vehical_color_id and
                    battery_rec.vehicle_id.vehical_color_id.name or '',
                    'vin': battery_rec.vehicle_id and
                    battery_rec.vehicle_id.vin_sn or '',
                    'old_battery': battery_rec.previous_battery_size or '',
                    'new_battery': battery_rec.new_battery_size or '',
                    'old_vin': '',
                    'new_vin': '',
                    'change_date': changed_date if changed_date else False,
                    'work_order': battery_rec.workorder_id and
                    battery_rec.workorder_id.name or '',
                    'wo_close_date': work_order_date if work_order_date else False,
                    'remarks': battery_rec.note or '',
                    'seq': seq + 'b'}
                vehicle_change_history.append(tvalues)
        if vin_ids:
            for vin_rec in vin_ids:
                seq = vin_rec.vehicle_id and vin_rec.vehicle_id.name or ''
                if vin_rec.changed_date:
                    changed_date = format_date(
                        self.env, vin_rec.changed_date,
                        self._context.get('lang'), date_format=False
                    )
                if vin_rec.workorder_id and vin_rec.workorder_id.date_close:
                    work_order_date = format_date(
                        self.env, vin_rec.workorder_id.date_close,
                        self._context.get('lang'), date_format=False
                    )
                vvalues = {
                    'description': seq,
                    'vehicle_type': vin_rec.vehicle_id and
                    vin_rec.vehicle_id.vechical_type_id and
                    vin_rec.vehicle_id.vechical_type_id.name or '',
                    'color_id': vin_rec.vehicle_id and
                    vin_rec.vehicle_id.vehical_color_id and
                    vin_rec.vehicle_id.vehical_color_id.name or '',
                    'vin': vin_rec.vehicle_id and
                    vin_rec.vehicle_id.vin_sn or '',
                    'plate': engine_rec.vehicle_id and
                    engine_rec.vehicle_id.license_plate or '',
                    'old_engine': '',
                    'new_engine': '',
                    'old_color': '',
                    'new_color': '',
                    'old_vin': vin_rec.previous_vin_no or '',
                    'new_vin': vin_rec.new_vin_no or '',
                    'change_date': changed_date if changed_date else False,
                    'work_order': vin_rec.workorder_id and
                    vin_rec.workorder_id.name or '',
                    'wo_close_date': work_order_date if work_order_date else False,
                    'remarks': vin_rec.note or '',
                    'seq': seq + 'c'}
                vehicle_change_history.append(vvalues)
        if vehicle_change_history:
            vehicle_change_history = sorted(vehicle_change_history,
                                            key=lambda k: k['seq'])
        return vehicle_change_history

    @api.model
    def _get_report_values(self, docids, data=None):
        if not data.get('form') or \
                not self.env.context.get('active_model') or \
                not self.env.context.get('active_id'):
            raise UserError(_("Form content is missing, \
                    this report cannot be printed."))

        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        result = self.get_vehicle_history(data.get('form'))
        return {
            'doc_ids': self.ids,
            'doc_model': model,
            'data': data['form'],
            'docs': docs,
            'time': time,
            'get_vehicle_history': result}
