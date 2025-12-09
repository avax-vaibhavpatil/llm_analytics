/**
 * Generate mock data for report preview and final reports
 * @param {Array<string>} columns - Array of column names
 * @param {number} rowCount - Number of rows to generate
 * @returns {Array<Object>} - Array of row objects
 */
export const generateMockData = (columns, rowCount = 10) => {
  const mockData = [];
  const columnNames = columns.map(col => typeof col === 'string' ? col : col.name);

  for (let i = 0; i < rowCount; i++) {
    const row = {};
    columnNames.forEach(col => {
      const colLower = col.toLowerCase();
      
      // Generate appropriate mock data based on column name patterns
      if (colLower.includes('id')) {
        row[col] = `ID${1000 + i}`;
      } 
      else if (colLower.includes('mrr') || colLower.includes('arr')) {
        row[col] = `$${(Math.floor(Math.random() * 2000) + 500).toFixed(2)}`;
      }
      else if (colLower.includes('amount') || colLower.includes('revenue') || colLower.includes('price') || colLower.includes('total')) {
        row[col] = `$${(Math.floor(Math.random() * 5000) + 100).toFixed(2)}`;
      }
      else if (colLower.includes('industry') || colLower.includes('sector')) {
        row[col] = ['Technology', 'Finance', 'Retail', 'Healthcare', 'Manufacturing'][i % 5];
      }
      else if (colLower.includes('date') || colLower.includes('created') || colLower.includes('signup') || colLower.includes('joined')) {
        const date = new Date(2024, Math.floor(Math.random() * 12), Math.floor(Math.random() * 28) + 1);
        row[col] = date.toISOString().split('T')[0];
      }
      else if (colLower.includes('name')) {
        if (colLower.includes('company') || colLower.includes('customer')) {
          row[col] = `Company ${i + 1}`;
        } else if (colLower.includes('product')) {
          row[col] = `Product ${i + 1}`;
        } else {
          row[col] = `Name ${i + 1}`;
        }
      }
      else if (colLower.includes('email')) {
        row[col] = `user${i + 1}@example.com`;
      }
      else if (colLower.includes('country')) {
        row[col] = ['USA', 'Canada', 'UK', 'Germany', 'France', 'Australia', 'India', 'Japan'][i % 8];
      }
      else if (colLower.includes('status')) {
        row[col] = ['Active', 'Pending', 'Completed', 'Cancelled'][i % 4];
      }
      else if (colLower.includes('segment') || colLower.includes('category')) {
        row[col] = ['Enterprise', 'SMB', 'Startup'][i % 3];
      }
      else if (colLower.includes('count') || colLower.includes('quantity')) {
        row[col] = Math.floor(Math.random() * 100) + 1;
      }
      else if (colLower.includes('rating') || colLower.includes('score')) {
        row[col] = (Math.random() * 5).toFixed(1);
      }
      else if (colLower.includes('phone')) {
        row[col] = `+1-555-${String(Math.floor(Math.random() * 9000) + 1000)}`;
      }
      else if (colLower.includes('description') || colLower.includes('comment')) {
        row[col] = `Sample description for item ${i + 1}`;
      }
      else {
        // Default fallback for unknown column types
        row[col] = `Value ${i + 1}`;
      }
    });
    mockData.push(row);
  }

  return mockData;
};

