from odoo.tests.common import TransactionCase
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT


class TestVehicleOdometer(TransactionCase):

    def setUp(self):
        super(TestVehicleOdometer, self).setUp()

    def test(self):
        odometer_obj = self.env['fleet.vehicle.odometer']
        fleet_vehicle = self.env.ref('fleet.vehicle_1')
        cr_dt = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        driver_obj = self.env['res.partner']

        self.driver = driver_obj.create({
                            'name':'Shivam',
                            'email':'shivam@gmail.com',
                            'phone': 9898981213})
        
        self.vehicle_odometer = odometer_obj.create({
                                        'date':cr_dt,
                                        'vehicle_id':fleet_vehicle.id,
                                        'driver_id':driver_obj.id,
                                        'value':1000})