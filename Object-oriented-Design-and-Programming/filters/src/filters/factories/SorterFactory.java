package filters.factories;

import filters.components.Sorter;
import filters.core.AbstractFilter;
import filters.core.FilterNode;

public class SorterFactory extends AbstractFilter {
    // data

    // technical
    public SorterFactory() {
        super(null);
    }

    // operations
    @Override
    public FilterNode insert(int value) {
        return new Sorter(value, this);
    }
}