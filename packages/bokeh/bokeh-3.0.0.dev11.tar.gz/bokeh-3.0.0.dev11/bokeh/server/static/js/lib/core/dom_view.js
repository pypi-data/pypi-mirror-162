import { View } from "./view";
import { createElement, remove, empty, StyleSheet } from "./dom";
import { isString } from "./util/types";
import base_css from "../styles/base.css";
export class DOMView extends View {
    get children_el() {
        return this.shadow_el ?? this.el;
    }
    initialize() {
        super.initialize();
        this.el = this._createElement();
    }
    remove() {
        remove(this.el);
        super.remove();
    }
    css_classes() {
        return [];
    }
    styles() {
        return [];
    }
    renderTo(element) {
        element.appendChild(this.el);
        this.render();
        this._has_finished = true;
        this.notify_finished();
    }
    _createElement() {
        return createElement(this.constructor.tag_name, { class: this.css_classes() });
    }
}
DOMView.__name__ = "DOMView";
DOMView.tag_name = "div";
export class DOMElementView extends DOMView {
}
DOMElementView.__name__ = "DOMElementView";
export class DOMComponentView extends DOMElementView {
    constructor() {
        super(...arguments);
        this._stylesheets = [];
    }
    initialize() {
        super.initialize();
        this.shadow_el = this.el.attachShadow({ mode: "open" });
        /*
        if (has_adopted_stylesheets) {
          const sheets: CSSStyleSheet[] = []
          for (const style of this.styles()) {
            const sheet = new CSSStyleSheet()
            sheet.replaceSync(style)
            sheets.push(sheet)
          }
          this.shadow_el.adoptedStyleSheets = sheets
        } else {
        */
        for (const style of this.styles()) {
            const stylesheet = isString(style) ? new StyleSheet(style) : style;
            this._stylesheets.push(stylesheet);
            this.shadow_el.appendChild(stylesheet.el);
        }
        //}
    }
    styles() {
        return [...super.styles(), base_css];
    }
    empty() {
        empty(this.shadow_el);
        for (const stylesheet of this._stylesheets) {
            this.shadow_el.appendChild(stylesheet.el);
        }
    }
}
DOMComponentView.__name__ = "DOMComponentView";
//# sourceMappingURL=dom_view.js.map