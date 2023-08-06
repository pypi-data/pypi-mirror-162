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

// This is just a container for a function so we can
// reference it from multiple places and pass it around easily
// if we pass a function by itself it's passed by value

struct parampair {
  pair get();

  void operator init(pair get()) {
    this.get = get;
  }
}

// A high-level solver of anythign involving a single real value
// we expect many more of these for each data type that might be solved
// e.g. pair, path, etc

struct solvepair {
  void suggest(parampair pr);
}

// A specific solver (strategy)

struct solvepairmax {
  solvepair parent;
  int ordinal;
  parampair[] params;
  pair maxpair = (realMin, realMin);

  void suggest(parampair pr) {
    params.push(pr);
    pair suggestion = pr.get();
    if(suggestion.x > this.maxpair.x) { this.maxpair = (suggestion.x, maxpair.y) ; }
    if(suggestion.y > this.maxpair.y) { this.maxpair = (maxpair.x, suggestion.y) ; }

    if(this.params.length >= this.ordinal) {
      // Set all functions to point to anonymous that returns max;
      pair result() = new pair() { return maxpair ; } ;
      for(parampair param : this.params) {
        param.get = result;
      }
    }
  }

  void operator init(int ordinal) {
    this.ordinal = ordinal;
    // Inheritance
    this.parent.suggest = this.suggest;
  }
}

// Has to be castable to real solver so clients
// don't care what method the solver is using
solvepair operator cast(solvepairmax max) {return max.parent;}
