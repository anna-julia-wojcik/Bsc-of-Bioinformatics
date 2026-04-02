public class Main {
    public static void printTriangle(int n) {
        // Create an array to store the digits of each row of the triangle
        // (n+1 because the row lengthens with each level)
        int[] row = new int[n + 1];

        // The first element of the row is always one
        row[0] = 1;
        String stars = "  ******* ";

        // Iterate over the number of rows provided by the user
        for (int i = 0; i <= n; i++) {
            // Print the iteration number at the beginning of the line, format to two spaces
            System.out.format("%2d", i);
            System.out.print(":");

            // Iterate through each element in the 'row' array
            for (int j = 0; j <= i; j++) {
                // If the value is -1, it means a calculation error (integer overflow)
                if (row[j] == -1) {
                    System.out.print(stars);
                } else {
                    // Format the number to eleven spaces
                    System.out.format("%11d", row[j]);
                }
            }

            System.out.println();

            // If the loop hasn't gone out of the array's index bounds
            if (i < n) {
                // Set the last element of the new row to 1
                row[i + 1] = 1;

                for (int j = i; j > 0; j--) {
                    // Remember information about numbers from the previous row
                    int leftValue = row[j - 1];
                    int rightValue = row[j];

                    // If either value is invalid, the result is also invalid
                    if (leftValue == -1 || rightValue == -1) {
                        row[j] = -1;
                    } else {
                        int sum = leftValue + rightValue;
                        // If the sum exceeds the int bounds, the sum is invalid
                        if (sum < 0) {
                            row[j] = -1;
                        } else {
                            // Assign the sum of the neighboring numbers from the previous row to the index in the new row
                            row[j] = sum;
                        }
                    }
                }
            }
        }
    }

    public static void main(String[] args) {
        // Check the number of arguments
        assert args.length == 1 : "Exactly one argument is required";

        // Convert the string to a number and check its validity
        int n = Integer.parseInt(args[0]);
        assert n >= 0 : "The provided number of Pascal's triangle levels must be non-negative";

        // Print the triangle
        printTriangle(n);
    }
}