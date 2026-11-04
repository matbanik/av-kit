using System.Windows.Forms;
using Xunit;
using Xunit.Abstractions;
using Xunit.Sdk;

namespace AvKit.RegionPicker.Tests;

/// <summary>
/// A <see cref="FactAttribute"/> that skips — visibly, with a reason in the receipt — when the
/// machine has only one display.
///
/// AC-40.27 requires the secondary-display case to skip rather than fail on single-monitor
/// hardware, which is a genuine external constraint. xunit v2 has no dynamic
/// <c>Assert.Skip</c>, and this repository restores from the local NuGet cache with no package
/// sources configured, so <c>Xunit.SkippableFact</c> cannot be added. The supported v2
/// mechanism is a discoverer that emits a skipped test case, which is what this does: the run
/// reports "Skipped" plus <see cref="SkipReason"/>, so the disposition receipt can quote it.
/// </summary>
[XunitTestCaseDiscoverer(
    "AvKit.RegionPicker.Tests.MultiMonitorFactDiscoverer",
    "avkit-region-picker-tests")]
[AttributeUsage(AttributeTargets.Method, AllowMultiple = false)]
public sealed class MultiMonitorFactAttribute : FactAttribute
{
    public const string SkipReason =
        "Screen.AllScreens.Length < 2 - no secondary display on this machine (CAPTURE-MULTIMON-HW).";
}

/// <summary>Emits a skipped test case for <see cref="MultiMonitorFactAttribute"/> on single-monitor hosts.</summary>
public sealed class MultiMonitorFactDiscoverer : FactDiscoverer
{
    public MultiMonitorFactDiscoverer(IMessageSink diagnosticMessageSink)
        : base(diagnosticMessageSink)
    {
    }

    protected override IXunitTestCase CreateTestCase(
        ITestFrameworkDiscoveryOptions discoveryOptions,
        ITestMethod testMethod,
        IAttributeInfo factAttribute)
    {
        if (Screen.AllScreens.Length >= 2)
        {
            return base.CreateTestCase(discoveryOptions, testMethod, factAttribute);
        }

        return new XunitSkippedDataRowTestCase(
            DiagnosticMessageSink,
            discoveryOptions.MethodDisplayOrDefault(),
            discoveryOptions.MethodDisplayOptionsOrDefault(),
            testMethod,
            MultiMonitorFactAttribute.SkipReason);
    }
}
