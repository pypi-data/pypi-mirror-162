import { JupyterFrontEndPlugin } from '@jupyterlab/application';
import { menu } from './menu';
import plugin from './button';

const main: JupyterFrontEndPlugin<any>[] = [
  plugin,
  menu
];

export default main;
