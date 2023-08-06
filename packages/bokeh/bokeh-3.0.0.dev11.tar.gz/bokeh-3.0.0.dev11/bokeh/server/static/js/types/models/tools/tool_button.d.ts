import { DOMElementView, DOMComponentView } from "../../core/dom_view";
import { StyleSheetLike } from "../../core/dom";
import type { ToolbarView } from "./toolbar";
import type { Tool } from "./tool";
export declare abstract class ToolButtonView extends DOMElementView {
    model: Tool;
    readonly parent: ToolbarView;
    readonly root: DOMComponentView;
    private _hammer?;
    private _menu?;
    initialize(): void;
    connect_signals(): void;
    remove(): void;
    styles(): StyleSheetLike[];
    css_classes(): string[];
    render(): void;
    protected abstract _clicked(): void;
    protected _pressed(): void;
}
//# sourceMappingURL=tool_button.d.ts.map