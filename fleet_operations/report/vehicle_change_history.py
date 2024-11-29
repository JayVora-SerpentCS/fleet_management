# # See LICENSE file for full copyright and licensing details.
# """Vehicle Change History Report."""

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
        models_to_check = {
            "engine_history": self.env["engine.history"],
            "color_history": self.env["color.history"],
            "tire_history": self.env["tire.history"],
            "battery_history": self.env["battery.history"],
            "vin_history": self.env["vin.history"],
        }
        domain = []
        if date_range.get("date_from"):
            domain += [("changed_date", ">=", date_range.get("date_from"))]
        if date_range.get("date_to"):
            domain += [("changed_date", "<=", date_range.get("date_to"))]
        if date_range.get("fleet_id"):
            domain += [("vehicle_id", "=", date_range.get("fleet_id"))]

        vehicle_change_history = []
        for report_type, model_obj in models_to_check.items():
            if date_range.get("report") == report_type:
                records = model_obj.search(domain)
                for rec in records:
                    seq = rec.vehicle_id and rec.vehicle_id.name or ""
                    changed_date = (
                        format_date(
                            self.env,
                            rec.changed_date,
                            self._context.get("lang"),
                            date_format=False,
                        )
                        if rec.changed_date
                        else False
                    )

                    work_order_date = (
                        format_date(
                            self.env,
                            rec.workorder_id.date_close,
                            self._context.get("lang"),
                            date_format=False,
                        )
                        if rec.workorder_id and rec.workorder_id.date_close
                        else False
                    )

                    values = {
                        "description": seq,
                        "vehicle_type": rec.vehicle_id
                        and rec.vehicle_id.vechical_type_id
                        and rec.vehicle_id.vechical_type_id.name
                        or "",
                        "color_id": rec.vehicle_id
                        and rec.vehicle_id.vehical_color_id
                        and rec.vehicle_id.vehical_color_id.name
                        or "",
                        "vin": rec.vehicle_id and rec.vehicle_id.vin_sn or "",
                        "plate": rec.vehicle_id and rec.vehicle_id.license_plate or "",
                        "new_engine": rec.new_engine_no
                        if report_type == "engine_history"
                        else "",
                        "old_engine": rec.previous_engine_no
                        if report_type == "engine_history"
                        else "",
                        "new_color": rec.current_color_id.name
                        if report_type == "color_history"
                        else "",
                        "old_color": rec.previous_color_id.name
                        if report_type == "color_history"
                        else "",
                        "new_tire": rec.new_tire_size
                        if report_type == "tire_history"
                        else "",
                        "old_tire": rec.previous_tire_size
                        if report_type == "tire_history"
                        else "",
                        "new_battery": rec.new_battery_size
                        if report_type == "battery_history"
                        else "",
                        "old_battery": rec.previous_battery_size
                        if report_type == "battery_history"
                        else "",
                        "old_vin": "",
                        "new_vin": "",
                        "change_date": changed_date,
                        "work_order": rec.workorder_id and rec.workorder_id.name or "",
                        "wo_close_date": work_order_date,
                        "remarks": rec.note or "",
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
