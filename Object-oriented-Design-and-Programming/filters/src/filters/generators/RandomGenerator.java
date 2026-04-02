package filters.generators;

import filters.core.AbstractFilter;
import filters.core.FilterNode;
import java.util.Random;

public class RandomGenerator extends AbstractFilter {
    // data
    private int range;
    private Random random = new Random();

    // technical
    public RandomGenerator(int range, FilterNode next) {
        super(next);
        this.range = range;
    }

    // operations
    @Override
    public FilterNode insert(int ignored) {
        if (next != null) {
            // Add a random integer from the given range
            next = next.insert(random.nextInt(range));
        }
        return this;
    }
}