using System.Collections.Concurrent;

namespace FileManager.Server.Services;

public interface IOtpService
{
    string Generate(string email);
    bool Verify(string email, string code);
}

public class OtpService : IOtpService, IHostedService, IDisposable
{
    private record OtpEntry(string Code, DateTime Expiry, int Failures);

    private readonly ConcurrentDictionary<string, OtpEntry> _store = new(StringComparer.OrdinalIgnoreCase);
    private readonly ILogger<OtpService> _logger;
    private Timer? _cleanupTimer;

    private const int ExpiryMinutes = 10;
    private const int MaxFailures   = 5;

    public OtpService(ILogger<OtpService> logger) => _logger = logger;

    public string Generate(string email)
    {
        var code = Random.Shared.Next(100000, 999999).ToString();
        _store[email] = new OtpEntry(code, DateTime.UtcNow.AddMinutes(ExpiryMinutes), 0);
        _logger.LogInformation("OTP generated for {Email}", email);
        return code;
    }

    public bool Verify(string email, string code)
    {
        if (!_store.TryGetValue(email, out var entry))
            return false;

        if (DateTime.UtcNow > entry.Expiry)
        {
            _store.TryRemove(email, out _);
            return false;
        }

        if (entry.Failures >= MaxFailures)
        {
            _store.TryRemove(email, out _);
            return false;
        }

        if (!entry.Code.Equals(code, StringComparison.Ordinal))
        {
            _store[email] = entry with { Failures = entry.Failures + 1 };
            return false;
        }

        // Valid — consume immediately (one-time use)
        _store.TryRemove(email, out _);
        return true;
    }

    // Background cleanup of expired entries
    public Task StartAsync(CancellationToken _)
    {
        _cleanupTimer = new Timer(_ =>
        {
            var now = DateTime.UtcNow;
            foreach (var key in _store.Keys)
                if (_store.TryGetValue(key, out var e) && now > e.Expiry)
                    _store.TryRemove(key, out OtpEntry? _);
        }, null, TimeSpan.FromMinutes(1), TimeSpan.FromMinutes(1));
        return Task.CompletedTask;
    }

    public Task StopAsync(CancellationToken _) { _cleanupTimer?.Change(Timeout.Infinite, 0); return Task.CompletedTask; }
    public void Dispose() => _cleanupTimer?.Dispose();
}
