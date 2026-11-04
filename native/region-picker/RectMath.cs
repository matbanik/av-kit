using System.Drawing;

namespace AvKit.RegionPicker;

/// <summary>
/// All rectangle logic in the helper. <see cref="PickerController"/> is its only caller;
/// neither <see cref="RegionForm"/> nor <see cref="Program"/> may reimplement any of it.
/// Every coordinate here is a physical device pixel.
/// </summary>
public static class RectMath
{
    /// <summary>
    /// The axis-aligned rectangle spanned by two drag points, in either drag direction.
    /// Width and height are never negative.
    /// </summary>
    public static Rectangle Normalize(Point a, Point b)
    {
        int left = Math.Min(a.X, b.X);
        int top = Math.Min(a.Y, b.Y);
        int width = Math.Abs(a.X - b.X);
        int height = Math.Abs(a.Y - b.Y);

        return new Rectangle(left, top, width, height);
    }

    /// <summary>
    /// True iff both edges meet <see cref="PickerContract.PICKER_MIN_EDGE_PX"/>. A rect that
    /// fails this is a cancel, not a tiny capture.
    /// </summary>
    public static bool MeetsMinEdge(Rectangle rect)
        => rect.Width >= PickerContract.PICKER_MIN_EDGE_PX
           && rect.Height >= PickerContract.PICKER_MIN_EDGE_PX;

    /// <summary>
    /// Intersects <paramref name="rect"/> with <paramref name="bounds"/> so a drag that leaves
    /// the display can never produce an out-of-range crop. Callers clamp in LOCAL space.
    /// </summary>
    public static Rectangle ClampToBounds(Rectangle rect, Rectangle bounds)
        => Rectangle.Intersect(rect, bounds);

    /// <summary>Maps a global (virtual-screen) point into the frozen frame's local space.</summary>
    public static Point ToLocal(Point globalPoint, Point origin)
        => new(globalPoint.X - origin.X, globalPoint.Y - origin.Y);

    /// <summary>Maps a global (virtual-screen) rectangle into the frozen frame's local space.</summary>
    public static Rectangle ToLocal(Rectangle globalRect, Point origin)
        => new(globalRect.X - origin.X, globalRect.Y - origin.Y, globalRect.Width, globalRect.Height);
}
