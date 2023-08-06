import * as p from "../../core/properties";
import { EventType } from "../../core/ui_events";
import { Signal0 } from "../../core/signaling";
import { Class } from "../../core/class";
import { Model } from "../../model";
import { Tool } from "./tool";
import { ToolButtonView } from "./tool_button";
import { Renderer } from "../renderers/renderer";
import { MenuItem } from "../../core/util/menus";
export declare type ToolLike<T extends Tool> = T | ToolProxy<T>;
export declare namespace ToolProxy {
    type Attrs<T extends Tool> = p.AttrsOf<Props<T>>;
    type Props<T extends Tool> = Model.Props & {
        tools: p.Property<T[]>;
        active: p.Property<boolean>;
        disabled: p.Property<boolean>;
    };
}
export interface ToolProxy<T extends Tool> extends ToolProxy.Attrs<T> {
}
export declare class ToolProxy<T extends Tool> extends Model {
    properties: ToolProxy.Props<T>;
    constructor(attrs?: Partial<ToolProxy.Attrs<T>>);
    do: Signal0<this>;
    get underlying(): Tool;
    get button_view(): Class<ToolButtonView>;
    get event_type(): EventType | EventType[];
    get default_order(): number;
    get tooltip(): string;
    get tool_name(): string;
    get computed_icon(): string | undefined;
    get toggleable(): boolean;
    get computed_overlays(): Renderer[];
    initialize(): void;
    connect_signals(): void;
    doit(): void;
    set_active(): void;
    get menu(): MenuItem[] | null;
}
//# sourceMappingURL=tool_proxy.d.ts.map