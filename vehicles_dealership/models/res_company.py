# See LICENSE file for full copyright and licensing details.
"""Fleet Vehicle and products models."""

from odoo import fields, models


class ResCompany(models.Model):
    """Res Company."""

    _inherit = "res.company"

    din_number = fields.Char("DIN", help="Dealer Identification Number")
