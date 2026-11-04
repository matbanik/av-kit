using System.Drawing;
using System.Drawing.Drawing2D;
using System.Runtime.InteropServices;
using System.Windows.Forms;

namespace AvKit.RegionPicker;

/// <summary>
/// The WinForms shell: an opaque, topmost, borderless window positioned at the target
/// display's bounds, showing the already-frozen bitmap. It holds no geometry — every input
/// handler delegates to <see cref="PickerController"/>.
/// </summary>
public sealed class RegionForm : Form, IPickerDialog
{
    /// <summary>How dark the desktop outside the drag rect is painted.</summary>
    private static readonly Color ShadeColor = Color.FromArgb(120, 0, 0, 0);

    private static readonly Color BandColor = Color.FromArgb(255, 0, 174, 255);

    private Bitmap? _frame;
    private PickerController? _controller;
    private bool _frameShownRaised;

    public RegionForm()
    {
        FormBorderStyle = FormBorderStyle.None;
        StartPosition = FormStartPosition.Manual;
        ShowInTaskbar = false;
        TopMost = true;
        KeyPreview = true;
        Cursor = Cursors.Cross;
        BackColor = Color.Black;
        DoubleBuffered = true;
        SetStyle(
            ControlStyles.UserPaint | ControlStyles.AllPaintingInWmPaint | ControlStyles.OptimizedDoubleBuffer,
            true);
    }

    /// <inheritdoc />
    public event Action? FrameShown;

    /// <summary>
    /// Shows the already-frozen frame at <paramref name="bounds"/> and blocks until the user
    /// settles the selection. The bitmap is owned by the caller and is not disposed here.
    /// </summary>
    public PickerResult Show(Bitmap frozenFrame, Rectangle bounds)
    {
        ArgumentNullException.ThrowIfNull(frozenFrame);

        _frame = frozenFrame;
        _controller = new PickerController(frozenFrame.Size);
        Bounds = bounds;

        ShowDialog();

        return _controller.Result;
    }

    protected override void OnShown(EventArgs e)
    {
        base.OnShown(e);

        if (_frameShownRaised)
        {
            return;
        }

        // Shown is raised exactly once, after the freeze-frame window is on screen and before
        // any input is accepted. It is coarse — it fires when the window is shown, not when
        // the compositor has presented a frame — so the readiness time Electron records is a
        // lower bound, which is accepted rather than papered over.
        _frameShownRaised = true;
        Activate();
        ForceToForeground(Handle);
        FrameShown?.Invoke();
    }

    /// <summary>
    /// Puts the freeze-frame window at the top of the z-order and gives it the keyboard focus.
    ///
    /// <see cref="Form.TopMost"/> and <see cref="Form.Activate"/> are not enough on their own:
    /// the picker is launched by Electron, so this process has never held the foreground, and
    /// Windows lets a background process show a window without raising it above whatever the
    /// user was actually looking at. The observed symptom is a picker that is "visible" by
    /// every API measure while the foreground app is painted over it - the user sees no
    /// overlay, and the keyboard events (Esc, Enter) go somewhere else.
    /// </summary>
    private static void ForceToForeground(IntPtr handle)
    {
        SetWindowPos(handle, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW);
        BringWindowToTop(handle);

        // Best-effort: the foreground lock can refuse this, and a refusal is not fatal because
        // the z-order calls above have already made the window visible.
        SetForegroundWindow(handle);
    }

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

    protected override void OnPaint(PaintEventArgs e)
    {
        if (_frame is null || _controller is null)
        {
            base.OnPaint(e);
            return;
        }

        Graphics g = e.Graphics;
        g.InterpolationMode = InterpolationMode.NearestNeighbor;
        g.PixelOffsetMode = PixelOffsetMode.Half;
        g.DrawImageUnscaled(_frame, 0, 0);

        Rectangle selection = _controller.Selection;
        using var shade = new SolidBrush(ShadeColor);

        if (selection.Width <= 0 || selection.Height <= 0)
        {
            g.FillRectangle(shade, _controller.LocalBounds);
            return;
        }

        foreach (Rectangle outside in Outside(_controller.LocalBounds, selection))
        {
            g.FillRectangle(shade, outside);
        }

        using var pen = new Pen(BandColor, 1f);
        g.DrawRectangle(pen, selection.X, selection.Y, Math.Max(0, selection.Width - 1), Math.Max(0, selection.Height - 1));
    }

    /// <summary>The four bands of the frame that the selection does not cover.</summary>
    private static IEnumerable<Rectangle> Outside(Rectangle frame, Rectangle selection)
    {
        yield return new Rectangle(frame.Left, frame.Top, frame.Width, selection.Top - frame.Top);
        yield return new Rectangle(frame.Left, selection.Bottom, frame.Width, frame.Bottom - selection.Bottom);
        yield return new Rectangle(frame.Left, selection.Top, selection.Left - frame.Left, selection.Height);
        yield return new Rectangle(selection.Right, selection.Top, frame.Right - selection.Right, selection.Height);
    }

    protected override void OnMouseDown(MouseEventArgs e)
    {
        base.OnMouseDown(e);

        if (_controller is null || e.Button != MouseButtons.Left)
        {
            return;
        }

        _controller.BeginDrag(e.Location);
        Invalidate();
    }

    protected override void OnMouseMove(MouseEventArgs e)
    {
        base.OnMouseMove(e);

        if (_controller is null || !_controller.IsDragging)
        {
            return;
        }

        _controller.UpdateDrag(e.Location);
        Invalidate();
    }

    protected override void OnMouseUp(MouseEventArgs e)
    {
        base.OnMouseUp(e);

        if (_controller is null || e.Button != MouseButtons.Left)
        {
            return;
        }

        _controller.EndDrag(e.Location);
        CloseIfSettled();
    }

    protected override void OnKeyDown(KeyEventArgs e)
    {
        base.OnKeyDown(e);

        if (_controller is null)
        {
            return;
        }

        switch (e.KeyCode)
        {
            case Keys.Escape:
                _controller.Cancel();
                e.Handled = true;
                break;

            case Keys.Enter:
                _controller.Commit();
                e.Handled = true;
                break;

            default:
                return;
        }

        CloseIfSettled();
    }

    protected override void OnFormClosing(FormClosingEventArgs e)
    {
        // Alt+F4, a task-switch kill, or anything else that closes the window without a
        // decision is a cancel: the controller must never be left un-settled, or the exit
        // code would depend on how the window happened to go away.
        _controller?.Cancel();
        base.OnFormClosing(e);
    }

    private void CloseIfSettled()
    {
        if (_controller is not null && _controller.Result.Kind != PickerResultKind.InProgress)
        {
            Close();
        }
        else
        {
            Invalidate();
        }
    }
}
