using System.Drawing;
using System.Drawing.Imaging;
using AvKit.RegionPicker;
using Xunit;

namespace AvKit.RegionPicker.Tests;

/// <summary>
/// AC-40.25 (global -> local mapping on a hostile monitor layout) and AC-40.26 (freeze before
/// the window exists; opaque 32-bpp pixels; an exact, unresampled crop).
/// </summary>
public class CaptureGeometryTests
{
    /// <summary>
    /// A synthetic display with a negative origin — a monitor left of and above the primary.
    /// Kept small so the per-pixel pattern is cheap to generate; the origin is what matters.
    /// </summary>
    private static readonly Rectangle NegativeOriginBounds = new(-1920, -300, 400, 300);

    private sealed record Harness(
        CallLog Log,
        FakeCaptureSource Capture,
        FakeDialog Dialog,
        RecordingWriter Stdout,
        RecordingWriter Stderr);

    private static Harness NewHarness(Rectangle bounds, Rectangle localSelection, bool transparentSource = false)
    {
        var log = new CallLog();
        return new Harness(
            log,
            new FakeCaptureSource(log, bounds) { LeaveAlphaTransparent = transparentSource },
            new FakeDialog(log, PickerResult.Confirmed(localSelection)),
            new RecordingWriter(log),
            new RecordingWriter(new CallLog()));
    }

    private static int Run(Harness h, string outPath)
        => Program.Run(new[] { "--out", outPath }, h.Capture, h.Dialog, h.Stdout, h.Stderr);

    // ---- AC-40.26(a): the freeze precedes the window -----------------------

    [Fact]
    public void TheFrameIsCaptured_BeforeTheDialogIsShown()
    {
        using var temp = new TempDir();
        Harness h = NewHarness(NegativeOriginBounds, new Rectangle(10, 20, 100, 80));

        Run(h, temp.OutFile);

        int capture = h.Log.IndexOf(CallLog.Capture);
        int show = h.Log.IndexOf(CallLog.Show);

        Assert.True(capture >= 0, "the frame was never captured: " + h.Log);
        Assert.True(show >= 0, "the dialog was never shown: " + h.Log);
        Assert.True(capture < show, "the window was shown before the freeze: " + h.Log);
    }

    [Fact]
    public void TheCaptureIsRequestedForTheTargetDisplayBounds()
    {
        using var temp = new TempDir();
        Harness h = NewHarness(NegativeOriginBounds, new Rectangle(10, 20, 100, 80));

        Run(h, temp.OutFile);

        Assert.Equal(1, h.Capture.CaptureCount);
        Assert.Equal(NegativeOriginBounds, h.Capture.RequestedBounds);
        Assert.Equal(NegativeOriginBounds, h.Dialog.ShownBounds);
        Assert.Equal(NegativeOriginBounds.Size, h.Dialog.ShownFrameSize);
    }

    // ---- AC-40.26(b): alpha is forced opaque -------------------------------

    [Fact]
    public void TheFrameHandedToTheDialog_IsFullyOpaque32Bpp()
    {
        using var temp = new TempDir();
        Harness h = NewHarness(NegativeOriginBounds, new Rectangle(10, 20, 100, 80), transparentSource: true);

        Run(h, temp.OutFile);

        Bitmap? frame = h.Dialog.ShownFrame;
        Assert.NotNull(frame);
        Assert.Equal(PixelFormat.Format32bppArgb, frame!.PixelFormat);
        AssertFullyOpaque(frame, "the frozen frame");
    }

    [Fact]
    public void TheSavedPng_IsFullyOpaque_EvenWhenTheBlitLeftAlphaAtZero()
    {
        using var temp = new TempDir();
        var selection = new Rectangle(10, 20, 100, 80);
        Harness h = NewHarness(NegativeOriginBounds, selection, transparentSource: true);

        int code = Run(h, temp.OutFile);

        Assert.Equal(PickerContract.PICKER_EXIT_CONFIRM, code);
        using var saved = new Bitmap(temp.OutFile);
        AssertFullyOpaque(saved, "the saved PNG");
    }

    private static void AssertFullyOpaque(Bitmap bitmap, string what)
    {
        for (int y = 0; y < bitmap.Height; y++)
        {
            for (int x = 0; x < bitmap.Width; x++)
            {
                byte alpha = bitmap.GetPixel(x, y).A;
                if (alpha != 255)
                {
                    Assert.Fail($"{what} has alpha {alpha} at ({x}, {y}); every pixel must be opaque");
                }
            }
        }
    }

    // ---- AC-40.26(c)(d): the crop is exact ---------------------------------

    [Theory]
    [InlineData(0, 0, 40, 30)]
    [InlineData(10, 20, 100, 80)]
    [InlineData(311, 217, 89, 83)]
    public void TheSavedPng_HasExactlyTheSelectionsSize_WithNoResampling(int x, int y, int w, int h)
    {
        using var temp = new TempDir();
        var selection = new Rectangle(x, y, w, h);
        Harness harness = NewHarness(NegativeOriginBounds, selection);

        int code = Run(harness, temp.OutFile);

        Assert.Equal(PickerContract.PICKER_EXIT_CONFIRM, code);
        using var saved = new Bitmap(temp.OutFile);
        Assert.Equal(selection.Width, saved.Width);
        Assert.Equal(selection.Height, saved.Height);
    }

    [Fact]
    public void TheSavedPng_MatchesThePattern_AtTheFourCornersAndTheCentre()
    {
        using var temp = new TempDir();
        var selection = new Rectangle(37, 61, 120, 90);
        Harness h = NewHarness(NegativeOriginBounds, selection);

        int code = Run(h, temp.OutFile);
        Assert.Equal(PickerContract.PICKER_EXIT_CONFIRM, code);

        using var saved = new Bitmap(temp.OutFile);
        var probes = new[]
        {
            new Point(0, 0),
            new Point(selection.Width - 1, 0),
            new Point(0, selection.Height - 1),
            new Point(selection.Width - 1, selection.Height - 1),
            new Point(selection.Width / 2, selection.Height / 2),
        };

        foreach (Point p in probes)
        {
            Color expected = FakeCaptureSource.ExpectedColor(selection.X + p.X, selection.Y + p.Y);
            Color actual = saved.GetPixel(p.X, p.Y);

            Assert.True(
                expected.ToArgb() == actual.ToArgb(),
                $"crop pixel ({p.X}, {p.Y}) is {actual} but the desktop pixel at " +
                $"({selection.X + p.X}, {selection.Y + p.Y}) is {expected} — the crop origin is off");
        }
    }

    // ---- AC-40.25: global -> local on a hostile layout ---------------------

    public static TheoryData<int, int, int, int> Layouts => new()
    {
        // a monitor left of and above the primary: signed virtual-screen coordinates
        { -1920, -300, 1920, 1080 },
        // a monitor right of the primary, positive but non-zero origin
        { 2560, 0, 2560, 1440 },
        // the high-DPI half of a mixed-scale pair: different origin AND different size
        { 1920, -420, 3840, 2160 },
        // the primary itself, the only (0,0) in the virtual screen
        { 0, 0, 1920, 1080 },
    };

    [Theory]
    [MemberData(nameof(Layouts))]
    public void ADragInsideTheDisplay_MapsToLocalBySubtractingTheOrigin(int bx, int by, int bw, int bh)
    {
        var bounds = new Rectangle(bx, by, bw, bh);
        var globalA = new Point(bx + 100, by + 50);
        var globalB = new Point(bx + 340, by + 230);

        Rectangle local = MapAndClamp(globalA, globalB, bounds);

        Assert.Equal(new Rectangle(100, 50, 240, 180), local);
    }

    [Theory]
    [MemberData(nameof(Layouts))]
    public void ADragThatLeavesAnyEdge_ClampsInsideTheFrozenBitmap(int bx, int by, int bw, int bh)
    {
        var bounds = new Rectangle(bx, by, bw, bh);
        var frame = new Rectangle(Point.Empty, bounds.Size);
        var anchor = new Point(bx + bw / 2, by + bh / 2);

        var escapes = new[]
        {
            new Point(bx - 500, anchor.Y + 200),        // left
            new Point(bx + bw + 500, anchor.Y + 200),   // right
            new Point(anchor.X + 200, by - 500),        // top
            new Point(anchor.X + 200, by + bh + 500),   // bottom
            new Point(bx - 500, by - 500),              // top-left corner
            new Point(bx + bw + 500, by + bh + 500),    // bottom-right corner
        };

        foreach (Point escape in escapes)
        {
            Rectangle local = MapAndClamp(anchor, escape, bounds);

            Assert.True(
                frame.Contains(local),
                $"drag {anchor} -> {escape} on {bounds} produced {local}, which escapes {frame}");
            Assert.True(
                RectMath.MeetsMinEdge(local),
                $"drag {anchor} -> {escape} on {bounds} collapsed to {local}");
        }
    }

    [Fact]
    public void ClampingHappensInLocalSpace_SoANegativeOriginCannotProduceAnOutOfRangeCrop()
    {
        var bounds = new Rectangle(-1920, -300, 1920, 1080);
        var frame = new Rectangle(Point.Empty, bounds.Size);

        // A drag anchored near the display's top-left, escaping past it. Subtracting the
        // origin AFTER clamping in global space is the bug this asserts against: it would
        // leave the rect at a positive global offset and index far outside the bitmap.
        Rectangle local = MapAndClamp(new Point(-1900, -280), new Point(-2500, -900), bounds);

        Assert.Equal(new Rectangle(0, 0, 20, 20), local);
        Assert.True(frame.Contains(local), local + " escapes " + frame);
    }

    private static Rectangle MapAndClamp(Point globalA, Point globalB, Rectangle bounds)
    {
        Point localA = RectMath.ToLocal(globalA, bounds.Location);
        Point localB = RectMath.ToLocal(globalB, bounds.Location);
        Rectangle rect = RectMath.Normalize(localA, localB);
        return RectMath.ClampToBounds(rect, new Rectangle(Point.Empty, bounds.Size));
    }
}
