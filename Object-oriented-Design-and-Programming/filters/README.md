# Filter Sequences - Java

## Project Description
A Java program implementing a dynamic sequence of filters (based on the Pipes and Filters / Chain of Responsibility design patterns). The system processes a stream of integers through different types of nodes:
- **Generators:** Produce sequences of consecutive or random numbers.
- **Factories (Producers):** Dynamically create and attach new filters to the sequence based on received values.
- **Components (Regular Filters):** Store, evaluate, swap, or drop numbers to achieve specific mathematical results (e.g., Sieve of Eratosthenes, sorting, or shuffling).

## Task description and requirements
[Task description (polish)](https://github.com/anna-julia-wojcik/Bsc-of-Bioinformatics/blob/main/Object-oriented-Design-and-Programming/Filters/task_requirements.txt)

## Project Structure

The project has been refactored into a logical package structure within the `filters` module:

### 1. `Test.java` (Main)
- The main entry point of the program.
- Contains pre-defined test chains: consecutive numbers, random permutations, Sieve of Eratosthenes, and random number sorting.

### 2. `core/`
- `FilterNode.java` & `AbstractFilter.java`: Define the contract and base logic for inserting values and printing the state of the sequence.

### 3. `generators/`
- `SequentialGenerator.java`, `RandomGenerator.java`: Generate initial numbers for the pipeline.

### 4. `factories/`
- `SieveFactory.java`, `SorterFactory.java`, `ShufflerFactory.java`, `HolderFactory.java`: Act as producers that dynamically instantiate and append new filters to the chain.

### 5. `components/`
- `Sieve.java`, `Sorter.java`, `Shuffler.java`, `Holder.java`: Process, compare, or filter the numbers passing through the chain.

## Requirements

- Java Development Kit (JDK) 8 or newer.

## How to Run the Program

Open a terminal, navigate to the `src` directory (or wherever your root `filters` folder is located), compile the files, and run the main test class:

```bash
cd src

# Compile all java files in the package and sub-packages (Linux/GitBash)
find . -name "*.java" > sources.txt
javac @sources.txt

# Run the program
java filters.Test
```
