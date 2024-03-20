/* @odoo-module */

import {onPatched, onWillDestroy, onWillPatch, useRef, useState} from "@odoo/owl";
import {useBus, useService} from "@web/core/utils/hooks";
import {KanbanRenderer} from "@web/views/kanban/kanban_renderer";
import {patch} from "@web/core/utils/patch";
import {registry} from "@web/core/registry";
import {useBounceButton} from "@web/views/view_hook";
import {useHotkey} from "@web/core/hotkeys/hotkey_hook";
import {useSortable} from "@web/core/utils/sortable_owl";

function validateColumnQuickCreateExamples(data) {
    const {allowedGroupBys = [], examples = [], foldField = ""} = data;
    if (!allowedGroupBys.length) {
        throw new Error("The example data must contain an array of allowed groupbys");
    }
    if (!examples.length) {
        throw new Error("The example data must contain an array of examples");
    }
    const someHasFoldedColumns = examples.some(
        ({foldedColumns = []}) => foldedColumns.length
    );
    if (!foldField && someHasFoldedColumns) {
        throw new Error(
            "The example data must contain a fold field if there are folded columns"
        );
    }
}

patch(KanbanRenderer.prototype, {
    setup() {
        this.dialogClose = [];
        /**
         * @type {{ processedIds: string[], columnQuickCreateIsFolded: boolean }}
         */
        this.state = useState({
            processedIds: [],
            columnQuickCreateIsFolded:
                !this.props.list.isGrouped || this.props.list.groups.length > 0,
        });
        this.dialog = useService("dialog");
        this.exampleData = registry
            .category("kanban_examples")
            .get(this.props.archInfo.examples, null);
        if (this.exampleData) {
            validateColumnQuickCreateExamples(this.exampleData);
        }
        this.ghostColumns = this.generateGhostColumns();

        // Sortable
        let dataRecordId = "";
        let dataGroupId = "";
        this.rootRef = useRef("root");
        if (
            this.canUseSortable &&
            this.props.list.model.config.resModel === "fleet.vehicle"
        ) {
            useSortable({
                enable: () => this.canResequenceGroups,
                // Params
                ref: this.rootRef,
                elements: ".o_group_draggable",
                handle: ".o_column_title",
                cursor: "move",
                // Hooks
                onDragStart: (params) => {
                    const {element} = params;
                    dataGroupId = element.dataset.id;
                    return this.sortStart(params);
                },
                onDragEnd: (params) => this.sortStop(params),
                onDrop: (params) => this.sortGroupDrop(dataGroupId, params),
            });
        } else {
            useSortable({
                enable: () => this.canResequenceRecords,
                // Params
                ref: this.rootRef,
                elements: ".o_draggable",
                ignore: ".dropdown",
                groups: () => this.props.list.isGrouped && ".o_kanban_group",
                connectGroups: () => this.canMoveRecords,
                cursor: "move",
                // Hooks
                onDragStart: (params) => {
                    const {element, group} = params;
                    dataRecordId = element.dataset.id;
                    dataGroupId = group && group.dataset.id;
                    return this.sortStart(params);
                },
                onDragEnd: (params) => this.sortStop(params),
                onGroupEnter: (params) => this.sortRecordGroupEnter(params),
                onGroupLeave: (params) => this.sortRecordGroupLeave(params),
                onDrop: (params) =>
                    this.sortRecordDrop(dataRecordId, dataGroupId, params),
            });
            useSortable({
                enable: () => this.canResequenceGroups,
                // Params
                ref: this.rootRef,
                elements: ".o_group_draggable",
                handle: ".o_column_title",
                cursor: "move",
                // Hooks
                onDragStart: (params) => {
                    const {element} = params;
                    dataGroupId = element.dataset.id;
                    return this.sortStart(params);
                },
                onDragEnd: (params) => this.sortStop(params),
                onDrop: (params) => this.sortGroupDrop(dataGroupId, params),
            });
        }

        useBounceButton(this.rootRef, (clickedEl) => {
            if (!this.props.list.count || this.props.list.model.useSampleModel) {
                return clickedEl.matches(
                    [
                        ".o_kanban_renderer",
                        ".o_kanban_group",
                        ".o_kanban_header",
                        ".o_column_quick_create",
                        ".o_view_nocontent_smiling_face",
                    ].join(", ")
                );
            }
            return false;
        });
        onWillDestroy(() => {
            this.dialogClose.forEach((close) => close());
        });

        if (this.env.searchModel) {
            useBus(this.env.searchModel, "focus-view", () => {
                const {model} = this.props.list;
                if (model.useSampleModel || !model.hasData()) {
                    return;
                }
                const firstCard = this.rootRef.el.querySelector(".o_kanban_record");
                if (firstCard) {
                    // Focus first kanban card
                    firstCard.focus();
                }
            });
        }

        useHotkey(
            "Enter",
            ({target}) => {
                if (!target.classList.contains("o_kanban_record")) {
                    return;
                }

                // Open first link
                const firstLink = target.querySelector(
                    ".oe_kanban_global_click, a, button"
                );
                if (firstLink && firstLink instanceof HTMLElement) {
                    firstLink.click();
                }
                return;
            },
            {area: () => this.rootRef.el}
        );

        const arrowsOptions = {area: () => this.rootRef.el, allowRepeat: true};
        if (this.env.searchModel) {
            useHotkey(
                "ArrowUp",
                ({area}) => {
                    if (!this.focusNextCard(area, "up")) {
                        this.env.searchModel.trigger("focus-search");
                    }
                },
                arrowsOptions
            );
        }
        useHotkey(
            "ArrowDown",
            ({area}) => this.focusNextCard(area, "down"),
            arrowsOptions
        );
        useHotkey(
            "ArrowLeft",
            ({area}) => this.focusNextCard(area, "left"),
            arrowsOptions
        );
        useHotkey(
            "ArrowRight",
            ({area}) => this.focusNextCard(area, "right"),
            arrowsOptions
        );

        let previousScrollTop = 0;
        onWillPatch(() => {
            previousScrollTop = this.rootRef.el.scrollTop;
        });
        onPatched(() => {
            this.rootRef.el.scrollTop = previousScrollTop;
        });
    },
});
