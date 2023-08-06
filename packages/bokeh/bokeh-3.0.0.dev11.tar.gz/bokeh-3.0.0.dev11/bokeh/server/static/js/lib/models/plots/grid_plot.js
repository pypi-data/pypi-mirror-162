var _a;
import { LayoutDOM, LayoutDOMView } from "../layouts/layout_dom";
import { ToolbarBox, ToolbarBoxView } from "../tools/toolbar_box";
import { Toolbar } from "../tools/toolbar";
import { ActionTool } from "../tools/actions/action_tool";
import { Grid, Row, Column } from "../../core/layout/grid";
import { CanvasLayer } from "../../core/util/canvas";
import { build_views, remove_views } from "../../core/build_views";
import { Location } from "../../core/enums";
import { div, position } from "../../core/dom";
export class GridPlotView extends LayoutDOMView {
    constructor() {
        super(...arguments);
        this._tool_views = new Map();
    }
    get toolbar_box_view() {
        return this.child_views.find((v) => v.model == this._toolbar);
    }
    initialize() {
        super.initialize();
        const { toolbar, toolbar_location } = this.model;
        this._toolbar = new ToolbarBox({ toolbar, toolbar_location: toolbar_location ?? "above" });
    }
    async lazy_initialize() {
        await super.lazy_initialize();
        await this.build_tool_views();
    }
    connect_signals() {
        super.connect_signals();
        const { toolbar, toolbar_location, children, rows, cols, spacing } = this.model.properties;
        this.on_change(toolbar_location, () => {
            const { toolbar_location } = this.model;
            this._toolbar.toolbar_location = toolbar_location ?? "above";
        });
        this.on_change([toolbar, toolbar_location, children, rows, cols, spacing], () => {
            this.rebuild();
        });
        this.on_change(this.model.toolbar.properties.tools, async () => {
            await this.build_tool_views();
        });
    }
    remove() {
        remove_views(this._tool_views);
        super.remove();
    }
    async build_tool_views() {
        const tools = this.model.toolbar.tools.filter((tool) => tool instanceof ActionTool);
        await build_views(this._tool_views, tools, { parent: this });
    }
    get child_models() {
        return [this._toolbar, ...this.model.children.map(([child]) => child)];
    }
    render() {
        super.render();
        this.grid_el = div({ style: { position: "absolute" } });
        this.shadow_el.appendChild(this.grid_el);
        for (const child_view of this.child_views) {
            if (child_view instanceof ToolbarBoxView)
                continue;
            this.grid_el.appendChild(child_view.el);
        }
    }
    update_position() {
        super.update_position();
        position(this.grid_el, this.grid.bbox);
    }
    _update_layout() {
        const grid = this.grid = new Grid();
        grid.rows = this.model.rows;
        grid.cols = this.model.cols;
        grid.spacing = this.model.spacing;
        for (const [child, row, col, row_span, col_span] of this.model.children) {
            const child_view = this._child_views.get(child);
            grid.items.push({ layout: child_view.layout, row, col, row_span, col_span });
        }
        grid.set_sizing(this.box_sizing());
        const { toolbar_location } = this.model;
        if (toolbar_location == null)
            this.layout = grid;
        else {
            this.layout = (() => {
                const tb = this.toolbar_box_view.layout;
                switch (toolbar_location) {
                    case "above": return new Column([tb, grid]);
                    case "below": return new Column([grid, tb]);
                    case "left": return new Row([tb, grid]);
                    case "right": return new Row([grid, tb]);
                }
            })();
            this.layout.set_sizing(this.box_sizing());
        }
    }
    export(type = "auto", hidpi = true) {
        const output_backend = (() => {
            switch (type) {
                case "auto": // TODO: actually infer the best type
                case "png": return "canvas";
                case "svg": return "svg";
            }
        })();
        const composite = new CanvasLayer(output_backend, hidpi);
        const { x, y, width, height } = this.grid.bbox.relative();
        composite.resize(width, height);
        composite.ctx.save();
        const bg_color = getComputedStyle(this.el).backgroundColor;
        composite.ctx.fillStyle = bg_color;
        composite.ctx.fillRect(x, y, width, height);
        for (const view of this.child_views) {
            const region = view.export(type, hidpi);
            const { x, y } = view.layout.bbox;
            composite.ctx.drawImage(region.canvas, x, y);
        }
        composite.ctx.restore();
        return composite;
    }
}
GridPlotView.__name__ = "GridPlotView";
export class GridPlot extends LayoutDOM {
    constructor(attrs) {
        super(attrs);
    }
}
_a = GridPlot;
GridPlot.__name__ = "GridPlot";
(() => {
    _a.prototype.default_view = GridPlotView;
    _a.define(({ Any, Int, Number, Tuple, Array, Ref, Or, Opt, Nullable }) => ({
        toolbar: [Ref(Toolbar), () => new Toolbar()],
        toolbar_location: [Nullable(Location), "above"],
        children: [Array(Tuple(Ref(LayoutDOM), Int, Int, Opt(Int), Opt(Int))), []],
        rows: [Any /*TODO*/, "auto"],
        cols: [Any /*TODO*/, "auto"],
        spacing: [Or(Number, Tuple(Number, Number)), 0],
    }));
})();
//# sourceMappingURL=grid_plot.js.map