# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class FleetVehicleExtend(models.Model):
    _inherit = 'fleet.vehicle'

    @api.multi
    def return_action_for_open(self):
        """ This opens the xml view specified in xml_id \
        for the current vehicle """
        self.ensure_one()
        xml_id = self.env.context.get('xml_id')
        if xml_id:
            res = self.env['ir.actions.act_window'].for_xml_id(
                                            'fleet_rent', xml_id)
            res.update(
                context=dict(self.env.context,
                             default_vehicle_id=self.id, group_by=False),
                domain=[('vehicle_id', '=', self.id)]
            )
            return res
        return False

    def _count_rent(self):
        """ This method count the total number of \
        rent for the current vehicle """
        Rent = self.env['account.analytic.account']
        for record in self:
            record.rent_count = \
                Rent.search_count([('vehicle_id', '=', record.id)])

    income_acc_id = fields.Many2one("account.account",
                                    string="Income Account")
    expence_acc_id = fields.Many2one("account.account",
                                     string="Expense Account")
    rent_count = fields.Integer(compute='_count_rent',
                                string="Rents")
