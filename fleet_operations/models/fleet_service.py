# See LICENSE file for full copyright and licensing details.
"""Fleet Service model."""
import time
from datetime import date, datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, Warning
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT, DEFAULT_SERVER_DATE_FORMAT, misc, ustr
from odoo.tools.float_utils import float_compare


class ServiceCategory(models.Model):
    """Service Category Model."""

    _name = 'service.category'
    _description = 'Vehicle Service Category'

    name = fields.Char(string="Service Category", size=2, translate=True)

    def copy(self, default=None):
        """Copy Method."""
        if not default:
            default = {}
        raise Warning(_('You can\'t duplicate record!'))


class FleetVehicleLogServices(models.Model):
    """Fleet Vehicle Log Services Model."""

    _inherit = 'fleet.vehicle.log.services'
    _order = 'id desc'
    _rec_name = 'name'

    def unlink(self):
        """Unlink Method."""
        for rec in self:
            if rec.state != 'draft':
                raise Warning(_('You can\'t delete Work Order which '
                                'in Confirmed or Done state!'))
        return super(FleetVehicleLogServices, self).unlink()

    @api.onchange('vehicle_id')
    def get_vehicle_info(self):
        """Onchange Method."""
        if self.vehicle_id:
            vehicle = self.vehicle_id
            self.vechical_type_id = vehicle.vechical_type_id and \
                vehicle.vechical_type_id.id or False,
            self.purchaser_id = vehicle.driver_id and \
                vehicle.driver_id.id or False,
            # self.fmp_id = vehicle.name or "",
#            self.main_type = vehicle.main_type or False,
            self.f_brand_id = vehicle.f_brand_id and \
                vehicle.f_brand_id.id or False,
            self.vehical_division_id = vehicle.vehical_division_id and \
                vehicle.vehical_division_id.id or False,
            self.vehicle_location_id = vehicle.vehicle_location_id and \
                vehicle.vehicle_location_id.id or False,

    def action_create_invoice(self):
        """Invoice for Deposit Receive."""
        for service in self:
            if service.amount <= 0.0:
                raise ValidationError("You can not create service invoice without amount!!"
                                      "Please add Service amount first !!")

            deposit_inv_ids = self.env['account.move'].search([
                ('vehicle_service_id', '=', service.id), ('type', '=', 'out_invoice'),
                ('state', 'in', ['draft', 'open', 'in_payment'])
            ])
            if deposit_inv_ids:
                raise Warning(_("Deposit invoice is already Pending\n"
                                "Please proceed that deposit invoice first"))

            if not service.purchaser_id:
                raise Warning(
                    _("Please configure Driver from vehicle or in a service order!!"))

            inv_ser_line = [(0, 0, {
                'name': ustr(service.cost_subtype_id and
                             service.cost_subtype_id.name) + ' - Service Cost',
                'price_unit': service.amount,
                'account_id': service.vehicle_id and service.vehicle_id.income_acc_id and
                service.vehicle_id.income_acc_id.id or False,
            })]
            for line in service.parts_ids:
                inv_line_values = {
                    'product_id': line.product_id and
                    line.product_id.id or False,
                    'name': line.product_id and
                    line.product_id.name or '',
                    'price_unit': line.price_unit or 0.00,
                    'quantity': line.qty,
                    'account_id': service.vehicle_id and service.vehicle_id.income_acc_id and
                    service.vehicle_id.income_acc_id.id or False
                }
                inv_ser_line.append((0, 0, inv_line_values))
            inv_values = {
                'partner_id': service.purchaser_id and
                service.purchaser_id.id or False,
                'type': 'out_invoice',
                'invoice_date': service.date_open,
                'invoice_date_due': service.date_complete,
                'invoice_line_ids': inv_ser_line,
                'vehicle_service_id': service.id,
                'is_invoice_receive': True,
            }
            self.env['account.move'].create(inv_values)

    def action_return_invoice(self):
        """Invoice for Deposit Return."""

        for service in self:
            deposit_inv_ids = self.env['account.move'].search([
                ('vehicle_service_id', '=', service.id), ('type', '=', 'out_refund'),
                ('state', 'in', ['draft', 'open', 'in_payment'])
            ])
            if deposit_inv_ids:
                raise Warning(_("Deposit Return invoice is already Pending\n"
                                "Please proceed that deposit invoice first"))

            inv_ser_line = [(0, 0, {
                'product_id': service.cost_subtype_id and
                service.cost_subtype_id.id or False,
                'name': 'Service Cost',
                'price_unit': service.amount or 0.0,
                'account_id': service.vehicle_id and service.vehicle_id.income_acc_id and
                service.vehicle_id.income_acc_id.id or False,
            })]
            for line in service.parts_ids:
                inv_line_values = {
                    'product_id': line.product_id.id or False,
                    'name': 'Service Cost',
                    'price_unit': line.price_unit or 0.00,
                    'quantity': line.qty,
                    'account_id': service.vehicle_id and service.vehicle_id.income_acc_id and
                    service.vehicle_id.income_acc_id.id or False
                }
                inv_ser_line.append((0, 0, inv_line_values))
            inv_values = {
                'partner_id': service.purchaser_id and
                service.purchaser_id.id or False,
                'type': 'out_refund',
                'invoice_date': service.date_open,
                'invoice_date_due': service.date_complete,
                'invoice_line_ids': inv_ser_line,
                'vehicle_service_id': service.id,
                'is_invoice_return': True,
            }
            self.env['account.move'].create(inv_values)

    def action_confirm(self):
        """Action Confirm Of Button."""
        sequence = self.env['ir.sequence'].next_by_code(
            'service.order.sequence')
        mod_obj = self.env['ir.model.data']
        context = self.env.context.copy()
        for work_order in self:
            if work_order.vehicle_id:
                if work_order.vehicle_id.state == 'write-off':
                    raise Warning(_("You can\'t confirm this \
                            work order which vehicle is in write-off state!"))
                elif work_order.vehicle_id.state == 'in_progress':
                    raise Warning(_("Previous work order is not "
                                    "complete, complete that work order first than "
                                    "you can confirm this work order!"))
                elif work_order.vehicle_id.state == 'draft' or \
                        work_order.vehicle_id.state == 'complete':
                    raise Warning(_("Confirm work order can only "
                                    "when vehicle status is in Inspection or Released!"))
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
            if work_order.vehicle_id:
                for pending_repair in \
                        work_order.vehicle_id.pending_repair_type_ids:
                    if pending_repair.state == 'in-complete':
                        return {
                            'name': _('Previous Repair Types'),
                            'context': context,
                            'view_type': 'form',
                            'view_mode': 'form',
                            'res_model': 'continue.pending.repair',
                            'views': [(resource_id, 'form')],
                            'type': 'ir.actions.act_window',
                            'target': 'new',
                        }
        return True

    def action_done(self):
        """Action Done Of Button."""
        context = dict(self.env.context)
        odometer_increment = 0.0
        increment_obj = self.env['next.increment.number']
        next_service_day_obj = self.env['next.service.days']
        mod_obj = self.env['ir.model.data']
        for work_order in self:
            service_inv = self.env['account.move'].search([
                ('type', '=', 'out_invoice'),
                ('vehicle_service_id', '=', work_order.id)])
            if work_order.amount > 0 and not service_inv:
                raise ValidationError("Vehicle Service amount is greater"
                                      " than Zero So, "
                                      "Without Service Invoice you can not done the Service !!"
                                      "Please Generate Service Invoice first !!")
            for repair_line in work_order.repair_line_ids:
                if repair_line.complete is True:
                    continue
                elif repair_line.complete is False:
                    model_data_ids = mod_obj.search([
                        ('model', '=', 'ir.ui.view'),
                        ('name', '=', 'pending_repair_confirm_form_view')])
                    resource_id = model_data_ids.read(['res_id'])[0]['res_id']
                    context.update({'work_order_id': work_order.id})
                    # self.env.args = cr, uid, misc.frozendict(context)
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
            return {
                'name': ('Next Service Day'),
                'res_model': 'update.next.service.config',
                'type': 'ir.actions.act_window',
                'view_id': False,
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new'
            }
        if increment_ids:
            odometer_increment = increment_ids[0].number

        next_service_day_ids = next_service_day_obj.search([
            ('vehicle_id', '=', work_order.vehicle_id.id)])
        if not next_service_day_ids:
            return {
                'name': ('Next Service Day'),
                'res_model': 'update.next.service.config',
                'type': 'ir.actions.act_window',
                'view_id': False,
                'view_mode': 'form',
                'view_type': 'form',
                'target': 'new'
            }
        work_order_vals = {}
        for work_order in self:
            # self.env.args = cr, uid, misc.frozendict(context)
            user = self.env.user
            if work_order.odometer == 0:
                raise Warning(_("Please set the current "
                                "Odometer of vehilce in work order!"))
            odometer_increment += work_order.odometer
            next_service_date = datetime.strptime(
                str(date.today()), DEFAULT_SERVER_DATE_FORMAT) + \
                timedelta(days=next_service_day_ids[0].days)
            work_order_vals.update({
                'state': 'done',
                'next_service_odometer': odometer_increment,
                'already_closed': True,
                'closed_by': user,
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
        if work_order.parts_ids:
            parts = self.env['task.line'].search([
                ('fleet_service_id', '=', work_order.id),
                ('is_deliver', '=', False)])
            if parts:
                for part in parts:
                    part.write({'is_deliver': True})
                    source_location = self.env.ref(
                        'stock.picking_type_out').default_location_src_id
                    dest_location, loc = self.env[
                        'stock.warehouse']._get_partner_locations()
                    move = self.env['stock.move'].create({
                        'name': 'Used in Work Order',
                        'product_id': part.product_id.id or False,
                        'location_id': source_location.id or False,
                        'location_dest_id': dest_location.id or False,
                        'product_uom': part.product_uom.id or False,
                        'product_uom_qty': part.qty or 0.0
                    })
                    move._action_confirm()
                    move._action_assign()
                    move.move_line_ids.write({'qty_done': part.qty})
                    move._action_done()
        return True

    def encode_history(self):
        """Method is used to create the Encode Qty.

        History for Team Trip from WO.
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

    def action_reopen(self):
        """Method Action Reopen."""
        for order in self:
            order.write({'state': 'done'})
            new_reopen_service = order.copy()
            new_reopen_service.write({
                'source_service_id': order.id,
                'date_open': False,
                'date_close': False,
                'cost_subtype_id': False,
                'amount': False,
                'team_id': False,
                'closed_by': False,
                'repair_line_ids': [(6, 0, [])],
                'parts_ids': [(6, 0, [])],
            })
            return {
                'view_mode': 'form',
                'view_type': 'form',
                'res_model': 'fleet.vehicle.log.services',
                'type': 'ir.actions.act_window',
                'target': 'current',
                'res_id': new_reopen_service.id,
            }

    @api.depends('parts_ids')
    def _compute_get_total(self):
        for rec in self:
            total = 0.0
            for line in rec.parts_ids:
                total += line.total
            rec.sub_total = total

    def write(self, vals):
        """Method Write."""
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
                        # 'vehicle_location_id': work_order.vehicle_id and
                        # work_order.vehicle_id.vehicle_location_id and
                        # work_order.vehicle_id.vehicle_location_id.id or False,
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
        """Method to send mail."""
        model_obj = self.env['ir.model.data']
        send_obj = self.env['mail.template']
        server_obj = self.env['ir.mail_server']
        res = model_obj.get_object_reference('fleet_operations',
                                             'email_template_edi_fleet')
        record_obj = model_obj.get_object_reference('fleet_operations',
                                                    'ir_mail_server_service')
        self._cr.execute("SELECT id FROM fleet_vehicle WHERE \
                            next_service_date = DATE(NOW()) + 1")
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
        """Method Default get."""
        vehicle_obj = self.env['fleet.vehicle']
        repair_type_obj = self.env['repair.type']
        if self._context.get('active_ids', False):
            for vehicle in vehicle_obj.browse(self._context['active_ids']):
                if vehicle.state == 'write-off':
                    raise Warning(_("You can\'t create work order "
                                    "for vehicle which is already write-off!"))
                elif vehicle.state == 'in_progress':
                    raise Warning(_("Previous work order is not "
                                    "complete,Please complete that work order first than you "
                                    "can create new work order!"))
                elif vehicle.state == 'rent':
                    raise Warning(_("You can\'t create work order "
                                    "for vehicle which is already On Rent!"))
                elif vehicle.state == 'draft' or vehicle.state == 'complete':
                    raise Warning(_("New work order can only be "
                                    "generated either vehicle status is in "
                                    "Inspection or Released!"))
        res = super(FleetVehicleLogServices, self).default_get(fields)
        repair_type_ids = repair_type_obj.search([])
        if not repair_type_ids:
            raise Warning(_("There is no data for "
                            "repair type, add repair type from configuration!"))
        return res

    @api.onchange('cost_subtype_id')
    def get_repair_line(self):
        """Method get repair line."""
        repair_lines = []
        if self.cost_subtype_id:
            for repair_type in self.cost_subtype_id.repair_type_ids:
                repair_lines.append((0, 0, {'repair_type_id': repair_type.id}))
            self.repair_line_ids = repair_lines

    # def _get_open_days(self):
    #     for work_order in self:
    #         diff = 0
    #         if work_order.state == 'confirm':
    #             diff = (datetime.today() -
    #                     datetime.strptime(str(work_order.date_open),
    #                                       DEFAULT_SERVER_DATE_FORMAT)).days
    #             work_order.open_days = str(diff)
    #         elif work_order.state == 'done':
    #             diff = (datetime.strptime(str(work_order.date_close),
    #                                       DEFAULT_SERVER_DATE_FORMAT) -
    #                     datetime.strptime(str(work_order.date_open),
    #                                       DEFAULT_SERVER_DATE_FORMAT)).days
    #             work_order.open_days = str(diff)
    #         else:
    #             work_order.open_days = str(diff)

    def _get_total_parts_line(self):
        for work_order in self:
            total_parts = [parts_line.id
                           for parts_line in work_order.parts_ids
                           if parts_line]
            work_order.total_parts_line = len(total_parts)

    @api.model
    def get_warehouse(self):
        """Method Get Warehouse."""
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
        """Method to check complete date."""
        for vehicle in self:
            if vehicle.date and vehicle.date_complete:
                if vehicle.date_complete < vehicle.date:
                    raise ValidationError('Estimated Date Should Be '
                                          'Greater Than Issue Date.')

    wono_id = fields.Integer(string='WONo',
                             help="Take this field for data migration")
    id = fields.Integer(string='ID')
    purchaser_id = fields.Many2one(
        'res.partner', string='Purchaser', related='vehicle_id.driver_id')
    name = fields.Char(string='Work Order', size=32, readonly=True,
                       translate=True, copy=False, default="New")
    fmp_id = fields.Char(string="Vehicle ID", size=64,
                         related='vehicle_id.name')
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
    etic = fields.Boolean(string='Estimated Time',
                          help="Estimated Time In Completion",
                          default=True)
    wrk_location_id = fields.Many2one('stock.location',
                                      string='Location ', readonly=True)
    wrk_attach_ids = fields.One2many('ir.attachment', 'wo_attachment_id',
                                     string='Attachments')
    task_ids = fields.One2many('service.task', 'main_id',
                               string='Service Task')
    parts_ids = fields.One2many('task.line', 'fleet_service_id',
                                string='Parts')
    note = fields.Text(string='Log Notes')
    date_child = fields.Date(related='cost_id.date', string='Cost Date',
                             store=True)
    sub_total = fields.Float(compute="_compute_get_total", string='Total Parts Amount',
                             store=True)
    state = fields.Selection([('draft', 'New'),
                              ('confirm', 'Open'), ('done', 'Done'),
                              ('cancel', 'Cancel')], string='Status',
                             default='draft', readonly=True)
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    delivery_id = fields.Many2one('stock.picking',
                                  string='Delivery Reference', readonly=True)
    team_id = fields.Many2one('res.partner', string="Teams")
    maintenance_team_id = fields.Many2one("stock.location", string="Team")
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
    # open_days = fields.Char(compute="_get_open_days", string="Open Days")
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
    vechical_location_id = fields.Many2one(related="vehicle_id.vehicle_location_id",
                                           string='Registration State', store=True)
    odometer = fields.Float(compute='_get_odometer', inverse='_set_odometer',
                            string='Last Odometer',
                            help='Odometer measure of the vehicle at the \
                                moment of this log')
    service_amount = fields.Float(
        compute="total_service_amount", string="Total Service Amount")
    source_service_id = fields.Many2one(
        'fleet.vehicle.log.services', string="Service", copy=False)
    invoice_count = fields.Integer(
        compute="count_invoice", string="Invoice Count")
    return_inv_count = fields.Integer(
        compute="return_invoice", string="Return Invoice")
    amount_receive = fields.Boolean(
        compute="invoice_receive", string="Invoice Receive")
    amount_return = fields.Boolean(string="Invoice Return")
    service_invoice_id = fields.One2many('account.move', 'vehicle_service_id',
                                         string="Service Invoice")
    service_ref_invoice_id = fields.One2many('account.move', 'vehicle_service_id',
                                             string="Service Refund Invoice")
    deposit_receive = fields.Boolean(string="Deposit Received?")

    def invoice_receive(self):
        for rec in self:
            inv_obj = self.env['account.move'].search([('type', '=', 'out_invoice'),
                                                       ('vehicle_service_id', '=', rec.id), ('state', '=', [
                                                           'draft', 'paid']),
                                                       ('is_invoice_receive', '=', True)])
            if inv_obj:
                rec.amount_receive = True
            else:
                rec.amount_receive = False

    def count_invoice(self):
        obj = self.env['account.move']
        for serv in self:
            serv.invoice_count = obj.search_count([
                ('type', '=', 'out_invoice'),
                ('vehicle_service_id', '=', serv.id)])

    def return_invoice(self):
        obj = self.env['account.move']
        for serv in self:
            serv.return_inv_count = obj.search_count([
                ('type', '=', 'out_refund'),
                ('vehicle_service_id', '=', serv.id)])

    @api.depends('amount', 'sub_total')
    def total_service_amount(self):
        for rec in self:
            rec.service_amount = rec.sub_total + rec.amount

    def _get_odometer(self):
        fleetvehicalodometer = self.env['fleet.vehicle.odometer']
        for record in self:
            vehicle_odometer = fleetvehicalodometer.search([
                ('vehicle_id', '=', record.vehicle_id.id)], limit=1,
                order='value desc')
            if vehicle_odometer:
                record.odometer = vehicle_odometer.value
            else:
                record.odometer = 0

    def _set_odometer(self):
        fleetvehicalodometer = self.env['fleet.vehicle.odometer']
        for record in self:
            vehicle_odometer = fleetvehicalodometer.search(
                [('vehicle_id', '=', record.vehicle_id.id)],
                limit=1, order='value desc')
            if record.odometer < vehicle_odometer.value:
                raise Warning(_('You can\'t enter odometer less than previous '
                                'odometer %s !') % (vehicle_odometer.value))
            if record.odometer:
                date = fields.Date.context_today(record)
                data = {'value': record.odometer, 'date': date,
                        'vehicle_id': record.vehicle_id.id}
                fleetvehicalodometer.create(data)


class WorkorderPartsHistoryDetails(models.Model):
    """Workorder Parts History Details."""

    _name = 'workorder.parts.history.details'
    _description = 'Workorder Parts History'
    _order = 'used_date desc'

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


class TripPartsHistoryDetails(models.Model):
    """Trip Parts History Details."""

    _name = 'trip.encoded.history'
    _description = 'Trip History'

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

    def _get_available_qty(self):
        for rec in self:
            available_qty = rec.used_qty - rec.dummy_encoded_qty
            if available_qty < 0:
                raise Warning(_('Quantity Available '
                                'must be greater than zero!'))
            rec.available_qty = available_qty

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
                                     string='Dummy Encoded Qty')
    available_qty = fields.Float(compute="_get_available_qty",
                                 string='Qty for Encoding',
                                 help='The Quantity which is available to use')


class TripPartsHistoryDetailsTemp(models.Model):
    """Trip Parts History Details Temp."""

    _name = 'trip.encoded.history.temp'
    _description = 'Trip History Temparery'

    product_id = fields.Many2one('product.product', string='Part No',
                                 help='The Part Number')
    used_qty = fields.Float(string='Used Qty',
                            help='The Quantity that is used in in Workorder')
    work_order_id = fields.Many2one('fleet.vehicle.log.services',
                                    string="Service Order")


class StockPicking(models.Model):
    """Stock Picking."""

    _inherit = 'stock.picking'
    _order = 'id desc'

    work_order_out_id = fields.Many2one('fleet.vehicle.log.services',
                                        string="Work Order ")
    work_order_old_id = fields.Many2one('fleet.vehicle.log.services',
                                        string="Work Order")
    work_order_reopen_id = fields.Many2one('fleet.vehicle.log.services',
                                           string=" Work Order")
    stock_warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    received_by_id = fields.Many2one('res.users', string='Received By')

    @api.model
    def create(self, vals):
        """Overridden create method."""
        if vals.get('origin', False) and vals['origin'][0] == ':':
            vals.update({'origin': vals['origin'][1:]})
        if vals.get('origin', False) and vals['origin'][-1] == ':':
            vals.update({'origin': vals['origin'][:-1]})
        return super(StockPicking, self).create(vals)

    def write(self, vals):
        """Overridden write method."""
        if vals.get('origin', False) and vals['origin'][0] == ':':
            vals.update({'origin': vals['origin'][1:]})
        if vals.get('origin', False) and vals['origin'][-1] == ':':
            vals.update({'origin': vals['origin'][:-1]})
        return super(StockPicking, self).write(vals)

    def do_partial_from_migration_script(self):
        """Do partial from migration script method."""
        assert len(self._ids) == 1, 'Partial picking processing \
                                    may only be done one at a time.'
        stock_move = self.env['stock.move']
        uom_obj = self.env['uom.uom']
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
    """Stock Move."""

    _inherit = 'stock.move'
    _order = 'id desc'

    type = fields.Many2one(related='picking_id.picking_type_id',
                           string='Shipping Type',
                           store=True)
    issued_received_by_id = fields.Many2one('res.users', string='Received By')

    @api.onchange('picking_type_id', 'location_id', 'location_dest_id')
    def onchange_move_type(self):
        """On change of move type gives sorce and destination location."""
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
        location_id = super(StockMove, self)._default_location_source()
        if self._context.get('stock_warehouse_id', False):
            warehouse_pool = self.env['stock.warehouse']
            for rec in warehouse_pool.browse(
                    [self._context['stock_warehouse_id']]):
                if rec.lot_stock_id:
                    location_id = rec.lot_stock_id.id
        return location_id

    @api.model
    def _default_location_destination(self):
        location_dest_id = super(StockMove, self)._default_location_source()
        if self._context.get('stock_warehouse_id', False):
            warehouse_pool = self.env['stock.warehouse']
            for rec in warehouse_pool.browse(
                    [self._context['stock_warehouse_id']]):
                if rec.wh_output_id_stock_loc_id:
                    location_dest_id = rec.wh_output_id_stock_loc_id and \
                        rec.wh_output_id_stock_loc_id.id or False
        return location_dest_id


class FleetWorkOrderSearch(models.TransientModel):
    """Fleet Workorder search model."""

    _name = 'fleet.work.order.search'
    _description = 'Fleet Workorder Search'
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
    work_order_id = fields.Many2one('fleet.vehicle.log.services',
                                    string='Service Order')
    fmp_id = fields.Many2one('fleet.vehicle', string='Vehicle ID')
    cost_subtype_id = fields.Many2one('fleet.service.type',
                                      string='Service Type')
    repair_type_id = fields.Many2one('repair.type', string='Repair Type')
    # open_days = fields.Char(string='Open Days', size=16)
    make_id = fields.Many2one("fleet.vehicle.model.brand", string="Make")
    model_id = fields.Many2one("fleet.vehicle.model", string="Model")

    @api.constrains('issue_date_from', 'issue_date_to')
    def check_issue_date(self):
        """Method to check issue date."""
        for vehicle in self:
            if vehicle.issue_date_to:
                if vehicle.issue_date_to < vehicle.issue_date_from:
                    raise ValidationError('Issue To Date Should Be '
                                          'Greater Than Last Issue From Date.')

    @api.constrains('issue_date_to')
    def check_issue_date(self):
        """Method to check issue date."""
        for vehicle in self:
            if vehicle.issue_date_to:
                raise ValidationError('Please Enter Issue From Date.')

    @api.constrains('open_date_from', 'open_date_to')
    def check_open_date(self):
        """Method to check open date."""
        for vehicle in self:
            if vehicle.open_date_to:
                if vehicle.open_date_to < vehicle.open_date_from:
                    raise ValidationError('Open To Date Should Be '
                                          'Greater Than Open From Date.')

    @api.constrains('close_date_form', 'close_date_to')
    def check_close_date(self):
        """Method to check close date."""
        for vehicle in self:
            if vehicle.close_date_to:
                if vehicle.close_date_to < vehicle.close_date_form:
                    raise ValidationError('Close To Date Should Be '
                                          'Greater Than Close From Date.')

    def get_work_order_detail_by_advance_search(self):
        """Method to get work order detail by advance search."""
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
            # if order.open_days:
            #     wrk_ids = work_order_obj.search([])
            #     if wrk_ids:
            #         for wk_order in wrk_ids:
            #             if wk_order.date_open:
            #                 diff = (datetime.today() -
            #                         wk_order.date_open).days
            #                 if str(diff) == wk_order.open_days:
            #                     order_ids.append(wk_order.id)
            #         order_ids = sorted(set(order_ids))

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
                    or order.fmp_id or order.vehical_division_id:
                    # or \
                    # order.open_days or order.make_id or order.model_id:
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
    """Res Users Model."""

    _inherit = 'res.users'

    usersql_id = fields.Char(string='User ID',
                             help="Take this field for data migration")


class IrAttachment(models.Model):
    """Ir Attachmentmodel."""

    _inherit = 'ir.attachment'

    wo_attachment_id = fields.Many2one('fleet.vehicle.log.services')


class ServiceTask(models.Model):
    """Service Task Model."""

    _name = 'service.task'
    _description = 'Maintenance of the Task '

    main_id = fields.Many2one('fleet.vehicle.log.services',
                              string='Maintanace Reference')
    type = fields.Many2one('fleet.service.type', string='Type')
    total_type = fields.Float(string='Cost', readonly=True, default=0.0)
    product_ids = fields.One2many('task.line', 'task_id', string='Product')
    maintenance_info = fields.Text(string='Information', translate=True)


class TaskLine(models.Model):
    """Task Line Model."""

    _name = 'task.line'
    _description = 'Task Line'

    task_id = fields.Many2one('service.task',
                              string='task reference')
    fleet_service_id = fields.Many2one('fleet.vehicle.log.services',
                                       string='Vehicle Work Order')
    product_id = fields.Many2one('product.product', string='Part')
    qty_hand = fields.Float(string='Qty on Hand',
                            help='Quantity on Hand')
    qty = fields.Float(string='Used', default=1.0)
    product_uom = fields.Many2one('uom.uom', string='UOM')
    price_unit = fields.Float(string='Unit Cost')
    total = fields.Float(string='Total Cost')
    date_issued = fields.Datetime(string='Date issued')
    issued_by = fields.Many2one('res.users', string='Issued By',
                                default=lambda self: self._uid)
    is_deliver = fields.Boolean(string="Is Deliver?")

    @api.constrains('qty', 'qty_hand')
    def _check_used_qty(self):
        for rec in self:
            if rec.qty <= 0:
                raise Warning(_('You can\'t '
                                'enter used quanity as Zero!'))

    @api.onchange('product_id', 'qty')
    def _onchage_product(self):
        for rec in self:
            if rec.product_id:
                prod = rec.product_id
                if prod.in_active_part:
                    rec.product_id = False
                    raise Warning(_('You can\'t select '
                                    'part which is In-Active!'))
                rec.qty_hand = prod.qty_available or 0.0
                rec.product_uom = prod.uom_id or False
                rec.price_unit = prod.list_price or 0.0
            if rec.qty and rec.price_unit:
                rec.total = rec.qty * rec.price_unit

    @api.onchange('price_unit')
    def _onchange_price_unit(self):
        for rec in self:
            if rec.qty and rec.price_unit:
                rec.total = rec.qty * rec.price_unit

    @api.model
    def create(self, vals):
        """
        Overridden create method to add the issuer.

        of the part and the time when it was issued.
        """
        # product_obj = self.env['product.product']
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
                warrnig = 'You can not have duplicate '
                'parts assigned !!!'
                raise Warning(_(warrnig))
        return super(TaskLine, self).create(vals)

    def write(self, vals):
        """
        Overridden write method to add the issuer of the part.

        and the time when it was issued.
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

    @api.onchange('date_issued')
    def check_onchange_part_issue_date(self):
        """Onchange method to check the validation for part issues date."""
        context_keys = self._context.keys()
        if 'date_open' in context_keys and self.date_issued:
            date_open = self._context.get('date_open', False)
            date_open = datetime.strptime(date_open,
                                          DEFAULT_SERVER_DATE_FORMAT)
            current_date = datetime.now().date()
            #
            if not self.date_issued >= date_open and \
                    not self.date_issued <= current_date:
                self.date_issued = False
                raise Warning(_('You can\t enter '
                                'parts issue either open work order date or in '
                                'between open work order date and current date!'))

    def unlink(self):
        """Overridden method to add validation before delete the history."""
        for part in self:
            if part.fleet_service_id.state == 'done':
                raise Warning(_("You can't delete part those already used."))
            if part.is_deliver:
                raise Warning(_("You can't delete part those already used."))
        return super(TaskLine, self).unlink()


class RepairType(models.Model):
    """Repair Type."""

    _name = 'repair.type'
    _description = 'Vehicle Repair Type'

    name = fields.Char(string='Repair Type', size=264,
                       translate=True)

    def copy(self, default=None):
        """Copy method."""
        if not default:
            default = {}
        raise Warning(_('You can\'t duplicate record!'))


class ServiceRepairLine(models.Model):
    """Service Repair Line."""

    _name = 'service.repair.line'
    _description = 'Service Repair Line'

    @api.constrains('date', 'target_date')
    def check_target_completion_date(self):
        """Method to check target compleion date."""
        for vehicle in self:
            if vehicle.issue_date and vehicle.target_date:
                if vehicle.target_date < vehicle.issue_date:
                    raise ValidationError('Target Completion Date Should Be '
                                          'Greater Than Issue Date.')

    @api.constrains('target_date', 'date_complete')
    def check_etic_date(self):
        """Method to check etic date."""
        for vehicle in self:
            if vehicle.target_date and vehicle.date_complete:
                if vehicle.target_date > vehicle.date_complete:
                    raise ValidationError('Repairs target completion date should be '
                                          'less than estimated date.')

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
    """Fleet Service Type."""

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

    def copy(self, default=None):
        """Method copy."""
        if not default:
            default = {}
        raise Warning(_('You can\'t duplicate record!'))
        return super(FleetServiceType, self).copy(default=default)
