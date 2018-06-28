# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from datetime import datetime, date
from odoo import models, fields, api, _
from odoo.exceptions import Warning


class PartsContactTrip(models.TransientModel):
    _name = 'parts.contact.trip'

    part_ids = fields.One2many('add.parts.contact.trip', 'wizard_part_id',
                               string='Assign Parts')

    @api.multi
    def add_part_on_contact_team_trip(self):
        del_obj = self.env['stock.picking']
        stock_move_obj = self.env['stock.move']
        team_assign_obj = self.env['fleet.team']
        parts_assign_obj = self.env["team.assign.parts"]
        move_lines_list = []
        delivery_dict = {}
        team_part_line_ids = []
        out_picking_type = self.env['stock.picking.type'].search([
                                          ('code', '=', 'outgoing')])
        in_picking_type = self.env['stock.picking.type'].search([
                                          ('code', '=', 'incoming')])
        for rec_main in self:
            for rec in rec_main.part_ids:
                if rec.qty_on_truck <= 0:
                    raise Warning("User Error!",
                                  _("Loaded part must be greater than zero!"))
            for rec in rec_main.part_ids:
                vals = {}
                if self._context.get('active_id'):
                    vals.update({'team_id':
                                self._context.get('active_id', False)})
                    if rec.product_id:
                        vals.update({'product_id': rec.product_id.id})
                    if rec.name:
                        vals.update({'name': rec.name})
                    if rec.vehicle_make_id:
                        vals.update({'vehicle_make_id':
                                    rec.vehicle_make_id.id})
                    if rec.qty_on_hand:
                        vals.update({'qty_on_hand': rec.qty_on_hand})
                    if rec.qty_on_truck:
                        vals.update({'qty_on_truck': rec.qty_on_truck})
                    if rec.qty_with_team:
                        vals.update({'qty_with_team': rec.qty_with_team})
                    if rec.qty_used:
                        vals.update({'qty_used': rec.qty_used})
                    if rec.qty_missing:
                        vals.update({'qty_missing': rec.qty_missing})
                    if rec.qty_damage:
                        vals.update({'qty_damage': rec.qty_damage})
                    if rec.remark:
                        vals.update({'remark': rec.remark})
                    if rec.issue_date:
                        vals.update({'issue_date': rec.issue_date})
                    if rec.state:
                        vals.update({'state': rec.state})

                    line_id = parts_assign_obj.create(vals)
                    team_part_line_ids.append(line_id)

        if self._context.get('active_id', False):
            for team in team_assign_obj.browse([self._context['active_id']]):
                flag = False
                if team.outgoing_ship_ids:
                    team_out_pick_id = team.outgoing_ship_ids[0].id
                    if team.outgoing_ship_ids[0].move_lines:
                        team.outgoing_ship_ids[0].move_lines.write(
                                                   {'state': 'draft'})
                        team.outgoing_ship_ids[0].move_lines.unlink()
                    flag = True
                for line in team.allocate_part_ids:
                    if line.qty_on_truck <= 0:
                        raise Warning("User Error!",
                                      _("Loaded part must be greater \
                                      than zero!"))
                    move_lines_list.append((0, 0, {
                                  'product_id': line.product_id and
                                  line.product_id.id or False,
                                  'name': line.name or '',
                                  'product_uom_qty': line.qty_on_truck or 0.0,
                                  'product_uom': line.product_id and
                                  line.product_id.uom_id and
                                  line.product_id.uom_id.id or False,
                                  'location_id': team.source_location_id and
                                  team.source_location_id.id or False,
                                  'location_dest_id':
                                  team.destination_location_id and
                                  team.destination_location_id.id or False,
                                  'create_date': line.issue_date
                                  }))
                if move_lines_list:
                    if not flag:
                        delivery_dict.update({
                          'move_lines': move_lines_list,
                          'origin': "Send to - " +
                          team.destination_location_id.name or '',
                          'picking_type_id': out_picking_type and
                                    out_picking_type.ids[0] or False
                          })
                        del_order_id = del_obj.create(delivery_dict)
                        team.write({'outgoing_ship_ids':
                                    [(4, del_order_id.id)]})
                        del_order_id.signal_workflow('button_confirm')
                        del_order_id.force_assign()
                        del_order_id.signal_workflow('button_done')
                    else:
                        for move in move_lines_list:
                            move_vals = move[2]
                            move_vals.update({'picking_id': team_out_pick_id,
                                              'state': 'done'})
                            stock_move_obj.create(move_vals)
                if team.state == 'returned':
                    pick_obj = self.env['stock.picking']
                    stock_move_obj = self.env['stock.move']
                    parts_assign_obj = self.env["team.assign.parts"]
                    move_lines_list = []
                    inc_dict = {}
                    flag = False
                    move_lines_list = []
                    if team.incoming_ship_ids:
                        team_in_pick_id = team.incoming_ship_ids[0].id
                        if team.incoming_ship_ids[0].move_lines:
                            team.incoming_ship_ids[0].move_lines.write(
                                                       {'state': 'draft'})
                            team.incoming_ship_ids[0].move_lines.unlink()
                        flag = True
                    for line in team.allocate_part_ids:
                        used_qty = line.qty_used + \
                                    line.qty_damage + line.qty_missing
                        line.write({'encode_qty': line.qty_used,
                                    'state': 'returned'})
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
                                 'picking_type_id': in_picking_type and
                                 in_picking_type.ids[0] or False
                                 })
                            inc_ship_id = pick_obj.create(inc_dict)
                            team.write({'incoming_ship_ids':
                                        [(4, inc_ship_id.id)]})
                            inc_ship_id.signal_workflow('button_confirm')
                            inc_ship_id.force_assign()
                            inc_ship_id.signal_workflow('button_done')
                        else:
                            for move in move_lines_list:
                                move_vals = move[2]
                                move_vals.update({'picking_id':
                                                  team_in_pick_id or False,
                                                  'state': 'done'})
                                stock_move_obj.create(move_vals)
        return True


class AddPartsContactTrip(models.TransientModel):
    _name = 'add.parts.contact.trip'

    wizard_part_id = fields.Many2one('parts.contact.trip', string='PartNo')
    product_id = fields.Many2one('product.product', string='PartNo',
                                 required=True)
    name = fields.Char(string='Part Name', size=124, translate=True)
    vehicle_make_id = fields.Many2one('fleet.vehicle.model.brand',
                                      string='Vehicle Make')
    qty_on_hand = fields.Float(string='Qty on Hand')
    qty_on_truck = fields.Float(string='Qty on Truck', required=True)
    qty_with_team = fields.Float(string='Qty with Team',
                                 help='This will be the quantity in case \
                                 if the parts are kept with the Team')
    qty_used = fields.Float(string='Used')
    qty_missing = fields.Float(string='Missing')
    qty_damage = fields.Float(string='Damage')
    remark = fields.Char(string='Remark', size=32, translate=True)
    issue_date = fields.Datetime(string='Issue Date',
                                 help='The date when the part was issued.')
    state = fields.Selection([('open', 'Open'), ('sent', 'Sent'),
                              ('returned', 'Returned'), ('close', 'Close')],
                             string='Status')

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
                self.qty_used = False
                self.qty_missing = False
                self.qty_damage = False
                self.qty_remaining = False
                self.remark = False
                self.price_unit = False
                self.date_issued = False,
                self.old_part_return = False
                raise Warning("User Error!", _("You can\'t select \
                            part which is In-Active!"))
            part_name = rec.name or ''
            if rec.qty_available <= 0:
                self.product_id = False
                self.name = False
                self.vehicle_make_id = False
                self.qty = 0.0
                raise Warning("User Error!", _("You can\'t select part \
                            which has zero quantity!"))
            self.name = part_name
            self.vehicle_make_id = rec.vehicle_make_id and \
                rec.vehicle_make_id.id or False
            self.qty_on_hand = rec.qty_available or 0.0

    @api.onchange('qty_with_team', 'qty_on_truck', 'qty_used',
                  'qty_missing', 'qty_damage')
    def check_used_damage(self):
        total_used = self.qty_used + self.qty_missing + self.qty_damage
        qty_team = self.qty_on_truck + self.qty_with_team
        if total_used > qty_team:
            self.qty_used = False
            self.qty_missing = False
            self.qty_damage = False
            raise Warning("User Error!", _("Total of Used, Missing \
                           and damage can \
                           not be greater than qty on truck!"))

    @api.onchange('qty_on_hand', 'qty_on_truck')
    def check_used_qty_in_truck(self):
        if self.qty_on_truck > self.qty_on_hand:
            self.qty_on_truck = False
            raise Warning("User Error!", _("Qty on Truck can not be \
                            greater than qty on hand!"))

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
        if self._context.get('return_date'):
            return_date = datetime.strptime(
                        self._context.get('return_date'), '%Y-%m-%d').date()
        if self.issue_date:
            issue_date = datetime.strptime(
                               self.issue_date[:10], '%Y-%m-%d').date()
            if trip_date and return_date:
                if trip_date > issue_date or issue_date > return_date:
                    self.issue_date = False
                    raise Warning("Warning !", _("Please enter issue \
                                date between Trip Date and Return Date!"))

            elif trip_date:
                if trip_date > issue_date or issue_date > date.today():
                    self.issue_date = False
                    raise Warning("Warning !", _("Please enter issue date \
                                       between Trip Date and Current Date!"))
            elif return_date:
                if return_date < issue_date or issue_date < date.today():
                    self.issue_date = False
                    raise Warning("Warning !", _("Please enter issue date \
                                   between Current Date and Return Date!"))

            elif not trip_date and not return_date and \
                    issue_date != date.today():
                self.issue_date = False
                raise Warning("Warning !", _("Please enter current \
                                date in issue date!!"))
        self.issue_date = issue_date_o


class EditPartsContactTeamTrip(models.Model):
    _name = 'edit.parts.contact.team.trip'

    part_ids = fields.One2many('team.assign.parts', 'wizard_parts_id',
                               string='Assign Parts')

    @api.model
    def default_get(self, fields):
        if self._context is None:
            self._context = {}
        res = super(EditPartsContactTeamTrip, self).default_get(fields)
        team_assign_obj = self.env['fleet.team']
        team_line_ids = []
        if self._context.get('active_id', False):
            team_rec_main = team_assign_obj.browse(self._context['active_id'])
            for team_line in team_rec_main.allocate_part_ids:
                team_line_ids.append(team_line.id)
        res.update({'part_ids': team_line_ids})
        return res

    @api.multi
    def save_part_on_contact_team_trip(self):
        del_obj = self.env['stock.picking']
        stock_move_obj = self.env['stock.move']
        team_assign_obj = self.env['fleet.team']
        move_lines_list = []
        delivery_dict = {}
        out_pick_type = self.env['stock.picking.type'].search([
                                       ('code', '=', 'outgoing')])
        for rec_main in self:
            for rec in rec_main.part_ids:
                if rec.qty_on_truck <= 0:
                    raise Warning("User Error!", _("Loaded part must \
                                            be greater than zero!"))
        if self._context.get('active_id'):
            for team in team_assign_obj.browse([self._context['active_id']]):
                flag = False
                if team.outgoing_ship_ids:
                    team_out_pick_id = team.outgoing_ship_ids[0].id
                    if team.outgoing_ship_ids[0].move_lines:
                        team.outgoing_ship_ids[0].move_lines.write(
                                                       {'state': 'draft'})
                        team.outgoing_ship_ids[0].move_lines.unlink()
                    flag = True
                for line in team.allocate_part_ids:
                    if line.qty_on_truck <= 0:
                        raise Warning("User Error!",
                                      _("Loaded part must be greater \
                                      than zero!"))
                    move_lines_list.append((0, 0, {
                          'product_id': line.product_id and
                          line.product_id.id or False,
                          'name': line.name or '',
                          'product_uom_qty': line.qty_on_truck or 0.0,
                          'product_uom': line.product_id and
                          line.product_id.uom_id and
                          line.product_id.uom_id.id or False,
                          'location_id': team.source_location_id and
                          team.source_location_id.id or False,
                          'location_dest_id': team.destination_location_id and
                          team.destination_location_id.id or False,
                          'create_date': line.issue_date
                      }))
                if move_lines_list:
                    if not flag:
                        delivery_dict.update({
                              'move_lines': move_lines_list,
                              'origin': "Send to - " +
                              team.destination_location_id.name or '',
                              'picking_type_id': out_pick_type and
                              out_pick_type.ids[0] or False})
                        del_order_id = del_obj.create(delivery_dict)
                        team.write({'outgoing_ship_ids':
                                    [(4, del_order_id.id)]})
                        del_order_id.signal_workflow('button_confirm')
                        del_order_id.force_assign()
                        del_order_id.action_done()
                    else:
                        for move in move_lines_list:
                            move_vals = move[2]
                            move_vals.update({'picking_id': team_out_pick_id})
                            new_del_ord_id = stock_move_obj.create(move_vals)
                            new_del_ord_id.signal_workflow('button_confirm')
                            new_del_ord_id.force_assign()
                            new_del_ord_id.action_done()
                if team.state == 'returned':
                    pick_obj = self.env['stock.picking']
                    stock_move_obj = self.env['stock.move']
                    move_lines_list = []
                    inc_dict = {}
                    flag = False
                    move_lines_list = []
                    in_picking_type = self.env['stock.picking.type'].search([
                                               ('code', '=', 'incoming')])
                    if team.incoming_ship_ids:
                        team_in_pick_id = team.incoming_ship_ids[0].id
                        if team.incoming_ship_ids[0].move_lines:
                            team.incoming_ship_ids[0].move_lines.write(
                                                       {'state': 'draft'})
                            team.incoming_ship_ids[0].move_lines.unlink()
                        flag = True
                    for line in team.allocate_part_ids:
                        used_qty = line.qty_used + \
                                    line.qty_damage + line.qty_missing
                        line.write({'encode_qty': line.qty_used,
                                    'state': 'returned'})
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
                                 'picking_type_id': in_picking_type and
                                 in_picking_type.ids[0] or False})
                            inc_ship_id = pick_obj.create(inc_dict)
                            team.write({'incoming_ship_ids':
                                        [(4, inc_ship_id.id)]})
                            inc_ship_id.signal_workflow('button_confirm')
                            inc_ship_id.force_assign()
                            inc_ship_id.action_done()
                        else:
                            for move in move_lines_list:
                                move_vals = move[2]
                                move_vals.update({'picking_id':
                                                  team_in_pick_id or False})
                                new_inc_ship = \
                                    stock_move_obj.create(move_vals)
                                new_inc_ship.signal_workflow('button_confirm')
                                new_inc_ship.force_assign()
                                new_inc_ship.action_done()
        return True
