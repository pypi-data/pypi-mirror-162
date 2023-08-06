import { Tool, ToolView } from "../tool";
import { ToolButtonView } from "../tool_button";
import { Signal } from "../../../core/signaling";
export class ActionToolButtonView extends ToolButtonView {
    _clicked() {
        this.model.do.emit(undefined);
    }
}
ActionToolButtonView.__name__ = "ActionToolButtonView";
export class ActionToolView extends ToolView {
    connect_signals() {
        super.connect_signals();
        this.connect(this.model.do, (arg) => this.doit(arg));
    }
}
ActionToolView.__name__ = "ActionToolView";
export class ActionTool extends Tool {
    constructor(attrs) {
        super(attrs);
        this.button_view = ActionToolButtonView;
        this.do = new Signal(this, "do");
    }
}
ActionTool.__name__ = "ActionTool";
//# sourceMappingURL=action_tool.js.map