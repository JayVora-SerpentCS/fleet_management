from odoo.tests.common import TransactionCase


class TestVehicleDamageType(TransactionCase):

    def setUp(self):
        super(TestVehicleDamageType, self).setUp()

    def test(self):
        damage_type_obj = self.env['damage.types']
        self.vehicle_damage_type = damage_type_obj.create({
                                            'name':'Interior',
                                            'code':'DT00017'})