import { Document } from "../document";
import { ViewOf } from "../core/view";
import { HasProps } from "../core/has_props";
import { UIElement } from "../models/ui/ui_element";
export declare function show<T extends UIElement>(obj: T, target?: HTMLElement | string): Promise<ViewOf<T>>;
export declare function show<T extends UIElement>(obj: T[], target?: HTMLElement | string): Promise<ViewOf<T>[]>;
export declare function show(obj: Document, target?: HTMLElement | string): Promise<ViewOf<HasProps>[]>;
export declare function show(obj: UIElement | Document, target?: HTMLElement | string): Promise<ViewOf<HasProps> | ViewOf<HasProps>[]>;
//# sourceMappingURL=io.d.ts.map