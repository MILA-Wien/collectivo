# Components

Define external components that can be used in the frontend. An alternative is to add Vue components directly to the frontend code through a [custom extension](../development.md#develop-custom-extensions).

## Installation

Add `collectivo.components` to `extensions` in [`collectivo.yml`](../reference.md#settings).

## Usage by other extensions

### Register a component

A component can be registered by a [custom extension](../development.md#develop-custom-extensions) as follows:

```python
from collectivo.extensions.modles import Extension
from collectivo.components.models import Component

Component.objects.register(
    name='my-component',
    type='iframe',
    path='https://example.com/',
    extension=Extension.objects.get(name='my-extension'),
)
```

There are two types of components:

- `iframe`: The component is displayed as an iframe.
- `remote`: The component is displayed as a remote webcomponent, using [vite-plugin-federation](https://github.com/originjs/vite-plugin-federation). All Javascript frameworks that are supported by Vite can be used, including Vue, React, Svelte, and more. The path must point towards a remote entry point. This is an experimental feature and can be subject to errors.

The component will be available on the frontend through the route `/<extension.name>/<component.name>`. For example, the component registered above will be available at `/my-extension/my-component` and will display an iframe to `https://example.com`. Hint: currently only 8 components can be registered per collectivo instance.

A [menu item](menus.md) or [dashboard button](dashboard.md) can be used to create an internal link to this route.

### Include a react app as a component
React apps can't be included as remote components without a writing a custom entrypoint. React components can be included as shown in th documentation of[vite-plugin-federation](https://github.com/originjs/vite-plugin-federation). Loading the app as a js module already triggers the react app to be loaded. This can be prevented by adding a `render()` method to the app's entry point. The react app can then be loaded as a remote component and will be rendered into the div with the id of the registered component.

```js
// src/collectivoComponent.jsx
import React from 'react';
import { createRoot } from 'react-dom/client';

export function render() {
  const App = React.lazy(() => import('./App'));
  const el = document.getElementById("my-component"); 
  const root = createRoot(el);
  root.render(<App />);
}
let M = {}
M.render = render;

export default M;
```
Example vite config for the react app:
```js
// vite.config.js
import { defineConfig } from 'vite';
import reactRefresh from '@vitejs/plugin-react-refresh'
import viteTsconfigPaths from 'vite-tsconfig-paths';
import svgrPlugin from 'vite-plugin-svgr';
import federation from '@originjs/vite-plugin-federation';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [reactRefresh(), viteTsconfigPaths(), svgrPlugin(),
    federation({
      name: 'my-component',
      filename: 'my-component.js',
      exposes: {
        './component': './src/collectvoComponent.jsx',
      },
    }),
  ],
  build: {
    target: 'esnext',
    minify: false,
  },
  base: '',
});

```

And the corresponding component registration:
```python
from collectivo.extensions.modles import Extension
from collectivo.components.models import Component

Component.objects.register(
    name='my-component',
    type='remote',
    path='https://example.com/assets/my-component.js',
    extension=Extension.objects.get(name='my-extension'),
)
```

## Reference

:::collectivo.components.models.Component
