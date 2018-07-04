# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import time
from datetime import datetime, date, timedelta
from odoo import models, fields, _, api
from odoo.tools import misc, DEFAULT_SERVER_DATE_FORMAT
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
from odoo.exceptions import Warning, ValidationError


class ServiceCategory(models.Model):
    _name = 'service.category'

    name = fields.Char(string="Service Category", size=2, translate=True)

    @api.multi
    def copy(self, default=None):
        if not default:
            default = {}
        raise Warning(_('You can\'t duplicate record!'))
        return super(ServiceCategory, self).copy(default=default)

    @api.multi
    def unlink(self):
        raise Warning(_('You can\'t delete record !'))
        return super(ServiceCategory, self).unlink()


class FleetVehicleLogServices(models.Model):

    @api.multi
    def copy(self, default=None):
        if not default:
            default = {}
        raise Warning(_('You can\'t duplicate record!'))
        return super(FleetVehicleLogServices, self).copy(default=default)

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise Warning(_('You can\'t delete Work Order which \
                                  in Confirmed or Done state!'))
        return super(FleetVehicleLogServices, self).unlink()

    @api.onchange('vehicle_id')
    def get_vehicle_info(self):
        if self.vehicle_id:
            vehicle = self.vehicle_id
            self.vechical_type_id = vehicle.vechical_type_id and \
                vehicle.vechical_type_id.id or False,
            self.purchaser_id = vehicle.driver_id and \
                vehicle.driver_id.id or False,
            self.fmp_id = vehicle.name or "",
#            self.main_type = vehicle.main_type or False,
            self.f_brand_id = vehicle.f_brand_id and \
                vehicle.f_brand_id.id or False,
            self.vehical_division_id = vehicle.vehical_division_id and \
                vehicle.vehical_division_id.id or False,
            self.vechical_location_id = vehicle.vechical_location_id and \
                vehicle.vechical_location_id.id or False,

    @api.multi
    def action_confirm(self):
        sequence = self.env['ir.sequence'].next_by_code('work.order.sequence')
        mod_obj = self.env['ir.model.data']
        cr, uid, context = self.env.args
        context = dict(context)
        for work_order in self:
            if work_order.vehicle_id:
                if work_order.vehicle_id.state == 'write-off':
                    raise Warning(_("You can\'t confirm this \
                            work order which vehicle is in write-off state!"))
                elif work_order.vehicle_id.state == 'in_progress':
                    raise Warning(_("Previous work order is not \
                            complete, complete that work order first than \
                                you can confirm this work order!"))
                elif work_order.vehicle_id.state == 'draft' or \
                        work_order.vehicle_id.state == 'complete':
                    raise Warning(_("Confirm work order can only \
                        when vehicle status is in Inspection or Released!"))
                work_order.vehicle_id.write({
                         'state': 'in_progress',
                         'last_change_status_date': date.today(),
                         'work_order_close': False})
            work_order.write({'state': 'confirm', 'name': sequence,
                              'date_open':
                              time.strftime(DEFAULT_SERVER_DATE_FORMAT)})
            model_data_ids = mod_obj.search([
                         ('model', '=', 'ir.ui.view'),
                         ('name', '=', 'continue_pending_repair_form_view')])
            resource_id = model_data_ids.read(['res_id'])[0]['res_id']
            context.update({'work_order_id': work_order.id,
                            'vehicle_id': work_order.vehicle_id and
                            work_order.vehicle_id.id or False})
            self.env.args = cr, uid, misc.frozendict(context)
            if work_order.vehicle_id:
                for pending_repair in \
                            work_order.vehicle_id.pending_repair_type_ids:
                    if pending_repair.state == 'in-complete':
                        return {
                            'name': _('Previous Repair Types'),
                            'context': self._context,
                            'view_type': 'form',
                            'view_mode': 'form',
                            'res_model': 'continue.pending.repair',
                            'views': [(resource_id, 'form')],
                            'type': 'ir.actions.act_window',
                            'target': 'new',
                        }
        return True

    @api.multi
    def action_done(self):
        cr, uid, context = self.env.args
        context = dict(context)
        odometer_increment = 0.0
        increment_obj = self.env['next.increment.number']
        next_service_day_obj = self.env['next.service.days']
        mod_obj = self.env['ir.model.data']

        for work_order in self:
            for repair_line in work_order.repair_line_ids:
                if repair_line.complete is True:
                    continue
                elif repair_line.complete is False:
                    model_data_ids = mod_obj.search([
                         ('model', '=', 'ir.ui.view'),
                         ('name', '=', 'pending_repair_confirm_form_view')])
                    resource_id = model_data_ids.read(['res_id'])[0]['res_id']
                    context.update({'work_order_id': work_order.id})
                    self.env.args = cr, uid, misc.frozendict(context)
                    return {
                        'name': _('WO Close Forcefully'),
                        'context': context,
                        'view_type': 'form',
                        'view_mode': 'form',
                        'res_model': 'pending.repair.confirm',
                        'views': [(resource_id, 'form')],
                        'type': 'ir.actions.act_window',
                        'target': 'new',
                    }
        increment_ids = increment_obj.search([
                        ('vehicle_id', '=', work_order.vehicle_id.id)])
        if not increment_ids:
            raise Warning(_("Next Increment \
                    Odometer is not set for %s please set it from \
                    configuration!") % (work_order.vehicle_id.name))
        if increment_ids:
            odometer_increment = increment_ids[0].number
        next_service_day_ids = next_service_day_obj.search([
                                ('vehicle_id', '=', work_order.vehicle_id.id)])
        if not next_service_day_ids:
            raise Warning(_("Next service days is \
                     not configured for %s please set it from \
                     configuration!") % (work_order.vehicle_id.name))

        work_order_vals = {}
        for work_order in self:
            if not work_order.team_trip_id:
                context.update({'wo': work_order})
            if work_order.team_trip_id:
                context.update({'team_trip': work_order.team_trip_id,
                                'workorder': work_order})
            self.env.args = cr, uid, misc.frozendict(context)
            if work_order.odometer == 0:
                raise Warning(_("Please set the current \
                                     Odometer of vehilce in work order!"))
            odometer_increment += work_order.odometer
            next_service_date = datetime.strptime(
                str(date.today()), DEFAULT_SERVER_DATE_FORMAT) + \
                timedelta(days=next_service_day_ids[0].days)
            work_order_vals.update({
                    'state': 'done',
                    'next_service_odometer': odometer_increment,
                    'already_closed': True,
                    'closed_by': uid,
                    'date_close': date.today(),
                    'next_service_date': next_service_date})
            work_order.write(work_order_vals)
            if work_order.vehicle_id:
                work_order.vehicle_id.write({
                     'state': 'complete',
                     'last_service_by_id': work_order.team_id and
                     work_order.team_id.id or False,
                     'last_service_date': date.today(),
                     'next_service_date': next_service_date,
                     'due_odometer': odometer_increment,
                     'due_odometer_unit': work_order.odometer_unit,
                     'last_change_status_date': date.today(),
                     'work_order_close': True})
                if work_order.already_closed:
                    for repair_line in work_order.repair_line_ids:
                        for pending_repair_line in \
                                work_order.vehicle_id.pending_repair_type_ids:
                            if repair_line.repair_type_id.id == \
                                pending_repair_line.repair_type_id.id and \
                                    work_order.name == \
                                    pending_repair_line.name:
                                if repair_line.complete is True:
                                    pending_repair_line.unlink()
        return True

    @api.multi
    def close_reopened_wo(self):
        """
        This method is used to update the existing shipment moves
        if WO parts are updated in terms of quantities or complete parts.
        """
        picking_obj = self.env['stock.picking']
        stock_move_obj = self.env['stock.move']
        location_obj = self.env['stock.location']
        stock_wh = self.env['stock.warehouse']
        delivery_dict = {}
        out_pick_type = self.env['stock.picking.type'].search([
                                           ('code', '=', 'outgoing')], limit=1)
        in_pick_type = self.env['stock.picking.type'].search([
                                           ('code', '=', 'incoming')], limit=1)
        for work_order in self:
            ret = False
            mov = False
            ship_id = work_order.out_going_ids and \
                work_order.out_going_ids[0] or False
            scrap_pick_id = work_order.old_parts_incoming_ship_ids and \
                work_order.old_parts_incoming_ship_ids[0] or False
            flag = False
            return_flag = False
            if ship_id:
                # If existing parts Updated
                move_ids = stock_move_obj.search([
                                      ('picking_id', '=', ship_id.id)])
                if move_ids:
                    self._cr.execute("delete from stock_move \
                                where id IN %s", (tuple(move_ids.ids),))
                flag = True
            else:
                if work_order.parts_ids:
                    # If no parts were there and we add parts.
                    src_loc = False
                    dest_loc = False
                    if out_pick_type and \
                            out_pick_type[0].default_location_src_id:
                        src_loc = out_pick_type[0].default_location_src_id.id
                    else:
                        src_loc = False
                        customerloc, src_loc = \
                            stock_wh._get_partner_locations()
                        if src_loc:
                            src_loc = src_loc.id

                    if out_pick_type and \
                            out_pick_type[0].default_location_dest_id:
                        dest_loc = out_pick_type[0].default_location_dest_id.id
                    else:
                        dest_loc = False
                        dest_loc, supplierloc = \
                            stock_wh._get_partner_locations()
                        if dest_loc:
                            dest_loc = dest_loc.id
                    delivery_dict.update({
                          'origin': work_order.name or '',
                          'picking_type_id': out_pick_type and
                          out_pick_type.ids[0] or False,
                          'location_id': src_loc or False,
                          'location_dest_id': dest_loc or False
                      })
                    ship_id = picking_obj.create(delivery_dict)
            if scrap_pick_id:
                # If a product is already returned we'll update it.
                move_ids = stock_move_obj.search([
                                  ('picking_id', '=', scrap_pick_id.id)])
                if move_ids:
                    self._cr.execute("delete from stock_move where \
                                id IN %s", (tuple(move_ids.ids),))
                return_flag = True
            for product in work_order.parts_ids:
                return_move_vals = {}
                mov = True
                move_vals = {
                    'product_id': product.product_id and
                    product.product_id.id or False,
                    'name': product.product_id and
                    product.product_id.name or '',
                    'product_uom_qty': product.qty or 0.0,
                    'product_uom': product.product_uom and
                    product.product_uom.id or False,
                    'location_id': out_pick_type.warehouse_id and
                    out_pick_type.warehouse_id.lot_stock_id and
                    out_pick_type.warehouse_id.lot_stock_id.id or False,
                    'location_dest_id': work_order.team_id and
                    work_order.team_id.id or False,
                    'price_unit': product.price_unit,
                    'picking_id': ship_id and ship_id.id,
                    'picking_type_id': out_pick_type and
                    out_pick_type.ids[0] or False
                }
                if product.old_part_return:
                    if not scrap_pick_id:
                        # If not parts were returned before
                        src_loc = False
                        dest_loc = False
                        if out_pick_type and \
                                out_pick_type[0].default_location_src_id:
                            src_loc = \
                                out_pick_type[0].default_location_src_id.id
                        else:
                            src_loc = False
                            customerloc, src_loc = \
                                stock_wh._get_partner_locations()
                            if src_loc:
                                src_loc = src_loc.id

                        if out_pick_type and \
                                out_pick_type[0].default_location_dest_id:
                            dest_loc = \
                                out_pick_type[0].default_location_dest_id.id
                        else:
                            dest_loc = False
                            dest_loc, supplierloc = \
                                stock_wh._get_partner_locations()
                            if dest_loc:
                                dest_loc = dest_loc.id
                        delivery_dict.update({
                              'origin': work_order.name or '',
                              'picking_type_id': out_pick_type and
                              out_pick_type.ids[0] or False,
                              'location_id': src_loc or False,
                              'location_dest_id': dest_loc or False
                          })
                        scrap_pick_id = picking_obj.create(delivery_dict)
                    ret = True
                    scrap_dest_loc_ids = location_obj.search(
                                             [("name", "=", "Scrapped")])
                    scrap_source_loc_id = False
                    if not scrap_dest_loc_ids:
                        raise Warning(_("There is no \
                                location defined for scrapped parts please \
                                define location with Scrapped!"))
                    if work_order.team_id:
                        scrap_source_loc_id = work_order.team_id and \
                                        work_order.team_id.id or False
                    else:
                        raise Warning(_("There is no team \
                                selected as source location, as old parts are \
                                returned so you need to select any for \
                                getting return parts.!"))
                    return_move_vals = {
                        'product_id': product.product_id and
                        product.product_id.id or False,
                        'name': product.product_id and
                        product.product_id.name or '',
                        'product_uom_qty': product.qty or 0.0,
                        'product_uom': product.product_uom and
                        product.product_uom.id or False,
                        'location_id': scrap_source_loc_id,
                        'location_dest_id': scrap_dest_loc_ids and
                        scrap_dest_loc_ids[0].id or False,
                        'price_unit': product.price_unit,
                        'picking_id': scrap_pick_id and
                        scrap_pick_id.id or False,
                        'picking_type_id': in_pick_type and
                        in_pick_type.ids[0] or False
                    }
                if mov:
                    if move_vals:
                        stock_move_obj.create(move_vals)
                else:
                    # If all parts removed from WO remove
                    # the complete delivery order.
                    work_order.write({'out_going_ids': [(6, 0, [])]})
                if ret:
                    if return_move_vals:
                        stock_move_obj.create(return_move_vals)
                else:
                    # IF none of the parts are being
                    # returned remove the incoming shipment
                    work_order.write(
                         {'old_parts_incoming_ship_ids': [(6, 0, [])]})
            if not flag and mov:
                # IF it's a new shipment make it done
                ship_id.signal_workflow('button_confirm')
                ship_id.force_assign()
                ship_id.action_done()
                work_order.write({'out_going_ids': [(4, ship_id.id)]})
            if not return_flag and ret:
                # IF it's a new shipment make it done
                scrap_pick_id.signal_workflow('button_confirm')
                scrap_pick_id.force_assign()
                scrap_pick_id.action_done()
                work_order.write(
                     {'old_parts_incoming_ship_ids': [(4, scrap_pick_id.id)]})
        return True

    @api.multi
    def update_incoming_shipment_from_migration_script(self):
        for order in self:
            for outgoing_shipment in order.out_going_ids:
                outgoing_shipment.write({'date': order.date_open,
                                         'min_date': order.date_open})
            for incoming_shipment in order.old_parts_incoming_ship_ids:
                incoming_shipment.write({'date': order.date_open,
                                         'min_date': order.date_open})
            for parts in order.parts_ids:
                order.is_parts = True
                for outgoing_shipment in order.out_going_ids:
                    for move_line_out in outgoing_shipment.move_lines:
                        if move_line_out.product_id.id == parts.product_id.id:
                            move_line_out.write({
                                'date': parts.date_issued or False,
                                'create_date': parts.date_issued or False,
                                'date_expected': parts.date_issued or False,
                                'issued_received_by_id': parts.issued_by and
                                parts.issued_by.id or False,
                            })
                for incoming_shipment in order.old_parts_incoming_ship_ids:
                    for move_line_in in incoming_shipment.move_lines:
                        if move_line_in.product_id.id == parts.product_id.id:
                            move_line_in.write({
                                'date': parts.date_issued or False,
                                'create_date': parts.date_issued or False,
                                'date_expected': parts.date_issued or False,
                                'issued_received_by_id': parts.issued_by and
                                parts.issued_by.id or False})
        return True

    @api.multi
    def encode_history(self):
        """
        This method is used to create the Encode Qty
        History for Team Trip from WO
        ------------------------------------------------------
        """
        wo_part_his_obj = self.env['workorder.parts.history.details']
        if self._context.get('team_trip', False):
            team_trip = self._context.get('team_trip', False)
            work_order = self._context.get('workorder', False)
            # If existing parts Updated
            wo_part_his_ids = wo_part_his_obj.search([
                      ('team_id', '=', team_trip and team_trip.id or False),
                      ('wo_id', '=', work_order and work_order.id or False)])
            if wo_part_his_ids:
                wo_part_his_ids.unlink()
            wo_part_dict = {}
            for part in work_order.parts_ids:
                wo_part_dict[part.product_id.id] = \
                            {'wo_en_qty': part.encoded_qty, 'qty': part.qty}
            for t_part in team_trip.allocate_part_ids:
                if t_part.product_id.id in wo_part_dict.keys():
                    new_wo_encode_qty = \
                        wo_part_dict[t_part.product_id.id]['wo_en_qty'] - \
                        wo_part_dict[t_part.product_id.id]['qty']
                    wo_part_history_vals = {
                        'team_id': team_trip.id,
                        'product_id': t_part.product_id.id,
                        'name': t_part.product_id.name,
                        'vehicle_make': t_part.product_id.vehicle_make_id.id,
                        'used_qty': wo_part_dict[t_part.product_id.id]['qty'],
                        'wo_encoded_qty':
                        wo_part_dict[t_part.product_id.id]['wo_en_qty'],
                        'new_encode_qty': new_wo_encode_qty,
                        'wo_id': work_order.id,
                        'used_date': t_part.issue_date,
                        'issued_by': self._uid or False
                    }
                    wo_part_his_obj.create(wo_part_history_vals)
                    t_part.write({'encode_qty': new_wo_encode_qty})
        return True

    @api.multi
    def action_reopen(self):
#        current_date = datetime.strptime(
#            datetime.strftime(date.today(), DEFAULT_SERVER_DATE_FORMAT),
#            DEFAULT_SERVER_DATE_FORMAT)
#        order_reopen_obj = self.env['work.order.reopen.days']
        for order in self:
            if order.vehicle_id:
#                reopen_ids = order_reopen_obj.search([
#                    ('vehicle_id', '=', order.vehicle_id.id)])
#                if not reopen_ids:
#                    raise Warning(_('Work Order Re-open \
#                    Days is not configured for %s please configure it \
#                    from configuration menu.') % (order.vehicle_id.name))
#                open_days = reopen_ids[0]
                if order.vehicle_id.state == 'write-off':
                    raise Warning(_("You can\'t Re-open this \
                            work order which vehicle is in write-off state!"))
                elif order.vehicle_id.state == 'in_progress':
                    raise Warning(_("Previous work order is not \
                         complete, complete that work order first than \
                          you can Re-Open work order!"))
                elif order.vehicle_id.state == 'draft' or \
                        order.vehicle_id.state == 'complete':
                    raise Warning(_("Re-open work order can \
                                only be generated either vehicle status \
                                    is in Inspection or Released!"))
                order.vehicle_id.write({'work_order_close': False,
                                        'state': 'in_progress'})
#            close_date = datetime.strptime(order.date_close,
#                                           DEFAULT_SERVER_DATE_FORMAT)
            self.write({'state': 'confirm'})
#            if abs((current_date - close_date).days) <= open_days.days:
#                self.write({'state': 'confirm'})
#            else:
#                raise Warning(_("This Work order is closed \
#                        more than %s days I can\'t be \
#                        re-open again!" % (open_days.days)))
        return True

    @api.multi
    def get_total(self):
        for rec in self:
            total = 0.0
            for line in rec.parts_ids:
                total += line.total
            rec.sub_total = total

    @api.multi
    def write(self, vals):
        if not self._context:
            self._context = {}
        for work_order in self:
            if work_order.vehicle_id:
                vals.update(
                    {
                        'fmp_id': work_order.vehicle_id and
                        work_order.vehicle_id.name or "",
                        'vechical_type_id': work_order.vehicle_id and
                        work_order.vehicle_id.vechical_type_id and
                        work_order.vehicle_id.vechical_type_id.id or False,
                        'purchaser_id': work_order.vehicle_id and
                        work_order.vehicle_id.driver_id and
                        work_order.vehicle_id.driver_id.id or False,
                        'main_type': work_order.vehicle_id.main_type,
                        'f_brand_id': work_order.vehicle_id and
                        work_order.vehicle_id.f_brand_id and
                        work_order.vehicle_id.f_brand_id.id or False,
                        'vehical_division_id': work_order.vehicle_id and
                        work_order.vehicle_id.vehical_division_id and
                        work_order.vehicle_id.vehical_division_id.id or False,
                        'vechical_location_id': work_order.vehicle_id and
                        work_order.vehicle_id.vechical_location_id and
                        work_order.vehicle_id.vechical_location_id.id or False,
                        })
        return super(FleetVehicleLogServices, self).write(vals)

    @api.model
    def _get_location(self):
        location_id = self.env['stock.location'].search([
                                     ('name', '=', 'Vehicle')])
        if location_id:
            return location_id.ids[0]
        return False

    @api.model
    def service_send_mail(self):
        model_obj = self.env['ir.model.data']
        send_obj = self.env['mail.template']
        res = model_obj.get_object_reference('fleet_operations',
                                             'email_template_edi_fleet')
        server_obj = self.env['ir.mail_server']
        record_obj = model_obj.get_object_reference('fleet_operations',
                                                    'ir_mail_server_service')
        self._cr.execute("SELECT id FROM fleet_vehicle WHERE \
                            next_service_date = DATE(NOW()) + 1")
#        due_odometer <= odometer OR
        vehicle_ids = [i[0] for i in self._cr.fetchall() if i]
        email_from_brw = server_obj.browse(record_obj[1])
        if res:
            temp_rec = send_obj.browse(res[1])
        for rec in self.browse(vehicle_ids):
            email_from = email_from_brw.smtp_user
            if not email_from:
                raise Warning(_("May be Out Going Mail \
                                    server is not configuration."))
            if vehicle_ids:
                temp_rec.send_mail(rec.id, force_send=True)
        return True

    @api.model
    def default_get(self, fields):
        vehicle_obj = self.env['fleet.vehicle']
        repair_type_obj = self.env['repair.type']
        if self._context.get('active_ids', False):
            for vehicle in vehicle_obj.browse(self._context['active_ids']):
                if vehicle.state == 'write-off':
                    raise Warning(_("You can\'t create work order \
                             for vehicle which is already write-off!"))
                elif vehicle.state == 'in_progress':
                    raise Warning(_("Previous work order is not \
                        complete, complete that work order first than you \
                        can create new work order!"))
                elif vehicle.state == 'rent':
                    raise Warning(_("You can\'t create work order \
                             for vehicle which is already On Rent!"))
                elif vehicle.state == 'draft' or vehicle.state == 'complete':
                    raise Warning(_("New work order can only be \
                            generated either vehicle status is in \
                            Inspection or Released!"))
        res = super(FleetVehicleLogServices, self).default_get(fields)
        repair_type_ids = repair_type_obj.search([])
        if not repair_type_ids:
            raise Warning(_("There is no data for \
                        repair type, add repair type from configuration!"))
        return res

    @api.onchange('cost_subtype_id')
    def get_repair_line(self):
        repair_lines = []
        if self.cost_subtype_id:
            for repair_type in self.cost_subtype_id.repair_type_ids:
                repair_lines.append((0, 0, {'repair_type_id': repair_type.id}))
            self.repair_line_ids = repair_lines

    @api.multi
    def _get_open_days(self):
        for work_order in self:
            diff = 0
            if work_order.state == 'confirm':
                diff = (datetime.today() -
                        datetime.strptime(work_order.date_open,
                                          DEFAULT_SERVER_DATE_FORMAT)).days
                work_order.open_days = str(diff)
            elif work_order.state == 'done':
                diff = (datetime.strptime(work_order.date_close,
                                          DEFAULT_SERVER_DATE_FORMAT) -
                        datetime.strptime(work_order.date_open,
                                          DEFAULT_SERVER_DATE_FORMAT)).days
                work_order.open_days = str(diff)
            else:
                work_order.open_days = str(diff)

    @api.multi
    def _get_total_parts_line(self):
        for work_order in self:
            total_parts = [parts_line.id
                           for parts_line in work_order.parts_ids
                           if parts_line]
            work_order.total_parts_line = len(total_parts)

    @api.model
    def get_warehouse(self):
        warehouse_ids = self.env['stock.warehouse'].search([])
        if warehouse_ids:
            return warehouse_ids.ids[0]
        else:
            return False

    @api.onchange('vehicle_id')
    def _onchange_vehicle(self):
        if not self.vehicle_id:
            return {}
        if self.vehicle_id:
            self.odometer = self.vehicle_id.odometer
            self.odometer_unit = self.vehicle_id.odometer_unit
            self.purchaser_id = self.vehicle_id.driver_id.id

    @api.constrains('date', 'date_complete')
    def check_complete_date(self):
        for vehicle in self:
            if vehicle.date and vehicle.date_complete:
                if vehicle.date_complete < vehicle.date:
                    raise ValidationError('ETIC Date Should Be \
                    Greater Than Issue Date.')

    _inherit = 'fleet.vehicle.log.services'

    _order = 'id desc'

    wono_id = fields.Integer(string='WONo',
                             help="Take this field for data migration")
    id = fields.Integer(string='ID')
    purchaser_id = fields.Many2one('res.partner', string='Purchaser')
    name = fields.Char(string='Work Order', size=32, readonly=True,
                       translate=True)
    fmp_id = fields.Char(string="Vehicle ID", size=64)
#    wo_invoice_reference = fields.Many2one('account.invoice',
#                                           string='Invoice Ref#',
#                                           readonly=True)
    wo_tax_amount = fields.Float(string='Tax', readonly=True)
    priority = fields.Selection([('normal', 'NORMAL'), ('high', 'HIGH'),
                                 ('low', 'LOW')], default='normal',
                                string='Work Priority')
    date_complete = fields.Date(string='Issued Complete ',
                                help='Date when the service is completed')
    date_open = fields.Date(string='Open Date',
                            help="When Work Order \
                                        will confirm this date will be set.")
    date_close = fields.Date(string='Date Close',
                             help="Closing Date of Work Order")
    closed_by = fields.Many2one('res.users', string='Closed By')
    etic = fields.Boolean(string='ETIC', help="Estimated Time In Completion",
                          default=True)
    wrk_location_id = fields.Many2one('stock.location',
                                      string='Location', readonly=True)
    wrk_attach_ids = fields.One2many('ir.attachment', 'wo_attachment_id',
                                     string='Attachments')
    task_ids = fields.One2many('service.task', 'main_id',
                               string='Service Task')
    parts_ids = fields.One2many('task.line', 'fleet_service_id',
                                string='Parts')
    note = fields.Text(string='Notes')
    date_child = fields.Date(related='cost_id.date', string='Date', store=True)
    inv_ref = fields.Many2one('account.invoice', string='Invoice Reference',
                              readonly=True)
    sub_total = fields.Float(compute="get_total", string='Total Cost',
                             default=0.0, store=True)
    state = fields.Selection([('draft', 'New'),
                              ('confirm', 'Open'), ('done', 'Close'),
                              ('cancel', 'Cancel')], string='Status',
                             default='draft', readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    delivery_id = fields.Many2one('stock.picking',
                                  string='Delivery Reference', readonly=True)
    team_id = fields.Many2one('res.partner', string="Teams")
    team_trip_id = fields.Many2one("fleet.team", string="Team Trip")
    maintenance_team_id = fields.Many2one("stock.location", string="Teams")
    next_service_date = fields.Date(string='Next Service Date')
    next_service_odometer = fields.Float(string='Next Odometer Value',
                                         readonly=True)
    repair_line_ids = fields.One2many('service.repair.line', 'service_id',
                                      string='Repair Lines')
    old_parts_incoming_ship_ids = fields.One2many('stock.picking',
                                                  'work_order_old_id',
                                                  string='Old Returned',
                                                  readonly=True)
    reopen_return_incoming_ship_ids = fields.One2many('stock.picking',
                                                      'work_order_reopen_id',
                                                      string='Reopen Returned',
                                                      readonly=True)
    out_going_ids = fields.One2many('stock.picking', 'work_order_out_id',
                                    string='Out Going', readonly=True)
    vechical_type_id = fields.Many2one('vehicle.type', string='Vechical Type')
    open_days = fields.Char(compute="_get_open_days", string="Open Days")
    already_closed = fields.Boolean("Already Closed?")
    total_parts_line = fields.Integer(compute="_get_total_parts_line",
                                      string='Total Parts')
    is_parts = fields.Boolean(string="Is Parts Available?")
    from_migration = fields.Boolean('From Migration')
    main_type = fields.Selection([('vehicle', 'Vehicle'),
                                  ('non-vehicle', ' Non-Vehicle')],
                                 string='Main Type')
    f_brand_id = fields.Many2one('fleet.vehicle.model.brand', string='Make')
    vehical_division_id = fields.Many2one('vehicle.divison', string='Division')
    vechical_location_id = fields.Many2one('service.department',
                                           string='Registration State')
    odometer = fields.Float(compute='_get_odometer', inverse='_set_odometer',
                            string='Last Odometer',
                            help='Odometer measure of the vehicle at the \
                                moment of this log')

    def _get_odometer(self):
        FleetVehicalOdometer = self.env['fleet.vehicle.odometer']
        for record in self:
            vehicle_odometer = FleetVehicalOdometer.search([
                ('vehicle_id', '=', record.vehicle_id.id)], limit=1,
                                                           order='value desc')
            if vehicle_odometer:
                record.odometer = vehicle_odometer.value
            else:
                record.odometer = 0

    def _set_odometer(self):
        FleetVehicalOdometer = self.env['fleet.vehicle.odometer']
        for record in self:
            vehicle_odometer = FleetVehicalOdometer.search(
                [('vehicle_id', '=', record.vehicle_id.id)],
                limit=1, order='value desc')
            if record.odometer < vehicle_odometer.value:
                raise Warning(_('You can\'t enter odometer less than previous \
                               odometer %s !') % (vehicle_odometer.value))
            if record.odometer:
                date = fields.Date.context_today(record)
                data = {'value': record.odometer, 'date': date,
                        'vehicle_id': record.vehicle_id.id}
                FleetVehicalOdometer.create(data)

    @api.onchange('team_id')
    def get_team_trip(self):
        if self.team_id:
            trip_ids = self.env['fleet.team'].search([
                         ("destination_location_id", "=", self.team_id.id),
                         ("state", "=", "close")])
            if trip_ids:
                for t_trip in trip_ids:
                    if not t_trip.is_work_order_done:
                        self.team_trip_id = t_trip.id
                        break


class FleetTeam(models.Model):
    _name = 'fleet.team'

    _order = 'id desc'

    @api.multi
    def copy(self, default=None):
        if not default:
            default = {}
        raise Warning(_('You can\'t duplicate record!'))
        return super(FleetTeam, self).copy(default=default)

    @api.multi
    def unlink(self):
        raise Warning(_('You can\'t delete record !'))
        return super(FleetTeam, self).unlink()

    @api.multi
    def _get_wo_done(self):
        """
        This method will indicate that the encoded qty for
        this contract team trip is issued.
        ------------------------------------------------------------------
        @param self : object pointer
        """
        for trip in self:
            flag = True
            if trip.from_migration:
                for part in trip.allocate_part_ids:
                    if part.encode_qty > 0.0:
                        flag = False
                        break
                if not trip.allocate_part_ids:
                    flag = False
            else:
                for part in trip.trip_parts_ids:
                    if part.available_qty > 0.0:
                        flag = False
                        break
                if not trip.trip_parts_ids:
                    flag = False
            trip.is_work_order_done = flag

    @api.multi
    def _get_total_parts_line(self):
        for rec in self:
            total_parts = [allocate_part.id
                           for allocate_part in rec.allocate_part_ids
                           if allocate_part]
            rec.total_parts_line = len(total_parts)

    @api.model
    def _default_source_location_id(self):
        stock_location_ids = self.env['stock.location'].search([
                                            ('name', '=', 'Stock')])
        if stock_location_ids:
            stock_location_ids = stock_location_ids.ids[0]
        else:
            stock_location_ids = False
        return stock_location_ids

    trip_id = fields.Integer('Trip ID',
                             help="Take this field for data migration")
    destination_location_id = fields.Many2one('stock.location',
                                              string="Team (Location)")
    name = fields.Char(string='Name',  size=64, translate=True)
    trip_date = fields.Date(string='Trip Date')
    return_date = fields.Date(string='Return Date')
    close_date = fields.Date(string='Close Date')
    source_location_id = fields.Many2one('stock.location',
                                         default=_default_source_location_id,
                                         string="Source Location")
    location_id = fields.Char(string="Destination Location", size=128,
                              translate=True)
    allocate_part_ids = fields.One2many('team.assign.parts', 'team_id',
                                        string='Assign Parts')
    note = fields.Text(string='Note', translate=True)
    state = fields.Selection([('draft', 'New'), ('open', 'Open'),
                              ('sent', 'Sent'), ('returned', 'Returned'),
                              ('close', 'Close')], default="draft",
                             string='Status')
    is_work_order_done = fields.Boolean(compute="_get_wo_done",
                                        string='Is Work Order Done?')
    incoming_ship_ids = fields.One2many('stock.picking', 'in_team_id',
                                        string='Incoming Shipment',
                                        readonly=True)
    outgoing_ship_ids = fields.One2many('stock.picking', 'out_team_id',
                                        string='Outgoing Shipment',
                                        readonly=True)
    incoming_rem_ship_ids = fields.One2many('stock.picking',
                                            'in_rem_team_id',
                                            'Incoming Remaining Shipment',
                                            readonly=True)
    is_return = fields.Boolean(string='Is Return?')
    from_migration = fields.Boolean(string='From Migration')
    wo_parts_ids = fields.One2many('workorder.parts.history.details',
                                   'team_id', string='Workorder Usage History')
    trip_parts_ids = fields.One2many('trip.encoded.history', 'team_id',
                                     string='Trip Usage History')
    total_parts_line = fields.Integer(compute="_get_total_parts_line",
                                      string='Total Parts')

    _order = 'id desc'

    @api.multi
    def update_incoming_shipment_from_migration_script(self):
        for order in self:
            order.name = order.destination_location_id and \
                        order.destination_location_id.name or ''
            for outgoing_shipment in order.outgoing_ship_ids:
                outgoing_shipment.write({'date': order.trip_date,
                                         'min_date': order.trip_date})
            for incoming_shipment in order.incoming_ship_ids:
                incoming_shipment.write({'date': order.trip_date,
                                         'min_date': order.trip_date})
            for parts in order.allocate_part_ids:
                for outgoing_shipment in order.outgoing_ship_ids:
                    for move_line_out in outgoing_shipment.move_lines:
                        if move_line_out.product_id.id == parts.product_id.id:
                            move_line_out.write({
                                 'date': parts.issue_date or False,
                                 'create_date': parts.issue_date or False,
                                 'date_expected': parts.issue_date or False})
                for incoming_shipment in order.incoming_ship_ids:
                    for move_line_in in incoming_shipment.move_lines:
                        if move_line_in.product_id.id == parts.product_id.id:
                            move_line_in.write({
                                'date': parts.issue_date or False,
                                'create_date': parts.issue_date or False,
                                'date_expected': parts.issue_date or False})
        return True

    @api.multi
    def send_parts_to_trip(self):
        for team in self:
            if team.state == 'close':
                raise Warning(_("Loaded parts already Deliver to trip!"))
            if team.state == 'sent':
                raise Warning(_("Team is already sent!"))
            if team.state != 'open':
                raise Warning(_("Please Open your trip before deliver it!"))
            if not team.allocate_part_ids:
                raise Warning(_("Please load the parts before deliver it!"))
            trip_vals = {'state': 'sent'}
            if not team.trip_date:
                trip_vals.update({'trip_date':
                                  time.strftime(DEFAULT_SERVER_DATE_FORMAT)})
            team.write(trip_vals)
            if team.allocate_part_ids:
                team.allocate_part_ids.write({"state": "sent"})
        return True

    @api.multi
    def get_return_from_trip(self):
        pick_obj = self.env['stock.picking']
        stock_move_obj = self.env['stock.move']
        move_lines_list = []
        inc_dict = {}
        flag = False
        in_pick_type = self.env['stock.picking.type'].search([
                                          ('code', '=', 'incoming')])
        for team in self:
            if team.state != 'sent':
                raise Warning(_("Please send your trip \
                                             before getting return it!"))
            if not team.allocate_part_ids:
                raise Warning(_("parts are not loaded!"))
            if not team.outgoing_ship_ids:
                raise Warning(_("parts are not Delivered \
                                            yet you can\'t get return it!"))
            if team.incoming_ship_ids:
                team_in_pick_id = team.incoming_ship_ids[0].id
                if team.incoming_ship_ids[0].move_lines:
                    team.incoming_ship_ids[0].move_lines.write(
                                           {'state': 'draft'})
                    team.incoming_ship_ids[0].move_lines.unlink()
                flag = True
            for line in team.allocate_part_ids:
                used_qty = line.qty_used + line.qty_damage + line.qty_missing
                line.write({'encode_qty': line.qty_used,
                            'state': 'returned', 'is_delete_line': True})
                if used_qty > 0:
                    move_lines_list.append((0, 0, {
                      'product_id': line.product_id and
                      line.product_id.id or False,
                      'name': line.name or '',
                      'product_uom_qty': used_qty,
                      'product_uom': line.product_id and
                      line.product_id.uom_id and
                      line.product_id.uom_id.id or False,
                      'location_id': team.destination_location_id and
                      team.destination_location_id.id or False,
                      'location_dest_id':
                      line.product_id.property_stock_inventory.id,
                      'create_date': line.issue_date
                      }))
            if move_lines_list:
                if not flag:
                    inc_dict.update({
                         'move_lines': move_lines_list,
                         'origin': "Used by - " + team.name or '',
                         'picking_type_id': in_pick_type and
                                    in_pick_type.ids[0] or False})
                    inc_ship_id = pick_obj.create(inc_dict)
                    team.write({'incoming_ship_ids': [(4, inc_ship_id.id)]})
                    inc_ship_id.signal_workflow('button_confirm')
                    inc_ship_id.force_assign()
                    inc_ship_id.signal_workflow('button_done')
                else:
                    for move in move_lines_list:
                        move_vals = move[2]
                        move_vals.update({'picking_id': team_in_pick_id,
                                          'state': 'done'})
                        stock_move_obj.create(move_vals)
            trip_vals = {'state': 'sent'}
            if not team.return_date:
                trip_vals.update({'return_date':
                                  time.strftime(DEFAULT_SERVER_DATE_FORMAT)})
            team.write({"state": "returned",
                        'is_return': True})
        return True

    @api.multi
    def open_trip(self):
        for rec in self:
            rec.state = 'open'

    @api.multi
    def close_trip(self):
        inc_obj = self.env['stock.picking']
        stock_move_obj = self.env['stock.move']
        trip_encoded_obj = self.env['trip.encoded.history']
        inc_dict = {}
        flag = False
        move_lines_list = []
        in_pick_type = self.env['stock.picking.type'].search([
                                         ('code', '=', 'incoming')])
        for team in self:
            if not team.is_return:
                raise Warning(_("Please Fill the Used Part \
                                Info and than close the team Trip!"))
            if team.allocate_part_ids:
                team.allocate_part_ids.write({'state': 'close'})
            for part_rec in team.allocate_part_ids:
                trip_encoded_ids = trip_encoded_obj.search([
                                ('team_id', '=', team.id),
                                ('product_id', '=', part_rec.product_id.id)])
                if trip_encoded_ids:
                    trip_encoded_ids.write({'used_qty': part_rec.qty_used})
                else:
                    vals = {
                            'team_id': team.id,
                            'product_id': part_rec.product_id.id,
                            'used_qty': part_rec.qty_used,
                            'part_name': part_rec.name
                            }
                    trip_encoded_obj.create(vals)

            if team.incoming_rem_ship_ids:
                team_in_rem_pick_id = team.incoming_rem_ship_ids[0].id
                if team.incoming_rem_ship_ids[0].move_lines:
                    team.incoming_rem_ship_ids[0].move_lines.write(
                                               {'state': 'draft'})
                    team.incoming_rem_ship_ids[0].move_lines.unlink()
                flag = True
            for line in team.allocate_part_ids:
                if line.qty_remaining > 0:
                    move_lines_list.append((0, 0, {
                      'product_id': line.product_id and
                      line.product_id.id or False,
                      'name': line.name or '',
                      'product_uom_qty': line.qty_remaining,
                      'product_uom': line.product_id and
                      line.product_id.uom_id and
                      line.product_id.uom_id.id or False,
                      'location_id': team.destination_location_id and
                      team.destination_location_id.id or False,
                      'location_dest_id': team.source_location_id.id,
                      'create_date': line.issue_date
                      }))
            if move_lines_list:
                if not flag:
                    inc_dict.update({
                         'move_lines': move_lines_list,
                         'picking_type_id': in_pick_type and
                         in_pick_type.ids[0] or False,
                         'origin': "Remaining Qty return by - " +
                         team.name or ''})
                    inc_ship_id = inc_obj.create(inc_dict)
                    team.write({'incoming_rem_ship_ids':
                                [(4, inc_ship_id.id)]})
                    inc_ship_id.signal_workflow('button_confirm')
                    inc_ship_id.force_assign()
                    inc_ship_id.force_assign()
                    inc_ship_id.action_done()
                else:
                    for move in move_lines_list:
                        move_vals = move[2]
                        move_vals.update({'picking_id':
                                          team_in_rem_pick_id or False})
                        new_inc_ship_id = stock_move_obj.create(move_vals)
                        new_inc_ship_id.signal_workflow('button_confirm')
                        new_inc_ship_id.force_assign()
                        new_inc_ship_id.action_done()
            team.write({'close_date':
                        time.strftime(DEFAULT_SERVER_DATE_FORMAT),
                        'state': 'close'})
        return True

    @api.multi
    def reopen_trip(self):
#        order_reopen_obj = self.env['work.order.reopen.days']
#        current_date = datetime.strptime(
#            datetime.strftime(date.today(), DEFAULT_SERVER_DATE_FORMAT),
#            DEFAULT_SERVER_DATE_FORMAT)
        for trip in self:
#            reopen_ids = order_reopen_obj.search([
#                ('vehicle_id', '=', trip.vehicle_id.id)])
#            if not reopen_ids:
#                raise Warning(_('Work Order Re-open \
#                    Days is not configured for %s please configure it \
#                    from configuration menu.') % (trip.vehicle_id.name))
#            open_days = reopen_ids and reopen_ids[0] or False
#            close_date = datetime.strptime(trip.close_date,
#                                           DEFAULT_SERVER_DATE_FORMAT)
            trip.state = 'open'
#            if abs((current_date - close_date).days) <= open_days.days:
#                trip.state = 'open'
#            else:
#                raise Warning(_("This Work order is closed \
#                         more than %s days I can\'t be \
#                         re-open again!" % (open_days.days)))
            if trip.allocate_part_ids:
                trip.allocate_part_ids.write({'state': 'open'})
        return True

    @api.onchange('destination_location_id')
    def onchange_get_name(self):
        prod_obj = self.env['product.product']
        assign_part_obj = self.env['team.assign.parts']
        cr, uid, context = self.env.args
        context = dict(context)
        if context is None:
            context = {}
        if self.destination_location_id:
            # Get the products on location
            team_rec = self.destination_location_id
            context.update({'location': team_rec.id})
            self.env.args = cr, uid, misc.frozendict(context)
            prod_ids = prod_obj.search([])
            part_assign_list = []
            for prod in prod_ids:
                if prod.qty_available > 0.0:
                    assign_part_obj.onchange_product_id()
                    part_assign_vals = {}
                    if prod.in_active_part:
                        part_assign_vals = \
                            {'product_id': False,
                             'name': False, 'vehicle_make_id': False,
                             'qty_on_hand': False, 'qty_on_truck': False,
                             'qty_used': 0.0, 'qty_missing': 0.0,
                             'qty_damage': 0.0, 'qty_remaining': False,
                             'remark': False, 'price_unit': False,
                             'date_issued': False, 'old_part_return': False,
                             }
                        raise Warning(_("You can\'t select \
                                part which is In-Active!"))
                    elif prod.qty_available <= 0:
                        part_assign_vals = {'product_id': False, 'name': False,
                                            'vehicle_make_id': False,
                                            'qty': 0.0}
                        raise Warning(_("You can\'t select \
                                part which has zero quantity!"))
                    else:
                        part_assign_vals = {
                            'name': prod.name or '',
                            'vehicle_make_id': prod.vehicle_make_id and
                            prod.vehicle_make_id.id or False,
                            'qty_on_hand': prod.qty_available or 0.0}

                    part_assign_vals.update({
                        'product_id': prod.id,
                        'qty_with_team': prod.qty_available,
                        'to_return': True,
                    })
                    part_assign_list.append((0, 0, part_assign_vals))

            self.name = team_rec.name or ''
            self.allocate_part_ids = part_assign_list


class WorkorderPartsHistoryDetails(models.Model):
    _name = 'workorder.parts.history.details'

    team_id = fields.Many2one('fleet.team', string='Contract Trip')
    product_id = fields.Many2one('product.product', string='Part No',
                                 help='The Part Number')
    name = fields.Char(string='Part Name', help='The Part Name',
                       translate=True)
    vehicle_make = fields.Many2one('fleet.vehicle.model.brand',
                                   string='Vehicle Make',
                                   help='The Make of the Vehicle')
    used_qty = fields.Float(string='Encoded Qty',
                            help='The Quantity that is used in in Workorder')
    wo_encoded_qty = fields.Float(string='Qty',
                                  help='The Quantity which is \
                                  available to use')
    new_encode_qty = fields.Float(string='Qty for Encoding',
                                  help='New Encoded Qty')
    wo_id = fields.Many2one('fleet.vehicle.log.services', string='Workorder',
                            help='The workorder for which the part was used')
    used_date = fields.Datetime(string='Issued Date')
    issued_by = fields.Many2one('res.users', string='Issued by',
                                help='The user who would issue the parts')

    _order = 'used_date desc'


class TripPartsHistoryDetails(models.Model):
    _name = 'trip.encoded.history'

    @api.multi
    def _get_encoded_qty(self):
        res = {}
        for parts_load in self:
            res[parts_load.id] = 0.0
            total__encode_qty = 0.0
            if parts_load.team_id and parts_load.team_id.wo_parts_ids:
                query = "select sum(used_qty) from \
                            workorder_parts_history_details where \
                            product_id=" + str(parts_load.product_id.id) + \
                            " and team_id=" + str(parts_load.team_id.id)
                self._cr.execute(query)
                result = self._cr.fetchone()
                total__encode_qty = result and result[0] or 0.0
                parts_load.write({'encoded_qty': total__encode_qty})
            if total__encode_qty:
                res[parts_load.id] = total__encode_qty
        return res

    @api.multi
    def _get_available_qty(self):
        for rec in self:
            available_qty = rec.used_qty - rec.dummy_encoded_qty
            if available_qty < 0:
                raise Warning(_('Quantity Available \
                                    must be greater than zero!'))
            rec.available_qty = available_qty

    team_id = fields.Many2one('fleet.team', string='Contract Trip')
    product_id = fields.Many2one('product.product', string='Part No',
                                 help='The Part Number')
    part_name = fields.Char(string='Part Name', size=128, translate=True)
    used_qty = fields.Float(string='Used Qty',
                            help='The Quantity that is used in in \
                                    Contact Team Trip')
    encoded_qty = fields.Float(string='Encoded Qty',
                               help='The Quantity that is used in \
                                        in Workorder')
    dummy_encoded_qty = fields.Float(compute="_get_encoded_qty",
                                     string='Encoded Qty')
    available_qty = fields.Float(compute="_get_available_qty",
                                 string='Qty for Encoding',
                                 help='The Quantity which is available to use')


class TripPartsHistoryDetailsTemp(models.Model):
    _name = 'trip.encoded.history.temp'

    team_id = fields.Many2one('fleet.team', string='Contract Trip')
    product_id = fields.Many2one('product.product', string='Part No',
                                 help='The Part Number')
    used_qty = fields.Float(string='Used Qty',
                            help='The Quantity that is used in in Workorder')
    work_order_id = fields.Many2one('fleet.vehicle.log.services',
                                    string="Work Order")


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    _order = 'id desc'

    out_team_id = fields.Many2one('fleet.team', string='Contact Team Trip')
    work_order_out_id = fields.Many2one('fleet.vehicle.log.services',
                                        string="Work Order")
    in_team_id = fields.Many2one('fleet.team', string='Contact Team Trip')
    in_rem_team_id = fields.Many2one('fleet.team', string='Contact Team Trip')
    work_order_old_id = fields.Many2one('fleet.vehicle.log.services',
                                        string="Work Order")
    work_order_reopen_id = fields.Many2one('fleet.vehicle.log.services',
                                           string="Work Order")
    stock_warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    received_by_id = fields.Many2one('res.users', string='Received By')

    @api.model
    def create(self, vals):
        if vals.get('origin', False) and vals['origin'][0] == ':':
            vals.update({'origin': vals['origin'][1:]})
        if vals.get('origin', False) and vals['origin'][-1] == ':':
            vals.update({'origin': vals['origin'][:-1]})
        return super(StockPicking, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('origin', False) and vals['origin'][0] == ':':
            vals.update({'origin': vals['origin'][1:]})
        if vals.get('origin', False) and vals['origin'][-1] == ':':
            vals.update({'origin': vals['origin'][:-1]})
        return super(StockPicking, self).write(vals)

    @api.multi
    def unlink(self):
        raise Warning(_('You can\'t delete record !'))
        return super(StockPicking, self).unlink()

    @api.multi
    def do_partial_from_migration_script(self):
        assert len(self._ids) == 1, 'Partial picking processing \
                                    may only be done one at a time.'
        stock_move = self.env['stock.move']
        uom_obj = self.env['product.uom']
        partial = self and self[0]
        partial_data = {
            'delivery_date': partial and partial.date or False
        }
        picking_type = ''
        if partial and partial.picking_type_id and \
                partial.picking_type_id.code == 'incoming':
            picking_type = 'in'
        elif partial and partial.picking_type_id and \
                partial.picking_type_id.code == 'outgoing':
            picking_type = 'out'
        elif partial and partial.picking_type_id and \
                partial.picking_type_id.code == 'internal':
            picking_type = 'int'
        for wizard_line in partial.move_lines:
            line_uom = wizard_line.product_uom
            move_id = wizard_line.id

            # Compute the quantity for respective wizard_line in
            # the line uom (this jsut do the rounding if necessary)
            qty_in_line_uom = uom_obj._compute_qty(line_uom.id,
                                                   wizard_line.product_qty,
                                                   line_uom.id)

            if line_uom.factor and line_uom.factor != 0:
                if float_compare(qty_in_line_uom, wizard_line.product_qty,
                                 precision_rounding=line_uom.rounding) != 0:
                    raise Warning(_('The unit of measure \
                            rounding does not allow you to ship "%s %s", \
                            only rounding of "%s %s" is accepted by the \
                            Unit of Measure.') % (wizard_line.product_qty,
                                                  line_uom.name,
                                                  line_uom.rounding,
                                                  line_uom.name))
            if move_id:
                # Check rounding Quantity.ex.
                # picking: 1kg, uom kg rounding = 0.01 (rounding to 10g),
                # partial delivery: 253g
                # => result= refused, as the qty left on picking
                # would be 0.747kg and only 0.75 is accepted by the uom.
                initial_uom = wizard_line.product_uom
                # Compute the quantity for respective
                # wizard_line in the initial uom
                qty_in_initial_uom = \
                    uom_obj._compute_qty(line_uom.id,
                                         wizard_line.product_qty,
                                         initial_uom.id)
                without_rounding_qty = (wizard_line.product_qty /
                                        line_uom.factor) * initial_uom.factor
                if float_compare(qty_in_initial_uom, without_rounding_qty,
                                 precision_rounding=initial_uom.rounding) != 0:
                    raise Warning(_('The rounding of the \
                        initial uom does not allow you to ship "%s %s", \
                        as it would let a quantity of "%s %s" to ship and \
                        only rounding of "%s %s" is accepted \
                        by the uom.') % (wizard_line.product_qty,
                                         line_uom.name,
                                         wizard_line.product_qty -
                                         without_rounding_qty,
                                         initial_uom.name,
                                         initial_uom.rounding,
                                         initial_uom.name))
            else:
                seq_obj_name = 'stock.picking.' + picking_type
                move_id = stock_move.create({
                        'name': self.env['ir.sequence'].next_by_code(
                                                             seq_obj_name),
                        'product_id': wizard_line.product_id and
                        wizard_line.product_id.id or False,
                        'product_qty': wizard_line.product_qty,
                        'product_uom': wizard_line.product_uom and
                        wizard_line.product_uom.id or False,
                        'prodlot_id': wizard_line.prodlot_id and
                        wizard_line.prodlot_id.id or False,
                        'location_id': wizard_line.location_id and
                        wizard_line.location_id.id or False,
                        'location_dest_id': wizard_line.location_dest_id and
                        wizard_line.location_dest_id.id or False,
                        'picking_id': partial and partial.id or False
                        })
                move_id.action_confirm()
            partial_data['move%s' % (move_id.id)] = {
                'product_id': wizard_line.product_id and
                wizard_line.product_id.id or False,
                'product_qty': wizard_line.product_qty,
                'product_uom': wizard_line.product_uom and
                wizard_line.product_uom.id or False,
                'prodlot_id': wizard_line.prodlot_id and
                wizard_line.prodlot_id.id or False,
            }
            product_currency_id = \
                wizard_line.product_id.company_id.currency_id and \
                wizard_line.product_id.company_id.currency_id.id or False
            picking_currency_id = \
                partial.company_id.currency_id and \
                partial.company_id.currency_id.id or False
            if (picking_type == 'in') and \
                    (wizard_line.product_id.cost_method == 'average'):
                partial_data['move%s' % (wizard_line.id)].update(
                         product_price=wizard_line.product_id.standard_price,
                         product_currency=product_currency_id or
                         picking_currency_id or False)
        partial.do_partial(partial_data)
        if partial.purchase_id:
            partial.purchase_id.write({'state': 'done'})
        return True


class StockMove(models.Model):
    _inherit = 'stock.move'

    _order = 'id desc'

    type = fields.Many2one(related='picking_id.picking_type_id',
                           string='Shipping Type',
                           store=True)
    issued_received_by_id = fields.Many2one('res.users', string='Received By')

    @api.onchange('picking_type_id', 'location_id', 'location_dest_id')
    def onchange_move_type(self):
        """
        On change of move type gives sorce and destination location.
        """
        if not self.location_id and not self.location_dest_id:
            mod_obj = self.env['ir.model.data']
            location_source_id = 'stock_location_stock'
            location_dest_id = 'stock_location_stock'
            if self.picking_type_id and \
                    self.picking_type_id.code == 'incoming':
                location_source_id = 'stock_location_suppliers'
                location_dest_id = 'stock_location_stock'
            elif self.picking_type_id and \
                    self.picking_type_id.code == 'outgoing':
                location_source_id = 'stock_location_stock'
                location_dest_id = 'stock_location_customers'
            source_location = mod_obj.get_object_reference('stock',
                                                           location_source_id)
            dest_location = mod_obj.get_object_reference('stock',
                                                         location_dest_id)
            self.location_id = source_location and source_location[1] or False
            self.location_dest_id = dest_location and dest_location[1] or False

    @api.model
    def _default_location_source(self):
        location_id = super(stock_move, self)._default_location_source()
        if self._context.get('stock_warehouse_id', False):
            warehouse_pool = self.env['stock.warehouse']
            for rec in warehouse_pool.browse(
                                 [self._context['stock_warehouse_id']]):
                if rec.lot_stock_id:
                    location_id = rec.lot_stock_id.id
        return location_id

    @api.model
    def _default_location_destination(self):
        location_dest_id = super(stock_move, self)._default_location_source()
        if self._context.get('stock_warehouse_id', False):
            warehouse_pool = self.env['stock.warehouse']
            for rec in warehouse_pool.browse(
                                 [self._context['stock_warehouse_id']]):
                if rec.wh_output_id_stock_loc_id:
                    location_dest_id = rec.wh_output_id_stock_loc_id and \
                                rec.wh_output_id_stock_loc_id.id or False
        return location_dest_id


class TeamAssignParts(models.Model):
    _name = 'team.assign.parts'

    @api.multi
    def _get_remaining_parts(self):
        for parts_load in self:
            used = parts_load.qty_used + \
                    parts_load.qty_missing + parts_load.qty_damage
            total = parts_load.qty_with_team + parts_load.qty_on_truck
            parts_load.qty_remaining = total - used

    @api.multi
    def _get_remaining_encode_qty(self):
        for parts_load in self:
            remaining_encode_qty = 0.0
            total__encode_qty = 0.0
            if parts_load.team_id and parts_load.team_id.wo_parts_ids:
                for wo_parts_rec in parts_load.team_id.wo_parts_ids:
                    if parts_load.product_id.id == wo_parts_rec.product_id.id:
                        total__encode_qty += wo_parts_rec.used_qty
                remaining_encode_qty = parts_load.qty_used - total__encode_qty
                parts_load.encode_qty = remaining_encode_qty
            if total__encode_qty:
                parts_load.dummy_encode_qty = remaining_encode_qty
            else:
                parts_load.dummy_encode_qty = parts_load.qty_used

    trip_history_id = fields.Integer(string='Trip Part History ID',
                                     help="Take this field for data migration")
    wizard_parts_id = fields.Many2one('edit.parts.contact.team.trip',
                                      string='PartNo')
    team_id = fields.Many2one('fleet.team', string='Team')
    product_id = fields.Many2one('product.product', string='PartNo',
                                 required=True)
    name = fields.Char(string='Part Name', size=124, translate=True)
    vehicle_make_id = fields.Many2one('fleet.vehicle.model.brand',
                                      string='Vehicle Make')
    encode_qty = fields.Float(string='Encode Qty')
    qty_on_hand = fields.Float(string='Qty on Hand')
    qty_on_truck = fields.Float(string='Qty on Truck', required=True)
    qty_used = fields.Float(string='Used')
    qty_missing = fields.Float(string='Missing')
    qty_damage = fields.Float(string='Damage')
    qty_remaining = fields.Float(compute="_get_remaining_parts",
                                 string='Remaining')
    remark = fields.Char(string='Remark', size=32, translate=True)
    state = fields.Selection([('open', 'Open'), ('sent', 'Sent'),
                              ('returned', 'Returned'),
                              ('close', 'Close')], string='Status',
                             default='open')
    qty_with_team = fields.Float(string='Qty with Team',
                                 help='This will be the quantity in \
                                     case if the parts are kept with the Team')
    to_return = fields.Boolean(string='Return?',
                               help='This will be checked in case we are \
                                       returning the parts back to stock')
    issued_by = fields.Many2one('res.users', string='Issued by',
                                default=lambda self: self._uid,
                                help='The user who would issue the parts')
    issue_date = fields.Date(string='Issue Date',
                             help='The date when the part was issued.')
    is_delete_line = fields.Boolean(string='Delete line?')
    dummy_encode_qty = fields.Float(compute="_get_remaining_encode_qty",
                                    string='Remaining encode qty')

    @api.multi
    def unlink(self):
        for product in self:
            if product.state == 'returned':
                raise Warning('Warning!', 'You can delete parts when contact \
                                            team trip is in return stage !')
            elif product.is_delete_line:
                raise Warning('Warning!', 'You can delete parts when contact \
                                            team trip is already return!')
        return super(TeamAssignParts, self).unlink()

    @api.model
    def create(self, vals):
        product_obj = self.env['product.product']
        if not vals.get('issue_date', False):
            vals.update({'issue_date':
                        time.strftime(DEFAULT_SERVER_DATE_FORMAT)})
        if vals.get('product_id', False):
            prod = product_obj.browse(vals['product_id'])
            vals.update({
                'name': prod.name or "",
                'vehicle_make_id': prod.vehicle_make_id and
                prod.vehicle_make_id.id or False,
                'qty_on_hand': prod.qty_available or 0.0
            })
        if vals.get('team_id', False) and vals.get('product_id', False):
            team_line_ids = self.search([
                     ('team_id', '=', vals['team_id']),
                     ('product_id', '=', vals['product_id'])])
            if team_line_ids:
                product_rec = product_obj.browse(vals['product_id'])
                raise Warning(_('You can not have duplicate \
                                parts assigned !!! \n Part No :- ' +
                                str(product_rec.default_code)))
        return super(TeamAssignParts, self).create(vals)

    @api.multi
    def write(self, vals):
        if vals.get('product_id', False) or vals.get('qty_on_truck', False):
            vals.update({
                     'issued_by': self._uid,
                     'issue_date': time.strftime(DEFAULT_SERVER_DATE_FORMAT)})
        return super(TeamAssignParts, self).write(vals)

    @api.onchange('qty_with_team', 'qty_on_truck', 'qty_used',
                  'qty_missing', 'qty_damage')
    def check_used_damage(self):
        total_used = self.qty_used + self.qty_missing + self.qty_damage
        qty_team = self.qty_on_truck + self.qty_with_team
        if total_used > qty_team:
            self.qty_used = 0.0
            self.qty_missing = 0.0
            self.qty_damage = 0.0
            raise Warning('Warning!', 'Total of Used, Missing and \
                           damage can not be greater than qty on truck!')

    @api.onchange('qty_on_hand', 'qty_on_truck')
    def check_used_qty_in_truck(self):
        if self.qty_on_truck > self.qty_on_hand:
            self.qty_on_truck = False
            raise Warning('User Error!!', 'Qty on Truck can not be \
                                greater than qty on hand!')

    @api.multi
    def copy(self, default=None):
        if not default:
            default = {}
        raise Warning(_('You can\'t duplicate record!'))
        return super(TeamAssignParts, self).copy(default=default)

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            rec = self.product_id
            if rec.in_active_part:
                self.product_id = False
                self.name = False
                self.vehicle_make_id = False
                self.qty_on_hand = False
                self.qty_on_truck = False
                self.qty_used = 0.0
                self.qty_missing = 0.0
                self.qty_damage = 0.0
                self.qty_remaining = False
                self.remark = False
                self.price_unit = False
                self.date_issued = False
                self.old_part_return = False
                raise Warning(_('You can\'t select \
                                        part which is In-Active!'))
            part_name = rec.name or ''
            if rec.qty_available <= 0:
                self.product_id = False
                self.name = False
                self.vehicle_make_id = False
                self.qty = 0.0
                raise Warning(_('You can\'t select part \
                                    which has zero quantity!'))
            self.name = part_name
            self.vehicle_make_id = rec.vehicle_make_id and \
                rec.vehicle_make_id.id or False,
            self.qty_on_hand = rec.qty_available or 0.0

    @api.onchange('issue_date')
    def onchange_issue_date(self):
        if not self._context:
            self._context = {}
        issue_date_o = self.issue_date or False
        trip_date = False
        return_date = False
        if self._context.get('trip_date', False):
            trip_date = datetime.strptime(self._context['trip_date'],
                                          '%Y-%m-%d').date()
        if self._context.get('return_date', False):
            return_date = datetime.strptime(self._context['return_date'],
                                            '%Y-%m-%d').date()
        if issue_date_o:
            issue_date = datetime.strptime(issue_date_o[:10],
                                           '%Y-%m-%d').date()
            if trip_date and return_date:
                if trip_date > issue_date or issue_date > return_date:
                    self.issue_date = False
                    raise Warning(_('Please enter \
                            issue date between Trip Date and Return Date!'))
            elif trip_date:
                if trip_date > issue_date or issue_date > date.today():
                    self.issue_date = False
                    raise Warning(_('Please enter \
                        issue date between Trip Date and Current Date!'))
            elif return_date:
                if return_date < issue_date or issue_date < date.today():
                    self.issue_date = False
                    raise Warning(_('Please enter \
                            issue date between Current Date and Return Date!'))
            elif not trip_date and not return_date and \
                    issue_date != date.today():
                self.issue_date = False
                raise Warning(_('Please enter current date \
                                           in issue date!!'))
        self.issue_date = issue_date_o


class StockLocation(models.Model):
    _inherit = 'stock.location'

    @api.multi
    def _get_teamp_trip_status(self):
        fleet_team_obj = self.env["fleet.team"]
        for location in self:
            flag = False
            trip_ids = fleet_team_obj.search([
                              ('destination_location_id', '=', location.id),
                              ('state', '=', 'close')])
            if trip_ids:
                for trip in trip_ids:
                    if trip.is_work_order_done is False:
                        flag = True
                        break
            location.is_team_trip = flag

    is_team = fields.Boolean(string='Is Team?')
    workshop = fields.Char(string='Work Shop Name')
    trip = fields.Boolean(string="Trip?")
    is_team_trip = fields.Boolean(compute="_get_teamp_trip_status",
                                  string="Is Team Trip", store=True)

#    @api.multi
#    def name_get(self):
#        res = {}
#        for m in self:
#            res[m.id] = m.name
#        return res.items()

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        team_trip_obj = self.env['fleet.team']
        if args is None:
            args = []
        ids = self.search(args).ids or []
        team_trip_ids = team_trip_obj.search([
                              ('destination_location_id', 'in', ids)])
        team_ids = ids
        wo_team_ids = []
        if self._context.get('t_trip', False):
            for team_trip in team_trip_ids:
                if self._context.get('t_trip', False):
                    if not team_trip.is_work_order_done and \
                            team_trip.destination_location_id.id in team_ids:
                        team_ids.remove(team_trip.destination_location_id.id)
                else:
                    if not team_trip.is_work_order_done and \
                                        team_trip.destination_location_id.id \
                                        not in wo_team_ids:
                            wo_team_ids.append(
                                   team_trip.destination_location_id.id)
            if not self._context.get('t_trip', False):
                team_ids = wo_team_ids
            if team_trip_ids:
                args = [('id', 'in', team_ids)]
        return super(StockLocation, self).name_search(name=name,
                                                       args=args,
                                                       operator=operator,
                                                       limit=limit)


class FleetWorkOrderSearch(models.TransientModel):
    _name = 'fleet.work.order.search'

    _rec_name = 'state'

    priority = fields.Selection([('normal', 'NORMAL'), ('high', 'HIGH'),
                                 ('low', 'LOW')], string='Order Priority')
    state = fields.Selection([('confirm', 'Open'), ('done', 'Close'),
                              ('any', 'Any')], string='Status')
    part_id = fields.Many2one('product.product', string='Parts')
    issue_date_from = fields.Date(string='Issue From')
    issue_date_to = fields.Date(string='Issue To')
    open_date_from = fields.Date(string='Open From')
    open_date_to = fields.Date(string='Open To')
    close_date_form = fields.Date(string='Close From')
    close_date_to = fields.Date(string='Close To')
    vehical_division_id = fields.Many2one('vehicle.divison',
                                          string="Division")
    team_id = fields.Many2one('fleet.team', string='Contact Team')
    work_order_id = fields.Many2one('fleet.vehicle.log.services',
                                    string='Work Order No')
    fmp_id = fields.Many2one('fleet.vehicle', string='Vehicle ID')
    cost_subtype_id = fields.Many2one('fleet.service.type',
                                      string='Service Type')
    repair_type_id = fields.Many2one('repair.type', string='Repair Type')
    open_days = fields.Char(string='Open Days', size=16)
    make_id = fields.Many2one("fleet.vehicle.model.brand", string="Make")
    model_id = fields.Many2one("fleet.vehicle.model", string="Model")

    @api.constrains('issue_date_from', 'issue_date_to')
    def check_issue_date(self):
        for vehicle in self:
            if vehicle.issue_date_to:
                if vehicle.issue_date_to < vehicle.issue_date_from:
                    raise ValidationError('Issue To Date Should Be \
                    Greater Than Last Issue From Date.')

    @api.constrains('open_date_from', 'open_date_to')
    def check_open_date(self):
        for vehicle in self:
            if vehicle.open_date_to:
                if vehicle.open_date_to < vehicle.open_date_from:
                    raise ValidationError('Open To Date Should Be \
                    Greater Than Open From Date.')

    @api.constrains('close_date_form', 'close_date_to')
    def check_close_date(self):
        for vehicle in self:
            if vehicle.close_date_to:
                if vehicle.close_date_to < vehicle.close_date_form:
                    raise ValidationError('Close To Date Should Be \
                    Greater Than Close From Date.')

    @api.multi
    def get_work_order_detail_by_advance_search(self):
        vehicle_obj = self.env['fleet.vehicle']
        work_order_obj = self.env['fleet.vehicle.log.services']
        part_line_obj = self.env['task.line']
        repair_line_obj = self.env['service.repair.line']
        domain = []
        order_ids = []
        for order in self:
            if order.make_id:
                vehicle_ids = vehicle_obj.search([
                                  ('f_brand_id', '=', order.make_id.id)])
                if vehicle_ids:
                    order_ids = work_order_obj.search([
                                   ('vehicle_id', 'in', vehicle_ids.ids)]).ids
                order_ids = sorted(set(order_ids))
            if order.model_id:
                vehicle_ids = vehicle_obj.search([
                                  ('model_id', '=', order.model_id.id)])
                if vehicle_ids:
                    order_ids = work_order_obj.search([
                                   ('vehicle_id', 'in', vehicle_ids.ids)]).ids
                order_ids = sorted(set(order_ids))
            part_id = order.part_id and order.part_id.id or False
            if part_id:
                parts_line_ids = part_line_obj.search([
                                       ('product_id', '=', part_id)])
                if parts_line_ids:
                    for part_line in parts_line_ids:
                        order_ids.append(part_line.fleet_service_id.id)
                    order_ids = sorted(set(order_ids))

            repair_type_id = order.repair_type_id and \
                order.repair_type_id.id or False
            if repair_type_id:
                repair_line_ids = repair_line_obj.search([
                                      ('repair_type_id', '=', repair_type_id)])
                if repair_line_ids:
                    for repair_line in repair_line_ids:
                        if repair_line.service_id:
                            order_ids.append(repair_line.service_id.id)
                    order_ids = sorted(set(order_ids))

            fmp_id = order.fmp_id and order.fmp_id.id or False
            if order.open_days:
                wrk_ids = work_order_obj.search([])
                if wrk_ids:
                    for wk_order in wrk_ids:
                        if wk_order.date_open:
                            diff = (datetime.today() -
                                    datetime.strptime(
                                        wk_order.date_open,
                                        DEFAULT_SERVER_DATE_FORMAT)).days
                            if str(diff) == wk_order.open_days:
                                order_ids.append(wk_order.id)
                    order_ids = sorted(set(order_ids))

            if fmp_id:
                work_order_ids = work_order_obj.search([
                                        ('vehicle_id', '=', fmp_id)])
                if work_order_ids:
                    for work_line in work_order_ids:
                        order_ids.append(work_line.id)
                    order_ids = sorted(set(order_ids))

            division_id = order.vehical_division_id and \
                order.vehical_division_id.id or False
            if division_id:
                vehicle_ids = vehicle_obj.search([
                                ('vehical_division_id', '=', division_id)])
                work_order_ids = work_order_obj.search([
                                ('vehicle_id', 'in', vehicle_ids.ids)])
                if work_order_ids:
                    for work_line in work_order_ids:
                        order_ids.append(work_line.id)
                    order_ids = sorted(set(order_ids))

            if order.state == 'confirm' or order.state == 'done':
                domain.append(('state', '=', order.state))
            if order.priority:
                domain += [('priority', '=', order.priority)]
            if order.team_id:
                domain += [('team_id', '=', order.team_id.id)]
            if order.work_order_id:
                order_ids.append(order.work_order_id.id)
            if order.cost_subtype_id:
                domain += [('cost_subtype_id', '=', order.cost_subtype_id.id)]
            if order.issue_date_from and order.issue_date_to:
                domain += [('date', '>=', order.issue_date_from)]
                domain += [('date', '<=', order.issue_date_to)]
            elif order.issue_date_from:
                domain += [('date', '=', order.issue_date_from)]
            if order.open_date_from and order.open_date_to:
                domain += [('date_open', '>=', order.open_date_from)]
                domain += [('date_open', '<=', order.open_date_to)]
            elif order.open_date_from:
                domain += [('date_open', '=', order.open_date_from)]
            if order.close_date_form and order.close_date_to:
                domain += [('date_close', '>=', order.close_date_form)]
                domain += [('date_close', '<=', order.close_date_to)]
            elif order.close_date_form:
                domain += [('date_close', '=', order.close_date_form)]

            if order.part_id or order.work_order_id or order.repair_type_id \
                    or order.fmp_id or order.vehical_division_id or \
                    order.open_days or order.make_id or order.model_id:
                domain += [('id', 'in', order_ids)]

            return {
                  'name': _('Work Order'),
                  'view_type': 'form',
                  "view_mode": 'tree,form',
                  'res_model': 'fleet.vehicle.log.services',
                  'type': 'ir.actions.act_window',
                  'nodestroy': True,
                  'domain': domain,
                  'context': self._context,
                  'target': 'current',
                  }
        return True


class ResUsers(models.Model):
    _inherit = 'res.users'

    usersql_id = fields.Char(string='User ID',
                             help="Take this field for data migration")


class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    wo_attachment_id = fields.Many2one('fleet.vehicle.log.services')


class ServiceTask(models.Model):
    _name = 'service.task'

    _description = 'Maintenance of the Task '

    main_id = fields.Many2one('fleet.vehicle.log.services',
                              string='Maintanace Reference')
    type = fields.Many2one('fleet.service.type', string='Type')
    total_type = fields.Float(string='Cost', readonly=True, default=0.0)
    product_ids = fields.One2many('task.line', 'task_id', string='Product')
    maintenance_info = fields.Text(string='Information', translate=True)


class TaskLine(models.Model):

    @api.multi
    def _amount_line(self):
        for line in self:
            price = line.price_unit * line.qty
            line.total = price

    _name = 'task.line'

    partshist_id = fields.Integer(string='Parts History ID',
                                  help="Take this field for data migration")
    wizard_parts_id = fields.Many2one('edit.parts.work.order',
                                      string='Parts Used')
    task_id = fields.Many2one('service.task',
                              string='task reference')
    fleet_service_id = fields.Many2one('fleet.vehicle.log.services',
                                       string='Vehicle Work Order')
    product_id = fields.Many2one('product.product', string='Product No',
                                 required=True)
    name = fields.Char(string='Part Name', size=124, translate=True)
    encoded_qty = fields.Float(string='Qty for Encoding',
                               help='Quantity that can be used')
    qty_hand = fields.Float(string='Qty on Hand',
                            help='Quantity on Hand')
    dummy_encoded_qty = fields.Float(string='Encoded Qty',
                                     help='Quantity that can be used')
    qty = fields.Float(string='Used')
    product_uom = fields.Many2one('product.uom', string='UOM', required=True)
    price_unit = fields.Float(string='Unit Cost')
    total = fields.Float(compute="_amount_line",  string='Total Cost')
    vehicle_make_id = fields.Many2one('fleet.vehicle.model.brand',
                                      string='Vehicle Make')
    date_issued = fields.Datetime(string='Date issued')
    old_part_return = fields.Boolean(string='Old Part Returned?')
    issued_by = fields.Many2one('res.users', string='Issued By',
                                default=lambda self: self._uid)
    is_deliver = fields.Boolean(string="Is Deliver?")

    @api.constrains('qty')
    def _check_used_qty(self):
        for rec in self:
            if rec.qty <= 0:
                raise Warning(_('You can\'t \
                            enter used quanity as Zero!'))

    @api.model
    def create(self, vals):
        """
        Overridden create method to add the issuer
        of the part and the time when it was issued.
        -----------------------------------------------------------
        @param self : object pointer
        """
        product_obj = self.env['product.product']
        if not vals.get('issued_by', False):
            vals.update({'issued_by': self._uid})
        if not vals.get('date_issued', False):
            vals.update({'date_issued':
                         time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})

        if vals.get('fleet_service_id', False) and \
                vals.get('product_id', False):
            task_line_ids = self.search([
                     ('fleet_service_id', '=', vals['fleet_service_id']),
                     ('product_id', '=', vals['product_id'])])
            if task_line_ids:
                product_rec = product_obj.browse(vals['product_id'])
                warrnig = 'You can not have duplicate \
                            parts assigned !!! \n Part No :- ' + \
                    product_rec.default_code
                raise Warning(_('User Error!'), _(warrnig))
        return super(TaskLine, self).create(vals)

    @api.multi
    def write(self, vals):
        """
        Overridden write method to add the issuer of the part
        and the time when it was issued.
        ---------------------------------------------------------------
        @param self : object pointer
        """
        if vals.get('product_id', False)\
            or vals.get('qty', False)\
            or vals.get('product_uom', False)\
            or vals.get('price_unit', False)\
                or vals.get('old_part_return') in (True, False):
                vals.update({'issued_by': self._uid,
                             'date_issued':
                             time.strftime(DEFAULT_SERVER_DATETIME_FORMAT)})
        return super(TaskLine, self).write(vals)

    @api.multi
    def unlink(self):
        trip_encoded_obj = self.env['trip.encoded.history']
        assign_part_obj = self.env['team.assign.parts']
        for task_line_rec in self:
            if task_line_rec.fleet_service_id and \
                    task_line_rec.fleet_service_id.team_trip_id:
                trip_encoded_ids = trip_encoded_obj.search([
                    ('team_id', '=', task_line_rec.fleet_service_id and
                     task_line_rec.fleet_service_id.team_trip_id.id),
                    ('product_id', '=', task_line_rec.product_id.id)])
                if trip_encoded_ids:
                    for trip_encoded_rec in trip_encoded_ids:
                        trip_encoded_rec.write({'encoded_qty':
                                                trip_encoded_rec.encoded_qty -
                                                task_line_rec.qty})
                assign_part_ids = assign_part_obj.search([
                      ('team_id', '=', task_line_rec.fleet_service_id and
                       task_line_rec.fleet_service_id.team_trip_id.id),
                      ('product_id', '=', task_line_rec.product_id and
                       task_line_rec.product_id.id)])
                if assign_part_ids:
                    for assign_part_rec in assign_part_ids:
                        assign_part_rec.write(
                          {'encode_qty': assign_part_rec.encode_qty +
                           task_line_rec.qty})
        return super(TaskLine, self).unlink()

    @api.onchange('date_issued')
    def check_onchange_part_issue_date(self):
        context_keys = self._context.keys()
        if 'date_open' in context_keys and self.date_issued:
            date_open = self._context.get('date_open', False)
            current_date = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
            if not self.date_issued >= date_open and \
                    not self.date_issued <= current_date:
                self.date_issued = False
                raise Warning(_('You can\t enter \
                        parts issue either open work order date or in \
                           between open work order date and current date!'))

    @api.onchange('product_id')
    def onchange_product_id(self):
        team_trip_obj = self.env['fleet.team']
        if self.product_id:
            rec = self.product_id
            if rec.in_active_part:
                self.product_id = False
                self.name = False
                self.vehicle_make_id = False
                self.qty = 1.0
                self.product_uom = False
                self.price_unit = False
                self.date_issued = False
                self.old_part_return = False
                raise Warning(_('You can\'t select \
                        part which is In-Active!'))
            unit_price = rec.standard_price
            product_uom_data = rec.uom_id.id
            part_name = rec.name or ''
            # Get Encoded Quantities from Team Trip
            if self._context.get('team_id', False):
                team_trip_ids = team_trip_obj.search([
                  ('destination_location_id', '=', self._context['team_id']),
                  ("state", "=", "close")])
                if team_trip_ids:
                    for t_trip in team_trip_ids:
                        if not t_trip.is_work_order_done:
                            for part in t_trip.allocate_part_ids:
                                if part.product_id.id == self.product_id.id:
                                    self.encoded_qty = part.encode_qty
                                    self.dummy_encoded_qty = part.encode_qty
                else:
                    if not rec.qty_available:
                        self.product_id = False
                        self.name = False
                        self.vehicle_make_id = False
                        self.qty = 1.0
                        self.product_uom = False
                        self.price_unit = False
                        self.date_issued = False
                        self.old_part_return = False
                        raise Warning(_('You can\'t select part \
                                           which has zero quantity!'))
            else:
                if not rec.qty_available:
                    self.product_id = False
                    self.name = False
                    self.vehicle_make_id = False
                    self.qty = 1.0
                    self.product_uom = False
                    self.price_unit = False
                    self.date_issued = False
                    self.old_part_return = False
                    raise Warning(_('You can\'t select part \
                                       which has zero quantity!'))
            self.price_unit = unit_price
            self.qty = 0
            self.product_uom = product_uom_data
            self.name = part_name
            self.vehicle_make_id = rec.vehicle_make_id and \
                rec.vehicle_make_id.id or False

    @api.onchange('product_id', 'qty', 'encoded_qty')
    def onchange_used_qty(self):
        rec_task = self[0]
        team_trip_obj = self.env['fleet.team']
        trip_encoded_obj = self.env['trip.encoded.history']
        if self.product_id:
            for rec in [self.product_id]:
                if self._context.get('team_id', False):
                    team_trip_ids = team_trip_obj.search([
                              ('destination_location_id', '=',
                               self._context['team_id']),
                              ("state", "=", "close")])
                    if team_trip_ids:
                        flag = False
                        if self._context.get('team_trip_id', False) and \
                                self.product_id:
                            remainig_encoded_qty = 0.0
                            trip_encoded_ids = trip_encoded_obj.search([
                                    ('team_id', '=',
                                        self._context.get('team_trip_id')),
                                    ('product_id', '=', self.product_id.id)])
                            if trip_encoded_ids:
                                remainig_encoded_qty = trip_encoded_ids and \
                                    trip_encoded_ids[0].available_qty or 0.0
                                if self._ids:
                                    used_qty_temp = self[0].qty or 0.0
                                    total_remainig_encoded_qty = \
                                        remainig_encoded_qty + used_qty_temp
                                    if total_remainig_encoded_qty < \
                                            self.qty:
                                        self.qty = 0.0
                                        raise Warning(_('You can\'t enter used\
                                               quantity greater than product \
                                               encoded quantity of trip!'))
                                    flag = True
                        if not flag and self.encode_qty < self.qty:
                            self.qty = 0.0
                            raise Warning(_('You can\'t enter used quantity \
                                           greater than product \
                                           encoded quantity of trip!'))

                    if not team_trip_ids:
                        qty_available = rec_task.qty + rec.qty_available
                        if qty_available < self.qty:
                            self.qty = 0.0
                            raise Warning(_('You can\'t enter used quantity \
                                   greater than product quantity on hand !'))
                else:
                    qty_available = rec_task.qty + rec.qty_available
                    if qty_available < self.qty:
                        self.qty = 0.0
                        raise Warning(_('You can\'t enter used quantity \
                                   greater than product quantity on hand !'))


class RepairType(models.Model):
    _name = 'repair.type'

    name = fields.Char(string='Repair Type', size=264,
                       translate=True)

    @api.multi
    def copy(self, default=None):
        if not default:
            default = {}
        raise Warning(_('You can\'t duplicate record!'))
        return super(RepairType, self).copy(default=default)

    @api.multi
    def unlink(self):
        raise Warning(_('You can\'t delete record !'))
        return super(RepairType, self).unlink()


class ServiceRepairLine(models.Model):
    _name = 'service.repair.line'

    @api.constrains('date', 'target_date')
    def check_target_completion_date(self):
        for vehicle in self:
            if vehicle.issue_date and vehicle.target_date:
                if vehicle.target_date < vehicle.issue_date:
                    raise ValidationError('Target Completion Date Should Be \
                    Greater Than Issue Date.')

    @api.constrains('target_date', 'date_complete')
    def check_etic_date(self):
        for vehicle in self:
            if vehicle.target_date and vehicle.date_complete:
                if vehicle.target_date > vehicle.date_complete:
                    raise ValidationError('Target Date Should Be \
                    Less Than ETIC Date.')

    service_id = fields.Many2one('fleet.vehicle.log.services',
                                 ondelete='cascade')
    repair_type_id = fields.Many2one('repair.type', string='Repair Type')
    categ_id = fields.Many2one('service.category', string='Category')
    issue_date = fields.Date(string='Issued Date ')
    date_complete = fields.Date(related='service_id.date_complete',
                                string="Complete Date")
    target_date = fields.Date(string='Target Completion')
    complete = fields.Boolean(string='Completed')


class FleetServiceType(models.Model):
    _inherit = 'fleet.service.type'

    category = fields.Selection([('contract', 'Contract'),
                                 ('service', 'Service'), ('both', 'Both')],
                                required=False,
                                string='Category', help='Choose wheter the \
                                                service refer to contracts, \
                                                vehicle services or both')
    repair_type_ids = fields.Many2many('repair.type',
                                       'fleet_service_repair_type_rel',
                                       'service_type_id', 'reapir_type_id',
                                       string='Repair Type')


#class work_order_reopen_days(models.Model):
#    _name = 'work.order.reopen.days'
#
#    _rec_name = 'days'
#
#    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle Id')
#    days = fields.Integer(string='Days')
#
#    @api.constrains('days')
#    def _constraint_positive_days(self):
#        for rec in self:
#            if rec.days <= 0:
#                raise Warning(_('Re-Open Days \
#                            Must be Greater than Zero!'))
#        return True


class ContactTeamTripSearch(models.TransientModel):
    _name = 'contact.team.trip.search'

    destination_location_id = fields.Many2one('stock.location',
                                              string="Team (Location)")
    trip_date_from = fields.Date(string='Trip Date From')
    trip_date_to = fields.Date(string='Trip Date To')
    return_date_from = fields.Date(string='Return Date From')
    return_date_to = fields.Date(string='Return Date To')
    source_location_id = fields.Many2one('stock.location',
                                         string="Source Location")
    location_id = fields.Char(string="Destination Location", size=128)

    @api.multi
    def get_contact_team_trip_by_advance_search(self):
        domain = []
        for order in self:
            if order.destination_location_id:
                domain += [('destination_location_id', '=',
                            order.destination_location_id.id)]
            if order.source_location_id:
                domain += [('source_location_id', '=',
                            order.source_location_id.id)]
            if order.location_id:
                domain += [('location_id', 'ilike', order.location_id)]

            if order.trip_date_from and order.trip_date_to:
                domain += [('trip_date', '>=', order.trip_date_from)]
                domain += [('trip_date', '<=', order.trip_date_to)]
            elif order.trip_date_from:
                domain += [('trip_date', '=', order.trip_date_from)]

            if order.return_date_from and order.return_date_to:
                domain += [('return_date', '>=', order.return_date_from)]
                domain += [('return_date', '<=', order.return_date_to)]
            elif order.return_date_from:
                domain += [('return_date', '=', order.return_date_from)]
            return {
                  'name': _('Contact Team Trip'),
                  'view_type': 'form',
                  "view_mode": 'tree,form',
                  'res_model': 'fleet.team',
                  'type': 'ir.actions.act_window',
                  'nodestroy': True,
                  'domain': domain,
                  'context': self._context,
                  'target': 'current',
                  }
        return True