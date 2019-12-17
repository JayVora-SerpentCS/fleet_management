# See LICENSE file for full copyright and licensing details.
"""This is model is update pending history."""

from odoo import api, fields, models


class UpdatePendingRepairHistory(models.Model):
    """Update Pending History."""

    _name = 'update.pending.repair.history'
    _description = 'Update Pending Repair History'

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle ID", size=64)
    fmp_id = fields.Char("Vehicle", char="128")
    pending_reapir_ids = fields.Many2many("pending.repair.type",
                                          "update_pending_history_rel",
                                          "pending_history_id",
                                          "pending_type_id",
                                          string="Vehicle Pending History")
    user_id = fields.Many2one("res.users", string="Applied By", readonly=True)
    state = fields.Selection([('draft', 'New'),
                              ('confirm', 'Applied')],
                             string="Status", default='draft')
    note = fields.Text(string="Note", translate=True)
    pending_reapir_history_ids = \
        fields.One2many('pending.applied.history', "updated_pending_id",
                        string="Pending Applied History", readonly=True)

    @api.onchange('vehicle_id')
    def get_fmp_id_info(self):
        """Onchange Method."""
        if self.vehicle_id:
            self.fmp_id = self.vehicle_id.name or ""
            
    def remove_selected_pending(self):
        """Method use to remove pending repair line.

        From vehicle service history after completed pending repair history.
        """
        applied_pending_obj = self.env['pending.applied.history']
        for pending in self:
            for applied_pending in pending.pending_reapir_ids:
                applied_pending_obj.create({
                    'updated_pending_id': pending.id,
                    'vehicle_rep_type_id':
                    applied_pending.vehicle_rep_type_id and
                    applied_pending.vehicle_rep_type_id.id or False,
                    'repair_type_id': applied_pending.repair_type_id and
                    applied_pending.repair_type_id.id or False,
                    'name': applied_pending.name or "",
                    'categ_id': applied_pending.categ_id and
                    applied_pending.categ_id.id or False,
                    'issue_date': applied_pending.issue_date,
                    'state': "complete",
                    "user_id": applied_pending.user_id and
                    applied_pending.user_id.id or False})
                applied_pending.unlink()
            pending.write({'state': 'confirm', 'user_id': self._uid})
        return True


class PendingAppliedHistory(models.Model):
    """Pending Applied History."""

    _name = 'pending.applied.history'
    _description = 'Pending applied History'

    updated_pending_id = fields.Many2one("update.pending.repair.history",
                                         string="Update Pending")
    vehicle_rep_type_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    repair_type_id = fields.Many2one('repair.type', string="Repair Type")
    name = fields.Char(string='Work Order #')
    categ_id = fields.Many2one("service.category", string="Category")
    issue_date = fields.Date(string="Issue Date")
    state = fields.Selection([('complete', 'Complete'),
                              ('in-complete', 'In Complete')], string="Status")
    user_id = fields.Many2one('res.users', string="By")
