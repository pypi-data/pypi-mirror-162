import { ToolButtonView } from "./tool_button";
import * as tools from "../../styles/tool_button.css";
import { classes } from "../../core/dom";
export class OnOffButtonView extends ToolButtonView {
    render() {
        super.render();
        classes(this.el).toggle(tools.active, this.model.active);
    }
    _clicked() {
        const { active } = this.model;
        this.model.active = !active;
    }
}
OnOffButtonView.__name__ = "OnOffButtonView";
//# sourceMappingURL=on_off_button.js.map