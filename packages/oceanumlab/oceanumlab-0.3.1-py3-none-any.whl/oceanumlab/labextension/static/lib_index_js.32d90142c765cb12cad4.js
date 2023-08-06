"use strict";
(self["webpackChunk_oceanum_oceanumlab"] = self["webpackChunk_oceanum_oceanumlab"] || []).push([["lib_index_js"],{

/***/ "./lib/DatameshUI.js":
/*!***************************!*\
  !*** ./lib/DatameshUI.js ***!
  \***************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "DatameshUI": () => (/* binding */ DatameshUI)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);


class DatameshUI extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ReactWidget {
    render() {
        return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("iframe", { src: `${"https://ui.datamesh.oceanum.io"}`, className: "datamesh-iframe" }));
    }
}


/***/ }),

/***/ "./lib/DatameshWidget.js":
/*!*******************************!*\
  !*** ./lib/DatameshWidget.js ***!
  \*******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "DatameshConnectWidget": () => (/* binding */ DatameshConnectWidget)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_cells__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/cells */ "webpack/sharing/consume/default/@jupyterlab/cells");
/* harmony import */ var _jupyterlab_cells__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_cells__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @lumino/coreutils */ "webpack/sharing/consume/default/@lumino/coreutils");
/* harmony import */ var _lumino_coreutils__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_lumino_coreutils__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _lumino_dragdrop__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @lumino/dragdrop */ "webpack/sharing/consume/default/@lumino/dragdrop");
/* harmony import */ var _lumino_dragdrop__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_lumino_dragdrop__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_7___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_7__);
/* harmony import */ var _DatasourceItem__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ./DatasourceItem */ "./lib/DatasourceItem.js");









const JUPYTER_CELL_MIME = 'application/vnd.jupyter.cells';
const datasourceCode = (datasource, notebook, icell) => {
    const datameshImport = notebook &&
        notebook.widgets.find(cell => {
            let found = false;
            for (let i = 0; i < icell; i++) {
                const line = cell.editor.getLine(i);
                if (line &&
                    line.indexOf('from oceanum.datamesh import Connector') >= 0) {
                    found = true;
                    break;
                }
            }
            return found;
        });
    let datasourceStr = datasource.datasource.replace(/[\s-.]/g, '_');
    if (datasource.variables ||
        datasource.geofilter ||
        datasource.timefilter ||
        datasource.spatialref) {
        datasourceStr += `=datamesh.query(${JSON.stringify(datasource)})`;
    }
    else {
        datasourceStr += `=datamesh.load_datasource('${datasource.datasource}')`;
    }
    if (!datameshImport) {
        datasourceStr =
            'from oceanum.datamesh import Connector' +
                '\n' +
                `datamesh=Connector("${window.datameshToken}")` +
                '\n' +
                datasourceStr;
    }
    return datasourceStr;
};
class DatameshWorkspaceDisplay extends (react__WEBPACK_IMPORTED_MODULE_7___default().Component) {
    constructor(props) {
        super(props);
        // Handle code datasource insert into an editor
        this.insertDatameshConnect = async (datasource) => {
            const widget = this.props.getCurrentWidget();
            if (widget instanceof _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2__.NotebookPanel) {
                const notebookWidget = widget;
                const notebookCell = notebookWidget.content.activeCell;
                const notebookCellIndex = notebookWidget.content
                    .activeCellIndex;
                const notebookCellEditor = notebookCell.editor;
                const datasourceStr = datasourceCode(datasource, notebookWidget.content, notebookCellIndex);
                if (notebookCell instanceof _jupyterlab_cells__WEBPACK_IMPORTED_MODULE_1__.CodeCell) {
                    this.verifyLanguageAndInsert(datasource, 'python', notebookCellEditor, notebookWidget.content, notebookCellIndex);
                }
                else {
                    notebookCellEditor.replaceSelection(datasourceStr);
                }
                const cell = notebookWidget.model.contentFactory.createCodeCell({});
                notebookWidget.model.cells.insert(notebookCellIndex + 1, cell);
            }
            else {
                this.showErrDialog('Datamesh datasource insert failed: Please select code cell');
            }
        };
        // Handle language compatibility between code datasource and editor
        this.verifyLanguageAndInsert = async (datasource, editorLanguage, editor, notebook, icell) => {
            const datasourceStr = datasourceCode(datasource, notebook, icell);
            if (editorLanguage && 'python' !== editorLanguage.toLowerCase()) {
                const result = await this.showWarnDialog(editorLanguage, datasource.description);
                if (result.button.accept) {
                    editor.replaceSelection(datasourceStr);
                }
            }
            else {
                // Language match or editorLanguage is unavailable
                editor.replaceSelection(datasourceStr);
            }
        };
        // Display warning dialog when inserting a code datasource incompatible with editor's language
        this.showWarnDialog = async (editorLanguage, datasourceName) => {
            return (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showDialog)({
                title: 'Warning',
                body: `Datasource connect is incompatible with ${editorLanguage}. Continue?`,
                buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.cancelButton(), _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.okButton()]
            });
        };
        // Display error dialog when inserting a code datasource into unsupported widget (i.e. not an editor)
        this.showErrDialog = (errMsg) => {
            return (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.showDialog)({
                title: 'Error',
                body: errMsg,
                buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.okButton()]
            });
        };
        this._drag = null;
        this._dragData = null;
        this.handleDragMove = this.handleDragMove.bind(this);
        this._evtMouseUp = this._evtMouseUp.bind(this);
    }
    render() {
        return (react__WEBPACK_IMPORTED_MODULE_7___default().createElement("div", { className: 'datamesh-workspace-display' }, this.props.spec && (react__WEBPACK_IMPORTED_MODULE_7___default().createElement("div", null,
            react__WEBPACK_IMPORTED_MODULE_7___default().createElement("span", { className: "datamesh-workspace-name" }, this.props.spec.name),
            react__WEBPACK_IMPORTED_MODULE_7___default().createElement("hr", null),
            this.props.spec.data.map(datasource => (
            // Render display of a code datasource
            react__WEBPACK_IMPORTED_MODULE_7___default().createElement("div", { key: datasource.id, "data-item-id": datasource.id, className: 'datasource-item' },
                react__WEBPACK_IMPORTED_MODULE_7___default().createElement(_DatasourceItem__WEBPACK_IMPORTED_MODULE_8__.DatasourceItem, { datasource: datasource, insertDatasource: this.insertDatameshConnect, onMouseDown: (event) => {
                        this.handleDragSnippet(event, datasource);
                    } }))))))));
    }
    // Initial setup to handle dragging a code datasource
    handleDragSnippet(event, datasource) {
        const { button } = event;
        // do nothing if left mouse button is clicked
        if (button !== 0) {
            return;
        }
        this._dragData = {
            pressX: event.clientX,
            pressY: event.clientY,
            dragImage: null
        };
        const mouseUpListener = (event) => {
            this._evtMouseUp(event, datasource, mouseMoveListener);
        };
        const mouseMoveListener = (event) => {
            this.handleDragMove(event, datasource, mouseMoveListener, mouseUpListener);
        };
        const target = event.target;
        target.addEventListener('mouseup', mouseUpListener, {
            once: true,
            capture: true
        });
        target.addEventListener('mousemove', mouseMoveListener, true);
        // since a browser has its own drag'n'drop support for images and some other elements.
        target.ondragstart = () => false;
    }
    _evtMouseUp(event, datasource, mouseMoveListener) {
        event.preventDefault();
        event.stopPropagation();
        const target = event.target;
        target.removeEventListener('mousemove', mouseMoveListener, true);
    }
    handleDragMove(event, datasource, mouseMoveListener, mouseUpListener) {
        event.preventDefault();
        event.stopPropagation();
        const data = this._dragData;
        if (data &&
            this.shouldStartDrag(data.pressX, data.pressY, event.clientX, event.clientY)) {
            // Create drag image
            const element = document.createElement('div');
            element.innerHTML = datasource.description;
            element.classList.add('datasource-drag-image');
            data.dragImage = element;
            // Remove mouse listeners and start the drag.
            const target = event.target;
            target.removeEventListener('mousemove', mouseMoveListener, true);
            target.removeEventListener('mouseup', mouseUpListener, true);
            void this.startDrag(data.dragImage, datasource, event.clientX, event.clientY);
        }
    }
    /**
     * Detect if a drag event should be started. This is down if the
     * mouse is moved beyond a certain distance (DRAG_THRESHOLD).
     *
     * @param prevX - X Coordinate of the mouse pointer during the mousedown event
     * @param prevY - Y Coordinate of the mouse pointer during the mousedown event
     * @param nextX - Current X Coordinate of the mouse pointer
     * @param nextY - Current Y Coordinate of the mouse pointer
     */
    shouldStartDrag(prevX, prevY, nextX, nextY) {
        const dx = Math.abs(nextX - prevX);
        const dy = Math.abs(nextY - prevY);
        return dx >= 0 || dy >= 5;
    }
    async startDrag(dragImage, datasource, clientX, clientY) {
        const contentFactory = new _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_2__.NotebookModel.ContentFactory({});
        const model = contentFactory.createCodeCell({});
        const content = datasourceCode(datasource, null, 0);
        model.value.text = content;
        this._drag = new _lumino_dragdrop__WEBPACK_IMPORTED_MODULE_5__.Drag({
            mimeData: new _lumino_coreutils__WEBPACK_IMPORTED_MODULE_4__.MimeData(),
            dragImage: dragImage,
            supportedActions: 'copy-move',
            proposedAction: 'copy',
            source: this
        });
        const selected = [model.toJSON()];
        this._drag.mimeData.setData(JUPYTER_CELL_MIME, selected);
        this._drag.mimeData.setData('text/plain', datasource.description);
        return this._drag.start(clientX, clientY).then(() => {
            this._drag = null;
            this._dragData = null;
        });
    }
}
/**
 * A widget for Datamesh Connections.
 */
class DatameshConnectWidget extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ReactWidget {
    constructor(props) {
        super();
        this.datameshWorkspaceSpec = null;
        this.props = props;
        this.renderSignal = new _lumino_signaling__WEBPACK_IMPORTED_MODULE_6__.Signal(this);
        this.renderDisplay = this.renderDisplay.bind(this);
        window.addEventListener('message', this.receiveIFrameMessage.bind(this), false);
    }
    receiveIFrameMessage(event) {
        if (event.data && event.data.action === 'workspace-modify') {
            this.datameshWorkspaceSpec = {
                id: event.data.id,
                name: event.data.name,
                data: event.data.data
            };
            console.log(this.datameshWorkspaceSpec);
            this.renderSignal.emit(this.datameshWorkspaceSpec);
        }
    }
    renderDisplay(datameshWorkspace) {
        return (react__WEBPACK_IMPORTED_MODULE_7___default().createElement((react__WEBPACK_IMPORTED_MODULE_7___default().Fragment), null, this.datameshWorkspaceSpec ? (react__WEBPACK_IMPORTED_MODULE_7___default().createElement(DatameshWorkspaceDisplay, { spec: datameshWorkspace, openDatameshUI: this.props.openDatameshUI, getCurrentWidget: this.props.getCurrentWidget, shell: this.props.app.shell })) : (react__WEBPACK_IMPORTED_MODULE_7___default().createElement("div", { className: "datasource-item-details" },
            react__WEBPACK_IMPORTED_MODULE_7___default().createElement("a", { onClick: this.props.openDatameshUI }, "Open"),
            " the Oceanum datamesh UI to add datasources. You will need to allow popups on this page if you are not already logged in to Oceanum.io."))));
    }
    render() {
        return (react__WEBPACK_IMPORTED_MODULE_7___default().createElement("div", { className: 'datamesh-connect' },
            react__WEBPACK_IMPORTED_MODULE_7___default().createElement("header", { className: 'datamesh-connect-header' },
                react__WEBPACK_IMPORTED_MODULE_7___default().createElement(this.props.icon.react, { tag: "span", width: "auto", height: "24px", verticalAlign: "middle", marginRight: "5px" }),
                react__WEBPACK_IMPORTED_MODULE_7___default().createElement("p", null, " Datamesh workspace "),
                react__WEBPACK_IMPORTED_MODULE_7___default().createElement("div", { className: "open-datamesh-ui", onClick: this.props.openDatameshUI, title: 'Open Datamesh UI' }, react__WEBPACK_IMPORTED_MODULE_7___default().createElement(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3__.addIcon.react, { height: "24px", verticalAlign: "middle" }))),
            react__WEBPACK_IMPORTED_MODULE_7___default().createElement(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.UseSignal, { signal: this.renderSignal, initialArgs: null }, (_, datameshWorkspace) => this.renderDisplay(datameshWorkspace))));
    }
}


/***/ }),

/***/ "./lib/DatasourceItem.js":
/*!*******************************!*\
  !*** ./lib/DatasourceItem.js ***!
  \*******************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "DatasourceItem": () => (/* binding */ DatasourceItem)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var phosphor_react__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! phosphor-react */ "webpack/sharing/consume/default/phosphor-react/phosphor-react");
/* harmony import */ var phosphor_react__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(phosphor_react__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _style_index_css__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ../style/index.css */ "./style/index.css");




/**
 * A React component for expandable containers.
 */
const DatasourceItem = ({ datasource, insertDatasource, onMouseDown }) => {
    const [expanded, setExpandedValue] = (0,react__WEBPACK_IMPORTED_MODULE_0__.useState)(false);
    const handleToggleExpand = () => {
        setExpandedValue(!expanded);
    };
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: expanded && 'expanded' },
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { key: datasource.id, className: "datasource-item-title" },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("button", { title: expanded ? 'Hide Details' : 'Show Details', onClick: handleToggleExpand, className: "datasource-item-expand" }, expanded ? (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.caretDownIcon.react, { tag: "span", elementPosition: "center", width: "20px" })) : (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.caretRightIcon.react, { tag: "span", elementPosition: "center", width: "20px" }))),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", { title: datasource.description, className: onMouseDown
                    ? 'datasource-item-name'
                    : 'datasource-item-name draggable', onClick: handleToggleExpand, onMouseDown: e => onMouseDown(e, datasource) }, datasource.description),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("button", { title: "Insert code to load datasource", onClick: handleToggleExpand, className: "datasource-item-action" },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(phosphor_react__WEBPACK_IMPORTED_MODULE_2__.ArrowBendDownRight, { size: 18, onClick: e => insertDatasource(datasource) }))),
        expanded && (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: 'datasource-item-details' },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: "datasource-query-field" },
                "Datasource id: ",
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", null, datasource.datasource)),
            datasource.geofilter && (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: "datasource-query-field" },
                "Geofilter type:",
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", null, datasource.geofilter.type))),
            datasource.variables && (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: "datasource-query-field" },
                "Variables:",
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", null, datasource.variables.join(',')))),
            datasource.timefilter && (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: "datasource-query-field" },
                "Timefilter:",
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", null, datasource.timefilter.times[0]),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", null, "to"),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", null, datasource.timefilter.times[1]))),
            datasource.spatialref && (react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", { className: "datasource-query-field" },
                "Spatial ref:",
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("span", null, datasource.spatialref))),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("div", null,
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement("a", { href: `https://oceanum.io/datasets/${datasource.datasource}`, target: "_blank" }, "Datasource details"))))));
};


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "datamesh_connect_extension": () => (/* binding */ datamesh_connect_extension),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/application */ "webpack/sharing/consume/default/@jupyterlab/application");
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _lumino_algorithm__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @lumino/algorithm */ "webpack/sharing/consume/default/@lumino/algorithm");
/* harmony import */ var _lumino_algorithm__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_lumino_algorithm__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @jupyterlab/settingregistry */ "webpack/sharing/consume/default/@jupyterlab/settingregistry");
/* harmony import */ var _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var _DatameshWidget__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! ./DatameshWidget */ "./lib/DatameshWidget.js");
/* harmony import */ var _DatameshUI__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! ./DatameshUI */ "./lib/DatameshUI.js");
/* harmony import */ var _style_index_css__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ../style/index.css */ "./style/index.css");
/* harmony import */ var _style_icons_oceanum_svg__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ../style/icons/oceanum.svg */ "./style/icons/oceanum.svg");











const oceanumIcon = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_3__.LabIcon({
    name: 'oceanum:main',
    svgstr: _style_icons_oceanum_svg__WEBPACK_IMPORTED_MODULE_8__["default"]
});
/**
 * Initialization data for the extension.
 */
const datamesh_connect_extension = {
    id: 'datamesh-connect',
    autoStart: true,
    requires: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ICommandPalette, _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__.ILayoutRestorer, _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__.ILabStatus, _jupyterlab_settingregistry__WEBPACK_IMPORTED_MODULE_6__.ISettingRegistry],
    optional: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.IThemeManager],
    activate: (app, palette, restorer, status, settingRegistry, themeManager) => {
        console.log('Oceanum datamesh connect extension is loaded');
        //Try to get the datamesh token from the settings
        const serversettings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_5__.ServerConnection.makeSettings();
        //let pluginSettings: ISettingRegistry.ISettings = null;
        const updateSettings = (set) => {
            const setting = set.get('datameshToken');
            if (setting && setting.user) {
                window.datameshToken = setting.user;
            }
        };
        settingRegistry.load('@oceanum/oceanumlab:plugin').then(set => {
            set.changed.connect(updateSettings, undefined);
            updateSettings(set);
        });
        //Try to get the datamesh token from the envars
        const requestUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_2__.URLExt.join(serversettings.baseUrl, 'oceanum', 'env', 'DATAMESH_TOKEN');
        fetch(requestUrl)
            .then(res => res.json())
            .then(json => {
            if (!window.datameshToken)
                window.datameshToken = json['DATAMESH_TOKEN'];
        });
        const getCurrentWidget = () => {
            return app.shell.currentWidget;
        };
        const openDatameshUI = (event) => {
            const widgetId = 'datamesh-ui';
            const openWidget = (0,_lumino_algorithm__WEBPACK_IMPORTED_MODULE_4__.find)(app.shell.widgets('main'), (widget, index) => {
                return widget.id === widgetId;
            });
            if (openWidget) {
                app.shell.activateById(widgetId);
                return;
            }
            const datameshUIWidget = new _DatameshUI__WEBPACK_IMPORTED_MODULE_9__.DatameshUI();
            datameshUIWidget.title.label = 'Oceanum Datamesh';
            datameshUIWidget.id = widgetId;
            datameshUIWidget.title.closable = true;
            datameshUIWidget.title.icon = oceanumIcon;
            datameshUIWidget.addClass('datamesh-ui');
            app.shell.add(datameshUIWidget, 'main');
        };
        const datameshConnectWidget = new _DatameshWidget__WEBPACK_IMPORTED_MODULE_10__.DatameshConnectWidget({
            app,
            name: 'Datamesh Connect',
            icon: oceanumIcon,
            openDatameshUI: openDatameshUI,
            getCurrentWidget
        });
        datameshConnectWidget.id = 'datamesh-connect';
        datameshConnectWidget.title.icon = oceanumIcon;
        datameshConnectWidget.title.caption = 'Datamesh Connect';
        restorer.add(datameshConnectWidget, 'datamesh-connect');
        // Rank has been chosen somewhat arbitrarily to give priority to the running
        // sessions widget in the sidebar.
        app.shell.add(datameshConnectWidget, 'left', { rank: 900 });
        app.commands.addCommand('datamesh-ui:open', {
            execute: (args) => {
                openDatameshUI(args);
            }
        });
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (datamesh_connect_extension);


/***/ }),

/***/ "./node_modules/css-loader/dist/cjs.js!./style/base.css":
/*!**************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./style/base.css ***!
  \**************************************************************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_css_loader_dist_runtime_cssWithMappingToString_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/cssWithMappingToString.js */ "./node_modules/css-loader/dist/runtime/cssWithMappingToString.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_cssWithMappingToString_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_cssWithMappingToString_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
// Imports


var ___CSS_LOADER_EXPORT___ = _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_node_modules_css_loader_dist_runtime_cssWithMappingToString_js__WEBPACK_IMPORTED_MODULE_0___default()));
// Module
___CSS_LOADER_EXPORT___.push([module.id, "", "",{"version":3,"sources":[],"names":[],"mappings":"","sourceRoot":""}]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ }),

/***/ "./node_modules/css-loader/dist/cjs.js!./style/index.css":
/*!***************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./style/index.css ***!
  \***************************************************************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_css_loader_dist_runtime_cssWithMappingToString_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/cssWithMappingToString.js */ "./node_modules/css-loader/dist/runtime/cssWithMappingToString.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_cssWithMappingToString_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_cssWithMappingToString_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _node_modules_css_loader_dist_cjs_js_base_css__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! -!../node_modules/css-loader/dist/cjs.js!./base.css */ "./node_modules/css-loader/dist/cjs.js!./style/base.css");
// Imports



var ___CSS_LOADER_EXPORT___ = _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_node_modules_css_loader_dist_runtime_cssWithMappingToString_js__WEBPACK_IMPORTED_MODULE_0___default()));
___CSS_LOADER_EXPORT___.i(_node_modules_css_loader_dist_cjs_js_base_css__WEBPACK_IMPORTED_MODULE_2__["default"]);
// Module
___CSS_LOADER_EXPORT___.push([module.id, ".datasource-drag-image {\n  border: var(--jp-border-width) solid var(--jp-cell-editor-border-color);\n  width: var(--jp-private-notebook-dragImage-width);\n  height: var(--jp-private-notebook-dragImage-height);\n  color: var(--jp-ui-font-color1);\n  background: var(--jp-layout-color1);\n}\n\n.datamesh-iframe {\n  width: 98%;\n  height: 98%;\n  padding: 5px;\n}\n\n.datamesh-connect {\n  color: var(--jp-ui-font-color1);\n  background: var(--jp-layout-color1);\n  height: 100%;\n}\n\n.datamesh-connect a {\n  color: var(--jp-content-link-color);\n}\n\n.datamesh-connect-header {\n  font-weight: bold;\n  padding: 8px 10px;\n  display: flex;\n  justify-content: space-between;\n}\n\n.datamesh-connect-header p {\n  font-weight: bold;\n}\n\n.add-connection {\n  border-radius: 4px;\n}\n\n.add-connection :hover {\n  background-color: #ddd;\n}\n\n.datasource-list-item {\n  border-bottom: var(--jp-border-width) solid var(--jp-border-color2);\n  display: flex;\n  flex-direction: column;\n  margin: 0;\n  padding: 0;\n}\n\n.open-datamesh-ui {\n  cursor: pointer;\n}\n\n.datamesh-workspace-name {\n  flex: 0 0 auto;\n  font-weight: 600;\n  text-transform: uppercase;\n  letter-spacing: 1px;\n  padding: 8px 8px 8px 12px;\n  margin: 0px;\n  margin-left: 0px;\n  margin-bottom: 10px;\n  font-size: var(--jp-ui-font-size1);\n}\n\n.datasource-item-expand,\n.datasource-item-action,\n.datasource-item-expand.jp-mod-styled {\n  background-color: transparent;\n  vertical-align: middle;\n  padding: 0;\n  width: 20px;\n  border: none;\n}\n\n.datasource-item-expand:hover {\n  cursor: pointer;\n}\n\n.datasource-item-details {\n  overflow-x: auto;\n  overflow-y: auto;\n  display: block;\n  padding: 5px;\n  margin: 5px;\n  border: 1px solid var(--jp-border-color2);\n  border-radius: 2px;\n  color: var(--jp-ui-font-color1);\n  background-color: var(--jp-layout-color1);\n}\n\n.datasource-item-details textarea {\n  color: var(--jp-ui-font-color1);\n}\n\n.datasource-item-action {\n  display: inline-flex;\n  align-self: flex-end;\n  align-items: center;\n  height: 100%;\n  border: none;\n}\n\n.datasource-item-action:hover,\n.datasource-item-name:hover {\n  cursor: pointer;\n}\n\n.datasource-item-name {\n  flex-grow: 1;\n  font-size: var(--jp-ui-font-size1);\n  white-space: nowrap;\n  overflow: hidden;\n  text-overflow: ellipsis;\n  padding: 4px 0 4px 2px;\n  line-height: 28px;\n}\n\n.datasource-item-title {\n  align-items: center;\n  display: flex;\n  flex-direction: row;\n  padding: 0px 4px;\n  height: 36px;\n}\n\n.datasource-item-title:hover {\n  background-color: var(--jp-layout-color2);\n}\n\n.datasource-query-field span {\n  margin-left: 5px;\n  white-space: nowrap;\n  font-size: var(--jp-ui-font-size0);\n}\n\n.expanded {\n  background-color: var(--jp-layout-color2);\n  padding: 2px;\n}\n", "",{"version":3,"sources":["webpack://./style/index.css"],"names":[],"mappings":"AAEA;EACE,uEAAuE;EACvE,iDAAiD;EACjD,mDAAmD;EACnD,+BAA+B;EAC/B,mCAAmC;AACrC;;AAEA;EACE,UAAU;EACV,WAAW;EACX,YAAY;AACd;;AAEA;EACE,+BAA+B;EAC/B,mCAAmC;EACnC,YAAY;AACd;;AAEA;EACE,mCAAmC;AACrC;;AAEA;EACE,iBAAiB;EACjB,iBAAiB;EACjB,aAAa;EACb,8BAA8B;AAChC;;AAEA;EACE,iBAAiB;AACnB;;AAEA;EACE,kBAAkB;AACpB;;AAEA;EACE,sBAAsB;AACxB;;AAEA;EACE,mEAAmE;EACnE,aAAa;EACb,sBAAsB;EACtB,SAAS;EACT,UAAU;AACZ;;AAEA;EACE,eAAe;AACjB;;AAEA;EACE,cAAc;EACd,gBAAgB;EAChB,yBAAyB;EACzB,mBAAmB;EACnB,yBAAyB;EACzB,WAAW;EACX,gBAAgB;EAChB,mBAAmB;EACnB,kCAAkC;AACpC;;AAEA;;;EAGE,6BAA6B;EAC7B,sBAAsB;EACtB,UAAU;EACV,WAAW;EACX,YAAY;AACd;;AAEA;EACE,eAAe;AACjB;;AAEA;EACE,gBAAgB;EAChB,gBAAgB;EAChB,cAAc;EACd,YAAY;EACZ,WAAW;EACX,yCAAyC;EACzC,kBAAkB;EAClB,+BAA+B;EAC/B,yCAAyC;AAC3C;;AAEA;EACE,+BAA+B;AACjC;;AAEA;EACE,oBAAoB;EACpB,oBAAoB;EACpB,mBAAmB;EACnB,YAAY;EACZ,YAAY;AACd;;AAEA;;EAEE,eAAe;AACjB;;AAEA;EACE,YAAY;EACZ,kCAAkC;EAClC,mBAAmB;EACnB,gBAAgB;EAChB,uBAAuB;EACvB,sBAAsB;EACtB,iBAAiB;AACnB;;AAEA;EACE,mBAAmB;EACnB,aAAa;EACb,mBAAmB;EACnB,gBAAgB;EAChB,YAAY;AACd;;AAEA;EACE,yCAAyC;AAC3C;;AAEA;EACE,gBAAgB;EAChB,mBAAmB;EACnB,kCAAkC;AACpC;;AAEA;EACE,yCAAyC;EACzC,YAAY;AACd","sourcesContent":["@import url('base.css');\n\n.datasource-drag-image {\n  border: var(--jp-border-width) solid var(--jp-cell-editor-border-color);\n  width: var(--jp-private-notebook-dragImage-width);\n  height: var(--jp-private-notebook-dragImage-height);\n  color: var(--jp-ui-font-color1);\n  background: var(--jp-layout-color1);\n}\n\n.datamesh-iframe {\n  width: 98%;\n  height: 98%;\n  padding: 5px;\n}\n\n.datamesh-connect {\n  color: var(--jp-ui-font-color1);\n  background: var(--jp-layout-color1);\n  height: 100%;\n}\n\n.datamesh-connect a {\n  color: var(--jp-content-link-color);\n}\n\n.datamesh-connect-header {\n  font-weight: bold;\n  padding: 8px 10px;\n  display: flex;\n  justify-content: space-between;\n}\n\n.datamesh-connect-header p {\n  font-weight: bold;\n}\n\n.add-connection {\n  border-radius: 4px;\n}\n\n.add-connection :hover {\n  background-color: #ddd;\n}\n\n.datasource-list-item {\n  border-bottom: var(--jp-border-width) solid var(--jp-border-color2);\n  display: flex;\n  flex-direction: column;\n  margin: 0;\n  padding: 0;\n}\n\n.open-datamesh-ui {\n  cursor: pointer;\n}\n\n.datamesh-workspace-name {\n  flex: 0 0 auto;\n  font-weight: 600;\n  text-transform: uppercase;\n  letter-spacing: 1px;\n  padding: 8px 8px 8px 12px;\n  margin: 0px;\n  margin-left: 0px;\n  margin-bottom: 10px;\n  font-size: var(--jp-ui-font-size1);\n}\n\n.datasource-item-expand,\n.datasource-item-action,\n.datasource-item-expand.jp-mod-styled {\n  background-color: transparent;\n  vertical-align: middle;\n  padding: 0;\n  width: 20px;\n  border: none;\n}\n\n.datasource-item-expand:hover {\n  cursor: pointer;\n}\n\n.datasource-item-details {\n  overflow-x: auto;\n  overflow-y: auto;\n  display: block;\n  padding: 5px;\n  margin: 5px;\n  border: 1px solid var(--jp-border-color2);\n  border-radius: 2px;\n  color: var(--jp-ui-font-color1);\n  background-color: var(--jp-layout-color1);\n}\n\n.datasource-item-details textarea {\n  color: var(--jp-ui-font-color1);\n}\n\n.datasource-item-action {\n  display: inline-flex;\n  align-self: flex-end;\n  align-items: center;\n  height: 100%;\n  border: none;\n}\n\n.datasource-item-action:hover,\n.datasource-item-name:hover {\n  cursor: pointer;\n}\n\n.datasource-item-name {\n  flex-grow: 1;\n  font-size: var(--jp-ui-font-size1);\n  white-space: nowrap;\n  overflow: hidden;\n  text-overflow: ellipsis;\n  padding: 4px 0 4px 2px;\n  line-height: 28px;\n}\n\n.datasource-item-title {\n  align-items: center;\n  display: flex;\n  flex-direction: row;\n  padding: 0px 4px;\n  height: 36px;\n}\n\n.datasource-item-title:hover {\n  background-color: var(--jp-layout-color2);\n}\n\n.datasource-query-field span {\n  margin-left: 5px;\n  white-space: nowrap;\n  font-size: var(--jp-ui-font-size0);\n}\n\n.expanded {\n  background-color: var(--jp-layout-color2);\n  padding: 2px;\n}\n"],"sourceRoot":""}]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ }),

/***/ "./style/icons/oceanum.svg":
/*!*********************************!*\
  !*** ./style/icons/oceanum.svg ***!
  \*********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = ("<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"44\" height=\"44\" viewBox=\"0 0 44.079582 44.079582\" version=\"1.1\" id=\"svg5870\">\n  <g\n     id=\"layer1\"\n     transform=\"translate(-82.281595,-124.52568)\">\n    <g\n       style=\"stroke:#3b547c;stroke-opacity:1\"\n       transform=\"matrix(0.26458333,0,0,0.26458333,69.475762,109.81485)\"\n       id=\"g2915\"\n       >\n      <g\n         style=\"stroke:#3b547c;stroke-opacity:1\"\n         id=\"g2903\">\n        <path\n           id=\"path2897\"\n           d=\"m 212.3,149.9 c -35.8,19.1 -58.2,-11 -80.6,-11 -22.4,0 -44.7,30.1 -80.6,11 1.2,8.7 3.8,17.2 7.7,25.1 38.7,13.5 55.8,-8.4 72.9,-8.4 17.1,0 34.1,22 72.9,8.4 3.9,-7.9 6.5,-16.3 7.7,-25.1 z\"\n           class=\"st8\"\n           \n           style=\"fill:#dce1f9;stroke:#3b547c;stroke-opacity:1\" />\n        <path\n           id=\"path2899\"\n           d=\"m 204.6,175 c -38.7,13.5 -55.8,-8.4 -72.9,-8.4 -17.1,0 -34.1,22 -72.9,8.4 4.4,8.9 10.4,16.9 17.7,23.6 31.1,6.8 43.1,-6.5 55.2,-6.5 12.1,0 24.1,13.3 55.2,6.5 7.3,-6.7 13.3,-14.7 17.7,-23.6 z\"\n           class=\"st8\"\n           \n           style=\"fill:#dce1f9;stroke:#3b547c;stroke-opacity:1\" />\n        <path\n           id=\"path2901\"\n           d=\"m 76.5,198.7 c 31.1,6.8 43.1,-6.5 55.2,-6.5 12.1,0 24.1,13.3 55.2,6.5 -15,13.9 -34.7,21.6 -55.2,21.6 -20.4,-0.1 -40.2,-7.8 -55.2,-21.6 z\"\n           class=\"st8\"\n           \n           style=\"fill:#dce1f9;stroke:#3b547c;stroke-opacity:1\" />\n      </g>\n      <g\n         style=\"stroke:#3b547c;stroke-opacity:1\"\n         id=\"g2913\">\n        <path\n           id=\"path2905\"\n           d=\"m 58.8,175 c 38.7,13.5 55.8,-8.4 72.9,-8.4 17.1,0 34.1,22 72.9,8.4\"\n           class=\"st9\"\n           \n           style=\"fill:none;stroke:#3b547c;stroke-width:4;stroke-linecap:round;stroke-linejoin:round;stroke-opacity:1\" />\n        <path\n           id=\"path2907\"\n           d=\"m 51.1,149.9 c 35.8,19.1 58.2,-11 80.6,-11 22.4,0 44.7,30.1 80.6,11\"\n           class=\"st9\"\n           \n           style=\"fill:none;stroke:#3b547c;stroke-width:4;stroke-linecap:round;stroke-linejoin:round;stroke-opacity:1\" />\n        <path\n           id=\"path2909\"\n           d=\"m 76.5,198.7 c 31.1,6.8 43.1,-6.5 55.2,-6.5 12.1,0 24.1,13.3 55.2,6.5\"\n           class=\"st9\"\n           \n           style=\"fill:none;stroke:#3b547c;stroke-width:4;stroke-linecap:round;stroke-linejoin:round;stroke-opacity:1\" />\n        <path\n           id=\"path2911\"\n           d=\"m 131.7,220.2 c 10.3,0 20.4,-1.9 29.9,-5.7 10.3,-4.1 19.7,-10.2 27.6,-18.1 7.9,-7.9 14,-17.2 18.1,-27.6 3.8,-9.5 5.7,-19.7 5.7,-29.9 0,-10.3 -1.9,-20.4 -5.7,-29.9 -4.1,-10.3 -10.2,-19.7 -18.1,-27.6 -7.9,-7.9 -17.2,-14 -27.6,-18.1 -9.5,-3.8 -19.7,-5.7 -29.9,-5.7 -10.3,0 -20.4,1.9 -29.9,5.7 -10.3,4.1 -19.7,10.2 -27.6,18.1 -7.9,7.9 -14,17.2 -18.1,27.6 -3.8,9.5 -5.7,19.7 -5.7,29.9 0,10.3 1.9,20.4 5.7,29.9 4.1,10.3 10.2,19.7 18.1,27.6 7.9,7.9 17.2,14 27.6,18.1 9.5,3.8 19.6,5.7 29.9,5.7 z\"\n           class=\"st9\"\n           \n           style=\"fill:none;stroke:#3b547c;stroke-width:4;stroke-linecap:round;stroke-linejoin:round;stroke-opacity:1\" />\n      </g>\n    </g>\n    <g\n       id=\"g3308\"\n       transform=\"matrix(0.26458333,0,0,0.26458333,69.475762,109.81485)\"\n       style=\"stroke:#3b547c;stroke-opacity:1\">\n      <g\n         id=\"g3296\"\n         style=\"stroke:#3b547c;stroke-opacity:1\">\n        <path\n           style=\"fill:#dce1f9;stroke:#3b547c;stroke-opacity:1\"\n           \n           class=\"st8\"\n           d=\"m 212.3,149.9 c -35.8,19.1 -58.2,-11 -80.6,-11 -22.4,0 -44.7,30.1 -80.6,11 1.2,8.7 3.8,17.2 7.7,25.1 38.7,13.5 55.8,-8.4 72.9,-8.4 17.1,0 34.1,22 72.9,8.4 3.9,-7.9 6.5,-16.3 7.7,-25.1 z\"\n           id=\"path3290\" />\n        <path\n           style=\"fill:#dce1f9;stroke:#3b547c;stroke-opacity:1\"\n           \n           class=\"st8\"\n           d=\"m 204.6,175 c -38.7,13.5 -55.8,-8.4 -72.9,-8.4 -17.1,0 -34.1,22 -72.9,8.4 4.4,8.9 10.4,16.9 17.7,23.6 31.1,6.8 43.1,-6.5 55.2,-6.5 12.1,0 24.1,13.3 55.2,6.5 7.3,-6.7 13.3,-14.7 17.7,-23.6 z\"\n           id=\"path3292\" />\n        <path\n           style=\"fill:#dce1f9;stroke:#3b547c;stroke-opacity:1\"\n           \n           class=\"st8\"\n           d=\"m 76.5,198.7 c 31.1,6.8 43.1,-6.5 55.2,-6.5 12.1,0 24.1,13.3 55.2,6.5 -15,13.9 -34.7,21.6 -55.2,21.6 -20.4,-0.1 -40.2,-7.8 -55.2,-21.6 z\"\n           id=\"path3294\" />\n      </g>\n      <g\n         id=\"g3306\"\n         style=\"stroke:#3b547c;stroke-opacity:1\">\n        <path\n           style=\"fill:none;stroke:#3b547c;stroke-width:4;stroke-linecap:round;stroke-linejoin:round;stroke-opacity:1\"\n           \n           class=\"st9\"\n           d=\"m 58.8,175 c 38.7,13.5 55.8,-8.4 72.9,-8.4 17.1,0 34.1,22 72.9,8.4\"\n           id=\"path3298\" />\n        <path\n           style=\"fill:none;stroke:#3b547c;stroke-width:4;stroke-linecap:round;stroke-linejoin:round;stroke-opacity:1\"\n           \n           class=\"st9\"\n           d=\"m 51.1,149.9 c 35.8,19.1 58.2,-11 80.6,-11 22.4,0 44.7,30.1 80.6,11\"\n           id=\"path3300\" />\n        <path\n           style=\"fill:none;stroke:#3b547c;stroke-width:4;stroke-linecap:round;stroke-linejoin:round;stroke-opacity:1\"\n           \n           class=\"st9\"\n           d=\"m 76.5,198.7 c 31.1,6.8 43.1,-6.5 55.2,-6.5 12.1,0 24.1,13.3 55.2,6.5\"\n           id=\"path3302\" />\n        <path\n           style=\"fill:none;stroke:#3b547c;stroke-width:4;stroke-linecap:round;stroke-linejoin:round;stroke-opacity:1\"\n           \n           class=\"st9\"\n           d=\"m 131.7,220.2 c 10.3,0 20.4,-1.9 29.9,-5.7 10.3,-4.1 19.7,-10.2 27.6,-18.1 7.9,-7.9 14,-17.2 18.1,-27.6 3.8,-9.5 5.7,-19.7 5.7,-29.9 0,-10.3 -1.9,-20.4 -5.7,-29.9 -4.1,-10.3 -10.2,-19.7 -18.1,-27.6 -7.9,-7.9 -17.2,-14 -27.6,-18.1 -9.5,-3.8 -19.7,-5.7 -29.9,-5.7 -10.3,0 -20.4,1.9 -29.9,5.7 -10.3,4.1 -19.7,10.2 -27.6,18.1 -7.9,7.9 -14,17.2 -18.1,27.6 -3.8,9.5 -5.7,19.7 -5.7,29.9 0,10.3 1.9,20.4 5.7,29.9 4.1,10.3 10.2,19.7 18.1,27.6 7.9,7.9 17.2,14 27.6,18.1 9.5,3.8 19.6,5.7 29.9,5.7 z\"\n           id=\"path3304\" />\n      </g>\n    </g>\n  </g>\n</svg>\n");

/***/ }),

/***/ "./style/index.css":
/*!*************************!*\
  !*** ./style/index.css ***!
  \*************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js */ "./node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js");
/* harmony import */ var _node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_cjs_js_index_css__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! !!../node_modules/css-loader/dist/cjs.js!./index.css */ "./node_modules/css-loader/dist/cjs.js!./style/index.css");

            

var options = {};

options.insert = "head";
options.singleton = false;

var update = _node_modules_style_loader_dist_runtime_injectStylesIntoStyleTag_js__WEBPACK_IMPORTED_MODULE_0___default()(_node_modules_css_loader_dist_cjs_js_index_css__WEBPACK_IMPORTED_MODULE_1__["default"], options);



/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (_node_modules_css_loader_dist_cjs_js_index_css__WEBPACK_IMPORTED_MODULE_1__["default"].locals || {});

/***/ })

}]);
//# sourceMappingURL=lib_index_js.32d90142c765cb12cad4.js.map