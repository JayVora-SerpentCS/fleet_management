from odoo.tests.common import TransactionCase


class TestVehicleRepairType(TransactionCase):

    def setUp(self):
        super(TestVehicleRepairType, self).setUp()

    def test(self):
        repair_type_obj = self.env['repair.type']
        self.repair_type = repair_type_obj.create({
                                'name':'Test Engine Repair'})