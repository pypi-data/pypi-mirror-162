import { Widget, WidgetView } from "./widget";
import { StyleSheetLike } from "../../core/dom";
import * as p from "../../core/properties";
export declare class SwitchView extends WidgetView {
    model: Switch;
    protected knob_el: HTMLElement;
    protected bar_el: HTMLElement;
    connect_signals(): void;
    styles(): StyleSheetLike[];
    render(): void;
    protected _update_active(): void;
    protected _update_disabled(): void;
}
export declare namespace Switch {
    type Attrs = p.AttrsOf<Props>;
    type Props = Widget.Props & {
        active: p.Property<boolean>;
    };
}
export interface Switch extends Switch.Attrs {
}
export declare class Switch extends Widget {
    properties: Switch.Props;
    __view_type__: SwitchView;
    constructor(attrs?: Partial<Switch.Attrs>);
}
//# sourceMappingURL=switch.d.ts.map