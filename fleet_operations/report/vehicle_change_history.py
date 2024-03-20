# See LICENSE file for full copyright and licensing details.
"""Vehicle Change History Report."""

import time

from odoo import _, api, models
from odoo.exceptions import UserError
from odoo.tools import format_date


class VehicalChangeHistoryReport(models.AbstractModel):
    """Vehicle change history report."""

    _name = "report.fleet_operations.vehicle_change_history_qweb"
    _description = "Vehicle Change History Report"

    def get_vehicle_history(self, date_range):
        """Method to get vehicle history."""
        engine_obj = self.env["engine.history"]
        color_obj = self.env["color.history"]
        tire_obj = self.env["tire.history"]
        battery_obj = self.env["battery.history"]
        vin_obj = self.env["vin.history"]
        domain = []
        if date_range.get("date_from"):
            domain += [("changed_date", ">=", date_range.get("date_from"))]
        if date_range.get("date_to"):
            domain += [("changed_date", "<=", date_range.get("date_to"))]
        if date_range.get("fleet_id"):
            domain += [("vehicle_id", "=", date_range.get("fleet_id"))]

        engine_ids = engine_obj.search(domain)
        color_ids = color_obj.search(domain)
        tire_ids = tire_obj.search(domain)
        battery_ids = battery_obj.search(domain)
        vin_ids = vin_obj.search(domain)
        vehicle_change_history = []
        changed_date = False
        work_order_date = False
        if (
            engine_ids
            and date_range.get("report") == "engine_history"
            or color_ids
            and date_range.get("report") == "color_history"
            or tire_ids
            and date_range.get("report") == "tire_history"
            or battery_ids
            and date_range.get("report") == "battery_history"
            or vin_ids
        ):
            for engine_rec in (
                engine_ids or color_ids or tire_ids or battery_ids or vin_ids
            ):
                seq = engine_rec.vehicle_id and engine_rec.vehicle_id.name or ""
                if engine_rec.changed_date:
                    changed_date = format_date(
                        self.env,
                        engine_rec.changed_date,
                        self._context.get("lang"),
                        date_format=False,
                    )
                if engine_rec.workorder_id and engine_rec.workorder_id.date_close:
                    work_order_date = format_date(
                        self.env,
                        engine_rec.workorder_id.date_close,
                        self._context.get("lang"),
                        date_format=False,
                    )

                values = {
                    "description": seq,
                    "vehicle_type": engine_rec.vehicle_id
                    and engine_rec.vehicle_id.vechical_type_id
                    and engine_rec.vehicle_id.vechical_type_id.name
                    or "",
                    "color_id": engine_rec.vehicle_id
                    and engine_rec.vehicle_id.vehical_color_id
                    and engine_rec.vehicle_id.vehical_color_id.name
                    or "",
                    "vin": engine_rec.vehicle_id and engine_rec.vehicle_id.vin_sn or "",
                    "plate": engine_rec.vehicle_id
                    and engine_rec.vehicle_id.license_plate
                    or "",
                    "old_engine": engine_rec.previous_engine_no or "",
                    "new_engine": engine_rec.new_engine_no or "",
                    "old_color": "",
                    "new_color": "",
                    "old_vin": "",
                    "new_vin": "",
                    "change_date": changed_date if changed_date else False,
                    "work_order": engine_rec.workorder_id
                    and engine_rec.workorder_id.name
                    or "",
                    "wo_close_date": work_order_date if work_order_date else False,
                    "remarks": engine_rec.note or "",
                    "seq": seq + "a",
                }
                vehicle_change_history.append(values)

        if vehicle_change_history:
            vehicle_change_history = sorted(
                vehicle_change_history, key=lambda k: k["seq"]
            )
        return vehicle_change_history

    @api.model
    def _get_report_values(self, docids, data=None):
        if (
            not data.get("form")
            or not self.env.context.get("active_model")
            or not self.env.context.get("active_id")
        ):
            msg = _(
                "Form content is missing, \
                    this report cannot be printed."
            )
            raise UserError(msg)

        model = self.env.context.get("active_model")
        docs = self.env[model].browse(self.env.context.get("active_id"))
        result = self.get_vehicle_history(data.get("form"))
        return {
            "doc_ids": self.ids,
            "doc_model": model,
            "data": data["form"],
            "docs": docs,
            "time": time,
            "get_vehicle_history": result,
        }
