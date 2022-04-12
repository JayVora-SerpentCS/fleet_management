odoo.define("fleet_operations.disable_drag_drop_kanban",function(require){

    var KanbanView = require('web.KanbanView');
    var KanbanColumn = require('web.KanbanColumn');
    var quick_create = require('web.kanban_quick_create');
    var ColumnQuickCreate = quick_create.ColumnQuickCreate;

    KanbanView.include({
        render_grouped: function (fragment) {
            var self = this;

            // Drag'n'drop activation/deactivation
            var group_by_field_attrs = this.fields[this.group_by_field];

            // Deactivate the drag'n'drop if:
            // - field is a date or datetime since we group by month
            // - field is readonly
            var draggable = true;
            if (group_by_field_attrs) {
                if (group_by_field_attrs.type === "date" || group_by_field_attrs.type === "datetime") {
                    var draggable = false;
                }
                else if (group_by_field_attrs.readonly !== undefined) {
                    var draggable = !(group_by_field_attrs.readonly);
                }
            }
            if(self.model == "fleet.vehicle" || self.model == "account.analytic.account"){
                draggable = false
            }
            var record_options = _.extend(this.record_options, {
                draggable: draggable,
            });

            var column_options = this.get_column_options();

            _.each(this.data.groups, function (group) {
                var column = new KanbanColumn(self, group, column_options, record_options);
                column.appendTo(fragment);
                self.widgets.push(column);
            });
            this.$el.sortable({
                axis: 'x',
                items: '> .o_kanban_group',
                handle: '.o_kanban_header',
                cursor: 'move',
                revert: 150,
                delay: 100,
                tolerance: 'pointer',
                forcePlaceholderSize: true,
                stop: function () {
                    var ids = [];
                    self.$('.o_kanban_group').each(function (index, u) {
                        ids.push($(u).data('id'));
                    });
                    self.resequence(ids);
                },
            });
            if (this.is_action_enabled('group_create') && this.grouped_by_m2o) {
                this.column_quick_create = new ColumnQuickCreate(this);
                this.column_quick_create.appendTo(fragment);
            }
            this.postprocess_m2m_tags();
        },
    });

});