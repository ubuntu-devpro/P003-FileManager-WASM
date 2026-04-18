using MailKit.Net.Smtp;
using MailKit.Security;
using MimeKit;

namespace FileManager.Server.Services;

public interface IEmailService
{
    Task SendAsync(string to, string subject, string htmlBody);
}

public class EmailService : IEmailService
{
    private readonly IConfiguration _config;
    private readonly ILogger<EmailService> _logger;

    public EmailService(IConfiguration config, ILogger<EmailService> logger)
    {
        _config = config;
        _logger = logger;
    }

    public async Task SendAsync(string to, string subject, string htmlBody)
    {
        var smtp = _config.GetSection("Smtp");
        var host     = smtp["Host"]        ?? "smtp.gmail.com";
        var port     = int.Parse(smtp["Port"] ?? "587");
        var username = smtp["Username"]    ?? "";
        var password = smtp["Password"]    ?? "";
        var fromName = smtp["FromName"]    ?? "FileManager";
        var fromAddr = smtp["FromAddress"] ?? username;

        var message = new MimeMessage();
        message.From.Add(new MailboxAddress(fromName, fromAddr));
        message.To.Add(MailboxAddress.Parse(to));
        message.Subject = subject;
        message.Body = new TextPart("html") { Text = htmlBody };

        using var client = new SmtpClient();
        await client.ConnectAsync(host, port, SecureSocketOptions.StartTls);
        await client.AuthenticateAsync(username, password);
        await client.SendAsync(message);
        await client.DisconnectAsync(true);

        _logger.LogInformation("Email sent to {To} subject={Subject}", to, subject);
    }
}
