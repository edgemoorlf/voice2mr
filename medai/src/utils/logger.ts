import fs from 'fs';
import path from 'path';

// Configure log directory and files
const LOG_DIR = process.env.LOG_DIR || path.join(process.cwd(), 'logs');
const USAGE_LOG_FILE = path.join(LOG_DIR, 'usage.log');
const ERROR_LOG_FILE = path.join(LOG_DIR, 'error.log');
const MAX_LOG_SIZE = 10 * 1024 * 1024; // 10MB
const MAX_LOG_FILES = 5;

// Ensure log directory exists
function ensureLogDir() {
  if (!fs.existsSync(LOG_DIR)) {
    fs.mkdirSync(LOG_DIR, { recursive: true });
  }
}

// Rotate log file if it's too large
function rotateLogFile(filePath: string) {
  if (!fs.existsSync(filePath)) return;
  
  const stats = fs.statSync(filePath);
  if (stats.size < MAX_LOG_SIZE) return;
  
  // Rotate existing files (file.1.log -> file.2.log, etc.)
  for (let i = MAX_LOG_FILES - 1; i >= 1; i--) {
    const oldFile = `${filePath}.${i}`;
    const newFile = `${filePath}.${i + 1}`;
    if (fs.existsSync(oldFile)) {
      if (i === MAX_LOG_FILES - 1) {
        fs.unlinkSync(oldFile); // Delete oldest
      } else {
        fs.renameSync(oldFile, newFile);
      }
    }
  }
  
  // Move current log to .1
  fs.renameSync(filePath, `${filePath}.1`);
}

// Write log entry to file
function writeLogToFile(filePath: string, logData: any) {
  try {
    ensureLogDir();
    rotateLogFile(filePath);
    
    const logEntry = JSON.stringify({
      timestamp: new Date().toISOString(),
      ...logData
    }) + '\n';
    
    fs.appendFileSync(filePath, logEntry);
  } catch (error) {
    // Fallback to console if file logging fails
    console.error('Failed to write to log file:', error);
    console.log('Original log data:', logData);
  }
}

// Usage tracking logger
export function logUsageToFile(data: any) {
  // Also log to console for immediate visibility
  console.log('📊 [USAGE-TRACKING]', data);
  
  // Write to usage log file
  writeLogToFile(USAGE_LOG_FILE, {
    type: 'usage',
    ...data
  });
}

// Error logger
export function logErrorToFile(data: any) {
  // Also log to console for immediate visibility
  console.error('❌ [ERROR-TRACKING]', data);
  
  // Write to error log file
  writeLogToFile(ERROR_LOG_FILE, {
    type: 'error',
    ...data
  });
}

// Get log statistics
export function getLogStats() {
  ensureLogDir();
  
  const stats = {
    usageLogSize: 0,
    errorLogSize: 0,
    usageLogExists: false,
    errorLogExists: false,
    logDirectory: LOG_DIR
  };
  
  try {
    if (fs.existsSync(USAGE_LOG_FILE)) {
      stats.usageLogExists = true;
      stats.usageLogSize = fs.statSync(USAGE_LOG_FILE).size;
    }
    
    if (fs.existsSync(ERROR_LOG_FILE)) {
      stats.errorLogExists = true;
      stats.errorLogSize = fs.statSync(ERROR_LOG_FILE).size;
    }
  } catch (error) {
    console.error('Error getting log stats:', error);
  }
  
  return stats;
}

// Clean old log files (utility function)
export function cleanOldLogs(daysToKeep: number = 30) {
  ensureLogDir();
  const cutoffTime = Date.now() - (daysToKeep * 24 * 60 * 60 * 1000);
  
  try {
    const files = fs.readdirSync(LOG_DIR);
    files.forEach(file => {
      const filePath = path.join(LOG_DIR, file);
      const stats = fs.statSync(filePath);
      
      if (stats.mtime.getTime() < cutoffTime) {
        fs.unlinkSync(filePath);
        console.log(`Cleaned old log file: ${file}`);
      }
    });
  } catch (error) {
    console.error('Error cleaning old logs:', error);
  }
}