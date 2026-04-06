namespace FileManager.Shared.Models;

// ===== Request DTOs =====

public record SearchRequest(string Path, string Query);

public record RenameRequest(string CurrentPath, string NewName);

public record MoveRequest(string[] SourcePaths, string DestinationPath);

public record DeleteRequest(string[] Paths);

// ===== Response DTOs =====

public record ApiResponse(bool Success, string Message = "");

public record FileItem(
    string Name,
    string Path,
    bool IsDirectory,
    long Size,
    DateTime Modified);

public record FileListResponse(
    bool Success,
    string Message,
    List<FileItem> Items,
    string CurrentPath);

public record FolderTreeNode(
    string Name,
    string Path,
    List<FolderTreeNode> Children);

public record FolderTreeResponse(
    bool Success,
    string Message,
    List<FolderTreeNode> Nodes);

public record UploadResponse(bool Success, string Message, int TotalUploaded);

public record SearchResponse(
    bool Success,
    string Message,
    List<FileItem> Results);
