from odoo.tests.common import TransactionCase
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT,DEFAULT_SERVER_DATETIME_FORMAT


class TestRegistration(TransactionCase):

    def setUp(self):
        super(TestRegistration, self).setUp()

    def test(self):
        self.vehicle_obj = self.env['fleet.vehicle']
        fleet_brand = self.env.ref('fleet.brand_audi')
        fleet_model = self.env.ref('fleet.model_a1')
        vehicle_type_obj = self.env['vehicle.type']
        vehicle_color_obj = self.env['color.color']
        registration_state_obj = self.env['res.country.state']
        driver_obj = self.env['res.partner']
        cr_dt = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        driver_no = self.vehicle_obj.get_driver_id_no()

        vehicle_registration_state = registration_state_obj.search([('name','=', 'Gujarat')])            
       
        vehicle_color = vehicle_color_obj.search([('name','=','BLACK')])
        vehicle_type = vehicle_type_obj.search([('name','=','Car')])
                                       
        self.driver = driver_obj.create({
                            'name':'Shivam',
                            'email':'shivam@gmail.com'})
        self.vehicle = self.vehicle_obj.create({
                                'f_brand_id': fleet_brand.id,
                                'model_id': fleet_model.id,
                                'license_plate': 'MH-04-7777',
                                'odometer': 3000,
                                'odometer_unit': 'kilometers',
                                'fuel_type': 'diesel',
                                'vechical_type_id':vehicle_type_obj.id,
                                'vehical_color_id':vehicle_color.id,
                                'vehicle_location_id':vehicle_registration_state.id,
                                'driver_id':driver_obj.id,
                                'engine_no':'ABC09X5',
                                'transmission':'manual',
                                'acquisition_date':cr_dt,
                                'start_date_insurance':cr_dt,
                                'end_date_insurance':cr_dt})