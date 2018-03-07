# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from datetime import datetime, date
from openerp import models, fields, api, _
from openerp.tools import misc
from openerp.exceptions import Warning


class job_card(models.Model):
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _name = 'job.card'
    _description = 'Job card related Vehicle'

    @api.multi
    def action_confirm(self):
        for job_card in self:
            if not job_card.maintain_line:
                raise Warning(("Error!"), ("You can not confirm Job card \
                                    order Which has no Line"))
            job_card.write({
                'state': 'confirm',
                'job_number': self.env['ir.sequence'].next_by_code(
                                            'job.card.sequence')})
        return True

    @api.multi
    def action_done(self):
        sale_order_pool = self.env['sale.order']
        res = {}
        sale_order_dict = {}
        for job_card in self:
            vehicle_rec = job_card.vehicle_id
            curr_date = datetime.strptime(str(date.today()), '%Y-%m-%d')
            from_date = vehicle_rec.warranty_period and \
                datetime.strptime(vehicle_rec.warranty_period,
                                  '%Y-%m-%d') or False
            if from_date and from_date >= curr_date:
                wrk_vals = {'state': 'done'}
            else:
                partner_id = job_card.customer_id and \
                            job_card.customer_id.id or False
                res = sale_order_pool.onchange_partner_id(partner_id)
                sale_order_dict['partner_id'] = partner_id
                sale_order_dict['partner_shipping_id'] = \
                    res['value']['partner_shipping_id']
                sale_order_dict['partner_invoice_id'] = \
                    res['value']['partner_invoice_id']
                sale_order_dict['pricelist_id'] = \
                    int(res['value']['pricelist_id'])
                sale_order_dict['order_line'] = []
                sale_order_dict['origin'] = job_card.job_number
                sale_order_line = []
                for task in job_card.maintain_line:
                    taxes = []
                    if job_card.job_part_tax_ids:
                        taxes.append(
                            (6, 0, [tax.id for tax in job_card.job_part_tax_ids
                                    ]))
                    for product in task.product_line:
                        sale_order_line.append((0, 0, {
                                'product_uom_qty': product.qty,
                                'product_id': product.product_id.id,
                                'product_uom': product.product_uom.id,
                                'price_unit': product.price_unit,
                                'name': product.product_id.name,
                                'tax_id': taxes or [],
                                'delay': 0.00}))
                sale_order_dict['order_line'] = sale_order_line
                sale_order_id = sale_order_pool.create(sale_order_dict)

                sale_order_id.action_button_confirm()
                invoice_id = sale_order_id.manual_invoice()
                if invoice_id:
                    inv_rec = self.env['account.invoice'].browse(
                                                 invoice_id['res_id'])
                    inv_rec.signal_workflow('invoice_open')
                wrk_vals = {'state': 'done',
                            'sale_order': sale_order_id.id or '',
                            'invoice': inv_rec.id or ''}
            job_card.write(wrk_vals)
            self.create_vehicle_cost()
        return res

    @api.onchange('company_id')
    def onchange_is_company(self):
        if self.company_id and self.company_id.partner_id:
            self.customer_id = self.company_id.partner_id

    @api.multi
    def create_vehicle_cost(self):
        vehicle_cost_obj = self.env['fleet.vehicle.cost']
        for job_card in self:
            for task in job_card.maintain_line:
                cost_order_dict = {
                    'vehicle_id': job_card.vehicle_id.id,
                    'amount': job_card.total,
                    'date': job_card.date_scheduled,
                    'cost_subtype_id': task.type.id
                }
            cost_order_id = vehicle_cost_obj.create(cost_order_dict)
            return cost_order_id

    @api.multi
    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.multi
    def get_total(self):
        final_total = 0.0
        total = 0.0
        for rec in self:
            for line in rec.maintain_line:
                for data in line.product_line:
                    if data.task_id:
                        final_total = final_total + data.total
                        total = final_total
                        rec.part = total

    @api.multi
    def main_total(self):
        for rec in self:
            main_total = rec.part + rec.total_tax_amount
            rec.total = main_total

    @api.multi
    def _get_tax_amount(self):
        final_total = 0.0
        taxes = []
        for rec in self:
            if rec.maintain_line:
                for line in rec.maintain_line:
                    if rec.job_part_tax_ids:
                        for data in line.product_line:
                            taxes .append(
                              rec.job_part_tax_ids.compute_all(
                                               data.price_unit, data.qty))
            if taxes:
                for tax in taxes:
                    for tax_data in tax['taxes']:
                        final_total += tax_data['amount']
                rec.total_tax_amount = final_total
            else:
                rec.total_tax_amount = 0.0

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
                raise Warning(_('User Error!'),
                              _('You can\'t enter odometer less than previous\
                               odometer %s !') % (vehicle_odometer.value))
            if record.odometer:
                date = fields.Date.context_today(record)
                data = {'value': record.odometer, 'date': date,
                        'vehicle_id': record.vehicle_id.id}
                FleetVehicalOdometer.create(data)

    _rec_name = 'job_number'

    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle',
                                 required=True)
    customer_id = fields.Many2one('res.partner', string='Customer',
                                  domain=[('customer', '=', True)])
    job_number = fields.Char(string='Job Card Order', size=32, readonly=True)
    odometer_id = fields.Many2one('fleet.vehicle.odometer', string='Odometer',
                                  help='Odometer measure of the vehicle \
                                          at the moment of this log')
    date_scheduled = fields.Date(string='Scheduled Date ', required=True,
                                 help='Date when the service is scheduled')
    date_complete = fields.Date(string='Issued Complete ', required=True,
                                help='Date when the service is completed')
    odometer = fields.Float(compute="_get_odometer", inverse='_set_odometer',
                            string='Odometer')
    type = fields.Selection([('service', 'Service'),
                             ('repairing', 'Repairing'),
                             ('service_repair', 'Service & Repairing')],
                            string='Job Card Types')
    priority = fields.Selection([('normal', 'NORMAL'), ('high', 'HIGH'),
                                 ('low', 'LOW')], string='Work Priority',
                                default='normal')
    sale_order = fields.Many2one('sale.order', string='SO#',
                                 readonly=True)
    invoice = fields.Many2one('account.invoice', string='Invoice #',
                              readonly=True)
    note = fields.Text(string='Notes', translate=True)
    part = fields.Float(compute="get_total", string='Parts', store=True)
    job_part_tax_ids = fields.Many2many('account.tax', 'job_part_order_tax',
                                        'job_part_order_id', 'tax_id',
                                        string='Taxes')
    total_tax_amount = fields.Float(compute="_get_tax_amount", string="Taxes",
                                    store=True)
    total = fields.Float(compute="main_total", string='Total')
    maintain_line = fields.One2many('job.maintenance.task', 'main_id',
                                    string='Maintenance Task')
    job_order_attach_ids = fields.One2many('ir.attachment',
                                           'jobcard_attachment_id',
                                           string='Attachments')
    is_comp_vehicle = fields.Boolean(string='Is Company Vehicle?')
    company_id = fields.Many2one('res.company', string='Company',
                                 default=lambda self: self.env['res.company'].
                                 _company_default_get('job.card'),
                                 required=True)
    fvlc_id_ref = fields.Many2one('fleet.vehicle.log.contract',
                                  string='Contract Order Reference',
                                  readonly=True)
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'),
                              ('done', 'Done'), ('cancel', 'Cancel')],
                             string='Status', default="draft", readonly=True)

    @api.multi
    def action_quotation_send(self):
        '''
        This function opens a window to compose an email,
        with the edi sale template message loaded by default
        '''
        assert len(self._ids) == 1, 'This option should only be used \
                                        for a single id at a time.'
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = \
                ir_model_data.get_object_reference(
                    'job_card', 'email_template_edi_sale')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = \
                ir_model_data.get_object_reference(
                    'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        cr, uid, context = self.env.args
        ctx = dict(context)
        ctx.update({
            'default_model': 'job.card',
            'default_res_id': self._ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        self.env.args = cr, uid, misc.frozendict(context)
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }


class ir_attachment(models.Model):
    _inherit = 'ir.attachment'

    jobcard_attachment_id = fields.Many2one('job.card',
                                            string="Job Card Attachment")


class job_maintenance_task(models.Model):
    _name = 'job.maintenance.task'
    _description = 'Maintenance of the Task '

    main_id = fields.Many2one('job.card', string='Maintenance Reference')
    type = fields.Many2one('fleet.service.type', string='Type')
    task_total = fields.Float(string='Cost', readonly=True)
    product_line = fields.One2many('job.maintenance.line', 'task_id',
                                   string='Product')
    jobcard_maintenance_info = fields.Text(string='Information',
                                           translate=True)


class job_maintenance_line(models.Model):

    @api.multi
    def _amount_line(self):
        for line in self:
            price = line.price_unit * line.qty
            line.total = price

    _name = 'job.maintenance.line'

    task_id = fields.Many2one('job.maintenance.task', string='task reference')
    product_id = fields.Many2one('product.product', string='Product',
                                 required=True)
    qty = fields.Float(string='Qty', required=True, default=1.0)
    product_uom = fields.Many2one('product.uom', string='Unit of Measure ',
                                  required=True)
    price_unit = fields.Float(string='Unit Price', required=True)
    total = fields.Float(compute="_amount_line", string='Sub Total')

    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            prod = self.product_id
            self.price_unit = prod.list_price
            self.product_uom = prod.uom_id and prod.uom_id.id or False
