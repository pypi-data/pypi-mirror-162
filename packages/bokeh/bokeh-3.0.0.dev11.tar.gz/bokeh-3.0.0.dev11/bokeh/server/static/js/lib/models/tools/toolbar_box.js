var _a;
import { Location } from "../../core/enums";
import { Toolbar } from "./toolbar";
import { LayoutDOM, LayoutDOMView } from "../layouts/layout_dom";
import { ContentBox } from "../../core/layout";
export class ToolbarBoxView extends LayoutDOMView {
    initialize() {
        this.model.toolbar.toolbar_location = this.model.toolbar_location;
        super.initialize();
    }
    get toolbar_view() {
        return this.child_views[0];
    }
    connect_signals() {
        super.connect_signals();
        const { parent } = this;
        if (parent instanceof LayoutDOMView) {
            parent.mouseenter.connect(() => {
                this.toolbar_view.set_visibility(true);
            });
            parent.mouseleave.connect(() => {
                this.toolbar_view.set_visibility(false);
            });
        }
        const { toolbar_location } = this.model.properties;
        this.on_change(toolbar_location, () => {
            this.model.toolbar.toolbar_location = this.model.toolbar_location;
        });
    }
    get child_models() {
        return [this.model.toolbar]; // XXX
    }
    _update_layout() {
        this.layout = new ContentBox(this.child_views[0].el);
        const { toolbar } = this.model;
        if (toolbar.horizontal) {
            this.layout.set_sizing({
                width_policy: "fit", min_width: 100, height_policy: "fixed",
            });
        }
        else {
            this.layout.set_sizing({
                width_policy: "fixed", height_policy: "fit", min_height: 100,
            });
        }
    }
    after_layout() {
        super.after_layout();
        this.toolbar_view.layout.bbox = this.layout.bbox;
        this.toolbar_view.render(); // render the second time to revise overflow
    }
}
ToolbarBoxView.__name__ = "ToolbarBoxView";
export class ToolbarBox extends LayoutDOM {
    constructor(attrs) {
        super(attrs);
    }
}
_a = ToolbarBox;
ToolbarBox.__name__ = "ToolbarBox";
(() => {
    _a.prototype.default_view = ToolbarBoxView;
    _a.define(({ Ref }) => ({
        toolbar: [Ref(Toolbar)],
        toolbar_location: [Location, "right"],
    }));
})();
//# sourceMappingURL=toolbar_box.js.map