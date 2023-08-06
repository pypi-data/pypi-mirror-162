import { UIElement, UIElementView } from "../ui/ui_element";
import { MenuItem, MenuItemView } from "./menu_item";
import { StyleSheetLike } from "../../core/dom";
import { Orientation } from "../../core/enums";
import * as p from "../../core/properties";
export declare class MenuView extends UIElementView {
    model: Menu;
    styles(): StyleSheetLike[];
    protected items: Map<MenuItem, MenuItemView>;
    lazy_initialize(): Promise<void>;
    remove(): void;
    render(): void;
}
export declare namespace Menu {
    type Attrs = p.AttrsOf<Props>;
    type Props = UIElement.Props & {
        items: p.Property<MenuItem[]>;
        reversed: p.Property<boolean>;
        orientation: p.Property<Orientation>;
    };
}
export interface Menu extends Menu.Attrs {
}
export declare class Menu extends UIElement {
    properties: Menu.Props;
    __view_type__: MenuView;
    constructor(attrs?: Partial<Menu.Attrs>);
}
//# sourceMappingURL=menu.d.ts.map