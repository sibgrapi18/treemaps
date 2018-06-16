# treemaps

This repository hosts the resources used in the paper *A Stable Greedy Insertion Treemap Algorithm for
Software Evolution Visualization*, submited to SIBGRAPI 2018.

`code` contains the implementations of GIT and Squarified GIT. To compile the code type `./compile.sh` in the
console from the repository root. To run the code, that is, generate the csv with the rectangles, 
run `./treemaps.sh <input_dir> <width> <height> <output_dir>`. Ex.: `./treemaps.sh datasets/bdb 1000 1000 output`

_TODO: add video generation instructions_

`datasets` holds the 28 datasets of software development origin that were used for the evaluation of the treemapping techniques. More information about the datasets
can be found in the paper.

Videos of the executions can be found at: https://www.youtube.com/playlist?list=PLy5Y4CMtJ7mKaUBrSZ3YgwrFYBb3xNpHg

![](https://j.gifs.com/l5yoWM.gif)

Lastly, `figures` holds all the visualizations generated for all datasets. This includes
all the figures that couldn't make it into the paper for lack of space.
