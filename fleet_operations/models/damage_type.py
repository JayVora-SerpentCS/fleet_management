# See LICENSE file for full copyright and licensing details.
"""Damage Type models."""

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class DamageTypes(models.Model):
    """Model Damage Types."""

    _name = 'damage.types'
    _description = 'Damage Types'

    name = fields.Char(string='Name', traslate=True)
    code = fields.Char(string='Code')

    @api.constrains('name')
    def _check_duplicate_damage_type(self):
        """Method to check duplicate damage type."""
        for damage in self:
            if self.search_count([
                ('name', 'ilike', damage.name.strip()),
                ('id', '!=', damage.id)
            ]):
                raise ValidationError(_("Damage types with this name "
                                        "already exists!"))
