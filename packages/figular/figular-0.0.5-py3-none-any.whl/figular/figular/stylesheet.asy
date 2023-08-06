// SPDX-FileCopyrightText: 2021-2 Galagic Limited, et. al. <https://galagic.com>
//
// SPDX-License-Identifier: AGPL-3.0-or-later
//
// figular generates visualisations from flexible, reusable parts
//
// For full copyright information see the AUTHORS file at the top-level
// directory of this distribution or at
// [AUTHORS](https://gitlab.com/thegalagic/figular/AUTHORS.md)
//
// This program is free software: you can redistribute it and/or modify it under
// the terms of the GNU Affero General Public License as published by the Free
// Software Foundation, either version 3 of the License, or (at your option) any
// later version.
//
// This program is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
// FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more
// details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program. If not, see <https://www.gnu.org/licenses/>.

import "figular/style.asy" as style;

typedef void updatestyle(style s);

// It's like a collection of restylable things
// our selector(s)

struct drawnthings {
  updatestyle shapes[];
  updatestyle texts[];
  updatestyle lines[];
}

drawnthings dt;

// Default stylesheet
struct stylesheet {
  pen coldark = gray(0.2);
  pen collight = rgb(.9,.9,.9);
  style circlestyle = style(strokewidth=0, fillcolor=coldark);
  style textstyle = style(text=font.computermodernroman + collight);
  style linestyle = style(strokewidth=1, strokecolor=coldark);
}

stylesheet defaultstylesheet;

void setupstyleforcircles(style s) {
  defaultstylesheet.circlestyle = s;
}

// Register stuff

style registershape(updatestyle s) {
  dt.shapes.push(s);
  return defaultstylesheet.circlestyle;
}

style registertext(updatestyle s) {
  dt.texts.push(s);
  return defaultstylesheet.textstyle;
}

style registerline(updatestyle s) {
  dt.lines.push(s);
  return defaultstylesheet.linestyle;
}

// Select and style

void styleshapes(style s) {
  // Update stylesheet
  defaultstylesheet.circlestyle = s;

  for(int x=0; x < dt.shapes.length ; ++x) {
    dt.shapes[x](s);
  }
}
