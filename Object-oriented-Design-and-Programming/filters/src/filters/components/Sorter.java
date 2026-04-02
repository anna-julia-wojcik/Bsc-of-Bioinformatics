package filters.components;

import filters.core.AbstractFilter;
import filters.core.FilterNode;

public class Sorter extends AbstractFilter {
    // data

    // technical
    public Sorter(int value, FilterNode next) {
        super(value, next);
    }

    // operations
    @Override
    public FilterNode insert(int value) {
        // If the new number is smaller than the stored one, swap them
        if (value < this.value) {
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
        System.out.print(this.value + " ");
        super.print();
    }
}