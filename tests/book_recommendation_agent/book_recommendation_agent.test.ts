// tests/book_recommendation_agent/book_recommendation_agent.test.ts
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { loadBooks } from '../../src/book_recommendation_agent/src/book_recommendation_agent';
import * as child_process from 'child_process';
import { EventEmitter } from 'events';

// 1. Mock child_process so we don't actually run Python
vi.mock('child_process', () => ({
  spawn: vi.fn(),
}));

describe('Book Recommendation Agent TS Tests', () => {
  
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('loadBooks()', () => {
    it('should resolve with parsed JSON when Python script succeeds', async () => {
      const mockBooks = { books: [{ title: 'Dune', author: 'Frank Herbert' }] };
      
      // Setup a mock process that acts like a real subprocess
      const mockProcess = new EventEmitter() as any;
      mockProcess.stdout = new EventEmitter();
      mockProcess.stderr = new EventEmitter();
      
      (child_process.spawn as any).mockReturnValue(mockProcess);

      const loadPromise = loadBooks('sci-fi');

      // Simulate Python outputting JSON data
      mockProcess.stdout.emit('data', Buffer.from(JSON.stringify(mockBooks)));
      // Simulate Python closing successfully
      mockProcess.emit('close', 0);

      const result = await loadPromise;
      expect(result).toEqual(mockBooks);
      expect(child_process.spawn).toHaveBeenCalledWith(
        expect.stringContaining('python'),
        expect.arrayContaining(['sci-fi']),
        expect.any(Object)
      );
    });

    it('should reject when the Python script returns invalid JSON', async () => {
      const mockProcess = new EventEmitter() as any;
      mockProcess.stdout = new EventEmitter();
      mockProcess.stderr = new EventEmitter();
      
      (child_process.spawn as any).mockReturnValue(mockProcess);

      const loadPromise = loadBooks('mystery');

      mockProcess.stdout.emit('data', Buffer.from('Not JSON!'));
      mockProcess.emit('close', 0);

      await expect(loadPromise).rejects.toThrow();
    });

    it('should reject with stderr message when Python script fails (exit code 1)', async () => {
      const mockProcess = new EventEmitter() as any;
      mockProcess.stdout = new EventEmitter();
      mockProcess.stderr = new EventEmitter();
      
      (child_process.spawn as any).mockReturnValue(mockProcess);

      const loadPromise = loadBooks('invalid');

      mockProcess.stderr.emit('data', Buffer.from('Module not found'));
      mockProcess.emit('close', 1);

      await expect(loadPromise).rejects.toThrow(/Module not found/);
    });
  });
});