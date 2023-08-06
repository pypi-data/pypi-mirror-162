var _a;
import { HTMLBox, HTMLBoxView } from "../layouts/html_box";
import { default_provider } from "../text/providers";
export class WidgetView extends HTMLBoxView {
    get orientation() {
        return "horizontal";
    }
    get default_size() {
        return this.model.default_size;
    }
    _width_policy() {
        return this.orientation == "horizontal" ? super._width_policy() : "fixed";
    }
    _height_policy() {
        return this.orientation == "horizontal" ? "fixed" : super._height_policy();
    }
    box_sizing() {
        const sizing = super.box_sizing();
        if (this.orientation == "horizontal") {
            if (sizing.width == null)
                sizing.width = this.default_size;
        }
        else {
            if (sizing.height == null)
                sizing.height = this.default_size;
        }
        return sizing;
    }
    get provider() {
        return default_provider;
    }
    async lazy_initialize() {
        await super.lazy_initialize();
        if (this.provider.status == "not_started")
            await this.provider.fetch();
    }
    after_layout() {
        super.after_layout();
        if (this.provider.status == "loading")
            this._has_finished = false;
    }
    process_tex(text) {
        if (!this.provider.MathJax)
            return text;
        const tex_parts = this.provider.MathJax.find_tex(text);
        const processed_text = [];
        let last_index = 0;
        for (const part of tex_parts) {
            processed_text.push(text.slice(last_index, part.start.n));
            processed_text.push(this.provider.MathJax.tex2svg(part.math, { display: part.display }).outerHTML);
            last_index = part.end.n;
        }
        if (last_index < text.length)
            processed_text.push(text.slice(last_index));
        return processed_text.join("");
    }
    contains_tex_string(text) {
        if (!this.provider.MathJax)
            return false;
        return this.provider.MathJax.find_tex(text).length > 0;
    }
    ;
}
WidgetView.__name__ = "WidgetView";
export class Widget extends HTMLBox {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Widget;
Widget.__name__ = "Widget";
(() => {
    _a.define(({ Number }) => ({
        default_size: [Number, 300],
    }));
    _a.override({
        margin: [5, 5, 5, 5],
    });
})();
//# sourceMappingURL=widget.js.map