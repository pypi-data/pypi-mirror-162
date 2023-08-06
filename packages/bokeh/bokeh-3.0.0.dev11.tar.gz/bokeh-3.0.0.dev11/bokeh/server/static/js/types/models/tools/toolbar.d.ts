import { StyleSheetLike } from "../../core/dom";
import * as p from "../../core/properties";
import { DOMComponentView } from "../../core/dom_view";
import { Logo, Location } from "../../core/enums";
import { CanvasLayer } from "../../core/util/canvas";
import { BBox } from "../../core/util/bbox";
import { Model } from "../../model";
import { Tool } from "./tool";
import { ToolProxy, ToolLike } from "./tool_proxy";
import { ToolButtonView } from "./tool_button";
import { GestureTool } from "./gestures/gesture_tool";
import { InspectTool } from "./inspectors/inspect_tool";
import { ActionTool } from "./actions/action_tool";
import { HelpTool } from "./actions/help_tool";
import { ContextMenu } from "../../core/util/menus";
export declare class ToolbarView extends DOMComponentView {
    model: Toolbar;
    el: HTMLElement;
    readonly tool_button_views: Map<ToolLike<Tool>, ToolButtonView>;
    protected _overflow_menu: ContextMenu;
    protected _overflow_el?: HTMLElement;
    get overflow_el(): HTMLElement | undefined;
    private _visible;
    get visible(): boolean;
    initialize(): void;
    lazy_initialize(): Promise<void>;
    connect_signals(): void;
    styles(): StyleSheetLike[];
    remove(): void;
    protected _build_tool_button_views(): Promise<void>;
    set_visibility(visible: boolean): void;
    protected _on_visible_change(): void;
    render(): void;
    layout: {
        bbox: BBox;
    };
    update_layout(): void;
    update_position(): void;
    after_layout(): void;
    export(type?: "auto" | "png" | "svg", hidpi?: boolean): CanvasLayer;
}
export declare type GesturesMap = {
    pan: {
        tools: ToolLike<GestureTool>[];
        active: ToolLike<GestureTool> | null;
    };
    scroll: {
        tools: ToolLike<GestureTool>[];
        active: ToolLike<GestureTool> | null;
    };
    pinch: {
        tools: ToolLike<GestureTool>[];
        active: ToolLike<GestureTool> | null;
    };
    tap: {
        tools: ToolLike<GestureTool>[];
        active: ToolLike<GestureTool> | null;
    };
    doubletap: {
        tools: ToolLike<GestureTool>[];
        active: ToolLike<GestureTool> | null;
    };
    press: {
        tools: ToolLike<GestureTool>[];
        active: ToolLike<GestureTool> | null;
    };
    pressup: {
        tools: ToolLike<GestureTool>[];
        active: ToolLike<GestureTool> | null;
    };
    rotate: {
        tools: ToolLike<GestureTool>[];
        active: ToolLike<GestureTool> | null;
    };
    move: {
        tools: ToolLike<GestureTool>[];
        active: ToolLike<GestureTool> | null;
    };
    multi: {
        tools: ToolLike<GestureTool>[];
        active: ToolLike<GestureTool> | null;
    };
};
export declare type GestureType = keyof GesturesMap;
export declare type Drag = Tool;
export declare const Drag: typeof Tool;
export declare type Inspection = Tool;
export declare const Inspection: typeof Tool;
export declare type Scroll = Tool;
export declare const Scroll: typeof Tool;
export declare type Tap = Tool;
export declare const Tap: typeof Tool;
declare type ActiveGestureToolsProps = {
    active_drag: p.Property<ToolLike<Drag> | "auto" | null>;
    active_scroll: p.Property<ToolLike<Scroll> | "auto" | null>;
    active_tap: p.Property<ToolLike<Tap> | "auto" | null>;
    active_multi: p.Property<ToolLike<GestureTool> | "auto" | null>;
};
export declare namespace Toolbar {
    type Attrs = p.AttrsOf<Props>;
    type Props = Model.Props & {
        tools: p.Property<(Tool | ToolProxy<Tool>)[]>;
        logo: p.Property<Logo | null>;
        autohide: p.Property<boolean>;
        toolbar_location: p.Property<Location>;
        gestures: p.Property<GesturesMap>;
        actions: p.Property<ToolLike<ActionTool>[]>;
        inspectors: p.Property<ToolLike<InspectTool>[]>;
        help: p.Property<ToolLike<HelpTool>[]>;
    } & ActiveGestureToolsProps & {
        active_inspect: p.Property<ToolLike<Inspection> | ToolLike<Inspection>[] | "auto" | null>;
    };
}
export interface Toolbar extends Toolbar.Attrs {
}
export declare class Toolbar extends Model {
    properties: Toolbar.Props;
    __view_type__: ToolbarView;
    constructor(attrs?: Partial<Toolbar.Attrs>);
    get horizontal(): boolean;
    get vertical(): boolean;
    connect_signals(): void;
    initialize(): void;
    protected _init_tools(): void;
    protected _activate_tools(): void;
    _active_change(tool: ToolLike<GestureTool>): void;
}
export {};
//# sourceMappingURL=toolbar.d.ts.map