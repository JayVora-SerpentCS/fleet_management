from odoo.tests.common import TransactionCase


class TestVehicleServiceType(TransactionCase):

    def setUp(self):
        super(TestVehicleServiceType, self).setUp()

    def test(self):
        service_type_obj = self.env['fleet.service.type']
        self.service_type = service_type_obj.create({
                                'name':'Test Repair And Maintenance'})