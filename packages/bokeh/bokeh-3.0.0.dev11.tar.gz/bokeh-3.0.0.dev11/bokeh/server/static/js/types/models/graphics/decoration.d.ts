import { Marking, MarkingView } from "./marking";
import { RendererView } from "../renderers/renderer";
import { Model } from "../../model";
import { View } from "../../core/view";
import * as visuals from "../../core/visuals";
import * as p from "../../core/properties";
export declare class DecorationView extends View {
    model: Decoration;
    visuals: Decoration.Visuals;
    parent: RendererView;
    marking: MarkingView;
    lazy_initialize(): Promise<void>;
}
export declare namespace Decoration {
    type Attrs = p.AttrsOf<Props>;
    type Props = Model.Props & {
        marking: p.Property<Marking>;
        node: p.Property<"start" | "middle" | "end">;
    };
    type Visuals = visuals.Visuals;
}
export interface Decoration extends Decoration.Attrs {
}
export declare class Decoration extends Model {
    properties: Decoration.Props;
    __view_type__: DecorationView;
    constructor(attrs?: Partial<Decoration.Attrs>);
}
//# sourceMappingURL=decoration.d.ts.map