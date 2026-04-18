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
public class UploadController : ControllerBase
{
    private readonly IFileService _fileService;
    private readonly string RootPath;

    public UploadController(IFileService fileService, IConfiguration configuration)
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

    private bool IsPathAllowed(string path)
    {
        var fullPath = Path.GetFullPath(path);
        return fullPath.StartsWith(Path.GetFullPath(RootPath));
    }

    private static readonly string[] RestrictedExtensions = { ".exe", ".dll", ".config" };

    [HttpPost]
    public async Task<IActionResult> Upload(
        [FromQuery] string? path = null,
        [FromQuery] string? destinationPath = null)
    {
        // Accept both 'path' and 'destinationPath' query params
        var destPath = path ?? destinationPath ?? GetRootPathForUser();

        if (!IsPathAllowed(destPath))
            return Ok(new UploadResponse(false, "路徑存取被拒絕", 0));

        if (!IsWithinUserScope(destPath))
            return StatusCode(403, new UploadResponse(false, "存取被拒絕", 0));

        // Read files from request form (accepts any field name)
        var formFiles = Request.Form.Files;
        if (formFiles.Count == 0)
            return Ok(new UploadResponse(false, "沒有上傳檔案", 0));

        int uploaded = 0;
        foreach (var file in formFiles)
        {
            var ext = Path.GetExtension(file.FileName).ToLowerInvariant();
            if (RestrictedExtensions.Contains(ext))
                continue;

            var filePath = Path.Combine(destPath, file.FileName);
            if (!IsPathAllowed(filePath) || !IsWithinUserScope(filePath))
                continue;

            Directory.CreateDirectory(destPath);
            await using var stream = System.IO.File.Create(filePath);
            await file.CopyToAsync(stream);
            uploaded++;
        }

        return Ok(new UploadResponse(true, "", uploaded));
    }
}
