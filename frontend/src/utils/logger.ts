/**
 * Logging utility for frontend application
 * Supports structured logging with levels and can be disabled in production
 */

export enum LogLevel {
  DEBUG = 0,
  INFO = 1,
  WARN = 2,
  ERROR = 3,
  NONE = 4,
}

class Logger {
  private level: LogLevel;
  private enabled: boolean;

  constructor() {
    // Determine log level from environment or default to INFO in production, DEBUG in development
    const envLevel = import.meta.env.VITE_LOG_LEVEL?.toUpperCase();
    this.level = envLevel ? (LogLevel[envLevel as keyof typeof LogLevel] ?? LogLevel.INFO) : 
      (import.meta.env.DEV ? LogLevel.DEBUG : LogLevel.INFO);
    
    // Can be disabled entirely via environment variable
    this.enabled = import.meta.env.VITE_LOGGING_ENABLED !== 'false';
  }

  private shouldLog(level: LogLevel): boolean {
    return this.enabled && level >= this.level;
  }

  private formatMessage(level: string, message: string, ...args: any[]): string {
    const timestamp = new Date().toISOString();
    return `[${timestamp}] [${level}] ${message}`;
  }

  debug(message: string, ...args: any[]): void {
    if (this.shouldLog(LogLevel.DEBUG)) {
      console.debug(this.formatMessage('DEBUG', message), ...args);
    }
  }

  info(message: string, ...args: any[]): void {
    if (this.shouldLog(LogLevel.INFO)) {
      console.info(this.formatMessage('INFO', message), ...args);
    }
  }

  warn(message: string, ...args: any[]): void {
    if (this.shouldLog(LogLevel.WARN)) {
      console.warn(this.formatMessage('WARN', message), ...args);
    }
  }

  error(message: string, error?: Error | unknown, ...args: any[]): void {
    if (this.shouldLog(LogLevel.ERROR)) {
      const errorDetails = error instanceof Error 
        ? { message: error.message, stack: error.stack, name: error.name }
        : error;
      console.error(this.formatMessage('ERROR', message), errorDetails, ...args);
    }
  }
}

// Export singleton instance
export const logger = new Logger();

// Export convenience functions
export const logDebug = (message: string, ...args: any[]) => logger.debug(message, ...args);
export const logInfo = (message: string, ...args: any[]) => logger.info(message, ...args);
export const logWarn = (message: string, ...args: any[]) => logger.warn(message, ...args);
export const logError = (message: string, error?: Error | unknown, ...args: any[]) => 
  logger.error(message, error, ...args);

