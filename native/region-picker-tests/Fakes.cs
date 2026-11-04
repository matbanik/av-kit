using System.Drawing;
using System.Drawing.Imaging;
using System.Text;
using AvKit.RegionPicker;

namespace AvKit.RegionPicker.Tests;

/// <summary>
/// The ordered log the fakes below append to. Call order is the whole point of AC-40.24 and
/// AC-40.26(a) — "the frame is captured before the window exists" is an ordering property, and
/// an ordering property can only be proven by recording the order.
/// </summary>
public sealed class CallLog
{
    public const string Capture = "capture";
    public const string Show = "show";
    public const string FrameShown = "frame-shown";
    public const string StdoutWrite = "stdout-write";
    public const string StdoutFlush = "stdout-flush";

    public List<string> Events { get; } = new();

    public void Add(string entry) => Events.Add(entry);

    public int IndexOf(string entry) => Events.IndexOf(entry);

    public override string ToString() => string.Join(" -> ", Events);
}

/// <summary>
/// A <see cref="TextWriter"/> that records both the text and the <see cref="Flush"/> calls.
/// The flush matters: the picker's stdout is a pipe held by Electron, and an unflushed
/// readiness line can sit in the buffer until the process exits — by which time the marker
/// Electron times against is useless.
/// </summary>
public sealed class RecordingWriter : TextWriter
{
    private readonly CallLog _log;
    private readonly StringBuilder _buffer = new();

    public RecordingWriter(CallLog log)
    {
        _log = log;
    }

    public override Encoding Encoding => Encoding.UTF8;

    public string Text => _buffer.ToString();

    public int FlushCount { get; private set; }

    public override void Write(char value)
    {
        _buffer.Append(value);
        _log.Add(CallLog.StdoutWrite);
    }

    public override void Write(string? value)
    {
        if (value is null)
        {
            return;
        }

        _buffer.Append(value);
        _log.Add(CallLog.StdoutWrite);
    }

    public override void WriteLine(string? value)
    {
        _buffer.Append(value).Append('\n');
        _log.Add(CallLog.StdoutWrite);
    }

    public override void Flush()
    {
        FlushCount++;
        _log.Add(CallLog.StdoutFlush);
    }
}

/// <summary>
/// An <see cref="ICaptureSource"/> that returns a known synthetic pattern instead of the
/// desktop, so the crop rules can be asserted pixel-for-pixel without a display.
/// </summary>
public sealed class FakeCaptureSource : ICaptureSource
{
    private readonly CallLog _log;

    public FakeCaptureSource(CallLog log, Rectangle bounds)
    {
        _log = log;
        Bounds = bounds;
    }

    public Rectangle Bounds { get; }

    public int CaptureCount { get; private set; }

    public Rectangle? RequestedBounds { get; private set; }

    /// <summary>When set, alpha is left at 0 so a caller that forgets to force it fails.</summary>
    public bool LeaveAlphaTransparent { get; init; }

    public Rectangle GetTargetBounds() => Bounds;

    public Bitmap Capture(Rectangle bounds)
    {
        CaptureCount++;
        RequestedBounds = bounds;
        _log.Add(CallLog.Capture);
        return CreatePattern(bounds.Size, LeaveAlphaTransparent ? (byte)0 : (byte)255);
    }

    /// <summary>
    /// A pattern whose colour is a pure function of the pixel's position, so an off-by-one
    /// crop origin is visible as a wrong colour rather than as a plausible-looking picture.
    /// </summary>
    public static Bitmap CreatePattern(Size size, byte alpha = 255)
    {
        var bitmap = new Bitmap(size.Width, size.Height, PixelFormat.Format32bppArgb);
        for (int y = 0; y < size.Height; y++)
        {
            for (int x = 0; x < size.Width; x++)
            {
                bitmap.SetPixel(x, y, ExpectedColor(x, y, alpha));
            }
        }

        return bitmap;
    }

    public static Color ExpectedColor(int x, int y, byte alpha = 255)
        => Color.FromArgb(alpha, (byte)(x % 251), (byte)(y % 241), (byte)((x + y) % 239));
}

/// <summary>
/// An <see cref="IPickerDialog"/> that never puts a window on screen: it announces the frame
/// is shown, then returns a scripted outcome.
/// </summary>
public sealed class FakeDialog : IPickerDialog
{
    private readonly CallLog _log;
    private readonly PickerResult _result;

    public FakeDialog(CallLog log, PickerResult result)
    {
        _log = log;
        _result = result;
    }

    public event Action? FrameShown;

    public int ShowCount { get; private set; }

    public Size? ShownFrameSize { get; private set; }

    public Rectangle? ShownBounds { get; private set; }

    /// <summary>The bitmap handed to <see cref="Show"/>, cloned before the caller disposes it.</summary>
    public Bitmap? ShownFrame { get; private set; }

    public PickerResult Show(Bitmap frozenFrame, Rectangle bounds)
    {
        ShowCount++;
        ShownFrameSize = frozenFrame.Size;
        ShownBounds = bounds;
        ShownFrame = (Bitmap)frozenFrame.Clone();
        _log.Add(CallLog.Show);
        _log.Add(CallLog.FrameShown);
        FrameShown?.Invoke();
        return _result;
    }
}
