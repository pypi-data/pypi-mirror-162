import { Model } from "../../model";
import { DOMComponentView } from "../../core/dom_view";
import { SerializableState } from "../../core/view";
import { BBox } from "../../core/util/bbox";
import * as p from "../../core/properties";
export declare abstract class UIElementView extends DOMComponentView {
    model: UIElement;
    get bbox(): BBox;
    serializable_state(): SerializableState;
}
export declare namespace UIElement {
    type Attrs = p.AttrsOf<Props>;
    type Props = Model.Props & {
        visible: p.Property<boolean>;
    };
}
export interface UIElement extends UIElement.Attrs {
}
export declare abstract class UIElement extends Model {
    properties: UIElement.Props;
    __view_type__: UIElementView;
    constructor(attrs?: Partial<UIElement.Attrs>);
}
//# sourceMappingURL=ui_element.d.ts.map