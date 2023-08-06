import { View } from "./view";
import { StyleSheet, ImportedStyleSheet, StyleSheetLike } from "./dom";
export interface DOMView extends View {
    constructor: Function & {
        tag_name: keyof HTMLElementTagNameMap;
    };
}
export declare abstract class DOMView extends View {
    static tag_name: keyof HTMLElementTagNameMap;
    el: Node;
    shadow_el?: ShadowRoot;
    get children_el(): Node;
    readonly root: DOMView;
    initialize(): void;
    remove(): void;
    css_classes(): string[];
    styles(): StyleSheetLike[];
    abstract render(): void;
    renderTo(element: Node): void;
    protected _createElement(): this["el"];
}
export declare abstract class DOMElementView extends DOMView {
    el: HTMLElement;
}
export declare abstract class DOMComponentView extends DOMElementView {
    parent: DOMElementView | null;
    readonly root: DOMComponentView;
    shadow_el: ShadowRoot;
    protected readonly _stylesheets: (StyleSheet | ImportedStyleSheet)[];
    initialize(): void;
    styles(): StyleSheetLike[];
    empty(): void;
}
//# sourceMappingURL=dom_view.d.ts.map