# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

"""Fleet Vehicle and products models."""

from odoo import api, fields, models


class FleetVehicle(models.Model):
    """Fleet Vehicle model."""

    _inherit = 'fleet.vehicle'
    _inherits = {'product.product': 'product_id'}

    product_id = fields.Many2one('product.product', 'Product',
                                 ondelete="cascade", delegate=True,
                                 required=True)
    image_128 = fields.Image(string="Image", readonly=False)

    @api.model
    def create(self, vals):
        """Overridden method to update the product information."""
        ctx = dict(self.env.context)
        new_vehicle = super(FleetVehicle, self.with_context(
            create_fleet_vehicle=True)).create(vals)
        ctx.update({"from_vehicle_create": True})
        if new_vehicle.product_id:
            new_vehicle.product_id.with_context(ctx).write({
                'name': new_vehicle.name,
                'image_1920': new_vehicle.image_1920,
                'is_vehicle': True})
        return new_vehicle

    def write(self, vals):
        """Overridden method to update the product information."""
        ctx = dict(self.env.context)
        res = super(FleetVehicle, self).write(vals)
        update_prod_vals = {}
        ctx.update({"from_vehicle_write": True})
        for vehicle in self:
            if vehicle.product_id:
                if vals.get('image_1920', False):
                    update_prod_vals.update({
                        'image_1920': vehicle.image_1920})
                if vals.get('model_id', False) or \
                        vals.get('license_plate', False):
                    update_prod_vals.update({'name': vehicle.name})
                if update_prod_vals:
                    vehicle.product_id.\
                        with_context(ctx).write(update_prod_vals)
        return res


class ProductTemplate(models.Model):
    """Product Template model."""

    _inherit = 'product.template'

    is_vehicle = fields.Boolean(string="Vehicle")


class ProductProduct(models.Model):
    """Product model."""

    _inherit = 'product.product'

    is_vehicle = fields.Boolean(string="Vehicle")

    @api.model
    def create(self, vals):
        """Overridden method to update the product information."""
        if not vals.get('name', False) and \
                self._context.get('create_fleet_vehicle', False):
            vals.update({'name': 'NEW VEHICLE',
                         'type': 'product',
                         'is_vehicle': True})
        return super(ProductProduct, self).create(vals)

    def write(self, vals):
        """Overridden method to update the vehicle information."""
        ctx = dict(self.env.context)
        res = super(ProductProduct, self).write(vals)
        for product in self:
            if ctx and not ctx.get("from_vehicle_create", False) and \
                    not ctx.get("from_vehicle_write", False):
                vehicles = self.env['fleet.vehicle'].search([
                    ('product_id', '=', product.id)])
                update_vehicle_vals = {}
                if vals.get('image_1920', False):
                    update_vehicle_vals.update({
                        'image_1920': product.image_1920})
                if vals.get('name', False):
                    update_vehicle_vals.update({'name': product.name})
                if update_vehicle_vals and vehicles:
                    for vehicle in vehicles:
                        vehicle.write(update_vehicle_vals)
        return res
