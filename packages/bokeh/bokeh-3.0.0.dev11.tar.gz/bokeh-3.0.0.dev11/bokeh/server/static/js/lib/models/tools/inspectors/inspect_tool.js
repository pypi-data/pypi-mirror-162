var _a;
import { Tool, ToolView } from "../tool";
import { OnOffButtonView } from "../on_off_button";
export class InspectToolView extends ToolView {
    get plot_view() {
        return this.parent;
    }
}
InspectToolView.__name__ = "InspectToolView";
export class InspectTool extends Tool {
    constructor(attrs) {
        super(attrs);
        this.event_type = "move";
    }
}
_a = InspectTool;
InspectTool.__name__ = "InspectTool";
(() => {
    _a.prototype.button_view = OnOffButtonView;
    _a.define(({ Boolean }) => ({
        toggleable: [Boolean, true],
    }));
    _a.override({
        active: true,
    });
})();
//# sourceMappingURL=inspect_tool.js.map