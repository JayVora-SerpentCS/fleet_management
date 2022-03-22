from odoo.tests.common import TransactionCase
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT


class TestVehicleCost(TransactionCase):

    def setUp(self):
        super(TestVehicleCost, self).setUp()

    def test(self):
        # cost_obj = self.env['fleet.vehicle.cost']
        fleet_vehicle = self.env.ref('fleet.vehicle_1')
        service_type_obj = self.env['fleet.service.type']
        cr_dt = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.vehicle_service = service_type_obj.create({
                                'name':'Washing'})
        # self.vehicle_cost = cost_obj.create({
        #                             'vehicle_id':fleet_vehicle.id,
        #                             'date':cr_dt,
        #                             'cost_subtype_id':service_type_obj.id,
        #                             'amount':1000})