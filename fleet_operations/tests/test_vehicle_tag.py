from odoo.tests.common import TransactionCase


class TestVehicleTag(TransactionCase):

    def setUp(self):
        super(TestVehicleTag, self).setUp()

    def test(self):
        vehicle_tag_obj = self.env['fleet.vehicle.tag']
        vehicle_tag = vehicle_tag_obj.search([('name','=','Break')])
        self.tag = vehicle_tag_obj.create({
                                'name':vehicle_tag.id})