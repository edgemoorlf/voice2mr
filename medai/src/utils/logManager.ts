import fs from 'fs';
import path from 'path';

const LOG_DIR = process.env.LOG_DIR || path.join(process.cwd(), 'logs');

// Inline the needed functions from logger.ts to avoid import issues
function getLogStats() {
  const stats = {
    usageLogSize: 0,
    errorLogSize: 0,
    usageLogExists: false,
    errorLogExists: false,
    logDirectory: LOG_DIR
  };
  
  try {
    const usageLogFile = path.join(LOG_DIR, 'usage.log');
    const errorLogFile = path.join(LOG_DIR, 'error.log');
    
    if (fs.existsSync(usageLogFile)) {
      stats.usageLogExists = true;
      stats.usageLogSize = fs.statSync(usageLogFile).size;
    }
    
    if (fs.existsSync(errorLogFile)) {
      stats.errorLogExists = true;
      stats.errorLogSize = fs.statSync(errorLogFile).size;
    }
  } catch (error) {
    console.error('Error getting log stats:', error);
  }
  
  return stats;
}

function cleanOldLogs(daysToKeep: number = 30) {
  if (!fs.existsSync(LOG_DIR)) return;
  
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

function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

export function showLogStats(): void {
  console.log('📊 Log Statistics:');
  console.log('==================');
  
  const stats = getLogStats();
  console.log(`Log Directory: ${stats.logDirectory}`);
  console.log(`Usage Log: ${stats.usageLogExists ? formatBytes(stats.usageLogSize) : 'Not found'}`);
  console.log(`Error Log: ${stats.errorLogExists ? formatBytes(stats.errorLogSize) : 'Not found'}`);
  
  // Show all log files in directory
  try {
    if (!fs.existsSync(LOG_DIR)) {
      console.log('\nLog directory does not exist yet.');
      return;
    }
    
    const files = fs.readdirSync(LOG_DIR);
    const logFiles = files.filter(f => f.endsWith('.log') || f.includes('.log.'));
    
    if (logFiles.length > 0) {
      console.log('\nAll log files:');
      logFiles.forEach(file => {
        const filePath = path.join(LOG_DIR, file);
        const stats = fs.statSync(filePath);
        const size = stats.size;
        const modified = stats.mtime.toISOString().split('T')[0];
        console.log(`  ${file}: ${formatBytes(size)} (${modified})`);
      });
    } else {
      console.log('\nNo log files found.');
    }
  } catch (error) {
    console.error('Error reading log directory:', (error as Error).message);
  }
}

export function tailLogs(logType: 'usage' | 'error' = 'usage', lines: number = 50): void {
  const logFile = logType === 'error' 
    ? path.join(LOG_DIR, 'error.log')
    : path.join(LOG_DIR, 'usage.log');
  
  if (!fs.existsSync(logFile)) {
    console.log(`Log file not found: ${logFile}`);
    return;
  }
  
  console.log(`📝 Last ${lines} lines from ${logType} log:`);
  console.log('='.repeat(50));
  
  try {
    const content = fs.readFileSync(logFile, 'utf8');
    const logLines = content.trim().split('\n').filter(line => line.trim());
    const lastLines = logLines.slice(-lines);
    
    lastLines.forEach(line => {
      try {
        const parsed = JSON.parse(line);
        const timestamp = parsed.timestamp ? `[${parsed.timestamp}]` : '[No timestamp]';
        const endpoint = parsed.endpoint || parsed.page || 'N/A';
        const type = parsed.type || 'api';
        const typeIcon = type === 'page_access' ? '📄' : '🔗';
        
        console.log(`${timestamp} ${typeIcon} ${endpoint}`);
        if (parsed.type === 'page_access') {
          console.log(`  Page Access: ${parsed.page}`);
          console.log(`  Language: ${parsed.language || 'unknown'}`);
          console.log(`  IP: ${parsed.clientIP}`);
          console.log(`  Referer: ${parsed.referer}`);
        } else {
          console.log(`  ${JSON.stringify(parsed, null, 2)}`);
        }
        console.log('---');
      } catch {
        console.log(line); // If not JSON, print as-is
      }
    });
  } catch (error) {
    console.error('Error reading log file:', (error as Error).message);
  }
}

export function cleanLogs(days: number = 30): void {
  console.log(`🧹 Cleaning logs older than ${days} days...`);
  cleanOldLogs(days);
  console.log('Log cleanup completed.');
}

// CLI interface - only run if this file is executed directly
function main() {
  const command = process.argv[2];
  const arg = process.argv[3];

  switch (command) {
    case 'stats':
      showLogStats();
      break;
    case 'tail':
      const logType = (arg === 'error' || arg === 'usage') ? arg : 'usage';
      const lines = parseInt(process.argv[4]) || 50;
      tailLogs(logType, lines);
      break;
    case 'clean':
      const days = parseInt(arg) || 30;
      cleanLogs(days);
      break;
    case 'help':
    default:
      console.log('📊 Voice2MR Log Management');
      console.log('Usage: npm run logs <command> [options]');
      console.log('');
      console.log('Commands:');
      console.log('  stats                 Show log file statistics');
      console.log('  tail [usage|error] [lines]  Show recent log entries (default: usage, 50 lines)');
      console.log('  clean [days]         Clean logs older than N days (default: 30)');
      console.log('  help                 Show this help message');
      console.log('');
      console.log('Examples:');
      console.log('  npm run logs stats');
      console.log('  npm run logs tail usage 100');
      console.log('  npm run logs tail error');
      console.log('  npm run logs clean 7');
      break;
  }
}

// Check if this module is being run directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main();
}