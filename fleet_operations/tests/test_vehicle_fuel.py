from odoo.tests.common import TransactionCase
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT


class TestVehicleFuel(TransactionCase):

    def setUp(self):
        super(TestVehicleFuel, self).setUp()

    def test(self):
        fuel_obj = self.env['fleet.vehicle.log.fuel']
        fleet_vehicle = self.env.ref('fleet.vehicle_1')
        cr_dt = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        
        self.vehicle_fuel = fuel_obj.create({
                                    'vehicle_id':fleet_vehicle.id,
                                    'current_fuel':5,
                                    'odometer':25000,
                                    'date':cr_dt})