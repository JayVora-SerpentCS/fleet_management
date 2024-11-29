# See LICENSE file for full copyright and licensing details.

"""Fleet Vehicle and products models."""

from odoo import api, fields, models


class ProductTemplate(models.Model):
    """Product Template model."""

    _inherit = "product.template"

    is_vehicle = fields.Boolean("Vehicle")


class ProductProduct(models.Model):
    """Product model."""

    _inherit = "product.product"

    @api.model_create_multi
    def create(self, vals_list):
        """Overridden method to update the product information."""
        for vals in vals_list:
            if not vals.get("name", False) and self._context.get(
                "create_fleet_vehicle", False
            ):
                vals.update(
                    {
                        "name": "NEW VEHICLE",
                        "type": "consu",
                        "is_vehicle": True,
                    }
                )
        return super(ProductProduct, self).create(vals_list)

    def write(self, vals):
        """Overridden method to update the vehicle information."""
        ctx = dict(self.env.context)
        res = super(ProductProduct, self).write(vals)
        for product in self:
            if (
                ctx
                and not ctx.get("from_vehicle_create", False)
                and not ctx.get("from_vehicle_write", False)
            ):
                vehicles = self.env["fleet.vehicle"].search(
                    [("product_id", "=", product.id)]
                )
                update_vehicle_vals = {}
                if vals.get("image_1920", False):
                    update_vehicle_vals.update({"image_1920": product.image_1920})
                if vals.get("name", False):
                    update_vehicle_vals.update({"name": product.name})
                if update_vehicle_vals and vehicles:
                    vehicles.write(update_vehicle_vals)
        return res


class FleetVehicle(models.Model):
    """Fleet Vehicle model."""

    _inherit = "fleet.vehicle"
    _inherits = {"product.product": "product_id"}

    product_id = fields.Many2one(
        "product.product", "Product", ondelete="cascade", required=True
    )
    image_128 = fields.Image("Image", readonly=False)

    @api.model_create_multi
    def create(self, vals_list):
        """Overridden method to update the product information."""
        for vals in vals_list:
            new_vehicle = super(
                FleetVehicle, self.with_context(create_fleet_vehicle=True)
            ).create(vals)
            if new_vehicle.product_id:
                new_vehicle.product_id.with_context(from_vehicle_create=True).write(
                    {
                        "name": new_vehicle.name,
                        "image_1920": new_vehicle.image_128,
                        "is_vehicle": True,
                        "company_id": new_vehicle.company_id,
                    }
                )
            return new_vehicle

    def write(self, vals):
        """Overridden method to update the product information."""
        res = super(FleetVehicle, self).write(vals)
        update_prod_vals = {}
        for vehicle in self:
            if vehicle.product_id:
                if vals.get("image_1920", False):
                    update_prod_vals.update({"image_1920": vehicle.image_1920})
                if vals.get("model_id", False) or vals.get("license_plate", False):
                    update_prod_vals.update({"name": vehicle.name})
                if update_prod_vals:
                    vehicle.product_id.with_context(from_vehicle_write=True).write(
                        update_prod_vals
                    )
        return res

    @api.model
    def name_search(self, name="", args=None, operator="ilike", limit=100):
        """
        This method is called when pass context 'remove_inprogeress'
        This method will remove in rent car state in_progress records
        """
        if self._context.get("remove_inprogeress"):
            inprograce_recs = (
                self.env["fleet.rent"]
                .with_context(is_updated=True)
                .search(
                    [
                        ("state", "=", "open"),
                    ]
                )
            )
            inprogress_ids = inprograce_recs.mapped("vehicle_id.id")
            args = [
                ("state", "not in", ["write-off", "in_progress"]),
                ("id", "not in", inprogress_ids),
            ]
        return super().name_search(name, args, operator, limit=limit)
