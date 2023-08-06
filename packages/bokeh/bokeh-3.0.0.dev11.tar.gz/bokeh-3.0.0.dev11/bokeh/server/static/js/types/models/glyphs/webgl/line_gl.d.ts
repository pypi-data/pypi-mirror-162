import { Transform } from "./base";
import { BaseLineGL, LineGLVisuals } from "./base_line";
import { ReglWrapper } from "./regl_wrap";
import { LineView } from "../line";
export declare class LineGL extends BaseLineGL {
    readonly glyph: LineView;
    constructor(regl_wrapper: ReglWrapper, glyph: LineView);
    draw(_indices: number[], main_glyph: LineView, transform: Transform): void;
    protected _get_visuals(): LineGLVisuals;
    protected _set_data_points(): Float32Array;
}
//# sourceMappingURL=line_gl.d.ts.map