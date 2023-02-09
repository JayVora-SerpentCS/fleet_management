# See LICENSE file for full copyright and licensing details.
"""Res Users Models."""

from odoo import fields, models


class ResPartner(models.Model):
    """Model res partner extended."""

    _inherit = "res.partner"

    d_id = fields.Char()
    is_driver = fields.Boolean()
    insurance = fields.Boolean()
