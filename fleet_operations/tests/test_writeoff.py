# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo.tests.common import TransactionCase
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT


class TestWriteOff(TransactionCase):

    def setUp(self):
        super(TestWriteOff, self).setUp()

    def test(self):
        self.vehicle_obj = self.env['fleet.vehicle']
        fleet_brand = self.env.ref('fleet.brand_audi')
        fleet_model = self.env.ref('fleet.model_a1')
        self.writeoff_obj = self.env['fleet.wittenoff']
        cr_dt = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)

        self.vehicle = self.vehicle_obj.create({
                                'f_brand_id': fleet_brand.id,
                                'model_id': fleet_model.id,
                                'license_plate': 'MH-04-7777',
                                'odometer': 3000,
                                'odometer_unit': 'kilometers',
                                'fuel_type': 'diesel'})
        self.writeoff = self.writeoff_obj.create({
                                'vehicle_id': self.vehicle.id,
                                'cost_esitmation': 2000,
                                'write_off_type': 'general_accident',
                                'report_date': cr_dt})
