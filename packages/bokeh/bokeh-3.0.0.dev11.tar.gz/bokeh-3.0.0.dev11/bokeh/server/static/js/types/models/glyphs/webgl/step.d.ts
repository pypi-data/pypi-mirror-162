import { Transform } from "./base";
import { BaseLineGL, LineGLVisuals } from "./base_line";
import { ReglWrapper } from "./regl_wrap";
import { StepView } from "../step";
export declare class StepGL extends BaseLineGL {
    readonly glyph: StepView;
    constructor(regl_wrapper: ReglWrapper, glyph: StepView);
    draw(_indices: number[], main_glyph: StepView, transform: Transform): void;
    protected _get_visuals(): LineGLVisuals;
    protected _set_data_points(): Float32Array;
}
//# sourceMappingURL=step.d.ts.map