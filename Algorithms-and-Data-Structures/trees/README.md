# Longest Alternating Path in Binary Tree - Python

## Project Description
A Python implementation of a binary tree structure where each node holds a specific color (Black 'B' or White 'W'). The primary goal of this project is to calculate and extract the longest alternating-color path (e.g., Black -> White -> Black) starting from the root down to the leaves. 

## My Contribution
This project was developed in a pair-programming setup. **My specific responsibility was designing and implementing the path-finding logic.** I wrote the `find_longest_alt_path` methods across all classes (`RegBinTree`, `RegBinNode`, and `Leaf`), which handle the recursive traversal, path comparison, and extraction of the correct sequence of nodes.

## Project Structure
- `main.py` - Contains the implementation of the core classes:
  - `Leaf`: Represents the end nodes of the tree.
  - `RegBinNode`: Represents the internal nodes containing color data and references to children.
  - `RegBinTree`: The main wrapper class managing the root and triggering the path calculations.

## Requirements
- Python 3.10 or newer (due to modern type hinting syntax like `X | Y`).

## How to Run the Project
Open a terminal, navigate to the project directory, and run the script:
```bash
python3 main.py
```
