using Microsoft.AspNetCore.Components.Web;
using Microsoft.AspNetCore.Components.WebAssembly.Hosting;
using FileManager.Client;
using FileManager.Client.Services;
using Radzen;

var builder = WebAssemblyHostBuilder.CreateDefault(args);
builder.RootComponents.Add<App>("#app");
builder.RootComponents.Add<HeadOutlet>("head::after");

// HTTP Client — base address follows wherever the app is hosted
builder.Services.AddScoped(sp => new HttpClient
{
    BaseAddress = new Uri(builder.HostEnvironment.BaseAddress)
});

// Radzen services
builder.Services.AddRadzenComponents();

// Auth service
builder.Services.AddScoped<IAuthService, AuthService>();

// Client-side debug logger (sends to server in Development)
builder.Services.AddScoped<ClientLogService>();

await builder.Build().RunAsync();
