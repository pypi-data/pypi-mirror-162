/* eslint-disable no-async-promise-executor */
import { AxiosError, AxiosInstance } from 'axios';
import { show_spinner, showSuccessPublishDialog, showFailurePublishDialog, showFailureImportLabDialog } from './dialog';
import { Dialog } from '@jupyterlab/apputils';
import { ATLAS_BASE_URL } from './config';
import axios from 'axios';
import { Globals } from './config';
import { source } from './config';

export const axiosHandler = (lab_token: string): AxiosInstance => {
  if (lab_token) Globals.TOKEN = lab_token;
  const atlasClient = axios.create({
      baseURL: ATLAS_BASE_URL,
      headers: {
        Authorization: `Bearer ${lab_token}`,
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*'
      }
    });
  return atlasClient;
}

/**
 * GET the lab model / JSON that represents a .ipynb file/notebook from ATLAS
 *
 * @param axiosHandler Axios client that contains a JWT Bearer token
 * @returns Promise<void>
 */
export const getLabModel = (axiosHandler: AxiosInstance) => {
  // GET the lab model
  return axiosHandler
    .get('v1/labs')
    .then(result => {
      Dialog.flush(); //remove spinner
      return JSON.parse(result.data.body);
    })
    .catch(error => {
      Dialog.flush(); //remove spinner
      showFailureImportLabDialog();
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
export const postLabModel = async (
  axiosHandler: AxiosInstance,
  labModel: string
): Promise<void> => {
  show_spinner('Publishing...');
  return new Promise<void>(async (resolve, reject) => {
    await axiosHandler
      .post('v1/labs', {
        body: labModel
      },{
        cancelToken: source.token,
      })
      .then(res => {
        console.log('SUCCESSFULLY PUSHED', res);
        Dialog.flush(); //remove spinner
        showSuccessPublishDialog();
        resolve;
      })
      .catch((error: AxiosError) => {
        console.log(error);
        Dialog.flush(); // remove spinner
        showFailurePublishDialog();
        reject;
      });
  });
};
