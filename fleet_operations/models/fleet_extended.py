# See LICENSE file for full copyright and licensing details.
"""Multi Image model."""

import logging
from datetime import date

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ProductProduct(models.Model):
    """product model."""

    _inherit = "product.product"

    in_active_part = fields.Boolean("In-Active Part?")
    vehicle_make_id = fields.Many2one("fleet.vehicle.model.brand", "Vehicle Make")


class FleetOperations(models.Model):
    """Fleet Operations model."""

    _inherit = "fleet.vehicle"
    _order = "id desc"
    _rec_name = "name"

    def copy(self, default=None):
        """Overridden copy method."""
        if not default:
            default = {}
        if self.state == "write-off":
            msg = _(
                "You can't duplicate this record " "because it is already write-off"
            )
            raise UserError(msg)
        return super(FleetOperations, self).copy(default=default)

    @api.model
    def vehicle_service_reminder_send_mail(self):
        """Method to Send Next Service Reminder to vehicle driver."""
        fleet_vehicles = self.env["fleet.vehicle"].search(
            [("next_service_date", "=", fields.Date.today())]
        )
        for vehicle in fleet_vehicles:
            if vehicle.driver_id and vehicle.driver_id.email:
                res = self.env.ref("fleet_operations.fleet_email_template")
                res.send_mail(vehicle.id, force_send=True)
        return True

    def update_history(self):
        """Method use update color engine,battery and tire history."""
        mod_obj = self.env["ir.model.data"]
        wizard_view = ""
        res_model = ""
        view_name = ""
        context = self.env.context
        context = dict(context)
        if context.get("history", False):
            if context.get("history", False) == "color":
                wizard_view = "update_color_info_form_view"
                res_model = "update.color.info"
                view_name = "Update Color Info"
            elif context.get("history", False) == "engine":
                wizard_view = "update_engine_info_form_view"
                res_model = "update.engine.info"
                view_name = "Update Engine Info"
            elif context.get("history", False) == "vin":
                wizard_view = "update_vin_info_form_view"
                res_model = "update.vin.info"
                view_name = "Update Vin Info"
            elif context.get("history", False) == "tire":
                wizard_view = "update_tire_info_form_view"
                res_model = "update.tire.info"
                view_name = "Update Tire Info"
            elif context.get("history", False) == "battery":
                wizard_view = "update_battery_info_form_view"
                res_model = "update.battery.info"
                view_name = "Update Battery Info"

        model_data_ids = mod_obj.search(
            [("model", "=", "ir.ui.view"), ("name", "=", wizard_view)]
        )
        resource_id = model_data_ids.read(["res_id"])[0]["res_id"]
        context.update({"vehicle_ids": self._ids})
        # self.env.args = cr, uid, misc.frozendict(context)
        return {
            "name": view_name,
            "context": self._context,
            "view_type": "form",
            "view_mode": "form",
            "res_model": res_model,
            "views": [(resource_id, "form")],
            "type": "ir.actions.act_window",
            "target": "new",
        }

    def set_released_state(self):
        """Method to set released state."""
        for vehicle in self:
            if vehicle.state == "complete":
                vehicle.write(
                    {
                        "state": "released",
                        "last_change_status_date": fields.Date.today(),
                        "released_date": fields.Date.today(),
                    }
                )
            else:
                msg = _(
                    "Vehicle status will only set to released "
                    "if it is in completed state."
                )
                raise UserError(msg)
        return True

    def name_get(self):
        """
        Method will be called when you view an M2O field in a form.

        And return name whatever we want to search.
        """
        if not len(self._ids):
            return []
        res = []
        for vehicle in self:
            vehicle_unique_id = vehicle.name or ""
            vehicle_unique_id += "-"
            vehicle_unique_id += vehicle.model_id and vehicle.model_id.name or ""
            res.append((vehicle["id"], vehicle_unique_id))
        return res

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        """Overwritten this method for the bypass base domain."""
        vehicle_ids = self.search(args, limit=limit)
        return vehicle_ids.name_get()

    def return_action_too_open(self):
        """
        The xml view specified in xml_id.

        For the current vehicle.
        """
        self.ensure_one()
        xml_id = self.env.context.get("xml_id")
        if xml_id:
            res = self.env["ir.actions.act_window"].for_xml_id(
                "fleet_operations", xml_id
            )
            res.update(
                context=dict(
                    self.env.context, default_vehicle_id=self.id, group_by=False
                ),
                domain=[("vehicle_id", "=", self.id)],
            )
            return res
        return False

    @api.constrains("tire_issuance_date", "battery_issuance_date")
    def check_tire_issuance_date(self):
        """Method to check tire issuance date."""
        for vehicle in self:
            if vehicle.tire_issuance_date and vehicle.battery_issuance_date:
                if (
                    vehicle.battery_issuance_date < vehicle.acquisition_date
                    and vehicle.tire_issuance_date < vehicle.acquisition_date
                ):
                    msg = _(
                        "Tire Issuance Date And Battery Issuance Date Should"
                        " Be Greater Than Registration Date."
                    )
                    raise ValidationError(msg)
            if (
                vehicle.tire_issuance_date
                and vehicle.tire_issuance_date < vehicle.acquisition_date
            ):
                msg = _(
                    "Tire Issuance Date Should Be " "Greater Than Registration Date."
                )
                raise ValidationError(msg)
            if (
                vehicle.battery_issuance_date
                and vehicle.battery_issuance_date < vehicle.acquisition_date
            ):
                msg = _(
                    "Battery Issuance Date Should Be " "Greater Than Registration Date."
                )
                raise ValidationError(msg)

    @api.constrains("warranty_period")
    def check_warranty_date(self):
        """Method to check warranty date."""
        for vehicle in self:
            if (
                vehicle.warranty_period
                and vehicle.warranty_period < vehicle.acquisition_date
            ):
                msg = _("Warranty Period Should Be " "Greater Than Registration Date.")
                raise ValidationError(msg)

    @api.constrains("driver_id")
    def check_duplicate_driver(self):
        for vehicle in self:
            if (
                vehicle.driver_id
                and self.search_count(
                    [
                        ("driver_id", "=", vehicle.driver_id.id),
                        ("id", "!=", vehicle.id),
                        ("state", "!=", "write-off"),
                    ]
                )
                > 1
            ):
                msg = _("Driver can be allocated to one vehicle only!")
                raise ValidationError(msg)

    @api.constrains("date_sold", "acquisition_date")
    def check_sold_date(self):
        """Method to check sold date."""
        for vehicle in self:
            if vehicle.acquisition_date and vehicle.date_sold:
                if vehicle.date_sold < vehicle.acquisition_date:
                    msg = _("Sold Date Should Be " "Greater Than Registration Date.")
                    raise ValidationError(msg)

    @api.constrains("date_sold", "transfer_date")
    def check_transfer_date(self):
        """Method to check transfer date."""
        for vehicle in self:
            if vehicle.transfer_date and vehicle.date_sold:
                if vehicle.transfer_date < vehicle.date_sold:
                    msg = _("Transfer Date Should Be " "Greater Than Sold Date.")
                    raise ValidationError(msg)

    @api.constrains("start_date_insurance", "end_date_insurance")
    def check_insurance_end_date(self):
        """Method to check insurance date."""
        for vehicle in self:
            if vehicle.start_date_insurance and vehicle.end_date_insurance:
                if vehicle.end_date_insurance < vehicle.start_date_insurance:
                    msg = _("Insurance end date should be " "greater than start date.")
                    raise ValidationError(msg)

    @api.constrains("start_date_insurance", "acquisition_date")
    def check_insurance_start_date(self):
        """Method to check insurance start date."""
        for vehicle in self:
            if vehicle.start_date_insurance and vehicle.acquisition_date:
                if vehicle.start_date_insurance < vehicle.acquisition_date:
                    msg = _(
                        "Insurance start date should be "
                        "greater than registration date."
                    )
                    raise ValidationError(msg)

    def _compute_get_odometer(self):
        fleet_vehicle_odometer_obj = self.env["fleet.vehicle.odometer"]
        for record in self:
            vehicle_odometer = fleet_vehicle_odometer_obj.search(
                [("vehicle_id", "=", record.id)], limit=1, order="value desc"
            )
            if vehicle_odometer:
                record.odometer = vehicle_odometer.value
            else:
                record.odometer = 0

    def _inverse_set_odometer(self):
        fleet_vehicle_odometer_obj = self.env["fleet.vehicle.odometer"]
        for record in self:
            vehicle_odometer = fleet_vehicle_odometer_obj.search(
                [("vehicle_id", "=", record.id)], limit=1, order="value desc"
            )
            if record.odometer < vehicle_odometer.value:
                msg = _(
                    "You can't enter odometer less than previous " "odometer %s !"
                ).format(vehicle_odometer.value)
                raise UserError(msg)

            if record.odometer:
                date = fields.Date.context_today(record)
                data = {"value": record.odometer, "date": date, "vehicle_id": record.id}
                fleet_vehicle_odometer_obj.create(data)

    @api.onchange("f_brand_id")
    def _onchange_brand(self):
        if self.f_brand_id:
            self.image_128 = self.f_brand_id.image_128
        else:
            self.image_128 = False

    @api.onchange("model_id")
    def _onchange_model_id(self):
        for model in self:
            if model.model_id:
                model.model_year = model.model_id.model_year or 0
                model.transmission = model.model_id.transmission or False
                model.seats = model.model_id.seats or 0
                model.doors = model.model_id.doors or 0
                model.color = model.model_id.color or ""
                model.trailer_hook = model.model_id.trailer_hook or 0
                model.fuel_type = model.model_id.default_fuel_type or False
                model.co2 = model.model_id.default_co2 or 0.0
                model.co2_standard = model.model_id.co2_standard or ""
                model.power = model.model_id.power or 0
                model.horsepower = model.model_id.horsepower or 0
                model.horsepower_tax = model.horsepower_tax or 0.0

    @api.depends("model_id", "license_plate")
    def _compute_vehicle_name(self):
        for record in self:
            if record.model_id and record.model_id.brand_id:
                lic_plate = record.license_plate
                if not record.license_plate:
                    lic_plate = ""
                record.name = (
                    record.model_id.brand_id.name
                    + "/"
                    + record.model_id.name
                    + "/"
                    + lic_plate
                )

    name = fields.Char(compute="_compute_vehicle_name", store=True)
    odometer_check = fields.Boolean("Odometer Change", default=True)
    fuel_qty = fields.Char("Fuel Quality")
    oil_name = fields.Char()
    oil_capacity = fields.Char()
    fleet_id = fields.Integer("Fleet ID", help="Take this field for data migration")
    f_brand_id = fields.Many2one("fleet.vehicle.model.brand", "Make")
    model_no = fields.Char(translate=True)
    license_plate = fields.Char(
        translate=True,
        help="License plate number of the vehicle.\
                                (ie: plate number for a vehicle)",
    )
    active = fields.Boolean(default=True)
    dealer_id = fields.Many2one("res.partner")
    mileage = fields.Integer("Mileage(K/H)")
    description = fields.Text("About Vehicle", translate=True)
    engine_size = fields.Char()
    cylinders = fields.Integer()
    front_tire_size = fields.Float()
    front_tire_pressure = fields.Integer()
    rear_tire_size = fields.Float()
    rear_tire_pressure = fields.Integer()
    last_service_date = fields.Date("Last Service", readonly=True)
    next_service_date = fields.Date("Next Service", readonly=True)
    last_odometer = fields.Float("Last Service Odometer")
    last_odometer_unit = fields.Selection(
        [("kilometers", "Kilometers"), ("miles", "Miles")],
        help="Unit of the odometer ",
    )
    due_odometer = fields.Float("Next Service Odometer", readonly=True)
    due_odometer_unit = fields.Selection(
        [("kilometers", "Kilometers"), ("miles", "Miles")],
        "Due Odometer Units",
        help="Unit of the odometer ",
    )
    left_wiper_blade = fields.Char("Wiper Blade(L)")
    right_wiper_blade = fields.Char("Wiper Blade(R)")
    rr_wiper_blade = fields.Char("Wiper Blade(RR)")
    vehicle_length = fields.Integer("Length(mm)")
    vehicle_width = fields.Integer("Width(mm)")
    vehicle_height = fields.Integer("Height(mm)")
    fuel_capacity = fields.Float()
    date_sold = fields.Date()
    buyer_id = fields.Many2one("res.partner", "Buyer")
    transfer_date = fields.Date()
    monthly_deprication = fields.Float("Deprication(Monthly)")
    resale_value = fields.Float("Current value")
    salvage_value = fields.Float()
    warranty_period = fields.Date("Warranty Upto")
    insurance_company_id = fields.Many2one(
        "res.partner", "Insurance Company", domain=[("insurance", "=", True)]
    )
    insurance_type_id = fields.Many2one("insurance.type", "Insurance Type")
    policy_number = fields.Char()
    payment = fields.Float()
    start_date_insurance = fields.Date("Start Date")
    end_date_insurance = fields.Date("End Date")
    payment_deduction = fields.Float("Deduction")
    fleet_attach_ids = fields.One2many(
        "ir.attachment", "attachment_id", "Fleet Attachments"
    )
    sale_purchase_attach_ids = fields.One2many(
        "ir.attachment", "attachment_id_2", "Attachments"
    )
    odometer = fields.Float(
        compute="_compute_get_odometer",
        inverse="_inverse_set_odometer",
        help="Odometer measure of the vehicle at the \
                                moment of this log",
    )
    vehical_color_id = fields.Many2one("color.color", "Vehicle Color")
    vehicle_location_id = fields.Many2one("res.country.state", "Registration State")
    vehical_division_id = fields.Many2one("vehicle.divison", "Division")
    driver_id = fields.Many2one("res.partner", "Driver")
    driver_identification_no = fields.Char("Driver ID")
    driver_contact_no = fields.Char("Driver Contact Number")
    main_type = fields.Selection(
        [("vehicle", "Vehicle"), ("non-vehicle", "Non-Vehicle")], default="vehicle"
    )
    vechical_type_id = fields.Many2one("vehicle.type", "Vechical Type")
    engine_no = fields.Char()
    multi_images = fields.Many2many(
        "ir.attachment",
        "fleet_vehicle_attachment_rel",
        "vehicle_id",
        "attachment_id",
    )
    state = fields.Selection(
        [
            ("inspection", "Draft"),
            ("in_progress", "In Service"),
            ("contract", "On Contract"),
            ("rent", "On Rent"),
            ("complete", "Completed"),
            ("released", "Released"),
            ("write-off", "Write-Off"),
        ],
        "Vehicle State",
        default="inspection",
    )
    is_id_generated = fields.Boolean("Is Id Generated?", default=False)
    increment_odometer = fields.Float("Next Increment Odometer")
    last_change_status_date = fields.Date("Last Status Changed Date", readonly=True)
    pending_repair_type_ids = fields.One2many(
        "pending.repair.type",
        "vehicle_rep_type_id",
        "Pending Repair Types",
        readonly=True,
    )
    released_date = fields.Date(readonly=True)
    tire_size = fields.Char()
    tire_srno = fields.Char("Tire S/N")
    tire_issuance_date = fields.Date()
    battery_size = fields.Char()
    battery_srno = fields.Char("Battery S/N")
    battery_issuance_date = fields.Date()
    color_history_ids = fields.One2many(
        "color.history", "vehicle_id", "Color History", readonly=True
    )
    engine_history_ids = fields.One2many(
        "engine.history", "vehicle_id", "Engine History", readonly=True
    )
    vin_history_ids = fields.One2many(
        "vin.history", "vehicle_id", "Vin History", readonly=True
    )
    tire_history_ids = fields.One2many(
        "tire.history", "vehicle_id", "Tire History", readonly=True
    )
    battery_history_ids = fields.One2many(
        "battery.history", "vehicle_id", "Battrey History", readonly=True
    )
    is_color_set = fields.Boolean("Is Color Set?")
    is_engine_set = fields.Boolean()
    is_vin_set = fields.Boolean("Is Vin Set?")
    is_tire_size_set = fields.Boolean("Is Tire Size set?")
    is_tire_srno_set = fields.Boolean("Is Tire Srno set?")
    is_tire_issue_set = fields.Boolean("Is Tire Issue set?")
    is_battery_size_set = fields.Boolean("Is battery Size set?")
    is_battery_srno_set = fields.Boolean("Is battery Srno set?")
    is_battery_issue_set = fields.Boolean("Is battery Issue set?")
    last_service_by_id = fields.Many2one("res.partner", "Last Service By")
    work_order_ids = fields.One2many(
        "fleet.vehicle.log.services", "vehicle_id", "Service Order"
    )
    reg_id = fields.Many2one("res.users", "Registered By")
    vehicle_owner = fields.Many2one("res.users")
    updated_by = fields.Many2one("res.users")
    updated_date = fields.Date("Updated date")
    work_order_close = fields.Boolean(default=True)
    fmp_id_editable = fields.Boolean("Vehicle ID Editable?")

    _sql_constraints = [
        (
            "vehilce_unique",
            "unique(vin_sn)",
            "The vehicle is already exist with this vin no.!",
        ),
        (
            "fmp_unique",
            "unique(name)",
            "The vehicle is already exist with this Vehicle ID!",
        ),
    ]

    income_acc_id = fields.Many2one("account.account", "Income Account")
    expence_acc_id = fields.Many2one("account.account", "Expense Account")

    @api.model
    def default_get(self, fields):
        """Method to default get."""
        res = super(FleetOperations, self).default_get(fields)
        res["acquisition_date"] = date.today().strftime("%Y-%m-%d")
        return res

    @api.model_create_multi
    def create(self, vals_list):
        """Create method override."""
        for vals in vals_list:
            if not vals.get("model_id", False):
                msg = _("Model is not selected for this vehicle!")
                raise UserError(msg)
            vals.update({"fmp_id_editable": True})
            seq = self.env["ir.sequence"].next_by_code("fleet.vehicle")
            vals.update({"name": seq})
            if self._uid:
                vals.update({"reg_id": self._uid})
            if not vals.get("acquisition_date", False):
                vals.update({"acquisition_date": fields.Date.today()})
            if not vals.get("last_change_status_date", False):
                vals.update({"last_change_status_date": fields.Date.today()})

            # checking once vin, color and engine number will be set than field
            # automatically become readonly.

            if vals.get("odometer_unit"):
                vals.update({"odometer_check": False})
            if vals.get("vin_sn", False):
                vals.update({"is_vin_set": True})
            if vals.get("vehical_color_id", False):
                vals.update({"is_color_set": True})
            if vals.get("engine_no", False):
                vals.update({"is_engine_set": True})
            if vals.get("tire_size", False):
                vals.update({"is_tire_size_set": True})
            if vals.get("tire_srno", False):
                vals.update({"is_tire_srno_set": True})
            if vals.get("tire_issuance_date", False):
                vals.update({"is_tire_issue_set": True})

            if vals.get("battery_size", False):
                vals.update({"is_battery_size_set": True})
            if vals.get("battery_srno", False):
                vals.update({"is_battery_srno_set": True})
            if vals.get("battery_issuance_date", False):
                vals.update({"is_battery_issue_set": True})

            return super(FleetOperations, self).create(vals)

    def write(self, vals):
        """
        Function write an entry in the open chatter whenever.

        we change important information.

        on the vehicle like the model, the drive, the state of the vehicle.

        or its license plate.
        """
        vals.update({"fmp_id_editable": True})
        if self._uid:
            vals.update({"updated_by": self.env.user.id})
            vals.update({"updated_date": fields.Date.today()})

        if vals.get("tire_size", False):
            vals.update({"is_tire_size_set": True})
        if vals.get("tire_srno", False):
            vals.update({"is_tire_srno_set": True})
        if vals.get("tire_issuance_date", False):
            vals.update({"is_tire_issue_set": True})

        if vals.get("battery_size", False):
            vals.update({"is_battery_size_set": True})
        if vals.get("battery_srno", False):
            vals.update({"is_battery_srno_set": True})
        if vals.get("battery_issuance_date", False):
            vals.update({"is_battery_issue_set": True})

        return super(FleetOperations, self).write(vals)

    @api.onchange("driver_id")
    def get_driver_id_no(self):
        """Method to get driver id no."""
        if self.driver_id:
            driver = self.driver_id
            self.driver_identification_no = driver.d_id or ""
            self.driver_contact_no = driver.mobile
        else:
            self.driver_identification_no = ""
            self.driver_contact_no = ""


class ColorHistory(models.Model):
    """Model color history."""

    _name = "color.history"
    _description = "Color History for Vehicle"

    vehicle_id = fields.Many2one("fleet.vehicle", "Vehicle")
    previous_color_id = fields.Many2one("color.color", "Previous Color")
    current_color_id = fields.Many2one("color.color", "New Color")
    changed_date = fields.Date("Change Date")
    note = fields.Text("Notes", translate=True)
    workorder_id = fields.Many2one("fleet.vehicle.log.services", "Work Order")


class EngineHistory(models.Model):
    """Model Engine History."""

    _name = "engine.history"
    _description = "Engine History for Vehicle"

    vehicle_id = fields.Many2one("fleet.vehicle", "Vehicle")
    previous_engine_no = fields.Char()
    new_engine_no = fields.Char()
    changed_date = fields.Date("Change Date")
    note = fields.Text("Notes", translate=True)
    workorder_id = fields.Many2one("fleet.vehicle.log.services", "Work Order")


class VinHistory(models.Model):
    """Model Vin History."""

    _name = "vin.history"
    _description = "Vin History"

    vehicle_id = fields.Many2one("fleet.vehicle", "Vehicle")
    previous_vin_no = fields.Char(translate=True)
    new_vin_no = fields.Char(translate=True)
    changed_date = fields.Date("Change Date")
    note = fields.Text("Notes", translate=True)
    workorder_id = fields.Many2one("fleet.vehicle.log.services", "Work Order")


class TireHistory(models.Model):
    """Model Tire History."""

    _name = "tire.history"
    _description = "Tire History for Vehicle"

    vehicle_id = fields.Many2one("fleet.vehicle", "Vehicle")
    previous_tire_size = fields.Char(translate=True)
    new_tire_size = fields.Char(translate=True)
    previous_tire_sn = fields.Char("Previous Tire Serial", translate=True)
    new_tire_sn = fields.Char("New Tire Serial")
    previous_tire_issue_date = fields.Date("Previous Tire Issuance Date")
    new_tire_issue_date = fields.Date("New Tire Issuance Date")
    changed_date = fields.Date("Change Date")
    note = fields.Text("Notes", translate=True)
    workorder_id = fields.Many2one("fleet.vehicle.log.services", "Work Order")


class BatteryHistory(models.Model):
    """Model Battery History."""

    _name = "battery.history"
    _description = "Battery History for Vehicle"

    vehicle_id = fields.Many2one("fleet.vehicle", "Vehicle")
    previous_battery_size = fields.Char()
    new_battery_size = fields.Char()
    previous_battery_sn = fields.Char("Previous Battery Serial")
    new_battery_sn = fields.Char("New Battery Serial")
    previous_battery_issue_date = fields.Date("Previous Battery Issuance Date")
    new_battery_issue_date = fields.Date("New Battery Issuance Date")
    changed_date = fields.Date("Change Date")
    note = fields.Text("Notes", translate=True)
    workorder_id = fields.Many2one("fleet.vehicle.log.services", "Work Order")


class PendingRepairType(models.Model):
    """Model Pending Repair Type."""

    _name = "pending.repair.type"
    _description = "Pending Repair Type"

    vehicle_rep_type_id = fields.Many2one("fleet.vehicle", "Vehicle")
    repair_type_id = fields.Many2one("repair.type", "Repair Type")
    name = fields.Char("Work Order #", translate=True)
    categ_id = fields.Many2one("service.category", "Category")
    issue_date = fields.Date()
    state = fields.Selection(
        [("complete", "Complete"), ("in-complete", "Pending")], "Status"
    )
    user_id = fields.Many2one("res.users", "By")


class VehicleDivision(models.Model):
    """Model Vehicle Division."""

    _name = "vehicle.divison"
    _description = "Vehicle Division"

    code = fields.Char(translate=True)
    name = fields.Char(required=True, translate=True)

    _sql_constraints = [
        ("vehicle.divison_uniq", "unique(name)", "This divison is already exist!")
    ]


class VehicleType(models.Model):
    """Model Vehicle Type."""

    _name = "vehicle.type"
    _description = "Vehicle Type"

    code = fields.Char(translate=True)
    name = fields.Char(required=True, translate=True)

    @api.constrains("name")
    def _check_unique_vehicle_type(self):
        for vehicle_type in self:
            if self.search_count(
                [
                    ("id", "!=", vehicle_type.id),
                    ("name", "ilike", vehicle_type.name.strip()),
                ]
            ):
                msg = _("Vehicle type with this name already exists!")
                raise UserError(msg)


class VehicleLocation(models.Model):
    """Model Vehicle Location."""

    _name = "vehicle.location"
    _description = "Vehicle Location"

    code = fields.Char(translate=True)
    name = fields.Char(required=True, translate=True)


class VehicleDepartment(models.Model):
    """Model Vehicle Department."""

    _name = "vehicle.department"
    _description = "Vehicle Department"

    code = fields.Char(translate=True)
    name = fields.Char(required=True, translate=True)


class ColorColor(models.Model):
    """Model Color."""

    _name = "color.color"
    _description = "Colors"

    code = fields.Char(translate=True)
    name = fields.Char(required=True, translate=True)

    @api.constrains("name")
    def check_color(self):
        """Method to check duplicate value."""
        for rec in self:
            if self.env["color.color"].search_count(
                [("name", "ilike", rec.name.strip()), ("id", "!=", rec.id)]
            ):
                msg = _("This color already exist")
                raise ValidationError(msg)


class IrAttachment(models.Model):
    """Model Ir Attachment."""

    _inherit = "ir.attachment"

    attachment_id = fields.Many2one("fleet.vehicle")
    attachment_id_2 = fields.Many2one("fleet.vehicle")


class FleetWittenOff(models.Model):
    """Model Fleet Witten Off."""

    _name = "fleet.wittenoff"
    _description = "Wittenoff Vehicles"
    _order = "id desc"
    _rec_name = "vehicle_id"

    name = fields.Char()
    fleet_id = fields.Integer("Fleet ID", help="Take this field for data migration")
    vehicle_id = fields.Many2one("fleet.vehicle", "Vehicle", required=True)
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env["res.company"]._default_currency_id(),
        help="The optional other currency if it is a multi-currency entry.",
    )
    vehicle_fmp_id = fields.Char("Vehicle ID")
    vin_no = fields.Char(translate=True)
    color_id = fields.Many2one("color.color", "Color")
    vehicle_plate = fields.Char("Vechicle Plate No.", translate=True)
    report_date = fields.Date()
    odometer = fields.Float()
    cost_esitmation = fields.Float("Cost Estimation")
    note_for_cause_damage = fields.Text("Cause of Damage", translate=True)
    note = fields.Text(translate=True)
    cancel_note = fields.Text(translate=True)
    multi_images = fields.Many2many(
        "ir.attachment",
        "fleet_written_off_attachment_rel",
        "writeoff_id",
        "attachment_id",
    )
    damage_type_ids = fields.Many2many(
        "damage.types",
        "fleet_wittenoff_damage_types_rel",
        "write_off_id",
        "damage_id",
        "Damage Type",
    )
    repair_type_ids = fields.Many2many(
        "repair.type",
        "fleet_wittenoff_repair_types_rel",
        "write_off_id",
        "repair_id",
        "Repair Type",
    )
    location_id = fields.Many2one("vehicle.location", "Location")
    driver_id = fields.Many2one("res.partner", "Driver")
    write_off_type = fields.Selection(
        [
            ("general_accident", "General Accident"),
            ("insurgent_attack", "Insurgent Attack"),
        ],
        "Write-off Type",
        default="general_accident",
    )
    contact_no = fields.Char("Driver Contact Number")
    odometer_unit = fields.Selection(
        [("kilometers", "Kilometers"), ("miles", "Miles")],
        help="Unit of the odometer ",
    )
    province_id = fields.Many2one("res.country.state", "Registration State")
    division_id = fields.Many2one("vehicle.divison", "Division")
    state = fields.Selection(
        [("draft", "Draft"), ("confirm", "Confirmed"), ("cancel", "Cancelled")],
        default="draft",
    )
    date_cancel = fields.Date("Date Cancelled")
    cancel_by_id = fields.Many2one("res.users", "Cancelled By")

    @api.constrains("cost_esitmation")
    def check_estimation_cost(self):
        for cost in self:
            if cost.cost_esitmation < 0:
                msg = _("Expense to repair cost should not be negative!")
                raise ValidationError(msg)

    def write(self, vals):
        """Override write method and update values."""
        for fleet_witten in self:
            if fleet_witten.vehicle_id:
                vals.update(
                    {
                        "vin_no": fleet_witten.vehicle_id
                        and fleet_witten.vehicle_id.vin_sn
                        or "",
                        "vehicle_fmp_id": fleet_witten.vehicle_id
                        and fleet_witten.vehicle_id.name
                        or "",
                        "color_id": fleet_witten.vehicle_id
                        and fleet_witten.vehicle_id.vehical_color_id
                        and fleet_witten.vehicle_id.vehical_color_id.id
                        or False,
                        "vehicle_plate": fleet_witten.vehicle_id
                        and fleet_witten.vehicle_id.license_plate
                        or "",
                        "province_id": fleet_witten.vehicle_id
                        and fleet_witten.vehicle_id.vehicle_location_id
                        and fleet_witten.vehicle_id.vehicle_location_id.id
                        or False,
                        "division_id": fleet_witten.vehicle_id
                        and fleet_witten.vehicle_id.vehical_division_id
                        and fleet_witten.vehicle_id.vehical_division_id.id
                        or False,
                        "driver_id": fleet_witten.vehicle_id
                        and fleet_witten.vehicle_id.driver_id
                        and fleet_witten.vehicle_id.driver_id.id
                        or False,
                        "contact_no": fleet_witten.vehicle_id
                        and fleet_witten.vehicle_id.driver_id
                        and fleet_witten.vehicle_id.driver_id.mobile
                        or "",
                        "odometer": fleet_witten.vehicle_id
                        and fleet_witten.vehicle_id.odometer
                        or 0.0,
                        "odometer_unit": fleet_witten.vehicle_id
                        and fleet_witten.vehicle_id.odometer_unit
                        or False,
                    }
                )
        return super(FleetWittenOff, self).write(vals)

    @api.model
    def default_get(self, fields):
        """Default get method update in state changing record."""
        vehicle_obj = self.env["fleet.vehicle"]
        res = super(FleetWittenOff, self).default_get(fields)
        if self._context.get("active_ids", False):
            for vehicle in vehicle_obj.browse(self._context["active_ids"]):
                if vehicle.state == "write-off":
                    msg = _("This vehicle is already in " "write-off state!")
                    raise UserError(msg)
                elif vehicle.state == "in_progress" or vehicle.state == "complete":
                    msg = _(
                        "You can't write-off this vehicle "
                        "which is in Progress or Complete state!"
                    )
                    raise UserError(msg)
                # elif vehicle.state == 'inspection':
                #     raise UserError(_("You can\'t write-off this "
                #                       "vehicle which is in Inspection"))
                elif vehicle.state == "rent":
                    msg = _("You can't write-off this " "vehicle which is On Rent.")
                    raise UserError(msg)
                res.update({"contact_no": vehicle.driver_contact_no or ""})
        return res

    @api.onchange("vehicle_id")
    def get_vehicle_info(self):
        """Method to get vehicle information."""
        if self.vehicle_id:
            vehicle = self.vehicle_id
            self.province_id = (
                vehicle.vehicle_location_id and vehicle.vehicle_location_id.id or False
            )
            self.driver_id = vehicle.driver_id and vehicle.driver_id.id or False
            self.contact_no = vehicle.driver_contact_no or ""
            self.vin_no = vehicle.vin_sn or ""
            self.vehicle_fmp_id = vehicle.name or ""
            self.color_id = (
                vehicle.vehical_color_id and vehicle.vehical_color_id.id or False
            )
            self.vehicle_plate = vehicle.license_plate or ""
            self.odometer = vehicle.odometer or 0.0
            self.odometer_unit = vehicle.odometer_unit or False
            self.division_id = (
                vehicle.vehical_division_id and vehicle.vehical_division_id.id or False
            )

    def cancel_writeoff(self):
        """Button method in cancel state in the write off."""
        return {
            "name": "Write Off Cancel Form",
            "res_model": "writeoff.cancel.reason",
            "type": "ir.actions.act_window",
            "view_id": False,
            "view_mode": "form",
            "view_type": "form",
            "target": "new",
        }

    def confirm_writeoff(self):
        """Confirm button method in the writeoff state."""
        for wr_off in self:
            if wr_off.vehicle_id:
                wr_off.vehicle_id.write(
                    {
                        "state": "write-off",
                        "last_change_status_date": fields.Date.today(),
                    }
                )
            wr_off.write(
                {
                    "state": "confirm",
                    "name": self.env["ir.sequence"].next_by_code(
                        "vehicle.writeoff.sequnce"
                    ),
                }
            )

    def action_set_to_draft(self):
        """Button method to set state in draft."""
        for wr_off in self:
            wr_off.write(
                {
                    "state": "draft",
                }
            )


class FleetVehicleModel(models.Model):
    """Model Fleet Vehicle."""

    _inherit = "fleet.vehicle.model"
    _rec_name = "name"

    name = fields.Char("Model name", required=True, translate=True)
    brand_id = fields.Many2one(
        "fleet.vehicle.model.brand", "Make", required=True, help="Brand of the vehicle"
    )

    image_128 = fields.Image("Image", readonly=False)

    _sql_constraints = [
        (
            "model_brand_name_uniq",
            "unique(name,brand_id)",
            "Model with this brand Name and Make is " "already exist!",
        )
    ]


class FleetVehicleModelBrand(models.Model):
    """Model Fleet Vehicle Model Brand."""

    _inherit = "fleet.vehicle.model.brand"

    name = fields.Char("Make", required=True, translate=True)

    @api.constrains("name")
    def _check_duplicate_model_brand(self):
        """Method to check duplicate damage type."""
        for model in self:
            if self.search_count(
                [("name", "ilike", model.name.strip()), ("id", "!=", model.id)]
            ):
                msg = _("Model Brand with this name already exists!")
                raise ValidationError(msg)


class FleetVehicleAdvanceSearch(models.TransientModel):
    """Model fleet vehicle advance search."""

    _name = "fleet.vehicle.advance.search"
    _description = "Vehicle Advance Search"
    _rec_name = "fmp_id"

    fmp_id = fields.Many2one("fleet.vehicle", "Vehicle ID")
    vehicle_location_id = fields.Many2one("res.country.state", "Province")
    state = fields.Selection(
        [
            ("inspection", "Inspection"),
            ("in_progress", "In Progress"),
            ("complete", "Completed"),
            ("released", "Released"),
            ("write-off", "Write-Off"),
        ],
        "Status",
    )
    vehical_color_id = fields.Many2one("color.color", "Color")
    vin_no = fields.Char()
    engine_no = fields.Char()
    last_service_date = fields.Date("Last Service From")
    last_service_date_to = fields.Date("Last Service To")
    next_service_date = fields.Date("Next Service From")
    next_service_date_to = fields.Date("Next Service To")
    acquisition_date = fields.Date("Registration From")
    acquisition_date_to = fields.Date("Registration To")
    release_date_from = fields.Date("Released From")
    release_date_to = fields.Date("Released To")
    driver_identification_no = fields.Char("Driver ID")
    vechical_type_id = fields.Many2one("vehicle.type", "Vechical Type")
    division_id = fields.Many2one("vehicle.divison", "Division")
    make_id = fields.Many2one("fleet.vehicle.model.brand", "Make")
    model_id = fields.Many2one("fleet.vehicle.model", "Model")


class VehicleUniqueSequence(models.Model):
    """Model Vehicle Unique Sequence."""

    _name = "vehicle.unique.sequence"
    _description = "Vehicle Unique Sequence"

    name = fields.Char(translate=True)
    vehicle_location_id = fields.Many2one("res.country.state", "Location ")
    make_id = fields.Many2one("fleet.vehicle.model.brand", "Make")
    sequence_id = fields.Many2one("ir.sequence", "Sequence")

    _sql_constraints = [
        (
            "location_make_name_uniq",
            "unique (vehicle_location_id,make_id,sequence_id)",
            "Location, Make and Sequence all should be \
                unique for unique sequence!",
        )
    ]


class NextIncrementNumber(models.Model):
    """Model Next Increment NUmber."""

    _name = "next.increment.number"
    _description = "Next Increment Number"

    name = fields.Char(translate=True)
    vehicle_id = fields.Many2one("fleet.vehicle")
    number = fields.Float("Odometer Increment")

    @api.constrains("number")
    def check_odometer_number(self):
        for rec in self:
            if rec.number < 0.0:
                msg = _(
                    "You can not add negative value " "for odometer number of vehicle!"
                )
                raise ValidationError(msg)

    @api.constrains("vehicle_id")
    def _check_vehicle_id(self):
        """Method to check last service date."""
        next_number = self.env["next.increment.number"]
        for increment in self:
            if next_number.search_count(
                [
                    ("vehicle_id", "=", increment.vehicle_id.id),
                    ("id", "!=", increment.id),
                ]
            ):
                msg = _(
                    "You can not add more than one odometer "
                    "increment configuration for same vehicle.!!!"
                )
                raise ValidationError(msg)


class NextServiceDays(models.Model):
    """Model Next Service Days."""

    _name = "next.service.days"
    _description = "Next Service days"

    name = fields.Char(translate=True)
    vehicle_id = fields.Many2one("fleet.vehicle")
    days = fields.Integer()

    @api.constrains("days")
    def check_service_days(self):
        for rec in self:
            if rec.days < 0:
                msg = _("You can not add negative value " "next service days!")
                raise ValidationError(msg)

    @api.constrains("vehicle_id")
    def _check_vehicle_id(self):
        """Method to check last service date."""
        for service in self:
            if self.search_count(
                [("vehicle_id", "=", service.vehicle_id.id), ("id", "!=", service.id)]
            ):
                msg = _(
                    "You can not add more than one next "
                    "service days configuration for same vehicle.!!!"
                )
                raise ValidationError(msg)


class DamageTypes(models.Model):
    """Model Damage Types."""

    _name = "damage.types"
    _description = "Damage Types"

    name = fields.Char(translate=True, required=True)
    code = fields.Char()

    @api.constrains("name", "code")
    def _check_duplicate_damage_type(self):
        """Method to check duplicate damage type."""
        for damage in self:
            if self.search_count(
                [
                    ("name", "ilike", damage.name.strip()),
                    ("code", "ilike", damage.code.strip()),
                    ("id", "!=", damage.id),
                ]
            ):
                msg = _("You can't add duplicate" " damage types !")
                raise ValidationError(msg)


class FleetVehicleOdometer(models.Model):
    """Model Fleet Vehicle Odometer."""

    _inherit = "fleet.vehicle.odometer"
    _description = "Odometer log for a vehicle"
    _order = "date desc"

    def _compute_vehicle_log_name_get_fnc(self):
        for record in self:
            name = record.vehicle_id and record.vehicle_id.name or False
            if record.date:
                if not name:
                    name = "New/" + str(record.date)
                name = name + " / " + str(record.date)
            record.name = name

    @api.onchange("vehicle_id")
    def _onchange_vehicle(self):
        """Method to onchange vehicle."""
        if self.vehicle_id:
            odometer_unit = self.vehicle_id.odometer_unit
            value = self.vehicle_id.odometer
            self.unit = odometer_unit
            self.value = value

    name = fields.Char(compute="_compute_vehicle_log_name_get_fnc", store=True)
    date = fields.Date(default=fields.Date.today())
    value = fields.Float("Odometer Value", group_operator="max")
    vehicle_id = fields.Many2one("fleet.vehicle", "Vehicle", required=True)
    make = fields.Many2one(related="vehicle_id.f_brand_id", store=True)
    model = fields.Many2one(related="vehicle_id.model_id", store=True)
    unit = fields.Selection(related="vehicle_id.odometer_unit", readonly=True)

    @api.model
    def default_get(self, fields):
        """Method default get."""
        res = super(FleetVehicleOdometer, self).default_get(fields)
        # cr, uid, context = self.env.args
        context = self.env.context
        # context = dict(context)
        fleet_obj = self.env["fleet.vehicle"]
        if self._context.get("active_id"):
            vehicle_id = fleet_obj.browse(context["active_id"])
            if vehicle_id.state == "write-off":
                res["vehicle_id"] = False
        return res


class ReportHeading(models.Model):
    """Model Report Heading."""

    _name = "report.heading"
    _description = "Report Heading"

    @api.depends("image")
    def _compute_get_image(self):
        return {p.id: tools.image_get_resized_images(p.image) for p in self}

    def _inverse_set_image(self):
        if self.image_small:
            self.image = tools.image_resize_image_small(
                self.image_small, size=(102, 50)
            )
        elif self.image_medium:
            self.image = tools.image_resize_image_small(
                self.image_medium, size=(102, 50)
            )

    name = fields.Char("Title", translate=True)
    revision_no = fields.Char("Rev. No.", translate=True)
    document_no = fields.Char("Document No.", translate=True)
    image = fields.Binary(
        help="This field holds the image used as image \
                            for the Report , limited to 1024x1024px.",
    )
    image_medium = fields.Binary(
        compute="_compute_get_image",
        inverse="_inverse_set_image",
        help="Medium-sized image of the Report. \
                                 It is automatically resized as a 128x128px \
                                image, with aspect ratio preserved, "
        "only when the image exceeds one of those \
                                 sizes. Use this field in form views or \
                                 some kanban views.",
    )
    image_small = fields.Binary(
        compute="_compute_get_image",
        inverse="_inverse_set_image",
        help="Small-sized image of the Report. \
                                It is automatically "
        "resized as a 64x64px image, \
                                with aspect ratio preserved. "
        "Use this field anywhere a small \
                                image is required.",
    )


class ResCompany(models.Model):
    """Model Res Company."""

    _inherit = "res.company"

    name = fields.Char(
        related="partner_id.name", required=True, store=True, translate=True
    )


class InsuranceType(models.Model):
    """Model Insurance Type."""

    _name = "insurance.type"
    _description = "Vehicle Insurance Type"

    name = fields.Char()
