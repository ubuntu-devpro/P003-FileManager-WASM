using FileManager.Shared.Models;
using Microsoft.AspNetCore.Mvc;

namespace FileManager.Server.Controllers;

[ApiController]
[Route("api/log")]
public class LogController : ControllerBase
{
    private readonly ILogger<LogController> _logger;
    private readonly IWebHostEnvironment _env;

    public LogController(ILogger<LogController> logger, IWebHostEnvironment env)
    {
        _logger = logger;
        _env = env;
    }

    [HttpPost("client")]
    public IActionResult ClientLog([FromBody] ClientLogEntry entry)
    {
        if (!_env.IsDevelopment())
            return NotFound();

        var msg = "[CLIENT] [{Source}] {Message}";
        var src = entry.Source ?? "unknown";

        switch (entry.Level.ToUpperInvariant())
        {
            case "ERROR":
            case "CRITICAL":
                _logger.LogError("{Ts} " + msg + "\n{Stack}", entry.Timestamp, src, entry.Message, entry.Stack ?? "");
                break;
            case "WARN":
            case "WARNING":
                _logger.LogWarning("{Ts} " + msg, entry.Timestamp, src, entry.Message);
                break;
            default:
                _logger.LogInformation("{Ts} " + msg, entry.Timestamp, src, entry.Message);
                break;
        }

        return Ok();
    }
}
