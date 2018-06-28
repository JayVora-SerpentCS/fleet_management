# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, api


class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.model
    def _get_group(self):
        dataobj = self.env['ir.model.data']
        result = super(ResUsers, self)._get_group()
        try:
            dummy, group_id = dataobj.sudo().get_object_reference('product',
                                                                  'group_uom')
            result.append(group_id)
        except ValueError:
            pass
        return result

    _defaults = {
        'groups_id': _get_group,
    }
