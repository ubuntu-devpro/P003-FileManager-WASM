using System.IO;
using System.Security.Cryptography;
using FileManager.Shared.Models;

namespace FileManager.Server.Services;

public class FileService : IFileService
{
    // Hardcoded root - no path traversal possible
    private static readonly string RootPath = "/home/devpro/data";
    private static readonly string[] RestrictedExtensions = { ".exe", ".dll", ".config" };

    public FileService()
    {
        // Ensure root directory exists
        Directory.CreateDirectory(RootPath);
    }

    private bool IsPathAllowed(string path)
    {
        // Path traversal protection
        var fullPath = Path.GetFullPath(path);
        var rootFull = Path.GetFullPath(RootPath);
        if (!fullPath.StartsWith(rootFull))
            return false;

        // File extension check
        var ext = Path.GetExtension(path).ToLowerInvariant();
        if (RestrictedExtensions.Contains(ext))
            return false;

        return true;
    }

    public async Task<FileListResponse> GetFilesAsync(string path)
    {
        try
        {
            if (!IsPathAllowed(path))
                return new(false, "路徑存取被拒絕", [], path);

            if (!Directory.Exists(path))
                return new(false, "目錄不存在", [], path);

            var items = new List<FileItem>();
            await Task.Run(() =>
            {
                foreach (var dir in Directory.GetDirectories(path))
                {
                    var info = new DirectoryInfo(dir);
                    items.Add(new FileItem(info.Name, dir, true, 0, info.LastWriteTime));
                }
                foreach (var file in Directory.GetFiles(path))
                {
                    var info = new FileInfo(file);
                    items.Add(new FileItem(info.Name, file, false, info.Length, info.LastWriteTime));
                }
            });

            return new(true, "", items, path);
        }
        catch (Exception ex)
        {
            return new(false, ex.Message, [], path);
        }
    }

    public async Task<FolderTreeResponse> GetFolderTreeAsync(string path)
    {
        try
        {
            if (!IsPathAllowed(path))
                return new(false, "路徑存取被拒絕", []);

            if (!Directory.Exists(path))
                return new(false, "目錄不存在", []);

            var root = await Task.Run(() => BuildTree(path));
            return new(true, "", new List<FolderTreeNode> { root });
        }
        catch (Exception ex)
        {
            return new(false, ex.Message, []);
        }
    }

    private FolderTreeNode BuildTree(string path)
    {
        var dir = new DirectoryInfo(path);
        var children = new List<FolderTreeNode>();

        try
        {
            foreach (var sub in Directory.GetDirectories(path))
            {
                children.Add(BuildTree(sub));
            }
        }
        catch { /* Skip inaccessible dirs */ }

        return new FolderTreeNode(dir.Name, path, children);
    }

    public async Task<ApiResponse> CreateFolderAsync(string path, string name)
    {
        try
        {
            var newPath = Path.Combine(path, name);
            if (!IsPathAllowed(newPath))
                return new(false, "路徑存取被拒絕");

            await Task.Run(() => Directory.CreateDirectory(newPath));
            return new(true, "資料夾已建立");
        }
        catch (Exception ex)
        {
            return new(false, ex.Message);
        }
    }

    public async Task<ApiResponse> RenameAsync(string currentPath, string newName)
    {
        try
        {
            if (!IsPathAllowed(currentPath))
                return new(false, "路徑存取被拒絕");

            var parent = Path.GetDirectoryName(currentPath) ?? "";
            var newPath = Path.Combine(parent, newName);

            if (!IsPathAllowed(newPath))
                return new(false, "新路徑存取被拒絕");

            await Task.Run(() => Directory.Move(currentPath, newPath));
            return new(true, "重新命名成功");
        }
        catch (Exception ex)
        {
            return new(false, ex.Message);
        }
    }

    public async Task<ApiResponse> MoveAsync(string[] sourcePaths, string destinationPath)
    {
        try
        {
            if (!IsPathAllowed(destinationPath))
                return new(false, "目標路徑存取被拒絕");

            int moved = 0;
            await Task.Run(() =>
            {
                foreach (var src in sourcePaths)
                {
                    if (!IsPathAllowed(src))
                        continue;
                    var name = Path.GetFileName(src);
                    var dest = Path.Combine(destinationPath, name);
                    if (Directory.Exists(src))
                        Directory.Move(src, dest);
                    else
                        File.Move(src, dest);
                    moved++;
                }
            });

            return new(true, $"已移動 {moved} 個項目");
        }
        catch (Exception ex)
        {
            return new(false, ex.Message);
        }
    }

    public async Task<ApiResponse> DeleteAsync(string[] paths)
    {
        try
        {
            int deleted = 0;
            await Task.Run(() =>
            {
                foreach (var p in paths)
                {
                    if (!IsPathAllowed(p))
                        continue;
                    if (Directory.Exists(p))
                        Directory.Delete(p, true);
                    else if (File.Exists(p))
                        File.Delete(p);
                    deleted++;
                }
            });

            return new(true, $"已刪除 {deleted} 個項目");
        }
       catch (Exception ex)
        {
            return new(false, ex.Message);
        }
    }

    public async Task<SearchResponse> SearchAsync(string path, string query)
    {
        try
        {
            if (!IsPathAllowed(path))
                return new(false, "路徑存取被拒絕", []);

            var results = new List<FileItem>();
            await Task.Run(() =>
            {
                foreach (var file in Directory.EnumerateFiles(path, $"*{query}*", SearchOption.AllDirectories))
                {
                    if (!IsPathAllowed(file)) continue;
                    var info = new FileInfo(file);
                    results.Add(new FileItem(info.Name, file, false, info.Length, info.LastWriteTime));
                }
            });

            return new(true, "", results);
        }
        catch (Exception ex)
        {
            return new(false, ex.Message, []);
        }
    }
}
