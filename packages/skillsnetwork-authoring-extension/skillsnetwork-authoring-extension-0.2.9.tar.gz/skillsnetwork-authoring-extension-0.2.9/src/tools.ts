/* eslint-disable @typescript-eslint/ban-types */
import { Cell, ICellModel } from '@jupyterlab/cells';
import {
  INotebookModel,
  NotebookPanel,
  NotebookModel
} from '@jupyterlab/notebook';
import { DocumentRegistry } from '@jupyterlab/docregistry';
import * as nbformat from '@jupyterlab/nbformat';
import { getLabModel } from './handler';
import { AxiosInstance } from 'axios';
import { Buffer } from 'buffer';
import { Globals } from './config';

export interface ICellData {
  cell_type: string;
  id: string;
  metadata: {};
  outputs: [];
  source: string[];
}
export interface IPynbRaw {
  cells: ICellData[];
  metadata: {};
  nbformat: number;
  nbformat_minor: number;
}

/**
 * Extracts the relevant data from the cells of the notebook
 *
 * @param cell Cell model
 * @returns ICellData object
 */
export const getCellContents = (cell: Cell<ICellModel>): ICellData => {
  const cellData: ICellData = {
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
export const getFileContents = (
  panel: NotebookPanel,
  context: DocumentRegistry.IContext<INotebookModel>
): string => {
  // Cell types: "code" | "markdown" | "raw"
  const allCells: any[] = [];
  panel.content.widgets.forEach((cell: Cell<ICellModel>) => {
    const cellData = getCellContents(cell);
    allCells.push(cellData);
  });

  // Get the configs from the notebook model
  const config_meta = context.model.metadata.toJSON();
  const config_nbmajor = context.model.nbformat;
  const config_nbminor = context.model.nbformatMinor;

  // Put all data into IPynbRaw object
  const rawFile: IPynbRaw = {
    cells: allCells,
    metadata: config_meta,
    nbformat: config_nbmajor,
    nbformat_minor: config_nbminor
  };
  return JSON.stringify(rawFile, null, 2);
};

export const loadLabContents = async (widget: NotebookPanel, axiosHandlers: AxiosInstance, author_env?: string): Promise<void> => {
  const model = new NotebookModel();
  // Only try to load the initial lab notebook if the author is not coming from their local env
  if (author_env !== 'local'){
    try {
      const lab_model = (await getLabModel(
        axiosHandlers
      )) as unknown as nbformat.INotebookContent;
      model.fromJSON(lab_model);
    } catch {
      throw 'Error getting lab model';
    }
    // testing purposes
    //model.fromJSON(DEFAULT_CONTENT);
  }
  // testing purposes:
  // model.fromJSON(DEFAULT_CONTENT);
  widget.content.model = model;
};

export const parseJwt = (token: string) => {
  const base64Url = token.split('.')[1];
  const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
  // const decoded = atob(base64);
  const decoded = Buffer.from(base64, 'base64').toString();
  const jsonPayload = decodeURIComponent(decoded.split('').map(function(c) {
      return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
  }).join(''));
  return JSON.parse(jsonPayload);
}

export const getLabFilePath = (jwtparsed: any): string => {
  let labFilename = jwtparsed.lab_filepath ?? Globals.DEFAULT_LAB_NAME;
  // Replace labs/ prefix with empty string
  // TODO: We need a more robust way to do this and not rely on the assumption that the lab is in the labs folder
  // TODO: This is required as the createNew method will not automatically create the parent directories
  labFilename = labFilename.replace('labs/', '');
  return labFilename;
}

// eslint-disable-next-line @typescript-eslint/quotes
export const DEFAULT_CONTENT: nbformat.INotebookContent = {
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
