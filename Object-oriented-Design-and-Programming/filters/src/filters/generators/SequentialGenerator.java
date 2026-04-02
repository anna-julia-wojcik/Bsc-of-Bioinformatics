package filters.generators;

import filters.core.AbstractFilter;
import filters.core.FilterNode;

public class SequentialGenerator extends AbstractFilter {
    // data
    private int current;

    // technical
    public SequentialGenerator(int start, FilterNode next) {
        super(next);
        this.current = start;
    }

    // operations
    @Override
    public FilterNode insert(int ignored) {
        if (next != null) {
            // Insert a number one greater than the current one
            next = next.insert(current++);
        }
        return this;
    }
}