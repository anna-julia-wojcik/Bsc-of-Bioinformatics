package filters.components;

import filters.core.AbstractFilter;
import filters.core.FilterNode;
import java.util.Random;

public class Shuffler extends AbstractFilter {
    // data
    private Random random = new Random();

    // technical
    public Shuffler(int value, FilterNode next) {
        super(value, next);
    }

    // operations
    @Override
    public FilterNode insert(int value) {
        // nextBoolean() returns True/False with a 1/2 probability, so on True, shuffle
        if (random.nextBoolean()) {
            int temp = this.value;
            this.value = value;
            value = temp;
        }
        if (next != null) {
            next = next.insert(value);
        }
        return this;
    }

    @Override
    public void print() {
        System.out.print(value + " ");
        super.print();
    }
}