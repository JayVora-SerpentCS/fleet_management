from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


@tagged("post_install", "fleet_operation", "-at_install")
class TestOperation(TransactionCase):

    def setUp(self):
        super(TestOperation, self).setUp()
        self.create_make = self.env['fleet.vehicle.model.brand']
        self.create_model = self.env['fleet.vehicle.model']
        self.create_vehicle_type = self.env['vehicle.type']
        self.create_res_user = self.env['res.users']
        self.create_vehicle = self.env['fleet.vehicle']
        self.create_product_template = self.env['product.template']
        self.create_fleet_vehicle_log_services = self.env['fleet.vehicle.log.services']
        self.damage_type_obj = self.env['damage.types']
        self.next_service_obj = self.env['next.service.days']
        self.repair_type_obj = self.env['repair.type']
        self.service_type_obj = self.env['fleet.service.type']
        self.vehicle_color_obj = self.env['color.color']
        self.workshop_id = self.env.ref('base.res_partner_1')
        self.registration_state_obj = self.env['res.country.state']
        self.odometer_obj = self.env['fleet.vehicle.odometer']
        self.driver_obj = self.env['res.partner']
        self.update_engine_info = self.env['update.engine.info']
        self.update_color_info = self.env['update.color.info']
        self.update_vin_info = self.env['update.vin.info']
        self.update_tire_info = self.env['update.tire.info']
        self.update_battery_info = self.env['update.battery.info']


        self.cr_dt = datetime.today().strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        self.create_fleet_work_order_search = self.env['fleet.work.order.search']
        
        self.vehicle_registration_state = self.registration_state_obj.search(
            [('name', '=', 'Gujarat')])
        self.vehicle_color = self.vehicle_color_obj.search(
            [('name', '=', 'BLACK')])

    def test_vehicle_operation(self):

        # create car maker
        self.create_make_1 = self.create_make.create({
            'name': 'RJ Makers'
        })
        self.assertTrue(self.create_make_1, 'Vehicle Maker not create')

        # create vehicle type
        self.create_vehicle_type_1 = self.create_vehicle_type.create({
            'name': 'type super car'
        })
        self.assertTrue(self.create_vehicle_type_1, 'Vehicle type not create')

        # create car model
        self.create_model_1 = self.create_model.create({
            'name': 'RJ A1 Model',
            'brand_id': self.create_make_1.id,
            'vehicle_type': 'car',
            'default_fuel_type': 'lpg',

        })
        self.assertTrue(self.create_model_1, 'Vehicle model not create')

        # create owner for vehicle
        self.create_res_user_owner_1 = self.create_res_user.create({
            'name': 'owner Raj',
            'login': 'login raj',
            'email': 'rajowner@gamil.com',
        })
        self.assertTrue(self.create_res_user_owner_1,
                        'Vehicle owner not create')

        # create vehicle
        self.create_vehicle_1 = self.create_vehicle.create({
            'f_brand_id': self.create_make_1.id,
            'model_id': self.create_model_1.id,
            'vehicle_owner': self.create_res_user_owner_1.id,
            'fuel_type': self.create_model_1.default_fuel_type,
            'license_plate': 'MH-04-7777',
            'odometer': 3000,
            'odometer_unit': 'kilometers',
            'engine_no': 'ABC09X5',
            'transmission': 'manual',
            'acquisition_date': self.cr_dt,
            'start_date_insurance': self.cr_dt,
            'end_date_insurance': self.cr_dt,
            'vehical_color_id': self.vehicle_color.id,
            'vehicle_location_id': self.vehicle_registration_state.id,
        })
        self.assertTrue(self.create_vehicle_1, 'Vehicle not create')

        # Create workorder for update or change vehicle infomation or vehicle services
        self.workorder = self.create_fleet_vehicle_log_services.create({
                                'vehicle_id': self.create_vehicle_1.id,
                                # 'cost_subtype_id': service_cost_id.id,
                                'fmp_id' : self.create_vehicle_1.id,
                                'amount': 2000,
                                'priority': 'normal',
                                'date_complete': self.cr_dt,
                                'team_id': self.workshop_id.id
                                })

        self.workorder.action_confirm()

        # Update Engine base on workorder 
        self.update_engine_info_1 = self.update_engine_info.create({
            'workorder_id' : self.workorder.id,
            'new_engine_no' : 'ENG-NEW-2022',
            'note' : 'change new engine',
            'vehicle_id' : self.create_vehicle_1.id,

        })
        self.assertTrue(self.update_engine_info_1, 'Engine info not update')

        # Update Color info
        self.update_color_info_1 = self.update_color_info.create({
            'workorder_id' : self.workorder.id,
            'vehicle_id' : self.create_vehicle_1.id,
            'note' : 'change color',
            'current_color_id' : self.vehicle_color.id,

        })
        self.assertTrue(self.update_engine_info_1, 'Color info not update')

        # Update Tire info
        self.update_tire_info_1 = self.update_tire_info.create({
            'workorder_id' : self.workorder.id,
            'vehicle_id' : self.create_vehicle_1.id,
            'note' : 'change tire info',
            'new_tire_size' : 'S3',
            'new_tire_sn' : 'SN',
            'new_tire_issue_date' : self.cr_dt,

        })
        self.assertTrue(self.update_engine_info_1, 'Tire info not update')

        # Update Battery Info
        self.update_battery_info_1 = self.update_battery_info.create({
            'workorder_id' : self.workorder.id,
            'vehicle_id' : self.create_vehicle_1.id,
            'note' : 'change battery info',
            'new_battery_size' : 'NB2',
            'new_battery_sn' : 'N SN',
            'new_battery_issue_date' :  self.cr_dt,
        })
        self.assertTrue(self.update_engine_info_1, 'Battert info not update')

        # create damage type
        self.vehicle_damage_type = self.damage_type_obj.create({
            'name': 'Interior',
            'code': 'DT00017'})
        self.assertTrue(self.vehicle_damage_type, 'Vehicle damage type not create')

        # create next service day
        self.next_service_day = self.next_service_obj.create({
            'name': 'Test Engine Service',
            'vehicle_id': self.create_vehicle_1.id,
            'days': 90})
        self.assertTrue(self.next_service_day, 'Next Vehicle Service day not create')

        # create repair type
        self.repair_type = self.repair_type_obj.create({
            'name': 'Test Engine Repair'})
        self.assertTrue(self.repair_type, 'Vehicle Repair Type not create')

        # create service type
        self.service_type = self.service_type_obj.create({
            'name': 'Test Repair And Maintenance'})
        self.assertTrue(self.service_type, 'Vehicle Service Type not create')

        # create color
        self.color = self.vehicle_color_obj.create({
            'name': self.vehicle_color.id})
        self.assertTrue(self.color, 'Vehicle Color not create')

        # create vehicle service
        self.vehicle_service = self.service_type_obj.create({
            'name': 'Washing'})
        self.assertTrue(self.vehicle_service, 'Vehicle Service not create')

        # create Driver
        self.driver = self.driver_obj.create({
            'name': 'jethalal',
            'email': 'jethalal@gmail.com',
            'phone': 9898981213})
        self.assertTrue(self.driver, 'Vehicle driver not create')

        # create odometer
        self.vehicle_odometer = self.odometer_obj.create({
            'date': self.cr_dt,
            'vehicle_id': self.create_vehicle_1.id,
            'driver_id': self.driver.id,
            'value': 1000})
        self.assertTrue(self.vehicle_odometer, 'Vehicle odometer not create')
