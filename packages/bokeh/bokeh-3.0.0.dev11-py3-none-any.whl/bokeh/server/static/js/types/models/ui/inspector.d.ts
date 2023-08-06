import { UIElement, UIElementView } from "./ui_element";
import * as p from "../../core/properties";
import { StyleSheetLike } from "../../core/dom";
import { Model } from "../../model";
import { PlainObject } from "../../core/types";
export declare class HTMLPrinter {
    readonly click: (obj: unknown) => void;
    readonly max_items: number;
    readonly max_depth: number;
    protected readonly visited: WeakSet<object>;
    protected depth: number;
    constructor(click: (obj: unknown) => void, max_items: number, max_depth: number);
    to_html(obj: unknown): HTMLElement;
    null(): HTMLElement;
    token(val: string): HTMLElement;
    boolean(val: boolean): HTMLElement;
    number(val: number): HTMLElement;
    string(val: string): HTMLElement;
    symbol(val: symbol): HTMLElement;
    array(obj: unknown[]): HTMLElement;
    iterable(obj: Iterable<unknown>): HTMLElement;
    object(obj: PlainObject): HTMLElement;
    model(obj: Model): HTMLElement;
    property(obj: p.Property): HTMLElement;
}
export declare class InspectorView extends UIElementView {
    model: Inspector;
    initialize(): void;
    styles(): StyleSheetLike[];
    private prev_listener;
    private watched_props;
    render(): void;
}
export declare namespace Inspector {
    type Attrs = p.AttrsOf<Props>;
    type Props = UIElement.Props;
}
export interface Inspector extends Inspector.Attrs {
}
export declare class Inspector extends UIElement {
    properties: Inspector.Props;
    __view_type__: InspectorView;
    constructor(attrs?: Partial<Inspector.Attrs>);
}
//# sourceMappingURL=inspector.d.ts.map