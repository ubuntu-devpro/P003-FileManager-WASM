using System.Net.Http.Json;
using Microsoft.JSInterop;

namespace FileManager.Client.Services;

public class AuthState
{
    public string? Email { get; set; }
    public bool IsAdmin { get; set; }
    public string? Domain { get; set; }
    public string? Token { get; set; }
    public bool IsAuthenticated => !string.IsNullOrEmpty(Token);
}

public interface IAuthService
{
    AuthState State { get; }
    Task<bool> LoginAsync(string email, string password);
    Task<(bool ok, string message)> RequestOtpAsync(string email);
    Task<bool> VerifyOtpAsync(string email, string code);
    Task LogoutAsync();
    Task CheckSessionAsync();
    event Action? StateChanged;
}

public class AuthService : IAuthService
{
    private readonly HttpClient _http;
    private readonly IJSRuntime _js;
    public AuthState State { get; private set; } = new();
    public event Action? StateChanged;

    public AuthService(HttpClient http, IJSRuntime js)
    {
        _http = http;
        _js = js;
    }

    public async Task CheckSessionAsync()
    {
        try
        {
            var token = await _js.InvokeAsync<string?>("localStorage.getItem", "fm_token");
            if (!string.IsNullOrEmpty(token))
            {
                State.Token = token;
                _http.DefaultRequestHeaders.Authorization =
                    new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", token);

                var resp = await _http.GetAsync("api/auth/session");
                if (resp.IsSuccessStatusCode)
                {
                    var session = await resp.Content.ReadFromJsonAsync<SessionResult>();
                    if (session != null)
                    {
                        State.Email = session.Email;
                        State.IsAdmin = session.IsAdmin;
                        State.Domain = session.Domain;
                    }
                }
            }
        }
        catch { }
        StateChanged?.Invoke();
    }

    public async Task<bool> LoginAsync(string email, string password)
    {
        try
        {
            var resp = await _http.PostAsJsonAsync("api/auth/login", new { email, password });
            if (!resp.IsSuccessStatusCode)
                return false;

            var json = await resp.Content.ReadFromJsonAsync<LoginResult>();
            if (json == null || !json.Success || string.IsNullOrEmpty(json.Token))
                return false;

            State.Token = json.Token;
            State.Email = json.Email;
            State.IsAdmin = json.IsAdmin;
            State.Domain = json.Domain;

            await _js.InvokeVoidAsync("localStorage.setItem", "fm_token", json.Token);
            _http.DefaultRequestHeaders.Authorization =
                new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", json.Token);

            StateChanged?.Invoke();
            return true;
        }
        catch
        {
            return false;
        }
    }

    public async Task<(bool ok, string message)> RequestOtpAsync(string email)
    {
        try
        {
            var resp = await _http.PostAsJsonAsync("api/auth/request-otp", new { email });
            var json = await resp.Content.ReadFromJsonAsync<OtpResult>();
            return (resp.IsSuccessStatusCode, json?.Message ?? "發生錯誤");
        }
        catch { return (false, "發生錯誤"); }
    }

    public async Task<bool> VerifyOtpAsync(string email, string code)
    {
        try
        {
            var resp = await _http.PostAsJsonAsync("api/auth/verify-otp", new { email, code });
            if (!resp.IsSuccessStatusCode) return false;
            var json = await resp.Content.ReadFromJsonAsync<LoginResult>();
            if (json == null || !json.Success || string.IsNullOrEmpty(json.Token)) return false;
            State.Token = json.Token;
            State.Email = json.Email;
            State.IsAdmin = json.IsAdmin;
            State.Domain = json.Domain;
            await _js.InvokeVoidAsync("localStorage.setItem", "fm_token", json.Token);
            _http.DefaultRequestHeaders.Authorization =
                new System.Net.Http.Headers.AuthenticationHeaderValue("Bearer", json.Token);
            StateChanged?.Invoke();
            return true;
        }
        catch { return false; }
    }

    public async Task LogoutAsync()
    {
        try { await _http.PostAsync("api/auth/logout", null); } catch { }
        State = new AuthState();
        await _js.InvokeVoidAsync("localStorage.removeItem", "fm_token");
        _http.DefaultRequestHeaders.Authorization = null;
        StateChanged?.Invoke();
    }

    private class OtpResult { public string? Message { get; set; } }

    private class LoginResult
    {
        public bool Success { get; set; }
        public string? Token { get; set; }
        public string? Email { get; set; }
        public bool IsAdmin { get; set; }
        public string? Domain { get; set; }
    }

    private class SessionResult
    {
        public string? Email { get; set; }
        public bool IsAdmin { get; set; }
        public string? Domain { get; set; }
    }
}
