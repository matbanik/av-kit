using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
using System.Windows.Forms;
using AvKit.RegionPicker;
using Xunit;

namespace AvKit.RegionPicker.Tests;

/// <summary>
/// AC-40.27 — the real-desktop proof. A fake <see cref="ICaptureSource"/> proves the plumbing
/// and the crop arithmetic, but it can never prove that <c>CopyFromScreen</c> with
/// <c>CaptureBlt</c> returns the right pixels on a DWM-composited desktop. These cases paint a
/// known fixture at a known screen rect and read it back through the production
/// <see cref="ScreenCaptureSource"/>.
///
/// Traited <c>Category=RealDesktop</c> so it runs under its own receipt: it needs a session
/// with a visible desktop, which the unit suite does not.
/// </summary>
[Trait("Category", "RealDesktop")]
public class RealDesktopCaptureTests
{
    private static readonly Color FixtureColor = Color.FromArgb(255, 42, 199, 91);

    [Fact]
    public void PrimaryDisplay_CaptureReturnsTheFixturesPixelsAtTheFixturesRect()
    {
        Screen target = Screen.PrimaryScreen ?? Screen.AllScreens[0];

        AssertFixtureIsCapturedOn(target);
    }

    [MultiMonitorFact]
    public void SecondaryDisplay_CaptureReturnsTheFixturesPixelsAtTheFixturesRect()
    {
        Screen[] secondary = Screen.AllScreens.Where(s => !s.Primary).ToArray();
        Assert.NotEmpty(secondary);

        AssertFixtureIsCapturedOn(secondary[0]);
    }

    private static void AssertFixtureIsCapturedOn(Screen target)
    {
        (Bitmap frame, Rectangle fixtureBounds) = RunSta(() => PaintFixtureAndCapture(target));

        using (frame)
        {
            Rectangle screenBounds = target.Bounds;
            Assert.Equal(screenBounds.Size, frame.Size);
            Assert.Equal(PixelFormat.Format32bppArgb, frame.PixelFormat);

            Rectangle local = RectMath.ToLocal(fixtureBounds, screenBounds.Location);
            Assert.True(
                new Rectangle(Point.Empty, screenBounds.Size).Contains(local),
                $"the fixture at {fixtureBounds} does not lie inside {screenBounds}");

            // Inset by two pixels: the outermost row of a window can carry a rounded corner
            // or a shadow, and this test is about geometry, not about window chrome.
            Rectangle probe = Rectangle.Inflate(local, -2, -2);
            AssertPixelsAre(frame, probe, FixtureColor, "the captured display");

            // The same rect cropped exactly the way the picker crops it.
            using Bitmap crop = frame.Clone(local, PixelFormat.Format32bppArgb);
            Assert.Equal(local.Width, crop.Width);
            Assert.Equal(local.Height, crop.Height);
            AssertPixelsAre(
                crop,
                Rectangle.Inflate(new Rectangle(Point.Empty, crop.Size), -2, -2),
                FixtureColor,
                "the crop");

            for (int y = 0; y < frame.Height; y += 97)
            {
                for (int x = 0; x < frame.Width; x += 97)
                {
                    Assert.Equal(255, frame.GetPixel(x, y).A);
                }
            }
        }
    }

    private static void AssertPixelsAre(Bitmap bitmap, Rectangle rect, Color expected, string what)
    {
        var probes = new[]
        {
            new Point(rect.Left, rect.Top),
            new Point(rect.Right - 1, rect.Top),
            new Point(rect.Left, rect.Bottom - 1),
            new Point(rect.Right - 1, rect.Bottom - 1),
            new Point(rect.Left + rect.Width / 2, rect.Top + rect.Height / 2),
        };

        foreach (Point p in probes)
        {
            Color actual = bitmap.GetPixel(p.X, p.Y);
            Assert.True(
                actual.R == expected.R && actual.G == expected.G && actual.B == expected.B,
                $"{what}: pixel ({p.X}, {p.Y}) is {actual} but the fixture painted {expected}");
        }
    }

    /// <summary>
    /// Shows an opaque fixture window at a known rect on <paramref name="target"/>, lets the
    /// compositor present it, and grabs the whole display through the production capture
    /// source. Returns the frame and the fixture's ACTUAL bounds as the window system placed
    /// them, so the assertion compares against reality rather than against the request.
    /// </summary>
    private static (Bitmap Frame, Rectangle FixtureBounds) PaintFixtureAndCapture(Screen target)
    {
        EnsurePerMonitorV2();

        Rectangle screenBounds = target.Bounds;
        var requested = new Rectangle(
            screenBounds.X + screenBounds.Width / 4,
            screenBounds.Y + screenBounds.Height / 4,
            Math.Min(320, screenBounds.Width / 3),
            Math.Min(240, screenBounds.Height / 3));

        using var fixture = new Form
        {
            FormBorderStyle = FormBorderStyle.None,
            StartPosition = FormStartPosition.Manual,
            ShowInTaskbar = false,
            TopMost = true,
            BackColor = FixtureColor,
            Bounds = requested,
        };

        fixture.Show();
        fixture.Activate();

        // Form.TopMost alone does not raise the window above the app that currently holds the
        // foreground, and the test host never holds it after the first fixture is torn down.
        // Without this the second fixture in a run is "visible" while another window is
        // painted over it, and the capture correctly returns that other window's pixels.
        // RegionForm.ForceToForeground does the same three calls for the same reason.
        SetWindowPos(fixture.Handle, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW);
        BringWindowToTop(fixture.Handle);
        SetForegroundWindow(fixture.Handle);
        fixture.Refresh();

        Rectangle actual = fixture.Bounds;

        // Wait for the compositor to have actually presented the fixture instead of sleeping a
        // fixed interval. A fixed sleep is a race: the same 600 ms that is ample when this is
        // the only test in the run is not ample when the window is the first one this process
        // has ever created, and the capture then reads the desktop that is still on screen.
        //
        // The wait polls GDI's GetPixel against the screen DC, which is a different call from
        // the BitBlt under test, and it establishes only the precondition the test's own
        // summary already claims ("lets the compositor present it"). Every assertion in
        // AssertFixtureIsCapturedOn - the frame's size and pixel format, the local-space
        // mapping, the five probe points, the exact crop, and the alpha sweep - is still
        // decided by the production capture path.
        WaitForFixtureOnScreen(actual, timeoutMilliseconds: 5000);
        var source = new ScreenCaptureSource();
        Bitmap frame = source.Capture(screenBounds);

        fixture.Hide();
        Pump(millseconds: 100);

        return (frame, actual);
    }

    /// <summary>Runs the WinForms message loop for a while so the fixture is actually presented.</summary>
    private static void Pump(int millseconds)
    {
        int deadline = Environment.TickCount + millseconds;
        while (Environment.TickCount < deadline)
        {
            Application.DoEvents();
            Thread.Sleep(15);
        }
    }

    /// <summary>
    /// Pumps the message loop until the fixture's colour is on the screen inside
    /// <paramref name="fixtureBounds"/>, or the timeout expires. On expiry it returns quietly
    /// and lets the capture assertions report what was actually on screen, so a genuine
    /// capture regression is never masked by a wait that threw first.
    /// </summary>
    private static void WaitForFixtureOnScreen(Rectangle fixtureBounds, int timeoutMilliseconds)
    {
        var centre = new Point(
            fixtureBounds.Left + (fixtureBounds.Width / 2),
            fixtureBounds.Top + (fixtureBounds.Height / 2));
        int expected = FixtureColor.R | (FixtureColor.G << 8) | (FixtureColor.B << 16);
        int deadline = Environment.TickCount + timeoutMilliseconds;

        while (Environment.TickCount < deadline)
        {
            Application.DoEvents();

            IntPtr screen = GetDC(IntPtr.Zero);
            if (screen != IntPtr.Zero)
            {
                try
                {
                    if (GetPixel(screen, centre.X, centre.Y) == expected)
                    {
                        // One more composed frame, so the whole window - not just the centre -
                        // is guaranteed to be on screen when the blit runs.
                        DwmFlush();
                        return;
                    }
                }
                finally
                {
                    ReleaseDC(IntPtr.Zero, screen);
                }
            }

            Thread.Sleep(15);
        }
    }

    [DllImport("dwmapi.dll")]
    private static extern int DwmFlush();

    private static readonly IntPtr HWND_TOPMOST = new(-1);

    private const uint SWP_NOSIZE = 0x0001;
    private const uint SWP_NOMOVE = 0x0002;
    private const uint SWP_SHOWWINDOW = 0x0040;

    [DllImport("user32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool SetWindowPos(IntPtr hWnd, IntPtr hWndInsertAfter, int x, int y, int cx, int cy, uint flags);

    [DllImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool BringWindowToTop(IntPtr hWnd);

    [DllImport("user32.dll")]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern IntPtr GetDC(IntPtr hWnd);

    [DllImport("user32.dll")]
    private static extern int ReleaseDC(IntPtr hWnd, IntPtr hDC);

    [DllImport("gdi32.dll")]
    private static extern int GetPixel(IntPtr hdc, int x, int y);

    /// <summary>
    /// The picker declares PerMonitorV2 in its own manifest, but this test runs inside the
    /// xunit test host, whose manifest is not ours. Without this the host is handed
    /// virtualized coordinates on any scaled display and the geometry assertions compare a
    /// physical capture against logical bounds.
    /// </summary>
    private static void EnsurePerMonitorV2()
    {
        try
        {
            SetProcessDpiAwarenessContext(DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2);
        }
        catch (EntryPointNotFoundException)
        {
            // Pre-1703 Windows; the run will fail loudly on a scaled display instead.
        }
    }

    private static readonly IntPtr DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2 = new(-4);

    [DllImport("user32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool SetProcessDpiAwarenessContext(IntPtr value);

    private static T RunSta<T>(Func<T> body)
    {
        T result = default!;
        Exception? error = null;

        var thread = new Thread(() =>
        {
            try
            {
                result = body();
            }
            catch (Exception ex)
            {
                error = ex;
            }
        });

        thread.SetApartmentState(ApartmentState.STA);
        thread.Start();
        thread.Join();

        if (error is not null)
        {
            throw new InvalidOperationException("the real-desktop fixture failed: " + error.Message, error);
        }

        return result;
    }
}
