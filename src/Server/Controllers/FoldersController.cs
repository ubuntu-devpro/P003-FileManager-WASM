using FileManager.Server.Services;
using FileManager.Shared.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.Extensions.Configuration;
using System.Security.Claims;

namespace FileManager.Server.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class FoldersController : ControllerBase
{
    private readonly IFileService _fileService;
    private readonly string RootPath;

    public FoldersController(IFileService fileService, IConfiguration configuration)
    {
        _fileService = fileService;
        RootPath = configuration["FileStorage:RootPath"] ?? "/home/devpro/data";
    }

    private string GetDomain()
    {
        return User.FindFirst("domain")?.Value ?? "";
    }

    private bool IsAdmin()
    {
        return User.FindFirst(ClaimTypes.Role)?.Value == "Admin";
    }

    private string GetRootPathForUser()
    {
        if (IsAdmin())
            return RootPath;
        var domain = GetDomain();
        return Path.Combine(RootPath, domain);
    }

    private bool IsWithinUserScope(string path)
    {
        var userRoot = Path.GetFullPath(GetRootPathForUser());
        var fullPath = Path.GetFullPath(path);
        return fullPath == userRoot || fullPath.StartsWith(userRoot + "/");
    }

    [HttpPost]
    public async Task<IActionResult> Create([FromQuery] string path, [FromQuery] string name)
    {
        // Validate name
        if (string.IsNullOrWhiteSpace(name))
            return BadRequest(new ApiResponse(false, "資料夾名稱不可為空"));

        if (name.Contains("..") || name.Contains('/') || name.Contains('\\'))
            return BadRequest(new ApiResponse(false, "資料夾名稱包含不合法字元"));

        // Validate path is within user scope
        if (!IsWithinUserScope(path))
            return StatusCode(403, new ApiResponse(false, "存取被拒絕"));

        var newPath = Path.Combine(path, name);
        if (!IsWithinUserScope(newPath))
            return StatusCode(403, new ApiResponse(false, "存取被拒絕"));

        var result = await _fileService.CreateFolderAsync(path, name);
        if (!result.Success)
        {
            if (result.Message.Contains("已存在"))
                return Conflict(result);
            return BadRequest(result);
        }
        return Ok(result);
    }
}
