using System.Drawing;
using System.Drawing.Imaging;

namespace AvKit.RegionPicker.Stub;

/// <summary>
/// A deterministic stand-in for <c>avkit-region-picker.exe</c>, used only by the AC-40.18
/// Playwright spec.
///
/// It honours the helper's wire contract exactly — <c>--out &lt;path&gt;</c>, a <c>ready</c>
/// line on stdout, and the declared exit codes — but takes its outcome from the environment
/// instead of from a human dragging a rectangle, so the real Electron spawn/publish/register
/// chain can be driven headlessly and reproducibly:
///
/// <list type="bullet">
///   <item><c>AVKIT_STUB_EXIT</c> — the process exit code (default 0). A non-zero code means
///     no file is written, which is what the cancel and error paths look like from Electron.</item>
///   <item><c>AVKIT_STUB_PIXEL</c> — <c>black</c> writes an all-black PNG (so the pixel guard
///     must reject it); anything else writes an opaque coloured one.</item>
/// </list>
///
/// It is NOT a second implementation of the picker: it never captures the screen, never shows
/// a window, and is never packaged. Everything it fakes is on the far side of the process
/// boundary the spec is there to exercise.
/// </summary>
public static class Program
{
    private const string OutFlag = "--out";
    private const string ReadyMarker = "ready";
    private const string ExitEnv = "AVKIT_STUB_EXIT";
    private const string PixelEnv = "AVKIT_STUB_PIXEL";

    private static readonly Color OpaqueFixture = Color.FromArgb(255, 42, 199, 91);

    public static int Main(string[] args)
    {
        ArgumentNullException.ThrowIfNull(args);

        string? outPath = ParseOutPath(args);
        if (outPath is null)
        {
            Console.Error.WriteLine($"{OutFlag} <path> is required");
            Console.Error.Flush();
            return 1;
        }

        string? parent = Path.GetDirectoryName(outPath);
        if (string.IsNullOrEmpty(parent) || !Directory.Exists(parent))
        {
            Console.Error.WriteLine($"the parent directory of {OutFlag} does not exist: {outPath}");
            Console.Error.Flush();
            return 1;
        }

        // Readiness first, exactly like the real helper's Shown handler: Electron's startup
        // timer is waiting on this line, and a stub that never printed it would make every
        // case time out instead of testing the outcome it was asked for.
        Console.Out.WriteLine(ReadyMarker);
        Console.Out.Flush();

        int exitCode = ResolveExitCode();
        if (exitCode != 0)
        {
            // Only a confirm produces a file. Writing one on the cancel path would let a
            // publication bug pass the "inbox unchanged" case for the wrong reason.
            return exitCode;
        }

        bool black = string.Equals(
            Environment.GetEnvironmentVariable(PixelEnv),
            "black",
            StringComparison.OrdinalIgnoreCase);

        WritePng(outPath, black ? Color.FromArgb(255, 0, 0, 0) : OpaqueFixture);
        return 0;
    }

    private static int ResolveExitCode()
    {
        string? raw = Environment.GetEnvironmentVariable(ExitEnv);
        if (string.IsNullOrWhiteSpace(raw))
        {
            return 0;
        }

        return int.TryParse(raw, out int parsed) ? parsed : 1;
    }

    /// <summary>
    /// Writes a small opaque 32-bpp PNG filled with <paramref name="fill"/>. The size is
    /// irrelevant to the spec; what matters is that it is a real PNG container with real
    /// pixels, so the production pixel guard makes a real decision about it.
    /// </summary>
    private static void WritePng(string path, Color fill)
    {
        using var bitmap = new Bitmap(64, 48, PixelFormat.Format32bppArgb);
        using (Graphics g = Graphics.FromImage(bitmap))
        using (var brush = new SolidBrush(fill))
        {
            g.FillRectangle(brush, 0, 0, bitmap.Width, bitmap.Height);
        }

        bitmap.Save(path, ImageFormat.Png);
    }

    private static string? ParseOutPath(string[] args)
    {
        for (int i = 0; i < args.Length - 1; i++)
        {
            if (string.Equals(args[i], OutFlag, StringComparison.Ordinal))
            {
                string candidate = args[i + 1];
                return string.IsNullOrWhiteSpace(candidate) ? null : Path.GetFullPath(candidate);
            }
        }

        return null;
    }
}
