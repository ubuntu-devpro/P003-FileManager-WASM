using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Text;
using FileManager.Server.Models;
using Microsoft.IdentityModel.Tokens;

namespace FileManager.Server.Services;

public interface IJwtService
{
    string GenerateToken(User user);
    User? ValidateCredentials(string email, string password);
}

public class JwtService : IJwtService
{
    private const string SecretKey = "P003-FileManager-WASM-SecretKey-2026-04-06-very-long-key-for-hs256";
    private const string Issuer = "FileManager.Server";
    private const string Audience = "FileManager.Client";

    // Hardcoded users
    private static readonly List<User> Users = new()
    {
        new User { Email = "admin@devpro.com.tw", PasswordHash = "admin123", IsAdmin = true, Domain = "devpro.com.tw" },
        new User { Email = "johnny@sinopac.com", PasswordHash = "johnny123", IsAdmin = false, Domain = "sinopac.com" },
        new User { Email = "user@others.com", PasswordHash = "user123", IsAdmin = false, Domain = "others.com" },
    };

    public User? ValidateCredentials(string email, string password)
    {
        return Users.FirstOrDefault(u =>
            u.Email.Equals(email, StringComparison.OrdinalIgnoreCase)
            && u.PasswordHash == password);
    }

    public string GenerateToken(User user)
    {
        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(SecretKey));
        var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

        var claims = new[]
        {
            new Claim(ClaimTypes.Email, user.Email),
            new Claim(ClaimTypes.Role, user.IsAdmin ? "Admin" : "User"),
            new Claim("domain", user.Domain),
        };

        var token = new JwtSecurityToken(
            issuer: Issuer,
            audience: Audience,
            claims: claims,
            expires: DateTime.UtcNow.AddHours(24),
            signingCredentials: creds
        );

        return new JwtSecurityTokenHandler().WriteToken(token);
    }
}
