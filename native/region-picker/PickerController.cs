using System.Drawing;

namespace AvKit.RegionPicker;

public enum PickerResultKind
{
    /// <summary>The user has not settled the selection yet.</summary>
    InProgress,

    /// <summary>A region meeting the minimum edge was confirmed.</summary>
    Confirmed,

    /// <summary>Esc, or a release below the minimum edge. No pixels are saved.</summary>
    Cancelled,
}

/// <summary>
/// The settled outcome of one picker session. <see cref="Rect"/> is in LOCAL frame
/// coordinates and is already clamped to the frozen bitmap, so it is safe to crop with.
/// </summary>
public readonly struct PickerResult : IEquatable<PickerResult>
{
    private PickerResult(PickerResultKind kind, Rectangle rect)
    {
        Kind = kind;
        Rect = rect;
    }

    public PickerResultKind Kind { get; }

    public Rectangle Rect { get; }

    public static PickerResult InProgress { get; } = new(PickerResultKind.InProgress, Rectangle.Empty);

    public static PickerResult Cancelled { get; } = new(PickerResultKind.Cancelled, Rectangle.Empty);

    public static PickerResult Confirmed(Rectangle rect) => new(PickerResultKind.Confirmed, rect);

    public bool Equals(PickerResult other) => Kind == other.Kind && Rect == other.Rect;

    public override bool Equals(object? obj) => obj is PickerResult other && Equals(other);

    public override int GetHashCode() => HashCode.Combine(Kind, Rect);

    public override string ToString() => $"{Kind}({Rect})";

    public static bool operator ==(PickerResult left, PickerResult right) => left.Equals(right);

    public static bool operator !=(PickerResult left, PickerResult right) => !left.Equals(right);
}

/// <summary>
/// The tested owner of drag state. <see cref="RegionForm"/> maps each input event to exactly
/// one method here and holds no geometry of its own, so the picker's behaviour can be proven
/// without putting a window on screen.
/// </summary>
public sealed class PickerController
{
    private Point _anchor;

    /// <param name="frameSize">Size of the frozen frame, in physical pixels.</param>
    public PickerController(Size frameSize)
    {
        LocalBounds = new Rectangle(Point.Empty, frameSize);
    }

    /// <summary>The frozen frame in local space — origin is always (0,0), by construction.</summary>
    public Rectangle LocalBounds { get; }

    /// <summary>True between <see cref="BeginDrag"/> and the release that ends it.</summary>
    public bool IsDragging { get; private set; }

    /// <summary>The live selection, normalized and clamped, for the rubber band to draw.</summary>
    public Rectangle Selection { get; private set; }

    /// <summary>Settles once and stays settled; later input is ignored.</summary>
    public PickerResult Result { get; private set; } = PickerResult.InProgress;

    private bool IsSettled => Result.Kind != PickerResultKind.InProgress;

    public void BeginDrag(Point local)
    {
        if (IsSettled)
        {
            return;
        }

        _anchor = local;
        IsDragging = true;
        Selection = Track(local);
    }

    public void UpdateDrag(Point local)
    {
        if (IsSettled || !IsDragging)
        {
            return;
        }

        Selection = Track(local);
    }

    public void EndDrag(Point local)
    {
        if (IsSettled || !IsDragging)
        {
            return;
        }

        Selection = Track(local);
        IsDragging = false;
        Settle();
    }

    /// <summary>Esc.</summary>
    public void Cancel()
    {
        if (IsSettled)
        {
            return;
        }

        IsDragging = false;
        Result = PickerResult.Cancelled;
    }

    /// <summary>Enter — confirms the current selection if it meets the minimum edge.</summary>
    public void Commit()
    {
        if (IsSettled)
        {
            return;
        }

        IsDragging = false;
        Settle();
    }

    /// <summary>
    /// The selection for a drag ending at <paramref name="local"/>. Clamping is in LOCAL
    /// space against the frozen frame, so a drag that leaves the display can never index
    /// outside the bitmap.
    /// </summary>
    private Rectangle Track(Point local)
        => RectMath.ClampToBounds(RectMath.Normalize(_anchor, local), LocalBounds);

    /// <summary>
    /// A release or an Enter is the same decision: a region meeting the minimum edge is a
    /// confirm, anything smaller is a cancel — never a tiny capture.
    /// </summary>
    private void Settle()
        => Result = RectMath.MeetsMinEdge(Selection)
            ? PickerResult.Confirmed(Selection)
            : PickerResult.Cancelled;
}
