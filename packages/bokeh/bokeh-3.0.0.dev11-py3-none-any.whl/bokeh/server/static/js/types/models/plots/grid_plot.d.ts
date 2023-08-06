import { LayoutDOM, LayoutDOMView } from "../layouts/layout_dom";
import { ToolbarBox, ToolbarBoxView } from "../tools/toolbar_box";
import { Toolbar } from "../tools/toolbar";
import { Grid, RowsSizing, ColsSizing } from "../../core/layout/grid";
import { CanvasLayer } from "../../core/util/canvas";
import { Location } from "../../core/enums";
import * as p from "../../core/properties";
export declare class GridPlotView extends LayoutDOMView {
    model: GridPlot;
    protected _toolbar: ToolbarBox;
    get toolbar_box_view(): ToolbarBoxView;
    initialize(): void;
    lazy_initialize(): Promise<void>;
    connect_signals(): void;
    remove(): void;
    private _tool_views;
    build_tool_views(): Promise<void>;
    get child_models(): LayoutDOM[];
    protected grid: Grid;
    protected grid_el: HTMLElement;
    render(): void;
    update_position(): void;
    _update_layout(): void;
    export(type?: "auto" | "png" | "svg", hidpi?: boolean): CanvasLayer;
}
export declare namespace GridPlot {
    type Attrs = p.AttrsOf<Props>;
    type Props = LayoutDOM.Props & {
        toolbar: p.Property<Toolbar>;
        toolbar_location: p.Property<Location | null>;
        children: p.Property<[LayoutDOM, number, number, number?, number?][]>;
        rows: p.Property<RowsSizing>;
        cols: p.Property<ColsSizing>;
        spacing: p.Property<number | [number, number]>;
    };
}
export interface GridPlot extends GridPlot.Attrs {
}
export declare class GridPlot extends LayoutDOM {
    properties: GridPlot.Props;
    __view_type__: GridPlotView;
    constructor(attrs?: Partial<GridPlot.Attrs>);
}
//# sourceMappingURL=grid_plot.d.ts.map