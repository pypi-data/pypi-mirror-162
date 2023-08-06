var _a;
import { CachedVariadicBox } from "../../core/layout/html";
import { div } from "../../core/dom";
import { Widget, WidgetView } from "./widget";
import clearfix_css, { clearfix } from "../../styles/clearfix.css";
export class MarkupView extends WidgetView {
    async lazy_initialize() {
        await super.lazy_initialize();
        if (this.provider.status == "not_started" || this.provider.status == "loading")
            this.provider.ready.connect(() => {
                if (this.contains_tex_string(this.model.text))
                    this.rerender();
            });
    }
    has_math_disabled() {
        return this.model.disable_math || !this.contains_tex_string(this.model.text);
    }
    rerender() {
        this.layout.invalidate_cache();
        this.render();
        this.root.compute_layout(); // XXX: invalidate_layout?
    }
    connect_signals() {
        super.connect_signals();
        this.connect(this.model.change, () => {
            this.rerender();
        });
    }
    styles() {
        return [...super.styles(), clearfix_css, "p { margin: 0; }"];
    }
    _update_layout() {
        this.layout = new CachedVariadicBox(this.el);
        this.layout.set_sizing(this.box_sizing());
    }
    render() {
        super.render();
        this.markup_el = div({ class: clearfix, style: { display: "inline-block" } });
        this.shadow_el.appendChild(this.markup_el);
        if (this.provider.status == "failed" || this.provider.status == "loaded")
            this._has_finished = true;
    }
}
MarkupView.__name__ = "MarkupView";
export class Markup extends Widget {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Markup;
Markup.__name__ = "Markup";
(() => {
    _a.define(({ Boolean, String }) => ({
        text: [String, ""],
        disable_math: [Boolean, false],
    }));
})();
//# sourceMappingURL=markup.js.map