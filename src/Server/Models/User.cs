namespace FileManager.Server.Models;

public class User
{
    public string Email { get; set; } = "";
    public string PasswordHash { get; set; } = "";
    public bool IsAdmin { get; set; }
    public string Domain { get; set; } = "";
}

public class LoginRequest
{
    public string Email { get; set; } = "";
    public string Password { get; set; } = "";
}

public class LoginResponse
{
    public bool Success { get; set; }
    public string? Token { get; set; }
    public string? Email { get; set; }
    public bool IsAdmin { get; set; }
    public string? Domain { get; set; }
    public string? Message { get; set; }
}

public class SessionResponse
{
    public string? Email { get; set; }
    public bool IsAdmin { get; set; }
    public string? Domain { get; set; }
}

public class OtpRequest
{
    public string Email { get; set; } = "";
}

public class OtpVerifyRequest
{
    public string Email { get; set; } = "";
    public string Code  { get; set; } = "";
}
