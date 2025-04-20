public static void main(String[] args) {
    // Default flag values.
    String endpoint = "";
    boolean debug = false;

    List<IndexInfo> data = null;
    try {
        if (debug) {
            data = getDataFromFile("indexes.json");
        } else {
            data = getDataFromServer(endpoint, days);
        }
    } catch (Exception e) {
        System.err.println("Error reading data: " + e.getMessage());
        e.printStackTrace();
        System.exit(1);
    }

    printLargestIndexes(data);
    printMostShards(data);
    printLeastBalanced(data);
}
