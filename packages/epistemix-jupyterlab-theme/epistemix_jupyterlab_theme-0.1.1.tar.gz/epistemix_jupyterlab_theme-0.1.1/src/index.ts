import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { IThemeManager } from '@jupyterlab/apputils';

/**
 * Initialization data for the epistemix_jupyterlab_theme extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'epistemix_jupyterlab_theme:plugin',
  autoStart: true,
  requires: [IThemeManager],
  activate: (app: JupyterFrontEnd, manager: IThemeManager) => {
    console.log(
      'JupyterLab extension epistemix_jupyterlab_theme is activated!'
    );
    const style = 'epistemix_jupyterlab_theme/index.css';

    manager.register({
      name: 'Epistemix',
      isLight: false,
      load: () => manager.loadCSS(style),
      unload: () => Promise.resolve(undefined)
    });
  }
};

export default plugin;
