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

import "figular/cleanse.asy" as cleanse;
import "figular/page.asy" as page;
import "figular/paramsolver.asy" as paramsolver;
import "figular/primitives.asy" as primitives;
import "figular/stylereset.asy" as stylereset;

struct circle {
  string[] blobs={};
  real degreeStart=0;
  bool middle=false;
  pen font = font.computermodernroman + defaultstylesheet.collight;
  parampair blobsizeparam;

  private pair getlabelsize(string text) {
    textbox t = textbox(page(), text, style(text=this.font));
    return t.size();
  }

  private pair getmaxlabelsize() {
    pair maxlabelsize = (0,0);
    for(string blobName : blobs) {
      pair size = getlabelsize(blobName);
      if (size.x > maxlabelsize.x) {
        maxlabelsize = (size.x, maxlabelsize.y);
      }
      if (size.y > maxlabelsize.y) {
        maxlabelsize = (maxlabelsize.x, size.y);
      }
    }
    return maxlabelsize;
  }

  private void drawblob(page p, pair pos, string blobName, real blobradius) {
    // We first create the circle to ensure default style is adopted
    primitives.circle c = circle(p, blobradius, pos, blobName);
    // Then we add the font to the that
    c.updatestyle(style(text=this.font));
  }

  private void drawcircle(page p, string[] blobNames, real degreeStart=0,
                          bool middle=false) {
    real magicnumber = 10;
    pair maxlabelsize = this.blobsizeparam.get();
    real blobradius = max(maxlabelsize.x, maxlabelsize.y)/2 + magicnumber;

    if(middle && blobNames.length > 1) {
      drawblob(p, (0,0), blobNames[0], blobradius);
      blobNames.delete(0,0);
    }

    real degreeStep = 360 / blobNames.length;
    real radius = 0;

    radius = blobradius + magicnumber;
    if (blobNames.length > 1) {
        radius = (blobradius + magicnumber) / Sin(degreeStep/2);
    }

    if(middle && radius < (2*blobradius)) {
      //There's a chance radius is too small to make space for middle blob
      radius = 2*blobradius + (magicnumber * 2);
    }

    pair pos = rotate(degreeStart) * (0, -radius);

    for(string blobName : blobNames) {
      drawblob(p, pos, blobName, blobradius);
      pos = rotate(degreeStep) * pos;
    }
  }

  void operator init(string[] input) {
    string arg;
    string[] parts;

    for(string arg: input) {
      parts = split(arg, "=");

      if(parts[0] == "blob" && parts.length > 1) {
        string cleansed = cleanse.escape(substr(arg, 5));
        if(length(cleansed) > 0) {
          blobs.push(cleansed);
        }
      } else if(parts[0] == "degreeStart" && parts.length > 1) {
        degreeStart = (real)parts[1];
      } else if(parts[0] == "middle" && parts.length > 1) {
        middle = parts[1] == "true";
      } else if(parts[0] == "font" && parts.length > 1) {
        font = findfont(parts[1]);
      }
    }

    this.blobsizeparam = parampair(getmaxlabelsize);
  }

  void draw(page p) {
    if(blobs.length != 0) {
      drawcircle(p, blobs, degreeStart, middle);
    }
  }

  void solveblobsize(solvepair solver) {
     solver.suggest(this.blobsizeparam);
  }

}

void run(picture pic, string[] input) {
  page p = page(pic);
  circle circle = circle(input);
  circle.draw(p);
  p.print();
}
