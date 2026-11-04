using System.ComponentModel;
using System.Drawing;
using System.Drawing.Imaging;
using System.Runtime.InteropServices;
using System.Windows.Forms;

namespace AvKit.RegionPicker;

/// <summary>
/// The GDI implementation of <see cref="ICaptureSource"/>: freeze the display under the
/// cursor into a 32-bpp opaque bitmap, before any picker window exists.
/// </summary>
public sealed class ScreenCaptureSource : ICaptureSource
{
    /// <summary>
    /// The display under the cursor at launch. Its origin may be negative (a monitor left of
    /// or above the primary) and its size is not any other monitor's, so no caller may assume
    /// either.
    /// </summary>
    public Rectangle GetTargetBounds()
    {
        Screen target = Screen.FromPoint(Cursor.Position);
        return target.Bounds;
    }

    /// <summary>
    /// Grabs <paramref name="bounds"/> from the desktop. <c>CaptureBlt</c> is required, not
    /// optional: without it layered windows (tooltips, overlays, most Electron menus) come
    /// back as holes in the frozen frame.
    /// </summary>
    public Bitmap Capture(Rectangle bounds)
    {
        if (bounds.Width <= 0 || bounds.Height <= 0)
        {
            throw new ArgumentOutOfRangeException(
                nameof(bounds),
                bounds,
                "the target display reported an empty bounds rectangle");
        }

        var bitmap = new Bitmap(bounds.Width, bounds.Height, PixelFormat.Format32bppArgb);
        try
        {
            BlitFromScreen(bitmap, bounds);

            ForceOpaque(bitmap);
            return bitmap;
        }
        catch
        {
            bitmap.Dispose();
            throw;
        }
    }

    /// <summary>
    /// Blits <paramref name="bounds"/> of the virtual screen into <paramref name="bitmap"/>.
    ///
    /// This goes to <c>BitBlt</c> directly rather than through
    /// <see cref="Graphics.CopyFromScreen(int, int, int, int, Size, CopyPixelOperation)"/>:
    /// that overload validates its argument against the <see cref="CopyPixelOperation"/> enum
    /// and throws <see cref="InvalidEnumArgumentException"/> for
    /// <c>SourceCopy | CaptureBlt</c>, because the combination is not itself a declared enum
    /// member. CaptureBlt is not optional here — without it layered windows come back as
    /// holes — so the managed wrapper cannot express what this helper needs.
    /// </summary>
    private static void BlitFromScreen(Bitmap bitmap, Rectangle bounds)
    {
        using Graphics graphics = Graphics.FromImage(bitmap);

        IntPtr destination = graphics.GetHdc();
        try
        {
            IntPtr screen = GetDC(IntPtr.Zero);
            if (screen == IntPtr.Zero)
            {
                throw new Win32Exception(Marshal.GetLastWin32Error(), "could not open a device context for the screen");
            }

            try
            {
                if (!BitBlt(
                        destination,
                        0,
                        0,
                        bounds.Width,
                        bounds.Height,
                        screen,
                        bounds.X,
                        bounds.Y,
                        SRCCOPY | CAPTUREBLT))
                {
                    throw new Win32Exception(Marshal.GetLastWin32Error(), "the screen blit failed");
                }
            }
            finally
            {
                ReleaseDC(IntPtr.Zero, screen);
            }
        }
        finally
        {
            graphics.ReleaseHdc(destination);
        }
    }

    private const uint SRCCOPY = 0x00CC0020;

    /// <summary>Include layered windows (tooltips, overlays, most Electron menus) in the blit.</summary>
    private const uint CAPTUREBLT = 0x40000000;

    [DllImport("user32.dll", SetLastError = true)]
    private static extern IntPtr GetDC(IntPtr hWnd);

    [DllImport("user32.dll")]
    private static extern int ReleaseDC(IntPtr hWnd, IntPtr hDC);

    [DllImport("gdi32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool BitBlt(
        IntPtr hdcDest,
        int x,
        int y,
        int cx,
        int cy,
        IntPtr hdcSrc,
        int x1,
        int y1,
        uint rop);

    /// <summary>
    /// Forces every pixel's alpha byte to 255. A GDI blit writes no meaningful alpha, and a
    /// PNG carrying whatever BitBlt happened to leave there is the "screenshot is invisible
    /// in some viewers" bug.
    /// </summary>
    public static void ForceOpaque(Bitmap bitmap)
    {
        ArgumentNullException.ThrowIfNull(bitmap);

        var area = new Rectangle(Point.Empty, bitmap.Size);
        if (area.Width == 0 || area.Height == 0)
        {
            return;
        }

        BitmapData data = bitmap.LockBits(area, ImageLockMode.ReadWrite, PixelFormat.Format32bppArgb);
        try
        {
            int rowBytes = area.Width * 4;
            byte[] row = new byte[rowBytes];

            for (int y = 0; y < area.Height; y++)
            {
                IntPtr line = IntPtr.Add(data.Scan0, y * data.Stride);
                Marshal.Copy(line, row, 0, rowBytes);

                // BGRA in memory: the alpha byte is the fourth of every quad.
                for (int offset = 3; offset < rowBytes; offset += 4)
                {
                    row[offset] = 255;
                }

                Marshal.Copy(row, 0, line, rowBytes);
            }
        }
        finally
        {
            bitmap.UnlockBits(data);
        }
    }
}
