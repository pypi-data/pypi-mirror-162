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
import "figular/primitives.asy" as primitives;
import "figular/stylereset.asy" as stylereset;

/******************************************************************************
Treerenderer assumptions:

* All provided pictures (heads, leaves) will be joined to the tree at their
  origin (0,0).
* All provided pictures are the same height. The coutourpictures assume each
  element of their extremes is another row down where each row is the exact
  same height.
*******************************************************************************/

struct treerenderer {

  // Maybe countourpage?
  private struct contourpicture {
    page p;
    real[] leftextremes;
    real[] rightextremes;

    void operator init(page p, real[] leftextremes, real[] rightextremes) {
      this.p = p;
      this.leftextremes = leftextremes;
      this.rightextremes = rightextremes;
    }
  }

  page head;
  page[] leaves;
  treerenderer[] trees;

  void operator init(page head) {
    this.head = head;
  }

  void addleaf(page leaf) {
    this.leaves.push(leaf);
  }

  void addtree(treerenderer tr) {
    this.trees.push(tr);
  }

  private treerenderer[] converttotreerenderer(page[] pages) {
    // Use map and maparray?
    treerenderer[] tr;
    for(page p : pages) {
      tr.push(treerenderer(p));
    }
    return tr;
  }

  private treerenderer[][] pack(page[] leaves, treerenderer[] trees) {
    treerenderer[][] tr;
    treerenderer[] topnodes = converttotreerenderer(leaves);
    treerenderer[] bottomnodes = copy(trees);
    bool tick = true;

    // If only one tree treat it as any other topnode
    if(topnodes.length == 1 && bottomnodes.length == 1) {
      topnodes.push(bottomnodes.pop());
    }
    // If we've an odd set of topnodes take the first one out on its own row
    if(topnodes.length % 2 == 1) {
      treerenderer[] row = { topnodes[0] };
      tr.push(row);
      topnodes.delete(0);
    }

    for(treerenderer topnode : topnodes) {
      if (tick) { tr.push(new treerenderer[0]); }
      tr[tr.length-1].push(topnode);
      tick = !tick;
    }

    // Put all bottom nodes on their own final row
    if(bottomnodes.length > 0) {
      tr.push(new treerenderer[0]);
      for(treerenderer tree : bottomnodes) {
        tr[tr.length-1].push(tree);
      }
    }

    return tr;
  }

  private real calcspacing(contourpicture left, contourpicture right) {
    real spacing;

    for(int i = 0 ; i < left.rightextremes.length &&
                    i < right.leftextremes.length ; ++i) {
      // Get the maximum left/right extremes of this level and surrounding +/- 1
      // By considering surrounding levels we prevent trees from plugging into each
      // other's gaps too closely, confusing the strucutre on large org charts
      int lowerslice = max(new int[] {i - 1, 0});
      real rightextreme = max(left.rightextremes[lowerslice:i+2]);
      real leftextreme = min(right.leftextremes[lowerslice:i+2]);

      real potentialspacing = rightextreme + abs(leftextreme);
      if(potentialspacing > spacing) {
        spacing = potentialspacing;
      }
    }

    return spacing;
  }

  private contourpicture rendercontour() {
    real horizspacing = 80;
    real vertspacing = 120;
    real cursor_y = 0;
    // We always base step down by the height of the head,
    // note the assumptions at top of this file
    real stepdown = abs(head.size().y/2) + vertspacing;
    real stepdowndrawfactor = 1;

    page dest;
    real[] leftextremes;
    real[] rightextremes;

    // pack them all up and treat all as treerenderers
    treerenderer[][] tree = pack(this.leaves, this.trees);

    // Add head's extremes
    leftextremes.push(head.min().x);
    rightextremes.push(head.max().x);

    for(treerenderer[] row : tree) {
      contourpicture[] contourpictures;
      real[] spacings;
      real stepleft;

      for(treerenderer tr : row) {
        contourpictures.push(tr.rendercontour());

        // If we got more than one we need to do spacings between them
        if(contourpictures.length > 1) {
          real spacing = calcspacing(contourpictures[contourpictures.length-2],
                                     contourpictures[contourpictures.length-1]);
          spacings.push(spacing + horizspacing);
        }
      }

      real cursor_x;
      if(contourpictures.length == 1 && tree.length == 1) {
        // Lone left/subtree under the head, place it directly below
        spacings.push(0);
      } else if(contourpictures.length == 1) {
        // Special case - has nothing following it so spacing must be forced
        real spacing = contourpictures[contourpictures.length-1].rightextremes[0];
        spacing += horizspacing/2;
        spacings.push(spacing);
        cursor_x = -spacing;
      } else {
        // Below we expect a spacing for every picture, add a final one
        spacings.push(0);
        cursor_x = -sum(spacings)/2;
      }

      // Draw the step down
      cursor_y += stepdown;
      line(dest, (0, cursor_y - (stepdown*stepdowndrawfactor)) -- 
                  (0, cursor_y - stepdown/2));

      for(int i = 0 ; i < contourpictures.length ; ++i) {
        // Always draw the stick down
        line(dest, (cursor_x, cursor_y) -- (cursor_x, cursor_y - stepdown/2));
        // Draw the next line across unless we're at the end of a long row
        if(i == 0 || i < row.length - 1) {
          // Draw the line over
          line(dest, (cursor_x, cursor_y - stepdown/2) -- 
                     (cursor_x + spacings[i], cursor_y - stepdown/2));
        }

        // Draw the card
        add(dest, contourpictures[i].p, (cursor_x, cursor_y));

        // At the start and end update our extremes
        if(i == 0) {
          // Update left extremes
          for(real leftextreme : contourpictures[i].leftextremes) {
            leftextremes.push(leftextreme + cursor_x);
          }
        }
        if(i == contourpictures.length - 1) {
          // Update right extremes
          for(real rightextreme : contourpictures[i].rightextremes) {
            rightextremes.push(rightextreme + cursor_x);
          }
        }

        // Move across for next one
        cursor_x += spacings[i];
      }
      // On further levels we need to draw back up higher to connect the levels
      stepdowndrawfactor = 1.5;
    }

    // Draw head last so it's on top of lines
    add(dest, head, (0,0));
    return contourpicture(dest, leftextremes, rightextremes);
  }

  public page render() {
    return rendercontour().p;
  }
}

/******************************************************************************

drawcard draws the actual people's 'cards' on the chart.

*******************************************************************************/

page drawcard(string title, string subtitle) {
  page p;
  int fontsize = 12;
  real corner_dia = 3 * fontsize ;
  real card_height = 2.5 * corner_dia ;
  real card_width = 5 * corner_dia;
  pen titlepen = font.computermodernroman_bold + defaultstylesheet.collight;
  pen subtitlepen = font.postscript_helvetica + defaultstylesheet.collight;

  // Box
  shape(p, (-card_width/2, card_height/2 - corner_dia/2)--
           (-card_width/2,-card_height/2 + corner_dia/2){down}..
           (-card_width/2+corner_dia/2,-card_height/2)--
           (card_width/2-corner_dia/2,-card_height/2){right}..
           (card_width/2,-card_height/2 + corner_dia/2)--
           (card_width/2, card_height/2 - corner_dia/2){up}..
           (card_width/2-corner_dia/2,card_height/2)--
           (-card_width/2+corner_dia/2,card_height/2){left}..
          cycle);

  // Title
  // This is a rule of thumb that works for us
  real descenderadjust = fontsize/2;
  real titleoffset = .2*corner_dia;
  textbox(p, width=4*corner_dia, place=(0, -titleoffset),
          align=N, title, style(text=titlepen+basealign, textsize=fontsize));

  // Big underline
  line(p, (-2*corner_dia,0)--(2*corner_dia,0), style(strokecolor=defaultstylesheet.collight, strokewidth=1));

  // Subtitle
  textbox(p, width=4*corner_dia, place=(0, titleoffset),
          align=S, subtitle, style(text=subtitlepen, textsize=9));

  return p;
}

/******************************************************************************

A person, who can draw themselves and team, know their title.

*******************************************************************************/

struct person {
  restricted person[] team;
  restricted string name;
  restricted string title;
  
  void operator init(string name, string title="") {
    this.name = name;
    this.title = title;
  }

  void updatetitle(string title) {
    this.title = title;
  }
  
  void addteammember(person p) {
    team.push(p);
  }

  private void drawontree(page drawcard(string, string),
                          treerenderer treerenderer,
                          treerenderer treerendererfactory(page head)) {
    page myLabel=drawcard(this.name, this.title);

    if (team.length == 0) {
      // We are a leaf
      treerenderer.addleaf(myLabel);
    } else {
      // We are a subtree
      treerenderer subtreerenderer = treerendererfactory(myLabel);
      for(person p : team) {
        p.drawontree(drawcard, subtreerenderer, treerendererfactory);
      }
      treerenderer.addtree(subtreerenderer);
    }
  }

  page draw(page drawcard(string, string),              // Function that draws cards
            treerenderer treerendererfactory(page head)
           ) {
    page myLabel=drawcard(this.name, this.title);
    treerenderer treerenderer = treerendererfactory(myLabel);
    for(person p : team) {
      p.drawontree(drawcard, treerenderer, treerendererfactory);
    }
    return treerenderer.render();
  }

  static person nullperson = person("NULL");
}

/******************************************************************************

Personmap and Keyvalue are straight from
[asymptote/map.asy at master · vectorgraphics/asymptote · GitHub]
(https://github.com/vectorgraphics/asymptote/blob/master/base/map.asy)
But we've used nullperson instead of a default in lookup.

*******************************************************************************/

struct keyvalue {
  restricted string key;
  restricted person T;

  void operator init(string key) {
    this.key=key;
  }
  void operator init(string key, person T) {
    this.key=key;
    this.T=T;
  }
}

struct personmap {
  private keyvalue[] M;

  bool operator < (keyvalue a, keyvalue b) {return a.key < b.key;}

  void add(string key, person T) {
    keyvalue m=keyvalue(key,T);
    M.insert(search(M,m,operator <)+1,m);
  }

  person lookup(string key) {
    int i=search(M,keyvalue(key),operator <);
    if(i >= 0 && M[i].key == key) return M[i].T;
    return person.nullperson;
  }
}

/******************************************************************************

Organisation allows you to add people by their data, ensures they are linked up
to their bosses and keeps track of who's top dog.

*******************************************************************************/

struct organisation {
  restricted person topdog = null;
  private personmap org;

  void add(string name, string title, string boss="") {
    person person = org.lookup(name);

    if(person == person.nullperson) {
      person = person(name, title);
      org.add(name, person);
    } else {
      // If they are already present they are a boss with no title
      person.updatetitle(title);
    }

    if(length(boss) > 0) {
      person bossperson = org.lookup(boss);

      if(bossperson == person.nullperson) {
        bossperson = person(boss);
        org.add(boss, bossperson);

        if(topdog == null) {
          topdog = bossperson;
        }
      }
      bossperson.addteammember(person);
    } else {
      topdog = person;
    }
  }

  // This is only for tests, ok?
  person lookup(string name) {
    return org.lookup(name);
  }
}

/******************************************************************************

Main

*******************************************************************************/

void processinput(string[] input, organisation org) {
  string arg;
  string[] parts;

  for(string arg: input) {
    parts = split(arg, "|");

    if(length(parts[0]) > 0) {
      string name = cleanse.escape(parts[0]);
      if(length(name) > 0) {
        string title = "";
        if(parts.length > 1) { title = cleanse.escape(parts[1]); }
        string boss = "";

        if(parts.length > 2 && length(parts[2]) > 0) {
          boss = cleanse.escape(parts[2]);
        }
        org.add(name, title, boss);
      }
    }
  }
}

struct orgchart {
  organisation org;
  page p;
  page drawer(string, string);

  private treerenderer treerendererfactory(page head) {
    return treerenderer(head);
  }

  void operator init(string[] input, page drawer(string, string)=drawcard) {
    processinput(input, org);
    this.drawer = drawcard;
  }

  void draw() {
    if(org.topdog != null) {
      p = org.topdog.draw(this.drawer, treerendererfactory);
    }
  }

  void draw(page p) {
    if(this.p.empty()) {
      draw();
    }
    add(p, this.p);
  }
}

void run(picture pic, string[] input) {
  page p = page(pic);
  orgchart orgchart = orgchart(input);
  orgchart.draw(p);
  p.print();
}
