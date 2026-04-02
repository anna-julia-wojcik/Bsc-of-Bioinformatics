package filters.components;

import filters.core.AbstractFilter;
import filters.core.FilterNode;

public class Sieve extends AbstractFilter {
    // data

    // technical
    public Sieve(int value, FilterNode next) {
        super(value, next);
    }

    // operations
    @Override
    public FilterNode insert(int value) {
        // If value % this.value == 0, it means a divisor exists - do not pass it further
        if (value % this.value != 0 && next != null) {
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