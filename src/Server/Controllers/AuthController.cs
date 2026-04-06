using FileManager.Server.Models;
using FileManager.Server.Services;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;

namespace FileManager.Server.Controllers;

[ApiController]
[Route("api/auth")]
public class AuthController : ControllerBase
{
    private readonly IJwtService _jwtService;

    public AuthController(IJwtService jwtService)
    {
        _jwtService = jwtService;
    }

    [HttpPost("login")]
    public IActionResult Login([FromBody] LoginRequest req)
    {
        if (string.IsNullOrWhiteSpace(req.Email) || string.IsNullOrWhiteSpace(req.Password))
            return BadRequest(new LoginResponse { Success = false, Message = "請輸入帳號和密碼" });

        var user = _jwtService.ValidateCredentials(req.Email, req.Password);
        if (user == null)
            return Unauthorized(new LoginResponse { Success = false, Message = "帳號或密碼錯誤" });

        var token = _jwtService.GenerateToken(user);
        return Ok(new LoginResponse
        {
            Success = true,
            Token = token,
            Email = user.Email,
            IsAdmin = user.IsAdmin,
            Domain = user.Domain
        });
    }

    [Authorize]
    [HttpGet("session")]
    public IActionResult Session()
    {
        var email = User.FindFirst(ClaimTypes.Email)?.Value;
        var role = User.FindFirst(ClaimTypes.Role)?.Value;
        var domain = User.FindFirst("domain")?.Value;

        return Ok(new SessionResponse
        {
            Email = email,
            IsAdmin = role == "Admin",
            Domain = domain
        });
    }

    [Authorize]
    [HttpPost("logout")]
    public IActionResult Logout()
    {
        // JWT is stateless, client just discards the token
        return Ok(new { success = true });
    }
}
