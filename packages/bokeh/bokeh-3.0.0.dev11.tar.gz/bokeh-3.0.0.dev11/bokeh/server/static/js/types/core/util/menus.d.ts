import { Orientation } from "../enums";
export declare type ScreenPoint = {
    left?: number;
    right?: number;
    top?: number;
    bottom?: number;
};
export declare type At = ScreenPoint | {
    left_of: HTMLElement;
} | {
    right_of: HTMLElement;
} | {
    below: HTMLElement;
} | {
    above: HTMLElement;
};
export declare type MenuEntry = {
    icon?: string;
    label?: string;
    tooltip?: string;
    class?: string;
    content?: HTMLElement;
    active?: () => boolean;
    handler?: () => void;
    if?: () => boolean;
};
export declare type MenuItem = MenuEntry | null;
export declare type MenuOptions = {
    target: HTMLElement;
    orientation?: Orientation;
    reversed?: boolean;
    prevent_hide?: (event: MouseEvent) => boolean;
    extra_styles?: string[];
};
export declare class ContextMenu {
    readonly items: MenuItem[];
    readonly el: HTMLElement;
    readonly shadow_el: ShadowRoot;
    readonly stylesheet_el: HTMLStyleElement;
    protected _open: boolean;
    get is_open(): boolean;
    get can_open(): boolean;
    readonly target: HTMLElement;
    readonly orientation: Orientation;
    readonly reversed: boolean;
    readonly prevent_hide?: (event: MouseEvent) => boolean;
    readonly extra_styles: string[];
    constructor(items: MenuItem[], options: MenuOptions);
    protected _item_click: (entry: MenuEntry) => void;
    protected _on_mousedown: (event: MouseEvent) => void;
    protected _on_keydown: (event: KeyboardEvent) => void;
    protected _on_blur: () => void;
    remove(): void;
    protected _listen(): void;
    protected _unlisten(): void;
    protected _position(at: At): void;
    styles(): string[];
    empty(): void;
    render(): void;
    show(at?: At): void;
    hide(): void;
    toggle(at?: At): void;
}
//# sourceMappingURL=menus.d.ts.map