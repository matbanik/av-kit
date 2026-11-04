using System.Drawing;
using AvKit.RegionPicker;
using Xunit;

namespace AvKit.RegionPicker.Tests;

/// <summary>
/// AC-40.16 — the drag state machine. <c>RegionForm</c> maps each input event to exactly one
/// method here, so proving these transitions proves the picker's behaviour without putting a
/// window on screen.
/// </summary>
public class PickerControllerTests
{
    private static readonly Size Frame = new(1920, 1080);

    private static PickerController NewController() => new(Frame);

    [Fact]
    public void NewController_HasNotSettledAndIsNotDragging()
    {
        PickerController c = NewController();

        Assert.Equal(PickerResultKind.InProgress, c.Result.Kind);
        Assert.False(c.IsDragging);
        Assert.Equal(new Rectangle(0, 0, Frame.Width, Frame.Height), c.LocalBounds);
    }

    [Fact]
    public void BeginDrag_StartsDraggingWithAZeroAreaSelection()
    {
        PickerController c = NewController();

        c.BeginDrag(new Point(10, 10));

        Assert.True(c.IsDragging);
        Assert.Equal(PickerResultKind.InProgress, c.Result.Kind);
        Assert.False(RectMath.MeetsMinEdge(c.Selection));
    }

    [Fact]
    public void DragAndRelease_ConfirmsTheNormalizedRect()
    {
        PickerController c = NewController();

        c.BeginDrag(new Point(10, 10));
        c.UpdateDrag(new Point(120, 90));
        c.EndDrag(new Point(200, 150));

        Assert.False(c.IsDragging);
        Assert.Equal(PickerResultKind.Confirmed, c.Result.Kind);
        Assert.Equal(new Rectangle(10, 10, 190, 140), c.Result.Rect);
        Assert.Equal(c.Result.Rect, c.Selection);
    }

    [Fact]
    public void DragBackwards_ConfirmsTheSameRectAsDraggingForwards()
    {
        PickerController c = NewController();

        c.BeginDrag(new Point(200, 150));
        c.UpdateDrag(new Point(10, 10));
        c.EndDrag(new Point(10, 10));

        Assert.Equal(PickerResultKind.Confirmed, c.Result.Kind);
        Assert.Equal(new Rectangle(10, 10, 190, 140), c.Result.Rect);
    }

    [Fact]
    public void UpdateDrag_TracksTheLiveSelectionForTheRubberBand()
    {
        PickerController c = NewController();

        c.BeginDrag(new Point(100, 100));
        c.UpdateDrag(new Point(140, 130));

        Assert.Equal(new Rectangle(100, 100, 40, 30), c.Selection);
        Assert.Equal(PickerResultKind.InProgress, c.Result.Kind);
    }

    [Fact]
    public void ReleaseBelowMinimumEdge_Cancels_AndSavesNoRegion()
    {
        int min = PickerContract.PICKER_MIN_EDGE_PX;
        PickerController c = NewController();

        c.BeginDrag(new Point(100, 100));
        c.EndDrag(new Point(100 + min - 1, 100 + min * 4));

        Assert.False(c.IsDragging);
        Assert.Equal(PickerResultKind.Cancelled, c.Result.Kind);
        Assert.Equal(Rectangle.Empty, c.Result.Rect);
    }

    [Fact]
    public void ClickWithoutDragging_Cancels()
    {
        PickerController c = NewController();

        c.BeginDrag(new Point(500, 500));
        c.EndDrag(new Point(500, 500));

        Assert.Equal(PickerResultKind.Cancelled, c.Result.Kind);
    }

    [Fact]
    public void DragPastTheDisplayEdge_ConfirmsAClampedRect()
    {
        PickerController c = NewController();

        c.BeginDrag(new Point(1800, 1000));
        c.EndDrag(new Point(4000, 4000));

        Assert.Equal(PickerResultKind.Confirmed, c.Result.Kind);
        Assert.Equal(new Rectangle(1800, 1000, 120, 80), c.Result.Rect);
        Assert.True(c.LocalBounds.Contains(c.Result.Rect), $"{c.Result.Rect} escaped {c.LocalBounds}");
    }

    [Fact]
    public void DragPastTheTopLeftEdge_ConfirmsAClampedRect()
    {
        PickerController c = NewController();

        c.BeginDrag(new Point(300, 200));
        c.EndDrag(new Point(-500, -500));

        Assert.Equal(PickerResultKind.Confirmed, c.Result.Kind);
        Assert.Equal(new Rectangle(0, 0, 300, 200), c.Result.Rect);
        Assert.True(c.LocalBounds.Contains(c.Result.Rect), $"{c.Result.Rect} escaped {c.LocalBounds}");
    }

    [Fact]
    public void Cancel_SettlesAsCancelled_EvenMidDrag()
    {
        PickerController c = NewController();

        c.BeginDrag(new Point(10, 10));
        c.UpdateDrag(new Point(400, 400));
        c.Cancel();

        Assert.False(c.IsDragging);
        Assert.Equal(PickerResultKind.Cancelled, c.Result.Kind);
    }

    [Fact]
    public void Cancel_BeforeAnyDrag_SettlesAsCancelled()
    {
        PickerController c = NewController();

        c.Cancel();

        Assert.Equal(PickerResultKind.Cancelled, c.Result.Kind);
    }

    [Fact]
    public void Commit_AfterAValidDrag_ConfirmsTheCurrentSelection()
    {
        PickerController c = NewController();

        c.BeginDrag(new Point(10, 10));
        c.UpdateDrag(new Point(200, 150));
        c.Commit();

        Assert.Equal(PickerResultKind.Confirmed, c.Result.Kind);
        Assert.Equal(new Rectangle(10, 10, 190, 140), c.Result.Rect);
    }

    [Fact]
    public void Commit_WithABelowMinimumSelection_Cancels()
    {
        int min = PickerContract.PICKER_MIN_EDGE_PX;
        PickerController c = NewController();

        c.BeginDrag(new Point(10, 10));
        c.UpdateDrag(new Point(10 + min - 1, 10 + min - 1));
        c.Commit();

        Assert.Equal(PickerResultKind.Cancelled, c.Result.Kind);
    }

    [Fact]
    public void Commit_WithNoSelectionAtAll_Cancels()
    {
        PickerController c = NewController();

        c.Commit();

        Assert.Equal(PickerResultKind.Cancelled, c.Result.Kind);
    }

    [Fact]
    public void UpdateOrEndDrag_WithoutBeginDrag_IsIgnored()
    {
        PickerController c = NewController();

        c.UpdateDrag(new Point(400, 400));
        c.EndDrag(new Point(900, 900));

        Assert.Equal(PickerResultKind.InProgress, c.Result.Kind);
        Assert.False(c.IsDragging);
    }

    [Fact]
    public void InputAfterTheResultSettles_IsIgnored()
    {
        PickerController c = NewController();

        c.BeginDrag(new Point(10, 10));
        c.EndDrag(new Point(200, 150));
        PickerResult settled = c.Result;

        c.BeginDrag(new Point(600, 600));
        c.UpdateDrag(new Point(900, 900));
        c.EndDrag(new Point(900, 900));
        c.Cancel();

        Assert.Equal(settled, c.Result);
    }
}
