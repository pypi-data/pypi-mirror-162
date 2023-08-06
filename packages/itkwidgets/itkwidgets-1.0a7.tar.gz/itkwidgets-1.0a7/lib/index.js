"use strict";
// Copyright (c) Insight Software Consortium
// Distributed under the terms of the Apache 2.0 License.
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    Object.defineProperty(o, k2, { enumerable: true, get: function() { return m[k]; } });
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __exportStar = (this && this.__exportStar) || function(m, exports) {
    for (var p in m) if (p !== "default" && !Object.prototype.hasOwnProperty.call(exports, p)) __createBinding(exports, m, p);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.ViewerView = exports.ViewerModel = void 0;
__exportStar(require("./version"), exports);
__exportStar(require("./widget"), exports);
var viewer_1 = require("./viewer");
Object.defineProperty(exports, "ViewerModel", { enumerable: true, get: function () { return viewer_1.ViewerModel; } });
Object.defineProperty(exports, "ViewerView", { enumerable: true, get: function () { return viewer_1.ViewerView; } });
//# sourceMappingURL=index.js.map