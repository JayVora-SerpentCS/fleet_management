from odoo.tests.common import TransactionCase


class TestRentType(TransactionCase):

    def setUp(self):
        super(TestRentType, self).setUp()

    def test(self):
        self.rent_type_obj = self.env['rent.type'].create({
            							'duration': 3,
            							'renttype': 'Months'
        								})