# See LICENSE file for full copyright and licensing details.
"""Res Users Models."""

from odoo import _, fields, api, models
from odoo.exceptions import UserError


class ResUsers(models.Model):
    """res users models."""

    _inherit = 'res.users'

    @api.model
    def read_group(self):
        """Read group method."""
        data_obj = self.env['ir.model.data']
        result = super(ResUsers, self).read_group()
        try:
            dummy, group_id = data_obj.sudo().get_object_reference('product', 'group_uom')
            result.append(group_id)
        except ValueError:
            pass
        return result

    _defaults = {
        'groups_id': read_group,
    }


class ResPartner(models.Model):
    """Model res partner extended."""

    _inherit = 'res.partner'

    d_id = fields.Char(string='ID-Card')
    is_driver = fields.Boolean(string='Is Driver')
    insurance = fields.Boolean(string='Insurance')
