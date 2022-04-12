from odoo.tests.common import TransactionCase


class TestVehicleColor(TransactionCase):

    def setUp(self):
        super(TestVehicleColor, self).setUp()

    def test(self):
        vehicle_color_obj = self.env['color.color']
        vehicle_color = vehicle_color_obj.search([('name','=','BLACK')], limit=1)
        self.color = vehicle_color_obj.create({
                                'name':vehicle_color.id})