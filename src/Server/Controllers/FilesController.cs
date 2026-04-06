using FileManager.Server.Services;
using FileManager.Shared.Models;
using Microsoft.AspNetCore.Mvc;

namespace FileManager.Server.Controllers;

[ApiController]
[Route("api/[controller]")]
public class FilesController : ControllerBase
{
    private readonly IFileService _fileService;
    private static readonly string RootPath = "/home/devpro/data";

    public FilesController(IFileService fileService)
    {
        _fileService = fileService;
    }

    [HttpGet]
    public async Task<FileListResponse> List([FromQuery] string path = "/home/devpro/data")
    {
        return await _fileService.GetFilesAsync(path);
    }

    [HttpGet("tree")]
    public async Task<FolderTreeResponse> Tree([FromQuery] string path = "/home/devpro/data")
    {
        return await _fileService.GetFolderTreeAsync(path);
    }

    [HttpPost("search")]
    public async Task<SearchResponse> Search([FromBody] SearchRequest req)
    {
        return await _fileService.SearchAsync(req.Path, req.Query);
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
