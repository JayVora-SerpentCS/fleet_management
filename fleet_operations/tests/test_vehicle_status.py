from odoo.tests.common import TransactionCase


class TestVehicleStatus(TransactionCase):

    def setUp(self):
        super(TestVehicleStatus, self).setUp()

    def test(self):
        vehicle_status_obj = self.env['fleet.vehicle.state'].search([('name','=','Registered')])
        self.vehicle_status = vehicle_status_obj.create({
                                'name':vehicle_status_obj.id})