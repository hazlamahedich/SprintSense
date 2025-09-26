import { renderHook } from '@testing-library/react';
import { useRedisCache } from '../useRedisCache';

describe('useRedisCache', () => {
  it('provides a Redis cache interface', () => {
    const { result } = renderHook(() => useRedisCache());

    expect(result.current.cache).toBeDefined();
    expect(result.current.cache.get).toBeDefined();
    expect(result.current.cache.set).toBeDefined();
    expect(result.current.cache.warmup).toBeDefined();
    expect(result.current.error).toBeNull();
    expect(result.current.isConnected).toBeDefined();
  });

  it('returns null for get requests (mock implementation)', async () => {
    const { result } = renderHook(() => useRedisCache());

    const value = await result.current.cache.get('test-key');

    expect(value).toBeNull();
  });

  it('successfully executes set requests (mock implementation)', async () => {
    const { result } = renderHook(() => useRedisCache());

    await expect(result.current.cache.set('test-key', {
      title: 'Test Title',
      confidence: 0.9,
      metadata: {
        tokensUsed: 100,
        model: 'test',
        cacheHit: false
      }
    })).resolves.toBeUndefined();
  });

  it('successfully executes warmup requests (mock implementation)', async () => {
    const { result } = renderHook(() => useRedisCache());

    await expect(result.current.cache.warmup('test-category')).resolves.toBeUndefined();
  });
});
