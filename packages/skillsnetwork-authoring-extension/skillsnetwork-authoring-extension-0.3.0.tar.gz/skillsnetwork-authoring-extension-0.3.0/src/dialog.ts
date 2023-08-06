/* eslint-disable @typescript-eslint/no-empty-function */
import { Widget } from '@lumino/widgets';
import { Dialog, showDialog, Spinner } from '@jupyterlab/apputils';
import { source } from './config';

/**
 * A widget that holds the loading spinner
 */
export class SpinnerDialog extends Widget {
  constructor() {
    const body = document.createElement('div');
    const spinner = new Spinner();
    body.appendChild(spinner.node);
    body.style.padding = '15px';
    super({ node: body });
  }
}

/**
 * Shows the Loading dialog
 */
export const show_spinner = (message:string): void => {
  const spinWidget = new SpinnerDialog();
  showDialog({
    title: message,
    body: spinWidget,
    buttons: [Dialog.cancelButton()]
  })
    .then(result => {
      if (!result.button.accept){
        source.cancel('Operation cancelled by the user.');
      }
    })
    .catch(error => {});
};

/**
 * Shows the Success dialog
 */
export const showSuccessPublishDialog = (): void => {
  showDialog({
    title: 'Success!',
    body: 'This lab was successfully submitted for publishing!',
    buttons: [Dialog.okButton()]
  })
    .then(result => {})
    .catch(error => {});
};

/**
 * Shows the Failed to publish dialog
 */
export const showFailurePublishDialog = (): void => {
  showDialog({
    title: 'Failed to Publish',
    body: 'This lab failed to publish.',
    buttons: [Dialog.okButton()]
  })
    .then(result => {})
    .catch(error => {});
};

/**
 * Shows the Failed to load lab dialog
 */
 export const showFailureImportLabDialog = (): void => {
  showDialog({
    title: 'Failed to Load Lab',
    body: 'This lab failed to load.',
    buttons: [Dialog.okButton()]
  })
    .then(result => {})
    .catch(error => {});
};
