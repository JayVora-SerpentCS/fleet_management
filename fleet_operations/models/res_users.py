# See LICENSE file for full copyright and licensing details.
"""Res Users Models."""

from odoo import _, fields, api, models
from odoo.exceptions import UserError


class ResPartner(models.Model):
    """Model res partner extended."""

    _inherit = 'res.partner'

    d_id = fields.Char(string='ID-Card')
    is_driver = fields.Boolean(string='Is Driver')
    insurance = fields.Boolean(string='Insurance')
