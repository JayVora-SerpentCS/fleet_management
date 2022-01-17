from odoo.tests.common import TransactionCase


class TestVehicleDriver(TransactionCase):

    def setUp(self):
        super(TestVehicleDriver, self).setUp()

    def test(self):
        driver_obj = self.env['res.partner']
        self.driver = driver_obj.create({
                                'name':'Shivam',
                                'email':'shivam@gmail.com',
            'phone': 9898981213})
        

