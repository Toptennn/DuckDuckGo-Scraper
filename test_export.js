// Test script to verify CSV and Excel export functionality

// Mock data with the new structure (url field instead of href)
const mockResults = [
  {
    title: "Test Article 1",
    url: "https://example.com/article1",
    description: "This is a test description",
    published_date: "2025-01-01",
  },
  {
    title: "Test Article 2", 
    url: "https://example.com/article2",
    description: "Another test description",
    published_date: "2025-01-02",
  }
];

// Test CSV export (should not include Description column)
const csvData = mockResults.map(result => ({
  Title: result.title || '',
  URL: result.url || '',
  'Post Date': result.date || result.post_date || result.published_date || '',
}));

console.log("CSV Export Data:");
console.log(csvData);

// Test Excel export (should not include Description and Domain columns)
const excelData = mockResults.map(result => ({
  Title: result.title || '',
  URL: result.url || '',
  'Post Date': result.date || result.post_date || result.published_date || '',
}));

console.log("\nExcel Export Data:");
console.log(excelData);

// Test URL field access
console.log("\nURL Field Test:");
mockResults.forEach((result, index) => {
  console.log(`Result ${index + 1}:`);
  console.log(`  Title: ${result.title}`);
  console.log(`  URL: ${result.url}`);
  console.log(`  Domain: ${result.url ? new URL(result.url).hostname : 'No URL'}`);
});
