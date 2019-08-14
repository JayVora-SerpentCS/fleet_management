# See LICENSE file for full copyright and licensing details.
"""Service department models."""

from odoo import fields, models


class ServiceDepartment(models.Model):
    """service Department."""

    _name = 'service.department'
    _description = 'Service Department'

    code = fields.Char(string='Code', size=3,
                       required=True, translate=True)
    name = fields.Char(string='Name', required=True,
                       translate=True)

    _sql_constraints = [('service.department_uniq', 'unique(name)',
                         'This registration state is already exist!')]
