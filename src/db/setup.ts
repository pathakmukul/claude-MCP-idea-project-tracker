import sqlite3 from 'sqlite3';
import { open } from 'sqlite';
import fs from 'fs/promises';
import path from 'path';

async function setupDatabase() {
  try {
    // Ensure data directory exists
    await fs.mkdir(path.join(process.cwd(), 'data'), { recursive: true });
    
    // Read schema file
    const schema = await fs.readFile(
      path.join(process.cwd(), 'src', 'db', 'schema.sql'), 
      'utf-8'
    );
    
    // Open database connection
    const db = await open({
      filename: path.join(process.cwd(), 'data', 'project_tracker.db'),
      driver: sqlite3.Database
    });
    
    // Execute schema
    await db.exec(schema);
    
    console.log('Database setup completed successfully!');
    await db.close();
  } catch (error) {
    console.error('Error setting up database:', error);
    process.exit(1);
  }
}

setupDatabase(); 
