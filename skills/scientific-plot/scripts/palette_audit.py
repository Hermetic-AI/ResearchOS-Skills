#!/usr/bin/env python3
"""Audit palette contrast against white/black and pairwise RGB separation."""
from __future__ import annotations
import argparse,json,math,sys
VERSION="0.1.0"
def hexrgb(value):
 value=value.lstrip('#')
 if len(value)!=6: raise ValueError(f"invalid hex color: {value}")
 return tuple(int(value[i:i+2],16)/255 for i in (0,2,4))
def linear(v): return v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4
def lum(rgb): return .2126*linear(rgb[0])+.7152*linear(rgb[1])+.0722*linear(rgb[2])
def contrast(a,b): return (max(a,b)+.05)/(min(a,b)+.05)
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--colors',required=True,help='comma-separated #RRGGBB values');p.add_argument('--version',action='version',version=f'%(prog)s {VERSION}');a=p.parse_args(argv)
 try:
  colors=[x.strip() for x in a.colors.split(',') if x.strip()]
  if len(colors)<2: raise ValueError('supply at least two colors')
  rgb=[hexrgb(x) for x in colors]; ls=[lum(x) for x in rgb]
  pairs=[{"colors":[colors[i],colors[j]],"rgb_distance":round(math.dist(rgb[i],rgb[j]),3)} for i in range(len(colors)) for j in range(i)]
  print(json.dumps({"colors":colors,"contrast_on_white":[round(contrast(x,1),2) for x in ls],"contrast_on_black":[round(contrast(x,0),2) for x in ls],"minimum_pairwise_rgb_distance":min(x['rgb_distance'] for x in pairs),"pairwise":pairs,"warnings":["WCAG contrast applies to text/background pairs, not a complete categorical-series check.","Inspect grayscale and color-vision-deficiency simulations before submission."]},indent=2));return 0
 except ValueError as e: print(f'error: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
