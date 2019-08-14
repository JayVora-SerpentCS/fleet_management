# See LICENSE file for full copyright and licensing details.
"""Pending Repair Confrim."""

from datetime import date, timedelta

from odoo import _, api, models
from odoo.exceptions import Warning
# from odoo.tools import DEFAULT_SERVER_DATE_FORMAT


class PendingRepairConfirm(models.TransientModel):
    """Pending Repair Confirm."""

    _name = 'pending.repair.confirm'
    _description = 'Pending Repair Confirm'

    @api.multi
    def confirm_wo_forcefully(self):
        """Method Confirm wo forcefully."""
        wo_obj = self.env['fleet.vehicle.log.services']
        increment_obj = self.env['next.increment.number']
        pending_rep_obj = self.env['pending.repair.type']
        next_service_day_obj = self.env['next.service.days']
        odometer_increment = 0.0
        work_order = False
        if self._context.get('work_order_id', False):
            work_order = wo_obj.browse(self._context['work_order_id'])
            increment_ids = increment_obj.search([
                ('vehicle_id', '=', work_order.vehicle_id.id)])
            if not increment_ids:
                raise Warning(_("Next Increment Odometer is not set for %s \
          please set it from configuration!") % (work_order.vehicle_id.name))
            if increment_ids:
                odometer_increment = increment_ids[0].number
            next_service_day_ids = next_service_day_obj.search([
                ('vehicle_id', '=', work_order.vehicle_id.id)],
                limit=1)
            if not next_service_day_ids:
                raise Warning(_("Next service days is \
                     not configured for %s please set it from \
                     configuration!") % (work_order.vehicle_id.name))
            work_order_vals = {}
            if work_order.odometer == 0:
                raise Warning(_("Please set the \
                        current Odometer of vehilce in work order!"))
            odometer_increment += work_order.odometer
            next_service_date = work_order.date + \
                timedelta(days=next_service_day_ids.days)

            if work_order.already_closed:
                for repair_line in work_order.repair_line_ids:
                    if repair_line.complete is False:
                        for repair_line_in_vehicle in \
                                work_order.vehicle_id:
                            if work_order.name == repair_line_in_vehicle.name \
                                    and repair_line.repair_type_id.id == \
                                    repair_line_in_vehicle.repair_type_id.id:
                                continue
                            else:
                                incomplete_rep_id = pending_rep_obj.create({
                                    'repair_type_id':
                                    repair_line.repair_type_id and
                                    repair_line.repair_type_id.id or False,
                                    'name': work_order.name or '',
                                    'state': 'in-complete',
                                    'user_id': self._uid,
                                    "categ_id": repair_line.categ_id and
                                    repair_line.categ_id.id or False,
                                    "issue_date": work_order.date})
                                work_order.vehicle_id.write({
                                    'pending_repair_type_ids':
                                    [(4, incomplete_rep_id.id)],
                                    'state': 'complete'})
                for repair_line in work_order.repair_line_ids:
                    for pending_repair_line in \
                            work_order.vehicle_id.pending_repair_type_ids:
                        if repair_line.repair_type_id.id == \
                                pending_repair_line.repair_type_id.id and \
                                work_order.name == pending_repair_line.name:
                            if repair_line.complete is True:
                                pending_repair_line.unlink()
            else:
                for repair_line in work_order.repair_line_ids:
                    if repair_line.complete is False:
                        incomplete_rep_id = pending_rep_obj.create(
                            {'repair_type_id':
                                repair_line.repair_type_id and
                                repair_line.repair_type_id.id or False,
                                'name': work_order.name or '',
                                'state': 'in-complete', 'user_id': self._uid,
                                "categ_id": repair_line.categ_id and
                                repair_line.categ_id.id or False,
                                "issue_date": work_order.date})
                        work_order.vehicle_id.write({
                            'pending_repair_type_ids':
                            [(4, incomplete_rep_id.id)],
                            'state': 'complete'})
                        work_order_vals.update({"already_closed": True})
            work_order_vals.update({'state': 'done', 'already_closed': True,
                                    'next_service_odometer':
                                    odometer_increment,
                                    'date_close': date.today(),
                                    'closed_by': self._uid,
                                    'next_service_date': next_service_date})
            work_order.write(work_order_vals)
            if work_order.vehicle_id:
                work_order.vehicle_id.write({
                    'state': 'complete',
                    'last_service_by_id': work_order.team_id and
                    work_order.team_id.id or False,
                    'last_service_date': work_order.date_open,
                    'next_service_date': next_service_date,
                    'due_odometer': odometer_increment,
                    'due_odometer_unit': work_order.odometer_unit,
                    'last_change_status_date': date.today()})
            if self._context.get('team_trip', False):
                self.encode_history()
        return True
