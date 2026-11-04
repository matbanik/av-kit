using System.Drawing;
using System.Text.Json;
using AvKit.RegionPicker;
using Xunit;

namespace AvKit.RegionPicker.Tests;

/// <summary>
/// A scratch directory that exists for the lifetime of one test, so the "--out parent must
/// exist" and "no file is written on cancel" assertions operate on real filesystem state.
/// </summary>
public sealed class TempDir : IDisposable
{
    public TempDir()
    {
        Path = System.IO.Path.Combine(
            System.IO.Path.GetTempPath(),
            "avkit-picker-tests-" + Guid.NewGuid().ToString("n"));
        Directory.CreateDirectory(Path);
    }

    public string Path { get; }

    public string OutFile => System.IO.Path.Combine(Path, "capture.png");

    public void Dispose()
    {
        try
        {
            if (Directory.Exists(Path))
            {
                Directory.Delete(Path, recursive: true);
            }
        }
        catch (IOException)
        {
            // A leaked scratch directory must never fail a test run.
        }
    }
}

/// <summary>
/// AC-40.4 (static contract + argv errors), AC-40.16 (outcome -> exit code) and AC-40.24
/// (readiness marker: value, flush, and ordering) driven through the real
/// <see cref="Program.Run"/> entrypoint.
/// </summary>
public class ProgramExitTests
{
    private static readonly Rectangle Bounds = new(0, 0, 640, 480);

    private sealed record Harness(
        CallLog Log,
        FakeCaptureSource Capture,
        FakeDialog Dialog,
        RecordingWriter Stdout,
        RecordingWriter Stderr);

    private static Harness NewHarness(PickerResult result, Rectangle? bounds = null)
    {
        var log = new CallLog();
        return new Harness(
            log,
            new FakeCaptureSource(log, bounds ?? Bounds),
            new FakeDialog(log, result),
            new RecordingWriter(log),
            new RecordingWriter(new CallLog()));
    }

    private static int Run(Harness h, params string[] args)
        => Program.Run(args, h.Capture, h.Dialog, h.Stdout, h.Stderr);

    // ---- AC-40.4: the constants are the contract ----------------------------

    private static JsonElement NamedSets()
    {
        string path = System.IO.Path.Combine(AppContext.BaseDirectory, "named-sets.json");
        Assert.True(File.Exists(path), "named-sets.json was not copied to the test output: " + path);
        return JsonDocument.Parse(File.ReadAllText(path)).RootElement;
    }

    [Fact]
    public void PickerContract_MatchesTheNamedSetsInThePlan()
    {
        JsonElement sets = NamedSets();

        Assert.Equal(PickerContract.PICKER_MIN_EDGE_PX, sets.GetProperty("PICKER_MIN_EDGE_PX").GetInt32());
        Assert.Equal(PickerContract.PICKER_EXIT_CONFIRM, sets.GetProperty("PICKER_EXIT_CONFIRM").GetInt32());
        Assert.Equal(PickerContract.PICKER_EXIT_ERROR, sets.GetProperty("PICKER_EXIT_ERROR").GetInt32());
        Assert.Equal(PickerContract.PICKER_EXIT_CANCEL, sets.GetProperty("PICKER_EXIT_CANCEL").GetInt32());
        Assert.Equal(PickerContract.PICKER_READY_MARKER, sets.GetProperty("PICKER_READY_MARKER").GetString());
    }

    [Fact]
    public void ExitCodes_AreDistinct()
    {
        var codes = new[]
        {
            PickerContract.PICKER_EXIT_CONFIRM,
            PickerContract.PICKER_EXIT_ERROR,
            PickerContract.PICKER_EXIT_CANCEL,
        };

        Assert.Equal(codes.Length, codes.Distinct().Count());
    }

    // ---- AC-40.16: outcome -> exit code ------------------------------------

    [Fact]
    public void ConfirmedOutcome_ExitsConfirm_AndWritesThePngToOut()
    {
        using var temp = new TempDir();
        Harness h = NewHarness(PickerResult.Confirmed(new Rectangle(10, 20, 100, 80)));

        int code = Run(h, "--out", temp.OutFile);

        Assert.Equal(PickerContract.PICKER_EXIT_CONFIRM, code);
        Assert.True(File.Exists(temp.OutFile), "no PNG at " + temp.OutFile + "; stderr was: " + h.Stderr.Text);
    }

    [Fact]
    public void CancelledOutcome_ExitsCancel_AndWritesNoFile()
    {
        using var temp = new TempDir();
        Harness h = NewHarness(PickerResult.Cancelled);

        int code = Run(h, "--out", temp.OutFile);

        Assert.Equal(PickerContract.PICKER_EXIT_CANCEL, code);
        Assert.False(File.Exists(temp.OutFile));
    }

    // ---- AC-40.4: argv errors fail closed, before any capture --------------

    [Fact]
    public void MissingOutArgument_ExitsError_WithoutCapturingOrShowing()
    {
        Harness h = NewHarness(PickerResult.Confirmed(new Rectangle(0, 0, 100, 100)));

        int code = Run(h);

        Assert.Equal(PickerContract.PICKER_EXIT_ERROR, code);
        Assert.Equal(0, h.Capture.CaptureCount);
        Assert.Equal(0, h.Dialog.ShowCount);
        Assert.NotEqual(string.Empty, h.Stderr.Text.Trim());
    }

    [Fact]
    public void DuplicateOutArgument_ExitsError()
    {
        using var temp = new TempDir();
        Harness h = NewHarness(PickerResult.Confirmed(new Rectangle(0, 0, 100, 100)));

        int code = Run(h, "--out", temp.OutFile, "--out", temp.OutFile);

        Assert.Equal(PickerContract.PICKER_EXIT_ERROR, code);
        Assert.False(File.Exists(temp.OutFile));
        Assert.NotEqual(string.Empty, h.Stderr.Text.Trim());
    }

    [Fact]
    public void OutArgumentWithoutAValue_ExitsError()
    {
        Harness h = NewHarness(PickerResult.Confirmed(new Rectangle(0, 0, 100, 100)));

        int code = Run(h, "--out");

        Assert.Equal(PickerContract.PICKER_EXIT_ERROR, code);
        Assert.Equal(0, h.Capture.CaptureCount);
    }

    [Fact]
    public void OutParentDirectoryMissing_ExitsError_WithoutCapturing()
    {
        using var temp = new TempDir();
        string missing = System.IO.Path.Combine(temp.Path, "no-such-dir", "capture.png");
        Harness h = NewHarness(PickerResult.Confirmed(new Rectangle(0, 0, 100, 100)));

        int code = Run(h, "--out", missing);

        Assert.Equal(PickerContract.PICKER_EXIT_ERROR, code);
        Assert.False(File.Exists(missing));
        Assert.Equal(0, h.Capture.CaptureCount);
        Assert.NotEqual(string.Empty, h.Stderr.Text.Trim());
    }

    [Fact]
    public void UnknownArgument_ExitsError()
    {
        using var temp = new TempDir();
        Harness h = NewHarness(PickerResult.Confirmed(new Rectangle(0, 0, 100, 100)));

        int code = Run(h, "--out", temp.OutFile, "--annotate");

        Assert.Equal(PickerContract.PICKER_EXIT_ERROR, code);
        Assert.False(File.Exists(temp.OutFile));
    }

    // ---- AC-40.24: the readiness marker ------------------------------------

    [Fact]
    public void ReadinessMarker_IsWrittenOnItsOwnLine_AndFlushed()
    {
        using var temp = new TempDir();
        Harness h = NewHarness(PickerResult.Confirmed(new Rectangle(10, 20, 100, 80)));

        Run(h, "--out", temp.OutFile);

        string[] lines = h.Stdout.Text
            .Split('\n')
            .Select(line => line.Trim('\r', ' '))
            .Where(line => line.Length > 0)
            .ToArray();

        Assert.Contains(PickerContract.PICKER_READY_MARKER, lines);
        Assert.True(h.Stdout.FlushCount > 0, "the readiness line was never flushed");
    }

    [Fact]
    public void ReadinessMarker_IsWrittenAfterTheDialogReportsTheFrameIsShown()
    {
        using var temp = new TempDir();
        Harness h = NewHarness(PickerResult.Confirmed(new Rectangle(10, 20, 100, 80)));

        Run(h, "--out", temp.OutFile);

        int frameShown = h.Log.IndexOf(CallLog.FrameShown);
        int write = h.Log.IndexOf(CallLog.StdoutWrite);
        int flush = h.Log.IndexOf(CallLog.StdoutFlush);

        Assert.True(frameShown >= 0, "the dialog never reported the frame: " + h.Log);
        Assert.True(write > frameShown, "the marker was written before the frame was shown: " + h.Log);
        Assert.True(flush > write, "the marker was not flushed after being written: " + h.Log);
    }

    [Fact]
    public void ReadinessMarker_IsNotWrittenWhenArgvIsRejected()
    {
        Harness h = NewHarness(PickerResult.Cancelled);

        Run(h, "--out");

        Assert.DoesNotContain(PickerContract.PICKER_READY_MARKER, h.Stdout.Text);
    }

    [Fact]
    public void ReadinessMarker_IsWrittenEvenWhenTheUserCancels()
    {
        using var temp = new TempDir();
        Harness h = NewHarness(PickerResult.Cancelled);

        Run(h, "--out", temp.OutFile);

        Assert.Contains(PickerContract.PICKER_READY_MARKER, h.Stdout.Text);
    }
}
