using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using FileManager.Client;
using FileManager.Client.Services;
using Radzen;

var builder = WebAssemblyHostBuilder.CreateDefault(args);
builder.RootComponents.Add<App>("#app");
builder.RootComponents.Add<HeadOutlet>("head::after");

// HTTP Client pointing to API server
builder.Services.AddScoped(sp => new HttpClient
{
    BaseAddress = new Uri("http://localhost:5001")
});

// Radzen services
builder.Services.AddRadzenComponents();

// Auth service
builder.Services.AddScoped<IAuthService, AuthService>();

await builder.Build().RunAsync();
