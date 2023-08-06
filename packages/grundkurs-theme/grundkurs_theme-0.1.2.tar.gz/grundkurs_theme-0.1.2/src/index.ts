import {
  JupyterFrontEnd,
  JupyterFrontEndPlugin
} from '@jupyterlab/application';

import { IThemeManager } from '@jupyterlab/apputils';

/**
 * Initialization data for the grundkurs_theme extension.
 */
const plugin: JupyterFrontEndPlugin<void> = {
  id: 'grundkurs_theme:plugin',
  autoStart: true,
  requires: [IThemeManager],
  activate: (app: JupyterFrontEnd, manager: IThemeManager) => {
    console.log('JupyterLab extension grundkurs_theme is activated!');
    const style = 'grundkurs_theme/index.css';

    manager.register({
      name: 'grundkurs_theme',
      isLight: true,
      load: () => manager.loadCSS(style),
      unload: () => Promise.resolve(undefined)
    });
  }
};

export default plugin;
