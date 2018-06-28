# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo.tests.common import TransactionCase


class TestRegistration(TransactionCase):

    def setUp(self):
        super(TestRegistration, self).setUp()

    def test(self):
        self.vehicle_obj = self.env['fleet.vehicle']
        fleet_brand = self.env.ref('fleet.brand_audi')
        fleet_model = self.env.ref('fleet.model_a1')
        self.vehicle = self.vehicle_obj.create({
                                'f_brand_id': fleet_brand.id,
                                'model_id': fleet_model.id,
                                'license_plate': 'MH-04-7777',
                                'odometer': 3000,
                                'odometer_unit': 'kilometers',
                                'fuel_type': 'diesel'})