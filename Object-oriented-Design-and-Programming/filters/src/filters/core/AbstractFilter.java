package filters.core;

public abstract class AbstractFilter implements FilterNode {
    // data
    protected FilterNode next;
    protected int value;

    // technical

    // constructor for generators and producers (factories)
    public AbstractFilter(FilterNode next) {
        this.next = next;
    }

    // constructor for regular filters
    public AbstractFilter(int value, FilterNode next) {
        this.value = value;
        this.next = next;
    }

    // operations
    @Override
    public abstract FilterNode insert(int value);

    @Override
    public void print() {
        // Pass the number to the next filter if it exists
        if (next != null) {
            next.print();
        } else {
            System.out.println();
        }
    }
}