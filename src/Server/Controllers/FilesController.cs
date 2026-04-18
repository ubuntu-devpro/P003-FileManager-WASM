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
public class FilesController : ControllerBase
{
    private readonly IFileService _fileService;
    private readonly string RootPath;

    public FilesController(IFileService fileService, IConfiguration configuration)
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
        var path = Path.Combine(RootPath, domain);
        Directory.CreateDirectory(path);
        return path;
    }

    private bool IsWithinUserScope(string path)
    {
        if (HasNullByte(path)) return false;
        var userRoot = Path.GetFullPath(GetRootPathForUser());
        var fullPath = Path.GetFullPath(path);
        return fullPath == userRoot || fullPath.StartsWith(userRoot + "/");
    }

    // Mutating ops (Delete/Rename/Move source) must not target the domain root itself.
    private bool IsWithinUserScopeForMutation(string path)
    {
        if (HasNullByte(path)) return false;
        var userRoot = Path.GetFullPath(GetRootPathForUser());
        var fullPath = Path.GetFullPath(path);
        return fullPath.StartsWith(userRoot + "/");
    }

    private static bool HasNullByte(string? s) => s != null && s.Contains('\0');

    /// <summary>
    /// For read-only endpoints: if user requests a path outside their scope,
    /// clamp it to their root instead of rejecting.
    /// Returns null if the path is in a sibling domain (truly unauthorized).
    /// </summary>
    private string? ClampPathToUserScope(string path)
    {
        if (HasNullByte(path)) return null;

        if (IsWithinUserScope(path))
            return path;

        var userRoot = Path.GetFullPath(GetRootPathForUser());
        var fullPath = Path.GetFullPath(path);

        // If the requested path is an ancestor of user root, redirect to user root
        if (userRoot.StartsWith(fullPath + "/") || userRoot == fullPath)
            return GetRootPathForUser();

        // Path is in a sibling domain or completely outside - reject
        return null;
    }

    [HttpGet]
    public async Task<IActionResult> List([FromQuery] string? path = null)
    {
        if (HasNullByte(path))
            return BadRequest(new FileListResponse(false, "路徑包含不合法字元", new(), path ?? ""));

        var root = GetRootPathForUser();
        var targetPath = string.IsNullOrEmpty(path) ? root : path;

        var clamped = ClampPathToUserScope(targetPath);
        if (clamped == null)
            return StatusCode(403, new FileListResponse(false, "存取被拒絕", new(), targetPath));

        return Ok(await _fileService.GetFilesAsync(clamped));
    }

    [HttpGet("tree")]
    public async Task<IActionResult> Tree([FromQuery] string? path = null)
    {
        if (HasNullByte(path))
            return BadRequest(new FolderTreeResponse(false, "路徑包含不合法字元", new()));

        var root = GetRootPathForUser();
        var targetPath = string.IsNullOrEmpty(path) ? root : path;

        var clamped = ClampPathToUserScope(targetPath);
        if (clamped == null)
            return StatusCode(403, new FolderTreeResponse(false, "存取被拒絕", new()));

        return Ok(await _fileService.GetFolderTreeAsync(clamped));
    }

    [HttpPost("search")]
    public async Task<IActionResult> Search([FromBody] SearchRequest req)
    {
        if (HasNullByte(req.Path) || HasNullByte(req.Query))
            return BadRequest(new SearchResponse(false, "路徑包含不合法字元", new()));

        var root = GetRootPathForUser();
        var searchPath = string.IsNullOrEmpty(req.Path) ? root : req.Path;

        var clamped = ClampPathToUserScope(searchPath);
        if (clamped == null)
            return StatusCode(403, new SearchResponse(false, "存取被拒絕", new()));

        var result = await _fileService.SearchAsync(clamped!, req.Query);

        // Extra safety: filter results to only include items within user's scope
        if (!IsAdmin() && result.Success)
        {
            var userRoot = Path.GetFullPath(GetRootPathForUser());
            var filtered = result.Results
                .Where(r => Path.GetFullPath(r.Path).StartsWith(userRoot + "/") || Path.GetFullPath(r.Path) == userRoot)
                .ToList();
            return Ok(new SearchResponse(true, result.Message, filtered));
        }

        return Ok(result);
    }

    [HttpPatch("rename")]
    public async Task<IActionResult> Rename([FromBody] RenameRequest req)
    {
        if (string.IsNullOrWhiteSpace(req.NewName))
            return BadRequest(new ApiResponse(false, "新名稱不可為空"));

        if (req.NewName.Contains("..") || req.NewName.Contains('/') || req.NewName.Contains('\\'))
            return BadRequest(new ApiResponse(false, "新名稱包含不合法字元"));

        if (HasNullByte(req.CurrentPath) || HasNullByte(req.NewName))
            return BadRequest(new ApiResponse(false, "路徑包含不合法字元"));

        if (!IsWithinUserScopeForMutation(req.CurrentPath))
            return StatusCode(403, new ApiResponse(false, "存取被拒絕"));

        var result = await _fileService.RenameAsync(req.CurrentPath, req.NewName);
        if (!result.Success)
            return BadRequest(result);
        return Ok(result);
    }

    [HttpPatch("move")]
    public async Task<IActionResult> Move([FromBody] MoveRequest req)
    {
        if (HasNullByte(req.DestinationPath))
            return BadRequest(new ApiResponse(false, "路徑包含不合法字元"));

        if (!IsWithinUserScope(req.DestinationPath))
            return StatusCode(403, new ApiResponse(false, "目標路徑存取被拒絕"));

        foreach (var src in req.SourcePaths)
        {
            if (HasNullByte(src))
                return BadRequest(new ApiResponse(false, "路徑包含不合法字元"));

            if (!IsWithinUserScopeForMutation(src))
                return StatusCode(403, new ApiResponse(false, "來源路徑存取被拒絕"));
        }

        return Ok(await _fileService.MoveAsync(req.SourcePaths, req.DestinationPath));
    }

    [HttpDelete]
    public async Task<IActionResult> Delete([FromBody] DeleteRequest req)
    {
        foreach (var p in req.Paths)
        {
            if (HasNullByte(p))
                return BadRequest(new ApiResponse(false, "路徑包含不合法字元"));

            if (!IsWithinUserScopeForMutation(p))
                return StatusCode(403, new ApiResponse(false, "存取被拒絕"));
        }

        return Ok(await _fileService.DeleteAsync(req.Paths));
    }

    [HttpGet("download")]
    public IActionResult Download([FromQuery] string path)
    {
        if (string.IsNullOrEmpty(path))
            return BadRequest("路徑不可為空");

        if (HasNullByte(path))
            return BadRequest("路徑包含不合法字元");

        if (!IsWithinUserScope(path))
            return StatusCode(403, "存取被拒絕");

        var fullPath = Path.GetFullPath(path);
        if (!System.IO.File.Exists(fullPath))
            return NotFound();

        var stream = new FileStream(fullPath, FileMode.Open, FileAccess.Read, FileShare.Read);
        var name = Path.GetFileName(fullPath);
        return File(stream, "application/octet-stream", name);
    }
}
