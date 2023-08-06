(self["webpackChunkskillsnetwork_authoring_extension"] = self["webpackChunkskillsnetwork_authoring_extension"] || []).push([["lib_index_js"],{

/***/ "./lib/button/index.js":
/*!*****************************!*\
  !*** ./lib/button/index.js ***!
  \*****************************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.a(module, async (__webpack_handle_async_dependencies__, __webpack_async_result__) => { try {
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "ButtonExtension": () => (/* binding */ ButtonExtension),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/docmanager */ "webpack/sharing/consume/default/@jupyterlab/docmanager");
/* harmony import */ var _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @lumino/disposable */ "webpack/sharing/consume/default/@lumino/disposable");
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_lumino_disposable__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/mainmenu */ "webpack/sharing/consume/default/@jupyterlab/mainmenu");
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _tools__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../tools */ "./lib/tools.js");
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ../handler */ "./lib/handler.js");
/* harmony import */ var _config__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ../config */ "./lib/config.js");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_4__);
var __webpack_async_dependencies__ = __webpack_handle_async_dependencies__([_tools__WEBPACK_IMPORTED_MODULE_5__, _handler__WEBPACK_IMPORTED_MODULE_6__, _config__WEBPACK_IMPORTED_MODULE_7__]);
([_tools__WEBPACK_IMPORTED_MODULE_5__, _handler__WEBPACK_IMPORTED_MODULE_6__, _config__WEBPACK_IMPORTED_MODULE_7__] = __webpack_async_dependencies__.then ? (await __webpack_async_dependencies__)() : __webpack_async_dependencies__);









/**
 * The plugin registration information.
 */
const plugin = {
    activate,
    id: 'skillsnetwork-authoring-extension:plugin',
    autoStart: true,
    requires: [_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_4__.INotebookTracker, _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_0__.IDocumentManager, _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_3__.IMainMenu]
};
/**
 * A notebook widget extension that adds a button to the toolbar.
 */
class ButtonExtension {
    /**
     * Create a new extension for the notebook panel widget.
     *
     * @param panel Notebook panel
     * @param context Notebook context
     * @returns Disposable on the added button
     */
    createNew(panel, context) {
        const start = async () => {
            // Get the current file contents
            const file = await (0,_tools__WEBPACK_IMPORTED_MODULE_5__.getFileContents)(panel, context);
            // POST to Atlas the file contents/lab model
            (0,_handler__WEBPACK_IMPORTED_MODULE_6__.postLabModel)((0,_handler__WEBPACK_IMPORTED_MODULE_6__.axiosHandler)(_config__WEBPACK_IMPORTED_MODULE_7__.Globals.TOKEN), file);
        };
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ToolbarButton({
            className: 'publish-lab-button',
            label: 'Publish',
            onClick: start,
            tooltip: 'Publish Lab'
        });
        panel.toolbar.insertItem(10, 'publish', button);
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_2__.DisposableDelegate(() => {
            button.dispose();
        });
    }
}
/**
 * Activate the extension.
 *
 * @param app Main application object
 */
async function activate(app, mainMenu, docManager) {
    console.log("Activated skillsnetwork-authoring-extension button plugin!");
    // init the token, globals
    const token = await (0,_config__WEBPACK_IMPORTED_MODULE_7__.ATLAS_TOKEN)();
    // Add the Publish widget to the lab environment
    app.docRegistry.addWidgetExtension('Notebook', new ButtonExtension());
    console.log('Detected your environment as: ', _config__WEBPACK_IMPORTED_MODULE_7__.Globals.LAB_TOOL_TYPE, _config__WEBPACK_IMPORTED_MODULE_7__.Globals.AUTHOR_ENV);
    console.log('Using default kernel: ', _config__WEBPACK_IMPORTED_MODULE_7__.Globals.PY_KERNEL_NAME);
    // Only try to load up a notebook when author is using the browser tool (not in local)
    if (_config__WEBPACK_IMPORTED_MODULE_7__.Globals.AUTHOR_ENV === 'browser') {
        const parsedToken = (0,_tools__WEBPACK_IMPORTED_MODULE_5__.parseJwt)(token);
        const labFilename = (0,_tools__WEBPACK_IMPORTED_MODULE_5__.getLabFilePath)(parsedToken);
        // Attempt to open the lab
        let widget = await docManager.createNew(labFilename, 'notebook', { name: _config__WEBPACK_IMPORTED_MODULE_7__.Globals.PY_KERNEL_NAME });
        await (0,_tools__WEBPACK_IMPORTED_MODULE_5__.loadLabContents)(widget, (0,_handler__WEBPACK_IMPORTED_MODULE_6__.axiosHandler)(token), _config__WEBPACK_IMPORTED_MODULE_7__.Globals.AUTHOR_ENV);
        widget.context.ready.then(() => {
            docManager.openOrReveal(labFilename, 'default', { name: _config__WEBPACK_IMPORTED_MODULE_7__.Globals.PY_KERNEL_NAME });
        });
    }
}
/**
 * Export the plugin as default.
 */
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);

__webpack_async_result__();
} catch(e) { __webpack_async_result__(e); } });

/***/ }),

/***/ "./lib/config.js":
/*!***********************!*\
  !*** ./lib/config.js ***!
  \***********************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.a(module, async (__webpack_handle_async_dependencies__, __webpack_async_result__) => { try {
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "ATLAS_BASE_URL": () => (/* binding */ ATLAS_BASE_URL),
/* harmony export */   "ATLAS_TOKEN": () => (/* binding */ ATLAS_TOKEN),
/* harmony export */   "CancelToken": () => (/* binding */ CancelToken),
/* harmony export */   "GET_PYKERNEL": () => (/* binding */ GET_PYKERNEL),
/* harmony export */   "Globals": () => (/* binding */ Globals),
/* harmony export */   "source": () => (/* binding */ source)
/* harmony export */ });
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! axios */ "webpack/sharing/consume/default/axios/axios");
/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(axios__WEBPACK_IMPORTED_MODULE_1__);
/* provided dependency */ var process = __webpack_require__(/*! process/browser */ "./node_modules/process/browser.js");



const getServerBaseUrl = (settings) => {
    let baseUrl = settings.baseUrl;
    // Add the trailing slash if it is missing.
    if (!baseUrl.endsWith('/')) {
        baseUrl += '/';
    }
    return baseUrl;
};
const ATLAS_BASE_URL = await (async () => {
    const currentUrl = window.location.href;
    const parameters = new URL(currentUrl).searchParams;
    const baseUrl = parameters.get('atlas_base_url');
    if (baseUrl === null) {
        const init = {
            method: 'GET',
        };
        const settings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_0__.ServerConnection.makeSettings();
        const requestUrl = getServerBaseUrl(settings) + 'skillsnetwork-authoring-extension/config';
        const response = await _jupyterlab_services__WEBPACK_IMPORTED_MODULE_0__.ServerConnection.makeRequest(requestUrl, init, settings);
        const configuration = (await response.json());
        return configuration.ATLAS_BASE_URL;
    }
    else {
        return baseUrl;
    }
})();
/**
 * Extracts the session token. Will first try to get a token via the URL, if none was found then try to get the token via cookie.
 *
 * @returns token
 */
const ATLAS_TOKEN = async () => {
    var _a;
    const currentURL = window.location.href;
    const params = new URL(currentURL).searchParams;
    let token = params.get('token');
    Globals.LAB_TOOL_TYPE = 'JUPYTER_LITE';
    if (token === null) {
        // Try getting it from cookie
        const COOKIE_NAME = (_a = process.env.ATLAS_TOKEN_COOKIE_NAME) !== null && _a !== void 0 ? _a : 'atlas_token';
        const reg = new RegExp(`(^| )${COOKIE_NAME}=([^;]+)`);
        let match = reg.exec(document.cookie);
        // If found then set that as our token o/w set it as empty str for now
        (match !== null) ? token = match[2] : token = 'NO_TOKEN';
        Globals.LAB_TOOL_TYPE = 'JUPYTER_LAB';
    }
    if (token === null || token === 'NO_TOKEN') {
        // If no token was found in the URL or cookies, the author is in their local env (hopefully...)
        Globals.AUTHOR_ENV = 'local';
    }
    else {
        Globals.AUTHOR_ENV = 'browser';
    }
    if (Globals.LAB_TOOL_TYPE === 'JUPYTER_LAB') {
        // In production, jupyterlab doesn't have python3 as a kernel option so use python
        Globals.PY_KERNEL_NAME = await GET_PYKERNEL();
        Globals.DEFAULT_LAB_NAME = 'lab.ipynb';
    }
    else if (Globals.LAB_TOOL_TYPE === 'JUPYTER_LITE') {
        Globals.PY_KERNEL_NAME = 'python';
        Globals.DEFAULT_LAB_NAME = 'lab.jupyterlite.ipynb';
    }
    Globals.TOKEN = token;
    return token;
};
/**
 * Gets the python kernel. If more than one python kernel is found, prioritize python3. If only one python kernel is found, select that kernel
 *
 * @returns pykernel
 */
const GET_PYKERNEL = async () => {
    // Get the available kernels
    let kspecs = await (await _jupyterlab_services__WEBPACK_IMPORTED_MODULE_0__.KernelSpecAPI.getSpecs()).kernelspecs;
    function checkPython(spec) {
        return spec.includes('python');
    }
    let keys = Object.keys(kspecs);
    // filter for only the spec names with python in it, sorted
    let filtered_keys = keys.filter(checkPython).sort();
    // return the priority python
    let pykernel = filtered_keys[filtered_keys.length - 1];
    return pykernel;
};
var CancelToken = (axios__WEBPACK_IMPORTED_MODULE_1___default().CancelToken);
var source = CancelToken.source();
// Global variables
class Globals {
}

__webpack_async_result__();
} catch(e) { __webpack_async_result__(e); } }, 1);

/***/ }),

/***/ "./lib/dialog.js":
/*!***********************!*\
  !*** ./lib/dialog.js ***!
  \***********************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.a(module, async (__webpack_handle_async_dependencies__, __webpack_async_result__) => { try {
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "SpinnerDialog": () => (/* binding */ SpinnerDialog),
/* harmony export */   "showFailureImportLabDialog": () => (/* binding */ showFailureImportLabDialog),
/* harmony export */   "showFailurePublishDialog": () => (/* binding */ showFailurePublishDialog),
/* harmony export */   "showSuccessPublishDialog": () => (/* binding */ showSuccessPublishDialog),
/* harmony export */   "show_spinner": () => (/* binding */ show_spinner)
/* harmony export */ });
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _config__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./config */ "./lib/config.js");
var __webpack_async_dependencies__ = __webpack_handle_async_dependencies__([_config__WEBPACK_IMPORTED_MODULE_2__]);
_config__WEBPACK_IMPORTED_MODULE_2__ = (__webpack_async_dependencies__.then ? (await __webpack_async_dependencies__)() : __webpack_async_dependencies__)[0];
/* eslint-disable @typescript-eslint/no-empty-function */



/**
 * A widget that holds the loading spinner
 */
class SpinnerDialog extends _lumino_widgets__WEBPACK_IMPORTED_MODULE_0__.Widget {
    constructor() {
        const body = document.createElement('div');
        const spinner = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Spinner();
        body.appendChild(spinner.node);
        body.style.padding = '15px';
        super({ node: body });
    }
}
/**
 * Shows the Loading dialog
 */
const show_spinner = (message) => {
    const spinWidget = new SpinnerDialog();
    (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.showDialog)({
        title: message,
        body: spinWidget,
        buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Dialog.cancelButton()]
    })
        .then(result => {
        if (!result.button.accept) {
            _config__WEBPACK_IMPORTED_MODULE_2__.source.cancel('Operation cancelled by the user.');
        }
    })
        .catch(error => { });
};
/**
 * Shows the Success dialog
 */
const showSuccessPublishDialog = () => {
    (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.showDialog)({
        title: 'Success!',
        body: 'This lab was successfully submitted for publishing!',
        buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Dialog.okButton()]
    })
        .then(result => { })
        .catch(error => { });
};
/**
 * Shows the Failed to publish dialog
 */
const showFailurePublishDialog = () => {
    (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.showDialog)({
        title: 'Failed to Publish',
        body: 'This lab failed to publish.',
        buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Dialog.okButton()]
    })
        .then(result => { })
        .catch(error => { });
};
/**
 * Shows the Failed to load lab dialog
 */
const showFailureImportLabDialog = () => {
    (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.showDialog)({
        title: 'Failed to Load Lab',
        body: 'This lab failed to load.',
        buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Dialog.okButton()]
    })
        .then(result => { })
        .catch(error => { });
};

__webpack_async_result__();
} catch(e) { __webpack_async_result__(e); } });

/***/ }),

/***/ "./lib/handler.js":
/*!************************!*\
  !*** ./lib/handler.js ***!
  \************************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.a(module, async (__webpack_handle_async_dependencies__, __webpack_async_result__) => { try {
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "axiosHandler": () => (/* binding */ axiosHandler),
/* harmony export */   "getLabModel": () => (/* binding */ getLabModel),
/* harmony export */   "postLabModel": () => (/* binding */ postLabModel)
/* harmony export */ });
/* harmony import */ var _dialog__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./dialog */ "./lib/dialog.js");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _config__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./config */ "./lib/config.js");
/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! axios */ "webpack/sharing/consume/default/axios/axios");
/* harmony import */ var axios__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(axios__WEBPACK_IMPORTED_MODULE_1__);
var __webpack_async_dependencies__ = __webpack_handle_async_dependencies__([_config__WEBPACK_IMPORTED_MODULE_2__, _dialog__WEBPACK_IMPORTED_MODULE_3__]);
([_config__WEBPACK_IMPORTED_MODULE_2__, _dialog__WEBPACK_IMPORTED_MODULE_3__] = __webpack_async_dependencies__.then ? (await __webpack_async_dependencies__)() : __webpack_async_dependencies__);






const axiosHandler = (lab_token) => {
    if (lab_token)
        _config__WEBPACK_IMPORTED_MODULE_2__.Globals.TOKEN = lab_token;
    const atlasClient = axios__WEBPACK_IMPORTED_MODULE_1___default().create({
        baseURL: _config__WEBPACK_IMPORTED_MODULE_2__.ATLAS_BASE_URL,
        headers: {
            Authorization: `Bearer ${lab_token}`,
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    });
    return atlasClient;
};
/**
 * GET the lab model / JSON that represents a .ipynb file/notebook from ATLAS
 *
 * @param axiosHandler Axios client that contains a JWT Bearer token
 * @returns Promise<void>
 */
const getLabModel = (axiosHandler) => {
    // GET the lab model
    return axiosHandler
        .get('v1/labs')
        .then(result => {
        _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.flush(); //remove spinner
        return JSON.parse(result.data.body);
    })
        .catch(error => {
        _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.flush(); //remove spinner
        (0,_dialog__WEBPACK_IMPORTED_MODULE_3__.showFailureImportLabDialog)();
        console.log(error);
        return 0;
    });
};
/**
 * POST the lab model / JSON from the .ipynb file/notebook to ATLAS
 *
 * @param axiosHandler Axios client that contains a JWT Bearer token
 * @returns Promise<void>
 */
const postLabModel = async (axiosHandler, labModel) => {
    (0,_dialog__WEBPACK_IMPORTED_MODULE_3__.show_spinner)('Publishing...');
    return new Promise(async (resolve, reject) => {
        await axiosHandler
            .post('v1/labs', {
            body: labModel
        }, {
            cancelToken: _config__WEBPACK_IMPORTED_MODULE_2__.source.token,
        })
            .then(res => {
            console.log('SUCCESSFULLY PUSHED', res);
            _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.flush(); //remove spinner
            (0,_dialog__WEBPACK_IMPORTED_MODULE_3__.showSuccessPublishDialog)();
            resolve;
        })
            .catch((error) => {
            console.log(error);
            _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Dialog.flush(); // remove spinner
            (0,_dialog__WEBPACK_IMPORTED_MODULE_3__.showFailurePublishDialog)();
            reject;
        });
    });
};

__webpack_async_result__();
} catch(e) { __webpack_async_result__(e); } });

/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.a(module, async (__webpack_handle_async_dependencies__, __webpack_async_result__) => { try {
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _menu__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ./menu */ "./lib/menu/index.js");
/* harmony import */ var _button__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ./button */ "./lib/button/index.js");
var __webpack_async_dependencies__ = __webpack_handle_async_dependencies__([_button__WEBPACK_IMPORTED_MODULE_0__, _menu__WEBPACK_IMPORTED_MODULE_1__]);
([_button__WEBPACK_IMPORTED_MODULE_0__, _menu__WEBPACK_IMPORTED_MODULE_1__] = __webpack_async_dependencies__.then ? (await __webpack_async_dependencies__)() : __webpack_async_dependencies__);


const main = [
    _button__WEBPACK_IMPORTED_MODULE_0__["default"],
    _menu__WEBPACK_IMPORTED_MODULE_1__.menu
];
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (main);

__webpack_async_result__();
} catch(e) { __webpack_async_result__(e); } });

/***/ }),

/***/ "./lib/menu/index.js":
/*!***************************!*\
  !*** ./lib/menu/index.js ***!
  \***************************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.a(module, async (__webpack_handle_async_dependencies__, __webpack_async_result__) => { try {
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "menu": () => (/* binding */ menu)
/* harmony export */ });
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/mainmenu */ "webpack/sharing/consume/default/@jupyterlab/mainmenu");
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @jupyterlab/docmanager */ "webpack/sharing/consume/default/@jupyterlab/docmanager");
/* harmony import */ var _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _dialog__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ../dialog */ "./lib/dialog.js");
/* harmony import */ var _tools__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ../tools */ "./lib/tools.js");
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! ../handler */ "./lib/handler.js");
/* harmony import */ var _config__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! ../config */ "./lib/config.js");
var __webpack_async_dependencies__ = __webpack_handle_async_dependencies__([_dialog__WEBPACK_IMPORTED_MODULE_5__, _tools__WEBPACK_IMPORTED_MODULE_6__, _config__WEBPACK_IMPORTED_MODULE_7__, _handler__WEBPACK_IMPORTED_MODULE_8__]);
([_dialog__WEBPACK_IMPORTED_MODULE_5__, _tools__WEBPACK_IMPORTED_MODULE_6__, _config__WEBPACK_IMPORTED_MODULE_7__, _handler__WEBPACK_IMPORTED_MODULE_8__] = __webpack_async_dependencies__.then ? (await __webpack_async_dependencies__)() : __webpack_async_dependencies__);









const menu = {
    id: 'skillsnetwork-authoring-extension:menu',
    autoStart: true,
    requires: [_jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_0__.IMainMenu, _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_3__.INotebookTracker, _jupyterlab_docmanager__WEBPACK_IMPORTED_MODULE_4__.IDocumentManager],
    activate: (app, mainMenu, notebookTracker, docManager) => {
        console.log('Activated skillsnetwork-authoring-extension menu plugin!');
        const editLabFromToken = 'edit-lab-from-token';
        app.commands.addCommand(editLabFromToken, {
            label: 'Edit a Lab',
            execute: () => {
                showTokenDialog(notebookTracker, docManager);
            }
        });
        const { commands } = app;
        // Create a new menu
        const menu = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_1__.Menu({ commands });
        menu.title.label = 'Skills Network';
        mainMenu.addMenu(menu, { rank: 80 });
        // Add command to menu
        menu.addItem({
            command: editLabFromToken,
            args: {}
        });
        const showTokenDialog = (notebookTracker, docManager) => {
            // Generate Dialog body
            let bodyDialog = document.createElement('div');
            let nameLabel = document.createElement('label');
            nameLabel.textContent = "Enter your authorization token: ";
            let tokenInput = document.createElement('input');
            tokenInput.className = "jp-mod-styled";
            bodyDialog.appendChild(nameLabel);
            bodyDialog.appendChild(tokenInput);
            (0,_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__.showDialog)({
                title: "Edit a Lab",
                body: new _lumino_widgets__WEBPACK_IMPORTED_MODULE_1__.Widget({ node: bodyDialog }),
                buttons: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__.Dialog.cancelButton(), _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_2__.Dialog.okButton()]
            }).then(async (result) => {
                if (result.button.accept) {
                    (0,_dialog__WEBPACK_IMPORTED_MODULE_5__.show_spinner)('Loading up your lab...');
                    const token = tokenInput.value;
                    const parsedToken = (0,_tools__WEBPACK_IMPORTED_MODULE_6__.parseJwt)(token);
                    const labFilename = (0,_tools__WEBPACK_IMPORTED_MODULE_6__.getLabFilePath)(parsedToken);
                    const nbPanel = docManager.createNew(labFilename, 'notebook', { name: _config__WEBPACK_IMPORTED_MODULE_7__.Globals.PY_KERNEL_NAME });
                    if (nbPanel === undefined) {
                        throw Error('Error loading lab');
                    }
                    nbPanel.show();
                    await (0,_tools__WEBPACK_IMPORTED_MODULE_6__.loadLabContents)(nbPanel, (0,_handler__WEBPACK_IMPORTED_MODULE_8__.axiosHandler)(tokenInput.value));
                }
            })
                .catch();
        };
    }
};

__webpack_async_result__();
} catch(e) { __webpack_async_result__(e); } });

/***/ }),

/***/ "./lib/tools.js":
/*!**********************!*\
  !*** ./lib/tools.js ***!
  \**********************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.a(module, async (__webpack_handle_async_dependencies__, __webpack_async_result__) => { try {
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "DEFAULT_CONTENT": () => (/* binding */ DEFAULT_CONTENT),
/* harmony export */   "getCellContents": () => (/* binding */ getCellContents),
/* harmony export */   "getFileContents": () => (/* binding */ getFileContents),
/* harmony export */   "getLabFilePath": () => (/* binding */ getLabFilePath),
/* harmony export */   "loadLabContents": () => (/* binding */ loadLabContents),
/* harmony export */   "parseJwt": () => (/* binding */ parseJwt)
/* harmony export */ });
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/notebook */ "webpack/sharing/consume/default/@jupyterlab/notebook");
/* harmony import */ var _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");
/* harmony import */ var buffer__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! buffer */ "webpack/sharing/consume/default/buffer/buffer");
/* harmony import */ var buffer__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(buffer__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _config__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./config */ "./lib/config.js");
var __webpack_async_dependencies__ = __webpack_handle_async_dependencies__([_handler__WEBPACK_IMPORTED_MODULE_2__, _config__WEBPACK_IMPORTED_MODULE_3__]);
([_handler__WEBPACK_IMPORTED_MODULE_2__, _config__WEBPACK_IMPORTED_MODULE_3__] = __webpack_async_dependencies__.then ? (await __webpack_async_dependencies__)() : __webpack_async_dependencies__);




/**
 * Extracts the relevant data from the cells of the notebook
 *
 * @param cell Cell model
 * @returns ICellData object
 */
const getCellContents = (cell) => {
    const cellData = {
        cell_type: cell.model.type,
        id: cell.model.id,
        metadata: {},
        outputs: [],
        source: [cell.model.value.text]
    };
    return cellData;
};
/**
 * Gets the raw data (cell models and content, notebook configurations) from the .ipynb file
 *
 * @param panel Notebook panel
 * @param context Notebook context
 */
const getFileContents = (panel, context) => {
    // Cell types: "code" | "markdown" | "raw"
    const allCells = [];
    panel.content.widgets.forEach((cell) => {
        const cellData = getCellContents(cell);
        allCells.push(cellData);
    });
    // Get the configs from the notebook model
    const config_meta = context.model.metadata.toJSON();
    const config_nbmajor = context.model.nbformat;
    const config_nbminor = context.model.nbformatMinor;
    // Put all data into IPynbRaw object
    const rawFile = {
        cells: allCells,
        metadata: config_meta,
        nbformat: config_nbmajor,
        nbformat_minor: config_nbminor
    };
    return JSON.stringify(rawFile, null, 2);
};
const loadLabContents = async (widget, axiosHandlers, author_env) => {
    const model = new _jupyterlab_notebook__WEBPACK_IMPORTED_MODULE_0__.NotebookModel();
    // Only try to load the initial lab notebook if the author is not coming from their local env
    if (author_env !== 'local') {
        try {
            const lab_model = (await (0,_handler__WEBPACK_IMPORTED_MODULE_2__.getLabModel)(axiosHandlers));
            model.fromJSON(lab_model);
        }
        catch (_a) {
            throw 'Error getting lab model';
        }
        // testing purposes
        //model.fromJSON(DEFAULT_CONTENT);
    }
    // testing purposes:
    // model.fromJSON(DEFAULT_CONTENT);
    widget.content.model = model;
};
const parseJwt = (token) => {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    // const decoded = atob(base64);
    const decoded = buffer__WEBPACK_IMPORTED_MODULE_1__.Buffer.from(base64, 'base64').toString();
    const jsonPayload = decodeURIComponent(decoded.split('').map(function (c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload);
};
const getLabFilePath = (jwtparsed) => {
    var _a;
    let labFilename = (_a = jwtparsed.lab_filepath) !== null && _a !== void 0 ? _a : _config__WEBPACK_IMPORTED_MODULE_3__.Globals.DEFAULT_LAB_NAME;
    // Replace labs/ prefix with empty string
    // TODO: We need a more robust way to do this and not rely on the assumption that the lab is in the labs folder
    // TODO: This is required as the createNew method will not automatically create the parent directories
    labFilename = labFilename.replace('labs/', '');
    return labFilename;
};
// eslint-disable-next-line @typescript-eslint/quotes
const DEFAULT_CONTENT = {
    cells: [
        {
            cell_type: 'code',
            id: 'c852569f-bf26-4994-88e7-3b94874d3853',
            metadata: {},
            source: ['print("hello world again")']
        },
        {
            cell_type: 'markdown',
            id: '5a2dc856-763a-4f12-b675-481ed971178a',
            metadata: {},
            source: ['this is markdown']
        },
        {
            cell_type: 'raw',
            id: '492a02e8-ec75-49f7-8560-b30256bca6af',
            metadata: {},
            source: ['this is raw']
        }
    ],
    metadata: {
        kernelspec: {
            display_name: 'Python 3 (ipykernel)',
            language: 'python',
            name: 'python3'
        },
        language_info: {
            codemirror_mode: { name: 'ipython', version: 3 },
            file_extension: '.py',
            mimetype: 'text/x-python',
            name: 'python',
            nbconvert_exporter: 'python',
            pygments_lexer: 'ipython3',
            version: '3.10.4'
        }
    },
    nbformat: 4,
    nbformat_minor: 5
};

__webpack_async_result__();
} catch(e) { __webpack_async_result__(e); } });

/***/ }),

/***/ "./node_modules/process/browser.js":
/*!*****************************************!*\
  !*** ./node_modules/process/browser.js ***!
  \*****************************************/
/***/ ((module) => {

// shim for using process in browser
var process = module.exports = {};

// cached from whatever global is present so that test runners that stub it
// don't break things.  But we need to wrap it in a try catch in case it is
// wrapped in strict mode code which doesn't define any globals.  It's inside a
// function because try/catches deoptimize in certain engines.

var cachedSetTimeout;
var cachedClearTimeout;

function defaultSetTimout() {
    throw new Error('setTimeout has not been defined');
}
function defaultClearTimeout () {
    throw new Error('clearTimeout has not been defined');
}
(function () {
    try {
        if (typeof setTimeout === 'function') {
            cachedSetTimeout = setTimeout;
        } else {
            cachedSetTimeout = defaultSetTimout;
        }
    } catch (e) {
        cachedSetTimeout = defaultSetTimout;
    }
    try {
        if (typeof clearTimeout === 'function') {
            cachedClearTimeout = clearTimeout;
        } else {
            cachedClearTimeout = defaultClearTimeout;
        }
    } catch (e) {
        cachedClearTimeout = defaultClearTimeout;
    }
} ())
function runTimeout(fun) {
    if (cachedSetTimeout === setTimeout) {
        //normal enviroments in sane situations
        return setTimeout(fun, 0);
    }
    // if setTimeout wasn't available but was latter defined
    if ((cachedSetTimeout === defaultSetTimout || !cachedSetTimeout) && setTimeout) {
        cachedSetTimeout = setTimeout;
        return setTimeout(fun, 0);
    }
    try {
        // when when somebody has screwed with setTimeout but no I.E. maddness
        return cachedSetTimeout(fun, 0);
    } catch(e){
        try {
            // When we are in I.E. but the script has been evaled so I.E. doesn't trust the global object when called normally
            return cachedSetTimeout.call(null, fun, 0);
        } catch(e){
            // same as above but when it's a version of I.E. that must have the global object for 'this', hopfully our context correct otherwise it will throw a global error
            return cachedSetTimeout.call(this, fun, 0);
        }
    }


}
function runClearTimeout(marker) {
    if (cachedClearTimeout === clearTimeout) {
        //normal enviroments in sane situations
        return clearTimeout(marker);
    }
    // if clearTimeout wasn't available but was latter defined
    if ((cachedClearTimeout === defaultClearTimeout || !cachedClearTimeout) && clearTimeout) {
        cachedClearTimeout = clearTimeout;
        return clearTimeout(marker);
    }
    try {
        // when when somebody has screwed with setTimeout but no I.E. maddness
        return cachedClearTimeout(marker);
    } catch (e){
        try {
            // When we are in I.E. but the script has been evaled so I.E. doesn't  trust the global object when called normally
            return cachedClearTimeout.call(null, marker);
        } catch (e){
            // same as above but when it's a version of I.E. that must have the global object for 'this', hopfully our context correct otherwise it will throw a global error.
            // Some versions of I.E. have different rules for clearTimeout vs setTimeout
            return cachedClearTimeout.call(this, marker);
        }
    }



}
var queue = [];
var draining = false;
var currentQueue;
var queueIndex = -1;

function cleanUpNextTick() {
    if (!draining || !currentQueue) {
        return;
    }
    draining = false;
    if (currentQueue.length) {
        queue = currentQueue.concat(queue);
    } else {
        queueIndex = -1;
    }
    if (queue.length) {
        drainQueue();
    }
}

function drainQueue() {
    if (draining) {
        return;
    }
    var timeout = runTimeout(cleanUpNextTick);
    draining = true;

    var len = queue.length;
    while(len) {
        currentQueue = queue;
        queue = [];
        while (++queueIndex < len) {
            if (currentQueue) {
                currentQueue[queueIndex].run();
            }
        }
        queueIndex = -1;
        len = queue.length;
    }
    currentQueue = null;
    draining = false;
    runClearTimeout(timeout);
}

process.nextTick = function (fun) {
    var args = new Array(arguments.length - 1);
    if (arguments.length > 1) {
        for (var i = 1; i < arguments.length; i++) {
            args[i - 1] = arguments[i];
        }
    }
    queue.push(new Item(fun, args));
    if (queue.length === 1 && !draining) {
        runTimeout(drainQueue);
    }
};

// v8 likes predictible objects
function Item(fun, array) {
    this.fun = fun;
    this.array = array;
}
Item.prototype.run = function () {
    this.fun.apply(null, this.array);
};
process.title = 'browser';
process.browser = true;
process.env = {};
process.argv = [];
process.version = ''; // empty string to avoid regexp issues
process.versions = {};

function noop() {}

process.on = noop;
process.addListener = noop;
process.once = noop;
process.off = noop;
process.removeListener = noop;
process.removeAllListeners = noop;
process.emit = noop;
process.prependListener = noop;
process.prependOnceListener = noop;

process.listeners = function (name) { return [] }

process.binding = function (name) {
    throw new Error('process.binding is not supported');
};

process.cwd = function () { return '/' };
process.chdir = function (dir) {
    throw new Error('process.chdir is not supported');
};
process.umask = function() { return 0; };


/***/ })

}]);
//# sourceMappingURL=lib_index_js.a798fa641347fb427e7a.js.map