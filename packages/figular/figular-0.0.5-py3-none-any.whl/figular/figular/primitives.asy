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

import "figular/page.asy" as page;
import "figular/style.asy" as style;
import "figular/stylesheet.asy" as stylesheet;

// -----------------------------------------------------

struct textbox {
  real width;
  pair place;
  align align;
  string text;
  style s;
  bool widthset = false;
  page p;
  Label l;

  private void draw(page p=this.p) {
    string textcontent = this.text;

    if(this.widthset) {
      if(this.align.dir == S) {
        textcontent = "\vphantom{\strut}" + textcontent;
      } else if (this.align.dir == N) {
        textcontent = textcontent + "\vphantom{\strut}";
      }
      textcontent = minipage("\centering{" + textcontent + "}", this.width);
    }

    this.l = this.s.textframe(p, this.place, this.align, textcontent);
  }

  void update(style s) {
    this.s = this.s + s;
    this.p.scrub(l);
    draw();
  }

  pair size() {
    page p;
    draw(p);
    return p.size();
  }

  void operator init(page p=currentpage,
                     real width=0,
                     pair place=(0,0),
                     align align=NoAlign,
                     string text="",
                     style s=nullstyle) {
    this.p = p;
    if(width != 0) {
      this.width=width;
      this.widthset=true;
    }
    this.place = place;
    this.align = align;
    this.text = text;

    style predefinedstyle = registertext(this.update);
    if(s == nullstyle) {
      this.s = predefinedstyle;
    } else {
      this.s = s;
    }
    this.draw();
  }
}

struct circle {
  style s;
  drawnpath dp = nulldrawnpath;
  textbox tb;
  page p;
  pair c;
  real r;

  private void draw() {
    if(dp == nulldrawnpath) {
      this.p.scrub(this.dp);
    }
    this.dp = this.s.filldraw(p, shift(this.c)*scale(r)*unitcircle);
  }

  public void updatestyle(style s) {
    // We create new so we're not sharing with anyone else
    // or affecting root stylesheet
    this.s = this.s+s;
    this.draw();
    this.tb.update(s);
  }

  void changeradius(real r) {
    this.r = r;
    this.draw();
  }

  void operator init(page p=currentpage, real r, pair center,
                     string text="", style s=nullstyle) {
    this.p = p;
    this.r = r;
    this.c = center;

    if(text != "") {
      this.tb = textbox(p, 2*r, center, text, s);
    }

    style predefinedstyle = registershape(this.updatestyle);
    if(s == nullstyle) {
      this.s = predefinedstyle;
    } else {
      this.s = s;
    }
    this.draw();
  }
}

struct shape {
  style s;
  drawnpath dp = nulldrawnpath;
  page p;
  path g;

  private void draw() {
    if(dp == nulldrawnpath) {
      this.p.scrub(this.dp);
    }
    this.dp = this.s.filldraw(p, g);
  }

  public void updatestyle(style s) {
    // We create new so we're not sharing with anyone else
    // or affecting root stylesheet
    this.s = this.s+s;
    this.draw();
  }

  void operator init(page p=currentpage, path g,
                     style s=nullstyle) {
    this.p = p;
    this.g = g;
    style predefinedstyle = registershape(this.updatestyle);
    if(s == nullstyle) {
      this.s = predefinedstyle;
    } else {
      this.s = s;
    }
    this.draw();
  }
}

struct line {
  style s;
  page p;
  path g;
  drawnpath dp=nulldrawnpath;

  private void draw() {
    if(dp == nulldrawnpath) {
      this.p.scrub(this.dp);
    }
    this.dp = this.s.draw(p, g);
  }

  public void update(style s) {
    // We create new so we're not sharing with anyone else
    // or affecting root stylesheet
    this.s = this.s+s;
    this.draw();
  }

  void operator init(page p=currentpage, path g, style s=nullstyle) {
    this.p = p;
    this.g = g;

    style predefinedstyle = registerline(this.update);
    if(s == nullstyle) {
      this.s = predefinedstyle;
    } else {
      this.s = s;
    }
    this.draw();
  }
}

