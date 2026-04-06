using FileManager.Server.Services;
using FileManager.Shared.Models;
using Microsoft.AspNetCore.Mvc;

namespace FileManager.Server.Controllers;

[ApiController]
[Route("api/[controller]")]
public class FoldersController : ControllerBase
{
    private readonly IFileService _fileService;

    public FoldersController(IFileService fileService)
    {
        _fileService = fileService;
    }

    [HttpPost]
    public async Task<ApiResponse> Create([FromQuery] string path, [FromQuery] string name)
    {
        return await _fileService.CreateFolderAsync(path, name);
    }
}
