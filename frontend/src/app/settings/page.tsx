"use client";

import { useEffect, useState } from "react";
import Shell from "@/components/layout/Shell";
import { Card, CardContent, CardHeader } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { whatsapp } from "@/lib/api";
import { Smartphone, QrCode, LogOut, CheckCircle, XCircle, Loader2 } from "lucide-react";

export default function SettingsPage() {
  const [hasSession, setHasSession] = useState<boolean | null>(null);
  const [qrData, setQrData] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string>("");

  useEffect(() => {
    whatsapp.status().then((r) => setHasSession(r.has_session)).catch(() => {});
  }, []);

  const handleGetQr = async () => {
    setLoading(true);
    setStatus("Launching WhatsApp Web…");
    try {
      const res = await whatsapp.qr();
      if (res.qr) {
        setQrData(res.qr);
        setStatus("Scan this QR code with your phone (WhatsApp → Linked Devices → Link a Device)");
      } else {
        setStatus("Already authenticated! ✅");
        setHasSession(true);
      }
    } catch (err: any) {
      setStatus(`Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    if (!confirm("This will delete your WhatsApp session. You'll need to scan QR again.")) return;
    await whatsapp.logout();
    setHasSession(false);
    setQrData(null);
    setStatus("Session cleared");
  };

  return (
    <Shell>
      <div className="space-y-6 max-w-2xl">
        <h2 className="text-2xl font-bold text-gray-900">WhatsApp Session</h2>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-3">
              <Smartphone className="w-5 h-5 text-brand-600" />
              <h3 className="font-semibold">Connection Status</h3>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center gap-3">
              {hasSession === null && <Loader2 className="w-5 h-5 animate-spin text-gray-400" />}
              {hasSession === true && (
                <>
                  <CheckCircle className="w-5 h-5 text-green-500" />
                  <span className="text-green-700 font-medium">Session active — WhatsApp is connected</span>
                </>
              )}
              {hasSession === false && (
                <>
                  <XCircle className="w-5 h-5 text-red-400" />
                  <span className="text-gray-600">No active session — scan QR code to connect</span>
                </>
              )}
            </div>

            <div className="flex gap-3">
              <Button onClick={handleGetQr} disabled={loading}>
                <QrCode className="w-4 h-4" /> {loading ? "Please wait…" : "Get QR Code"}
              </Button>
              {hasSession && (
                <Button variant="danger" onClick={handleLogout}>
                  <LogOut className="w-4 h-4" /> Disconnect
                </Button>
              )}
            </div>

            {status && <p className="text-sm text-gray-600 bg-gray-50 rounded-lg p-3">{status}</p>}

            {qrData && (
              <div className="flex flex-col items-center gap-4 p-6 bg-white border-2 border-dashed border-gray-200 rounded-xl">
                <img src={`data:image/png;base64,${qrData}`} alt="WhatsApp QR Code" className="w-64 h-64" />
                <p className="text-sm text-gray-500 text-center max-w-sm">
                  Open WhatsApp on your phone → Settings → Linked Devices → Link a Device → Scan this QR code
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader><h3 className="font-semibold">Safety Tips</h3></CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm text-gray-600">
              <li>• Use delays of <strong>8–25 seconds</strong> between messages to avoid blocks</li>
              <li>• Keep daily limit under <strong>500 messages</strong> for new numbers</li>
              <li>• Avoid sending identical messages to many contacts — use <code>{"{Name}"}</code> placeholders</li>
              <li>• Don&apos;t send to numbers that haven&apos;t opted in</li>
              <li>• If you get a temporary ban, stop for 24–48 hours</li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </Shell>
  );
}
