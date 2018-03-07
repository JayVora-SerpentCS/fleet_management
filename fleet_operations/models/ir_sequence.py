# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from openerp import models, api


class ir_sequence(models.Model):
    _inherit = 'ir.sequence'

    _defaults = {
        'padding': 4,
    }

    @api.model
    def create(self, vals):
        seq = super(ir_sequence, self).create(vals)
        code_code = ""
        sequence_type_obj = self.env['ir.sequence.type']
        if seq:
            code_code = seq.name[0:20]
            sequence_type_obj.create(
                           {'name': code_code, 'code': code_code})
            seq.code = code_code
        return seq
