#!/bin/bash

mkdir -p bin

# Compile https://github.com/EduardoVernier/greedy-insertion-treemap
javac -d bin $(find ./code/git -name "*.java")

# Compile sqr git https://github.com/EduardoVernier/squarified-git
javac -d bin $(find ./code/squarified-git -name "*.java")

