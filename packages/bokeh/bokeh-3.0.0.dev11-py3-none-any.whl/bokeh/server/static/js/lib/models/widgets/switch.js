var _a;
import { Widget, WidgetView } from "./widget";
import { div } from "../../core/dom";
import switch_css from "../../styles/widgets/switch.css";
export class SwitchView extends WidgetView {
    connect_signals() {
        super.connect_signals();
        const { active, disabled } = this.model.properties;
        this.on_change(active, () => this._update_active());
        this.on_change(disabled, () => this._update_disabled());
        this.el.addEventListener("click", () => {
            if (!this.model.disabled) {
                this.model.active = !this.model.active;
            }
        });
    }
    styles() {
        return [...super.styles(), switch_css];
    }
    render() {
        super.render();
        this.knob_el = div({ class: "knob" });
        this.bar_el = div({ class: "bar" }, this.knob_el);
        this.shadow_el.appendChild(this.bar_el);
        this._update_active();
        this._update_disabled();
    }
    _update_active() {
        this.el.classList.toggle("active", this.model.active);
    }
    _update_disabled() {
        this.el.classList.toggle("disabled", this.model.disabled);
    }
}
SwitchView.__name__ = "SwitchView";
export class Switch extends Widget {
    constructor(attrs) {
        super(attrs);
    }
}
_a = Switch;
Switch.__name__ = "Switch";
(() => {
    _a.prototype.default_view = SwitchView;
    _a.define(({ Boolean }) => ({
        active: [Boolean, false],
    }));
    _a.override({
        width: 32,
    });
})();
//# sourceMappingURL=switch.js.map