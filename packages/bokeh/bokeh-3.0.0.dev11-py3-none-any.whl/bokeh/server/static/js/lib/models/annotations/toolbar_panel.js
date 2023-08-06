var _a;
import { Annotation, AnnotationView } from "./annotation";
import { Toolbar } from "../tools/toolbar";
import { build_view } from "../../core/build_views";
import { div, empty, position, display, undisplay, remove } from "../../core/dom";
import { SideLayout } from "../../core/layout/side_panel";
import { BBox } from "../../core/util/bbox";
export class ToolbarPanelView extends AnnotationView {
    constructor() {
        super(...arguments);
        this._invalidate_toolbar = true;
        this._previous_bbox = new BBox();
    }
    update_layout() {
        this.layout = new SideLayout(this.panel, () => this.get_size(), true);
    }
    initialize() {
        super.initialize();
        this.el = div();
        this.plot_view.canvas_view.add_event(this.el);
    }
    async lazy_initialize() {
        await super.lazy_initialize();
        this.toolbar_view = await build_view(this.model.toolbar, { parent: this }); // XXX: ???
    }
    connect_signals() {
        super.connect_signals();
        this.plot_view.mouseenter.connect(() => {
            this.toolbar_view.set_visibility(true);
        });
        this.plot_view.mouseleave.connect(() => {
            this.toolbar_view.set_visibility(false);
        });
    }
    remove() {
        this.toolbar_view.remove();
        remove(this.el);
        super.remove();
    }
    render() {
        if (!this.model.visible)
            undisplay(this.el);
        super.render();
    }
    _render() {
        // TODO: this should be handled by the layout
        const { bbox } = this.layout;
        if (!this._previous_bbox.equals(bbox)) {
            position(this.el, bbox);
            this._previous_bbox = bbox;
            this._invalidate_toolbar = true;
        }
        if (this._invalidate_toolbar) {
            this.el.style.position = "absolute";
            empty(this.el);
            this.el.appendChild(this.toolbar_view.el);
            this.toolbar_view.layout.bbox = bbox;
            this.toolbar_view.render();
            if (this.model.inner)
                this.toolbar_view.el.classList.add("bk-inner");
            this._invalidate_toolbar = false;
        }
        display(this.el);
    }
    _get_size() {
        const { tools, logo } = this.model.toolbar;
        return {
            width: tools.length * 30 + (logo != null ? 25 : 0) + 15,
            height: 30,
        };
    }
}
ToolbarPanelView.__name__ = "ToolbarPanelView";
export class ToolbarPanel extends Annotation {
    constructor(attrs) {
        super(attrs);
    }
}
_a = ToolbarPanel;
ToolbarPanel.__name__ = "ToolbarPanel";
(() => {
    _a.prototype.default_view = ToolbarPanelView;
    _a.define(({ Ref }) => ({
        toolbar: [Ref(Toolbar)],
    }));
    _a.internal(({ Boolean }) => ({
        inner: [Boolean, false],
    }));
})();
//# sourceMappingURL=toolbar_panel.js.map