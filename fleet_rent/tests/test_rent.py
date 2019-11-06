# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo.tests.common import TransactionCase
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT


class TestRent(TransactionCase):

    def setUp(self):
        super(TestRent, self).setUp()

    def test(self):
        self.vehicle_obj = self.env['fleet.vehicle']
        fleet_brand = self.env.ref('fleet.brand_audi')
        fleet_model = self.env.ref('fleet.model_a1')
        self.rent_obj = self.env['fleet.rent']
        tenant_id = self.env.ref('base.user_admin')
        self.rent_type_obj = self.env['rent.type']
        cr_dt = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        self.vehicle = self.vehicle_obj.create({
            'f_brand_id': fleet_brand.id,
            'model_id': fleet_model.id,
            'license_plate': 'MH-04-7777',
            'odometer': 3000,
            'odometer_unit': 'kilometers',
            'fuel_type': 'diesel'
        })
        self.rent_type_id = self.rent_type_obj.create({
            'duration': 1,
            'renttype': 'Months'
        })
        self.rent = self.rent_obj.create({
            'name': 'Test Rent',
            'vehicle_id': self.vehicle.id,
            'tenant_id': tenant_id.id,
            'ten_date': cr_dt,
            'rent_type_id': self.rent_type_id.id
        })
