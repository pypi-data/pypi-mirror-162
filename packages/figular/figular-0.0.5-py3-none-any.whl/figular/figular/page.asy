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

pair a4=(210mm, 297mm);

struct drawnpath {
  path g;
  void drawroutine(picture);

  void operator init(path g, void drawroutine(picture)) {
    this.g = g;
    this.drawroutine = drawroutine;
  }
}

drawnpath nulldrawnpath;

struct page {
  private struct pagepos {
    page page;
    pair pos;

    void operator init(page page, pair pos) {
      this.page = page; this.pos = pos;
    }
  }

  pair min, max; 
  drawnpath[] drawnpaths = new drawnpath[]{};
  Label[] labels = new Label[]{};
  pagepos[] pagepos = new pagepos[]{};
  picture pic;
  pair dim = (0,0);
  bool uptodate = false;

  // Dimensions

  void setdim(pair dim) {
    this.uptodate = false;
    this.dim = dim;
    fill(this.pic, scale(dim.x, dim.y)*unitsquare, p=invisible);
  }

  pair size() {
    return this.max-this.min;
  }

  pair min() {
    return this.min;
  }

  pair max() {
    return this.max;
  }

  bool empty() {
    return drawnpaths.length == 0 && 
           labels.length == 0 &&
           pagepos.length == 0;
  }

  // Bounds

  private void updatebounds(pair possmin, pair possmax) {
    if(possmin.x < min.x) { min = (possmin.x, min.y); }
    if(possmin.y < min.y) { min = (min.x, possmin.y); }
    if(possmax.x > max.x) { max = (possmax.x, max.y); }
    if(possmax.y > max.y) { max = (max.x, possmax.y); }
  }

  private void updatebounds(drawnpath dp) {
    pair possmin, possmax;
    picture p;

    dp.drawroutine(p);
    updatebounds(min(p), max(p));
  }

  private void updatebounds(Label l) {
    picture p;
    label(p, l);
    updatebounds(min(p), max(p));
  }

  private void updatebounds(page p, pair pos) {
    pair possmin, possmax;
    possmin = shift(pos)*p.min();
    possmax = shift(pos)*p.max();
    updatebounds(possmin, possmax);
  }

  private void updateallbounds() {
    min = (realMax,realMax);
    max = (realMin,realMin);

    for(drawnpath dp : drawnpaths) {
      updatebounds(dp);
    }
    for(Label l : labels) {
      updatebounds(l);
    }
  }

  // Deferred draw pushing and scrubbing

  void push(drawnpath dp) {
    this.uptodate = false;
    drawnpaths.push(dp);
    updatebounds(dp);
  }

  void scrub(drawnpath dp) {
    for(int i=0 ; i < drawnpaths.length ; ++i) {
      if(drawnpaths[i] == dp) {
        drawnpaths.delete(i);
        updateallbounds();
        break;
      }
    }
  }

  void push(Label l) {
    this.uptodate = false;
    labels.push(l);
    updatebounds(l);
  }

  void scrub(Label l) {
    for(int i=0 ; i < labels.length ; ++i) {
      if(labels[i] == l) {
        labels.delete(i);
        updateallbounds();
        break;
      }
    }
  }

  void push(page page, pair pos) {
    this.uptodate = false;
    pagepos.push(pagepos(page, pos));
    updatebounds(page, pos);
  }

  void print() {
    // Shipout process may call print more than once so be idempotent
    if(!this.uptodate) {
      // TODO: We naively draw paths then labels but we should draw in the order
      // they are provided. Note that labels are always on top in asy unless you
      // call layer()
      for(drawnpath dp: drawnpaths) {
        dp.drawroutine(this.pic);
      }
      for(Label l: labels) {
        label(this.pic, l);
      }
      for(pagepos pp: pagepos) {
        pp.page.print(); // Ensure it's up-to-date
        // Asy ignores our flipped coords when we add a page's picture so
        // flip then as we add
        add(this.pic, reflect(W,E)*pp.page.pic, pp.pos);
      }

      // Finally clip anything outside 
      if(this.dim != (0,0)) {
        clip(this.pic, scale(this.dim.x, this.dim.y)*unitsquare);
      }

      this.uptodate = true;
    }
  }

  void operator init(picture pic=new picture) {
    this.pic = pic;
    // Set axes to behave as normal drawing programs, i.e. increase down/right
    unitsize(this.pic, 1, -1);
  }
}

page currentpage = page(currentpicture);

void page(pair dim) {
  currentpage.setdim(dim);
}

void add(page dest, page src, pair topleft=(0,0)) {
  dest.push(src, topleft);
}
// Insert code into shipout to give us chance to do final draw
// One shipout may end up calling the other, or only one may be called. So
// page's print should be idempotent and ideally not repeat itself.
void shipoutframe(string prefix, frame f, string format, bool wait, bool view, string options, string script, light light, projection P, transform t) = shipout;
void shipoutpicture(string prefix, picture pic, frame orientation(frame), string format, bool wait, bool view, string options, string script, light light, projection P) = shipout;
shipout = new void(string prefix, frame f, string format, bool wait, bool view, string options, string script, light light, projection P, transform t) {
  currentpage.print();
  shipoutframe(prefix, f, format, wait, view, options, script, light, P, t);
};
shipout = new void(string prefix, picture pic, frame orientation(frame), string format, bool wait, bool view, string options, string script, light light, projection P) {
  currentpage.print();
  shipoutpicture(prefix, pic, orientation, format, wait, view, options, script, light, P);
};
