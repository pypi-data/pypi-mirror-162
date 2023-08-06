import { div, style, classes, empty, remove, Keys } from "../dom";
import { reversed } from "./array";
import menus_css, * as menus from "../../styles/menus.css";
import icons_css from "../../styles/icons.css";
import base_css from "../../styles/base.css";
//import {DOMComponentView} from "../dom_view"
export class ContextMenu {
    constructor(items, options) {
        this.items = items;
        this.el = div();
        this._open = false;
        this._item_click = (entry) => {
            entry.handler?.();
            this.hide();
        };
        this._on_mousedown = (event) => {
            if (event.composedPath().includes(this.el))
                return;
            if (this.prevent_hide?.(event) ?? false)
                return;
            this.hide();
        };
        this._on_keydown = (event) => {
            if (event.keyCode == Keys.Esc)
                this.hide();
        };
        this._on_blur = () => {
            this.hide();
        };
        this.target = options.target;
        this.orientation = options.orientation ?? "vertical";
        this.reversed = options.reversed ?? false;
        this.prevent_hide = options.prevent_hide;
        this.extra_styles = options.extra_styles ?? [];
        this.shadow_el = this.el.attachShadow({ mode: "open" });
        this.stylesheet_el = style({}, ...this.styles());
        this.shadow_el.appendChild(this.stylesheet_el);
    }
    get is_open() {
        return this._open;
    }
    get can_open() {
        return this.items.length != 0;
    }
    remove() {
        this._unlisten();
        remove(this.el);
    }
    _listen() {
        document.addEventListener("mousedown", this._on_mousedown);
        document.addEventListener("keydown", this._on_keydown);
        window.addEventListener("blur", this._on_blur);
    }
    _unlisten() {
        document.removeEventListener("mousedown", this._on_mousedown);
        document.removeEventListener("keydown", this._on_keydown);
        window.removeEventListener("blur", this._on_blur);
    }
    _position(at) {
        const pos = (() => {
            if ("left_of" in at) {
                const { left, top } = at.left_of.getBoundingClientRect();
                return { right: left, top };
            }
            if ("right_of" in at) {
                const { top, right } = at.right_of.getBoundingClientRect();
                return { left: right, top };
            }
            if ("below" in at) {
                const { left, bottom } = at.below.getBoundingClientRect();
                return { left, top: bottom };
            }
            if ("above" in at) {
                const { left, top } = at.above.getBoundingClientRect();
                return { left, bottom: top };
            }
            return at;
        })();
        const rect = this.target.getBoundingClientRect();
        const style = getComputedStyle(this.target);
        const margin_left = parseFloat(style.marginLeft);
        const margin_top = parseFloat(style.marginTop);
        this.el.style.left = pos.left != null ? `${pos.left - (rect.left - margin_left)}px` : "";
        this.el.style.top = pos.top != null ? `${pos.top - (rect.top - margin_top)}px` : "";
        this.el.style.right = pos.right != null ? `${rect.right + margin_left - pos.right}px` : "";
        this.el.style.bottom = pos.bottom != null ? `${rect.bottom + margin_top - pos.bottom}px` : "";
    }
    styles() {
        return [base_css, /*...super.styles(), */ menus_css, icons_css, ...this.extra_styles];
    }
    empty() {
        empty(this.shadow_el);
        this.shadow_el.appendChild(this.stylesheet_el);
    }
    render() {
        this.empty();
        classes(this.el).add(menus[this.orientation]);
        const items = this.reversed ? reversed(this.items) : this.items;
        for (const item of items) {
            let el;
            if (item == null) {
                el = div({ class: menus.divider });
            }
            else if (item.if != null && !item.if()) {
                continue;
            }
            else if (item.content != null) {
                el = item.content;
            }
            else {
                const icon = item.icon != null ? div({ class: [menus.menu_icon, item.icon] }) : null;
                const classes = [item.active?.() ?? false ? menus.active : null, item.class];
                el = div({ class: classes, title: item.tooltip, tabIndex: 0 }, icon, item.label, item.content);
                el.addEventListener("click", () => {
                    this._item_click(item);
                });
                el.addEventListener("keydown", (event) => {
                    if (event.keyCode == Keys.Enter) {
                        this._item_click(item);
                    }
                });
            }
            this.shadow_el.appendChild(el);
        }
    }
    show(at) {
        if (this.items.length == 0)
            return;
        if (!this._open) {
            this.render();
            if (this.shadow_el.children.length == 0)
                return;
            (this.target.shadowRoot ?? this.target).appendChild(this.el);
            this._position(at ?? { left: 0, top: 0 });
            this._listen();
            this._open = true;
        }
    }
    hide() {
        if (this._open) {
            this._open = false;
            this._unlisten();
            remove(this.el);
        }
    }
    toggle(at) {
        this._open ? this.hide() : this.show(at);
    }
}
ContextMenu.__name__ = "ContextMenu";
//# sourceMappingURL=menus.js.map