import { Tool, ToolView } from "../tool";
import { ToolButtonView } from "../tool_button";
import { LayoutDOMView } from "../../layouts/layout_dom";
import { Signal } from "../../../core/signaling";
import * as p from "../../../core/properties";
export declare class ActionToolButtonView extends ToolButtonView {
    model: ActionTool;
    protected _clicked(): void;
}
export declare abstract class ActionToolView extends ToolView {
    model: ActionTool;
    readonly parent: LayoutDOMView;
    connect_signals(): void;
    abstract doit(arg?: unknown): void;
}
export declare namespace ActionTool {
    type Attrs = p.AttrsOf<Props>;
    type Props = Tool.Props;
}
export interface ActionTool extends ActionTool.Attrs {
}
export declare abstract class ActionTool extends Tool {
    properties: ActionTool.Props;
    __view_type__: ActionToolView;
    constructor(attrs?: Partial<ActionTool.Attrs>);
    button_view: typeof ActionToolButtonView;
    do: Signal<string | undefined, this>;
}
//# sourceMappingURL=action_tool.d.ts.map