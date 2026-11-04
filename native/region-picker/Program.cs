using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
using System.Windows.Forms;

namespace AvKit.RegionPicker;

/// <summary>
/// The helper's whole wire contract with Electron, declared in one place.
/// The values here are mirrored by the MEU-40 plan folder's <c>named-sets.json</c>,
/// and <c>ProgramExitTests</c> reads that file and asserts they agree — a typo on
/// either side is a failing test rather than a picker that silently never signals
/// readiness.
/// </summary>
public static class PickerContract
{
    /// <summary>Minimum width AND height, in physical pixels, of a confirmable region.</summary>
    public const int PICKER_MIN_EDGE_PX = 8;

    /// <summary>A region meeting <see cref="PICKER_MIN_EDGE_PX"/> was confirmed; the PNG is at --out.</summary>
    public const int PICKER_EXIT_CONFIRM = 0;

    /// <summary>Bad argv, unwritable --out parent, or a GDI failure. Reason on stderr; no file written.</summary>
    public const int PICKER_EXIT_ERROR = 1;

    /// <summary>The user cancelled (Esc, or released below the minimum edge). No file written.</summary>
    public const int PICKER_EXIT_CANCEL = 2;

    /// <summary>
    /// Written on its own line to stdout, and flushed, from the handler for the form's
    /// first Shown event. It is the only start-of-picker event Electron can observe.
    /// </summary>
    public const string PICKER_READY_MARKER = "ready";
}

/// <summary>
/// The seam that owns pixels. The GDI implementation is <see cref="ScreenCaptureSource"/>;
/// tests substitute a fake so the ordering and crop rules can be proven without a desktop.
/// </summary>
public interface ICaptureSource
{
    /// <summary>Bounds of the display under the cursor, in physical pixels. May have a negative origin.</summary>
    Rectangle GetTargetBounds();

    /// <summary>Grabs <paramref name="bounds"/> from the desktop into a 32-bpp opaque bitmap.</summary>
    Bitmap Capture(Rectangle bounds);
}

/// <summary>
/// The seam that owns the on-screen picker. <see cref="RegionForm"/> is the WinForms
/// implementation; tests substitute a fake that records call order.
/// </summary>
public interface IPickerDialog
{
    /// <summary>
    /// Raised exactly once, when the frozen frame is on screen and before any input is
    /// accepted. <see cref="Program.Run"/> writes the readiness marker from this event,
    /// never from its own prologue.
    /// </summary>
    event Action? FrameShown;

    /// <summary>Shows the already-frozen frame and blocks until the user settles the selection.</summary>
    PickerResult Show(Bitmap frozenFrame, Rectangle bounds);
}

public static class Program
{
    [STAThread]
    public static int Main(string[] args)
    {
        // NOT ApplicationConfiguration.Initialize(): its generated body calls
        // Application.SetHighDpiMode at runtime, which is both too late (see app.manifest)
        // and rejected outright (WFAC010) while the manifest owns the DPI declaration.
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        using var dialog = new RegionForm();
        return Run(args, new ScreenCaptureSource(), dialog, Console.Out, Console.Error);
    }

    /// <summary>
    /// The real entrypoint, with both OS-facing collaborators injected so the contract is
    /// testable. Returns one of the <see cref="PickerContract"/> exit codes.
    /// </summary>
    public static int Run(
        string[] args,
        ICaptureSource capture,
        IPickerDialog dialog,
        TextWriter stdout,
        TextWriter stderr)
    {
        ArgumentNullException.ThrowIfNull(args);
        ArgumentNullException.ThrowIfNull(capture);
        ArgumentNullException.ThrowIfNull(dialog);
        ArgumentNullException.ThrowIfNull(stdout);
        ArgumentNullException.ThrowIfNull(stderr);

        string outPath;
        try
        {
            outPath = ParseOutPath(args);
        }
        catch (ArgumentException ex)
        {
            return Fail(stderr, ex.Message);
        }

        // Argv is rejected before anything is captured or shown: a bad invocation must never
        // put a window over the user's desktop, and it must never leave a partial file.
        string? parent = Path.GetDirectoryName(outPath);
        if (string.IsNullOrEmpty(parent) || !Directory.Exists(parent))
        {
            return Fail(stderr, $"the parent directory of --out does not exist: {outPath}");
        }

        void OnFrameShown()
        {
            // The readiness marker is written from the frame-shown notification, never from
            // this method's prologue: a marker printed before the freeze frame is visible
            // would make Electron's startup measurement time process creation instead.
            stdout.WriteLine(PickerContract.PICKER_READY_MARKER);
            stdout.Flush();
        }

        dialog.FrameShown += OnFrameShown;
        try
        {
            Rectangle bounds = capture.GetTargetBounds();

            // Freeze first, show second. Showing the window and grabbing after is the
            // ordering defect this whole helper exists to remove.
            using Bitmap frame = capture.Capture(bounds);
            ScreenCaptureSource.ForceOpaque(frame);

            PickerResult result = dialog.Show(frame, bounds);
            if (result.Kind != PickerResultKind.Confirmed)
            {
                return PickerContract.PICKER_EXIT_CANCEL;
            }

            Rectangle local = RectMath.ClampToBounds(
                result.Rect,
                new Rectangle(Point.Empty, frame.Size));

            if (!RectMath.MeetsMinEdge(local))
            {
                return PickerContract.PICKER_EXIT_CANCEL;
            }

            using Bitmap crop = frame.Clone(local, PixelFormat.Format32bppArgb);
            ScreenCaptureSource.ForceOpaque(crop);
            crop.Save(outPath, ImageFormat.Png);

            return PickerContract.PICKER_EXIT_CONFIRM;
        }
        catch (Exception ex) when (ex is IOException
                                      or UnauthorizedAccessException
                                      or ExternalException
                                      or ArgumentException
                                      or InvalidOperationException)
        {
            return Fail(stderr, ex.Message);
        }
        finally
        {
            dialog.FrameShown -= OnFrameShown;
        }
    }

    private static int Fail(TextWriter stderr, string reason)
    {
        stderr.WriteLine(reason);
        stderr.Flush();
        return PickerContract.PICKER_EXIT_ERROR;
    }

    /// <summary>
    /// The whole argv surface: exactly one <c>--out &lt;path&gt;</c>. Unknown arguments are
    /// rejected rather than ignored — Electron is the only caller, so anything unexpected is
    /// a bug in the contract, and failing closed keeps it visible.
    /// </summary>
    private static string ParseOutPath(string[] args)
    {
        const string OutFlag = "--out";
        string? outPath = null;

        for (int i = 0; i < args.Length; i++)
        {
            if (!string.Equals(args[i], OutFlag, StringComparison.Ordinal))
            {
                throw new ArgumentException($"unrecognized argument: {args[i]}");
            }

            if (outPath is not null)
            {
                throw new ArgumentException($"{OutFlag} was given more than once");
            }

            if (i + 1 >= args.Length)
            {
                throw new ArgumentException($"{OutFlag} requires a path");
            }

            outPath = args[++i];
            if (string.IsNullOrWhiteSpace(outPath))
            {
                throw new ArgumentException($"{OutFlag} requires a non-empty path");
            }
        }

        if (outPath is null)
        {
            throw new ArgumentException($"{OutFlag} <path> is required");
        }

        return Path.GetFullPath(outPath);
    }
}
