# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from openerp import models, api


class ir_rule(models.Model):
    _inherit = 'ir.rule'

    @api.model
    def disable_manager_record_rule(self):
        """
        It will inactive the base record rule.
        """
        self.env.ref('fleet.fleet_user_contract_visibility_manager').write({
                                                        'domain_force': []})
        self.env.ref('fleet.fleet_user_cost_visibility_manager').write({
                                                        'domain_force': []})
        self.env.ref('fleet.fleet_user_service_visibility_manager').write({
                                                        'domain_force': []})
        self.env.ref('fleet.fleet_user_odometer_visibility_manager').write({
                                                        'domain_force': []})
        self.env.ref('fleet.fleet_user_fuel_log_visibility_manager').write({
                                                        'domain_force': []})
        self.env.ref('fleet.fleet_user_vehicle_visibility_manager').write({
                                                        'domain_force': []})
        return True
