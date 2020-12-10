# See LICENSE file for full copyright and licensing details.
"""Damage Type models."""

from odoo import _, api, fields, models


class DamageTypes(models.Model):
    """Model Damage Types."""

    _name = 'damage.types'
    _description = 'Damage Types'

    name = fields.Char(string='Name', traslate=True)
    code = fields.Char(string='Code')

    def copy(self, default=None):
        """Copy method cannot duplicate record and overide method."""
        if not default:
            default = {}
        raise Warning(_('You can\'t duplicate damage types!'))
	