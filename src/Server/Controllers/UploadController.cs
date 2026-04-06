using FileManager.Server.Services;
using FileManager.Shared.Models;
using Microsoft.AspNetCore.Mvc;

namespace FileManager.Server.Controllers;

[ApiController]
[Route("api/[controller]")]
public class UploadController : ControllerBase
{
    private readonly IFileService _fileService;
    private static readonly string RootPath = "/home/devpro/data";

    private bool IsPathAllowed(string path)
    {
        var fullPath = Path.GetFullPath(path);
        return fullPath.StartsWith(Path.GetFullPath(RootPath));
    }

    [HttpPost]
    public async Task<UploadResponse> Upload(
        [FromQuery] string destinationPath = "/home/devpro/data",
        IFormFile[]? files = null)
    {
        if (files == null || files.Length == 0)
            return new(false, "沒有上傳檔案", 0);

        if (!IsPathAllowed(destinationPath))
            return new(false, "路徑存取被拒絕", 0);

        int uploaded = 0;
        foreach (var file in files)
        {
            var destPath = Path.Combine(destinationPath, file.FileName);
            if (!IsPathAllowed(destPath))
                continue;

            await using var stream = System.IO.File.Create(destPath);
            await file.CopyToAsync(stream);
            uploaded++;
        }

        return new(true, "", uploaded);
    }
}
