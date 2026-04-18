using System.Net.Http.Json;
using FileManager.Shared.Models;

namespace FileManager.Client.Services;

public class ClientLogService
{
    private readonly HttpClient _http;

    public ClientLogService(HttpClient http) => _http = http;

    public Task InfoAsync(string message, string? source = null) =>
        SendAsync("INFO", message, source);

    public Task WarnAsync(string message, string? source = null) =>
        SendAsync("WARN", message, source);

    public Task ErrorAsync(string message, string? source = null, string? stack = null) =>
        SendAsync("ERROR", message, source, stack);

    private async Task SendAsync(string level, string message, string? source, string? stack = null)
    {
        try
        {
            var entry = new ClientLogEntry(
                level, message, source, stack,
                DateTime.UtcNow.ToString("HH:mm:ss.fff"));
            await _http.PostAsJsonAsync("api/log/client", entry);
        }
        catch { /* never throw from logger */ }
    }
}
