import {ServerConnection} from '@jupyterlab/services';
import axios from "axios";
import { KernelSpecAPI } from '@jupyterlab/services';

interface Configuration {
	ATLAS_BASE_URL: string;
}

const getServerBaseUrl = (settings: ServerConnection.ISettings): string => {
  let baseUrl = settings.baseUrl;
  // Add the trailing slash if it is missing.
  if (!baseUrl.endsWith('/')) {
    baseUrl += '/';
  }
  return baseUrl;
}

export const ATLAS_BASE_URL = await (async (): Promise<string> => {
	const currentUrl = window.location.href;

	const parameters = new URL(currentUrl).searchParams;
	const baseUrl: string | undefined = parameters.get('atlas_base_url')!;
	if (baseUrl === null) {
		const init: RequestInit = {
			method: 'GET',
		};
		const settings = ServerConnection.makeSettings();
		const requestUrl = getServerBaseUrl(settings) + 'skillsnetwork-authoring-extension/config';
    const response = await ServerConnection.makeRequest(
			requestUrl,
			init,
			settings,
		);
		const configuration: Configuration
      = (await response.json()) as Configuration;
		return configuration.ATLAS_BASE_URL;
  } else {
    return baseUrl
  }
})();

/**
 * Extracts the session token. Will first try to get a token via the URL, if none was found then try to get the token via cookie.
 *
 * @returns token
 */
export const ATLAS_TOKEN = async (): Promise<string> => {

  const currentURL = window.location.href;
  const params = new URL(currentURL).searchParams;
  let token: string | null = params.get('token');
  Globals.LAB_TOOL_TYPE = 'JUPYTER_LITE';

  if (token === null) {
    // Try getting it from cookie
    const COOKIE_NAME: string = process.env.ATLAS_TOKEN_COOKIE_NAME ?? 'atlas_token';
    const reg: RegExp = new RegExp(`(^| )${COOKIE_NAME}=([^;]+)`);
    let match = reg.exec(document.cookie);
    // If found then set that as our token o/w set it as empty str for now
    (match !== null) ? token = match[2] : token = 'NO_TOKEN'
    Globals.LAB_TOOL_TYPE = 'JUPYTER_LAB';
  }

  if (token === null || token === 'NO_TOKEN'){
    // If no token was found in the URL or cookies, the author is in their local env (hopefully...)
    Globals.AUTHOR_ENV = 'local'
  }else{
    Globals.AUTHOR_ENV = 'browser'
  }

  if (Globals.LAB_TOOL_TYPE === 'JUPYTER_LAB') {
    // In production, jupyterlab doesn't have python3 as a kernel option so use python
    Globals.PY_KERNEL_NAME = await GET_PYKERNEL();
    Globals.DEFAULT_LAB_NAME = 'lab.ipynb';
  }else if (Globals.LAB_TOOL_TYPE === 'JUPYTER_LITE'){
    Globals.PY_KERNEL_NAME = 'python'
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
export const GET_PYKERNEL = async (): Promise<string> => {
  // Get the available kernels
  let kspecs = await (await KernelSpecAPI.getSpecs()).kernelspecs;

  function checkPython(spec: string){
    return spec.includes('python')
  }

  let keys = Object.keys(kspecs)
  // filter for only the spec names with python in it, sorted
  let filtered_keys = keys.filter(checkPython).sort()
  // return the priority python
  let pykernel = filtered_keys[filtered_keys.length-1];

  return pykernel
}

export var CancelToken = axios.CancelToken;
export var source = CancelToken.source();

// Global variables
export class Globals {
  public static TOKEN: string;
  public static AUTHOR_ENV: string;
  public static LAB_TOOL_TYPE: string;
  public static PY_KERNEL_NAME: string;
  public static DEFAULT_LAB_NAME: string;
}
