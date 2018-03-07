# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from openerp import SUPERUSER_ID
from openerp import api


def pre_init_hook(cr):
    cr.execute("""
         UPDATE fleet_vehicle SET driver_id = NULL """)
    cr.commit()
    cr.execute("""
                UPDATE fleet_vehicle_log_services SET purchaser_id = NULL""")
    cr.commit()
