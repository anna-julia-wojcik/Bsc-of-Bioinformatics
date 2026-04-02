package filters;

import filters.core.FilterNode;
import filters.factories.HolderFactory;
import filters.factories.ShufflerFactory;
import filters.factories.SieveFactory;
import filters.factories.SorterFactory;
import filters.generators.RandomGenerator;
import filters.generators.SequentialGenerator;

public class Test {

    public void runTest(int count, FilterNode g) {
        for (int i = 1; i <= count; i++) {
            // For the generator, the value of the insert argument doesn't matter
            g.insert(0);  
        }
        g.print();
    }

    public static void runAllTests() {

        final int max = 10;
        Test t = new Test();

        System.out.println("Print consecutive numbers 0.." + (max - 1));
        t.runTest(max, new SequentialGenerator(0, new HolderFactory()));

        System.out.println("Print a fairly random permutation of numbers 0.." + (max - 1));
        t.runTest(max, new SequentialGenerator(0, new ShufflerFactory()));

        System.out.println("Sieve of Eratosthenes for numbers 0..100");
        t.runTest(100 - 1, new SequentialGenerator(2, new SieveFactory()));

        System.out.println("Sort random numbers in the range 0..100");
        t.runTest(max, new RandomGenerator(100, new SorterFactory()));

    }

    public static void main(String[] args) {
        runAllTests();
    }
}