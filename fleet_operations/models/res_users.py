# See LICENSE file for full copyright and licensing details.
"""Res Users Models."""

from odoo import _, fields, api, models


class ResUsers(models.Model):
    """res users models."""

    _inherit = 'res.users'

    @api.model
    def read_group(self):
        """Read group method."""
        dataobj = self.env['ir.model.data']
        result = super(ResUsers, self).read_group()
        try:
            dummy, group_id = dataobj.sudo().get_object_reference('product',
                                                                  'group_uom')
            result.append(group_id)
        except ValueError:
            pass
        return result

    _defaults = {
        'groups_id': read_group,
    }

    @api.model_create_multi
    def create(self, vals_list):
        """Create method to the users."""
        users = super(ResUsers, self.with_context(
            default_customer=False)).create(vals_list)
        for user in users:
            user.partner_id.active = user.active
            if user.partner_id.company_id:
                user.partner_id.write({'company_id': user.company_id.id})
        return users


class ResPartnerExtended(models.Model):
    """Model res partner extended."""

    _inherit = 'res.partner'

    d_id = fields.Char(string='ID-Card', size=64)
    is_driver = fields.Boolean(string='Is Driver')
    insurance = fields.Boolean(string='Insurance')

    def copy(self, default=None):
        """Copy method cannot duplicate record and overide method."""
        if not default:
            default = {}
        raise Warning(_('You can\'t duplicate record!'))
        return super(ResPartnerExtended, self).copy(default=default)