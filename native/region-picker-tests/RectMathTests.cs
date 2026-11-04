using System.Drawing;
using AvKit.RegionPicker;
using Xunit;

namespace AvKit.RegionPicker.Tests;

/// <summary>AC-40.1, AC-40.2, AC-40.3 — the helper's whole geometry contract.</summary>
public class RectMathTests
{
    // ---- AC-40.1: Normalize -------------------------------------------------

    [Theory]
    // top-left -> bottom-right
    [InlineData(10, 10, 50, 40, 10, 10, 40, 30)]
    // bottom-right -> top-left (the same rectangle, dragged backwards)
    [InlineData(50, 40, 10, 10, 10, 10, 40, 30)]
    // top-right -> bottom-left
    [InlineData(50, 10, 10, 40, 10, 10, 40, 30)]
    // bottom-left -> top-right
    [InlineData(10, 40, 50, 10, 10, 10, 40, 30)]
    // negative virtual-screen coordinates (a monitor left of and above the primary)
    [InlineData(-100, -80, -20, -10, -100, -80, 80, 70)]
    [InlineData(-20, -10, -100, -80, -100, -80, 80, 70)]
    public void Normalize_ReturnsAxisAlignedRect_ForEitherDragDirection(
        int ax, int ay, int bx, int by, int ex, int ey, int ew, int eh)
    {
        Rectangle actual = RectMath.Normalize(new Point(ax, ay), new Point(bx, by));

        Assert.Equal(new Rectangle(ex, ey, ew, eh), actual);
    }

    [Fact]
    public void Normalize_NeverReturnsNegativeExtent()
    {
        Rectangle actual = RectMath.Normalize(new Point(500, 500), new Point(0, 0));

        Assert.True(actual.Width >= 0, $"width was {actual.Width}");
        Assert.True(actual.Height >= 0, $"height was {actual.Height}");
    }

    [Fact]
    public void Normalize_EqualPoints_ProducesZeroAreaRect()
    {
        Rectangle actual = RectMath.Normalize(new Point(33, 44), new Point(33, 44));

        Assert.Equal(new Rectangle(33, 44, 0, 0), actual);
        Assert.False(RectMath.MeetsMinEdge(actual));
    }

    // ---- AC-40.2: MeetsMinEdge ---------------------------------------------

    [Fact]
    public void MeetsMinEdge_ExactlyMinimumSquare_IsAccepted()
    {
        int min = PickerContract.PICKER_MIN_EDGE_PX;

        Assert.True(RectMath.MeetsMinEdge(new Rectangle(0, 0, min, min)));
    }

    [Fact]
    public void MeetsMinEdge_OneBelowMinimumWidth_IsRejected()
    {
        int min = PickerContract.PICKER_MIN_EDGE_PX;

        Assert.False(RectMath.MeetsMinEdge(new Rectangle(0, 0, min - 1, min * 10)));
    }

    [Fact]
    public void MeetsMinEdge_OneBelowMinimumHeight_IsRejected()
    {
        int min = PickerContract.PICKER_MIN_EDGE_PX;

        Assert.False(RectMath.MeetsMinEdge(new Rectangle(0, 0, min * 10, min - 1)));
    }

    [Fact]
    public void MeetsMinEdge_EmptyRect_IsRejected()
    {
        Assert.False(RectMath.MeetsMinEdge(Rectangle.Empty));
    }

    // ---- AC-40.3: ClampToBounds --------------------------------------------

    [Fact]
    public void ClampToBounds_RectInsideBounds_IsUnchanged()
    {
        var bounds = new Rectangle(0, 0, 1920, 1080);
        var rect = new Rectangle(100, 200, 300, 400);

        Assert.Equal(rect, RectMath.ClampToBounds(rect, bounds));
    }

    [Theory]
    // past the right/bottom edges
    [InlineData(1800, 1000, 400, 400, 1800, 1000, 120, 80)]
    // past the left/top edges (a drag that started inside and left the display)
    [InlineData(-200, -100, 400, 400, 0, 0, 200, 300)]
    // larger than the display in both axes
    [InlineData(-50, -50, 5000, 5000, 0, 0, 1920, 1080)]
    public void ClampToBounds_NeverExceedsTheFrozenBitmap(
        int rx, int ry, int rw, int rh, int ex, int ey, int ew, int eh)
    {
        var bounds = new Rectangle(0, 0, 1920, 1080);

        Rectangle actual = RectMath.ClampToBounds(new Rectangle(rx, ry, rw, rh), bounds);

        Assert.Equal(new Rectangle(ex, ey, ew, eh), actual);
        Assert.True(bounds.Contains(actual), $"{actual} escaped {bounds}");
    }

    [Fact]
    public void ClampToBounds_FullyOutsideRect_CollapsesToEmpty()
    {
        var bounds = new Rectangle(0, 0, 1920, 1080);

        Rectangle actual = RectMath.ClampToBounds(new Rectangle(4000, 4000, 100, 100), bounds);

        Assert.True(actual.Width == 0 || actual.Height == 0, $"expected a degenerate rect, got {actual}");
        Assert.False(RectMath.MeetsMinEdge(actual));
    }

    // ---- Global -> local ----------------------------------------------------

    [Theory]
    [InlineData(0, 0, 100, 50, 100, 50)]
    [InlineData(-1920, -300, -1820, -250, 100, 50)]
    [InlineData(2560, 0, 2660, 50, 100, 50)]
    public void ToLocal_Point_SubtractsTheDisplayOrigin(
        int ox, int oy, int gx, int gy, int ex, int ey)
    {
        Assert.Equal(new Point(ex, ey), RectMath.ToLocal(new Point(gx, gy), new Point(ox, oy)));
    }

    [Fact]
    public void ToLocal_Rectangle_SubtractsTheDisplayOriginAndKeepsSize()
    {
        var origin = new Point(-1920, -300);
        var global = new Rectangle(-1820, -250, 640, 480);

        Assert.Equal(new Rectangle(100, 50, 640, 480), RectMath.ToLocal(global, origin));
    }
}
