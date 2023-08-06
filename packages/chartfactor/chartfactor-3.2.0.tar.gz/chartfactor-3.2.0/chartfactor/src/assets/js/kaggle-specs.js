window.KaggleConfigurations = function () {
    try {
        /**
         * Lodash uniqBy alternative
         * @param {*} arr
         * @param {*} predicate
         * @returns
         */
        const uniqBy = (arr, predicate) => {
            const cb =
                typeof predicate === "function" ? predicate : (o) => o[predicate];

            return [
                ...arr
                    .reduce((map, item) => {
                        const key = item === null || item === undefined ? item : cb(item);

                        map.has(key) || map.set(key, item);

                        return map;
                    }, new Map())
                    .values(),
            ];
        };

        /**
         * Lodash get alternative
         * @param {*} obj
         * @param {*} path
         * @param {*} def
         * @returns
         */
        function get(obj, path, def) {
            var fullPath = path
                .replace(/\[/g, ".")
                .replace(/]/g, "")
                .split(".")
                .filter(Boolean);

            return fullPath.every(everyFunc) ? obj : def;

            function everyFunc(step) {
                return !(step && (obj = obj[step]) === undefined);
            }
        }

        /**
         * Lodash isEmpty alternative
         * @param {*} obj 
         * @returns 
         */
        function isEmpty(obj) {
            return Object.keys(obj).length === 0;
        }

        /**
         * Get the current kernel
         * @returns kernel instance
         */
        function getKernel() {
            let kernel;

            if (
                typeof jupyterlab !== "undefined" &&
                jupyterlab.shell.currentWidget?.context?.sessionContext.session?.kernel
            ) {
                kernel =
                    jupyterlab.shell.currentWidget?.context?.sessionContext.session
                        ?.kernel;
            }

            return kernel;
        }

        /**
         * Get the current context
         * @returns kernel instance
         */
        function getContext() {
            let contex;

            if (
                typeof jupyterlab !== "undefined" &&
                jupyterlab.shell.currentWidget?.context
            ) {
                contex = jupyterlab.shell.currentWidget?.context;
            }

            return contex;
        }

        /**
         * Suscribe current kernel activeCellChanged evt to a custom
         * onActiveCellChanged event listener
         */
        function suscribeToOnActiveCellChange() {
            const kernel = getKernel();

            const onActiveCellChanged = (event) => {
                if (event.activeCell) {
                    if (kernel) {
                        kernel.requestExecute({
                            code: `cfpy_active_cell_id = '${event.activeCell.model.id}'`,
                            silent: true,
                        });
                    }
                }
            };

            if (kernel) {
                jupyterlab.shell.currentWidget.content.activeCellChanged.disconnect(
                    onActiveCellChanged,
                    this
                );
                jupyterlab.shell.currentWidget.content.activeCellChanged.connect(
                    onActiveCellChanged,
                    this
                );
            }
        }

        function getLocalStorageItem(key) {
            let item = localStorage.getItem(key);

            if (item !== null) {
                try {
                    item = JSON.parse(item);
                } catch (e) { }
            }

            return item;
        } 

        const getProvidersFromApp = (app) => {
            const providers = getLocalStorageItem("cfs.dataProviders");
            const usedDataProvidersNames = uniqBy(
                app.widgetList
                    .map((w) => get(w, "source.provider.name", null))
                    .filter((pname) => pname)
            );
            const usedDataProviders = providers.filter((v) => {
                if (usedDataProvidersNames.includes(v.name)) {
                    if (v.customCode) delete v.customCode;
                    if (v.metadata) delete v.metadata;
                    return true;
                }
                return false;
            });

            return usedDataProviders;
        };

        /**
         * Custom function to save the the app in the cell metadata
         * @returns 
         */
        function toJSONWithDasboards() {
            var _a;
            const cells = [];
            for (
                let i = 0;
                i <
                (((_a = this.cells) === null || _a === void 0 ? void 0 : _a.length) ||
                    0);
                i++
            ) {
                const cell = this.cells.get(i).toJSON();
                cell.id = this.cells.get(i).id;

                if (cell.cell_type === "code") {
                    const app = getLocalStorageItem(`cfs.app-${cell.id}`);

                    if (app && !window.syncWithStudio) {
                        app.id = cell.id;
                        const appProviders = getProvidersFromApp(app);

                        cell.metadata.cf_studio_app = {};
                        cell.metadata.cf_studio_providers = [];

                        cell.metadata.cf_studio_app[`cfs.app-${cell.id}`] = app;
                        this.cells.get(i).metadata.set('cf_studio_app', {[`cfs.app-${cell.id}`]: app});

                        const providers = uniqBy(
                            [...appProviders],
                            "name"
                        );
                        cell.metadata.cf_studio_providers = providers;
                        this.cells.get(i).metadata.set('cf_studio_providers', providers);

                    } else if (cell.metadata.cf_studio_app && !isEmpty(cell.metadata.cf_studio_app)) {
                        // If the cell contains an studio app in the metadata
                        // and the id of that app is different to the cell id
                        // then we change the key of that cell by one with the current cell id
                        const currentKey = Object.keys(cell.metadata.cf_studio_app)[0];                        

                        if (!currentKey.includes(cell.id)) {
                            this.cells.get(i).metadata.delete('cf_studio_app');
                            this.cells.get(i).metadata.set('cf_studio_app', {[`cfs.app-${cell.id}`]: cell.metadata.cf_studio_app[currentKey]});
                            delete Object.assign(cell.metadata.cf_studio_app, {[`cfs.app-${cell.id}`]: cell.metadata.cf_studio_app[currentKey] })[currentKey];
                            cell.metadata.cf_studio_app[`cfs.app-${cell.id}`].id = cell.id;
                        }
                    }
                }

                cells.push(cell);
            }

            this._ensureMetadata();
            const metadata = Object.create(null);
            for (const key of this.metadata.keys()) {
                metadata[key] = JSON.parse(JSON.stringify(this.metadata.get(key)));
            }

            return {
                metadata,
                nbformat_minor: this._nbformatMinor,
                nbformat: this._nbformat,
                cells,
            };
        }

        /**
         * Suscribe current kernel saving action to
         * onSave event listener
         */
        function suscribeToOnSave() {
            const getCellIframe = (executionCount) => {
                const kernel = getKernel();
                const cellIframeId = `iframe${executionCount}_${kernel?.id}`;
                return document.getElementById(cellIframeId);
            };

            const getStudioAppForAllCells = () => {
                return new Promise((resolve, reject) => {
                    try {
                        const cells = [
                            ...jupyterlab.shell.currentWidget.model.cells._cellMap._map.values(),
                        ];

                        for (const cell of cells) {
                            if (cell.type === "code") {
                                const cellIFrame = getCellIframe(cell.executionCount);

                                if (cellIFrame) {
                                    cellIFrame.contentWindow.postMessage(
                                        {
                                            action: "getStudioApp",
                                            appId: `cfs.app-${cell.id}`,
                                        },
                                        "*"
                                    );
                                }
                            }
                        }

                        resolve(true);
                    } catch (error) {
                        reject(error);
                    }
                });
            };

            const onSave = async (context, state) => {
                const current = jupyterlab.shell.currentWidget;
                if (current) {
                    switch (state) {
                        case "started":
                            if (window.syncWithStudio) {
                                await getStudioAppForAllCells();
                                window.syncWithStudio = false;
                            }

                            current.model.toJSON = toJSONWithDasboards;
                            break;
                        case "completed":
                            window.syncWithStudio = true;
                            break;
                        default:
                            break;
                    }
                }
            };

            if (
                typeof jupyterlab !== "undefined" &&
                jupyterlab.shell.currentWidget?.context
            ) {
                jupyterlab.shell.currentWidget.context.saveState.disconnect(
                    onSave,
                    this
                );
                jupyterlab.shell.currentWidget.context.saveState.connect(onSave, this);
            }
        }

        /**
         * Saves an app into localStorage
         * @param {*} key
         * @param {*} item
         */
        function saveAppToLocalStorage(key, item) {
            if (typeof key !== "string") key = key.toString();
            if (typeof item !== "string") item = JSON.stringify(item);

            localStorage.setItem(key, item);
        }

        /**
         * Receive the CFS information sent from CharFactor Studio
         * and saves it to local Kaggle storage
         * @param {} event
         */
        async function cfsSynchronizeMessageEventListener(event) {
            if (event.data.action === "getStudioApp" && event.data.studioAppId) {
                if (typeof jupyterlab !== "undefined") {
                    saveAppToLocalStorage(event.data.studioAppId, event.data.studioApp);
                    saveAppToLocalStorage(
                        "cfs.dataProviders",
                        event.data.studioAppProviders
                    );

                    window.syncWithStudio = false;
                    await jupyterlab.commands.execute("docmanager:save");
                }
            }
        }

        /**
         * Suscribe to cfsSynchronizeMessageEventListener
         */
        function suscribeToSynchronizeMessage() {
            try {
                window.removeEventListener(
                    "message",
                    window.cfsSynchronizeMessageEventListener,
                    false
                );
            } catch (e) { }
            window.addEventListener(
                "message",
                (window.cfsSynchronizeMessageEventListener =
                    cfsSynchronizeMessageEventListener),
                false
            );
        }

        function createTempIframe(url = 'https://chartfactor.com/studio/jupyter.html', cell, callback) {
            let iframe = document.getElementById(cell.id);

            if (!iframe) {
                iframe = document.createElement('iframe');
                try {
                    iframe.id = cell.id;
                    iframe.name = cell.id;
                    iframe.src = `${url}jupyter.html`;
                    iframe.style.display = 'none';
                    iframe.addEventListener("load", function () {
                        callback(cell, this);
                    });
                    document.body.appendChild(iframe);
                } catch (err) {
                    console.error('Oops, unable to create the Iframe element.', err);
                }
            } else {
                callback(cell, iframe);
            }
        };

        function getIframeUrl(cell) {
            let iframeUrl;
            const source = cell.source.split('\n');
            source.forEach(s => {
                // Searching for a format like ".studio('My app', url='http://localhost:3333')" or 
                // ".studio('My app', 'http://localhost:3333')"
                if (s.includes('cf.studio')) {
                    const match = s.match(`studio\\((\\s?)+(app=)?[\\'\\"](.*)[\\'\\"]\\,(\\s?)+(url=)?[\\'\\"](.*?)[\\'\\"]\\)`);
                    if (match) {
                        iframeUrl = match[6];
                        if (iframeUrl && iframeUrl.startsWith('http')) {
                            iframeUrl = iframeUrl.trim();
                            // Adding trailing slash if missing
                            iframeUrl = iframeUrl.replace(/\/?$/, '/');
                        }
                    } else {
                        iframeUrl = 'https://chartfactor.com/studio/';
                    }
                }
            });

            return iframeUrl;
        }

        /**
         * Suscribe to kernel connectionStatusChanged evt
         * to remove apps from localStorage.
         */
        function suscribeToConnectionStatusChanged() {            
            const context = getContext();

            if (context.sessionContext) {
                context.model.toJSON = toJSONWithDasboards;

                /**
                 * Remove the app from kaggle and studio local storages
                 * @param {*} cell
                 */
                const removeFromLocalStorage = (cell) => {
                    localStorage.removeItem(`cfs.app-${cell.id}`);

                    const sendRemoveMessage = (cell, cellIFrame) => {
                        cellIFrame.contentWindow.postMessage(
                            {
                                action: "removeStudioApp",
                                storageKey: `cfs.app-${cell.id}`,
                            },
                            "*"
                        );
                        setTimeout(() => {
                            try {
                                document.body.removeChild(cellIFrame);    
                            } catch (error) {
                                cellIFrame.remove();
                            }                            
                        }, 1000);
                    };
                    createTempIframe(getIframeUrl(cell), cell, sendRemoveMessage);
                };

                const connectionStatusChanged = (sender, status) => {
                    if (status === "disconnected") {
                        let notebookConfig = context.model.toJSON(context.model);

                        for (const cell of notebookConfig.cells) {
                            if (cell.cell_type === "code" && cell.metadata.cf_studio_app) {
                                try {
                                    removeFromLocalStorage(cell);
                                } catch (error) {
                                    removeFromLocalStorage(cell);
                                }
                            }
                        }
                    }
                }

                context.sessionContext.connectionStatusChanged.connect(connectionStatusChanged);
            }
        };

        /**
         * Performs the notebook sync to send apps to studio localStorage
         */
        function executeNotebookSynchronization() {
            if (typeof jupyterlab !== "undefined") {

                /**
                 * Sends the cell's app to studio local storage
                 * @param {*} notebookConfig 
                 */
                const synchronizeNotebook = () => {
                    const context = getContext();
                    const kernel = getKernel();

                    if (context) {
                        context.model.toJSON = toJSONWithDasboards;

                        context.ready.then(() => {
                            return context.sessionContext.ready;
                        }).then(() => {
                            /**
                             * Sends the cell app to studio localStorage
                             * @param {*} cell 
                             * @param {*} cellIFrame 
                             */
                            const sendPostMessageToStudio = (cell, cellIFrame) => {
                                // Synchronizing cell's app
                                if (cell.metadata.cf_studio_app) {
                                    const keys = Object.keys(cell.metadata.cf_studio_app);
                                    if (keys && keys.length > 0) {
                                        cell.metadata.cf_studio_app[keys[0]].creationDate = Date.now();
                                        cellIFrame.contentWindow.postMessage({
                                            action: 'saveStudioApp',
                                            storageKey: keys[0],
                                            storageItem: cell.metadata.cf_studio_app[keys[0]]
                                        }, '*');
                                    }
                                }

                                // Synchronizing cell's providers
                                if (cell.metadata.cf_studio_providers) {
                                    cellIFrame.contentWindow.postMessage({
                                        action: 'saveStudioApp',
                                        storageKey: 'cfs.dataProviders',
                                        storageItem: cell.metadata.cf_studio_providers
                                    }, '*');
                                }

                                setTimeout(() => {
                                    try {
                                        document.body.removeChild(cellIFrame);    
                                    } catch (error) {
                                        cellIFrame.remove();                                
                                    }                                    
                                }, 1000);
                            };

                            let notebookConfig = context.model.toJSON(context.model);
                            for (const cell of notebookConfig.cells) {
                                if (cell.cell_type === 'code' && cell.metadata.cf_studio_app) {
                                    createTempIframe(getIframeUrl(cell), cell, sendPostMessageToStudio);
                                    kernel.requestExecute({
                                        code: `cfpy_active_cell_id = '${cell.id}'`,
                                        silent: true,
                                    });
                                }
                            }
                        });
                    }
                };

                if (window.firstTimeSync) {
                    window.firstTimeSync = false;
                    synchronizeNotebook();
                }
            }
        }

        return {
            suscribeToOnActiveCellChange,
            suscribeToOnSave,
            suscribeToSynchronizeMessage,
            suscribeToConnectionStatusChanged,
            executeNotebookSynchronization
        };
    } catch (error) {
        console.error(err);
    }
};

(() => {
    if (!window.kaggleConfigInstance) {
        window.kaggleConfigInstance = window.KaggleConfigurations();
    }
})();

window.initKaggleConfigurations = function () {
    window.syncWithStudio = true;
    window.firstTimeSync = true;
    if (!window.kaggleConfigInstance) {
        window.kaggleConfigInstance = window.KaggleConfigurations();
    }

    window.kaggleConfigInstance.executeNotebookSynchronization();
    window.kaggleConfigInstance.suscribeToSynchronizeMessage();
    window.kaggleConfigInstance.suscribeToOnActiveCellChange();
    window.kaggleConfigInstance.suscribeToOnSave();
    window.kaggleConfigInstance.suscribeToConnectionStatusChanged();
};

(() => {
    window.initKaggleConfigurations();
})();
