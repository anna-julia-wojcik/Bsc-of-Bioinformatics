package filters.components;

import filters.core.AbstractFilter;
import filters.core.FilterNode;

public class Holder extends AbstractFilter {
    // data

    // technical
    public Holder(int value, FilterNode next) {
        super(value, next);
    }

    // operations
    @Override
    public FilterNode insert(int value) {
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