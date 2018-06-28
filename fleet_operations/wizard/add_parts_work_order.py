# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import time
from odoo.tools import misc, DEFAULT_SERVER_DATE_FORMAT
from odoo import models, fields, api, _
from odoo.exceptions import Warning


class PartsWorkOrder(models.TransientModel):
    _name = 'parts.work.order'

    part_ids = fields.One2many('add.parts.work.order', 'wizard_part_id',
                               string='Used Parts')

    @api.multi
    def add_part_on_work_order(self):
        work_order_obj = self.env['fleet.vehicle.log.services']
        parts_used_obj = self.env["task.line"]
        for rec_main in self:
            for rec in rec_main.part_ids:
                vals = {}
                if self._context.get('active_id', False):
                    vals.update({'fleet_service_id':
                                 self._context['active_id']})
                    if rec.product_id:
                        vals.update({'product_id': rec.product_id.id})
                    if rec.name:
                        vals.update({'name': rec.name})
                    if rec.vehicle_make_id:
                        vals.update({'vehicle_make_id':
                                     rec.vehicle_make_id.id})
                    if rec.qty:
                        vals.update({'qty': rec.qty})
                    vals.update({'encoded_qty': rec.encoded_qty})
                    vals.update({'qty_hand': rec.qty_hand})
                    if rec.product_uom:
                        vals.update({'product_uom': rec.product_uom.id})
                    if rec.price_unit:
                        vals.update({'price_unit': rec.price_unit})
                    if rec.date_issued:
                        vals.update({'date_issued': rec.date_issued})
                    if rec.old_part_return:
                        vals.update({'old_part_return': rec.old_part_return})
                    parts_used_obj.create(vals)
        if self._context.get('active_id', False):
            for work_order in work_order_obj.browse(
                                    [self._context.get('active_id')]):
                if work_order.parts_ids:
                    work_order.write({'is_parts': True})
                if not work_order.parts_ids:
                    work_order.write({'is_parts': False})
                if not work_order.team_trip_id:
                    work_order.close_reopened_wo()
                elif work_order.team_trip_id:
                    cr, uid, context = self.env.args
                    context = dict(context)
                    context.update({'team_trip': work_order.team_trip_id.id,
                                    'workorder': work_order.id})
                    work_order.encode_history()
                    self.env.args = cr, uid, misc.frozendict(context)
                    for part_rec in work_order.parts_ids:
                        trip_encoded_ids = \
                            self.env['trip.encoded.history'].search(
                               [('team_id', '=', work_order.team_trip_id.id),
                                ('product_id', '=', part_rec.product_id and
                                 part_rec.product_id.id or False)])
                        if trip_encoded_ids:
                            encoded_qty = \
                                trip_encoded_ids[0].encoded_qty + part_rec.qty
                            trip_encoded_ids[0].write(
                                          {'encoded_qty': encoded_qty})
        return True


class AddPartsWorkOrder(models.TransientModel):
    _name = 'add.parts.work.order'

    wizard_part_id = fields.Many2one('parts.work.order', string='PartNo')
    product_id = fields.Many2one('product.product', string='Product No')
    qty = fields.Float(string='Used')
    old_part_return = fields.Boolean(string='Old Part Returned?')

    price_unit = fields.Float(string='Unit Cost')
    name = fields.Char(string='Part Name', size=124, translate=True)
    qty_hand = fields.Float(string='Qty on Hand', help='Quantity on Hand')
    encoded_qty = fields.Float(string='Qty for Encoding',
                               help='Quantity that can be used')
    vehicle_make_id = fields.Many2one('fleet.vehicle.model.brand',
                                      string='Vehicle Make')
    product_uom = fields.Many2one('product.uom', string='UOM')
    date_issued = fields.Datetime(string='Date issued')

    dummy_price_unit = fields.Float(string='Unit Cost')
    dummy_name = fields.Char(string='Part Name', size=124, translate=True)
    dummy_qty_hand = fields.Float(string='Qty on Hand', help='Qty on Hand')
    dummy_encoded_qty = fields.Float(string='Qty for Encoding',
                                            help='Quantity that can be used')
    dummy_vehicle_make_id = fields.Many2one('fleet.vehicle.model.brand',
                                            string='Vehicle Make')
    dummy_product_uom = fields.Many2one('product.uom', string='UOM')
    dummy_date_issued = fields.Datetime(string='Date issued')

    @api.onchange('date_issued')
    def check_onchange_part_issue_date(self):
        context_keys = self._context.keys()
        if 'date_open' in context_keys and self.date_issued:
            date_open = self._context.get('date_open', False)
            current_date = time.strftime(DEFAULT_SERVER_DATE_FORMAT)
            if self.date_issued >= date_open and \
                    self.date_issued <= current_date:
                return True
            else:
                self.date_issued = False
                raise Warning(('You can\t enter \
                       parts issue either open \
                       work order date or in between open work \
                       order date and current date!'))

    @api.onchange('product_id')
    def onchange_product_id(self):
        team_trip_obj = self.env['fleet.team']
        if self.product_id:
            rec = self.product_id
            if rec.active is False:
                raise Warning(_("You can\'t select \
                            part which is In-Active!"))
                self.name = False
                self.qty = 1.0
                self.price_unit = False
                self.old_part_return = False
                self.product_id = False
                self.vehicle_make_id = False
                self.product_uom = False
                self.date_issued = False
            unit_price = rec.standard_price
            product_uom_data = rec.uom_id.id
            part_name = rec.name or ''
            part_qty_hand = rec.qty_available
            # Get Encoded Quantities from Team Trip
            if self._context.get('team_id', False):
                team_trip_ids = team_trip_obj.search([
                  ('destination_location_id', '=', self._context['team_id']),
                  ("state", "=", "close")])
                if team_trip_ids:
                    for t_trip in team_trip_ids:
                        if not t_trip.is_work_order_done:
                            for part in t_trip.trip_parts_ids:
                                if part.product_id.id == self.product_id.id:
                                    self.encoded_qty = part.available_qty
                                    self.dummy_encoded_qty = part.available_qty
                else:
                    if rec.qty_available <= 0:
                        raise Warning(_("You can\'t \
                                    select part \
                                    which has zero quantity!"))
                        self.product_id = False
                        self.name = False
                        self.vehicle_make_id = False
                        self.qty = 1.0
                        self.qty_hand = 1.0
                        self.price_unit = False
                        self.date_issued = False
                        self.product_uom = False
                        self.old_part_return = False
                        self.encoded_qty = 0.0
                        self.dummy_price_unit = False
                        self.dummy_name = False
                        self.dummy_product_uom = False
                        self.dummy_date_issued = False
                        self.dummy_encoded_qty = 0.0
                        self.dummy_qty_hand = 0.0
                        self.dummy_vehicle_make_id = False
            else:
                if rec.qty_available < self.used_qty:
                    raise Warning(_("You can\'t enter \
                                    used quantity greater \
                                   than product quantity on hand !"))
                    self.qty = 1.0
            self.price_unit = unit_price
            self.qty_hand = part_qty_hand
            self.qty = 0.0
            self.product_uom = product_uom_data
            self.name = part_name
            self.dummy_qty_hand = part_qty_hand
            self.dummy_price_unit = unit_price
            self.dummy_product_uom = product_uom_data
            self.dummy_name = part_name

    @api.onchange('product_id', 'qty', 'encoded_qty')
    def onchange_used_qty(self):
        team_trip_obj = self.env['fleet.team']
        if self.product_id:
            rec = self.product_id
            if self._context.get('team_id', False):
                team_trip_ids = team_trip_obj.search([
                  ('destination_location_id', '=', self._context['team_id']),
                  ("state", "=", "close")])
                if team_trip_ids and self.encoded_qty < self.qty:
                    self.qty = 0.0
                    raise Warning(_("You can\'t enter \
                               used quantity greater \
                               than product encoded quantity of trip!"))
                if not team_trip_ids:
                    if rec.qty_available < self.qty:
                        self.qty = 0.0
                        raise Warning(_("You can\'t \
                               enter used quantity \
                               greater than product quantity on hand !"))
            else:
                if rec.qty_available < self.qty:
                    self.qty = 0.0
                    raise Warning(_("You can\'t enter \
                                used quantity greater \
                                than product quantity on hand !"))


class EditPartsWorkOrder(models.Model):
    _name = 'edit.parts.work.order'

    part_ids = fields.One2many('task.line', 'wizard_parts_id',
                               string='Used Parts')

    @api.model
    def default_get(self, fields):
        if self._context is None:
            self._context = {}
        res = super(EditPartsWorkOrder, self).default_get(fields)
        work_order_obj = self.env['fleet.vehicle.log.services']
        work_order_line_ids = []
        trip_encoded_temp__obj = self.env['trip.encoded.history.temp']
        if self._context.get('active_id'):
            work_order_rec = work_order_obj.browse(self._context['active_id'])
            for work_order_line in work_order_rec.parts_ids:
                work_order_line_ids.append(work_order_line.id)
                if work_order_rec.team_trip_id:
                    trip_encoded_temp_ids = trip_encoded_temp__obj.search([
                           ('team_id', '=', work_order_rec.team_trip_id.id),
                           ('product_id', '=', work_order_line.product_id.id),
                           ('work_order_id', '=', work_order_rec.id)])
                    if trip_encoded_temp_ids:
                        trip_encoded_temp_ids.unlink()
                    vals = {
                        'team_id': work_order_rec.team_trip_id.id,
                        'product_id': work_order_line.product_id.id,
                        'used_qty': work_order_line.qty,
                        'work_order_id': work_order_rec.id
                    }
                    trip_encoded_temp__obj.create(vals)
        res.update({'part_ids': work_order_line_ids})
        return res

    @api.multi
    def save_part_on_work_order(self):
        work_order_obj = self.env['fleet.vehicle.log.services']
        cr, uid, context = self.env.args
        context = dict(context)
        if context.get('active_id', False):
            for work_order in work_order_obj.browse(
                                [context['active_id']]):
                if not work_order.parts_ids:
                    work_order.write({'is_parts': False})
                if work_order.parts_ids:
                    work_order.write({'is_parts': True})
                if not work_order.team_trip_id:
                    work_order.close_reopened_wo()
                elif work_order.team_trip_id:
                    trip_encoded_obj = self.env['trip.encoded.history']
                    trip_encoded_temp_obj = \
                        self.env['trip.encoded.history.temp']
                    context.update({'team_trip': work_order.team_trip_id.id,
                                    'workorder': work_order.id})
                    work_order.encode_history()
                    self.env.args = cr, uid, misc.frozendict(context)
                    for part_rec in work_order.parts_ids:
                        trip_encoded_ids = trip_encoded_obj.search([
                                ('team_id', '=', work_order.team_trip_id.id),
                                ('product_id', '=', part_rec.product_id.id)])
                        trip_encoded_temp_ids = \
                            trip_encoded_temp_obj.search([
                                  ('team_id', '=', work_order.team_trip_id.id),
                                  ('product_id', '=', part_rec.product_id.id),
                                  ('work_order_id', '=', work_order.id)])
                        part_used_qty = 0.0
                        if trip_encoded_temp_ids:
                            part_used_qty = trip_encoded_temp_ids[0].used_qty
                        if trip_encoded_ids:
                            encoded_qty = \
                                trip_encoded_ids[0].encoded_qty - \
                                part_used_qty + part_rec.qty
                            trip_encoded_ids[0].write(
                                              {'encoded_qty': encoded_qty})
        return True