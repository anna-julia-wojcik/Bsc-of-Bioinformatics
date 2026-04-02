package filters.factories;

import filters.components.Sieve;
import filters.core.AbstractFilter;
import filters.core.FilterNode;

public class SieveFactory extends AbstractFilter {
    // data

    // technical
    public SieveFactory() {
        super(null);
    }

    // operations
    @Override
    public FilterNode insert(int value) {
        return new Sieve(value, this);
    }
}