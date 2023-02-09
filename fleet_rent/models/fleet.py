# See LICENSE file for full copyright and licensing details.
"""Fleet Model."""

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class FleetVehicleExtend(models.Model):
    """Fleet Vehicle Extend."""

    _inherit = "fleet.vehicle"

    def _compute_count_rent(self):
        """Count the total number of Rent for the current vehicle."""
        rent_obj = self.env["fleet.rent"]
        for vehicle in self:
            vehicle.rent_count = rent_obj.search_count(
                [("vehicle_id", "=", vehicle.id)]
            )

    rent_count = fields.Integer(compute="_compute_count_rent", string="Rents")
