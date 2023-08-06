(self["webpackChunkjupyterannotate"] = self["webpackChunkjupyterannotate"] || []).push([["lib_widget_js"],{

/***/ "./lib/components/Annotate.js":
/*!************************************!*\
  !*** ./lib/components/Annotate.js ***!
  \************************************/
/***/ (function(__unused_webpack_module, exports, __webpack_require__) {

"use strict";

var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
const preact_1 = __webpack_require__(/*! preact */ "./node_modules/preact/dist/preact.module.js");
const hooks_1 = __webpack_require__(/*! preact/hooks */ "./node_modules/preact/hooks/dist/hooks.module.js");
const TopBar_1 = __importDefault(__webpack_require__(/*! ./TopBar */ "./lib/components/TopBar.js"));
const Highlightable_1 = __importDefault(__webpack_require__(/*! ./Highlightable */ "./lib/components/Highlightable.js"));
const colors_1 = __webpack_require__(/*! ./colors */ "./lib/components/colors.js");
function Annotate({ docs, labels, initialSpans, registerSpanChangeCallback, onUpdateSpans, }) {
    const totalDocs = docs.length;
    const [selectedLabel, setSelectedLabel] = hooks_1.useState();
    const [docIndex, setDocIndex] = hooks_1.useState(0);
    const [docSpans, setDocSpans] = hooks_1.useState(initialSpans.length
        ? initialSpans
        : [...Array(totalDocs).keys()].map(() => []));
    const text = hooks_1.useMemo(() => {
        return docs[docIndex];
    }, [docIndex, docs]);
    hooks_1.useEffect(() => {
        registerSpanChangeCallback((spans) => {
            setDocSpans(spans);
        });
    }, []);
    const onChangeLabel = (label) => {
        setSelectedLabel(label);
    };
    const onUpdate = (changedSpans) => {
        const updatedSpans = [...docSpans];
        updatedSpans[docIndex] = changedSpans;
        setDocSpans(updatedSpans);
        onUpdateSpans(updatedSpans);
    };
    const onChangeNav = (docIndex) => {
        setDocIndex(docIndex);
    };
    const spans = docSpans[docIndex] || [];
    const coloredLabels = hooks_1.useMemo(() => {
        const colors = Object.keys(colors_1.HIGHLIGHT_COLORS);
        return labels.map((text, index) => ({
            text,
            color: colors[index % colors.length],
        }));
    }, [labels]);
    const activeLabel = selectedLabel || coloredLabels[0];
    return preact_1.h("div", null, [
        preact_1.h(TopBar_1.default, {
            selectedLabel: activeLabel,
            labels: coloredLabels,
            totalDocs,
            docIndex,
            onChangeLabel,
            onChangeNav,
        }),
        preact_1.h(Highlightable_1.default, { text, selectedLabel: activeLabel, spans, onUpdate }),
    ]);
}
exports["default"] = Annotate;
//# sourceMappingURL=Annotate.js.map

/***/ }),

/***/ "./lib/components/Highlightable.js":
/*!*****************************************!*\
  !*** ./lib/components/Highlightable.js ***!
  \*****************************************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {

"use strict";

Object.defineProperty(exports, "__esModule", ({ value: true }));
const preact_1 = __webpack_require__(/*! preact */ "./node_modules/preact/dist/preact.module.js");
const hooks_1 = __webpack_require__(/*! preact/hooks */ "./node_modules/preact/hooks/dist/hooks.module.js");
const colors_1 = __webpack_require__(/*! ./colors */ "./lib/components/colors.js");
const SpanLabel = ({ text, label, onClick, }) => {
    const color = colors_1.HIGHLIGHT_COLORS[label.color] || colors_1.HIGHLIGHT_COLORS.red;
    const style = {
        backgroundColor: color[50],
        color: color[800],
        borderColor: color[800],
    };
    return preact_1.h("span", { style, className: "span", onClick, title: label.text }, [
        text,
    ]);
};
const getHighlightedText = (text, spans, onRemoveSpan) => {
    const chunks = [];
    let prevOffset = 0;
    spans
        .sort((a, b) => (a.start > b.start ? 1 : -1))
        .forEach((span) => {
        chunks.push(preact_1.h("span", { "data-offset": prevOffset }, text.slice(prevOffset, span.start)));
        chunks.push(SpanLabel({
            text: span.text,
            label: span.label,
            onClick: () => onRemoveSpan(span),
        }));
        prevOffset = span.end;
    });
    chunks.push(preact_1.h("span", { "data-offset": prevOffset }, text.slice(prevOffset)));
    return chunks;
};
const Highlightable = ({ text, selectedLabel, spans, onUpdate, }) => {
    const ref = hooks_1.useRef(null);
    function onSelect(event) {
        var _a;
        const dataset = ((_a = event.target) === null || _a === void 0 ? void 0 : _a.dataset) || {};
        const offset = parseInt(dataset.offset || "0", 10);
        const selected = window.getSelection();
        const selectedText = (selected === null || selected === void 0 ? void 0 : selected.toString()) || "";
        if (!selectedText.trim() || !selected) {
            return;
        }
        const startOffset = selected.anchorOffset > selected.focusOffset
            ? selected.focusOffset
            : selected.anchorOffset;
        const endOffset = selected.anchorOffset < selected.focusOffset
            ? selected.focusOffset
            : selected.anchorOffset;
        const start = startOffset + offset;
        const end = endOffset + offset;
        onUpdate(spans.concat([
            {
                start,
                end,
                text: text.slice(start, end),
                label: selectedLabel,
            },
        ]));
    }
    const onRemoveSpan = (span) => {
        onUpdate(spans.filter((s) => s.start !== span.start));
    };
    hooks_1.useEffect(() => {
        const el = ref.current;
        if (el) {
            el.addEventListener("mouseup", onSelect);
        }
    }, [ref.current, onSelect]);
    return preact_1.h("div", { ref, className: "content" }, getHighlightedText(text, spans, onRemoveSpan));
};
exports["default"] = Highlightable;
//# sourceMappingURL=Highlightable.js.map

/***/ }),

/***/ "./lib/components/Labels.js":
/*!**********************************!*\
  !*** ./lib/components/Labels.js ***!
  \**********************************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {

"use strict";

Object.defineProperty(exports, "__esModule", ({ value: true }));
const preact_1 = __webpack_require__(/*! preact */ "./node_modules/preact/dist/preact.module.js");
const colors_1 = __webpack_require__(/*! ./colors */ "./lib/components/colors.js");
const Label = ({ label, isSelected, onClick, }) => {
    const className = isSelected ? "label selected" : "label";
    const color = colors_1.HIGHLIGHT_COLORS[label.color] || colors_1.HIGHLIGHT_COLORS.red;
    const borderColor = isSelected ? color[300] : color[800];
    const style = {
        borderLeft: `solid 4px ${borderColor}`,
    };
    return preact_1.h("div", { style, className, onClick: () => onClick(label) }, label.text);
};
const Labels = ({ labels, selectedLabel, onChangeLabel }) => {
    return preact_1.h("div", { className: "labelContainer" }, labels.map((label) => preact_1.h(Label, {
        label,
        isSelected: label.text === selectedLabel.text,
        onClick: onChangeLabel,
    })));
};
exports["default"] = Labels;
//# sourceMappingURL=Labels.js.map

/***/ }),

/***/ "./lib/components/Nav.js":
/*!*******************************!*\
  !*** ./lib/components/Nav.js ***!
  \*******************************/
/***/ (function(__unused_webpack_module, exports, __webpack_require__) {

"use strict";

var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
const preact_1 = __webpack_require__(/*! preact */ "./node_modules/preact/dist/preact.module.js");
const ChevronRight_1 = __importDefault(__webpack_require__(/*! ./icons/ChevronRight */ "./lib/components/icons/ChevronRight.js"));
const ChevronLeft_1 = __importDefault(__webpack_require__(/*! ./icons/ChevronLeft */ "./lib/components/icons/ChevronLeft.js"));
const Nav = ({ docIndex, totalDocs, onChangeNav }) => {
    const onPrev = () => {
        if (docIndex > 0) {
            onChangeNav(docIndex - 1);
        }
    };
    const onNext = () => {
        if (docIndex < totalDocs - 1) {
            onChangeNav(docIndex + 1);
        }
    };
    return preact_1.h("div", { className: "nav" }, [
        preact_1.h("div", { className: "navLink", onClick: onPrev, title: "Previous Document" }, preact_1.h(ChevronLeft_1.default, null)),
        preact_1.h("div", null, `${docIndex + 1} / ${totalDocs}`),
        preact_1.h("div", { className: "navLink", onClick: onNext, title: "Next Document" }, preact_1.h(ChevronRight_1.default, null)),
    ]);
};
exports["default"] = Nav;
//# sourceMappingURL=Nav.js.map

/***/ }),

/***/ "./lib/components/TopBar.js":
/*!**********************************!*\
  !*** ./lib/components/TopBar.js ***!
  \**********************************/
/***/ (function(__unused_webpack_module, exports, __webpack_require__) {

"use strict";

var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
const preact_1 = __webpack_require__(/*! preact */ "./node_modules/preact/dist/preact.module.js");
const Labels_1 = __importDefault(__webpack_require__(/*! ./Labels */ "./lib/components/Labels.js"));
const Nav_1 = __importDefault(__webpack_require__(/*! ./Nav */ "./lib/components/Nav.js"));
const TopBar = ({ labels, selectedLabel, docIndex, totalDocs, onChangeLabel, onChangeNav, }) => {
    return preact_1.h("div", { className: "topBar" }, [
        preact_1.h(Labels_1.default, { labels, selectedLabel, onChangeLabel }),
        preact_1.h(Nav_1.default, { docIndex, totalDocs, onChangeNav }),
    ]);
};
exports["default"] = TopBar;
//# sourceMappingURL=TopBar.js.map

/***/ }),

/***/ "./lib/components/colors.js":
/*!**********************************!*\
  !*** ./lib/components/colors.js ***!
  \**********************************/
/***/ ((__unused_webpack_module, exports) => {

"use strict";

Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.HIGHLIGHT_COLORS = exports.GREY = void 0;
exports.GREY = {
    slate: {
        50: "#F8FAFC",
        300: "#CBD5E1",
        800: "#1E293B",
    },
    gray: {
        50: "#F9FAFB",
        300: "#D1D5DB",
        800: "#1F2937",
    },
    zinc: {
        50: "#FAFAFA",
        300: "#D4D4D8",
        800: "#27272A",
    },
    neutral: {
        50: "#FAFAFA",
        300: "#D4D4D4",
        800: "#262626",
    },
    stone: {
        50: "#FAFAF9",
        300: "#D6D3D1",
        800: "#292524",
    },
};
exports.HIGHLIGHT_COLORS = {
    red: {
        50: "#FEF2F2",
        300: "#FCA5A5",
        800: "#991B1B",
    },
    cyan: {
        50: "#ECFEFF",
        300: "#67E8F9",
        800: "#155E75",
    },
    amber: {
        50: "#FFFBEB",
        300: "#FCD34D",
        800: "#92400E",
    },
    violet: {
        50: "#F5F3FF",
        300: "#C4B5FD",
        800: "#5B21B6",
    },
    yellow: {
        50: "#FEFCE8",
        300: "#FDE047",
        800: "#854D0E",
    },
    lime: {
        50: "#F7FEE7",
        300: "#BEF264",
        800: "#3F6212",
    },
    emerald: {
        50: "#ECFDF5",
        300: "#6EE7B7",
        800: "#065F46",
    },
    teal: {
        50: "#F0FDFA",
        300: "#5EEAD4",
        800: "#115E59",
    },
    orange: {
        50: "#FFF7ED",
        300: "#FDBA74",
        800: "#9A3412",
    },
    sky: {
        50: "#F0F9FF",
        300: "#7DD3FC",
        800: "#075985",
    },
    blue: {
        50: "#EFF6FF",
        300: "#93C5FD",
        800: "#1E40AF",
    },
    indigo: {
        50: "#EEF2FF",
        300: "#A5B4FC",
        800: "#3730A3",
    },
    purple: {
        50: "#FAF5FF",
        300: "#D8B4FE",
        800: "#6B21A8",
    },
    fuchsia: {
        50: "#FDF4FF",
        300: "#F0ABFC",
        800: "#86198F",
    },
    pink: {
        50: "#FDF2F8",
        300: "#F9A8D4",
        800: "#9D174D",
    },
    rose: {
        50: "#FFF1F2",
        300: "#FDA4AF",
        800: "#9F1239",
    },
};
//# sourceMappingURL=colors.js.map

/***/ }),

/***/ "./lib/components/icons/ChevronLeft.js":
/*!*********************************************!*\
  !*** ./lib/components/icons/ChevronLeft.js ***!
  \*********************************************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {

"use strict";

Object.defineProperty(exports, "__esModule", ({ value: true }));
const preact_1 = __webpack_require__(/*! preact */ "./node_modules/preact/dist/preact.module.js");
const ChevronLeft = () => {
    return preact_1.h("svg", {
        fill: "none",
        viewBox: "0 0 24 24",
        stroke: "currentColor",
        "stroke-width": "2",
    }, [
        preact_1.h("path", {
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
            d: "M15 19l-7-7 7-7",
        }),
    ]);
};
exports["default"] = ChevronLeft;
//# sourceMappingURL=ChevronLeft.js.map

/***/ }),

/***/ "./lib/components/icons/ChevronRight.js":
/*!**********************************************!*\
  !*** ./lib/components/icons/ChevronRight.js ***!
  \**********************************************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {

"use strict";

Object.defineProperty(exports, "__esModule", ({ value: true }));
const preact_1 = __webpack_require__(/*! preact */ "./node_modules/preact/dist/preact.module.js");
const ChevronRight = () => {
    return preact_1.h("svg", {
        fill: "none",
        viewBox: "0 0 24 24",
        stroke: "currentColor",
        "stroke-width": "2",
    }, [
        preact_1.h("path", {
            "stroke-linecap": "round",
            "stroke-linejoin": "round",
            d: "M9 5l7 7-7 7",
        }),
    ]);
};
exports["default"] = ChevronRight;
//# sourceMappingURL=ChevronRight.js.map

/***/ }),

/***/ "./lib/version.js":
/*!************************!*\
  !*** ./lib/version.js ***!
  \************************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {

"use strict";

// Copyright (c) Stuart Quin
// Distributed under the terms of the Modified BSD License.
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.MODULE_NAME = exports.MODULE_VERSION = void 0;
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
// eslint-disable-next-line @typescript-eslint/no-var-requires
const data = __webpack_require__(/*! ../package.json */ "./package.json");
/**
 * The _model_module_version/_view_module_version this package implements.
 *
 * The html widget manager assumes that this is the same as the npm package
 * version number.
 */
exports.MODULE_VERSION = data.version;
/*
 * The current package name.
 */
exports.MODULE_NAME = data.name;
//# sourceMappingURL=version.js.map

/***/ }),

/***/ "./lib/widget.js":
/*!***********************!*\
  !*** ./lib/widget.js ***!
  \***********************/
/***/ (function(__unused_webpack_module, exports, __webpack_require__) {

"use strict";

// Copyright (c) Stuart Quin
// Distributed under the terms of the Modified BSD License.
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.AnnotateView = exports.AnnotateModel = void 0;
const base_1 = __webpack_require__(/*! @jupyter-widgets/base */ "webpack/sharing/consume/default/@jupyter-widgets/base");
const preact_1 = __webpack_require__(/*! preact */ "./node_modules/preact/dist/preact.module.js");
const version_1 = __webpack_require__(/*! ./version */ "./lib/version.js");
const Annotate_1 = __importDefault(__webpack_require__(/*! ./components/Annotate */ "./lib/components/Annotate.js"));
// Import the CSS
__webpack_require__(/*! ../css/widget.css */ "./css/widget.css");
class AnnotateModel extends base_1.DOMWidgetModel {
}
exports.AnnotateModel = AnnotateModel;
AnnotateModel.serializers = Object.assign({}, base_1.DOMWidgetModel.serializers);
AnnotateModel.model_name = "AnnotateModel";
AnnotateModel.model_module = version_1.MODULE_NAME;
AnnotateModel.model_module_version = version_1.MODULE_VERSION;
AnnotateModel.view_name = "AnnotateView"; // Set to null if no view
AnnotateModel.view_module = version_1.MODULE_NAME; // Set to null if no view
AnnotateModel.view_module_version = version_1.MODULE_VERSION;
class AnnotateView extends base_1.DOMWidgetView {
    render() {
        const docs = this.model.get("docs") || [];
        const labels = this.model.get("labels");
        const initialSpans = this.model.get("spans") || [];
        const registerSpanChangeCallback = (callback) => {
            this.model.on("change:spans", (model) => {
                if (callback) {
                    callback(model.changed.spans);
                }
            }, this);
        };
        const app = preact_1.h("div", { className: "app" }, preact_1.h(Annotate_1.default, {
            docs,
            registerSpanChangeCallback,
            labels,
            initialSpans,
            onUpdateSpans: (spans) => this.handleChange(spans),
        }));
        preact_1.render(app, this.el);
    }
    handleChange(spans) {
        this.model.set("spans", spans);
        this.model.save_changes();
    }
}
exports.AnnotateView = AnnotateView;
//# sourceMappingURL=widget.js.map

/***/ }),

/***/ "./node_modules/css-loader/dist/cjs.js!./css/widget.css":
/*!**************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./css/widget.css ***!
  \**************************************************************/
/***/ ((module, exports, __webpack_require__) => {

// Imports
var ___CSS_LOADER_API_IMPORT___ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
exports = ___CSS_LOADER_API_IMPORT___(false);
// Module
exports.push([module.id, ".content {\n  padding: 20px;\n  line-height: 1.7;\n  font-size: 18px;\n  font-family: \"Lato\", \"Trebuchet MS\", Roboto, Helvetica, Arial, sans-serif;\n\n  max-width: 720px;\n}\n.label {\n  margin: 5px 10px 5px 0;\n  cursor: pointer;\n  display: block;\n  padding: 1px 8px 1px 5px;\n  position: relative;\n  border-radius: 4px;\n  font-size: 16px;\n\n  white-space: nowrap;\n\n  background-color: #D1D5DB;\n  color: #1F2937;\n}\n.selected {\n  background: white;\n}\n.labelContainer {\n  display: flex;\n  max-width: 800px;\n  overflow-x: auto;\n  flex-grow: 1;\n  font-weight: bold;\n  font-family: \"Roboto Condensed\", \"Arial Narrow\", sans-serif;\n  text-transform: uppercase;\n  border-top-left-radius: 0;\n  border-top-right-radius: 0;\n}\n\n.topBar {\n  display: flex;\n  align-items: center;\n  justify-content: space-between;\n  color: #1F2937;\n  width: 100%;\n  padding: 12px;\n  background: #F3F4F6;\n  box-sizing: border-box;\n  font-size: 20px;\n}\n\n.nav {\n  display: flex;\n}\n\n.navLink {\n  cursor: pointer;\n  width: 16px;\n}\n\n.span {\n  font-size: 18px;\n  padding: 0.25em 0.4em;\n  padding-bottom: 2px;\n  font-weight: bold;\n  line-height: 1;\n  cursor: pointer;\n}\n\n.span:hover {\n  border-bottom: solid 1px;\n}\n\n.spanLabel {\n  font-size: 12px;\n  padding-left: 8px;\n  text-transform: uppercase;\n  color: rgb(31, 41, 55);\n}\n", ""]);
// Exports
module.exports = exports;


/***/ }),

/***/ "./css/widget.css":
/*!************************!*\
  !*** ./css/widget.css ***!
  \************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var api = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js */ "./node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js");
            var content = __webpack_require__(/*! !!../node_modules/css-loader/dist/cjs.js!./widget.css */ "./node_modules/css-loader/dist/cjs.js!./css/widget.css");

            content = content.__esModule ? content.default : content;

            if (typeof content === 'string') {
              content = [[module.id, content, '']];
            }

var options = {};

options.insert = "head";
options.singleton = false;

var update = api(content, options);



module.exports = content.locals || {};

/***/ }),

/***/ "./package.json":
/*!**********************!*\
  !*** ./package.json ***!
  \**********************/
/***/ ((module) => {

"use strict";
module.exports = JSON.parse('{"name":"jupyterannotate","version":"0.1.2","description":"A Jupyter Text Annotation Widget","keywords":["jupyter","jupyterlab","jupyterlab-extension","widgets"],"files":["lib/**/*.js","dist/*.js","css/*.css"],"homepage":"https://github.com/DataQA/jupyterannotate","bugs":{"url":"https://github.com/DataQA/jupyterannotate/issues"},"license":"BSD-3-Clause","author":{"name":"Stuart Quin","email":"stuart@dataqa.ai"},"main":"lib/index.js","types":"./lib/index.d.ts","repository":{"type":"git","url":"https://github.com/DataQA/jupyterannotate"},"scripts":{"build":"yarn run build:lib && yarn run build:nbextension && yarn run build:labextension:dev","build:prod":"yarn run build:lib && yarn run build:nbextension && yarn run build:labextension","build:labextension":"jupyter labextension build .","build:labextension:dev":"jupyter labextension build --development True .","build:lib":"tsc","build:nbextension":"webpack","clean":"yarn run clean:lib && yarn run clean:nbextension && yarn run clean:labextension","clean:lib":"rimraf lib","clean:labextension":"rimraf jupyterannotate/labextension","clean:nbextension":"rimraf jupyterannotate/nbextension/static/index.js","lint":"eslint . --ext .ts,.tsx --fix","lint:check":"eslint . --ext .ts,.tsx","prepack":"yarn run build:lib","test":"jest","watch":"npm-run-all -p watch:*","watch:lib":"tsc -w","watch:nbextension":"webpack --watch --mode=development","watch:labextension":"jupyter labextension watch ."},"dependencies":{"@jupyter-widgets/base":"^1.1.10 || ^2.0.0 || ^3.0.0 || ^4.0.0"},"devDependencies":{"@babel/core":"^7.5.0","@babel/preset-env":"^7.5.0","@faker-js/faker":"^7.4.0","@jupyterlab/builder":"^3.0.0","@phosphor/application":"^1.6.0","@phosphor/widgets":"^1.6.0","@testing-library/preact":"^3.2.2","@types/jest":"^26.0.0","@types/webpack-env":"^1.13.6","@typescript-eslint/eslint-plugin":"^3.6.0","@typescript-eslint/parser":"^3.6.0","acorn":"^7.2.0","css-loader":"^3.2.0","eslint":"^7.4.0","eslint-config-prettier":"^6.11.0","eslint-plugin-prettier":"^3.1.4","fs-extra":"^7.0.0","identity-obj-proxy":"^3.0.0","jest":"^26.0.0","mkdirp":"^0.5.1","npm-run-all":"^4.1.3","preact":"^10.10.1","prettier":"^2.0.5","rimraf":"^2.6.2","source-map-loader":"^1.1.3","style-loader":"^1.0.0","ts-jest":"^26.0.0","ts-loader":"^8.0.0","typescript":"~4.1.3","webpack":"^5.61.0","webpack-cli":"^4.0.0"},"jupyterlab":{"extension":"lib/plugin","outputDir":"jupyterannotate/labextension/","sharedPackages":{"@jupyter-widgets/base":{"bundled":false,"singleton":true}}}}');

/***/ })

}]);
//# sourceMappingURL=lib_widget_js.82d05bfd25cb2ac56520.js.map