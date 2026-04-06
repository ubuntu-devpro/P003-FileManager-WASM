using FileManager.Shared.Models;

namespace FileManager.Server.Services;

public interface IFileService
{
    Task<FileListResponse> GetFilesAsync(string path);
    Task<FolderTreeResponse> GetFolderTreeAsync(string path);
    Task<ApiResponse> CreateFolderAsync(string path, string name);
    Task<ApiResponse> RenameAsync(string currentPath, string newName);
    Task<ApiResponse> MoveAsync(string[] sourcePaths, string destinationPath);
    Task<ApiResponse> DeleteAsync(string[] paths);
    Task<SearchResponse> SearchAsync(string path, string query);
}
