/* Unofficial ONLYOFFICE Overtype toolbar — user-visible legal notices. SPDX-License-Identifier: AGPL-3.0-only */
(function () {
  'use strict';
  const plugin = window.Asc && window.Asc.plugin;
  if (!plugin) return;
  const TOGGLE = 'onlyoffice-native-overtype';
  const ABOUT = 'onlyoffice-native-overtype-about';
  let registered = false;
  plugin.init = function () {
    if (registered) return;
    registered = true;
    plugin.executeMethod('AddToolbarMenuItem', [{
      guid: plugin.guid || 'asc.{A360C0D9-711B-4C90-BFB4-58AC023074E6}',
      tabs: [{id: 'plugins', text: 'Plugins', items: [
        {id: TOGGLE, type: 'big-button', text: 'Overtype',
         hint: 'Nem hivatalos ONLYOFFICE-módosítás (2026). Insert váltja az INS/OVR módot. A jogi tájékoztatót a Névjegy és licencek gombbal nyithatja meg.',
         icons: 'resources/icon.png', lockInViewMode: false, enableToggle: false,
         split: false, items: []},
        {id: ABOUT, type: 'button', text: 'Névjegy és licencek',
         hint: 'Eredeti fejlesztő: Ascensio System SIA / ONLYOFFICE. Nem hivatalos módosítás. GNU AGPLv3 és ONLYOFFICE-kiegészítések.',
         icons: 'resources/icon.png', lockInViewMode: false,
         split: false, items: []}
      ]}]
    }]);
  };
  plugin.event_onToolbarMenuClick = function (id) {
    if (id === ABOUT) {
      if (typeof window.Asc.PluginWindow !== 'function') {
        console.error('Overtype: this editor cannot open legal information window');
        return;
      }
      const popup = new window.Asc.PluginWindow();
      popup.show({
        url: new URL('about.html', window.location.href).href,
        description: 'Overtype — Névjegy és licencek',
        type: 'window', size: [590, 460], buttons: []
      });
      return;
    }
    if (id !== TOGGLE) return;
    plugin.executeMethod('OOOvertypeToggle', [], function (mode) {
      if (typeof mode !== 'boolean') console.warn('Overtype: native toggle failed / editor not active');
    });
  };
})();
