/* eslint-disable prettier/prettier */
/* eslint-disable @typescript-eslint/explicit-module-boundary-types */
/* eslint-disable @typescript-eslint/ban-types */
import { DocumentRegistry } from '@jupyterlab/docregistry';
import { IDocumentManager } from '@jupyterlab/docmanager';
import { ToolbarButton } from '@jupyterlab/apputils';
import { IDisposable, DisposableDelegate } from '@lumino/disposable';
import { IMainMenu } from '@jupyterlab/mainmenu';
import { getFileContents, getLabFilePath, loadLabContents, parseJwt } from '../tools';
import { axiosHandler, postLabModel } from '../handler';
import { Globals } from '../config';
import { ATLAS_TOKEN } from '../config';

import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import {
  NotebookPanel,
  INotebookModel,
  INotebookTracker
} from '@jupyterlab/notebook';

/**
 * The plugin registration information.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  activate,
  id: 'skillsnetwork-authoring-extension:plugin',
  autoStart: true,
  requires: [INotebookTracker, IDocumentManager, IMainMenu]
};

/**
 * A notebook widget extension that adds a button to the toolbar.
 */
export class ButtonExtension
  implements DocumentRegistry.IWidgetExtension<NotebookPanel, INotebookModel>
{
  /**
   * Create a new extension for the notebook panel widget.
   *
   * @param panel Notebook panel
   * @param context Notebook context
   * @returns Disposable on the added button
   */
  createNew(
    panel: NotebookPanel,
    context: DocumentRegistry.IContext<INotebookModel>
  ): IDisposable {
    const start = async () => {
      // Get the current file contents
      const file = await getFileContents(panel, context);
      // POST to Atlas the file contents/lab model
      postLabModel(axiosHandler(Globals.TOKEN), file);
    };

    const button = new ToolbarButton({
      className: 'publish-lab-button',
      label: 'Publish',
      onClick: start,
      tooltip: 'Publish Lab'
    });

    panel.toolbar.insertItem(10, 'publish', button);
    return new DisposableDelegate(() => {
      button.dispose();
    });
  }
}

/**
 * Activate the extension.
 *
 * @param app Main application object
 */
async function activate(
  app: JupyterFrontEnd,
  mainMenu: IMainMenu,
  docManager: IDocumentManager
) {

  console.log("Activated skillsnetwork-authoring-extension button plugin!");

  // init the token, globals
  const token = await ATLAS_TOKEN();

  // Add the Publish widget to the lab environment
  app.docRegistry.addWidgetExtension('Notebook', new ButtonExtension());

  console.log('Detected your environment as: ', Globals.LAB_TOOL_TYPE, Globals.AUTHOR_ENV);
  console.log('Using default kernel: ', Globals.PY_KERNEL_NAME);

  // Only try to load up a notebook when author is using the browser tool (not in local)
  if (Globals.AUTHOR_ENV === 'browser'){
    const parsedToken = parseJwt(token)
    const labFilename = getLabFilePath(parsedToken);

    // Attempt to open the lab
    let widget = await docManager.createNew(labFilename, 'notebook', { name:  Globals.PY_KERNEL_NAME} ) as any;
    await loadLabContents(widget, axiosHandler(token), Globals.AUTHOR_ENV);
      widget.context.ready.then(() => {
        docManager.openOrReveal(labFilename, 'default', { name:  Globals.PY_KERNEL_NAME });
      });
  }
}

/**
 * Export the plugin as default.
 */
export default plugin;
