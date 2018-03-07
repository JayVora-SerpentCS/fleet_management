# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields
import logging
_logger = logging.getLogger(__name__)


class service_department(models.Model):
    _name = 'service.department'

    code = fields.Char(string='Code', size=3,
                       required=True, translate=True)
    name = fields.Char(string='Name', required=True,
                       translate=True)

    _sql_constraints = [('service.department_uniq', 'unique(name)',
                         'This registration state is already exist!')]
