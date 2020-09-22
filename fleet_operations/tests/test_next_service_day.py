from odoo.tests.common import TransactionCase


class TestNextServiceDay(TransactionCase):

    def setUp(self):
        super(TestNextServiceDay, self).setUp()

    def test(self):
        next_service_obj = self.env['next.service.days']
        fleet_vehicle = self.env.ref('fleet.vehicle_1')
        self.next_service_day = next_service_obj.create({
                                    'name':'Engine Service',
                                    'vehicle_id':fleet_vehicle.id,
                                    'days':90})