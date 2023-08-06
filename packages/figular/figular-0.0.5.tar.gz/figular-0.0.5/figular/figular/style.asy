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

// We adopt asy's defaults to make use of their addition operator below
pen nullpen = defaultpen;

struct style {
  pen strokecolor;
  pen strokeopacity;
  real strokewidth;
  pen dashes;
  pen join;
  pen cap;
  pen fillcolor;
  // TODO: consider breaking out typical font settings into each their own
  // thing to closer match Inkscape. We've done it with textsize so why not the rest
  // maybe even separate structures for stroke, fill and text.
  pen text;
  real textsize;

  private pen flattenlinestyle() {
    // This only works as we use asy's defaults as our defaults and the
    // addition operator make sure all other non-default attributes of the
    // rightmost pen will override those of the leftmost pen.
    pen result=defaultpen;
    if(this.strokecolor != nullpen) {
      // Strip out our colour first as otherwise asy will add the colours
      result = colorless(result) + strokecolor;
    }
    if(this.strokeopacity != nullpen) {
      result += this.strokeopacity;
    }
    if(this.strokewidth != realMax) {
      result += this.strokewidth;
    }
    if(this.dashes != nullpen) {
      result += this.dashes;
    }
    if(this.join != nullpen) {
      result += this.join;
    }
    if(this.cap != nullpen) {
      result += this.cap;
    }
    return result;
  }

  private pen flattentextstyle() {
    pen result=this.text;
    if(this.textsize != realMax) {
      result += fontsize(this.textsize);
    }
    return result;
  }

  void operator init(pen strokecolor=nullpen,
                     pen strokeopacity=nullpen,
                     real strokewidth=realMax,
                     pen dashes=nullpen,
                     pen join=nullpen,
                     pen cap=nullpen,
                     pen fillcolor=nullpen,
                     pen text=nullpen,
                     real textsize=realMax) {
    this.strokecolor=strokecolor;
    this.strokeopacity=strokeopacity;
    this.strokewidth=strokewidth;
    this.dashes=dashes;
    this.join=join;
    this.cap=cap;
    this.fillcolor=fillcolor;
    this.text=text;
    this.textsize=textsize;
  }

  drawnpath draw(page p, path g) {
    pen finallinestyle = flattenlinestyle();
    drawnpath dp = drawnpath(g, new void(picture p) { draw(p, g, finallinestyle); });
    p.push(dp);
    return dp;
  }

  drawnpath filldraw(page p, path g) {
    pen finallinestyle = flattenlinestyle();
    drawnpath dp;

    // Asymptote's filldraw and draw seem to always draw an outline even when
    // linewidth=0. Bug?
    if(linewidth(finallinestyle) > 0) {
      dp = drawnpath(g, new void(picture p) { filldraw(p, g, this.fillcolor, finallinestyle); });
    } else {
      dp = drawnpath(g, new void(picture p) { fill(p, g, this.fillcolor); });
    }
    p.push(dp);
    return dp;
  }

  Label textframe(page p, pair place, align align, string text) {
    pen finaltextstyle = flattentextstyle();
    Label l = Label(text, text, place, align, finaltextstyle);
    p.push(l);
    return l;
  }
}

style operator+(style a, style b) {
  style result;
  if(b.strokecolor != nullpen) {
    // Strip out our colour first as otherwise asy will add the colours
    result.strokecolor = b.strokecolor;
  } else {
    result.strokecolor = a.strokecolor;
  }
  if(b.strokeopacity != nullpen) {
    result.strokeopacity = b.strokeopacity;
  } else {
    result.strokeopacity = a.strokeopacity;
  }
  if(b.strokewidth != realMax) {
    result.strokewidth = b.strokewidth;
  } else {
    result.strokewidth = a.strokewidth;
  }
  if(b.dashes != nullpen) {
    result.dashes = b.dashes;
  } else {
    result.dashes = a.dashes;
  }
  if(b.join != nullpen) {
    result.join = b.join;
  } else {
    result.join= a.join;
  }
  if(b.cap != nullpen) {
    result.cap = b.cap;
  } else {
    result.cap= a.cap;
  }
  if(b.fillcolor != nullpen) {
    result.fillcolor = b.fillcolor;
  } else {
    result.fillcolor= a.fillcolor;
  }
  if(b.text != nullpen) {
    result.text = b.text;
  } else {
    result.text = a.text;
  }
  if(b.textsize != realMax) {
    result.textsize = b.textsize;
  } else {
    result.textsize = a.textsize;
  }
  return result;
}

style nullstyle = style();

// ----------------------------------------------------------------------------
// Fonts
// ----------------------------------------------------------------------------

usepackage("fontspec");

pen getfont(string fontname) {
  return fontcommand("\setmainfont{"+fontname+"}");
}

struct fontrec {
  pen wield;
  string family;
  string style;

  void operator init(pen wield, string family, string style) {
    this.wield = wield;
    this.family = family;
    this.style = style;
  }
}

struct fontinfo {
  // TODO:
  // * We desperately need a uniform way of categorising/referring to typefaces/fonts
  // * Some fonts such as the built-in helpers for standard PostScript fonts end up being
  //   substituted in final PDF. Should it not be the case that you get what
  //   you request or should it work like the web and substitute as/when
  //   needed.     
  fontrec[] all;
  fontrec avantgarde = all.push(fontrec(AvantGarde(), "Avant Garde", "Normal"));
  fontrec avantgarde_bold = all.push(fontrec(AvantGarde("b"), "Avant Garde", "Bold"));
  fontrec computermodernroman = all.push(fontrec(font("OT1", "cmr", "m", "n"), "Computer Modern Roman", "Normal"));
  fontrec computermodernroman_bold = all.push(fontrec(font("OT1", "cmr", "b", "n"), "Computer Modern Roman", "Bold"));
  fontrec computermodern_sansserif = all.push(fontrec(font("OT1", "cmss", "m", "n"), "Computer Modern Sans Serif", "Normal"));
  fontrec computermodern_teletype = all.push(fontrec(font("OT1", "cmtt", "m", "n"), "Computer Modern Teletype", "Normal"));
  fontrec dejavu_sansserif = all.push(fontrec(getfont("DejaVu Sans"), "DeJaVu Sans Serif", "Normal"));
  fontrec postscript_helvetica = all.push(fontrec(Helvetica(), "Helvetica", "Normal"));
}

fontinfo font;

// TODO: Only required for circle and we should eliminate this by having UI
// pass through proper fontname
pen findfont(string name) {
  if(name == "cmr") {
    return font.computermodernroman.wield;
  } else if(name == "cmss") {
    return font.computermodern_sansserif.wield;
  } else if(name == "cmtt") {
    return font.computermodern_teletype.wield;
  }
  abort("findfont - no support for: "+name);
  return defaultpen;
}

pen operator cast(fontrec fs) { return fs.wield; };
