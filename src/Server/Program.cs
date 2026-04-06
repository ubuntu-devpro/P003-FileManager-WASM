using FileManager.Server.Services;
using Microsoft.Extensions.FileProviders;

var builder = WebApplication.CreateBuilder(args);

// Add services
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();

// CORS for Blazor WASM client
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowBlazor", policy =>
    {
        policy.WithOrigins("https://localhost:5001", "http://localhost:5000")
              .AllowAnyHeader()
              .AllowAnyMethod()
              .AllowCredentials();
    });
});

// File service
builder.Services.AddSingleton<IFileService, FileService>();

var app = builder.Build();

app.UseCors("AllowBlazor");
app.UseStaticFiles();  // Serve Blazor WASM static files
app.MapControllers();

// Fallback to index.html for Blazor WASM routing
app.MapFallbackToFile("index.html");

app.Run();
