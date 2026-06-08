// Copyright 2026 Rinat Ishmaev
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

import "vuetify/styles";
import "@mdi/font/css/materialdesignicons.css";
import { createVuetify } from "vuetify";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";
import { getPreset } from "../themes/presets";

const ocean = getPreset("ocean");

export const vuetify = createVuetify({
  components,
  directives,
  theme: {
    defaultTheme: "cedLight",
    themes: {
      cedLight: {
        dark: false,
        colors: { ...ocean.light },
      },
      cedDark: {
        dark: true,
        colors: { ...ocean.dark },
      },
    },
  },
});
