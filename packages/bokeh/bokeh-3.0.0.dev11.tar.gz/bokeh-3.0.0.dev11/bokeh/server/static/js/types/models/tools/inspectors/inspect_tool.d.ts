import { Tool, ToolView } from "../tool";
import { PlotView } from "../../plots/plot";
import * as p from "../../../core/properties";
export declare abstract class InspectToolView extends ToolView {
    model: InspectTool;
    readonly parent: PlotView;
    get plot_view(): PlotView;
}
export declare namespace InspectTool {
    type Attrs = p.AttrsOf<Props>;
    type Props = Tool.Props & {
        toggleable: p.Property<boolean>;
    };
}
export interface InspectTool extends InspectTool.Attrs {
}
export declare abstract class InspectTool extends Tool {
    properties: InspectTool.Props;
    __view_type__: InspectToolView;
    constructor(attrs?: Partial<InspectTool.Attrs>);
    event_type: "move";
}
//# sourceMappingURL=inspect_tool.d.ts.map