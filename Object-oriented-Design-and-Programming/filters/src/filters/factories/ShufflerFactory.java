package filters.factories;

import filters.components.Shuffler;
import filters.core.AbstractFilter;
import filters.core.FilterNode;

public class ShufflerFactory extends AbstractFilter {
    // data

    // technical
    public ShufflerFactory() {
        super(null);
    }

    // operations
    @Override
    public FilterNode insert(int value) {
        return new Shuffler(value, this);
    }
}