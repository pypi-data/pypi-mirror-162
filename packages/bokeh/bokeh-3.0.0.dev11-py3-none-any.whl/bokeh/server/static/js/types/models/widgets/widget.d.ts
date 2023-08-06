import { HTMLBox, HTMLBoxView } from "../layouts/html_box";
import { Orientation } from "../../core/enums";
import { BoxSizing, SizingPolicy } from "../../core/layout";
import { MathJaxProvider } from "../text/providers";
import * as p from "../../core/properties";
export declare abstract class WidgetView extends HTMLBoxView {
    model: Widget;
    protected get orientation(): Orientation;
    protected get default_size(): number | undefined;
    protected _width_policy(): SizingPolicy;
    protected _height_policy(): SizingPolicy;
    box_sizing(): Partial<BoxSizing>;
    get provider(): MathJaxProvider;
    lazy_initialize(): Promise<void>;
    after_layout(): void;
    process_tex(text: string): string;
    protected contains_tex_string(text: string): boolean;
}
export declare namespace Widget {
    type Attrs = p.AttrsOf<Props>;
    type Props = HTMLBox.Props & {
        default_size: p.Property<number>;
    };
}
export interface Widget extends Widget.Attrs {
}
export declare abstract class Widget extends HTMLBox {
    properties: Widget.Props;
    __view_type__: WidgetView;
    constructor(attrs?: Partial<Widget.Attrs>);
}
//# sourceMappingURL=widget.d.ts.map