# See LICENSE file for full copyright and licensing details.

from datetime import datetime

from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


@tagged("-standard", "fleet_rent")
class TestRent(TransactionCase):
    def setUp(self):
        super(TestRent, self).setUp()
        self.vehicle_obj = self.env["fleet.vehicle"]
        self.fleet_brand = self.env.ref("fleet.brand_audi")
        self.fleet_model = self.env.ref("fleet.model_a1")
        self.rent_obj = self.env["fleet.rent"]
        self.tenant_id = self.env.ref("base.user_admin")
        self.rent_type_obj = self.env["rent.type"]
        self.cr_dt = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.date_end = self.rent_obj._compute_create_date()
        self.rent_schedule = self.rent_obj.create_rent_schedule()
        self.vehicle_owner = self.rent_obj._compute_change_vehicle_owner()
        self.vehicle_odometer = self.rent_obj.change_odometer()

    def test_create_fleet_rent(self):

        self.vehicle = self.vehicle_obj.create(
            {
                "f_brand_id": self.fleet_brand.id,
                "model_id": self.fleet_model.id,
                "license_plate": "MH-04-7777",
                "odometer": 3000,
                "odometer_unit": "kilometers",
                "fuel_type": "diesel",
            }
        )
        self.rent_type_id = self.rent_type_obj.create(
            {"duration": 1, "renttype": "Months"}
        )
        self.rent = self.rent_obj.create(
            {
                "name": "Test Rent",
                "vehicle_id": self.vehicle.id,
                "tenant_id": self.tenant_id.id,
                "rent_type_id": self.rent_type_id.id,
                "rent_amt": 1000,
                "deposit_amt": 100,
                "date_end": self.date_end,
            }
        )

        self.rent_type_obj = self.rent_type_obj.create(
            {"duration": 3, "renttype": "Months"}
        )
