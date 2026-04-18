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
    private readonly IConfiguration _config;
    private readonly IOtpService _otp;
    private readonly IEmailService _email;

    public AuthController(IJwtService jwtService, IConfiguration config,
                          IOtpService otp, IEmailService email)
    {
        _jwtService = jwtService;
        _config = config;
        _otp = otp;
        _email = email;
    }

    [HttpPost("login")]
    public IActionResult Login([FromBody] LoginRequest req)
    {
        if (string.IsNullOrWhiteSpace(req.Email) || string.IsNullOrWhiteSpace(req.Password))
            return BadRequest(new LoginResponse { Success = false, Message = "請輸入帳號和密碼" });

        var allowedDomains = _config.GetSection("AllowedEmailDomains").Get<List<string>>() ?? new();
        if (allowedDomains.Count > 0)
        {
            var atIdx = req.Email.LastIndexOf('@');
            var domain = atIdx >= 0 ? req.Email[(atIdx + 1)..] : "";
            if (!allowedDomains.Any(d => d.Equals(domain, StringComparison.OrdinalIgnoreCase)))
                return Unauthorized(new LoginResponse { Success = false, Message = "不允許的 Email 網域" });
        }

        var user = _jwtService.ValidateCredentials(req.Email, req.Password);
        if (user == null)
            return Unauthorized(new LoginResponse { Success = false, Message = "帳號或密碼錯誤" });

        var adminEmails = _config.GetSection("AdminEmails").Get<List<string>>() ?? new();
        var adminDomains = _config.GetSection("AdminDomains").Get<List<string>>() ?? new();
        user.IsAdmin = adminEmails.Any(a => a.Equals(user.Email, StringComparison.OrdinalIgnoreCase))
                    || adminDomains.Any(d => d.Equals(user.Domain, StringComparison.OrdinalIgnoreCase));

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

    [HttpPost("request-otp")]
    public async Task<IActionResult> RequestOtp([FromBody] OtpRequest req)
    {
        if (string.IsNullOrWhiteSpace(req.Email))
            return BadRequest(new { success = false, message = "請輸入 Email" });

        if (!IsAllowedDomain(req.Email))
            return Unauthorized(new { success = false, message = "不允許的 Email 網域" });

        var code = _otp.Generate(req.Email);

        try
        {
            var html = $@"
                <div style='font-family:sans-serif;max-width:400px'>
                  <h2>📁 FileManager 登入驗證碼</h2>
                  <p>您的一次性驗證碼為：</p>
                  <div style='font-size:2rem;font-weight:bold;letter-spacing:8px;color:#4F81BD'>{code}</div>
                  <p style='color:#888;font-size:0.85rem'>驗證碼 10 分鐘內有效，請勿告知他人。</p>
                </div>";
            await _email.SendAsync(req.Email, "FileManager 登入驗證碼", html);
        }
        catch (Exception ex)
        {
            return StatusCode(502, new { success = false, message = $"發信失敗：{ex.Message}" });
        }

        // Always reply the same message to prevent email enumeration
        return Ok(new { success = true, message = "若帳號存在，驗證碼已發送至信箱" });
    }

    [HttpPost("verify-otp")]
    public IActionResult VerifyOtp([FromBody] OtpVerifyRequest req)
    {
        if (string.IsNullOrWhiteSpace(req.Email) || string.IsNullOrWhiteSpace(req.Code))
            return BadRequest(new LoginResponse { Success = false, Message = "請輸入 Email 和驗證碼" });

        if (!IsAllowedDomain(req.Email))
            return Unauthorized(new LoginResponse { Success = false, Message = "不允許的 Email 網域" });

        if (!_otp.Verify(req.Email, req.Code))
            return Unauthorized(new LoginResponse { Success = false, Message = "驗證碼錯誤或已過期" });

        var user = BuildUserFromEmail(req.Email);
        var token = _jwtService.GenerateToken(user);
        return Ok(new LoginResponse
        {
            Success = true, Token = token,
            Email = user.Email, IsAdmin = user.IsAdmin, Domain = user.Domain
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
        return Ok(new { success = true });
    }

    private bool IsAllowedDomain(string email)
    {
        var allowed = _config.GetSection("AllowedEmailDomains").Get<List<string>>() ?? new();
        if (allowed.Count == 0) return true;
        var atIdx = email.LastIndexOf('@');
        var domain = atIdx >= 0 ? email[(atIdx + 1)..] : "";
        return allowed.Any(d => d.Equals(domain, StringComparison.OrdinalIgnoreCase));
    }

    private FileManager.Server.Models.User BuildUserFromEmail(string email)
    {
        var atIdx = email.LastIndexOf('@');
        var domain = atIdx >= 0 ? email[(atIdx + 1)..] : "";
        var adminEmails = _config.GetSection("AdminEmails").Get<List<string>>() ?? new();
        var adminDomains = _config.GetSection("AdminDomains").Get<List<string>>() ?? new();
        var isAdmin = adminEmails.Any(a => a.Equals(email, StringComparison.OrdinalIgnoreCase))
                   || adminDomains.Any(d => d.Equals(domain, StringComparison.OrdinalIgnoreCase));
        return new FileManager.Server.Models.User
        {
            Email = email, Domain = domain, IsAdmin = isAdmin, PasswordHash = ""
        };
    }
}
