# See LICENSE file for full copyright and licensing details.
"""Repair Line Summary."""

from odoo import api, fields, models
from odoo.exceptions import ValidationError, Warning


class UpdateNextServiceConfig(models.TransientModel):
    """Added Next Service and Odometer Increment."""

    _name = 'update.next.service.config'
    _description = 'Update Next Service configuration'

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle Id")
    number = fields.Float(string="Odometer Increment")
    days = fields.Integer(string="Days")

    def action_done(self):
        """Method to set Next Service Day and Odometer Increment."""
        next_service_obj = self.env['next.service.days']
        service_obj = self.env['fleet.vehicle.log.services']
        incre_obj = self.env['next.increment.number']
        service_active_id = service_obj.browse(self._context['active_id'])
        if self.days <= 0:
            raise ValidationError('Next service days must be greater than zero !')

        next_days = {
            'vehicle_id': self.vehicle_id and self.vehicle_id.id or False,
            'days': self.days
        }
        next_ser_configs = self.env['next.service.days'].search([('vehicle_id','=',self.vehicle_id.id)])
        if not next_ser_configs:
            next_service_obj.create(next_days)

        next_odometer = {
            'vehicle_id': self.vehicle_id and self.vehicle_id.id or False,
            'number': self.number
        }
        next_incree_configs = self.env['next.increment.number'].search([('vehicle_id','=',self.vehicle_id.id)])
        if not next_incree_configs:
            incre_obj.create(next_odometer)

        service_active_id.action_done()

    @api.model
    def default_get(self, default_fields):
        """Method is used to set Vehicle Id."""
        res = super(UpdateNextServiceConfig, self).default_get(default_fields)
        serv_obj = self.env['fleet.vehicle.log.services']
        service = serv_obj.browse(self._context['active_id'])
        if service:
            res.update({
                'vehicle_id': service.vehicle_id and service.vehicle_id.id or False,
            })
        return res
