using FileManager.Server.Services;
using FileManager.Shared.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;

namespace FileManager.Server.Controllers;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class FilesController : ControllerBase
{
    private readonly IFileService _fileService;
    private static readonly string RootPath = "/home/devpro/data";

    public FilesController(IFileService fileService)
    {
        _fileService = fileService;
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
        return $"{RootPath}/{domain}";
    }

    [HttpGet]
    public async Task<FileListResponse> List([FromQuery] string? path = null)
    {
        var root = GetRootPathForUser();
        var targetPath = string.IsNullOrEmpty(path) ? root : path;
        return await _fileService.GetFilesAsync(targetPath);
    }

    [HttpGet("tree")]
    public async Task<FolderTreeResponse> Tree([FromQuery] string? path = null)
    {
        var root = GetRootPathForUser();
        var targetPath = string.IsNullOrEmpty(path) ? root : path;
        return await _fileService.GetFolderTreeAsync(targetPath);
    }

    [HttpPost("search")]
    public async Task<SearchResponse> Search([FromBody] SearchRequest req)
    {
        var root = GetRootPathForUser();
        var searchPath = string.IsNullOrEmpty(req.Path) ? root : req.Path;
        return await _fileService.SearchAsync(searchPath, req.Query);
    }

    [HttpPatch("rename")]
    public async Task<ApiResponse> Rename([FromBody] RenameRequest req)
    {
        return await _fileService.RenameAsync(req.CurrentPath, req.NewName);
    }

    [HttpPatch("move")]
    public async Task<ApiResponse> Move([FromBody] MoveRequest req)
    {
        return await _fileService.MoveAsync(req.SourcePaths, req.DestinationPath);
    }

    [HttpDelete]
    public async Task<ApiResponse> Delete([FromBody] DeleteRequest req)
    {
        return await _fileService.DeleteAsync(req.Paths);
    }

    [HttpGet("download")]
    public IActionResult Download([FromQuery] string path)
    {
        if (!System.IO.File.Exists(path))
            return NotFound();

        var bytes = System.IO.File.ReadAllBytes(path);
        var name = Path.GetFileName(path);
        return File(bytes, "application/octet-stream", name);
    }
}
