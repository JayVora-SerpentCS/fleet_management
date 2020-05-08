from odoo.tests.common import TransactionCase


class TestVehicleModel(TransactionCase):

    def setUp(self):
        super(TestVehicleModel, self).setUp()

    def test(self):
        self.vehicle_obj = self.env['fleet.vehicle.model']
        fleet_brand = self.env['fleet.vehicle.model.brand'].create({
                                                    'name':'i20'})

        self.vehicle = self.vehicle_obj.create({
                                'name':'suzuki',
                                'brand_id':fleet_brand.id})