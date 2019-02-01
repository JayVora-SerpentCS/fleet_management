from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    din_number = fields.Char(string="DIN", help="Dealer Identification Number")
