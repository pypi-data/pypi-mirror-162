export const inner = "bk-inner"
export const hidden = "bk-hidden"
export const logo = "bk-logo"
export const above = "bk-above"
export const below = "bk-below"
export const left = "bk-left"
export const right = "bk-right"
export default `:host{display:flex;flex-wrap:nowrap;align-items:center;user-select:none;-ms-user-select:none;-moz-user-select:none;-webkit-user-select:none;}:host(.bk-inner){background-color:white;opacity:0.8;}:host(.bk-hidden){visibility:hidden;opacity:0;transition:visibility 0.3s linear, opacity 0.3s linear;}.bk-logo{flex-shrink:0;}:host(.bk-above),:host(.bk-below){flex-direction:row;justify-content:flex-end;}:host(.bk-above) .bk-logo,:host(.bk-below) .bk-logo{order:1;margin-left:5px;margin-right:0px;}:host(.bk-left),:host(.bk-right){flex-direction:column;justify-content:flex-start;}:host(.bk-left) .bk-logo,:host(.bk-right) .bk-logo{order:0;margin-bottom:5px;margin-top:0px;}`
