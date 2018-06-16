#!/bin/bash

# This script works for one dataset at a time
# To run for all datasets inside a folder do the following:
# for dataset in $(find dataset/* -maxdepth 0 -type d); do ./treemaps.sh $dataset 1000 1000 output; done
# output folder must exist

print_invalid_usage(){
  echo "usage: ./treemaps.sh -input_dir -width -height -output_dir"
  echo "example: ./treemaps.sh dataset/exo 1000 1000 output"
}

check_args(){
  # Check number of arguments
  if [ $# -ne 4 ] ; then
    echo "Wrong number of arguments"
    print_invalid_usage
    exit
  fi

  # Check if input_dir exists
  if [ ! -d $1 ] ; then
    echo $1
    echo "Invalid input_dir"
    print_invalid_usage
    exit
  fi

  # Check if width and height are positive numbers
  re='^[0-9]+$'
  if ! [[ $2 =~ $re ]] ; then
     echo "Width is not a number"
     print_invalid_usage
     exit
  fi

  if ! [[ $3 =~ $re ]] ; then
     echo "Height is not a number"
     print_invalid_usage
     exit
  fi
}


check_args $*
input_dir=$1
width=$2
height=$3
output_dir=$4
dataset_name=$(basename $input_dir) # Extract dataset name -- end of path
input_dir=$(readlink -f $input_dir) # Get absolute path in case it isn't already
output_dir=$(readlink -f $output_dir) 

date >> log
echo $* >> log

# If running on SSH need to set window parameters
export DISPLAY=:0.0

# Run new technique - Greedy Insertion Treemap
complete_output_dir="$output_dir""/git/""$dataset_name"
date|awk '{print $4}'
echo $complete_output_dir
java -cp ./bin com.eduardovernier.Main $input_dir $width $height $complete_output_dir &> /dev/null

# Run Greedy Insertion Treemap with Squarified Initialization
complete_output_dir="$output_dir""/sqrgit/""$dataset_name"
date|awk '{print $4}'
echo $complete_output_dir
java -cp ./bin com.ufrgs.Main $input_dir $width $height $complete_output_dir
