var _a;
import { Model } from "../../model";
import { DOMComponentView } from "../../core/dom_view";
import { BBox } from "../../core/util/bbox";
const { round } = Math;
export class UIElementView extends DOMComponentView {
    get bbox() {
        const self = this.el.getBoundingClientRect();
        const { left, top } = (() => {
            if (this.parent != null) {
                const parent = this.parent.el.getBoundingClientRect();
                return {
                    left: self.left - parent.left,
                    top: self.top - parent.top,
                };
            }
            else {
                return { left: 0, top: 0 };
            }
        })();
        const bbox = new BBox({
            left: round(left),
            top: round(top),
            width: round(self.width),
            height: round(self.height),
        });
        return bbox;
    }
    serializable_state() {
        return {
            ...super.serializable_state(),
            bbox: this.bbox.box,
        };
    }
}
UIElementView.__name__ = "UIElementView";
export class UIElement extends Model {
    constructor(attrs) {
        super(attrs);
    }
}
_a = UIElement;
UIElement.__name__ = "UIElement";
(() => {
    _a.define(({ Boolean }) => ({
        visible: [Boolean, true],
    }));
})();
//# sourceMappingURL=ui_element.js.map