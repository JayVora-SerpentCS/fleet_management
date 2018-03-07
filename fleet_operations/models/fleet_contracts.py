# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from datetime import datetime
from openerp import models, fields, api, _
from openerp.exceptions import Warning, ValidationError


class fleet_vehicle_log_contract(models.Model):
    _inherit = 'fleet.vehicle.log.contract'

    @api.model
    def create(self, vals):
        vehicle_id = vals.get('vehicle_id', False)
        st_dt = vals.get('start_date', False)
        vehicle_obj = self.env['fleet.vehicle']
        veh_ser_obj = self.env['fleet.vehicle.log.services']
        vehicle_rent = self.env['account.analytic.account']
        vehicle_rec = vehicle_obj.browse(vehicle_id)
        veh_ser_rec = veh_ser_obj.search([('vehicle_id', '=', vehicle_id),
                                          ('date_complete', '>', st_dt)])
        vehicle_rent = vehicle_rent.browse(vehicle_id)
        vehicle_rent_rec = vehicle_rent.search([
            ('vehicle_id', '=', vehicle_id), ('date', '>', st_dt)])
        if vehicle_rec.state == 'in_progress' and veh_ser_rec:
                raise ValidationError('This Vehicle In Service. So You Can Not\
                                        Create Contract For This Vehicle')
        if vehicle_rec.state == 'rent' and vehicle_rent_rec:
                raise ValidationError('This Vehicle In Rent. So You Can Not \
                                        Create Contract For This Vehicle.')
        if vehicle_id and st_dt:
            avil_contracts = self.env['fleet.vehicle.log.contract'].search(
                [('vehicle_id', '=', vehicle_id),
                 ('start_date', '<=', st_dt),
                 ('expiration_date', '>=', st_dt),
                 ('state', '!=', 'closed')])
            if avil_contracts:
                raise ValidationError('This vehicle contract is \
                        already available. You can not create another \
                        contract for this vehicle on same contract date.')
        return super(fleet_vehicle_log_contract, self).create(vals)

    @api.multi
    def write(self, vals):
        vehicle_id = self.vehicle_id.id
#         vehicle = vals.get('vehicle_id')
        st_dt = vals.get('start_date', False)
        vehicle_obj = self.env['fleet.vehicle']
        veh_ser_obj = self.env['fleet.vehicle.log.services']
        vehicle_rent = self.env['account.analytic.account']
        vehicle_rec = vehicle_obj.browse(vehicle_id)
        veh_ser_rec = veh_ser_obj.search([('vehicle_id', '=', vehicle_id),
                                          ('date_complete', '>', st_dt)])
        vehicle_rent = vehicle_rent.browse(vehicle_id)
        vehicle_rent_rec = vehicle_rent.search([
            ('vehicle_id', '=', vehicle_id), ('date', '<', st_dt)])
        if vehicle_rec.state == 'in_progress' and veh_ser_rec:
                raise ValidationError('This Vehicle In Service. So You Can Not\
                                        Create Contract For This Vehicle')
        if vehicle_rec.state == 'rent' and vehicle_rent_rec:
                raise ValidationError('This Vehicle In Rent. So You Can Not \
                                        Create Contract For This Vehicle.')
        if vehicle_id and st_dt:
            avil_contracts = self.env['fleet.vehicle.log.contract'].search(
                [('vehicle_id', '=', vehicle_id),
                 ('start_date', '<=', st_dt),
                 ('expiration_date', '>=', st_dt),
                 ('state', '!=', 'closed')])
            if avil_contracts:
                raise ValidationError('This vehicle contract is \
                        already available. You can not create another \
                        contract for this vehicle on same contract date.')
        return super(fleet_vehicle_log_contract, self).write(vals)

    @api.model
    def default_get(self, fields):
        res = super(fleet_vehicle_log_contract, self).default_get(fields)
        res.update({'state': 'draft'})
        return res

#     @api.multi
#     def action_cancel(self):
#         for rec in self:
#             rec.state = 'cancel'

    @api.multi
    def action_close(self):
        for rec in self:
            rec.state = 'toclose'

    @api.multi
    def action_confirm(self):
        seq = self.env['ir.sequence'].next_by_code('vehicle.contract.sequnce')
        for contract in self:
            contract.write({
                            'state': 'confirm',
                            'contract_no': seq})

    @api.multi
    def scheduler_manage_auto_costs(self):
        res = super(fleet_vehicle_log_contract,
                    self).fleet_vehicle_log_contract()
        return res

    @api.multi
    def action_work_order_create(self):
        fvls_obj = self.env['fleet.vehicle.log.services']
        fvls_dict = {}
        for contract in self:
            fvls_dict['vehicle_id'] = contract.vehicle_id and \
                                contract.vehicle_id.id or False
#            log_res = fvls_obj.on_change_vehicle(cr, uid, ids,
#                                contract.vehicle_id.id)
#            fvls_dict['purchaser_id'] = log_res['value']['purchaser_id']
            fvls_dict['vendor_id'] = contract.insurer_id and \
                contract.insurer_id.id or False
            fvls_dict['date'] = contract.date or False
            fvls_dict['odometer'] = contract.odometer
            fvls_dict['fvlc_id'] = contract.id,
            work_order = fvls_obj.create(fvls_dict)
            contract.work_order = work_order or ''
        return True

    @api.multi
    def action_job_card_create(self):
        job_card_obj = self.env['job.card']
        job_vals_dict = {}
        for contract in self:
            job_vals_dict['vehicle_id'] = contract.vehicle_id and \
                            contract.vehicle_id.id or False
            job_vals_dict['customer_id'] = contract.insurer_id and \
                contract.insurer_id.id or False
            job_vals_dict['date_scheduled'] = contract.start_date or False
            job_vals_dict['date_complete'] = contract.date or False
            job_vals_dict['odometer'] = contract.odometer
            job_vals_dict['fvlc_id_ref'] = contract.id or False
            job_number = job_card_obj.create(job_vals_dict)
            contract.job_number = job_number or ''
        return True

    @api.model
    def contract_email_send(self):
        email_cc = []
        template_obj = self.env['email.template']
        model_obj = self.env['ir.model.data']
        res_obj = self.env['res.groups']
        res = model_obj.get_object_reference('fleet_operations',
                                             'email_template_edi_contract')
        server_obj = self.env['ir.mail_server']
        record_obj = model_obj.get_object_reference('fleet_operations',
                                                    'ir_mail_server_service')
        self._cr.execute("select id from fleet_vehicle_log_contract where \
            expiration_date between DATE(NOW()) and DATE(NOW()) + 7")
        contract_ids = [i[0]for i in self._cr.fetchall()]
        email_from_brw = server_obj.browse(record_obj[1])
        result_id = res_obj.search([('category_id', '=', 'Fleet'),
                                    ('name', '=', 'Manager')], limit=1)
        if res:
            tmp_id = template_obj.browse(res[1])

        for rec in self.browse(contract_ids):
            email_from = email_from_brw.smtp_user
            if not email_from:
                raise Warning(_("Warning"), _("May be Out Going Mail \
                                    server is not configuration."))

            for data in result_id:
                for line in data.users:
                    manager_email = line.email
                    email_cc.append(str(manager_email))

            if contract_ids:
                tmp_id.send_mail(rec.id, force_send=True)
        return True

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
                              _('You can\'t enter odometer less than previous \
                               odometer %s !') % (vehicle_odometer.value))
            if record.odometer:
                date_dt = fields.Date.context_today(record)
                data = {'value': record.odometer, 'date': date_dt,
                        'vehicle_id': record.vehicle_id.id}
                FleetVehicalOdometer.create(data)

    @api.constrains('date')
    def check_invoice_date(self):
        for vehicle in self:
            if vehicle.date:
                if vehicle.date < vehicle.start_date:
                    raise ValidationError('Contract Invoice Date Should Be \
                    Greater Than Start Date.')

    @api.constrains('expiration_date')
    def check_expiration_date(self):
        for vehicle in self:
            if vehicle.expiration_date:
                if vehicle.expiration_date < vehicle.start_date:
                    raise ValidationError('Contract End Date Should Be \
                    Greater Than Start Date.')

    @api.constrains('start_date')
    def check_start_date(self):
        for vehicle in self:
            if vehicle.start_date:
                dt = datetime.now().date()
                dt_str = dt.strftime('%Y-%m-%d')
                if vehicle.start_date < dt_str:
                    raise ValidationError('Contract Start Date Should Be \
                    Greater Than Current Date.')

    @api.v7
    def on_change_vehicle(self, cr, uid, ids, vehicle_id, context=None):
        if not vehicle_id:
            return {}
        odometer = \
            self.pool.get('fleet.vehicle').browse(cr, uid, vehicle_id,
                                                  context=context).odometer
        return {
            'value': {
                'odometer': odometer,
            }
        }

    _rec_name = 'contract_no'

    odometer = fields.Float(
        compute='_get_odometer',
        inverse='_set_odometer',
        string='Last Odometer',
        help='Odometer measure of the vehicle at the moment of this log')
    odometer_unit = fields.Selection(
        related='vehicle_id.odometer_unit',
        help='Unit of the odometer ')
    name = fields.Char(string='Name', size=32, translate=True)
    work_order = fields.Many2one('fleet.vehicle.log.services',
                                 string='Work Order Reference', readonly=True)
    contract_no = fields.Char(string="Contract No", size=32, readonly=True,
                              translate=True)
    state = fields.Selection([('draft', 'Draft'), ('open', 'In Progress'),
                              ('confirm', 'Confirm'), ('toclose', 'To Close'),
                              ('closed', 'Terminated')], string='Status',
                             readonly=True, default='draft',
                             help='Choose whether the contract is still \
                                    valid or not')

#     state = fields.Selection([('draft', 'Draft'), ('open', 'In Progress'),
#                           ('confirm', 'Confirm'), ('toclose', 'To Close'),
#                           ('closed', 'Terminated'), ('cancel', 'Cancel')],
#                              string='Status', readonly=True, default='draft',
#                              help='Choose whether the contract is still \
#                                     valid or not')
    job_number = fields.Many2one('job.card', string='Job card Reference',
                                 readonly=True)
