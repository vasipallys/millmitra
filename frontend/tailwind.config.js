/** Coexist with MUI: no preflight, tw- prefix, used only on new composable pages. */
export default {
  prefix: 'tw-',
  corePlugins: {
    preflight: false,
  },
  content: [
    './src/pages/Iiot.jsx',
    './src/pages/FormBuilder.jsx',
    './src/pages/DashboardBuilder.jsx',
    './src/pages/DynamicEntity.jsx',
    './src/components/metadata/**/*.{js,jsx}',
  ],
  theme: {
    extend: {},
  },
  plugins: [],
};
