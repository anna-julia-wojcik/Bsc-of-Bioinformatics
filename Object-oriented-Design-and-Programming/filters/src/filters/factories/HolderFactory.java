package filters.factories;

import filters.components.Holder;
import filters.core.AbstractFilter;
import filters.core.FilterNode;

public class HolderFactory extends AbstractFilter {
    // data

    // technical
    public HolderFactory() {
        super(null);
    }

    // operations
    @Override
    public FilterNode insert(int value) {
        return new Holder(value, this);
    }
}